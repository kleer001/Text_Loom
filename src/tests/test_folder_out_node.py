import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType, NodeState
import shutil
import tempfile

def verify(actual, expected, name):
    if actual == expected:
        print(f"✅ {name} PASSED")
        print(f"Expected: {expected}")
        print(f"Got: {actual}")
    else:
        print(f"❌ {name} FAILED")
        print(f"Expected: {expected}")
        print(f"Got: {actual}")
        if isinstance(expected, list) and isinstance(actual, list):
            print(f"Length - Expected: {len(expected)}, Got: {len(actual)}")

def verify_file_exists(path, name):
    if os.path.exists(path):
        print(f"✅ {name} PASSED - File exists: {path}")
    else:
        print(f"❌ {name} FAILED - File does not exist: {path}")

def verify_file_content(path, expected_content, name):
    if os.path.exists(path):
        with open(path, 'r') as f:
            actual_content = f.read()
        if actual_content == expected_content:
            print(f"✅ {name} PASSED")
            print(f"Expected content: {expected_content}")
            print(f"Got content: {actual_content}")
        else:
            print(f"❌ {name} FAILED")
            print(f"Expected content: {expected_content}")
            print(f"Got content: {actual_content}")
    else:
        print(f"❌ {name} FAILED - File does not exist: {path}")

test_base_dir = tempfile.mkdtemp(prefix="folder_out_test_")

