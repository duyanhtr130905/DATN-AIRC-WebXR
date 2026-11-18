"""Negative offline reference tests without downloading an asset in logic CI."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from verify_export_reference import verify
HERE=Path(__file__).resolve().parent
class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.ref=json.loads((HERE/'export-bounds-v1.json').read_text())
        self.bundle={'modelSha256':self.ref['model_sha256'],'modelBytes':self.ref['model_bytes']}
    def reject(self,reference,message):
        with patch('verify_export_reference.validate_bundle',return_value=self.bundle):
            with self.assertRaisesRegex(ValueError,message):verify(HERE,reference)
    def test_wrong_asset_hash(self):
        self.ref['model_sha256']='0'*64;self.reject(self.ref,'identity')
    def test_wrong_asset_bytes(self):
        self.ref['model_bytes']+=1;self.reject(self.ref,'identity')
    def test_reference_is_complete_versioned(self):
        self.assertEqual(self.ref['schema_version'],1)
        self.assertEqual(len(self.ref['records']),121)
        self.assertEqual(len({r['id'] for r in self.ref['records']}),121)
        self.assertEqual(sum(r['vertex_samples'] for r in self.ref['records']),402482)
        self.assertTrue(all(len(r['bounds'])==6 for r in self.ref['records']))
if __name__=='__main__':unittest.main()
