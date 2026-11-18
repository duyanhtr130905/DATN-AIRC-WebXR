"""Join frozen GLB and Blender diagnostic evidence without modifying E0 or assets."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys

from tv_diagnostic_math import (bounds, extrema, file_identity, glb_components, hausdorff,
                                prism_clearance, read_glb, survey_to_gltf, union_bounds)
from validate_asset import validate_bundle

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ID = 'P507-TV-LARGE'
EPS = 2e-6  # Evidence matching tolerance only; E0's 3mm gate is untouched.


def join_by_name(components):
    result = {}
    for c in components:
        result.setdefault(c['node'], []).append(c)
    return result


def component_points(parts):
    return [p for c in parts for p in c['positions_gltf']]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--artifact-dir', type=Path, required=True)
    ap.add_argument('--blender-dir', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--three-report', type=Path)
    ap.add_argument('--require-original-version', action='store_true')
    args = ap.parse_args()
    artifact, generated = args.artifact_dir, args.blender_dir
    bundle = validate_bundle(artifact)
    b = json.loads((generated/'blender-tv-report.json').read_text(encoding='utf-8'))
    if b['frozen_glb'] != file_identity(artifact/'P507_G1_G2_PROVISIONAL.glb') or b['frozen_blend'] != file_identity(artifact/'P507_G1_G2_PROVISIONAL.blend'):
        raise ValueError('Blender report belongs to different source files')
    m = json.loads((artifact/'asset-manifest.json').read_text(encoding='utf-8'))
    frozen_path = artifact/'P507_G1_G2_PROVISIONAL.glb'
    doc, _ = read_glb(frozen_path)
    frozen = glb_components(frozen_path, ID)
    names = join_by_name(frozen)
    if set(names) != {c['name'] for c in b['components']}:
        raise ValueError('Component set mismatch')
    original, evaluated, components = [], [], []
    maximum_raw_hd = 0
    weighted_delta, bevel_raw_delta = [], []
    for c in b['components']:
        parts = names[c['name']]
        actual = component_points(parts)
        raw = [survey_to_gltf(p) for p in c['original']['positions_survey']]
        eval_ = [survey_to_gltf(p) for p in c['evaluated']['positions_survey']]
        original += raw
        evaluated += eval_
        raw_hd = hausdorff(raw, actual)
        maximum_raw_hd = max(maximum_raw_hd, raw_hd)
        wn_hd = hausdorff(eval_, [survey_to_gltf(p) for p in c['without_weighted_normals']['positions_survey']])
        bevel_hd = hausdorff(raw, [survey_to_gltf(p) for p in c['without_bevel']['positions_survey']])
        weighted_delta.append(wn_hd)
        bevel_raw_delta.append(bevel_hd)
        components.append({'name': c['name'], 'blender_id': c['id'], 'blender_parent': c['parent'],
            'blender_modifiers': c['modifiers'], 'matrix_world_survey': c['matrix_world_survey'],
            'matrix_local_survey': c['matrix_local_survey'], 'blender_scale': c['scale'],
            'original_vertices': c['original']['vertex_count'], 'evaluated_vertices': c['evaluated']['vertex_count'],
            'original_polygons': c['original']['polygon_count'], 'evaluated_polygons': c['evaluated']['polygon_count'],
            'glb_position_vertices': len(actual), 'original_bounds_gltf': bounds(raw),
            'evaluated_bounds_gltf': bounds(eval_), 'frozen_bounds_gltf': bounds(actual),
            'local_positions_raw_vs_frozen_hausdorff_m': hausdorff(
                [survey_to_gltf(p) for p in c['original']['positions_local_survey']],
                [p for part in parts for p in part['positions_local_gltf']]),
            'frozen_minus_evaluated_m': [x-y for x,y in zip(bounds(actual),bounds(eval_))],
            'frozen_minus_evaluated_mm': [1000*(x-y) for x,y in zip(bounds(actual),bounds(eval_))],
            'raw_vs_frozen_hausdorff_m': raw_hd, 'evaluated_vs_frozen_hausdorff_m': hausdorff(eval_, actual),
            'weighted_normals_disabled_hausdorff_m': wn_hd, 'bevel_disabled_vs_raw_hausdorff_m': bevel_hd,
            'original_extrema_survey': c['original']['extrema_survey'], 'evaluated_extrema_survey': c['evaluated']['extrema_survey'],
            'glb_primitives': [{k:v for k,v in p.items() if not k.startswith('positions_')} for p in parts]})
    actual_points = component_points(frozen)
    actual_extrema = []
    for e in extrema(actual_points):
        offset = 0
        for c in frozen:
            if e['vertex'] < offset+c['vertex_count']:
                actual_extrema.append({**e, 'node':c['node'], 'node_index':c['node_index'],
                    'primitive_index':c['primitive_index'], 'accessor':c['position_accessor'],
                    'accessor_vertex':e['vertex']-offset})
                break
            offset += c['vertex_count']
    evaluated_extrema = []
    for e in extrema(evaluated):
        offset = 0
        for c in b['components']:
            n = c['evaluated']['vertex_count']
            if e['vertex'] < offset+n:
                evaluated_extrema.append({**e,'object':c['name'],'evaluated_vertex':e['vertex']-offset})
                break
            offset += n
    manifest_bounds_survey = next(i['authored_bounds_survey'] for i in m['instances'] if i['id']==ID)
    a = manifest_bounds_survey
    manifest_bounds = [a[0],a[2],-a[4],a[3],a[5],-a[1]]
    eval_bounds = bounds(evaluated)
    manifest_eval_delta = max(abs(x-y) for x,y in zip(manifest_bounds,eval_bounds))
    cases = []
    for export in b['diagnostic_exports']:
        path = generated/export['filename']
        if file_identity(path) != export['identity']:
            raise ValueError('Diagnostic export file changed')
        parts = join_by_name(glb_components(path, ID))
        if set(parts) != set(names):
            raise ValueError('Diagnostic component set changed')
        max_raw, max_eval, max_frozen, max_matrix = 0,0,0,0
        for c in b['components']:
            vertices = component_points(parts[c['name']])
            actual_matrix = parts[c['name']][0]['world_matrix_gltf']
            frozen_matrix = names[c['name']][0]['world_matrix_gltf']
            max_matrix = max(max_matrix, *(abs(actual_matrix[i][j]-frozen_matrix[i][j]) for i in range(4) for j in range(4)))
            max_raw = max(max_raw, hausdorff(vertices,[survey_to_gltf(p) for p in c['original']['positions_survey']]))
            max_eval = max(max_eval, hausdorff(vertices,[survey_to_gltf(p) for p in c['evaluated']['positions_survey']]))
            max_frozen = max(max_frozen, hausdorff(vertices,component_points(names[c['name']])))
        cases.append({**export, 'bounds_gltf':union_bounds([q['bounds_gltf'] for p in parts.values() for q in p]),
                      'max_component_hausdorff_original_m':max_raw,'max_component_hausdorff_evaluated_m':max_eval,
                      'max_component_hausdorff_frozen_m':max_frozen,'max_matrix_entry_delta_vs_frozen':max_matrix})
    proxies = {p['id']:p for p in m['collision_proxies']}
    containment = {}
    for c in glb_components(frozen_path):
        if c['id'] not in proxies:
            continue
        item = containment.setdefault(c['id'],{'vertex_samples':0,'minimum_signed_clearance_m':math.inf,'violations_at_1mm':0})
        for point in c['positions_gltf']:
            clearance = prism_clearance(point,proxies[c['id']])
            item['vertex_samples'] += 1
            item['minimum_signed_clearance_m'] = min(item['minimum_signed_clearance_m'],clearance)
            item['violations_at_1mm'] += clearance < -.001
    if len(containment) != 121:
        raise ValueError('Expected 121 actual logical geometries in containment audit')
    tests = {c['case']:c for c in cases}
    proven = (maximum_raw_hd < EPS and manifest_eval_delta < EPS
        and all(c['local_positions_raw_vs_frozen_hausdorff_m'] < EPS for c in components)
        and all(c['max_matrix_entry_delta_vs_frozen'] < 1e-9 for c in cases)
        and max(weighted_delta) < EPS and max(bevel_raw_delta) < EPS
        and b['operator_defaults']['export_apply'] is False
        and all(tests[k]['max_component_hausdorff_frozen_m'] < EPS for k in ('omitted_apply','apply_false','apply_true_without_bevel','apply_false_without_bevel'))
        and all(tests[k]['max_component_hausdorff_evaluated_m'] < EPS for k in ('apply_true','apply_true_without_weighted_normals')))
    matching_version = b['blender_version']=='4.0.2' and b['exporter_version']==[4,0,44] and doc['asset']['generator']=='Khronos glTF Blender I/O v4.0.44'
    report = {'conclusion':'ROOT_CAUSE_CONFIRMED' if proven and matching_version else 'ROOT_CAUSE_PARTIAL' if proven else 'ROOT_CAUSE_UNRESOLVED',
        'label':'READ_ONLY_DIAGNOSTIC; no contract correction authorized',
        'root_cause': ('Evaluated pre-export BEVEL geometry was measured for authored bounds, but uncombined TV components were exported from original meshes: export_apply omitted defaults false. Weighted normals do not change positions.' if proven else 'UNRESOLVED: controlled comparisons did not establish a cause.'),
        'controlled_tests_support_cause':proven,'matching_original_blender_version':matching_version,
        'experiment_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'work_tree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
        'bundle':bundle,'frozen_blend':b['frozen_blend'],'blender_version':b['blender_version'],
        'blend_file_version':b['blend_file_version'],'original_exporter':doc['asset']['generator'],
        'diagnostic_exporter_version':b['exporter_version'],'diagnostic_exporter_module_sha256':b['exporter_module_sha256'],
        'operator_defaults':b['operator_defaults'],'evidence_comparison_epsilon_m':EPS,
        'e0_gate_tolerance_m_unchanged':.003,'e0':'E0_FAIL_UNCHANGED','e1':'BLOCKED_UNCHANGED',
        'union_bounds_gltf':{'original_blender':bounds(original),'evaluated_blender':eval_bounds,'frozen_glb':bounds(actual_points),'manifest':manifest_bounds},
        'manifest_vs_evaluated_max_delta_m':manifest_eval_delta,
        'frozen_minus_manifest_m':[x-y for x,y in zip(bounds(actual_points),manifest_bounds)],
        'actual_glb_extrema':actual_extrema,'evaluated_blender_extrema':evaluated_extrema,
        'components':components,'diagnostic_exports':cases,
        'containment':{'logical_ids':len(containment),'vertex_samples':sum(p['vertex_samples'] for p in containment.values()),
            'violations_at_1mm':sum(p['violations_at_1mm'] for p in containment.values()),'tv':containment[ID],
            'per_id':containment},
        'unverified':['Navigation/human safety/PCCC/accessibility and E1 runtime are not evaluated.',
            'Diagnostic subset export bytes are not frozen artifact bytes; compare positions, not file hashes.']}
    if args.three_report:
        three = json.loads(args.three_report.read_text(encoding='utf-8'))
        delta = max(abs(x-y) for x,y in zip(three['union_bounds_gltf'],bounds(actual_points)))
        report['three'] = {'version':three['three_version'],'browser':three['browser'],
            'manual_vs_python_bounds_max_delta_m':delta,
            'box3_vs_manual_max_delta_m':three['box3_vs_manual_max_delta_m'],
            'components':three['components']}
        if delta > EPS or three['box3_vs_manual_max_delta_m'] > EPS:
            report['conclusion'] = 'ROOT_CAUSE_UNRESOLVED'
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('conclusion','blender_version','controlled_tests_support_cause','manifest_vs_evaluated_max_delta_m','frozen_minus_manifest_m')},indent=2))
    return 0 if proven and (matching_version or not args.require_original_version) else 1


if __name__=='__main__':
    raise SystemExit(main())
