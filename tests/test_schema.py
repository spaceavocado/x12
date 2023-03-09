import unittest

from x12.schema.schema import Schema, Segment, Usage, by_segment, by_segment_element


class TestPredicate(unittest.TestCase):
    def test_by_segment(self):
        predicate = by_segment('needle')
        tests = [
            ([], False),
            (['bogus'], False),
            (['needle'], True),
        ]
        for arg, expect in tests:
            self.assertEqual(predicate(arg), expect)
            
    def test_by_segment_element(self):
        predicate = by_segment_element('needle', 1, ['val'])
        tests = [
            ([], False),
            (['bogus'], False),
            (['needle'], False),
            (['needle', 'bogus'], False),
            (['needle', 'val'], True),
        ]
        for arg, expect in tests:
            self.assertEqual(predicate(arg), expect)
            

class TestSchema(unittest.TestCase):
    def test_add_child(self):
        root = Schema("root", Usage.REQUIRED)
        child = root.add_child("child", Usage.REQUIRED, lambda: True)

        self.assertEqual(child.depth, 1)
        self.assertIs(child.parent, root)
        self.assertEqual(root.children, [child])

    def test_with_segments(self):
        root = Schema("root", Usage.REQUIRED)
        segment = Segment("SEGMENT", Usage.REQUIRED, lambda: True)
        root.with_segments(segment)
        
        self.assertEqual(root.segments, [segment])

    def test_matches(self):
        root = Schema("root", Usage.REQUIRED, lambda tokens: tokens[0] == "YES")
        
        self.assertEqual(root.matches(["YES"]), True)
        self.assertEqual(root.matches(["NO"]), False)
        
    def test___str__(self):
        segment_1 = Segment("S1", Usage.REQUIRED, lambda: True)
        segment_2 = Segment("S2", Usage.REQUIRED, lambda: True)
        
        tests = [
            (Schema("root", Usage.REQUIRED), "+--root\n"),
            (
                Schema("root", Usage.REQUIRED).with_segments(segment_1, segment_2),
                "+--root (S1, S2)\n"
            ),
            (
                Schema("root", Usage.REQUIRED).add_child("child", Usage.REQUIRED, lambda: True).parent,
                "+--root\n|  +--child\n"
            )
        ]
        
        for schema, expect in tests:
            self.assertEqual(str(schema), expect)

if __name__ == '__main__':
    unittest.main()