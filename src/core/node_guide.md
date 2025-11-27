# Node Guide

This document provides comprehensive documentation for all node types in Text Loom.

---

## 1. QueryNode

**QueryNode: A node that interfaces with Large Language Models (LLMs) to process text prompts and generate responses.**

This node serves as a bridge between the node graph system and local LLM installations, enabling prompt-based text generation and processing. It can handle single or multiple prompts, with options to limit processing for development or resource management.

### Key Features

1. **LLM Integration:**
   - Automatically detects and connects to local LLM installations
   - Supports dynamic LLM selection and switching
   - Provides fallback mechanisms when preferred LLM is unavailable

2. **Prompt Processing:**
   - Handles both single and batch prompt processing
   - Maintains response history
   - Supports forced response regeneration
   - Provides clean, formatted LLM responses

### Parameters

**limit** (bool): When True, restricts processing to only the first prompt. Useful for testing or managing resource usage.

**response** (List[str]): Stores the history of LLM responses. Updated after each successful processing.

**llm_name** (str): Identifier for the target LLM (e.g., "Ollama"). Defaults to "Ollama" but can be auto-detected.

**find_llm** (button): Triggers automatic LLM detection. Updates llm_name with found installation.

**respond** (button): Forces reprocessing of current prompts. Updates responses regardless of cache.

### Input/Output

**Input:** List[str] of prompts to process
**Output:** List[str] of LLM-generated responses

---

## 2. NullNode

**NullNode: A simple pass-through node that doesn't modify its input.**

This node acts as a connector or placeholder in node graphs, allowing you to route data without transformation. It's useful for organizing complex graphs or as a temporary connection point.

### Features

- Single input connection
- Multiple output connections supported
- Zero processing overhead
- Maintains data integrity

### Input/Output

**Input:** List[str]
**Output:** List[str] (unchanged from input)

---

## 3. LooperNode

**LooperNode: A powerful node for iterative processing of data with configurable loop behavior.**

This node enables iterative operations by managing internal input and output connections, making it ideal for tasks that require repeated processing or accumulation of results. Think of it as a sophisticated 'for' loop that can process data iteratively while maintaining node graph connectivity.

### Parameters

**min** (int): Starting value for the loop iteration (must be non-negative).

**max** (int): Ending value for the loop iteration (must be non-negative).

**step** (int): Increment value between iterations (cannot be zero).

**max_from_input** (bool): When enabled, sets max iterations based on input data length.

**feedback_mode** (bool): Enables feedback loop mode where each iteration's output feeds into the next.

**use_test** (bool): When enabled, runs only a single test iteration.

**cook_loops** (bool): Controls whether to force cook operations on each loop iteration.

**test_number** (int): Specific iteration to run when use_test is enabled (must be between min and max).

**input_hook** (str): Custom input processing hook (advanced usage).

**output_hook** (str): Custom output processing hook (advanced usage).

**timeout_limit** (float): Maximum execution time in seconds (default: 300.0).

**data_limit** (int): Maximum memory usage in bytes (default: 200MB).

### Features

- Configurable iteration range and step size
- Feedback mode for accumulative processing
- Test mode for debugging specific iterations
- Resource limits (timeout and memory)
- Custom hooks for advanced control

---

## 4. FileOutNode

**FileOutNode: A node that writes string lists to text files with hash-based change detection.**

This node writes content to a text file with intelligent change detection. The hash check helps determine whether the file needs to be written again, avoiding unnecessary disk operations.

### Parameters

**filename** (str): The name of the file to write to.

**content** (List[str]): A list of strings to be written to the file.

**refresh** (button): Force the file to be written regardless of content changes or hash matching.

**format_output** (bool): When True (default), formats output by stripping brackets and joining with newlines. When False, preserves Python list format (e.g. ["item1", "item2"]) for round-trip processing.

### Features

- Hash-based change detection to avoid redundant writes
- Optional formatting for human-readable output
- Force refresh capability
- Supports round-trip processing with FileInNode

### Input/Output

**Input:** List[str] of content to write
**Output:** None (writes to file)

---

## 5. FileInNode

**FileInNode: A node that reads and parses text files or input strings into lists.**

