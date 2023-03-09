"""X12 schema"""

from enum import Enum
from typing import Callable


class Usage(Enum):
    """Loop/Segment usage."""

    # Data element must be submitted for the data type and must not be blank.
    REQUIRED = 0
    # This element is not required and may be blank, however, if submitted, it will be edited.
    OPTIONAL = 1
    # Required based upon values of other elements.
    SITUATIONAL = 2
    # Not required, not edited, not collected. If submitted it will be ignored.
    NON_NEEDED = 3

# Loop/segment match predicate.
# I.e. for given segment tokens (list[str]) determine if matches or not.
Predicate = Callable[[list[str]], bool]

def by_segment(segment_id: str) -> Predicate:
    """Loop/segment predicate by segment ID."""

    return lambda tokens: len(tokens) > 0 and tokens[0] == segment_id


def by_segment_element(segment_id: str, element_index: int, element_value: list[str]) -> Predicate:
    """Loop/segment predicate by segment ID and element value(s) at given element index."""

    return lambda tokens: \
        by_segment(segment_id)(tokens) and \
        len(tokens) > element_index and \
        tokens[element_index] in element_value


class Segment:
    """X12 Segment schema"""
    def __init__(self, name: str, usage: Usage, predicate: Predicate, unique: bool = True):
        self.name = name
        self.usage = usage
        self.predicate = predicate
        self.unique = unique

    def matches(self, tokens: list[str]) -> bool:
        """Does the loop matches given the segment elements (tokens)."""

        return self.predicate(tokens)

    def __str__(self) -> str:
        return self.name


class Schema:
    """X12 Loop schema"""

    def __init__(
        self, loop_name: str,
        usage: Usage = Usage.REQUIRED,
        predicate: Predicate = None
    ) -> None:
        self.loop_name = loop_name
        self.usage = usage
        self.predicate = predicate
        self.depth = 0
        self.children: list[Schema] = []
        self.segments: list[Segment] = []
        self.parent: Schema | None = None

    def add_child(self, loop_name: str, usage: Usage, predicate: Predicate):
        """Add a child loop schema."""

        child = Schema(loop_name, usage, predicate)
        child.depth = self.depth + 1
        child.parent = self
        self.children.append(child)
        return child

    def with_segments(self, *segments: list[Segment]):
        """Add loop's segment schemas."""

        for segment in segments:
            self.segments.append(segment)
        return self

    def matches(self, tokens: list[str]) -> bool:
        """Does the loop matches given the segment elements (tokens)."""

        return not self.predicate or self.predicate(tokens)

    def __str__(self) -> str:
        res = f"{'|  '*self.depth}+--{self.loop_name}"
        res += f" ({', '.join(str(segment) for segment in self.segments)})" \
            if len(self.segments) > 0 else ""

        res += "\n"
        res += "".join(str(child) for child in self.children)
        return res
