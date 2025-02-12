## FileInNode
- file_name: "./input.txt" (STRING)
- file_text: "" (STRING)
- refresh: (BUTTON)

## FileOutNode
- file_name: "./output.txt" (STRING)
- file_text: "" (STRING)
- refresh: (BUTTON)
- format_output: True (TOGGLE)

## InputNullNode
- in_node: "" (STRING)
- in_data: [] (STRINGLIST)
- feedback_mode: False (TOGGLE)

## LooperNode
- min: 1 (INT)
- max: 3 (INT)
- step: 1 (INT)
- max_from_input: False (TOGGLE)
- feedback_mode: False (TOGGLE)
- use_test: False (TOGGLE)
- cook_loops: False (TOGGLE)
- test_number: 1 (INT)
- input_hook: "" (STRING)
- output_hook: "" (STRING)
- staging_data: [] (STRINGLIST)
- timeout_limit: 300.0 (FLOAT)
- data_limit: 209715200 (INT)

## MakeListNode
- limit: False (TOGGLE)
- max_list: 5 (INT)
- refresh: (BUTTON)

## MergeNode
- single_string: True (TOGGLE)
- use_insert: False (TOGGLE)
- insert_string: "##N" (STRING)

## NullNode
[No parameters]

## OutputNullNode
- out_data: [] (STRINGLIST)
- feedback_mode: False (TOGGLE)
- cook_loops: False (TOGGLE)
- in_node: "" (STRING)

## QueryNode  
- limit: True (TOGGLE)
- response: [] (STRINGLIST)
- llm_name: "Ollama" (STRING)
- find_llm: (BUTTON)
- respond: (BUTTON)

## SectionNode
- enabled: True (TOGGLE)
- prefix1: "Interviewer" (STRING)
- prefix2: "Participant" (STRING)
- trim_prefix: True (TOGGLE)
- regex_file: "regex.dat.json" (STRING)

## SplitNode
- enabled: True (TOGGLE)
- split_expr: "" (STRING)

## TextNode
- text_string: "" (STRING)
- pass_through: True (TOGGLE)
- per_item: True (TOGGLE)
- prefix: False (TOGGLE)