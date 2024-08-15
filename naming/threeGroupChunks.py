#!/usr/bin/env python3

import sys
import re
import os
import itertools

def validate_input(lines):
    if len(lines) != 3:  # Now only expecting 3 lines
        return False
    
    patterns = lines[0].strip().split(',')
    for pattern in patterns:
        if not re.match(r'^[34]+$', pattern):  # Only 3 and 4 are valid
            return False
    
    for i, line in enumerate(lines[1:], start=3):  # Start checking from 3-letter words
        words = line.strip().split(',')
        if not all(len(word.strip()) == i for word in words):
            return False
    
    return True

def generate_unique_combinations(pattern, word_dict):
    word_lists = [word_dict[digit] for digit in pattern]
    for combo in itertools.product(*word_lists):
        if len(set(combo)) == len(combo):  # Check if all words are unique
            yield combo

def generate_combinations(input_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    if not validate_input(lines):
        print("Invalid input file format.")
        return
    
    patterns = lines[0].strip().split(',')
    three_letter_words = lines[1].strip().split(',')
    four_letter_words = lines[2].strip().split(',')
    
    word_dict = {
        '3': three_letter_words,
        '4': four_letter_words
    }
    
    output_file = os.path.splitext(input_file)[0] + "_output.txt"
    
    with open(output_file, 'w') as f:
        for pattern in patterns:
            unique_combinations = generate_unique_combinations(pattern, word_dict)
            for combo in unique_combinations:
                f.write(' '.join(combo) + '\n')
    
    print(f"Combinations have been written to {output_file}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 gencomb.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    
    generate_combinations(input_file)

if __name__ == "__main__":
    main()
