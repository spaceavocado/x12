"""X12 Loop Segment."""

from x12.common.colors import color_cyan
from x12.parser.context import Context

class Segment:
    """X12 Loop Segment object."""

    def __init__(self, context: Context) -> None:
        self.context = context
        self.elements = []

    def add_elements(self, segment: str):
        """Add segment elements from a segment line."""

        self.elements = segment.split(self.context.element_separator)
        return self

    def to_xml(self, depth: int = 0) -> str:
        """Serialize segment into XML."""

        if len(self.elements) == 0:
            return ""

        res = f"{'  '*depth}<{self.elements[0]}>\n"
        for index, element in enumerate(self.elements[1:], 1):
            tag = self.elements[0] + str(index).zfill(2)
            res += f"{'  '*(depth+1)}<{tag}><![CDATA[{element}]]></{tag}>"
            res += "\n" if index <= len(self.elements) else ""
        res += f"{'  '*depth}</{self.elements[0]}>\n"
        return res


    def __str__(self) -> str:
        return self.context.element_separator.join(element for element in self.elements) + \
            self.context.segment_separator


    def to_debug(self) -> str:
        """A helper tool to serialize segment into segment line with highlighted segment id."""

        return f"{color_cyan(self.elements[0])}{self.context.element_separator}" + \
            self.context.element_separator.join(element for element in self.elements[1:])
