"""
Smart Parse - Intelligent list parsing for inline numbered lists.

This module provides enhanced list parsing that can extract items from text where
numbered markers appear inline (on the same line) rather than on separate lines.

The parser looks for numbered markers in text and splits at those positions.
When you enable "sticky" mode, it locks onto the first marker type it finds
(numeric, cardinal words, or ordinal words) and ignores all other types.

Attributes:
    NUMBER_WORDS (dict): Combined mapping of all number words to numeric values.
    CARDINAL_WORDS (dict): Cardinal numbers only (one, two, twenty-one, etc.).
    ORDINAL_WORDS (dict): Ordinal numbers only (first, second, twenty-first, etc.).

Note:
    Marker Types:
        - Numeric: 1. 2. 3. -1. 0. 100.
        - Cardinal words: one. two. three. twenty-one.
        - Ordinal words: first. second. third. twenty-first.

    Separators:
        Markers must be followed by one of: ``. : - _``
        Then whitespace (or end of string).

    Parameters for parse_list:
        - **sticky** (default: False): Enable inline parsing. Without this, works line-by-line.
        - **ordered** (default: False): Markers must go in one direction (ascending or descending).
        - **strict** (default: False): Markers must differ by exactly 1.
        - **greedy** (default: False): After a break, pick up from the rejected marker.

Example:
    Basic sticky parsing::

        >>> from smart_parse import parse_list
        >>> parse_list("1. Apple 2. Banana 3. Cherry", sticky=True)
        ['Apple', 'Banana', 'Cherry']

    Handles embedded periods (locks onto numeric, ignores "five.")::

        >>> parse_list("1. Fourth five. 2. Sixty", sticky=True)
        ['Fourth five.', 'Sixty']

    Phone numbers (digits in content don't confuse it)::

        >>> parse_list("1. (909) 345-7789 2. (990) 233-6678", sticky=True)
        ['(909) 345-7789', '(990) 233-6678']

    With ordinal words::

        >>> parse_list("first: Apple second: Banana third: Cherry", sticky=True)
        ['Apple', 'Banana', 'Cherry']

    Ordered mode (rejects out-of-order markers)::

        >>> parse_list("1. A 2. B 5. C 3. D", sticky=True, ordered=True)
        ['A', 'B', 'C 3. D']

    Strict mode (markers must be consecutive)::

        >>> parse_list("1. A 2. B 4. C", sticky=True, strict=True)
        ['A', 'B 4. C']

    Greedy mode (pick up the thread after break)::

        >>> parse_list("1. A 2. B 4. C 5. D", sticky=True, strict=True, greedy=False)
        ['A', 'B 4. C 5. D']

        >>> parse_list("1. A 2. B 4. C 5. D", sticky=True, strict=True, greedy=True)
        ['A', 'B 4. C', 'D']

    Combined ordered + strict (consecutive AND single direction)::

        >>> parse_list("3. A 2. B 1. C", sticky=True, ordered=True, strict=True)
        ['A', 'B', 'C']

    Zigzag with strict only (direction can change)::

        >>> parse_list("1. A 2. B 1. C 2. D", sticky=True, strict=True, greedy=True)
        ['A', 'B', 'C', 'D']
"""
import re


