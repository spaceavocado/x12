# pylint: disable=locally-disabled, missing-module-docstring, missing-function-docstring

import pytest

from x12.schema.schema import Schema, Segment, Usage, by_segment, by_segment_element


@pytest.mark.parametrize(
    "tokens, expected",
    [
        ([], False),
        (["bogus"], False),
        (["needle"], True),
    ],
)
def test_by_segment(tokens, expected):
    assert by_segment("needle")(tokens) == expected


@pytest.mark.parametrize(
    "tokens, expected",
    [
        ([], False),
        (["bogus"], False),
        (["needle"], False),
        (["needle", "bogus"], False),
        (["needle", "val"], True),
    ],
)
def test_by_segment_element(tokens, expected):
    assert by_segment_element("needle", 1, ["val"])(tokens) == expected


def test_add_child():
    root = Schema("root", Usage.REQUIRED)
    child = root.add_child("child", Usage.REQUIRED, lambda: True)

    assert child.depth == 1
    assert child.parent is root
    assert root.children == [child]


def test_with_segments():
    root = Schema("root", Usage.REQUIRED)
    segment = Segment("SEGMENT", Usage.REQUIRED, lambda: True)
    root.with_segments(segment)

    assert root.segments == [segment]


def test_matches():
    root = Schema("root", Usage.REQUIRED, lambda tokens: tokens[0] == "YES")

    assert root.matches(["YES"]) is True
    assert root.matches(["NO"]) is False


@pytest.mark.parametrize(
    "schema, expect",
    [
        (Schema("root", Usage.REQUIRED), "+--root\n"),
        (
            Schema("root", Usage.REQUIRED).with_segments(
                Segment("S1", Usage.REQUIRED, lambda: True),
                Segment("S2", Usage.REQUIRED, lambda: True),
            ),
            "+--root (S1, S2)\n",
        ),
        (
            Schema("root", Usage.REQUIRED)
            .add_child("child", Usage.REQUIRED, lambda: True)
            .parent,
            "+--root\n|  +--child\n",
        ),
    ],
)
def test___str__(schema, expect):
    assert str(schema) == expect
