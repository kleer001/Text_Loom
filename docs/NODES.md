# Text Loom Node Reference

Quick reference guide for all Text Loom nodes. For comprehensive documentation with detailed examples, see [node_guide.md](node_guide.md).

---

## QueryNode (⌘) - FLOW

Interfaces with Large Language Models to process text prompts and generate responses.

**Parameters:**
- `limit` (bool, default: False) - Restrict processing to first prompt only
- `response` (List[str]) - History of LLM responses
- `llm_name` (str, default: "Ollama") - Target LLM identifier
- `find_llm` (button) - Auto-detect available LLMs
- `respond` (button) - Force regenerate responses

**Input:** List[str] of prompts
**Output:** List[str] of LLM-generated responses

**Example:**
```
Input: ["Summarize this text: Hello world"]
Output: ["A brief greeting consisting of two common English words."]
```

**Notes:**
- Automatically detects local LLM installations
- Maintains response history across evaluations
- Supports dynamic LLM switching

---

## NullNode (∅) - FLOW

Simple pass-through node that doesn't modify input. Useful for routing and organizing complex graphs.

**Parameters:**
- None

**Input:** List[str]
**Output:** List[str] (unchanged)

**Example:**
```
Input: ["apple", "banana"]
Output: ["apple", "banana"]
```

---

## InputNullNode (▷) - FLOW

Retrieves input from another specified node. Primarily used inside Looper nodes for accessing external data.

**Parameters:**
- `in_node` (str, default: "") - Path to source node
- `in_data` (List[str], default: []) - Data from source node
- `feedback_mode` (bool, default: False) - Use previous loop output as input

**Input:** None (reads from specified node)
**Output:** List[str] from source node

**Example:**
```
in_node: "/obj/file_reader"
Output: [data from file_reader node's input connection]
```

**Notes:**
- Used inside Looper nodes to access external inputs
- Feedback mode enables iterative processing with previous results
- Automatically detects and handles node path resolution

---

## OutputNullNode (◁) - FLOW

Mirrors input to output parameter while accumulating data. Primarily used inside Looper nodes for collecting results.

**Parameters:**
- `out_data` (List[str], default: []) - Accumulated output data
- `feedback_mode` (bool, default: False) - Enable feedback loop
- `cook_loops` (bool, default: False) - Force cook on each iteration
- `in_node` (str, default: "") - Parent node path

**Input:** List[str]
**Output:** List[str] (accumulated across iterations)

**Example:**
```
Loop iteration 1 input: ["result1"]
Loop iteration 2 input: ["result2"]
Final output: ["result1", "result2"]
```

**Notes:**
- Used inside Looper nodes to collect iteration results
- Accumulates data by extending the list on each cook
- Supports feedback mode for iterative refinement

---

## LooperNode (⟲) - FLOW

Iterative processing node for repeated operations over data ranges or input items.

**Parameters:**
- `min` (int, default: 0) - Starting iteration value
- `max` (int, default: 10) - Ending iteration value
- `step` (int, default: 1) - Increment between iterations
- `max_from_input` (bool, default: False) - Set max from input length
- `feedback_mode` (bool, default: False) - Feed each iteration output into next
- `use_test` (bool, default: False) - Run single test iteration
- `test_number` (int, default: 0) - Which iteration to test
- `timeout_limit` (float, default: 300.0) - Max execution time in seconds
- `data_limit` (int, default: 200MB) - Max memory usage

**Input:** List[str] (optional, used when max_from_input=True)
**Output:** List[str] of iteration results

**Example:**
```
Input: ["item1", "item2", "item3"]
max_from_input: True
Output: [processed_item1, processed_item2, processed_item3]
```

**Notes:**
- Manages internal input/output nodes for child graph
- Supports resource limits and timeout protection
- Test mode useful for debugging specific iterations

---

## FileOutNode (⤴) - FILE

Writes string lists to text files with hash-based change detection.

**Parameters:**
- `filename` (str, default: "./output.txt") - Target file path
- `content` (List[str]) - Data to write
- `refresh` (button) - Force write regardless of changes
- `format_output` (bool, default: True) - Format as lines vs Python list

**Input:** List[str] to write
**Output:** None (writes to file)

**Example:**
```
Input: ["line1", "line2", "line3"]
filename: "output.txt"
format_output: True
→ Creates file with:
line1
line2
line3
```

**Notes:**
- Hash checking prevents unnecessary disk writes
- format_output=False preserves Python list format for round-trip processing

---

## FolderOutNode (📂) - FILE

**⚠️ NOT YET IMPLEMENTED - SPECIFICATION ONLY**

