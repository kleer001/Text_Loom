# Node Grouping Suggestions for Color Coding

This document proposes three different grouping schemes (3, 4, and 5 groups) for color-coding the 15 node types in Text Loom.

---

## 3-Group Scheme: "Data Flow"

**Justification:** Groups nodes by their primary role in data flow - where data enters/exits, how it transforms, and how flow is controlled.

### Group 1: INPUT/OUTPUT (I/O Operations)
**Nodes:** FileInNode, FileOutNode, FolderNode, QueryNode

**Rationale:** These nodes interact with external systems (filesystem, LLMs). They're the boundaries where data enters or leaves the graph.

### Group 2: TRANSFORM (Data Transformation)
**Nodes:** TextNode, ChunkNode, SectionNode, MakeListNode, JSONNode, SplitNode, MergeNode, CountNode, SearchNode

**Rationale:** These nodes process, reshape, analyze, or filter data. They're the workhorses that manipulate data between input and output.

**Overlapping Membership:**
- **QueryNode** (50% I/O, 50% Transform) - Both external service AND text processor

### Group 3: CONTROL (Flow Control)
**Nodes:** LooperNode, NullNode

**Rationale:** These nodes manage graph execution flow rather than transforming data content. LooperNode controls iteration; NullNode routes connections.

---

## 4-Group Scheme: "Functional Categories"

**Justification:** Groups nodes by their primary function, providing better granularity for understanding what each node does.

### Group 1: FILE OPERATIONS (Blue/Cyan Theme)
**Nodes:** FileInNode, FileOutNode, FolderNode

**Rationale:** All nodes that directly interact with the filesystem for reading or writing files.

### Group 2: TEXT PROCESSING (Green Theme)
**Nodes:** TextNode, ChunkNode, SectionNode, MakeListNode

**Rationale:** Nodes that manipulate or restructure text content - splitting, parsing, chunking, or modifying strings.

**Overlapping Membership:**
- **JSONNode** (70% Text Processing, 30% Data Format) - Parses text but specifically for structured data

### Group 3: LIST & DATA OPERATIONS (Yellow/Orange Theme)
**Nodes:** SplitNode, MergeNode, JSONNode, SearchNode, CountNode

**Rationale:** Nodes that operate on list structures - combining, splitting, filtering, or analyzing collections.

**Overlapping Membership:**
- **SectionNode** (50% Text Processing, 50% List Operations) - Processes text prefixes but outputs split lists
- **SearchNode** (60% List Operations, 40% Analysis) - Filters lists but also performs analysis

### Group 4: CONTROL & EXTERNAL (Purple/Magenta Theme)
**Nodes:** LooperNode, NullNode, QueryNode

**Rationale:** Special-purpose nodes for flow control and external service integration.

**Overlapping Membership:**
- **QueryNode** (70% Control/External, 30% Text Processing) - External LLM service but generates text

---

## 5-Group Scheme: "Detailed Taxonomy"

**Justification:** Maximum granularity for color coding, separating nodes by specific functional roles. Best for complex graphs with many node types.

### Group 1: INPUT SOURCES (Blue Theme)
**Nodes:** FileInNode, FolderNode

**Rationale:** Nodes that primarily read or ingest data from external sources into the graph.

**Overlapping Membership:**
- **TextNode** (20% Input Source) - Can generate text without input when pass_through=False

### Group 2: OUTPUT SINKS (Red Theme)
**Nodes:** FileOutNode, QueryNode

**Rationale:** Nodes that send data outside the graph - to files or external services.

**Overlapping Membership:**
- **QueryNode** (50% Output Sink, 50% Text Generator) - Sends to LLM but also receives responses

### Group 3: TEXT TRANSFORMERS (Green Theme)
**Nodes:** TextNode, ChunkNode, SectionNode, MakeListNode, JSONNode

**Rationale:** Nodes that parse, split, or restructure text content while preserving semantic meaning.

**Overlapping Membership:**
- **CountNode** (30% Text Transformer) - When using word_freq or char_freq modes, analyzes text structure

