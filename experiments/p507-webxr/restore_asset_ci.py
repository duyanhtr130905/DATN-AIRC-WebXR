"""Installation-token-only restore. Owner local path remains restore_asset.py."""
import argparse
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from restore_asset import sha, verify_archive, extract_verified
from validate_asset import HERE, ROOT, validate_bundle

REPO = 'duyanhtr130905/DATN-AIRC-WebXR-asset-vault'
REPO_ID = 1462515003
SOURCE = 'duyanhtr130905/DATN-AIRC-WebXR'


class Rejected(Exception):
    pass


def demand(ok, code):
    if not ok:
        raise Rejected(code)


def trusted_context(env):
    demand(env.get('GITHUB_ACTIONS') == 'true' and env.get('GITHUB_REPOSITORY') == SOURCE
           and env.get('GITHUB_REPOSITORY_ID') == '1457386122'
           and env.get('GITHUB_EVENT_NAME') in ('push', 'workflow_dispatch')
           and env.get('GITHUB_REF') == 'refs/heads/main', 'UNTRUSTED_CONTEXT')
    demand(re.fullmatch('[a-f0-9]{40}', env.get('GITHUB_SHA','')) is not None
           and env.get('GITHUB_WORKFLOW_SHA') == env['GITHUB_SHA'], 'UNTRUSTED_SHA')
    demand(env.get('GITHUB_WORKFLOW_REF') in {
        SOURCE+'/.github/workflows/p507-e0-e1.yml@refs/heads/main',
        SOURCE+'/.github/workflows/p507-tv-diagnostic.yml@refs/heads/main'}, 'UNTRUSTED_WORKFLOW')


def validate_identity(identity, env):
    demand(all(env.get(k) for k in ('P507_APP_CLIENT_ID','P507_APP_ID','P507_VAULT_INSTALLATION_ID',
                                   'P507_TOKEN_INSTALLATION_ID')), 'SECURITY_APPROVAL_REQUIRED')
    demand(identity.get('result') == 'APP_IDENTITY_PASS'
           and str(identity.get('app_id')) == env['P507_APP_ID']
           and identity.get('client_id') == env['P507_APP_CLIENT_ID']
           and str(identity.get('installation_id')) == env['P507_VAULT_INSTALLATION_ID']
           == env['P507_TOKEN_INSTALLATION_ID']
           and identity.get('owner') == 'duyanhtr130905'
           and identity.get('permissions') == {'contents':'read','metadata':'read'}
           and identity.get('repository_selection') == 'selected'
           and identity.get('head') == env['GITHUB_SHA'], 'APP_IDENTITY_MISMATCH')
    try:
        age = (datetime.now(timezone.utc)-datetime.fromisoformat(identity['verified_at'])).total_seconds()
        demand(0 <= age < 600, 'STALE_APP_IDENTITY')
    except (KeyError, ValueError):
        raise Rejected('STALE_APP_IDENTITY') from None


def verify_repo(meta):
    demand(meta.get('id') == REPO_ID and meta.get('full_name') == REPO
           and meta.get('private') is True and meta.get('owner',{}).get('login') == 'duyanhtr130905',
           'VAULT_IDENTITY_MISMATCH')
    demand(not any(meta.get('permissions',{}).get(p) for p in ('push','admin','maintain','triage')),
           'EXCESSIVE_TOKEN_PERMISSIONS')


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class API:
    def __init__(self, token):
        demand(bool(token), 'CREDENTIAL_MISSING')
        self.token = token

    def read(self, path, raw=False):
        demand((path == 'repos/'+REPO or path.startswith('repos/'+REPO+'/contents/')
                or path == 'installation/repositories?per_page=100') and '://' not in path,
               'SOURCE_NOT_ALLOWED')
        req = Request('https://api.github.com/'+path, headers={
            'Authorization':'Bearer '+self.token, 'User-Agent':'p507-vault-ci',
            'Accept':'application/vnd.github.raw+json' if raw else 'application/vnd.github+json',
            'X-GitHub-Api-Version':'2026-03-10'})
        try:
            with build_opener(NoRedirect).open(req, timeout=60) as response:
                blob = response.read(16*1024*1024+1)
                demand(len(blob) <= 16*1024*1024, 'RESPONSE_TOO_LARGE')
        except HTTPError as error:
            raise Rejected({401:'CREDENTIAL_INVALID_OR_EXPIRED',403:'VAULT_ACCESS_DENIED',
                            404:'PINNED_SOURCE_UNAVAILABLE'}.get(error.code,'VAULT_HTTP_FAILURE')) from None
        except (URLError, TimeoutError, OSError):
            raise Rejected('NETWORK_FAILURE') from None
        if raw:
            return blob
        try:
            return json.loads(blob)
        except ValueError:
            raise Rejected('INVALID_API_RESPONSE') from None


