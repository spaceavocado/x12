# pylint: disable=locally-disabled, missing-module-docstring, missing-function-docstring

from unittest.mock import mock_open, patch

import pytest

from x12.parser.context import Context
from x12.parser.loop import Loop
from x12.parser.parse import find_child_schema, find_parent_loop_schema, parse
from x12.schema.schema import Schema, Usage, by_segment


@patch("builtins.print")
def test_file_exception(mock_print):
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = FileNotFoundError()
        with pytest.raises(FileNotFoundError):
            parse("path", Schema("root", Usage.REQUIRED))
        assert mock_print.call_args[0][0] == "unable to find path"

    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = OSError()
        with pytest.raises(OSError):
            parse("path", Schema("root", Usage.REQUIRED))
        assert mock_print.call_args[0][0] == "failed to read path"


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            "ISA*00~",
            """
<LOOP NAME="X12">
  <LOOP NAME="ISA">
    <ISA>
      <ISA01><![CDATA[00]]></ISA01>
    </ISA>
  </LOOP>
</LOOP>
""",
        ),
        (
            "ISA*00~\nIEA*00~",
            """
<LOOP NAME="X12">
  <LOOP NAME="ISA">
    <ISA>
      <ISA01><![CDATA[00]]></ISA01>
    </ISA>
  </LOOP>
  <LOOP NAME="IEA">
    <IEA>
      <IEA01><![CDATA[00]]></IEA01>
    </IEA>
  </LOOP>
</LOOP>
""",
        ),
        (
            "ISA*00~\nST*00~\r\nNM1*00~\nIEA*00~",
            """
<LOOP NAME="X12">
  <LOOP NAME="ISA">
    <ISA>
      <ISA01><![CDATA[00]]></ISA01>
    </ISA>
  </LOOP>
  <LOOP NAME="ST">
    <ST>
      <ST01><![CDATA[00]]></ST01>
    </ST>
    <NM1>
      <NM101><![CDATA[00]]></NM101>
    </NM1>
  </LOOP>
  <LOOP NAME="IEA">
    <IEA>
      <IEA01><![CDATA[00]]></IEA01>
    </IEA>
  </LOOP>
</LOOP>
""",
        ),
    ],
)
def test_evaluate(data, expected):
    ctx = Context("~", "*", ":")
    x12 = Schema("X12", Usage.REQUIRED)
    x12.add_child("ISA", Usage.REQUIRED, by_segment("ISA"))
    x12.add_child("ST", Usage.REQUIRED, by_segment("ST"))
    x12.add_child("IEA", Usage.REQUIRED, by_segment("IEA"))

    with patch("builtins.open", mock_open(read_data=data)):
        assert parse("mocked_file", x12, ctx).to_xml() == expected.lstrip()


def test_find_child_schema():
    root = Schema("root", Usage.REQUIRED)
    needle_1 = root.add_child(
        "child_1", Usage.REQUIRED, lambda tokens: tokens[0] == "FIND_ME"
    )

    tests = [
        (["bogus"], None),
        (["FIND_ME"], needle_1),
    ]

    for tokens, expected in tests:
        assert find_child_schema(root, tokens) == expected


def test_find_parent_loop_schema():
    schema_root = Schema("root", Usage.REQUIRED)
    schema_child_1 = schema_root.add_child("child_1", Usage.REQUIRED, lambda _: False)
    schema_child_2 = schema_root.add_child(
        "child_2", Usage.REQUIRED, lambda tokens: tokens[0] == "FIND_ME"
    )
    schema_child_3 = schema_child_2.add_child(
        "child_3", Usage.REQUIRED, lambda _: False
    )

    loop_root = Loop(schema_root, Context("~", "*", ":"))
    loop_child_1 = loop_root.add_loop(schema_child_1)
    loop_child_2 = loop_root.add_loop(schema_child_2)
    loop_child_3 = loop_child_2.add_loop(schema_child_3)

    tests = [
        (schema_root, loop_root, ["bogus"], None),
        (schema_child_1, loop_child_1, ["bogus"], None),
        (schema_child_1, loop_child_1, ["FIND_ME"], (loop_root, schema_child_2)),
        (schema_child_3, loop_child_3, ["FIND_ME"], (loop_root, schema_child_2)),
    ]

    for schema, loop, tokens, expected in tests:
        assert find_parent_loop_schema(schema, tokens, loop) == expected
