"""Independent decoder, extrema/point-set and oriented proxy diagnostics tests."""
import math
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from tv_diagnostic_math import accessor_positions, bounds, extrema, hausdorff, matmul, node_matrix, prism_clearance, survey_to_gltf, transform, union_bounds


class DiagnosticMathTests(unittest.TestCase):
    def test_quaternion_translation_and_nonuniform_scale(self):
        n={'rotation':[0,0,math.sin(math.pi/4),math.cos(math.pi/4)],'scale':[2,3,4],'translation':[5,6,7]}
        p=transform(node_matrix(n),[1,0,0])
        for a,b in zip(p,[5,8,7]):
            self.assertAlmostEqual(a,b)

    def test_gltf_column_major_and_parent_composition(self):
        parent=node_matrix({'translation':[1,2,3]})
        child=node_matrix({'matrix':[1,0,0,0,0,1,0,0,0,0,1,0,4,5,6,1]})
        self.assertEqual(transform(matmul(parent,child),[0,0,0]),[5,7,9])

    def test_dense_interleaved_positions_and_offsets(self):
        data=b'xxxx'+struct.pack('<fffIfffI',1,2,3,99,4,5,6,98)
        doc={'bufferViews':[{'byteOffset':4,'byteLength':32,'byteStride':16}],
             'accessors':[{'bufferView':0,'componentType':5126,'type':'VEC3','count':2}]}
        self.assertEqual(accessor_positions(doc,data,0),[[1,2,3],[4,5,6]])
        doc['accessors'][0]['count']=3
        with self.assertRaisesRegex(ValueError,'outside'):
            accessor_positions(doc,data,0)

    def test_union_extremum_changes_component(self):
        a=[[.153,0,0],[1.7,1,1]]
        b=[[.157,0,0],[1.77,1,1]]
        self.assertEqual(union_bounds([bounds(a),bounds(b)]),[.153,0,0,1.77,1,1])
        self.assertEqual(extrema(a)[0]['vertex'],0)

    def test_hausdorff_ignores_split_vertices_and_index_order(self):
        self.assertEqual(hausdorff([[0,0,0],[1,1,1]],[[1,1,1],[0,0,0],[0,0,0]]),0)
        self.assertAlmostEqual(hausdorff([[0,0,0]],[[.008,0,0]]),.008)

    def test_oriented_containment_rejects_AABB_false_inside(self):
        p={'polygon':[[2,0],[3,1],[2,2],[1,1]],'bottom_z':1,'top_z':2}
        self.assertGreater(prism_clearance([2,1.5,-1],p),0)
        self.assertLess(prism_clearance([1.05,1.5,-.05],p),0)
        p['polygon'].reverse()
        self.assertGreater(prism_clearance([2,1.5,-1],p),0)
        self.assertLess(prism_clearance([2,.5,-1],p),0)

    def test_axis_conversion_once(self):
        self.assertEqual(survey_to_gltf([1,2,3]),[1,3,-2])

    def test_degenerate_or_empty_inputs_fail(self):
        with self.assertRaises(ValueError):
            bounds([])
        with self.assertRaises(ValueError):
            hausdorff([],[[0,0,0]])
        with self.assertRaises(ValueError):
            prism_clearance([0,0,0],{'polygon':[[0,0],[1,0],[2,0]],'bottom_z':0,'top_z':1})


if __name__=='__main__':
    unittest.main()