def restore(api, pin, destination):
    demand(pin['repository'] == REPO and pin['commit'] == '908a5cbb1f77b75b28666fd424cbd85f2aba4c1f', 'SOURCE_NOT_ALLOWED')
    demand(not destination.exists(), 'DESTINATION_EXISTS')
    listing = api.read('installation/repositories?per_page=100')
    demand(listing.get('total_count') == 1 and len(listing.get('repositories',[])) == 1, 'TOKEN_REPOSITORY_SCOPE_MISMATCH')
    verify_repo(listing['repositories'][0])
    verify_repo(api.read('repos/'+REPO))
    prefix = 'repos/'+REPO+'/contents/'+quote(pin['directory'],safe='/')+'/'
    def read(name):
        return api.read(prefix+quote(name,safe='')+'?ref='+pin['commit'], raw=True)
    manifest_bytes = read('archive-manifest.json')
    demand(sha(manifest_bytes) == pin['manifest_sha256'], 'MANIFEST_HASH_MISMATCH')
    manifest = json.loads(manifest_bytes)
    lock = (HERE/'asset-lock.json').read_bytes().replace(b'\r\n',b'\n')
    demand(sha(lock) == pin['asset_lock_sha256'] and read('asset-lock.json') == lock
           and manifest['asset_lock_sha256'] == sha(lock), 'FILE_LOCK_MISMATCH')
    demand(len(manifest['members']) == 28, 'MEMBER_COUNT_MISMATCH')
    archive_bytes = read(pin['archive_name'])
    verify_archive(archive_bytes, manifest, pin)
    (ROOT/'.local').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='ci-vault-', dir=ROOT/'.local') as td:
        archive = Path(td)/'original.zip'
        archive.write_bytes(archive_bytes)
        staging = Path(td)/'verified'
        extract_verified(archive,manifest,staging)
        bundle = validate_bundle(staging)
        verify_repo(api.read('repos/'+REPO))
        destination.parent.mkdir(parents=True,exist_ok=True)
        demand(not destination.exists(), 'DESTINATION_EXISTS')
        staging.rename(destination)
    return {'result':'CI_VAULT_BUNDLE_PASS','vault_commit':pin['commit'],
            'archive_sha256':pin['archive_sha256'],'archive_bytes':len(archive_bytes),
            'member_count':28,'bundle':bundle,'original_artifact_requests':0,'generated_fallback':False}


def main():
    output = ROOT/'.local/p507-e0-e1/ci-vault-report.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    report = {'result':'BLOCKED','status':'SECURITY_APPROVAL_REQUIRED'}
    try:
        trusted_context(os.environ)
        token = os.environ.get('P507_VAULT_TOKEN','')
        demand(bool(token),'CREDENTIAL_MISSING')
        identity = json.loads((ROOT/'.local/p507-ci/app-identity.json').read_text())
        validate_identity(identity,os.environ)
        demand(subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip() == os.environ['GITHUB_SHA'], 'CHECKOUT_SHA_MISMATCH')
        pin = json.loads((HERE/'vault-lock.json').read_text())
        report = restore(API(token),pin,ROOT/'.local/p507-e0-e1/artifact')
        report.update(head=os.environ['GITHUB_SHA'],identity='APP_INSTALLATION',
                      installation_id=identity['installation_id'],private=True)
    except Rejected as error:
        report['status'] = str(error)
    except Exception:
        # Never interpolate HTTP bodies, exception objects, env, request headers or keys.
        report['status'] = 'INVALID_OR_UNAVAILABLE_BUNDLE'
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
    return 0 if report['result']=='CI_VAULT_BUNDLE_PASS' else 1


if __name__=='__main__':
    raise SystemExit(main())
