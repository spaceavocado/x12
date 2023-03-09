"""X12 file parser."""

from typing import Tuple
from x12.parser.context import Context
from x12.parser.loop import Loop
from x12.schema.schema import Schema


def parse (file_path: str, x12: Schema, context: Context = Context("~", "*", ":")):
    """Parse source x12 file with given schema."""

    content = ''
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        print(f"unable to find {file_path}")
        raise
    except OSError:
        print(f"failed to read {file_path}")
        raise

    # Remove the line-breaks and than split by segment separator to get the lines.
    lines = content.replace("\r", "").replace("\n", "").split(context.segment_separator)

    root = Loop(x12, context)
    head = root
    schema = x12

    for line in lines:
        if line.strip() == "":
            continue

        tokens = line.split(context.element_separator)
        child_schema = find_child_schema(schema, tokens)
        if child_schema:
            schema = child_schema
            head = head.add_loop(schema)
            head.add_segment(line)
            continue

        parent = find_parent_loop_schema(schema, tokens, head)
        if parent:
            parent_loop, parent_schema = parent
            schema = parent_schema
            head = parent_loop.add_loop(schema)
            head.add_segment(line)
            continue

        head.add_segment(line)

    return root

def find_child_schema (schema: Schema, tokens: list[str]) -> Schema | None:
    """Find matching child loop schema by schema predicate for given segment (tokens)."""

    for node in schema.children:
        if is_matching_loop(node, tokens):
            return node
    return None

def find_parent_loop_schema (schema: Schema, tokens: list[str], loop: Loop) \
    -> Tuple[Loop, Schema] | None:
    """
    Find recursively matching parent loop and schema,
    by schema predicate for given segment (tokens).
    """

    if not schema.parent or not loop.parent:
        return None

    for node in schema.parent.children:
        if is_matching_loop(node, tokens):
            return (loop.parent, node)

    return find_parent_loop_schema(schema.parent, tokens, loop.parent)

def is_matching_loop(schema: Schema, tokens: list[str]) -> bool:
    """Determine if the schema matches for given segment (tokens)."""

    return schema.matches(tokens)
