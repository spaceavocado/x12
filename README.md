# Space Avocado X12 Parser
A simple X12 file parser, allowing to parse X12 loops and segment based on schema.

*Credit: Inspired by [Maven Central X12 Parser](https://github.com/ryanco/x12-parser).*

> X12 is a message formatting standard used with Electronic Data Interchange (EDI) documents for trading partners to share electronic business documents in an agreed-upon and standard format. It is the most common EDI standard used in the United States.

**X12 Document List**: https://en.wikipedia.org/wiki/X12_Document_List

**X12 Schematic:**

![X12-Schematic](https://user-images.githubusercontent.com/1224609/223794653-9b3abcfe-cb6b-4bd5-aec6-14f07e9280e4.gif)

See more details at https://x12.org/.

---

**Table of Content**
- [Space Avocado X12 Parser](#space-avocado-x12-parser)
  - [Installation](#installation)
  - [How to use](#how-to-use)
    - [1. Define a schema for the x12 file to be parsed.](#1-define-a-schema-for-the-x12-file-to-be-parsed)
      - [Loop/Segment Matcher Predicate](#loopsegment-matcher-predicate)
      - [Loop schema could be decorated with segment schemas](#loop-schema-could-be-decorated-with-segment-schemas)
    - [2. Parse](#2-parse)
      - [Loop Operations](#loop-operations)
      - [Segment Operations](#segment-operations)
    - [3. Optional: Analyze parsed loop.](#3-optional-analyze-parsed-loop)
  - [Contributing](#contributing)
  - [License](#license)

---

## Installation

You can install the **Space Avocado X12 Parser** from [PyPI](https://pypi.org/project/spaceavocado-x12/):

    python -m pip install spaceavocado-x12

The reader is supported on Python 3.7 and above.

## How to use

### 1. Define a schema for the x12 file to be parsed.

```py
from x12.schema.schema import Schema, Usage, by_segment, by_segment_element

def schema() -> Schema:
    x12 = Schema('X12')
    isa = x12.add_child('ISA', Usage.REQUIRED, by_segment('ISA'))
    gs = isa.add_child('GS', Usage.REQUIRED, by_segment('GS'))
    st = gs.add_child('ST', Usage.REQUIRED, by_segment_element('ST', 1, ['835']))

    st.add_child('1000A', Usage.REQUIRED, by_segment_element('N1', 1, ['PR']))
    st.add_child('1000B', Usage.REQUIRED, by_segment_element('N1', 1, ['PE']))

    mm = st.add_child('2000', Usage.REQUIRED, by_segment('LX'))
    mmc = mm.add_child('2100', Usage.REQUIRED, by_segment('CLP'))
    mmc.add_child('2110', Usage.REQUIRED, by_segment('SVC'))

    gs.add_child('SE', Usage.REQUIRED, by_segment('SE'))
    isa.add_child('GE', Usage.REQUIRED, by_segment('GE'))
    x12.add_child('IEA', Usage.REQUIRED, by_segment('IEA'))

    return x12
```

To see the structure of the schema: ```print(schema())```.

```
+--X12
|  +--ISA
|  |  +--GS
|  |  |  +--ST
|  |  |  |  +--1000A
|  |  |  |  +--1000B
|  |  |  |  +--2000
|  |  |  |  |  +--2100
|  |  |  |  |  |  +--2110
|  |  |  +--SE
|  |  +--GE
|  +--IEA
```

The above is an example of true nested structure of x12 835 document schema but schema could be defied in any, i.e. you can get flat structure if needed, e.g.:

```py
from x12.schema.schema import Schema, Usage, by_segment, by_segment_element

def schema() -> Schema:
    x12 = Schema('X12')

    x12.add_child('1000A', Usage.REQUIRED, by_segment_element('N1', 1, ['PR']))
    x12.add_child('1000B', Usage.REQUIRED, by_segment_element('N1', 1, ['PE']))

    x12.add_child('2000', Usage.REQUIRED, by_segment('LX'))
    x12.add_child('2100', Usage.REQUIRED, by_segment('CLP'))
    x12.add_child('2110', Usage.REQUIRED, by_segment('SVC'))

    return x12
```

```
+--X12
|  +--1000A
|  +--1000B
|  +--2000
|  +--2100
|  +--2110
```

#### Loop/Segment Matcher Predicate
There are 2 build-in predicates, for the most commonly used situations:

**by_segment**
- Used to determine a **loop** by **segment ID**.
- E.g.: ```by_segment('LX')``` matches this segment ```LX*DATA_1*DATA_N~```.

**by_segment_element**
- Used to determine a **loop** by **segment ID** and **element value(s)** at given **element index**.
- In many situations loop could start with the same segment id but differing the element values.
- E.g.: ```by_segment_element('N1', 1, ['PR', 'PE'])``` matches this segment ```N1*PR*DATA_N~``` or ```N1*PE*DATA_N~``` but not ```N1*QE*DATA_N~```.

A custom predicate function could be used:
- ```x12.add_child('2000', Usage.REQUIRED, lambda tokens: tokens[0] == "LX")```.
- The above is an equivalent of ```x12.add_child('2000', Usage.REQUIRED, by_segment('LX'))```.

#### Loop schema could be decorated with segment schemas
This is useful of [Analyze parsed loop](#3-optional-analyze-parsed-loop).

Example:
```py
from x12.schema.schema import Segment

gs.add_child('ST', Usage.REQUIRED, by_segment_element('ST', 1, ['835'])).with_segments(
    Segment('ST', Usage.REQUIRED, by_segment('ST')),
    Segment('BPR', Usage.REQUIRED, by_segment('BPR')),
    Segment('TRN', Usage.REQUIRED, by_segment('TRN')),
    Segment('REF', Usage.REQUIRED, by_segment('REF')),
    Segment('DTM', Usage.REQUIRED, by_segment('DTM'))
)
```
- Uses the same Usage and predicates as **Loop** schema.
- The segment schemas are in sequential order of anticipated segments within the given loop.


### 2. Parse

```py
from x12.schema.schema import Schema, Usage
from x12.parser.parse import parse

# Real schema here
schema = Schema("X12")

loop = parse(filepath_to_x12_file, schema)
```

**Note**: if the x12 file does use the standard segment, element and composite separators, you can provide custom definition:

```py
from x12.parser.context import Context

loop = parse(filepath_to_x12_file, schema, Context("~", "*", ":"))
```

#### Loop Operations

**Serialization:**
Loop could be serialized to:
- XML: ```loop.to_xml()```
- original x12 format ```str(loop)```
- Debug view: ```loop.to_debug()```. This provides visual distinction for loops and segments.
    ![debug view](https://user-images.githubusercontent.com/1224609/223806918-b1e30dc6-bb5d-4492-a8f7-4cc7d33700ab.jpg)

**Find Child Loops:**
```py
# find loop by loop schema name

# Non recursive, search only within loop's direct children loops
loops = loop.find_loops("ST")

# Recursive, find loops anywhere in the downstream tree structure.
loops = loop.find_loops("NM1", True)
```

**Find Segments:**
```py
# find segment by segment ID

# Non recursive, search only within loop's segments
segments = loop.find_segments("ST")

# Recursive, find segments anywhere in the downstream tree structure.
segments = loop.find_segments("NM1", True)
```

**Other operations:**
- To access loop parent: ```loop.parent```
- Direct access to children loops: ```loop.loops```
- Direct access to segments: ```loop.segments```

#### Segment Operations

**Serialization:**
Segment could be serialized to:
- XML: ```segment.to_xml()```
- original x12 format ```str(segment)```
- Debug view: ```segment.to_debug()```. This provides visual distinction for segments.
    ![debug view](https://user-images.githubusercontent.com/1224609/223809367-518981df-164e-4a8d-b3bd-5a7185e26178.jpg)

**Access segment elements**
```segment.elements```

### 3. Optional: Analyze parsed loop.
This is an optional step to analyze the parsed document to see missing and unexpected loops/segments based on the schema.

```py
from x12.schema.schema import Schema, Usage
from x12.parser.parse import parse
from x12.parser.analyze import analyze

# Real schema here
schema = Schema("X12")

loop = parse(filepath_to_x12_file, schema)

print(analyze(loop))
```

**Example:**

![analyze](https://user-images.githubusercontent.com/1224609/223810446-b3371fe5-5d41-4d2e-ba24-2245edb8f1d2.jpg)
- Red indicates missing loops / segments.
- Yellow indicates unexpected segments.


---

## Contributing

See [contributing.md](https://github.com/spaceavocado/x12/blob/master/contributing.md).

## License

Space Avocado X12 Parser is released under the MIT license. See [LICENSE.md]([LICENSE.md](https://github.com/spaceavocado/x12/blob/master/LICENSE.md)).

