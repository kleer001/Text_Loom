import configparser
import math
import os
from datetime import datetime

import gradio as gr

from word_utils import extract_key_words

# The only setting we need on creation
config = configparser.ConfigParser()
config.read('settings.cfg')
maxvalue = config['DEFAULT']['max_items']
MAX_ITEMS = int(maxvalue)


def generate_filename(zeroth_cue, first_cue):
    key_words = extract_key_words(zeroth_cue)

    # If we don't have enough key words, fall back to using words from the first cue
    if len(key_words) < 4:
        first_cue_words = extract_key_words(first_cue, num_words=4 - len(key_words))
        key_words.extend(first_cue_words)

    base_filename = ''.join(word.capitalize() for word in key_words[:4])
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_filename}{date_str}.txt"


def save_results(zeroth_cue, first_cue, second_cue, *components):
    # Create the 'saved_cues' directory if it doesn't exist
    save_dir = os.path.join(os.getcwd(), 'saved_cues')
    os.makedirs(save_dir, exist_ok=True)

    filename = generate_filename(zeroth_cue, first_cue)

    counter = 1
    while os.path.exists(os.path.join(save_dir, filename)):
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{counter}{ext}"
        counter += 1

    full_path = os.path.join(save_dir, filename)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(f"0th Cue: {zeroth_cue}\n")
        f.write(f"1st Cue: {first_cue}\n")
        f.write(f"2nd Cue: {second_cue}\n\n")

        for i in range(0, len(components), 2):
            item = components[i]
            result = components[i + 1] if i + 1 < len(components) else None

            if item:  # If item has a value, save it
                f.write(f"Item: {item}\n")
                if result:  # If result has a value, save it
                    f.write("******\n")
                    f.write(f"Result:\n{result}\n")  # Write 'Result:' on its own line
                f.write("\n")  # Extra newline for separation

    return full_path


def open_file(file_path):
    if not os.path.exists(file_path):
        return "", "", "", []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    zeroth_cue = ""
    first_cue = ""
    second_cue = ""
    items_and_results = []
    current_item = ""
    current_result = ""
    reading_result = False
    item_section_started = False

    for line in lines:
        line = line.strip()
        if line.startswith("0th Cue: "):
            zeroth_cue = line.split(': ', 1)[1]
        elif line.startswith("1st Cue: "):
            first_cue = line.split(': ', 1)[1]
        elif line.startswith("2nd Cue: "):
            second_cue = line.split(': ', 1)[1]
        elif line.startswith("Item: "):
            item_section_started = True
            if current_item:
                items_and_results.append((current_item, current_result.strip()))
                current_result = ""
            current_item = line.split(': ', 1)[1]
            reading_result = False
        elif item_section_started:
            if line.startswith("******"):
                reading_result = True
            elif reading_result:
                if line.startswith("Result:"):
                    continue
                current_result += line + "\n"

    if current_item:
        items_and_results.append((current_item, current_result.strip()))

    return zeroth_cue, first_cue, second_cue, items_and_results


def create_library_ui():
    with gr.Tab("Files"):
        gr.Markdown("# File Management")

        with gr.Row():
            with gr.Column():
                save_btn = gr.Button("Save Results")
                save_output = gr.File(label="Saved File")

            with gr.Column():
                open_input = gr.File(label="File to Open")
                open_btn = gr.Button("Open File", interactive=False)

        library_status_message = gr.Textbox(label="File Status", interactive=False)

        # Enable the Open File button only when a file is selected
        open_input.change(
            lambda x: gr.update(interactive=x is not None),
            inputs=[open_input],
            outputs=[open_btn]
        )

    return save_btn, save_output, open_input, open_btn, library_status_message


def save_results_wrapper(zeroth_cue, first_cue, second_cue, *components):
    full_path = save_results(zeroth_cue, first_cue, second_cue, *components)
    return gr.update(value=full_path, visible=True), f"File saved as {os.path.basename(full_path)}"


def calculate_lines(text, width=60):
    lines = text.split('\n')
    total_lines = sum(math.ceil(len(line) / width) for line in lines)
    return max(1, total_lines)


def open_file_wrapper(file_obj):
    if file_obj is None:
        return [gr.update()] * (3 + MAX_ITEMS * 4) + [
            gr.update(value="Please select a file before clicking 'Open File'")]

    file_path = file_obj.name
    zeroth_cue, first_cue, second_cue, items_and_results = open_file(file_path)

    outputs = [
        gr.update(value=zeroth_cue, visible=True, lines=calculate_lines(zeroth_cue)),
        gr.update(value=first_cue, visible=True, lines=calculate_lines(first_cue)),
        gr.update(value=second_cue, visible=True, lines=calculate_lines(second_cue))
    ]

    for i in range(MAX_ITEMS):
        if i < len(items_and_results):
            item_text, result_text = items_and_results[i]
            has_content = bool(item_text.strip() or result_text.strip())
            outputs.extend([
                gr.update(visible=has_content),  # Row
                gr.update(value=item_text, visible=True, lines=calculate_lines(item_text)),  # Item
                gr.update(visible=True),  # Button
                gr.update(value=result_text, visible=True, lines=calculate_lines(result_text))  # Result
            ])
        else:
            outputs.extend([
                gr.update(visible=False),  # Row
                gr.update(value="", visible=False),  # Item
                gr.update(visible=False),  # Button
                gr.update(value="", visible=False)  # Result
            ])

    status_message = gr.update(value=f"File opened: {os.path.basename(file_path)}")
    outputs.append(status_message)

    return outputs

    print(f"Number of outputs: {len(outputs)}")
    return outputs + [status_message]
