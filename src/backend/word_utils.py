import string


def load_stop_words():
    file_path = '../stop_words.data'
    with open(file_path, 'r') as f:
        return set(line.strip() for line in f)


def extract_key_words(text, num_words=4):
    stop_words = load_stop_words()

    # Convert to lowercase and remove punctuation
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Split into words and filter out stop words
    words = [word for word in text.split() if word not in stop_words]

    # Return the first num_words
    return words[-num_words:]