Writes input list items as separate files into a specified folder. Each list item becomes an individual file.

**Parameters (Planned):**
- `folder_path` (str, default: "./output") - Target directory
- `filename_pattern` (str, default: "output_{count}.txt") - Template with {index}, {count}, {input}
- `file_extension` (str, default: ".txt") - File extension
- `overwrite` (bool, default: False) - Overwrite vs append suffix for collisions
- `refresh` (button) - Force write all files
- `format_output` (bool, default: True) - Raw string vs Python list format

**Input:** List[str] (each item becomes a file)
**Output:** List[str] (file paths created)

**Example (Planned):**
```
Input: ["First document", "Second document", "Third document"]
filename_pattern: "doc_{count}"
→ Creates:
  output/doc_1.txt (contains: "First document")
  output/doc_2.txt (contains: "Second document")
  output/doc_3.txt (contains: "Third document")
```

**Notes:**
- **Status:** Specification exists at src/core/folder_out_node.py but not implemented
- **Planned features:** Hash-based optimization, collision handling, sanitized filenames
- **Use FileOutNode** with a Looper node for similar functionality until implementation

---

## FileInNode (⤵) - FILE

Reads and parses text files or input strings into lists.

**Parameters:**
- `file_name` (str, default: "./input.txt") - Source file path
- `file_text` (str) - Current file content
- `refresh` (button) - Force reload file

**Input:** Optional List[str] (overrides file reading if provided)
**Output:** List[str] parsed from file or input

**Example:**
```
file_name: "data.txt"
→ Reads file and parses ["item1", "item2", "item3"]
```

**Notes:**
- MD5 hash-based change detection
- Can parse Python list syntax: ["item1", "item2"]
- Input connection overrides file reading

---

## TextNode (Ꭲ) - TEXT

Manipulates text strings with append/prepend operations and list syntax support.

**Parameters:**
- `text_string` (str, default: "") - Text or list to process
- `pass_through` (bool, default: False) - Process input data
- `per_item` (bool, default: False) - Apply to each item vs concatenate
- `prefix` (bool, default: False) - Add before vs after input

**Input:** List[str]
**Output:** List[str] with text manipulated

**Example:**
```
Input: ["world"]
text_string: "Hello"
prefix: True
Output: ["Hello world"]
```

**Notes:**
- Supports Python list syntax: ["first", "second"]
- Empty list [] creates [""]
- Invalid syntax falls back to plain string

---

## SplitNode (⋔) - LIST

Splits lists into two parts based on slice expressions or random selection.

**Parameters:**
- `enabled` (bool, default: True) - Enable/disable node
- `split_expr` (str, default: "[0]") - Slice or random expression

**Split Expression Types:**
- List slicing: `[0]`, `[1:3]`, `[::2]`, `[::-1]`
- Random: `random(seed[,count])` - seed can be "time" or number

**Input:** List[str]
**Output 0:** Selected items
**Output 1:** Remaining items
**Output 2:** Empty (reserved)

**Example:**
```
Input: ["a", "b", "c", "d"]
split_expr: "[1:3]"
Output 0: ["b", "c"]
Output 1: ["a", "d"]
```

---

## SectionNode (§) - TEXT

Sections input text based on prefix matching patterns with regex support.

**Parameters:**
- `prefix1` (str, default: "Interviewer") - First prefix pattern
- `prefix2` (str, default: "Participant") - Second prefix pattern
- `trim_prefix` (bool, default: True) - Remove matched prefix from output
- `regex_file` (str, default: "regex.dat.json") - Regex shortcuts file

**Pattern Types:**
- Wildcard: `Q*` matches "Q:", "Query", "Question"
- Regex: `^Chapter\\d+` matches "Chapter1", "Chapter22"
- Shortcut: `@phone`, `@email`, `@date` (from regex.dat.json)

**Input:** List[str]
**Output 0:** Lines matching first prefix
**Output 1:** Lines matching second prefix
**Output 2:** Unmatched lines

**Example:**
```
Input: ["Q: What time?", "A: 3 PM", "Note: check"]
prefix1: "Q*"
prefix2: "A*"
Output 0: ["What time?"]
Output 1: ["3 PM"]
Output 2: ["Note: check"]
```

**External Dependencies:**
- **File:** `src/core/regex.dat.json`
- **Contains:** 18 predefined patterns (@phone, @email, @date, @time, @ipv4, @currency, @hashtag, @handle, @speaker, @question, @answer, @timestamp, @scene, @character, @direction, @transition)
- **Location:** Same directory as section_node.py
- **Format:** JSON with pattern/description/examples

---

