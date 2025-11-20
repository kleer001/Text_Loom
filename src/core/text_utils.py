import re


def generate_number_words():
    units = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
    tens = ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    scales = ["hundred", "thousand"]

    ordinal_units = ["", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth"]
    ordinal_teens = ["tenth", "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth", "nineteenth"]
    ordinal_tens = ["twentieth", "thirtieth", "fortieth", "fiftieth", "sixtieth", "seventieth", "eightieth",
                    "ninetieth"]

    number_words = {}

    # Add cardinal numbers
    for i, word in enumerate(units[1:] + teens):
        number_words[word] = i + 1

    for i, ten in enumerate(tens):
        number_words[ten] = (i + 2) * 10

    # Add ordinal numbers
    for i, word in enumerate(ordinal_units[1:] + ordinal_teens):
        number_words[word] = i + 1

    for i, ten in enumerate(ordinal_tens):
        number_words[ten] = (i + 2) * 10

    # Add compounds (twenty-one to ninety-nine, and twenty-first to ninety-ninth)
    for i, ten in enumerate(tens):
        for j, unit in enumerate(units[1:]):
            cardinal = f"{ten}-{unit}"
            ordinal = f"{ten}-{ordinal_units[j + 1]}"
            number_words[cardinal] = (i + 2) * 10 + (j + 1)
            number_words[ordinal] = (i + 2) * 10 + (j + 1)

    # Add scales
    for i, scale in enumerate(scales):
        number_words[scale] = 10 ** ((i + 1) * 2)
        number_words[f"{scale}th"] = 10 ** ((i + 1) * 2)

    return number_words


NUMBER_WORDS = generate_number_words()


def parse_list(text):

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

    if not isinstance(text, str):
        return ""  # Return empty string if text is not a string

    number_words = generate_number_words()
    number_word_pattern = '|'.join(sorted(number_words.keys(), key=len, reverse=True))
    lines = text.split('\n')

    start_index = next((i for i, line in enumerate(lines)
                        if re.match(r'^(\d+|{word_pattern})([.:\-_]?\s)'.format(word_pattern=number_word_pattern),
                                    line.strip(), flags=re.IGNORECASE)),None)

    if start_index is None:
        return text  # If no numbered list is found, return the original text

    processed_items = []
    current_item = ""
    for line in lines[start_index:]:
        clean_line = re.sub(r'^(\d+|{word_pattern})([.:\-_]?\s)'.format(word_pattern=number_word_pattern), '',
                            line.strip(), flags=re.IGNORECASE)

        if re.match(r'^(\d+|{word_pattern})([.:\-_]?\s)'.format(word_pattern=number_word_pattern), line.strip(),
                    flags=re.IGNORECASE):
            if current_item:
                processed_items.append(current_item.strip())
            current_item = clean_line
        else:
            current_item += " " + clean_line

    if current_item:
        processed_items.append(current_item.strip())

    return processed_items
