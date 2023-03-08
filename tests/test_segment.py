import unittest

from x12.parser.context import Context
from x12.parser.segment import Segment

class TestSegment(unittest.TestCase):
    def test_add_elements(self):
        segment = Segment(Context("~", "*", ":"))
        segment.add_elements("1*2*3")
        

        self.assertEqual(segment.elements, ["1", "2", "3"])
        
    def test_to_xml(self):
        segment = Segment(Context("~", "*", ":"))
        segment.add_elements("PR*2*3")
        
        tests = [
            (0, "<PR>\n  <PR01><![CDATA[2]]></PR01>\n  <PR02><![CDATA[3]]></PR02>\n</PR>\n"),
            (1, "  <PR>\n    <PR01><![CDATA[2]]></PR01>\n    <PR02><![CDATA[3]]></PR02>\n  </PR>\n"),
        ]
        for depth, expect in tests:
            self.assertEqual(segment.to_xml(depth), expect)
            
        segment = Segment(Context("~", "*", ":"))
        self.assertEqual(segment.to_xml(), "")
        
    def test___str__(self):
        segment = Segment(Context("~", "*", ":"))
        segment.add_elements("1*2*3")
        
        self.assertEqual(str(segment), "1*2*3~")
        
    def test_to_debug(self):
        segment = Segment(Context("~", "*", ":"))
        segment.add_elements("1*2*3")
        

        self.assertEqual(segment.to_debug(), "\x1b[96m1\x1b[0m*2*3")

if __name__ == '__main__':
    unittest.main()