## MakeListNode (≣) - TEXT

Parses numbered lists from text into string lists.

**Parameters:**
- `limit` (bool, default: False) - Limit output items
- `max_list` (int, default: 10) - Max items when limit=True

**Supported Formats:**
- Arabic: `1.`, `2.`, `3.`
- Written: `one.`, `two.`, `three.`
- Ordinal: `first.`, `second.`, `third.`
- Separators: `. : - _`

**Input:** List[str] (parses first item)
**Output:** List[str] of parsed items

**Example:**
```
Input: ["1. First item\n2. Second item\n3. Third"]
Output: ["First item", "Second item", "Third"]
```

**External Dependencies:**
- **Function:** `parse_list()` from utilities module
- **Limitations:**
  - Only processes first item in input list
  - Cannot handle nested lists
  - No Roman numerals (i., ii., iii.)
  - No lettered lists (a., b., c.)
  - Max number support up to thousands

---

## MergeNode (⋈) - LIST

Combines multiple input lists into single output with optional formatting.

**Parameters:**
- `single_string` (bool, default: False) - Merge all into one item
- `insert_string` (str, default: "") - Prefix for each item (use 'N' for index)
- `use_insert` (bool, default: False) - Apply insert_string

**Input:** Multiple List[str] connections (unlimited)
**Output:** Single List[str] (merged)

**Example:**
```
Input 1: ["Hello", "World"]
Input 2: ["How", "Are"]
Output: ["Hello", "World", "How", "Are"]

With insert_string="N. " and use_insert=True:
Output: ["1. Hello", "2. World", "3. How", "4. Are"]
```

---

## FolderNode (📁) - FILE

Scans directories and reads file contents for batch processing.

**Parameters:**
- `folder_path` (str, default: "./input") - Directory to scan
- `pattern` (str, default: "*") - File pattern (wildcards or regex)
- `recursive` (bool, default: False) - Include subdirectories
- `sort_by` (str, default: "name") - name/date/size (add _desc for reverse)
- `max_files` (int, default: 0) - Limit files (0=unlimited)
- `min_size` (int, default: 0) - Min file size in bytes
- `max_size` (int, default: 0) - Max file size in bytes
- `include_hidden` (bool, default: False) - Include hidden files
- `on_error` (str, default: "warn") - stop/warn/ignore
- `follow_symlinks` (bool, default: False) - Follow symbolic links

**Input:** None
**Output 0:** List[str] of file contents
**Output 1:** List[str] of file paths
**Output 2:** List[str] of error messages

**Example:**
```
folder_path: "./logs"
pattern: "*.txt"
sort_by: "date_desc"
max_files: 10
Output 0: [contents of 10 most recent .txt files]
Output 1: ["/logs/file1.txt", "/logs/file2.txt", ...]
```

**Notes:**
- Supports $GLOBAL variable substitution in paths
- Pattern supports wildcards (`*.txt`) or regex (`^error_.*\\.log`)

---

## JSONNode (⌘) - TEXT

Parses JSON text and extracts data using JSONPath-style queries.

**Parameters:**
- `json_path` (str, default: "") - Dot notation or JSONPath
- `extraction_mode` (str, default: "array") - array/values/keys/flatten
- `format_output` (str, default: "raw") - raw/labeled/json
- `on_parse_error` (str, default: "warn") - warn/passthrough/empty
- `max_depth` (int, default: 0) - Max nesting (0=unlimited)
- `enabled` (bool, default: True) - Enable/disable

**Path Syntax:**
- Dot: `items`, `data.results`
- Index: `items[0]`, `users[-1]`
- Wildcard: `users[*].name`

**Input:** List[str] (first item parsed as JSON)
**Output:** List[str] of extracted values

**Example:**
```
Input: ['{"users": [{"name": "Alice"}, {"name": "Bob"}]}']
json_path: "users[*].name"
Output: ["Alice", "Bob"]
```

**Notes:**
- All values stringified (numbers become "42", booleans become "true"/"false")
- Wildcard expansion flattens to single list

---

## ChunkNode (⊟) - TEXT

Splits text into chunks by character count, sentence, or paragraph boundaries.

**Parameters:**
- `chunk_mode` (menu, default: "character") - character/sentence/paragraph
- `chunk_size` (int, default: 1000) - Target chunk size in characters
- `overlap_size` (int, default: 100) - Overlap between chunks
- `respect_boundaries` (bool, default: True) - Avoid mid-sentence splits
- `min_chunk_size` (int, default: 50) - Minimum chunk size
- `add_metadata` (bool, default: False) - Prepend "Chunk N/Total:"
- `enabled` (bool, default: True) - Enable/disable

