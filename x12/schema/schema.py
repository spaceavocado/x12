"""X12 schema"""

from enum import Enum
from typing import Callable


class Usage(Enum):
    """Loop/Segment usage."""

    REQUIRED = 0
    OPTIONAL = 1
    SITUATIONAL = 2

# Loop/segment match predicate.
# I.e. for given segment tokens (list[str]) determine if matches or not.
Predicate = Callable[[list[str]], bool]

def by_segment(segment_id: str) -> Predicate:
    """Loop/segment predicate by segment ID."""

    return lambda tokens: len(tokens) > 0 and tokens[0] == segment_id


def by_segment_element(segment_id: str, element_index: int, element_value: list[str]) -> Predicate:
    """Loop/segment predicate by segment ID and element value(s) at given element index."""

    return lambda tokens: by_segment(segment_id)(tokens) and len(tokens) > element_index and tokens[element_index] in element_value


class Segment:
    """X12 Segment schema"""
    def __init__(self, name: str, usage: Usage, predicate: Predicate, unique: bool = True):
        self.name = name
        self.usage = usage
        self.predicate = predicate
        self.unique = unique


class Schema:
    """X12 Loop schema"""

    def __init__(self, loop_name: str, usage: Usage = Usage.REQUIRED, predicate: Predicate = None) -> None:
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

    def with_segments(self, segments: list[Segment]):
        """Add loop's segment schemas."""

        for child in segments:
            self.segments.append(child)
        return self

    def matches(self, tokens: list[str]) -> bool:
        """Does the loop matches given the segment elements (tokens)."""

        return not self.predicate or self.predicate(tokens)

    def __str__(self) -> str:
        res = f"{'|  '*self.depth}+--{self.loop_name}"
        res += f" ({', '.join(segment.name for segment in self.segments)})" if len(self.segments) > 0 else ""
        res += "\n"
        res += "".join(str(child) for child in self.children)
        return res
