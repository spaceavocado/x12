# pylint: disable=locally-disabled, too-few-public-methods

"""X12 context."""

class Context:
    """X12 context object."""

    def __init__(
        self,
        segment_separator: str,
        element_separator: str,
        composite_element_separator: str
    ) -> None:
        self.segment_separator = segment_separator
        self.element_separator = element_separator
        self.composite_element_separator = composite_element_separator
