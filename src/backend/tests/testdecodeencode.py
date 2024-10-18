import os
import re
import codecs

ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)

def decode_escapes(s):
    def decode_match(match):
        try:
            return codecs.decode(match.group(0), 'unicode-escape')
        except UnicodeDecodeError:
            # In case we matched the wrong thing after a double-backslash
            return match.group(0)

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)

inputfile = os.path.abspath("output.txt")

with open(inputfile, "r") as f:
    content = f.read()
    content = content.replace("[","").replace("]","")
    content = decode_escapes(content)
    print(content)

input_file_path = os.path.abspath("output_fix.txt")
with open(input_file_path, "w") as f:
    f.write(content)
