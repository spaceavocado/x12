# Space Avocado X12 Parser
A simple X12 file parser, allowing to parse X12 loops and segment based on schema.

> X12 is a message formatting standard used with Electronic Data Interchange (EDI) documents for trading partners to share electronic business documents in an agreed-upon and standard format. It is the most common EDI standard used in the United States.

See more details at https://x12.org/.

### X12 Document List
https://en.wikipedia.org/wiki/X12_Document_List

*Credit: Inspired by [Maven Central X12 Parser](https://github.com/ryanco/x12-parser).*

### X12 Schematic
![X12-Schematic](https://user-images.githubusercontent.com/1224609/223794653-9b3abcfe-cb6b-4bd5-aec6-14f07e9280e4.gif)

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

gs.add_child('ST', Usage.REQUIRED, by_segment_element('ST', 1, ['835'])).with_segments([
    Segment('ST', Usage.REQUIRED, by_segment('ST')),
    Segment('BPR', Usage.REQUIRED, by_segment('BPR')),
    Segment('TRN', Usage.REQUIRED, by_segment('TRN')),
    Segment('REF', Usage.REQUIRED, by_segment('REF')),
    Segment('DTM', Usage.REQUIRED, by_segment('DTM'))
])
```
- Uses the same Usage and predicates as **Loop** schema.
- The segment schemas are in sequential order of anticipated segments within the given loop.


### 2. Parse
### 3. Optional: Analyze parsed loop.