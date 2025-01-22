1. QueryNode:
```
QueryNode: A node that interfaces with Large Language Models (LLMs) to process text prompts and generate responses.

This node serves as a bridge between the node graph system and local LLM installations, enabling prompt-based
text generation and processing. It can handle single or multiple prompts, with options to limit processing
for development or resource management.

Key Features:
    1. LLM Integration:
        - Automatically detects and connects to local LLM installations
        - Supports dynamic LLM selection and switching
        - Provides fallback mechanisms when preferred LLM is unavailable
        
    2. Prompt Processing:
        - Handles both single and batch prompt processing
        - Maintains response history
        - Supports forced response regeneration
        - Provides clean, formatted LLM responses

Parameters:
    limit (bool): 
        When True, restricts processing to only the first prompt
        Useful for testing or managing resource usage
        
    response (List[str]): 
        Stores the history of LLM responses
        Updated after each successful processing
        
    llm_name (str): 
        Identifier for the target LLM (e.g., "Ollama")
        Defaults to "Ollama" but can be auto-detected
        
    find_llm (button): 
        Triggers automatic LLM detection
        Updates llm_name with found installation
        
    respond (button):
        Forces reprocessing of current prompts
        Updates responses regardless of cache
```

2. NullNode:
```
Represents a Null Node in the workspace.

The Null Node is a simple pass-through node that doesn't modify its input.
It has a single input and can connect its output to multiple other nodes.
```

3. LooperNode:
```
LooperNode: A powerful node for iterative processing of data with configurable loop behavior.

This node enables iterative operations by managing internal input and output connections, making it 
ideal for tasks that require repeated processing or accumulation of results. Think of it as a 
sophisticated 'for' loop that can process data iteratively while maintaining node graph connectivity.

Parameters:
    min (int): Starting value for the loop iteration (must be non-negative)
    max (int): Ending value for the loop iteration (must be non-negative)
    step (int): Increment value between iterations (cannot be zero)
    max_from_input (bool): When enabled, sets max iterations based on input data length
    feedback_mode (bool): Enables feedback loop mode where each iteration's output feeds into the next
    use_test (bool): When enabled, runs only a single test iteration
    cook_loops (bool): Controls whether to force cook operations on each loop iteration
    test_number (int): Specific iteration to run when use_test is enabled (must be between min and max)
    input_hook (str): Custom input processing hook (advanced usage)
    output_hook (str): Custom output processing hook (advanced usage)
    timeout_limit (float): Maximum execution time in seconds (default: 300.0)
    data_limit (int): Maximum memory usage in bytes (default: 200MB)
```

4. FileOutNode:
```
Write the given content to a text file. The function provides a refresh button to force the write.

The hash check helps to determine whether the file needs to be written again. If the hash of the input content matches the previously recorded hash and `force_write` is False, the function will skip writing the file.

Parameters:
    filename (str): The name of the file to write to.
    content (list of str): A list of strings to be written to the file.
    refresh (button): Force the file to be written regardless of content changes or hash matching. Default is False.
    format_output (bool): When True (default), formats output by stripping brackets and joining with newlines. 
                        When False, preserves Python list format (e.g. ["item1", "item2"]) for round-trip processing.
```

5. FileInNode:
```
FileInNode: A node that reads and parses text files or input strings into lists.

This node can either read from a file or take input text, parsing formatted string lists 
like "[item1, item2, item3]" into proper Python lists. If no input is provided, reads 
from the specified file.

Parameters:
    file_name (str): Path to the target file (defaults to "./input.txt")
    file_text (str): Contains the current file content
    refresh (button): Force reloads the file content

Input Processing:
    - If input is provided, uses that instead of file content
    - Parses text in format "[item1, item2, ...]" into list items
    - Handles quoted strings, escapes, and empty items
    - Falls back to single-item list for invalid formats

Features:
    - Monitors file changes using MD5 hashing
    - Automatically reloads when file content changes
    - Provides error reporting for file access issues
    - Supports force refresh via button
```

6. TextNode:
```
A node that manipulates text strings with advanced list support.

Takes a list of strings as input and either appends or prepends text based on the node's parameters.
The text_string parameter supports both plain strings and Python-style list syntax:

Plain string: "hello" -> creates ["hello"]
List syntax: ["first", "second"] -> creates ["first", "second"]

List Syntax Details:
- Uses Python-style list notation with square brackets
- Strings must be quoted with either single (') or double (") quotes
- Mixed quote types are supported: ["first", 'second']
- Supports escaped quotes: ["escaped\\"quote"]
- Empty strings are preserved: ["", "test", ""]
- Empty list [] creates [""]
- Invalid syntax falls back to treating input as plain string

Parameters:
text_string: The text to process. Accepts plain string or list syntax
pass_through: When True, processes input data. When False, uses only text_string
per_item: When True, applies each text string to every input item
        When False, concatenates lists of strings
prefix: When True, adds text before input. When False, adds after
```

