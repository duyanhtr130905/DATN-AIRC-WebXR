"""Unprivileged CI security negatives. Synthetic network/ZIP fixtures are not live App proof."""
import copy
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
import zipfile
import restore_asset_ci as ci
from restore_asset import sha


def context():
    return {'GITHUB_ACTIONS':'true','GITHUB_REPOSITORY':ci.SOURCE,'GITHUB_REPOSITORY_ID':'1457386122',
            'GITHUB_EVENT_NAME':'push','GITHUB_REF':'refs/heads/main','GITHUB_SHA':'a'*40,
            'GITHUB_WORKFLOW_SHA':'a'*40,'GITHUB_WORKFLOW_REF':ci.SOURCE+'/.github/workflows/p507-e0-e1.yml@refs/heads/main',
            'P507_APP_CLIENT_ID':'client','P507_APP_ID':'123','P507_VAULT_INSTALLATION_ID':'456','P507_TOKEN_INSTALLATION_ID':'456'}


def identity():
    return {'result':'APP_IDENTITY_PASS','app_id':123,'client_id':'client','installation_id':456,
            'owner':'duyanhtr130905','permissions':{'contents':'read','metadata':'read'},
            'repository_selection':'selected','head':'a'*40,'verified_at':datetime.now(timezone.utc).isoformat()}


def repo():
    return {'id':ci.REPO_ID,'full_name':ci.REPO,'private':True,'owner':{'login':'duyanhtr130905'},
            'permissions':{'pull':True,'push':False,'admin':False}}


