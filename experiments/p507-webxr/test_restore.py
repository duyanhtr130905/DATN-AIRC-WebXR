"""Restore rejection tests: archive integrity, extraction safety and access boundary."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from restore_asset import extract_verified, private_owner_repo, verify_archive


def fixture(entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as z:
        for name, data in entries:
            z.writestr(name, data)
    blob = stream.getvalue()
    manifest = {'archive':{'sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob)},
                'artifact_id':14309207795,'run_id':44038653564,
                'members':[{'path':n,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()} for n,b in entries]}
    return blob, manifest


class RestoreTests(unittest.TestCase):
    def test_archive_corruption_and_wrong_provenance_fail(self):
        blob, m = fixture([('asset.bin', b'original')])
        pin = {'archive_bytes':len(blob),'archive_sha256':hashlib.sha256(blob).hexdigest()}
        verify_archive(blob,m,pin)
        with self.assertRaisesRegex(ValueError,'Archive SHA'):
            verify_archive(blob+b'x',m,pin)
        m['artifact_id'] = 0
        with self.assertRaisesRegex(ValueError,'provenance'):
            verify_archive(blob,m,pin)

    def test_safe_extract_and_existing_target_is_preserved(self):
        blob,m=fixture([('asset.bin',b'original')])
        with tempfile.TemporaryDirectory() as d:
            archive=Path(d)/'source.zip';archive.write_bytes(blob);dest=Path(d)/'restore'
            extract_verified(archive,m,dest)
            self.assertEqual((dest/'asset.bin').read_bytes(),b'original')
            with self.assertRaisesRegex(ValueError,'refusing overwrite'):
                extract_verified(archive,m,dest)
            self.assertEqual((dest/'asset.bin').read_bytes(),b'original')

    def test_unsafe_paths_rejected_before_write(self):
        for name in ('../escape','/absolute','C:/escape','dir\\escape'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as d:
                blob,m=fixture([(name,b'x')]);archive=Path(d)/'source.zip';archive.write_bytes(blob)
                dest=Path(d)/'restore'
                with self.assertRaises(ValueError):
                    extract_verified(archive,m,dest)
                self.assertFalse(dest.exists())

    def test_unexpected_duplicate_and_wrong_member_hash_fail(self):
        for mode in ('unexpected','duplicate','hash'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as d:
                blob,m=fixture([('asset.bin',b'x')])
                if mode=='unexpected':m['members']=[]
                if mode=='duplicate':blob,_=fixture([('asset.bin',b'x'),('asset.bin',b'x')])
                if mode=='hash':m['members'][0]['sha256']='0'*64
                archive=Path(d)/'source.zip';archive.write_bytes(blob);dest=Path(d)/'restore'
                with self.assertRaises(ValueError):extract_verified(archive,m,dest)
                self.assertFalse(dest.exists())

    def test_public_repo_and_nonowner_auth_fail(self):
        for public,login in ((True,'owner'),(False,'collaborator')):
            with self.subTest(public=public,login=login):
                meta={'owner':{'login':'owner'},'private':not public,'permissions':{'admin':True},'full_name':'owner/vault'}
                with patch('restore_asset.subprocess.check_output',side_effect=[json.dumps({'login':login}),json.dumps(meta)]):
                    with self.assertRaisesRegex(ValueError,'PRIVATE vault'):
                        private_owner_repo({'owner':'owner','repository':'owner/vault'})


if __name__=='__main__':unittest.main()
