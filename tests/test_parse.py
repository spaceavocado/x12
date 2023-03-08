import unittest

from unittest.mock import patch, mock_open
from x12.parser.context import Context
from x12.parser.loop import Loop
from x12.parser.parse import find_child_schema, find_parent_loop_schema, parse
from x12.schema.schema import Schema, Usage, by_segment

class TestParse(unittest.TestCase):
    @patch('builtins.print')
    def test_file_exception(self, mock_print):
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = FileNotFoundError()
            with self.assertRaises(FileNotFoundError):
                parse("path", Schema("root", Usage.REQUIRED))
            self.assertEqual(mock_print.call_args[0][0], "unable to find path")

        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = OSError()
            with self.assertRaises(OSError):
                parse("path", Schema("root", Usage.REQUIRED))
            self.assertEqual(mock_print.call_args[0][0], "failed to read path")
    
    def test_parse(self):
        ctx = Context("~", "*", ":")
        x12 = Schema("X12", Usage.REQUIRED)
        isa = x12.add_child("ISA", Usage.REQUIRED, by_segment("ISA"))
        st = x12.add_child("ST", Usage.REQUIRED, by_segment("ST"))
        iea = x12.add_child("IEA", Usage.REQUIRED, by_segment("IEA"))
        
        tests = [
            ("ISA*00~", Loop(x12, ctx).add_loop(isa).add_segment("ISA*00").parent.to_xml()),
            (
                "ISA*00~\nIEA*00~",
                Loop(x12, ctx)
                    .add_loop(isa).add_segment("ISA*00").parent
                    .add_loop(iea).add_segment("IEA*00").parent
                    .to_xml()
            ),
            (
                "ISA*00~\nST*00~\r\nNM1*00~\nIEA*00~",
                Loop(x12, ctx)
                    .add_loop(isa).add_segment("ISA*00").parent
                    .add_loop(st).add_segment("ST*00").add_segment("NM1*00").parent
                    .add_loop(iea).add_segment("IEA*00").parent
                    .to_xml()
            )
        ]
        
        for data, expected in tests:
            with patch("builtins.open", mock_open(read_data=data)):
                self.assertEqual(parse("path", x12, ctx).to_xml(), expected)
    
    def test_find_child_schema(self):
        root = Schema("root", Usage.REQUIRED)
        needle_1 = root.add_child("child_1", Usage.REQUIRED, lambda tokens: tokens[0] == "A")
        
        tests = [
            (["bogus"], None),
            (["A"], needle_1),
        ]
        
        for tokens, expect in tests:
            self.assertEqual(find_child_schema(root, tokens), expect)
            
    def test_find_parent_loop_schema(self):
        schema_root = Schema("root", Usage.REQUIRED)
        schema_child_1 = schema_root.add_child("child_1", Usage.REQUIRED, lambda tokens: False)
        schema_child_2 = schema_root.add_child("child_2", Usage.REQUIRED, lambda tokens: tokens[0] == "B")
        schema_child_3 = schema_child_2.add_child("child_3", Usage.REQUIRED, lambda tokens: False)
        
        loop_root = Loop(schema_root, Context("~", "*", ":"))
        loop_child_1 = loop_root.add_loop(schema_child_1)
        loop_child_2 = loop_root.add_loop(schema_child_2)
        loop_child_3 = loop_child_2.add_loop(schema_child_3)
        
        tests = [
            (schema_root, loop_root, ["bogus"], None),
            (schema_child_1, loop_child_1, ["bogus"], None),
            (schema_child_1, loop_child_1, ["B"], (loop_root, schema_child_2)),
            (schema_child_3, loop_child_3, ["B"], (loop_root, schema_child_2)),
        ]
        
        for schema, loop, tokens, expect in tests:
            self.assertEqual(find_parent_loop_schema(schema, tokens, loop), expect)
    
if __name__ == '__main__':
    unittest.main()
