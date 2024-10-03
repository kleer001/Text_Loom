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
