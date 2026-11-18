"""Negative bundle tests; full runtime checks require actual browser GLTFLoader."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('e0', HERE/'validate_asset.py')
e0 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e0)


class BundleTests(unittest.TestCase):
    def test_missing_asset_is_explicit(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, 'Missing asset bundle file'):
                e0.validate_bundle(Path(d))

    def test_hash_mismatch_detected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/e0.FILES[0]
            p.write_bytes(b'corrupt')
            lock = json.loads((HERE/'asset-lock.json').read_text())
            lock['files'][e0.FILES[0]]['bytes'] = 7
            with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
                e0.validate_bundle(Path(d),lock)

    def test_size_mismatch_detected(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/e0.FILES[0]).write_bytes(b'bad')
            with self.assertRaisesRegex(ValueError, 'File size mismatch'):
                e0.validate_bundle(Path(d))

    def test_corrupt_glb(self):
        for blob in (b'', b'x'*40):
            with self.assertRaisesRegex(ValueError,'Corrupt GLB'):
                e0.glb_document(blob)

    def test_lock_records_exact_artifact(self):
        lock=json.loads((HERE/'asset-lock.json').read_text())
        self.assertEqual(lock['artifact_id'],14309207795)
        self.assertNotEqual(lock['checkout_sha'],lock['source_sha'])
        self.assertEqual(len(lock['files']),6)


if __name__ == '__main__':
    unittest.main()
