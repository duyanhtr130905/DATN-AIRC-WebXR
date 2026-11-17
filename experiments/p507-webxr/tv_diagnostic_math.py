"""Read-only GLB positions/transforms and exact oriented-prism diagnostics.

No dependency on Blender or Three; comparison code is independently testable.
"""
import hashlib
import json
import math
from pathlib import Path
import struct

IDENTITY = [[float(i == j) for j in range(4)] for i in range(4)]


def matmul(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def transform(m, p):
    q = [sum(m[i][j]*([*p, 1][j]) for j in range(4)) for i in range(4)]
    if not math.isclose(q[3], 1, abs_tol=1e-8):
        raise ValueError('Non-affine transform unsupported')
    return q[:3]


def node_matrix(n):
    if 'matrix' in n:
        a = n['matrix']
        return [[a[j*4+i] for j in range(4)] for i in range(4)]
    x, y, z, w = n.get('rotation', [0, 0, 0, 1])
    s = n.get('scale', [1, 1, 1])
    t = n.get('translation', [0, 0, 0])
    a = [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
         [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
         [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]
    return [[*(a[i][j]*s[j] for j in range(3)), t[i]] for i in range(3)]+[[0, 0, 0, 1]]


def read_glb(path):
    blob = Path(path).read_bytes()
    if len(blob) < 20 or struct.unpack_from('<4sII', blob) != (b'glTF', 2, len(blob)):
        raise ValueError('Invalid GLB header')
    chunks = {}
    offset = 12
    while offset < len(blob):
        length, kind = struct.unpack_from('<I4s', blob, offset)
        offset += 8
        if offset+length > len(blob):
            raise ValueError('Truncated GLB chunk')
        chunks[kind] = blob[offset:offset+length]
        offset += length
    return json.loads(chunks[b'JSON']), chunks[b'BIN\x00']


def accessor_positions(doc, binary, index):
    a = doc['accessors'][index]
    if a['componentType'] != 5126 or a['type'] != 'VEC3' or a.get('sparse'):
        raise ValueError('Diagnostic requires dense FLOAT VEC3 positions')
    view = doc['bufferViews'][a['bufferView']]
    if view.get('buffer', 0) != 0:
        raise ValueError('External buffer unsupported')
    start = view.get('byteOffset', 0)+a.get('byteOffset', 0)
    stride = view.get('byteStride', 12)
    if stride < 12 or start+(a['count']-1)*stride+12 > view.get('byteOffset', 0)+view['byteLength']:
        raise ValueError('Accessor outside buffer view')
    return [list(struct.unpack_from('<fff', binary, start+i*stride)) for i in range(a['count'])]


def extrema(vertices):
    if not vertices:
        raise ValueError('Cannot bound empty geometry')
    result = []
    for high in (False, True):
        for axis in range(3):
            index = (max if high else min)(range(len(vertices)), key=lambda i: vertices[i][axis])
            result.append({'axis': 'xyz'[axis]+('max' if high else 'min'),
                           'vertex': index, 'point': vertices[index], 'value': vertices[index][axis]})
    return result


def bounds(vertices):
    return [e['value'] for e in extrema(vertices)]


def union_bounds(items):
    if not items:
        raise ValueError('Empty bounds union')
    return [min(b[i] for b in items) for i in range(3)]+[max(b[i] for b in items) for i in range(3, 6)]


def glb_components(path, ident=None):
    doc, binary = read_glb(path)
    found = []
    seen = set()

    def visit(index, parent_world, inherited_id, parent):
        if index in seen:
            raise ValueError('Node repeated/cyclic in active glTF scene')
        seen.add(index)
        n = doc['nodes'][index]
        own = n.get('extras', {}).get('survey_instance_id', inherited_id)
        world = matmul(parent_world, node_matrix(n))
        if 'mesh' in n and (ident is None or own == ident):
            for primitive_index, primitive in enumerate(doc['meshes'][n['mesh']]['primitives']):
                a = primitive['attributes']['POSITION']
                local = accessor_positions(doc, binary, a)
                vertices = [transform(world, v) for v in local]
                found.append({'id': own, 'node_index': index, 'node': n.get('name'), 'parent_index': parent,
                              'mesh_index': n['mesh'], 'primitive_index': primitive_index, 'position_accessor': a,
                              'mode': primitive.get('mode', 4), 'vertex_count': len(vertices),
                              'index_count': doc['accessors'][primitive['indices']]['count'] if 'indices' in primitive else None,
                              'world_matrix_gltf': world, 'bounds_gltf': bounds(vertices),
                              'extrema_gltf': extrema(vertices), 'positions_gltf': vertices,
                              'positions_local_gltf': local, 'extras': n.get('extras', {})})
        for child in n.get('children', []):
            visit(child, world, own, index)
    for root in doc['scenes'][doc.get('scene', 0)]['nodes']:
        visit(root, IDENTITY, None, None)
    return found


def survey_to_gltf(p):
    return [p[0], p[2], -p[1]]


def hausdorff(a, b):
    """Symmetric point-set distance, independent of triangulation/index order."""
    if not a or not b:
        raise ValueError('Empty point set')
    def directed(xs, ys):
        return max(min(math.dist(x, y) for y in ys) for x in xs)
    return max(directed(a, b), directed(b, a))


def prism_clearance(point_gltf, proxy):
    x, z, negative_y = point_gltf
    y = -negative_y
    poly = proxy['polygon']
    signed_area = sum(a[0]*b[1]-b[0]*a[1] for a, b in zip(poly, poly[1:]+poly[:1]))
    if abs(signed_area) < 1e-12:
        raise ValueError('Degenerate proxy')
    winding = 1 if signed_area > 0 else -1
    distances = []
    for a, b in zip(poly, poly[1:]+poly[:1]):
        length = math.dist(a, b)
        if length < 1e-12:
            raise ValueError('Degenerate edge')
        distances.append(winding*((b[0]-a[0])*(y-a[1])-(b[1]-a[1])*(x-a[0]))/length)
    return min(*distances, z-proxy['bottom_z'], proxy['top_z']-z)


def file_identity(path):
    blob = Path(path).read_bytes()
    return {'bytes': len(blob), 'sha256': hashlib.sha256(blob).hexdigest()}
