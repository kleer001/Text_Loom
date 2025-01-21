#doesn't work yet

import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType
from core.print_node_info import print_node_info

# First create our sample input file
sample_qa = """Q: What is the capital of France?
A: Paris is the capital of France.
Q: How many continents are there?
A: There are seven continents on Earth.
Q: What is the chemical symbol for gold?
A: Au is the chemical symbol for gold."""

input_file = "sample_qa.txt"
with open(input_file, "w") as f:
    f.write(sample_qa)

def setup_nodes():
    print("\n=== Setting up nodes ===")
    
    # Create all nodes
    file_in = Node.create_node(NodeType.FILE_IN, node_name="file_in")
    section = Node.create_node(NodeType.SECTION, node_name="section")
    looper = Node.create_node(NodeType.LOOPER, node_name="looper")
    
    # Create nodes inside the looper
    text_combine = Node.create_node(NodeType.TEXT, node_name="text_combine", parent_path="/looper")
    query = Node.create_node(NodeType.QUERY, node_name="query", parent_path="/looper")
    text_analysis = Node.create_node(NodeType.TEXT, node_name="text_analysis", parent_path="/looper")
    split = Node.create_node(NodeType.SPLIT, node_name="split", parent_path="/looper")
    
    # Create output node
    file_out = Node.create_node(NodeType.FILE_OUT, node_name="file_out")
    
    # Configure FileInNode
    file_in._parms["file_name"].set(input_file)
    
    # Configure SectionNode to properly split Q&A
    section._parms["prefix1"].set("Q")
    section._parms["prefix2"].set("A")
    section._parms["delimiter"].set(":")
    section._parms["trim_prefix"].set(True)
    section.set_input(0, file_in)
    
    # Configure TextNode to combine Q&A pairs with proper formatting
    text_combine._parms["text_string"].set("")
    text_combine._parms["pass_through"].set(True)
    text_combine._parms["per_item"].set(True)
    
    # Set up loop input handling
    merge = Node.create_node(NodeType.MERGE, node_name="merge", parent_path="/looper")
    merge.set_input(0, section, 0)  # Questions
    merge.set_input(1, section, 1)  # Answers
    
    # Properly connect nodes to looper's internal structure
    looper.connect_loop_in(merge)  # Connect merge to looper's input
    text_combine.set_input(0, merge)
    
    # Configure QueryNode
    query.set_input(0, text_combine)
    
    # Configure TextNode to format with Analysis
    text_analysis._parms["text_string"].set("\nAnalysis: ")
    text_analysis._parms["prefix"].set(False)
    text_analysis.set_input(0, query)
    
    # Configure SplitNode
    split._parms["split_expr"].set("[0:2]")
    split.set_input(0, text_analysis)
    
    # Connect to looper's output structure
    looper.connect_loop_out(split)
    
    # Configure FileOutNode
    file_out._parms["filename"].set("qa_analysis_output.txt")
    file_out.set_input(0, looper)
    
    return file_out, looper, split

def run_test():
    print("\n=== Running mega-test ===")
    file_out, looper, split = setup_nodes()
    
    print("\nInitial evaluation:")
    result = file_out.eval()
    print(f"Final Result length: {len(result)}")
    print(f"Final Result: {result}")
    
    print("\nSplit node outputs:")
    print_split_outputs(split)
    
    print("\nCook counts:")
    print(f"Split node: {split._cook_count}")
    print(f"Looper output node: {looper._output_node._cook_count}")
    
    return result

def print_split_outputs(split_node):
    print("\n=== Split Node Current Output State ===")
    full_output = split_node._output
    if isinstance(full_output, list) and len(full_output) >= 2:
        print("MAIN Output (index 0):", full_output[0])
        print("REMAINDER Output (index 1):", full_output[1])
    else:
        print("Unexpected split output format:", full_output)
    print("=====================================")

if __name__ == "__main__":
    print("\n=== Mega Test - All Node Types ===")
    results = run_test()
    
    print("\nChecking output file:")
    try:
        with open("qa_analysis_output.txt", "r") as f:
            print(f.read())
    except Exception as e:
        print(f"Error reading output file: {e}")
    
    # Cleanup
    try:
        os.remove(input_file)
        os.remove("qa_analysis_output.txt")
    except:
        pass
    