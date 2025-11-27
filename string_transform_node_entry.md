## 16. StringTransformNode

**StringTransformNode: A node that performs various string transformations on text items.**

Applies text transformations including find/replace operations, regex-based substitutions, case transformations, whitespace normalization, and trimming to each item in the input list. This is a versatile text manipulation node for cleaning, reformatting, and standardizing text data.

### Key Features

- Find and replace with literal or regex patterns
- Case transformations (upper, lower, title, capitalize)
- Whitespace trimming (start, end, both)
- Whitespace normalization (collapse multiple spaces)
- Case-sensitive or case-insensitive matching
- Per-item transformation (maintains list structure)

### Parameters

**operation** (menu): Determines the type of transformation to apply:
- "find_replace" - Find and replace text (literal or regex)
- "regex_replace" - Regex-based find and replace (same as find_replace with use_regex=True)
- "case_transform" - Change case based on case_mode parameter
- "trim" - Remove whitespace based on trim_mode parameter
- "whitespace_normalize" - Collapse multiple spaces into single spaces

**find_text** (str, default: ""): The text or pattern to search for. Used with find_replace and regex_replace operations.

**replace_text** (str, default: ""): The replacement text. Supports regex capture groups when use_regex is True.

**use_regex** (bool, default: False): When True, treats find_text as a regular expression pattern. When False, performs literal string matching.

**case_sensitive** (bool, default: True): When True, find/replace operations are case-sensitive. When False, ignores case differences during matching.

**case_mode** (menu, default: "upper"): Determines case transformation when operation is "case_transform":
- "upper" - Convert to uppercase
- "lower" - Convert to lowercase
- "title" - Convert to title case (first letter of each word capitalized)
- "capitalize" - Capitalize first letter only

**trim_mode** (menu, default: "both"): Determines trimming behavior when operation is "trim":
- "both" - Remove whitespace from start and end
- "start" - Remove whitespace from start only
- "end" - Remove whitespace from end only

**normalize_spaces** (bool, default: False): When True, applies whitespace normalization after the primary operation (collapses multiple spaces to single space). Not applied when operation is already "whitespace_normalize".

**enabled** (bool, default: True): Enables/disables the node's functionality.

### Input/Output

**Input:** List[str] of text items to transform
**Output:** List[str] of transformed text items (maintains same list length)

### Usage Examples

**Example 1: Simple find and replace**
```
Input: ["Hello world", "Hello universe", "Goodbye world"]
operation: "find_replace"
find_text: "world"
replace_text: "Earth"
case_sensitive: True

Output: ["Hello Earth", "Hello universe", "Goodbye Earth"]
```

**Example 2: Case-insensitive find and replace**
```
Input: ["Hello World", "HELLO WORLD", "hello world"]
operation: "find_replace"
find_text: "hello"
replace_text: "Hi"
case_sensitive: False

Output: ["Hi World", "Hi WORLD", "Hi world"]
```

**Example 3: Regex pattern replacement**
```
Input: ["Price: $99.99", "Cost: $149.50", "Total: $1,234.56"]
operation: "find_replace"
find_text: "\\$([0-9,]+\\.[0-9]{2})"
replace_text: "USD \\1"
use_regex: True

Output: ["Price: USD 99.99", "Cost: USD 149.50", "Total: USD 1,234.56"]
```

**Example 4: Case transformation**
```
Input: ["hello world", "GOODBYE MOON", "Mixed Case Text"]
operation: "case_transform"
case_mode: "title"

Output: ["Hello World", "Goodbye Moon", "Mixed Case Text"]
```

**Example 5: Trim whitespace**
```
Input: ["  hello  ", "  world  ", "  test  "]
operation: "trim"
trim_mode: "both"

Output: ["hello", "world", "test"]
```

**Example 6: Whitespace normalization**
```
Input: ["Multiple    spaces   here", "Too  many    gaps"]
operation: "whitespace_normalize"

Output: ["Multiple spaces here", "Too many gaps"]
```

**Example 7: Combined operations with normalize_spaces**
```
Input: ["Hello    World", "Goodbye     Moon"]
operation: "case_transform"
case_mode: "upper"
normalize_spaces: True

Output: ["HELLO WORLD", "GOODBYE MOON"]
```

**Example 8: Regex with capture groups**
```
Input: ["Name: John Doe", "Name: Jane Smith"]
operation: "find_replace"
find_text: "Name: (\\w+) (\\w+)"
replace_text: "\\2, \\1"
use_regex: True

Output: ["Doe, John", "Smith, Jane"]
```

**Example 9: Remove all digits**
```
Input: ["Item123", "Product456", "Order789"]
operation: "find_replace"
find_text: "\\d+"
replace_text: ""
use_regex: True

Output: ["Item", "Product", "Order"]
```

**Example 10: Trim start only**
```
Input: ["  leading spaces  ", "  more spaces  "]
operation: "trim"
trim_mode: "start"

Output: ["leading spaces  ", "more spaces  "]
```

### Notes

- All transformations are applied to each list item independently
- The list structure is preserved (output has same number of items as input)
- Invalid regex patterns generate warnings and return text unchanged
- Regex capture groups are supported in replace_text using \\1, \\2, etc.
- When use_regex is False, special regex characters in find_text are automatically escaped
- normalize_spaces can be combined with any operation except "whitespace_normalize"
- Case transformations follow Python's str.upper(), str.lower(), str.title(), and str.capitalize() behavior
- Empty find_text returns the original text unchanged
- The node uses hash-based change detection to avoid unnecessary reprocessing
