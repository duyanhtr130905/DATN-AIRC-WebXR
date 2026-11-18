"""Download only the pinned CI artifact with existing gh authentication; never replace exports."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from validate_asset import HERE, ROOT, validate_bundle

REPO='duyanhtr130905/DATN-AIRC-WebXR'


def main():
    ap=argparse.ArgumentParser()
    source=ap.add_mutually_exclusive_group()
    source.add_argument('--download',action='store_true')
    source.add_argument('--restore-vault',action='store_true',help='Explicit owner-only PRIVATE vault restore; never automatic fallback')
    args=ap.parse_args()
    lock=json.loads((HERE/'asset-lock.json').read_text())
    target=ROOT/'.local/p507-e0-e1/artifact'
    if args.restore_vault:
        subprocess.run([sys.executable,str(HERE/'restore_asset.py')],check=True)
    if args.download:
        metadata=json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/actions/artifacts/{lock["artifact_id"]}'],text=True))
        assert not metadata['expired'], 'Pinned artifact expired: E0_BLOCKED; no automatic substitute or re-export'
        assert metadata['name']==lock['artifact_name'] and metadata['workflow_run']['id']==lock['run_id'] and metadata['workflow_run']['head_sha']==lock['source_sha'], 'Artifact provenance mismatch'
        target.parent.mkdir(parents=True,exist_ok=True)
        # Record only public provenance fields, never auth headers/tokens.
        safe={k:metadata[k] for k in ('id','name','expired','digest','created_at','expires_at','workflow_run')}
        (target.parent/'download-provenance.json').write_text(json.dumps(safe,indent=2)+'\n')
        if not target.exists():
            subprocess.run(['gh','run','download',str(lock['run_id']),'--repo',REPO,'--name',lock['artifact_name'],'--dir',str(target)],check=True)
    print(json.dumps(validate_bundle(target),indent=2))


if __name__=='__main__':
    main()