class SecurityTests(unittest.TestCase):
    def test_fork_pr_branch_workflow_and_sha_rejected(self):
        ci.trusted_context(context())
        for k,v in [('GITHUB_EVENT_NAME','pull_request'),('GITHUB_EVENT_NAME','pull_request_target'),
                    ('GITHUB_REPOSITORY','attacker/fork'),('GITHUB_REF','refs/heads/feature'),
                    ('GITHUB_WORKFLOW_REF','wrong'),('GITHUB_WORKFLOW_SHA','b'*40),('GITHUB_REPOSITORY_ID','0')]:
            with self.subTest(k=k,v=v):
                e=context();e[k]=v
                with self.assertRaises(ci.Rejected):ci.trusted_context(e)

    def test_identity_installation_permissions_stale_and_missing_config(self):
        ci.validate_identity(identity(),context())
        for key,value in [('installation_id',999),('client_id','other'),('owner','other'),
                          ('permissions',{'contents':'write','metadata':'read'}),('repository_selection','all'),
                          ('head','b'*40),('verified_at','2000-01-01T00:00:00+00:00')]:
            with self.subTest(key=key):
                i=identity();i[key]=value
                with self.assertRaises(ci.Rejected):ci.validate_identity(i,context())
        with self.assertRaisesRegex(ci.Rejected,'SECURITY_APPROVAL_REQUIRED'):ci.validate_identity(identity(),{})

    def test_private_exact_repo_and_read_only_required(self):
        ci.verify_repo(repo())
        for key,value in [('private',False),('id',0),('full_name','attacker/vault'),
                          ('owner',{'login':'attacker'}),('permissions',{'push':True})]:
            with self.subTest(key=key):
                r=repo();r[key]=value
                with self.assertRaises(ci.Rejected):ci.verify_repo(r)

    def test_missing_invalid_expired_denied_missing_commit_and_network(self):
        with self.assertRaisesRegex(ci.Rejected,'CREDENTIAL_MISSING'):ci.API('')
        errors=[(HTTPError('https://api.github.com',s,'sensitive response',{},None),code)
                for s,code in [(401,'CREDENTIAL_INVALID_OR_EXPIRED'),(403,'VAULT_ACCESS_DENIED'),(404,'PINNED_SOURCE_UNAVAILABLE')]]
        errors.append((URLError('secret must not leak'),'NETWORK_FAILURE'))
        for error,code in errors:
            with self.subTest(code=code),patch('restore_asset_ci.build_opener') as opener:
                opener.return_value.open.side_effect=error
                with self.assertRaisesRegex(ci.Rejected,code):ci.API('SENSITIVE_SENTINEL').read('repos/'+ci.REPO)
        with self.assertRaisesRegex(ci.Rejected,'SOURCE_NOT_ALLOWED'):
            ci.API('sentinel').read('repos/attacker/repo')
        with self.assertRaisesRegex(ci.Rejected,'SOURCE_NOT_ALLOWED'):
            ci.API('sentinel').read('repos/duyanhtr130905/DATN-AIRC-WebXR/actions/artifacts/14309207795/zip')

    def test_cli_failure_never_logs_token_or_exception_body(self):
        with tempfile.TemporaryDirectory() as d,patch.object(ci,'ROOT',Path(d)),patch.dict(os.environ,context(),clear=True),patch('builtins.print') as printed:
            self.assertEqual(ci.main(),1)
            s=(Path(d)/'.local/p507-e0-e1/ci-vault-report.json').read_text()
            self.assertIn('CREDENTIAL_MISSING',s)
            self.assertNotIn('SENSITIVE_SENTINEL',s+str(printed.call_args_list))

    def test_vault_only_synthetic_restore_and_scope_lock_negatives(self):
        # Actual archive and real App test remain BLOCKED until credentials are approved.
        lock=(ci.HERE/'asset-lock.json').read_bytes().replace(b'\r\n',b'\n')
        data={f'fixture-{i}':b'fixture' for i in range(28)}
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z:
            for n,b in data.items():z.writestr(n,b)
        archive=stream.getvalue()
        manifest={'artifact_id':14309207795,'run_id':44038653564,'asset_lock_sha256':sha(lock),
                  'archive':{'bytes':len(archive),'sha256':sha(archive)},
                  'members':[{'path':n,'bytes':len(b),'sha256':sha(b)} for n,b in data.items()]}
        mb=json.dumps(manifest).encode()
        pin=json.loads((ci.HERE/'vault-lock.json').read_text())
        pin.update(archive_bytes=len(archive),archive_sha256=sha(archive),manifest_sha256=sha(mb))
        class FakeAPI:
            def __init__(self,mode):self.mode=mode;self.paths=[]
            def read(self,path,raw=False):
                self.paths.append(path)
                assert '/actions/' not in path and 'generated' not in path
                if path.startswith('installation/'):
                    return {'total_count':2 if self.mode=='scope' else 1,'repositories':[repo()]}
                if path=='repos/'+ci.REPO:return repo()
                assert '?ref=908a5cbb1f77b75b28666fd424cbd85f2aba4c1f' in path
                if '/archive-manifest.json?' in path:return mb
                if '/asset-lock.json?' in path:return b'bad lock' if self.mode=='lock' else lock
                return archive+b'bad' if self.mode=='archive' else archive
        for mode in ('pass','scope','lock','archive'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as d,patch.object(ci,'ROOT',Path(d)),patch.object(ci,'validate_bundle',return_value={'result':'SYNTHETIC_NOT_E0_PROOF'}):
                api=FakeAPI(mode);dest=Path(d)/'.local/artifact'
                if mode=='pass':
                    self.assertEqual(ci.restore(api,pin,dest)['result'],'CI_VAULT_BUNDLE_PASS')
                    self.assertEqual(len(list(dest.iterdir())),28)
                else:
                    with self.assertRaises((ci.Rejected,ValueError)):ci.restore(api,pin,dest)
                    self.assertFalse(dest.exists())

    def test_workflow_secret_boundary_and_no_privileged_legacy_download(self):
        for name in ('p507-e0-e1.yml','p507-tv-diagnostic.yml'):
            s=(ci.ROOT/'.github/workflows'/name).read_text()
            self.assertNotIn('pull_request_target',s)
            self.assertNotIn('--download',s)
            self.assertIn('NOT_RUN_PRIVILEGED_REQUIRED',s)
            priv=s.split('  vault-'+('frozen-asset-browser' if name.startswith('p507-e0') else 'original-version-diagnostic')+':')[1]
            self.assertIn("github.ref == 'refs/heads/main'",priv)
            self.assertIn('environment: p507-vault-ci',priv)
            self.assertIn('ref: ${{ github.sha }}',priv)
            self.assertIn('permission-contents: read',priv)
            self.assertIn('repositories: DATN-AIRC-WebXR-asset-vault',priv)
            self.assertIn('skip-token-revoke: false',priv)
            self.assertIn('--restore-vault-ci',priv)
            self.assertNotIn('--download',priv)
            self.assertNotIn('GITHUB_WORKSPACE',priv)
            self.assertNotIn('runner.temp',priv)
            self.assertNotIn('secrets.',s.split('  asset-validation-status:')[0])


if __name__=='__main__':unittest.main()
