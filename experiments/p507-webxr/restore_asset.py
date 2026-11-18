"""Explicit owner-only restore from pinned PRIVATE vault; no Actions-artifact fallback."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import subprocess
import tempfile
from datetime import datetime, timezone
import zipfile

from validate_asset import HERE, ROOT, require, validate_bundle


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def verify_archive(blob, manifest, pin):
    require(len(blob) == pin['archive_bytes'] and sha(blob) == pin['archive_sha256'], 'Archive SHA/bytes mismatch')
    require(manifest['archive']['sha256'] == pin['archive_sha256'] and manifest['archive']['bytes'] == pin['archive_bytes'], 'Manifest archive mismatch')
    require(manifest['artifact_id'] == 14309207795 and manifest['run_id'] == 44038653564, 'Original provenance mismatch')


def extract_verified(archive, manifest, destination):
    require(not destination.exists(), 'Restore destination already exists; refusing overwrite')
    expected = {r['path']: r for r in manifest['members']}
    require(len(expected) == len(manifest['members']), 'Duplicate manifest member')
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist()
        require(len(infos) == len({i.filename for i in infos}), 'Duplicate ZIP entry')
        require({i.filename for i in infos} == set(expected), 'ZIP member set differs')
        # Validate every path and byte before writing any member.
        for i in infos:
            name = PurePosixPath(i.filename)
            require(not name.is_absolute() and not any(p in ('..', '.') for p in name.parts)
                    and '\\' not in i.filename and ':' not in i.filename
                    and not i.is_dir() and not stat.S_ISLNK(i.external_attr >> 16), 'Unsafe ZIP member')
            require(i.file_size == expected[i.filename]['bytes'], 'ZIP member size mismatch')
            require(sha(z.read(i)) == expected[i.filename]['sha256'], 'ZIP member SHA mismatch')
        destination.mkdir(parents=True)
        for i in infos:
            target = destination.joinpath(*PurePosixPath(i.filename).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(i))


def private_owner_repo(pin):
    login = json.loads(subprocess.check_output(['gh', 'api', 'user'], text=True))['login']
    meta = json.loads(subprocess.check_output(['gh', 'api', 'repos/'+pin['repository']], text=True))
    require(login == pin['owner'] == meta['owner']['login'] and meta['private'] is True
            and meta['permissions']['admin'] is True, 'BLOCKED: owner authentication and PRIVATE vault required')
    return {'repository':meta['full_name'], 'private':meta['private'], 'authenticated_owner':login}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--destination', type=Path, default=ROOT/'.local/p507-e0-e1/artifact')
    args = ap.parse_args()
    dest = args.destination.resolve()
    require(dest.is_relative_to((ROOT/'.local').resolve()), 'Destination must be inside this checkout .local')
    require(not dest.exists(), 'Restore destination already exists; use a clean checkout/destination')
    pin = json.loads((HERE/'vault-lock.json').read_text(encoding='utf-8'))
    lock = (HERE/'asset-lock.json').read_bytes().replace(b'\r\n', b'\n')
    require(sha(lock) == pin['asset_lock_sha256'], 'Source asset lock changed')
    before = private_owner_repo(pin)
    temp_root = ROOT/'.local'
    temp_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='p507-vault-fetch-', dir=temp_root) as td:
        fetched = Path(td)/'remote.git'
        subprocess.run(['gh', 'repo', 'clone', pin['repository'], str(fetched), '--', '--bare'], check=True)
        # Read Git blobs directly: no CRLF conversion of manifests or archive.
        def blob(name):
            return subprocess.check_output(['git', 'show', pin['commit']+':'+pin['directory']+'/'+name], cwd=fetched)
        manifest_blob = blob('archive-manifest.json')
        require(sha(manifest_blob) == pin['manifest_sha256'], 'Pinned manifest hash mismatch')
        manifest = json.loads(manifest_blob)
        require(blob('asset-lock.json') == lock and manifest['asset_lock_sha256'] == sha(lock), 'Vault/source lock mismatch')
        archive_blob = blob(pin['archive_name'])
        verify_archive(archive_blob, manifest, pin)
        archive = Path(td)/'original.zip'
        archive.write_bytes(archive_blob)
        staging = Path(td)/'verified-bundle'
        extract_verified(archive, manifest, staging)
        bundle = validate_bundle(staging)
        after = private_owner_repo(pin)
        dest.parent.mkdir(parents=True, exist_ok=True)
        require(not dest.exists(), 'Destination appeared during restore; refusing overwrite')
        staging.rename(dest)
    report = {'result':'RESTORE_BUNDLE_PASS', 'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'head':subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        'dirty':bool(subprocess.check_output(['git','status','--porcelain'], cwd=ROOT, text=True).strip()),
        'vault_commit':pin['commit'], 'archive_sha256':pin['archive_sha256'], 'archive_bytes':pin['archive_bytes'],
        'privacy_before':before, 'privacy_after':after, 'member_count':len(manifest['members']),
        'origin_actions_downloads':0, 'existing_local_bundle_used':False, 'bundle':bundle,
        'notice':'E0 actual geometry/reference and E1 Chrome must run separately; no CI cross-repo credentials granted.'}
    output = ROOT/'.local/p507-e0-e1/vault-restore-report.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
