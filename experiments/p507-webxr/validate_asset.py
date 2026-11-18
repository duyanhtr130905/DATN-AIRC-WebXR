"""Validate the exact, immutable CI export bundle. No asset repair or regeneration."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FILES = ('P507_G1_G2_PROVISIONAL.glb', 'asset-manifest.json', 'geometry-report.json',
         'report.json', 'gltf-validation-report.json', 'browser-report.json')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def glb_document(blob):
    require(len(blob) >= 20, 'Corrupt GLB: truncated header')
    magic, version, length, chunk, kind = struct.unpack_from('<4sIII4s', blob)
    require(magic == b'glTF' and version == 2 and length == len(blob), 'Corrupt GLB header/length')
    require(kind == b'JSON' and chunk <= len(blob)-20, 'Corrupt GLB JSON chunk')
    return json.loads(blob[20:20+chunk])


def validate_bundle(directory, lock=None):
    lock = lock or json.loads((HERE/'asset-lock.json').read_text())
    for name in FILES:
        path = directory/name
        require(path.is_file(), 'Missing asset bundle file: '+name)
        blob = path.read_bytes()
        expected = lock['files'][name]
        require(len(blob) == expected['bytes'], 'File size mismatch: '+name)
        require(hashlib.sha256(blob).hexdigest() == expected['sha256'], 'SHA-256 mismatch: '+name)
    m, r, b, g, v = [json.loads((directory/name).read_text(encoding='utf-8')) for name in
                     ('asset-manifest.json','report.json','browser-report.json','geometry-report.json','gltf-validation-report.json')]
    model = (directory/FILES[0]).read_bytes()
    digest = hashlib.sha256(model).hexdigest()
    require(m['model_sha256'] == r['glb_sha256'] == b['glbSha256'] == digest, 'Mixed export/model hash')
    require(m['model_bytes'] == r['glb_bytes'] == b['glbBytes'] == len(model), 'Model bytes disagree')
    require(m['source_sha'] == r['source_sha'] == b['ciHeadSha'] == lock['source_sha'], 'Source SHA mismatch')
    require(m['checkout_sha'] == r['checkout_sha'] == b['checkoutHeadSha'] == b['ciCheckoutSha'] == lock['checkout_sha'], 'CI checkout SHA mismatch')
    require(str(b['ciRunId']) == str(lock['run_id']), 'CI run mismatch')
    require(not r['source_work_tree_dirty'] and not b['workTreeDirty'], 'Dirty source export')
    for filename, sha in r['input_sha256'].items():
        committed = subprocess.check_output(['git','show','HEAD:experiments/p507-g1-g2/'+filename], cwd=ROOT)
        working = (ROOT/'experiments/p507-g1-g2'/filename).read_bytes()
        require(hashlib.sha256(committed).hexdigest() == sha and working.replace(b'\r\n',b'\n') == committed, 'Frozen input changed (Git blob hash / working LF comparison): '+filename)
    require(g['ok'] and r['ok'] and v['issues']['numErrors'] == 0, 'Source export/validator failed')
    require(m['schema_version'] == 1 and m['unit'] == 'metre', 'Unsupported schema/unit')
    require('(x,z,-y)' in m['axis_conversion'], 'Axis contract mismatch')
    for field, dimensions, source in [('survey_baseline',(6,8.1,3.5),'USER_REPORTED'),
                                      ('virtual_dimensions',(6.9,9.315,3.5),'OWNER_APPROVED_VIRTUAL_ADAPTATION')]:
        require(tuple(m[field][k] for k in ('width_x','length_y','height_z')) == dimensions and m[field]['source'] == source, field+' mismatch')
    records = m['instances']
    ids = [i['id'] for i in records]
    placed = {i['id'] for i in records if i['status'] != 'UNPLACED'}
    require(len(ids) == len(set(ids)) == 123 and len(placed) == 121, 'Logical ID counts/duplicates')
    require(len([i for i in placed if i.startswith('P507-DESK-')]) == 17, 'Desk count mismatch')
    require([sum(i.startswith('P507-CHAIR-'+c+'-') for i in placed) for c in 'ABC'] == [12,12,10], 'Chair allocation mismatch')
    unplaced = {'P507-CHAIR-C-09','P507-CHAIR-C-10'}
    require(set(ids)-placed == unplaced and all(i['placement_allocation'] is None and not i['survey_transform'].get('center') for i in records if i['id'] in unplaced), 'UNPLACED records changed')
    proxies = m['collision_proxies']
    require(len(proxies) == 121 and {p['id'] for p in proxies} == placed, 'Proxy ID contract mismatch')
    require(proxies == g['occupancy'] == r['occupancy'], 'Mixed proxy export')
    for p in proxies:
        require(len(p['polygon']) >= 3 and p['top_z'] > p['bottom_z'], 'Invalid proxy: '+p['id'])
    doc = glb_document(model)
    node_ids = {n.get('extras',{}).get('survey_instance_id') for n in doc['nodes']} - {None}
    require(node_ids == placed, 'Actual GLB logical ID set mismatch')
    require(m['floor']['surface_z_survey'] == 0, 'Floor contract mismatch')
    require(m['starting_pose']['feet_gltf'] == [1.25,0,-7.415] and m['starting_pose']['feet_survey'] == [1.25,7.415,0], 'Starting pose mismatch')
    return {'result':'E0_BUNDLE_PASS', 'sourceSha':m['source_sha'], 'checkoutSha':m['checkout_sha'],
            'modelSha256':digest, 'modelBytes':len(model), 'stableRecords':123,'placedIDs':121,
            'notice':'Runtime world-geometry, identity transform and capsule spawn checks also required for E0_PASS.'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--asset-dir', type=Path, default=ROOT/'.local/p507-e0-e1/artifact')
    ap.add_argument('--prepare', action='store_true')
    args = ap.parse_args()
    output = ROOT/'.local/p507-e0-e1/e0-bundle-report.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        report = validate_bundle(args.asset_dir)
        if args.prepare:
            dest = ROOT/'.local/p507-e0-e1/served'
            dest.mkdir(parents=True, exist_ok=True)
            for name in (FILES[0], FILES[1]):
                shutil.copyfile(args.asset_dir/name, dest/name)
            shutil.copyfile(HERE/'asset-lock.json', dest/'asset-lock.json')
    except (OSError, ValueError, KeyError, TypeError) as error:
        report = {'result':'E0_BLOCKED' if isinstance(error,FileNotFoundError) else 'E0_FAIL','error':str(error)}
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if report['result'] == 'E0_BUNDLE_PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