def generate_number_words():
    """
    Generate dictionaries mapping number words to their numeric values.

    Returns:
        tuple: (combined_dict, cardinal_dict, ordinal_dict)
            - combined_dict: All number words (for backward compatibility)
            - cardinal_dict: Cardinal numbers (one, two, twenty-one, etc.)
            - ordinal_dict: Ordinal numbers (first, second, twenty-first, etc.)
    """
    units = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
    tens = ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    scales = ["hundred", "thousand"]

    ordinal_units = ["", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth"]
    ordinal_teens = ["tenth", "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth", "nineteenth"]
    ordinal_tens = ["twentieth", "thirtieth", "fortieth", "fiftieth", "sixtieth", "seventieth", "eightieth",
                    "ninetieth"]

    number_words = {}
    cardinal_words = {}
    ordinal_words = {}

    # Add cardinal numbers
    for i, word in enumerate(units[1:] + teens):
        number_words[word] = i + 1
        cardinal_words[word] = i + 1

    for i, ten in enumerate(tens):
        number_words[ten] = (i + 2) * 10
        cardinal_words[ten] = (i + 2) * 10

    # Add ordinal numbers
    for i, word in enumerate(ordinal_units[1:] + ordinal_teens):
        number_words[word] = i + 1
        ordinal_words[word] = i + 1

    for i, ten in enumerate(ordinal_tens):
        number_words[ten] = (i + 2) * 10
        ordinal_words[ten] = (i + 2) * 10

    # Add compounds (twenty-one to ninety-nine, and twenty-first to ninety-ninth)
    for i, ten in enumerate(tens):
        for j, unit in enumerate(units[1:]):
            cardinal = f"{ten}-{unit}"
            ordinal = f"{ten}-{ordinal_units[j + 1]}"
            number_words[cardinal] = (i + 2) * 10 + (j + 1)
            number_words[ordinal] = (i + 2) * 10 + (j + 1)
            cardinal_words[cardinal] = (i + 2) * 10 + (j + 1)
            ordinal_words[ordinal] = (i + 2) * 10 + (j + 1)

    # Add scales
    for i, scale in enumerate(scales):
        number_words[scale] = 10 ** ((i + 1) * 2)
        number_words[f"{scale}th"] = 10 ** ((i + 1) * 2)
        cardinal_words[scale] = 10 ** ((i + 1) * 2)
        ordinal_words[f"{scale}th"] = 10 ** ((i + 1) * 2)

    return number_words, cardinal_words, ordinal_words


NUMBER_WORDS, CARDINAL_WORDS, ORDINAL_WORDS = generate_number_words()


def parse_list(text, sticky=False, ordered=False, strict=False, greedy=False):
    """
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
        sticky (bool): When True, enables inline parsing that locks onto the first marker type found
            (numeric, cardinal, or ordinal) and only splits on markers of that same type.
            Default is False (line-by-line parsing).
        ordered (bool): When True, only accepts markers that follow ascending or descending order.
            Default is False.
        strict (bool): When True, only accepts markers that differ by exactly 1 from the previous marker.
            Default is False.
        greedy (bool): When True with ordered/strict, allows picking up the sequence after a break
            by tracking rejected markers. Default is False.

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

        >>> # Sticky parsing for inline lists
        >>> text = "1. Fourth five. 2. Sixty"
        >>> parse_list(text, sticky=True)
        ['Fourth five.', 'Sixty']

        >>> # With ordered=True, markers must ascend or descend
        >>> text = "1. Apple 3. Banana 2. Cherry"
        >>> parse_list(text, sticky=True, ordered=True)
        ['Apple 3. Banana 2. Cherry']

        >>> # With strict=True, markers must differ by exactly 1
        >>> text = "1. Apple 2. Banana 4. Cherry"
        >>> parse_list(text, sticky=True, strict=True)
        ['Apple', 'Banana 4. Cherry']

        >>> # With greedy=True, pick up the thread after breaks
        >>> text = "1. A 2. B 4. C 5. D"
        >>> parse_list(text, sticky=True, strict=True, greedy=True)
        ['A', 'B 4. C', 'D']

    Notes:
        - List items are assumed to start with a number or number word followed by a separator
        - Subsequent lines without numbers are considered continuation of the previous item
        - The function preserves internal spacing but trims leading/trailing whitespace
        - Non-string inputs return an empty string rather than raising an error
        - When sticky=True, newlines in content are collapsed to spaces
    """

    if not isinstance(text, str):
        return ""  # Return empty string if text is not a string

    if sticky:
        return _parse_list_sticky(text, ordered, strict, greedy)

    # Original line-by-line parsing logic
    number_word_pattern = '|'.join(sorted(NUMBER_WORDS.keys(), key=len, reverse=True))
    lines = text.split('\n')

    start_index = next((i for i, line in enumerate(lines)
                        if re.match(r'^(\d+|{word_pattern})([.:\-_]\s)'.format(word_pattern=number_word_pattern),
                                    line.strip(), flags=re.IGNORECASE)), None)

    if start_index is None:
        return text  # If no numbered list is found, return the original text

    processed_items = []
    current_item = ""
    for line in lines[start_index:]:
        clean_line = re.sub(r'^(\d+|{word_pattern})([.:\-_]\s)'.format(word_pattern=number_word_pattern), '',
                            line.strip(), flags=re.IGNORECASE)

        if re.match(r'^(\d+|{word_pattern})([.:\-_]\s)'.format(word_pattern=number_word_pattern), line.strip(),
                    flags=re.IGNORECASE):
            if current_item:
                processed_items.append(current_item.strip())
            current_item = clean_line
        else:
            current_item += " " + clean_line

    if current_item:
        processed_items.append(current_item.strip())

    return processed_items


def _parse_list_sticky(text, ordered=False, strict=False, greedy=False):
    """
    Internal function for sticky (inline) list parsing.

    Finds the first marker, locks onto its type (numeric, cardinal, or ordinal),
    and splits only on markers of that same type.
    """
    # Build patterns for each marker type
    cardinal_pattern = '|'.join(sorted(CARDINAL_WORDS.keys(), key=len, reverse=True))
    ordinal_pattern = '|'.join(sorted(ORDINAL_WORDS.keys(), key=len, reverse=True))

    # Pattern to find any marker: (start of string or whitespace) + marker + separator + (whitespace or end)
    # Using word boundary to avoid matching "one" in "someone"
    numeric_marker_re = re.compile(r'(?:^|(?<=\s))(-?\d+)([.:\-_])(?:\s|$)', re.IGNORECASE)
    cardinal_marker_re = re.compile(r'(?:^|(?<=\s))\b(' + cardinal_pattern + r')\b([.:\-_])(?:\s|$)', re.IGNORECASE)
    ordinal_marker_re = re.compile(r'(?:^|(?<=\s))\b(' + ordinal_pattern + r')\b([.:\-_])(?:\s|$)', re.IGNORECASE)

    # Find first marker of each type
    first_numeric = numeric_marker_re.search(text)
    first_cardinal = cardinal_marker_re.search(text)
    first_ordinal = ordinal_marker_re.search(text)

    # Determine which type appears first
    first_markers = []
    if first_numeric:
        first_markers.append(('numeric', first_numeric.start(), first_numeric))
    if first_cardinal:
        first_markers.append(('cardinal', first_cardinal.start(), first_cardinal))
    if first_ordinal:
        first_markers.append(('ordinal', first_ordinal.start(), first_ordinal))

    if not first_markers:
        return text  # No markers found

    # Sort by position and get the first one
    first_markers.sort(key=lambda x: x[1])
    marker_type, _, first_match = first_markers[0]

    # Select the appropriate regex and word dict based on marker type
    if marker_type == 'numeric':
        marker_re = numeric_marker_re
        word_dict = None
    elif marker_type == 'cardinal':
        marker_re = cardinal_marker_re
        word_dict = CARDINAL_WORDS
    else:  # ordinal
        marker_re = ordinal_marker_re
        word_dict = ORDINAL_WORDS

    # Find all markers of the selected type
    all_markers = list(marker_re.finditer(text))

    if not all_markers:
        return text

    # Extract marker info: (position, end_position, value)
    marker_info = []
    for match in all_markers:
        marker_text = match.group(1)
        if marker_type == 'numeric':
            value = int(marker_text)
        else:
            value = word_dict.get(marker_text.lower(), 0)
        marker_info.append((match.start(), match.end(), value))

    # Apply ordered/strict filtering
    filtered_markers = [marker_info[0]]  # Always keep the first marker
    prev_value = marker_info[0][2]
    direction = None  # Will be determined by second marker

    for start, end, value in marker_info[1:]:
        accept = True

        if strict:
            # Must differ by exactly 1
            if abs(value - prev_value) != 1:
                accept = False

        if ordered and accept:
            # Must follow consistent direction
            if direction is None:
                # Determine direction from first two markers
                if value > prev_value:
                    direction = 'asc'
                elif value < prev_value:
                    direction = 'desc'
                else:
                    accept = False  # Same value, reject
            else:
                if direction == 'asc' and value <= prev_value:
                    accept = False
                elif direction == 'desc' and value >= prev_value:
                    accept = False

        if accept:
            filtered_markers.append((start, end, value))
            prev_value = value
        elif greedy:
            # Pick up the thread: update prev_value to rejected marker
            # so subsequent markers can continue from here
            prev_value = value
            if ordered:
                direction = None  # Reset direction for new thread

    # Split text at marker positions
    result = []
    for i, (start, end, value) in enumerate(filtered_markers):
        if i < len(filtered_markers) - 1:
            next_start = filtered_markers[i + 1][0]
            content = text[end:next_start]
        else:
            content = text[end:]

        # Collapse newlines to spaces and strip
        content = ' '.join(content.split())
        result.append(content)

    return result