7. SplitNode:
```
SplitNode: A versatile node for splitting lists of strings into two parts based on various expressions.

This node takes a list of strings as input and splits it into two outputs: selected items and remaining items.
The split behavior is controlled by the 'split_expr' parameter which supports two types of expressions:

1. List Selection Expression: [index] or [start:end:step]
    - Uses Python-style list slicing syntax
    - Examples:
        - [0]     -> Selects the first item
        - [-1]    -> Selects the last item
        - [1:3]   -> Selects items at indices 1 and 2
        - [::2]   -> Selects every other item
        - [::-1]  -> Selects all items in reverse order
        - [1:]    -> Selects all items from index 1 onwards
        - [:-1]   -> Selects all items except the last one

2. Random Selection Expression: random(seed[,count])
    - Randomly selects items from the input list
    - seed can be either:
        - 'time' for time-based randomization
        - a number for deterministic randomization
    - Optional count parameter specifies how many items to select
    - Examples:
        - random(time)      -> Randomly selects 1 item using current time as seed
        - random(42)        -> Randomly selects 1 item using seed 42
        - random(time,3)    -> Randomly selects 3 items using current time as seed
        - random(42,5)      -> Randomly selects 5 items using seed 42

Parameters:
    enabled (bool): Enables/disables the node's functionality
    split_expr (str): Expression defining how to split the input list

Outputs:
    Selected Items (output 0): Items that match the split expression criteria
    Remaining Items (output 1): Items that weren't selected
    Empty (output 2): Always empty list (reserved for future use)
```

8. SectionNode:
"""
A node that sections input text based on prefix matching patterns.

Separates input text into three outputs based on two prefix patterns. 
Lines matching either prefix are routed to corresponding outputs, 
with unmatched lines sent to the third output.

Prefix Pattern Types:
    1. Wildcard Patterns:
        * Matches any sequence of characters
        ? Matches exactly one character
        Examples:
        - "Q*" matches "Q:", "Query", "Question"
        - "Speaker?" matches "Speaker1", "Speaker2"
        - "*Bot" matches "ChatBot", "TestBot"

    2. Regex Patterns (starting with ^):
        Supports full regex matching
        Example: "^Chapter\d+" matches "Chapter1", "Chapter22"

    3. Shortcut Patterns (starting with @):
        Predefined regex patterns from a configuration file
        Example: "@scene" might match scene headings
        
Parameters:
    prefix1 (str): First prefix to match
    prefix2 (str): Second prefix to match
    delimiter (str): Separates prefix from content (default: ":")
    trim_prefix (bool): Removes prefix when True
    enabled (bool): Enables/disables node functionality

Inputs:
    input (List[str]): Strings to process

Outputs:
    output[0]: Lines matching first prefix
    output[1]: Lines matching second prefix
    output[2]: Unmatched lines

Example Usage (Simple):
    Input: ["Q: What time?", "A: 3 PM", "Note: check later"]
    prefix1 = "Q*"
    prefix2 = "A*"
    Output[0]: ["What time?"]
    Output[1]: ["3 PM"]
    Output[2]: ["Note: check later"]

Example Usage (Complex):
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

Notes:
    - Whitespace around prefixes and delimiters is normalized
    - Empty outputs contain [""] rather than []
    - Wildcard patterns are converted to regex internally
    - Delimiter within prefix is treated as part of the prefix
"""


9. MakeListNode(Node):
"""
A node that takes a string list as input, parses the first item, and outputs a new string list.

This node uses the parse_list function to split the input string into a list of strings.
It can optionally limit the number of output items based on the 'limit' and 'max_list' parameters.

Attributes:
    _is_time_dependent (bool): Always False for this node.

parse_list: 

Parse numbered lists from text into a list of strings, supporting both numeric and word-based numbering.

This function intelligently extracts numbered lists from text while handling various numbering formats
and multi-line items. It's particularly useful for processing structured text content like meeting notes,
instructions, or any text containing numbered lists.

Capabilities:
    - Supports multiple numbering formats:
        * Arabic numerals (1., 2., 3.)
        * Written numbers (one., two., three.)
        * Ordinal numbers (first., second., third.)
        * Compound numbers (twenty-one, ninety-nine)
    - Handles various separators between numbers and text (. : - _)
    - Preserves multi-line list items
    - Maintains original text formatting within list items
    - Case-insensitive number word recognition

Limitations:
    - Only processes the first numbered list encountered in the text
    - Cannot handle nested lists
    - Maximum number support up to thousands
    - Does not preserve the original numbering format
    - Cannot process Roman numerals (i., ii., iii.)
    - Does not handle lettered lists (a., b., c.)

Args:
    text (str): Input text containing a numbered list

Returns:
    Union[str, List[str]]: 
        - If a numbered list is found: List of strings, each representing a list item
        - If no list is found or input is not a string: Original text or empty string

Examples:
    >>> text = '''
    ... Meeting Agenda:
    ... 1. Review previous minutes
    ...    Additional notes about minutes
    ... 2. Discuss new projects
    ... 3. Plan next meeting'''
    >>> parse_list(text)
    ['Review previous minutes Additional notes about minutes',
    'Discuss new projects',
    'Plan next meeting']

    >>> text = '''
    ... Project Steps:
    ... First: Initialize repository
    ... Second: Set up environment
    ... Third: Begin development'''
    >>> parse_list(text)
    ['Initialize repository',
    'Set up environment',
    'Begin development']

Notes:
    - List items are assumed to start with a number or number word followed by a separator
    - Subsequent lines without numbers are considered continuation of the previous item
    - The function preserves internal spacing but trims leading/trailing whitespace
    - Non-string inputs return an empty string rather than raising an error
"""