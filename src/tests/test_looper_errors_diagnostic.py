#!/usr/bin/env python3
"""
Quick diagnostic test to check for errors after looper cooking.
"""
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import NodeEnvironment, Node, NodeType

# Clear environment
NodeEnvironment.nodes.clear()

# Create simple looper
looper = Node.create_node(NodeType.LOOPER, node_name="looper1")
text1 = Node.create_node(NodeType.TEXT, node_name="text1", parent_path="/looper1")

# Setup
text1._parms["text_string"].set("Item $$N")
looper._output_node.set_input(0, text1)
looper._parms["min"].set(1)
looper._parms["max"].set(3)
looper._parms["step"].set(1)

# Cook
print("Cooking looper...")
looper.cook()
result = looper.eval()

print(f"\nResult: {result}")
print(f"Looper state: {looper._state}")
print(f"Looper errors: {looper._errors}")
print(f"Looper warnings: {looper._warnings}")

print(f"\nInputNullNode errors: {looper._input_node._errors}")
print(f"InputNullNode warnings: {looper._input_node._warnings}")

print(f"\nOutputNullNode errors: {looper._output_node._errors}")
print(f"OutputNullNode warnings: {looper._output_node._warnings}")

print(f"\ntext1 errors: {text1._errors}")
print(f"text1 warnings: {text1._warnings}")

# Check determine_execution_success logic
success = (looper._state.value in ['unchanged', 'cooked'] and len(looper._errors) == 0)
print(f"\nWould execute_node report success? {success}")
print(f"  - State check: {looper._state.value in ['unchanged', 'cooked']} (state={looper._state.value})")
print(f"  - Errors check: {len(looper._errors) == 0} (errors={len(looper._errors)})")