This node can either read from a file or take input text, parsing formatted string lists like "[item1, item2, item3]" into proper Python lists. If no input is provided, reads from the specified file.

### Parameters

**file_name** (str): Path to the target file (defaults to "./input.txt").

**file_text** (str): Contains the current file content.

**refresh** (button): Force reloads the file content.

### Input Processing

- If input is provided, uses that instead of file content
- Parses text in format "[item1, item2, ...]" into list items
- Handles quoted strings, escapes, and empty items
- Falls back to single-item list for invalid formats

### Features

- Monitors file changes using MD5 hashing
- Automatically reloads when file content changes
- Provides error reporting for file access issues
- Supports force refresh via button
- Can parse list-formatted strings from input

### Input/Output

**Input:** Optional List[str] (overrides file reading if provided)
**Output:** List[str] parsed from file or input

---

## 6. TextNode

**TextNode: A node that manipulates text strings with advanced list support.**

Takes a list of strings as input and either appends or prepends text based on the node's parameters. The text_string parameter supports both plain strings and Python-style list syntax.

### Parameters

**text_string** (str): The text to process. Accepts plain string or list syntax:
- Plain string: "hello" → creates ["hello"]
- List syntax: ["first", "second"] → creates ["first", "second"]

**pass_through** (bool): When True, processes input data. When False, uses only text_string.

**per_item** (bool): When True, applies each text string to every input item. When False, concatenates lists of strings.

**prefix** (bool): When True, adds text before input. When False, adds after.

### List Syntax Details

