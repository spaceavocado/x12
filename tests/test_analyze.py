# pylint: disable=locally-disabled, missing-module-docstring, missing-function-docstring

from x12.parser.analyze import (
    Occurrence,
    SegmentProbe,
    analyze,
    find_matching_segment_schema,
)
from x12.parser.context import Context
from x12.parser.loop import Loop
from x12.parser.segment import Segment
from x12.schema.schema import Schema
from x12.schema.schema import Segment as SegmentSchema
from x12.schema.schema import Usage


def test_find_matching_segment_schema():
    ctx = Context("~", "*", ":")
    schema = Schema("schema", Usage.REQUIRED).with_segments(
        SegmentSchema("SEG_1", Usage.REQUIRED, lambda tokens: tokens[0] == "SEG_1"),
        SegmentSchema("SEG_2", Usage.REQUIRED, lambda tokens: tokens[0] == "SEG_2"),
        SegmentSchema("SEG_3", Usage.REQUIRED, lambda tokens: tokens[0] == "SEG_3"),
    )

    tests = [
        (Segment(ctx).add_elements("bogus"), 0, None),
        (Segment(ctx).add_elements("SEG_1"), 1, None),
        (Segment(ctx).add_elements("SEG_1"), 0, (0, schema.segments[0])),
        (Segment(ctx).add_elements("SEG_3"), 0, (2, schema.segments[2])),
        (Segment(ctx).add_elements("SEG_3"), 2, (2, schema.segments[2])),
    ]

    for segment, offset, expected in tests:
        assert find_matching_segment_schema(segment, schema, offset) == expected


def test___str__():
    ctx = Context("~", "*", ":")

    tests = [
        (
            SegmentProbe(Occurrence.EXPECTED, Segment(ctx).add_elements("SEG*DATA")),
            "\x1b[92mSEG\x1b[0m*DATA",
        ),
        (
            SegmentProbe(Occurrence.UNEXPECTED, Segment(ctx).add_elements("SEG*DATA")),
            "\x1b[93mSEG\x1b[0m*DATA",
        ),
        (
            SegmentProbe(
                Occurrence.MISSING,
                SegmentSchema("SEG", Usage.REQUIRED, lambda _: False),
            ),
            "\x1b[91mSEG\x1b[0m",
        ),
    ]

    for probe, expected in tests:
        assert str(probe) == expected


