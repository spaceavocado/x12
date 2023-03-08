import unittest

from x12.parser.context import Context
from x12.parser.loop import Loop
from x12.schema.schema import Schema, Usage

class TestSegment(unittest.TestCase):
    def test_add_loop(self):
        loop = Loop(Schema("root", Usage.REQUIRED), Context("~", "*", ":"))
        child = loop.add_loop(Schema("child", Usage.REQUIRED))
        
        self.assertEqual(loop.loops, [child])
        self.assertIs(child.parent, loop)
        self.assertIs(child.depth, 1)
        
    def test_add_segment(self):
        loop = Loop(Schema("root", Usage.REQUIRED), Context("~", "*", ":"))
        loop.add_segment("1*2*3")
        
        self.assertEqual(len(loop.segments), 1)
        self.assertEqual(str(loop.segments[0]), "1*2*3~")
        
    def test_find_loops(self):
        loop = Loop(Schema("root", Usage.REQUIRED), Context("~", "*", ":"))
        needle_1 = loop.add_loop(Schema("loop_1", Usage.REQUIRED))
        needle_2 = needle_1.add_loop(Schema("loop_2", Usage.REQUIRED))
        needle_3 = needle_1.add_loop(Schema("loop_1", Usage.REQUIRED))
        
        tests = [
            ("bogus", False, []),
            ("bogus", True, []),
            ("loop_1", False, [needle_1]),
            ("loop_1", True, [needle_1, needle_3]),
            ("loop_2", False, []),
            ("loop_2", True, [needle_2]),
        ]
        
        for name, recursive, expect in tests:
            self.assertEqual(loop.find_loops(name, recursive), expect)
            
    def test_find_segments(self):
        loop = Loop(Schema("root", Usage.REQUIRED), Context("~", "*", ":"))
        loop_1 = loop.add_loop(Schema("loop_1", Usage.REQUIRED))
        needle_1 = loop.add_segment("SEG_1").segments[0]
        needle_2 = loop_1.add_segment("SEG_2").segments[0]
        needle_3 = loop_1.add_segment("SEG_1").segments[1]
        
        tests = [
            ("bogus", False, []),
            ("bogus", True, []),
            ("SEG_1", False, [needle_1]),
            ("SEG_1", True, [needle_1, needle_3]),
            ("SEG_2", False, []),
            ("SEG_2", True, [needle_2]),
        ]
        
        for name, recursive, expect in tests:
            self.assertEqual(loop.find_segments(name, recursive), expect)
        
    def test_to_xml(self): 
        root = lambda: Loop(Schema("root", Usage.REQUIRED), Context("~", "*", ":"))
               
        tests = [
            (root(), '<LOOP NAME="root">\n</LOOP>\n'),
            (root().add_segment("PR*1*2"), '<LOOP NAME="root">\n<PR>\n  <PR01><![CDATA[1]]></PR01>\n  <PR02><![CDATA[2]]></PR02>\n</PR>\n</LOOP>\n'),
            (root().add_loop(Schema("child", Usage.REQUIRED)).parent, '<LOOP NAME="root">\n  <LOOP NAME="child">\n  </LOOP>\n</LOOP>\n'),
            (root().add_loop(Schema("child", Usage.REQUIRED)).add_segment("PR*1*2").parent, '<LOOP NAME="root">\n  <LOOP NAME="child">\n  <PR>\n    <PR01><![CDATA[1]]></PR01>\n    <PR02><![CDATA[2]]></PR02>\n  </PR>\n  </LOOP>\n</LOOP>\n'),
        ]

        for loop, expect in tests:
            self.assertEqual(loop.to_xml(), expect)
        
    def test___str__(self): 
        root = lambda: Loop(Schema("root", Usage.REQUIRED), Context("~", "*", ":"))
               
        tests = [
            (root(), ""),
            (root().add_segment("PR*1*2"), "PR*1*2~"),
            (root().add_loop(Schema("child", Usage.REQUIRED)).parent, ""),
            (root().add_loop(Schema("child", Usage.REQUIRED)).add_segment("PR*1*2").parent, "PR*1*2~"),
            (root().add_segment("PR*1*2").add_loop(Schema("child", Usage.REQUIRED)).add_segment("PE*1*2").parent, "PR*1*2~\nPE*1*2~"),
        ]

        for loop, expect in tests:
            self.assertEqual(str(loop), expect)
        
    def test_to_debug(self): 
        root = lambda: Loop(Schema("root", Usage.REQUIRED), Context("~", "*", ":"))
               
        tests = [
            (root(), "<\x1b[92mroot\x1b[0m>:"),
            (root().add_segment("PR*1*2"), "<\x1b[92mroot\x1b[0m>:\n\x1b[96mPR\x1b[0m*1*2"),
            (root().add_loop(Schema("child", Usage.REQUIRED)).parent, "<\x1b[92mroot\x1b[0m>:\n<\x1b[92mchild\x1b[0m>:"),
            (root().add_loop(Schema("child", Usage.REQUIRED)).add_segment("PR*1*2").parent, "<\x1b[92mroot\x1b[0m>:\n<\x1b[92mchild\x1b[0m>:\n  \x1b[96mPR\x1b[0m*1*2"),
        ]

        for loop, expect in tests:
            self.assertEqual(loop.to_debug(), expect)

if __name__ == '__main__':
    unittest.main()
