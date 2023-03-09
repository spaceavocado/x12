"""Helper module to analyze the parsed x12."""

from enum import Enum
from typing import Callable, Tuple
from x12.common.colors import color_green, color_yellow, color_red, color_cyan
from x12.parser.loop import Loop
from x12.parser.segment import Segment
from x12.schema.schema import Schema, Segment as SegmentSchema, Usage


def find_matching_segment_schema(
    segment: Segment,
    schema: Schema,
    offset: int
) -> Tuple[int, Segment] | None:
    """Find position and matching segment schema."""

    for index, segment_schema in enumerate(schema.segments[offset:], offset):
        if segment_schema.matches(segment.elements):
            return (index, segment_schema)

    return None


class Occurrence(Enum):
    """Loop/segment occurrence in the parsed x12 loop."""

    EXPECTED = 0
    UNEXPECTED = 1
    MISSING = 2


class SegmentProbe:
    # pylint: disable=too-few-public-methods
    """Segment probe handling printing of the segment/schema subject."""

    def __init__(self, occurrence: Occurrence, subject: Segment | SegmentSchema) -> None:
        self.occurrence = occurrence
        self.segment = subject if isinstance(subject, Segment) else None
        self.schema = subject if isinstance(subject, SegmentSchema) else None

    def __str__(self) -> str:
        def print_segment(segment: Segment, highlight: Callable[[str], str] = lambda x: x) -> str:
            separator = segment.context.element_separator
            return f"{highlight(segment.elements[0])}{separator}" + \
                separator.join(element for element in segment.elements[1:])

        if self.occurrence == Occurrence.EXPECTED:
            return print_segment(self.segment, color_green)
        if self.occurrence == Occurrence.MISSING:
            return f"{color_red(self.schema.name)}"

        return print_segment(self.segment, color_yellow)


def analyze(loop: Loop) -> str:
    """Analyze the parsed loop to determine expected, missing and unexpected segments/loops."""

    def traverse(loop: Loop, expected: bool = True):
        """Traverse recursively the loop."""

        highlight = color_cyan if expected else color_red
        res = f"{'  '*loop.depth}<{highlight(loop.schema.loop_name)}>"

        index = 0
        segment_res: list(SegmentProbe) = []
        for segment in loop.segments:
            found = find_matching_segment_schema(segment, loop.schema, index)
            if found:
                at_index, segment_schema = found
                for missing_schema in loop.schema.segments[index:at_index]:
                    if missing_schema.usage == Usage.REQUIRED:
                        segment_res.append(SegmentProbe(
                            Occurrence.MISSING, missing_schema))

                segment_res.append(SegmentProbe(Occurrence.EXPECTED, segment))
                index = at_index + (1 if segment_schema.unique else 0)
            else:
                segment_res.append(SegmentProbe(
                    Occurrence.UNEXPECTED, segment))

        segment_res += [
            SegmentProbe(Occurrence.MISSING, segment_schema)
                for segment_schema in loop.schema.segments[index:]
                if segment_schema.usage == Usage.REQUIRED
        ]

        for probe in segment_res:
            res += "\n" + '  '*(loop.depth+1) + str(probe)

        for schema in loop.schema.children:
            loops = loop.find_loops(schema.loop_name)
            for child in loops:
                res += "\n" + traverse(child, True)
            if len(loops) == 0 and schema.usage == Usage.REQUIRED:
                res += "\n" + \
                    f"{'  '*(loop.depth+1)}<{color_red(schema.loop_name)}>"

        return res

    return traverse(loop)
