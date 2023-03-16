# pylint: disable=locally-disabled, missing-module-docstring, missing-function-docstring

import re

import pytest

from x12.parser.context import Context
from x12.parser.segment import Segment


def test_add_elements():
    segment = Segment(Context("~", "*", ":"))
    segment.add_elements("1*2*3")

    assert segment.elements == ["1", "2", "3"]


@pytest.mark.parametrize(
    "segment_line, depth, expected",
    [
        (
            "",
            0,
            "",
        ),
        (
            "PR*2*3",
            0,
            """
<PR>
  <PR01><![CDATA[2]]></PR01>
  <PR02><![CDATA[3]]></PR02>
</PR>
""",
        ),
        (
            "PR*2*3",
            1,
            """
  <PR>
    <PR01><![CDATA[2]]></PR01>
    <PR02><![CDATA[3]]></PR02>
  </PR>
""",
        ),
    ],
)
def test_to_xml(segment_line, depth, expected):
    segment = Segment(Context("~", "*", ":"))
    segment.add_elements(segment_line)

    assert segment.to_xml(depth) == re.sub(r"^\n", "", expected)


def test___str__():
    segment = Segment(Context("~", "*", ":"))
    segment.add_elements("1*2*3")

    assert str(segment) == "1*2*3~"


def test_to_debug():
    segment = Segment(Context("~", "*", ":"))
    segment.add_elements("1*2*3")

    assert segment.to_debug() == "\x1b[96m1\x1b[0m*2*3"
