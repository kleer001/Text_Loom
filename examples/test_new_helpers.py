print("=== Testing new helper functions ===")

text = create('text', 'test_node', text_string="Hello")
merge = create('merge', 'merger')
connect(text, merge)

print("\n1. Testing node_type...")
t = node_type(text)
print(f"   Type: {t}")
assert t == 'TEXT'

print("\n2. Testing input/output names...")
inp_names = input_names(merge)
out_names = output_names(merge)
print(f"   Input names: {inp_names}")
print(f"   Output names: {out_names}")

print("\n3. Testing cook metrics...")
run(merge)
count = cook_count(merge)
time_ms = last_cook_time(merge)
print(f"   Cook count: {count}")
print(f"   Last cook time: {time_ms}ms")

print("\n4. Testing needs_to_cook...")
dirty = needs_to_cook(merge)
print(f"   Needs cook: {dirty}")
parm(text, 'text_string', 'Modified')
dirty_after = needs_to_cook(merge)
print(f"   After change: {dirty_after}")

print("\n5. Testing cook_dependencies...")
deps = cook_dependencies(merge)
print(f"   Dependencies: {[d.name() for d in deps]}")

print("\n6. Testing input_nodes...")
inp_nodes = input_nodes(merge)
print(f"   Input nodes: {[n.name() for n in inp_nodes]}")

print("\n7. Testing errors/warnings...")
initial_errors = errors(merge)
initial_warnings = warnings(merge)
print(f"   Errors: {initial_errors}")
print(f"   Warnings: {initial_warnings}")

print("\n8. Testing time dependency...")
is_td = is_time_dependent(text)
print(f"   Time dependent: {is_td}")

print("\n9. Testing node_exists...")
exists = node_exists('/test_node')
not_exists = node_exists('/fake_node')
print(f"   /test_node exists: {exists}")
print(f"   /fake_node exists: {not_exists}")

print("\n10. Testing inputs_with_indices...")
inputs_idx = inputs_with_indices(merge, use_names=True)
print(f"   Inputs with indices: {inputs_idx}")

print("\n11. Testing outputs_with_indices...")
outputs_idx = outputs_with_indices(text, use_names=True)
print(f"   Outputs with indices: {outputs_idx}")

print("\n12. Testing children...")
child_list = children(text)
print(f"   Children: {child_list}")

print("\n=== All new functions work! ===")