### Group 4: LIST OPERATORS (Yellow Theme)
**Nodes:** SplitNode, MergeNode, SearchNode, CountNode

**Rationale:** Nodes that manipulate list structures - combining, splitting, filtering, or deduplicating collections.

**Overlapping Membership:**
- **SectionNode** (40% List Operator) - Outputs multiple filtered lists based on prefixes
- **MakeListNode** (40% List Operator) - Creates lists from text
- **JSONNode** (30% List Operator) - Extracts arrays and creates lists

### Group 5: CONTROL & UTILITY (Purple Theme)
**Nodes:** LooperNode, NullNode

**Rationale:** Infrastructure nodes that control execution flow and graph connectivity without transforming data content.

---

## Overlapping Membership Summary

Some nodes naturally span multiple categories. Here's a complete matrix:

| Node | Primary Group | Secondary Group(s) | Split % |
|------|---------------|-------------------|---------|
| QueryNode | I/O (3-group), Control/External (4-group), Output Sink (5-group) | Transform (50% in 3-group), Text Processing (30% in 4-group), Text Transformer (50% in 5-group) | Variable |
| JSONNode | Transform (3-group), List Operations (4-group), Text Transformer (5-group) | Text Processing (70% in 4-group), List Operator (30% in 5-group) | 70/30 |
| SectionNode | Transform (3-group), Text Processing (4-group), Text Transformer (5-group) | List Operations (50% in 4-group), List Operator (40% in 5-group) | 60/40 |
| SearchNode | Transform (3-group), List Operations (4-group), List Operator (5-group) | Analysis (40% in 4-group) | 60/40 |
| TextNode | Transform (3-group), Text Processing (4-group), Text Transformer (5-group) | Input Source (20% in 5-group) | 80/20 |
| CountNode | Transform (3-group), List Operations (4-group), List Operator (5-group) | Text Transformer (30% in 5-group) | 70/30 |
| MakeListNode | Transform (3-group), Text Processing (4-group), Text Transformer (5-group) | List Operator (40% in 5-group) | 60/40 |

---

## Recommended Color Palettes

### For 3-Group Scheme:
- **Group 1 (I/O):** Blue (#3498db)
- **Group 2 (Transform):** Green (#2ecc71)
- **Group 3 (Control):** Purple (#9b59b6)
- **Overlapping:** Gradient or split colors

### For 4-Group Scheme:
- **Group 1 (File Operations):** Cyan (#17a2b8)
- **Group 2 (Text Processing):** Green (#28a745)
- **Group 3 (List & Data Operations):** Orange (#fd7e14)
- **Group 4 (Control & External):** Purple (#6f42c1)
- **Overlapping:** Use color mixing or border highlights

### For 5-Group Scheme:
- **Group 1 (Input Sources):** Blue (#007bff)
- **Group 2 (Output Sinks):** Red (#dc3545)
- **Group 3 (Text Transformers):** Green (#28a745)
- **Group 4 (List Operators):** Yellow (#ffc107)
- **Group 5 (Control & Utility):** Purple (#6610f2)
- **Overlapping:** Use dual-color borders or subtle gradients

---

## Implementation Suggestions

### Option A: Hard Assignment
Assign each node to its primary group only. Simplest to implement, clearest visual distinction.

### Option B: Primary + Badge
Use primary group color with a small badge/icon for secondary membership. Good balance of clarity and information.

### Option C: Gradient/Split
For overlapping nodes, use a gradient or split-color design showing percentage membership. Most informative but potentially cluttered.

### Option D: Border Highlight
Primary group determines fill color, secondary group determines border color. Clean and effective for dual membership.

---

## Recommendation

**For general use:** 4-Group Scheme with Primary + Badge approach
- Provides good functional distinction
- Not too many colors to track
- Clear visual categories
- Badge system elegantly handles overlap

**For complex workflows:** 5-Group Scheme with Border Highlight
- Maximum granularity for large graphs
- Clear input/output visual distinction
- Border colors show data flow patterns

**For simplicity:** 3-Group Scheme with Hard Assignment
- Minimal color palette
- Clear high-level categories
- Easiest to learn for new users