**Input:** List[str] of text to chunk
**Output:** List[str] of chunks (all inputs flattened)

**Example:**
```
Input: ["Long text that needs splitting..."]
chunk_mode: "character"
chunk_size: 50
overlap_size: 10
Output: ["Long text that needs...", "...needs splitting..."]
```

**Notes:**
- Sentence detection: periods/exclamation/question marks + whitespace
- Paragraph detection: double newlines (`\n\n`)
- respect_boundaries may create chunks larger than chunk_size

---

## CountNode (#) - LIST

Performs counting, deduplication, and frequency analysis on text lists.

**Parameters:**
- `stat_mode` (menu, default: "count") - count/deduplicate/word_freq/char_freq
- `count_what` (menu, default: "items") - items/words/characters/lines
- `preserve_order` (bool, default: True) - For deduplication
- `top_n` (int, default: 0) - Limit frequency results (0=all)
- `case_sensitive` (bool, default: False) - Case handling
- `format_output` (menu, default: "plain") - plain/labeled/json
- `enabled` (bool, default: True) - Enable/disable

**Input:** List[str]
**Output:** List[str] with statistical results

**Example:**
```
Input: ["apple", "banana", "apple", "cherry"]
stat_mode: "deduplicate"
Output: ["apple", "banana", "cherry"]

stat_mode: "count"
count_what: "items"
Output: ["4"]
```

---

## SearchNode (🔍) - LIST

Searches and filters text based on patterns with boolean logic.

**Parameters:**
- `search_text` (str, default: "") - Search terms (comma/space separated)
- `search_mode` (menu, default: "contains") - contains/exact/starts_with/ends_with/regex
- `case_sensitive` (bool, default: False) - Case matching
- `boolean_mode` (menu, default: "OR") - OR/AND/NOT
- `invert_match` (bool, default: False) - Invert matching logic
- `enabled` (bool, default: True) - Enable/disable

**Input:** List[str]
**Output 0:** Matching items
**Output 1:** Non-matching items
**Output 2:** Empty (reserved)

**Example:**
```
Input: ["apple pie", "banana bread", "apple cake"]
search_text: "apple"
search_mode: "contains"
Output 0: ["apple pie", "apple cake"]
Output 1: ["banana bread"]
```

**Notes:**
- Multiple terms in search_text split by commas/spaces
- Regex mode supports full regular expressions
- Boolean NOT equivalent to inverting each term

---

## StringTransformNode (⎔) - TEXT

Performs string transformations including find/replace, case changes, and trimming.

**Parameters:**
- `operation` (menu, default: "find_replace") - find_replace/regex_replace/case_transform/trim/whitespace_normalize
- `find_text` (str, default: "") - Text/pattern to find
- `replace_text` (str, default: "") - Replacement text
- `use_regex` (bool, default: False) - Treat find_text as regex
- `case_sensitive` (bool, default: True) - Case matching for find/replace
- `case_mode` (menu, default: "upper") - upper/lower/title/capitalize
- `trim_mode` (menu, default: "both") - both/start/end
- `normalize_spaces` (bool, default: False) - Collapse multiple spaces
- `enabled` (bool, default: True) - Enable/disable

**Input:** List[str]
**Output:** List[str] (transformed, same length as input)

**Example:**
```
Input: ["Hello World", "HELLO WORLD"]
operation: "find_replace"
find_text: "hello"
replace_text: "Hi"
case_sensitive: False
Output: ["Hi World", "Hi WORLD"]
```

**Notes:**
- Regex capture groups supported: `\\1`, `\\2`, etc.
- normalize_spaces can combine with any operation
- Invalid regex generates warning, returns text unchanged

---

## Node Groups

**FLOW:** QueryNode, NullNode, InputNullNode, OutputNullNode, LooperNode
**FILE:** FileOutNode, FolderOutNode ⚠️, FileInNode, FolderNode
**TEXT:** TextNode, SectionNode, MakeListNode, ChunkNode, StringTransformNode
**LIST:** SplitNode, MergeNode, JSONNode, CountNode, SearchNode

**Total: 19 nodes** (18 implemented, 1 specification only)

---

## External Files & Dependencies

**Section Node:**
- File: `src/core/regex.dat.json`
- 18 predefined regex patterns for common data types
- Accessible via `@pattern_name` syntax

**MakeList Node:**
- Function: `parse_list()` utility
- Limitations: No nested lists, Roman numerals, or lettered lists
- Max number words up to thousands

**All File Nodes:**
- Default paths relative to execution directory
- Support absolute and relative paths
- UTF-8 text encoding assumed