def test_analyze():
    ctx = Context("~", "*", ":")

    segment_1 = SegmentSchema("SG1", Usage.REQUIRED, lambda tokens: tokens[0] == "SG1")
    segment_2 = SegmentSchema("SG2", Usage.OPTIONAL, lambda tokens: tokens[0] == "SG2")
    segment_3 = SegmentSchema("SG3", Usage.REQUIRED, lambda tokens: tokens[0] == "SG3")
    segment_4 = SegmentSchema("SG4", Usage.REQUIRED, lambda tokens: tokens[0] == "SG4")
    segment_5 = SegmentSchema("SG5", Usage.REQUIRED, lambda tokens: tokens[0] == "SG5")
    segment_6 = SegmentSchema(
        "SG6", Usage.OPTIONAL, lambda tokens: tokens[0] == "SG6", False
    )

    root = Schema("X12", Usage.REQUIRED)
    loop_1 = root.add_child(
        "LOOP_1", Usage.REQUIRED, lambda tokens: tokens[0] == "SG1"
    ).with_segments(segment_1, segment_2, segment_3, segment_4)
    loop_3 = root.add_child(
        "LOOP_3", Usage.REQUIRED, lambda tokens: tokens[0] == "SG5"
    ).with_segments(segment_5, segment_6)

    tests = [
        # All as expected
        (
            Loop(root, ctx)
            .add_loop(loop_1)
            .add_segment("SG1*0")
            .add_segment("SG2*0")
            .add_segment("SG3*0")
            .add_segment("SG4*0")
            .parent.add_loop(loop_3)
            .add_segment("SG5*0")
            .parent,
            """
<\x1b[96mX12\x1b[0m>
  <\x1b[96mLOOP_1\x1b[0m>
    \x1b[92mSG1\x1b[0m*0
    \x1b[92mSG2\x1b[0m*0
    \x1b[92mSG3\x1b[0m*0
    \x1b[92mSG4\x1b[0m*0
  <\x1b[96mLOOP_3\x1b[0m>
    \x1b[92mSG5\x1b[0m*0
""",
        ),
        # Missing required loop, skipped optional segment
        (
            Loop(root, ctx)
            .add_loop(loop_1)
            .add_segment("SG1*0")
            .add_segment("SG3*0")
            .add_segment("SG4*0")
            .parent,
            """
<\x1b[96mX12\x1b[0m>
  <\x1b[96mLOOP_1\x1b[0m>
    \x1b[92mSG1\x1b[0m*0
    \x1b[92mSG3\x1b[0m*0
    \x1b[92mSG4\x1b[0m*0
  <\x1b[91mLOOP_3\x1b[0m>
""",
        ),
        # Missing required segment
        (
            Loop(root, ctx)
            .add_loop(loop_1)
            .add_segment("SG1*0")
            .add_segment("SG2*0")
            .parent.add_loop(loop_3)
            .add_segment("SG5*0")
            .parent,
            """
<\x1b[96mX12\x1b[0m>
  <\x1b[96mLOOP_1\x1b[0m>
    \x1b[92mSG1\x1b[0m*0
    \x1b[92mSG2\x1b[0m*0
    \x1b[91mSG3\x1b[0m
    \x1b[91mSG4\x1b[0m
  <\x1b[96mLOOP_3\x1b[0m>
    \x1b[92mSG5\x1b[0m*0
""",
        ),
        # Missing required segment gapped
        (
            Loop(root, ctx)
            .add_loop(loop_1)
            .add_segment("SG1*0")
            .add_segment("SG2*0")
            .add_segment("SG4*0")
            .parent.add_loop(loop_3)
            .add_segment("SG5*0")
            .parent,
            """
<\x1b[96mX12\x1b[0m>
  <\x1b[96mLOOP_1\x1b[0m>
    \x1b[92mSG1\x1b[0m*0
    \x1b[92mSG2\x1b[0m*0
    \x1b[91mSG3\x1b[0m
    \x1b[92mSG4\x1b[0m*0
  <\x1b[96mLOOP_3\x1b[0m>
    \x1b[92mSG5\x1b[0m*0
""",
        ),
        # Unexpected segments
        (
            Loop(root, ctx)
            .add_loop(loop_1)
            .add_segment("SG1*0")
            .add_segment("BOGUS*0")
            .add_segment("SG3*0")
            .add_segment("SG4*0")
            .parent.add_loop(loop_3)
            .add_segment("SG5*0")
            .parent,
            """
<\x1b[96mX12\x1b[0m>
  <\x1b[96mLOOP_1\x1b[0m>
    \x1b[92mSG1\x1b[0m*0
    \x1b[93mBOGUS\x1b[0m*0
    \x1b[92mSG3\x1b[0m*0
    \x1b[92mSG4\x1b[0m*0
  <\x1b[96mLOOP_3\x1b[0m>
    \x1b[92mSG5\x1b[0m*0
""",
        ),
        # Collection of segments
        (
            Loop(root, ctx)
            .add_loop(loop_1)
            .add_segment("SG1*0")
            .add_segment("SG3*0")
            .add_segment("SG4*0")
            .parent.add_loop(loop_3)
            .add_segment("SG5*0")
            .add_segment("SG6*0")
            .add_segment("SG6*0")
            .parent,
            """
<\x1b[96mX12\x1b[0m>
  <\x1b[96mLOOP_1\x1b[0m>
    \x1b[92mSG1\x1b[0m*0
    \x1b[92mSG3\x1b[0m*0
    \x1b[92mSG4\x1b[0m*0
  <\x1b[96mLOOP_3\x1b[0m>
    \x1b[92mSG5\x1b[0m*0
    \x1b[92mSG6\x1b[0m*0
    \x1b[92mSG6\x1b[0m*0
""",
        ),
    ]

    for loop, expected in tests:
        assert analyze(loop) == expected.strip()