- Uses Python-style list notation with square brackets
- Strings must be quoted with either single (') or double (") quotes
- Mixed quote types are supported: ["first", 'second']
- Supports escaped quotes: ["escaped\\"quote"]
- Empty strings are preserved: ["", "test", ""]
- Empty list [] creates [""]
- Invalid syntax falls back to treating input as plain string

### Input/Output

**Input:** List[str]
**Output:** List[str] with text appended or prepended

---

## 7. SplitNode

**SplitNode: A versatile node for splitting lists of strings into two parts based on various expressions.**

This node takes a list of strings as input and splits it into two outputs: selected items and remaining items. The split behavior is controlled by the 'split_expr' parameter which supports two types of expressions.

### Expression Types

**1. List Selection Expression:** [index] or [start:end:step]

Uses Python-style list slicing syntax:
- `[0]` → Selects the first item
- `[-1]` → Selects the last item
- `[1:3]` → Selects items at indices 1 and 2
- `[::2]` → Selects every other item
- `[::-1]` → Selects all items in reverse order
- `[1:]` → Selects all items from index 1 onwards
- `[:-1]` → Selects all items except the last one

**2. Random Selection Expression:** random(seed[,count])

Randomly selects items from the input list:
- seed can be either 'time' for time-based randomization or a number for deterministic randomization
- Optional count parameter specifies how many items to select

Examples:
- `random(time)` → Randomly selects 1 item using current time as seed
- `random(42)` → Randomly selects 1 item using seed 42
- `random(time,3)` → Randomly selects 3 items using current time as seed
- `random(42,5)` → Randomly selects 5 items using seed 42

### Parameters

**enabled** (bool): Enables/disables the node's functionality.

**split_expr** (str): Expression defining how to split the input list.

### Input/Output

**Input:** List[str]
**Outputs:**
- Output 0 (Selected Items): Items that match the split expression criteria
- Output 1 (Remaining Items): Items that weren't selected
- Output 2 (Empty): Always empty list (reserved for future use)

---

## 8. SectionNode

**SectionNode: A node that sections input text based on prefix matching patterns.**

Separates input text into three outputs based on two prefix patterns. Lines matching either prefix are routed to corresponding outputs, with unmatched lines sent to the third output.

### Prefix Pattern Types

**1. Wildcard Patterns:**
- `*` matches any sequence of characters
- `?` matches exactly one character

Examples:
- "Q*" matches "Q:", "Query", "Question"
- "Speaker?" matches "Speaker1", "Speaker2"
- "*Bot" matches "ChatBot", "TestBot"

**2. Regex Patterns** (starting with ^):

Supports full regex matching.
Example: "^Chapter\\d+" matches "Chapter1", "Chapter22"

**3. Shortcut Patterns** (starting with @):

Predefined regex patterns from a configuration file.
Example: "@scene" might match scene headings

### Parameters

**prefix1** (str): First prefix to match.

**prefix2** (str): Second prefix to match.

**delimiter** (str): Separates prefix from content (default: ":").

**trim_prefix** (bool): Removes prefix when True.

**enabled** (bool): Enables/disables node functionality.

### Input/Output

**Input:** List[str] of strings to process
**Outputs:**
- Output 0: Lines matching first prefix
- Output 1: Lines matching second prefix
- Output 2: Unmatched lines

### Usage Examples

**Simple Example:**
```
Input: ["Q: What time?", "A: 3 PM", "Note: check later"]
prefix1 = "Q*"
prefix2 = "A*"

Output[0]: ["What time?"]
Output[1]: ["3 PM"]
Output[2]: ["Note: check later"]
```

**Complex Example:**
```
Input: [
    "INT. COFFEE SHOP - DAY",
    "DETECTIVE SMITH: Hello",
    "Q: First question",
    "(looking around)",
    "A: Detailed answer"
]
prefix1 = "@scene"
prefix2 = "Q*"

Output[0]: ["COFFEE SHOP - DAY"]
Output[1]: ["First question"]
Output[2]: ["DETECTIVE SMITH: Hello", "(looking around)", "A: Detailed answer"]
```

### Notes

- Whitespace around prefixes and delimiters is normalized
- Empty outputs contain [""] rather than []
- Wildcard patterns are converted to regex internally
- Delimiter within prefix is treated as part of the prefix

---

## 9. MakeListNode

**MakeListNode: A node that parses numbered lists from text into a list of strings.**

This node takes a string list as input, parses the first item using the parse_list function, and outputs a new string list. It can optionally limit the number of output items based on the 'limit' and 'max_list' parameters.

### Capabilities

**Supports multiple numbering formats:**
- Arabic numerals (1., 2., 3.)
- Written numbers (one., two., three.)
- Ordinal numbers (first., second., third.)
- Compound numbers (twenty-one, ninety-nine)

**Additional features:**
- Handles various separators between numbers and text (. : - _)
- Preserves multi-line list items
- Maintains original text formatting within list items
- Case-insensitive number word recognition

### Limitations

- Only processes the first numbered list encountered in the text
- Cannot handle nested lists
- Maximum number support up to thousands
- Does not preserve the original numbering format
- Cannot process Roman numerals (i., ii., iii.)
- Does not handle lettered lists (a., b., c.)

### Parameters

**limit** (bool): When True, limits the number of output items.

**max_list** (int): Maximum number of items to output when limit is enabled.

### Usage Examples

**Example 1: Arabic numerals with multi-line items**
```
Input: '''
Meeting Agenda:
1. Review previous minutes
   Additional notes about minutes
2. Discuss new projects
3. Plan next meeting'''

Output: [
    'Review previous minutes Additional notes about minutes',
    'Discuss new projects',
    'Plan next meeting'
]
```

**Example 2: Written number words**
```
Input: '''
Project Steps:
First: Initialize repository
Second: Set up environment
Third: Begin development'''

Output: [
    'Initialize repository',
    'Set up environment',
    'Begin development'
]
```

### Notes

- List items are assumed to start with a number or number word followed by a separator
- Subsequent lines without numbers are considered continuation of the previous item
- The function preserves internal spacing but trims leading/trailing whitespace
- Non-string inputs return an empty string rather than raising an error

### Input/Output

**Input:** List[str] (first item parsed as numbered list)
**Output:** List[str] of parsed list items

---

## 10. MergeNode

**MergeNode: A node that combines multiple input string lists into a single output list.**

Can combine inputs with optional formatting and indexing features. Accepts unlimited input connections and produces a single output list.

### Parameters

**single_string** (bool): When True, merges all input strings into a single-item list.

**insert_string** (str): String to insert before each list item. Use 'N' as a placeholder for the item's index number (starting at 1). Automatically wrapped with newline characters.

**use_insert** (bool): When True, adds the `insert_string` before each item during merge.

### Features

- Accepts unlimited input connections
- Produces single output list
- Optional index-based item labeling
- Flexible input reordering
- Maintains input string formatting

### Usage Examples

**Basic Merge:**
```
Input 1: ["Hello", "World"]
Input 2: ["How", "Are", "You"]
Input 3: ["Today?"]

Output: ["Hello", "World", "How", "Are", "You", "Today?"]
```

**With Indexed Insertion:**
```
Inputs: Same as above
insert_string: "Section N:"
use_insert: True

Output: [
    "Section 1: Hello",
    "Section 2: World",
    "Section 3: How",
    "Section 4: Are",
    "Section 5: You",
    "Section 6: Today?"
]
```

**Single String Mode:**
```
Inputs: Same as above
single_string: True

Output: ["Hello World How Are You Today?"]
```

### Input/Output

**Input:** Multiple List[str] connections (unlimited)
**Output:** Single List[str] (merged result)

---

## 11. FolderNode

**FolderNode: A directory scanning node for batch file processing workflows.**

This node enables batch processing of text files by scanning directories, filtering files based on various criteria, and reading their contents. The primary use case is processing entire directories of text files through LLM pipelines without manually specifying each file.

### Core Functionality

- Scans directories for matching text files
- Filters files by pattern, size, and visibility
- Reads file contents and returns them as a list
- Supports both recursive and non-recursive directory traversal
- Provides flexible sorting and limiting options

### Parameters

**folder_path** (str): Path to the directory to scan. Supports $GLOBAL variable substitution for dynamic paths. Default: "./input"

**pattern** (str): Filename matching pattern supporting both wildcards and regex:
- Wildcards: Use `*.txt` for all text files, `test*.log` for logs starting with "test"
- Regex: Use `^alpha.*\\.txt` for regex pattern matching
- Default: `*` (matches all files)

**recursive** (bool): When True, includes files from subdirectories in the scan. When False, only scans the immediate directory. Default: False

**sort_by** (str): Determines the file ordering method:
- "name": Sort alphabetically by filename (ascending)
- "name_desc": Sort alphabetically by filename (descending)
- "date": Sort by modification time (oldest first)
- "date_desc": Sort by modification time (newest first)
- "size": Sort by file size (smallest first)
- "size_desc": Sort by file size (largest first)
- "none": No sorting, files in directory order
- Default: "name"

**max_files** (int): Maximum number of files to process. Set to 0 for unlimited files. Useful for testing large directories or limiting processing time. Default: 0 (unlimited)

**min_size** (int): Minimum file size in bytes. Files smaller than this are excluded. Set to 0 for no minimum. Default: 0

**max_size** (int): Maximum file size in bytes. Files larger than this are excluded. Set to 0 for no maximum. Default: 0

**include_hidden** (bool): When True, includes hidden files (those starting with a dot). When False, skips hidden files. Default: False

**on_error** (str): Error handling behavior:
- "stop": Stop processing and raise error on first file read failure
- "warn": Continue processing but log warnings for failed files
- "ignore": Silently skip files that cannot be read
- Default: "warn"

**follow_symlinks** (bool): When True, follows symbolic links to files and directories. When False, ignores symlinks. Default: False

### Input/Output

**Input:** None (uses folder_path parameter)
**Outputs:**
- Output 0 (File Contents): List of strings containing the contents of each matched file
- Output 1 (File Names): List of strings containing the full paths of each successfully read file
- Output 2 (Errors): List of strings containing error messages for each file (empty strings indicate success)

### Usage Examples

**Example 1: Simple directory scan**
```
folder_path = "./documents"
pattern = "*.txt"
recursive = False

Output 0: ["Content of doc1.txt", "Content of doc2.txt", ...]
Output 1: ["./documents/doc1.txt", "./documents/doc2.txt", ...]
Output 2: ["", "", ...]
```

**Example 2: Recursive scan with size filtering**
```
folder_path = "./data"
pattern = "*.log"
recursive = True
min_size = 1000
max_size = 100000
sort_by = "date_desc"

Output 0: [Most recent log contents within size range]
Output 1: [Corresponding log file paths]
Output 2: [Error messages or empty strings]
```

**Example 3: Limited file processing**
```
folder_path = "./training_data"
pattern = "*.csv"
max_files = 10
sort_by = "size_desc"

Output 0: [Contents of 10 largest CSV files]
Output 1: [Paths to those 10 files]
Output 2: [Error status for each file]
```

**Example 4: Regex pattern matching**
```
folder_path = "./logs"
pattern = "^error_.*\\.log"
recursive = True
include_hidden = False

Output 0: [Contents of files matching regex "^error_.*\\.log"]
Output 1: [Paths to matched files]
Output 2: [Error messages]
```

### Features

- Pattern Matching: Supports both glob-style wildcards (`*.txt`) and full regex patterns
- Size Filtering: Filters files by minimum and maximum size constraints
- Sorting Options: Six different sorting methods plus unsorted option
- Error Handling: Configurable error behavior for strict or best-effort processing
- Hidden Files: Optional inclusion of hidden files
- Symlink Support: Configurable symbolic link following
- File Limiting: Process a specific number of files for testing
- Path Variables: Supports $GLOBAL variable substitution in folder paths

### Notes

- All file contents are read as UTF-8 text strings
- The node validates directory existence before scanning
- Empty outputs contain [""] rather than [] for consistent list structure
- Permission errors are handled according to the on_error parameter
- File paths in Output 1 are always absolute paths
- The node is not time-dependent and caches results until input or parameters change

---

## 12. JSONNode

**JSONNode: A node that parses JSON text and extracts data as text lists.**

Takes JSON text as input and extracts values based on JSONPath-style queries. All output is returned as List[str] with everything stringified for text processing. This node acts as a bridge between JSON data and text-based node processing.

### Path Syntax

The `json_path` parameter supports a lightweight JSONPath syntax:

**Dot Notation:**
- `items` - Access top-level key
- `data.results` - Access nested keys
- `user.profile.name` - Multiple levels deep

**Array Indexing:**
- `items[0]` - First item
- `users[-1]` - Last item
- `data.results[2]` - Specific index

**Wildcards:**
- `users[*].name` - Extract name from all users
- `items[*]` - Get all array items
- `users[*].tags[*]` - Nested wildcard (flattens all results)

**Empty Path:**
- `""` (empty string) - Process entire JSON based on extraction_mode

### Parameters

**json_path** (str, default: ""): JSONPath or dot notation to extract data. Empty string returns entire JSON structure. Supports nested paths and wildcards.

**extraction_mode** (str, default: "array"):
- "array" - Extract array items as list
- "values" - Extract object values as list (ignores keys)
- "keys" - Extract object keys as list (ignores values)
- "flatten" - Flatten nested structure with full paths

**format_output** (str, default: "raw"):
- "raw" - Plain string values: ["Alice", "Bob"]
- "labeled" - Key-value pairs: ["name: Alice", "age: 30"]
- "json" - Each item as JSON string: ['{"name":"Alice"}', '{"name":"Bob"}']

**on_parse_error** (str, default: "warn"):
- "warn" - Log warning, output [""]
- "passthrough" - Return original text unchanged
- "empty" - Return [""]

**max_depth** (int, default: 0): Maximum nesting level to traverse (0 = unlimited). Prevents infinite recursion on circular references. Only applies to flatten mode.

**enabled** (bool, default: True): When False, passes through input unchanged. Useful for temporarily disabling JSON parsing.

### Input/Output

**Input:** List[str] (expects first item to be JSON string)
**Output:** List[str] (extracted values as strings)

### Usage Examples

**Simple Array Extraction:**
```
Input: '{"items": ["apple", "banana", "cherry"]}'
json_path: "items"

Output: ["apple", "banana", "cherry"]
```

**Wildcard Path:**
```
Input: '{"users": [{"name": "Alice"}, {"name": "Bob"}]}'
json_path: "users[*].name"

Output: ["Alice", "Bob"]
```

**Extract Object Values:**
```
Input: '{"count": 42, "status": "ok", "active": true}'
json_path: ""
extraction_mode: "values"

Output: ["42", "ok", "true"]
```

**Extract Object Keys:**
```
Input: '{"count": 42, "status": "ok"}'
extraction_mode: "keys"

Output: ["count", "status"]
```

**Flatten Nested Structure:**
```
Input: '{"user": {"name": "Alice", "profile": {"age": 30}}}'
json_path: ""
extraction_mode: "flatten"

Output: ["user.name: Alice", "user.profile.age: 30"]
```

**Nested Wildcards:**
```
Input: '{"users": [
    {"name": "Alice", "tags": ["admin", "user"]},
    {"name": "Bob", "tags": ["user", "guest"]}
]}'
json_path: "users[*].tags[*]"

Output: ["admin", "user", "user", "guest"]
```

**JSON Format Output:**
```
Input: '{"items": [{"id": 1, "name": "Item1"}, {"id": 2, "name": "Item2"}]}'
json_path: "items"
format_output: "json"

Output: ['{"id": 1, "name": "Item1"}', '{"id": 2, "name": "Item2"}']
```

### Notes

- All values are converted to strings (numbers become "42", booleans become "true"/"false")
- Empty or null values become empty strings ""
- Single values are always wrapped in a list: ["value"]
- Invalid JSON triggers the error handling behavior (warn/passthrough/empty)
- Wildcard expansion collects all matching values into a flat list
- The node stays text-only - no data type conversion or schema validation
- For complex JSON manipulation, chain multiple JsonNodes together

---

## 13. ChunkNode

**ChunkNode: A node that splits text into chunks using various strategies.**

Supports chunking by character count, sentence boundaries, or paragraph boundaries. Can respect sentence/paragraph boundaries to avoid mid-sentence splits and supports overlapping chunks for context preservation. This is particularly useful for preparing text for LLM processing with token limits or creating manageable text segments.

### Key Features

- Multiple chunking strategies (character, sentence, paragraph)
- Configurable chunk size and overlap
- Boundary-respecting mode to preserve semantic units
- Minimum chunk size enforcement
- Optional metadata labeling for chunks

### Parameters

**chunk_mode** (menu): Determines the chunking strategy:
- "character" - Splits by character count
- "sentence" - Splits by sentence boundaries (uses punctuation detection)
- "paragraph" - Splits by paragraph boundaries (double newlines)

**chunk_size** (int, default: 1000): Target size for each chunk in characters. The actual size may vary based on boundary respect settings.

**overlap_size** (int, default: 100): Number of characters to overlap between consecutive chunks. Useful for maintaining context across chunk boundaries.

**respect_boundaries** (bool, default: True): When True and chunk_mode is "character", avoids splitting mid-sentence. When False, splits strictly at character count.

**min_chunk_size** (int, default: 50): Minimum size for a chunk in characters. Chunks smaller than this are merged with the previous chunk.

**add_metadata** (bool, default: False): When True, prepends each chunk with metadata in format "Chunk N/Total: {content}".

**enabled** (bool, default: True): Enables/disables the node's functionality.

### Input/Output

**Input:** List[str] of text items to chunk
**Output:** List[str] of text chunks (all input items are chunked and concatenated into a flat list)

### Usage Examples

**Example 1: Character-based chunking with overlap**
```
Input: ["This is a long document that needs to be split into smaller pieces for processing by an LLM with limited context."]
chunk_mode: "character"
chunk_size: 50
overlap_size: 10
respect_boundaries: True

Output: [
    "This is a long document that needs to be split",
    "split into smaller pieces for processing by an",
    "by an LLM with limited context."
]
```

**Example 2: Sentence-based chunking**
```
Input: ["First sentence. Second sentence. Third sentence. Fourth sentence."]
chunk_mode: "sentence"
chunk_size: 50
overlap_size: 0

Output: [
    "First sentence. Second sentence.",
    "Third sentence. Fourth sentence."
]
```

**Example 3: With metadata labeling**
```
Input: ["Short text to chunk."]
chunk_mode: "character"
chunk_size: 10
add_metadata: True

Output: [
    "Chunk 1/2: Short text",
    "Chunk 2/2:  to chunk."
]
```

**Example 4: Paragraph-based chunking**
```
Input: ["First paragraph here.\n\nSecond paragraph here.\n\nThird paragraph here."]
chunk_mode: "paragraph"
chunk_size: 100

Output: [
    "First paragraph here.",
    "Second paragraph here.",
    "Third paragraph here."
]
```

### Notes

- Sentence detection uses regex matching for periods, exclamation marks, and question marks followed by whitespace
- Paragraph detection requires double newlines (`\n\n`)
- When respect_boundaries is True, chunks may be larger than chunk_size to preserve complete sentences
- Overlap is measured in characters, not semantic units
- Minimum chunk size prevents orphaned fragments
- Multiple input items are processed sequentially and all chunks are concatenated into a single output list

---

## 14. CountNode

**CountNode: A node that performs counting and statistical operations on text lists.**

Provides counting operations (items, words, characters, lines), deduplication with order preservation, and frequency analysis for words and characters. Results can be formatted as plain text, labeled output, or JSON for downstream processing.

### Key Features

- Multiple counting modes (items, words, characters, lines)
- Deduplication with configurable order preservation
- Word and character frequency analysis
- Configurable output formatting (plain, labeled, JSON)
- Case-sensitive and case-insensitive modes

### Parameters

**stat_mode** (menu): Determines the statistical operation to perform:
- "count" - Counts items, words, characters, or lines based on count_what parameter
- "deduplicate" - Removes duplicate items from the list
- "word_freq" - Analyzes word frequency across all input items
- "char_freq" - Analyzes character frequency across all input items

**count_what** (menu): When stat_mode is "count", specifies what to count:
- "items" - Total number of list items
- "words" - Total word count across all items
- "characters" - Total character count across all items
- "lines" - Total line count (counts newlines + 1 per item)

**preserve_order** (bool, default: True): When True in deduplicate mode, maintains the original order of first occurrences. When False, sorts deduplicated items alphabetically.

**top_n** (int, default: 0): For frequency modes, limits output to top N most frequent items. Set to 0 for unlimited (all items).

**case_sensitive** (bool, default: False): When True, treats uppercase and lowercase as distinct in deduplication and frequency analysis. When False, normalizes to lowercase.

**format_output** (menu, default: "plain"): Determines output format:
- "plain" - Simple values: count as string, or "key: value" for frequencies
- "labeled" - Descriptive labels: "Items count: 5" or "Item 1: value"
- "json" - JSON formatted output for programmatic processing

**enabled** (bool, default: True): Enables/disables the node's functionality.

### Input/Output

**Input:** List[str] of text items to analyze
**Output:** List[str] containing statistical results (format depends on stat_mode and format_output)

### Usage Examples

**Example 1: Count items**
```
Input: ["apple", "banana", "cherry", "date"]
stat_mode: "count"
count_what: "items"
format_output: "plain"

Output: ["4"]
```

**Example 2: Count words**
```
Input: ["Hello world", "How are you"]
stat_mode: "count"
count_what: "words"
format_output: "labeled"

Output: ["Words count: 5"]
```

**Example 3: Deduplicate with order preservation**
```
Input: ["apple", "banana", "apple", "cherry", "banana"]
stat_mode: "deduplicate"
preserve_order: True
case_sensitive: False

Output: ["apple", "banana", "cherry"]
```

**Example 4: Word frequency analysis**
```
Input: ["the quick brown fox", "the lazy dog"]
stat_mode: "word_freq"
top_n: 3
case_sensitive: False
format_output: "plain"

Output: ["the: 2", "quick: 1", "brown: 1"]
```

**Example 5: Character frequency with JSON output**
```
Input: ["hello"]
stat_mode: "char_freq"
top_n: 2
format_output: "json"

Output: ['{"l": 2, "h": 1}']
```

### Notes

- Word counting uses simple whitespace splitting
- Line counting includes the implicit final line (count of `\n` + 1 per item)
- Deduplication with preserve_order=False uses alphabetical sorting
- Frequency analysis with top_n=0 returns all items sorted by frequency (most common first)
- JSON output format varies by operation type (single count, list, or frequency dictionary)
- Case-insensitive mode normalizes text to lowercase for comparison but preserves original case in output

---

## 15. SearchNode

**SearchNode: A node that searches and filters text items based on patterns and keywords.**

Supports multiple search modes (contains, exact, starts_with, ends_with, regex) and can combine multiple keywords with AND/OR/NOT boolean logic. Provides dual outputs for matching and non-matching items, making it ideal for filtering and routing text through node graphs.

### Key Features

- Multiple search modes including full regex support
- Boolean logic for combining multiple search terms (AND/OR/NOT)
- Case-sensitive and case-insensitive matching
- Dual outputs for matching and non-matching items
- Invert match capability for negative filtering

### Parameters

**search_text** (str, default: ""): The search term(s) to match against. Multiple terms can be separated by commas or spaces. Each term is treated according to the boolean_mode setting.

**search_mode** (menu, default: "contains"): Determines how to match search terms against text:
- "contains" - Item contains the search term anywhere
- "exact" - Item exactly equals the search term
- "starts_with" - Item starts with the search term
- "ends_with" - Item ends with the search term
- "regex" - Search term is interpreted as a regular expression

**case_sensitive** (bool, default: False): When True, matches are case-sensitive. When False, ignores case differences.

**boolean_mode** (menu, default: "OR"): Controls how multiple search terms are combined:
- "OR" - Matches items that match ANY search term
- "AND" - Matches items that match ALL search terms
- "NOT" - Matches items that match NONE of the search terms

**invert_match** (bool, default: False): When True, inverts the matching logic (matching items go to non-matching output and vice versa).

**enabled** (bool, default: True): Enables/disables the node's functionality.

### Input/Output

**Input:** List[str] of items to search/filter
**Outputs:**
- Output 0 (Matching Items): Items that match the search criteria
- Output 1 (Non-Matching Items): Items that don't match the search criteria
- Output 2 (Empty): Always empty list (reserved for future use)

### Usage Examples

**Example 1: Simple contains search**
```
Input: ["apple pie", "banana bread", "cherry tart", "apple cake"]
search_text: "apple"
search_mode: "contains"
case_sensitive: False

Output 0 (Matching): ["apple pie", "apple cake"]
Output 1 (Non-Matching): ["banana bread", "cherry tart"]
```

**Example 2: Exact match**
```
Input: ["cat", "cats", "cat house", "dog"]
search_text: "cat"
search_mode: "exact"

Output 0 (Matching): ["cat"]
Output 1 (Non-Matching): ["cats", "cat house", "dog"]
```

**Example 3: Multiple terms with OR logic**
```
Input: ["red apple", "green banana", "red cherry", "yellow lemon"]
search_text: "red, green"
boolean_mode: "OR"

Output 0 (Matching): ["red apple", "green banana", "red cherry"]
Output 1 (Non-Matching): ["yellow lemon"]
```

**Example 4: Multiple terms with AND logic**
```
Input: ["red apple", "green apple", "red cherry", "green banana"]
search_text: "apple, red"
search_mode: "contains"
boolean_mode: "AND"

Output 0 (Matching): ["red apple"]
Output 1 (Non-Matching): ["green apple", "red cherry", "green banana"]
```

**Example 5: Regex pattern matching**
```
Input: ["file_001.txt", "file_002.txt", "document.pdf", "file_abc.txt"]
search_text: "file_\\d+\\.txt"
search_mode: "regex"

Output 0 (Matching): ["file_001.txt", "file_002.txt"]
Output 1 (Non-Matching): ["document.pdf", "file_abc.txt"]
```

**Example 6: NOT logic for exclusion**
```
Input: ["apple", "banana", "apricot", "cherry"]
search_text: "app"
search_mode: "starts_with"
boolean_mode: "NOT"

Output 0 (Matching): ["banana", "cherry"]
Output 1 (Non-Matching): ["apple", "apricot"]
```

**Example 7: Inverted match**
```
Input: ["test.txt", "data.csv", "report.pdf"]
search_text: ".txt"
search_mode: "ends_with"
invert_match: True

Output 0 (Matching): ["data.csv", "report.pdf"]
Output 1 (Non-Matching): ["test.txt"]
```

### Notes

- Multiple search terms in search_text are split by commas or whitespace
- Empty search_text matches nothing (all items go to non-matching output)
- Invalid regex patterns generate warnings and fail to match
- Case-insensitive mode converts both text and search terms to lowercase for comparison
- Boolean mode NOT is equivalent to inverting each term individually
- Combining invert_match with boolean_mode allows complex filtering logic
- The node provides warnings for regex errors in the log
