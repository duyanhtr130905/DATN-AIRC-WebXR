"""Offline reference verification; never regenerates expected values."""
import json
from pathlib import Path
from tv_diagnostic_math import glb_components, union_bounds, prism_clearance
from validate_asset import validate_bundle, require
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def verify(directory, reference=None):
    bundle=validate_bundle(directory)
    ref=reference or json.loads((HERE/'export-bounds-v1.json').read_text())
    require(ref['schema_version']==1 and ref['model_sha256']==bundle['modelSha256'] and ref['model_bytes']==bundle['modelBytes'],'Reference asset identity mismatch')
    records=ref['records'];ids=[r['id'] for r in records]
    manifest=json.loads((directory/'asset-manifest.json').read_text())
    proxies={p['id']:p for p in manifest['collision_proxies']}
    require(len(ids)==len(set(ids))==121 and set(ids)==set(proxies),'Reference missing/duplicate IDs')
    groups={}
    for c in glb_components(directory/'P507_G1_G2_PROVISIONAL.glb'):
        if c['id'] in proxies:groups.setdefault(c['id'],[]).append(c)
    maximum=0; samples=0
    for r in records:
        cs=groups[r['id']];actual=union_bounds([c['bounds_gltf'] for c in cs])
        require(len(r['bounds'])==6,'Reference bounds length')
        delta=max(abs(a-b) for a,b in zip(actual,r['bounds']));maximum=max(maximum,delta)
        require(delta<2e-6,'Reference bounds differ: '+r['id'])
        require(r['primitive_count']==len(cs) and r['vertex_samples']==sum(c['vertex_count'] for c in cs),'Reference component counts: '+r['id'])
        for c in cs:
            for v in c['positions_gltf']:
                samples+=1;require(prism_clearance(v,proxies[r['id']])>=-.001,'Proxy containment: '+r['id'])
    return {'result':'PASS','method':'independent Python POSITION/hierarchy decoder','maxReferenceDeltaM':maximum,'vertexSamples':samples,'assetHash':bundle['modelSha256']}
if __name__=='__main__':
    result=verify(ROOT/'.local/p507-e0-e1/artifact')
    (ROOT/'.local/p507-e0-e1/export-reference-report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