try:
    print("\n=== Test 1: Basic File Writing ===")

    text_node = Node.create_node(NodeType.TEXT, node_name="text1")
    folder_out_node = Node.create_node(NodeType.FOLDER_OUT, node_name="folder_out1")

    test_dir1 = os.path.join(test_base_dir, "test1")

    text_node._parms["text_string"].set('["First document", "Second document", "Third document"]')
    text_node._parms["pass_through"].set(False)

    folder_out_node.set_input(0, text_node)
    folder_out_node._parms["folder_path"].set(test_dir1)
    folder_out_node._parms["filename_pattern"].set("output_{count}.txt")
    folder_out_node._parms["overwrite"].set(True)

    output = folder_out_node.eval()

    verify(len(output), 3, "Three files created")
    verify_file_exists(os.path.join(test_dir1, "output_1.txt"), "First file exists")
    verify_file_exists(os.path.join(test_dir1, "output_2.txt"), "Second file exists")
    verify_file_exists(os.path.join(test_dir1, "output_3.txt"), "Third file exists")
    verify_file_content(os.path.join(test_dir1, "output_1.txt"), "First document", "First file content")
    verify_file_content(os.path.join(test_dir1, "output_2.txt"), "Second document", "Second file content")
    verify_file_content(os.path.join(test_dir1, "output_3.txt"), "Third document", "Third file content")


    print("\n=== Test 2: Filename Pattern with {index} ===")

    text_node2 = Node.create_node(NodeType.TEXT, node_name="text2")
    folder_out_node2 = Node.create_node(NodeType.FOLDER_OUT, node_name="folder_out2")

    test_dir2 = os.path.join(test_base_dir, "test2")

    text_node2._parms["text_string"].set('["Alpha", "Beta"]')
    text_node2._parms["pass_through"].set(False)

    folder_out_node2.set_input(0, text_node2)
    folder_out_node2._parms["folder_path"].set(test_dir2)
    folder_out_node2._parms["filename_pattern"].set("file_{index}.txt")
    folder_out_node2._parms["overwrite"].set(True)

    output2 = folder_out_node2.eval()

    verify_file_exists(os.path.join(test_dir2, "file_0.txt"), "Index 0 file exists")
    verify_file_exists(os.path.join(test_dir2, "file_1.txt"), "Index 1 file exists")


    print("\n=== Test 3: Filename Pattern with {input} ===")

    text_node3 = Node.create_node(NodeType.TEXT, node_name="text3")
    folder_out_node3 = Node.create_node(NodeType.FOLDER_OUT, node_name="folder_out3")

    test_dir3 = os.path.join(test_base_dir, "test3")

    text_node3._parms["text_string"].set('["MyDocument", "AnotherFile"]')
    text_node3._parms["pass_through"].set(False)

    folder_out_node3.set_input(0, text_node3)
    folder_out_node3._parms["folder_path"].set(test_dir3)
    folder_out_node3._parms["filename_pattern"].set("doc_{input}.txt")
    folder_out_node3._parms["overwrite"].set(True)

    output3 = folder_out_node3.eval()

    verify_file_exists(os.path.join(test_dir3, "doc_MyDocument.txt"), "Input-named file 1 exists")
    verify_file_exists(os.path.join(test_dir3, "doc_AnotherFile.txt"), "Input-named file 2 exists")


    print("\n=== Test 4: Filename Sanitization ===")

    text_node4 = Node.create_node(NodeType.TEXT, node_name="text4")
    folder_out_node4 = Node.create_node(NodeType.FOLDER_OUT, node_name="folder_out4")

    test_dir4 = os.path.join(test_base_dir, "test4")

    text_node4._parms["text_string"].set('["Invalid/Name*Test", "Another:File?Name"]')
    text_node4._parms["pass_through"].set(False)

    folder_out_node4.set_input(0, text_node4)
    folder_out_node4._parms["folder_path"].set(test_dir4)
    folder_out_node4._parms["filename_pattern"].set("{input}.txt")
    folder_out_node4._parms["overwrite"].set(True)

    output4 = folder_out_node4.eval()

    verify(len(output4), 2, "Two sanitized files created")
    print(f"Sanitized files: {[os.path.basename(f) for f in output4]}")


    print("\n=== Test 5: Overwrite False (Collision Handling) ===")

    text_node5 = Node.create_node(NodeType.TEXT, node_name="text5")
    folder_out_node5 = Node.create_node(NodeType.FOLDER_OUT, node_name="folder_out5")

    test_dir5 = os.path.join(test_base_dir, "test5")
    os.makedirs(test_dir5, exist_ok=True)

    with open(os.path.join(test_dir5, "output_1.txt"), 'w') as f:
        f.write("Existing file")

    text_node5._parms["text_string"].set('["New content"]')
    text_node5._parms["pass_through"].set(False)

    folder_out_node5.set_input(0, text_node5)
    folder_out_node5._parms["folder_path"].set(test_dir5)
    folder_out_node5._parms["filename_pattern"].set("output_{count}.txt")
    folder_out_node5._parms["overwrite"].set(False)

    output5 = folder_out_node5.eval()

    verify_file_content(os.path.join(test_dir5, "output_1.txt"), "Existing file", "Original file unchanged")
    verify_file_exists(os.path.join(test_dir5, "output_1_1.txt"), "Collision file created")
    verify_file_content(os.path.join(test_dir5, "output_1_1.txt"), "New content", "New file has correct content")


    print("\n=== Test 6: Hash-Based Write Optimization ===")

    text_node6 = Node.create_node(NodeType.TEXT, node_name="text6")
    folder_out_node6 = Node.create_node(NodeType.FOLDER_OUT, node_name="folder_out6")

    test_dir6 = os.path.join(test_base_dir, "test6")

    text_node6._parms["text_string"].set('["Content1", "Content2"]')
    text_node6._parms["pass_through"].set(False)

    folder_out_node6.set_input(0, text_node6)
    folder_out_node6._parms["folder_path"].set(test_dir6)
    folder_out_node6._parms["filename_pattern"].set("file_{count}.txt")
    folder_out_node6._parms["overwrite"].set(True)

    output6_first = folder_out_node6.eval()

    first_mtime = os.path.getmtime(os.path.join(test_dir6, "file_1.txt"))

    import time
    time.sleep(0.1)

    folder_out_node6.set_state(NodeState.UNCOOKED)
    output6_second = folder_out_node6.eval()

    second_mtime = os.path.getmtime(os.path.join(test_dir6, "file_1.txt"))

    verify(first_mtime == second_mtime, True, "File not rewritten when content unchanged")


    print("\n=== Test 7: Custom File Extension ===")

    text_node7 = Node.create_node(NodeType.TEXT, node_name="text7")
    folder_out_node7 = Node.create_node(NodeType.FOLDER_OUT, node_name="folder_out7")

    test_dir7 = os.path.join(test_base_dir, "test7")

    text_node7._parms["text_string"].set('["Markdown content"]')
    text_node7._parms["pass_through"].set(False)

    folder_out_node7.set_input(0, text_node7)
    folder_out_node7._parms["folder_path"].set(test_dir7)
    folder_out_node7._parms["filename_pattern"].set("readme_{count}")
    folder_out_node7._parms["file_extension"].set(".md")
    folder_out_node7._parms["overwrite"].set(True)

    output7 = folder_out_node7.eval()

    verify_file_exists(os.path.join(test_dir7, "readme_1.md"), "Markdown file exists")
    verify_file_content(os.path.join(test_dir7, "readme_1.md"), "Markdown content", "Markdown file content")


    print("\n=== Test 8: Empty List Input ===")

    text_node8 = Node.create_node(NodeType.TEXT, node_name="text8")
    folder_out_node8 = Node.create_node(NodeType.FOLDER_OUT, node_name="folder_out8")

    test_dir8 = os.path.join(test_base_dir, "test8")

    text_node8._parms["text_string"].set('[]')
    text_node8._parms["pass_through"].set(False)

    folder_out_node8.set_input(0, text_node8)
    folder_out_node8._parms["folder_path"].set(test_dir8)
    folder_out_node8._parms["overwrite"].set(True)

    output8 = folder_out_node8.eval()

    verify(len(output8), 1, "Empty list creates one file with empty string")


    print("\n=== Test 9: Disabled Node ===")

    text_node9 = Node.create_node(NodeType.TEXT, node_name="text9")
    folder_out_node9 = Node.create_node(NodeType.FOLDER_OUT, node_name="folder_out9")

    test_dir9 = os.path.join(test_base_dir, "test9")

    text_node9._parms["text_string"].set('["Test content"]')
    text_node9._parms["pass_through"].set(False)

    folder_out_node9.set_input(0, text_node9)
    folder_out_node9._parms["folder_path"].set(test_dir9)
    folder_out_node9._parms["enabled"].set(False)

    output9 = folder_out_node9.eval()

    verify(output9, ["Test content"], "Disabled node passes through input")
    verify(os.path.exists(test_dir9), False, "Disabled node doesn't create directory")


    print("\n=== Test Complete ===")

finally:
    shutil.rmtree(test_base_dir)
    print(f"\nCleaned up test directory: {test_base_dir}")
