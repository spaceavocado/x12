"""X12 Loop."""

from x12.common.colors import color_green
from x12.parser.context import Context
from x12.parser.segment import Segment
from x12.schema.schema import Schema

class Loop:
    """X12 Loop object."""

    def __init__(self, schema: Schema, context: Context) -> None:
        self.schema = schema
        self.context = context
        self.depth = 0
        self.loops: list[Loop] = []
        self.segments: list[Segment] = []
        self.parent: Loop = None

    def add_loop(self, schema: Schema):
        """Add a child loop of a given x12 loop schema."""

        child = Loop(schema, self.context)
        child.depth = self.depth + 1
        child.parent = self
        self.loops.append(child)
        return child

    def add_segment(self, segment: str):
        """Add a segment of a given x12 segment schema."""

        child = Segment(self.context)
        child.add_elements(segment)
        self.segments.append(child)
        return self

    def find_loops(self, name: str, recursive: bool = False):
        """Find child loops by loop schema name."""

        res = []
        for loop in self.loops:
            if loop.schema.loop_name == name:
                res.append(loop)
            if recursive:
                res += loop.find_loops(name, recursive)
        return res

    def find_segments(self, name: str, recursive: bool = False) -> list[Segment]:
        """Find segments by segment id (name)."""

        res = []
        for segment in self.segments:
            if segment.elements[0] == name:
                res.append(segment)
        if recursive:
            for loop in self.loops:
                res += loop.find_segments(name, recursive)
        return res

    def to_xml(self) -> str:
        """Serialize loop into XML."""

        res = f'{"  "*self.depth}<LOOP NAME="{self.schema.loop_name}">\n'
        res += "".join(segment.to_xml(self.depth) for segment in self.segments)
        res += "".join(loop.to_xml() for loop in self.loops)
        res += f"{'  '*self.depth}</LOOP>\n"
        return res

    def __str__(self) -> str:
        return "\n".join(
            [str(segment) for segment in self.segments] + [str(loop) for loop in self.loops]
        )

    def to_debug(self) -> str:
        """A helper tool to serialize loop with segment lines with highlighted segment id."""

        prefix = "  "*self.depth
        return "\n".join(
            [f"<{color_green(self.schema.loop_name)}>:"] +
            [prefix + segment.to_debug() for segment in self.segments] +
            [loop.to_debug() for loop in self.loops]
        )
