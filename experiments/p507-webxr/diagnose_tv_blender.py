"""Blender-only read/diagnostic exports; frozen .blend/GLB/manifest never written.

blender --background --disable-autoexec --python-exit-code 1 --python THIS -- --artifact-dir ... --output-dir ...
"""
import argparse
import hashlib
import inspect
import json
from pathlib import Path
import sys

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from tv_diagnostic_math import bounds, extrema, file_identity, survey_to_gltf

IDENT = 'P507-TV-LARGE'


def arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('--artifact-dir', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    return ap.parse_args(sys.argv[sys.argv.index('--')+1:])


def points(obj, evaluated=False):
    at = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()) if evaluated else obj
    mesh = at.to_mesh() if evaluated else obj.data
    try:
        local = [[float(c) for c in v.co] for v in mesh.vertices]
        world = [[float(c) for c in (at.matrix_world @ v.co)] for v in mesh.vertices]
        return {'vertex_count': len(world), 'polygon_count': len(mesh.polygons),
                'bounds_survey': bounds(world), 'bounds_gltf': bounds([survey_to_gltf(p) for p in world]),
                'extrema_survey': extrema(world), 'positions_survey': world, 'positions_local_survey': local}
    finally:
        if evaluated:
            at.to_mesh_clear()


def modifier_info(mod):
    record = {'name': mod.name, 'type': mod.type, 'show_viewport': mod.show_viewport, 'show_render': mod.show_render}
    for key in ('width', 'segments', 'affect', 'limit_method', 'angle_limit', 'offset_type',
                'use_clamp_overlap', 'loop_slide', 'harden_normals', 'weight', 'mode', 'keep_sharp', 'thresh'):
        if hasattr(mod, key):
            value = getattr(mod, key)
            if isinstance(value, (str, int, float, bool)):
                record[key] = value
    return record


def open_frozen(path):
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
    bpy.context.view_layer.update()
    return sorted([o for o in bpy.context.scene.objects if o.type == 'MESH' and o.get('survey_instance_id') == IDENT], key=lambda o: o.name)


def disable(objects, kinds):
    for o in objects:
        for mod in o.modifiers:
            if mod.type in kinds:
                mod.show_viewport = False
                mod.show_render = False
    bpy.context.view_layer.update()


def main():
    args = arguments()
    artifact = args.artifact_dir.resolve()
    output = args.output_dir.resolve()
    if artifact == output or artifact in output.parents:
        raise ValueError('Diagnostic output must be separate from frozen artifact')
    output.mkdir(parents=True, exist_ok=True)
    blend = artifact/'P507_G1_G2_PROVISIONAL.blend'
    original_identity = file_identity(blend)
    manifest = json.loads((artifact/'asset-manifest.json').read_text(encoding='utf-8'))
    objects = open_frozen(blend)
    if len(objects) != 5:
        raise ValueError('Frozen TV must contain five components')
    import io_scene_gltf2
    exporter_file = Path(inspect.getfile(io_scene_gltf2))
    props = bpy.ops.export_scene.gltf.get_rna_type().properties
    report = {'label': 'DIAGNOSTIC_EXPORT_ONLY', 'asset_source_sha': manifest['source_sha'],
              'asset_checkout_sha': manifest['checkout_sha'], 'frozen_blend': original_identity,
              'frozen_glb': file_identity(artifact/'P507_G1_G2_PROVISIONAL.glb'),
              'blender_version': bpy.app.version_string, 'blend_file_version': list(bpy.data.version),
              'exporter_version': list(getattr(io_scene_gltf2, 'bl_info', {}).get('version', [])),
              'exporter_module_sha256': hashlib.sha256(exporter_file.read_bytes()).hexdigest(),
              'operator_defaults': {key: props[key].default for key in ('export_apply','export_yup','export_extras','use_selection')},
              'components': [], 'diagnostic_exports': [], 'e0': 'E0_FAIL_UNCHANGED', 'e1': 'BLOCKED_UNCHANGED'}
    for o in objects:
        report['components'].append({'name': o.name, 'id': o['survey_instance_id'],
            'data_name': o.data.name, 'parent': o.parent.name if o.parent else None,
            'matrix_world_survey': [list(row) for row in o.matrix_world],
            'matrix_local_survey': [list(row) for row in o.matrix_local],
            'location': list(o.location), 'rotation_mode': o.rotation_mode,
            'rotation_euler': list(o.rotation_euler), 'scale': list(o.scale),
            'modifiers': [modifier_info(m) for m in o.modifiers],
            'original': points(o), 'evaluated': points(o, True)})
    for label, kinds in [('without_weighted_normals', {'WEIGHTED_NORMAL'}), ('without_bevel', {'BEVEL'}), ('without_both', {'BEVEL','WEIGHTED_NORMAL'})]:
        objects = open_frozen(blend)
        disable(objects, kinds)
        for item, o in zip(report['components'], objects):
            if item['name'] != o.name:
                raise ValueError('Component ordering mismatch')
            item[label] = points(o, True)
    # Selection intentionally includes TV only in separate exports; compare point sets,
    # never ZIP/GLB bytes, and never use these exports as frozen R4 inputs.
    cases = [('omitted_apply', None, set()), ('apply_false', False, set()),
             ('apply_true', True, set()), ('apply_true_without_weighted_normals', True, {'WEIGHTED_NORMAL'}),
             ('apply_true_without_bevel', True, {'BEVEL'}), ('apply_false_without_bevel', False, {'BEVEL'})]
    for label, apply, disabled in cases:
        objects = open_frozen(blend)
        disable(objects, disabled)
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        filename = 'DIAGNOSTIC_EXPORT_ONLY_'+label+'.glb'
        options = {'filepath': str(output/filename), 'export_format': 'GLB', 'use_selection': True,
                   'export_yup': True, 'export_extras': True}
        if apply is not None:
            options['export_apply'] = apply
        result = bpy.ops.export_scene.gltf(**options)
        if 'FINISHED' not in result:
            raise RuntimeError('Diagnostic export failed: '+label)
        report['diagnostic_exports'].append({'case': label, 'filename': filename,
            'export_apply': 'OMITTED_OPERATOR_DEFAULT' if apply is None else apply,
            'disabled_modifier_types': sorted(disabled), 'identity': file_identity(output/filename)})
    if file_identity(blend) != original_identity:
        raise RuntimeError('Frozen blend was modified')
    (output/'blender-tv-report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'blender':report['blender_version'], 'exporter':report['exporter_version'],
        'defaults':report['operator_defaults'], 'components':len(report['components']), 'exports':len(report['diagnostic_exports']),
        'frozen_blend_unchanged':True}, indent=2))


if __name__ == '__main__':
    main()
