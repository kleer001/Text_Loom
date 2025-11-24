import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from repl.helpers import (
    create, ls, types, connect_next, run, parm, inspect, tree,
    find, disconnect, set_global, get_global, destroy
)

print("=== Testing all helper functions ===")

print("\n1. Creating nodes...")
text1 = create('text', 'hello', text_string="Hello")
text2 = create('text', 'world', text_string="World")
merge = create('merge', 'combiner')
print(f"   Created: {text1.name()}, {text2.name()}, {merge.name()}")

print("\n2. Listing nodes...")
all_nodes = ls()
print(f"   Total nodes: {len(all_nodes)}")

print("\n3. Testing types...")
available_types = types()
print(f"   Available types: {len(available_types)}")

print("\n4. Connecting nodes...")
connect_next(text1, merge)
connect_next(text2, merge)
print(f"   Merge inputs: {len(merge.inputs())}")

print("\n5. Running workflow...")
result = run(merge)
print(f"   Result: {result}")

print("\n6. Testing parm...")
parm(text1, 'text_string', 'Modified')
new_val = parm(text1, 'text_string')
print(f"   New param value: {new_val}")

print("\n7. Inspecting node...")
info = inspect(merge)
print(f"   Merge type: {info['type']}, inputs: {info['inputs']}")

print("\n8. Testing tree...")
tree()

print("\n9. Testing find...")
found = find('/hello')
print(f"   Found node: {found.name()}")

print("\n10. Testing disconnect...")
disconnect(merge, 0)
print(f"   Merge inputs after disconnect: {len(merge.inputs())}")

print("\n11. Testing globals...")
set_global('TEST_KEY', 'test_value')
val = get_global('TEST_KEY')
print(f"   Global value: {val}")

print("\n12. Testing destroy...")
destroy(text2)
print(f"   Nodes after destroy: {ls()}")

print("\n=== All tests passed! ===")
