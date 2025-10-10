import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.base_classes import Node, NodeType, NodeState

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

print("\n=== Test 3: Extract → Merge → Format ===")

# Create JSON with user data
users_json = '''{
  "users": [
    {"name": "Alice Smith", "email": "alice@example.com", "role": "Admin", "active": true},
    {"name": "Bob Jones", "email": "bob@example.com", "role": "User", "active": true},
    {"name": "Charlie Brown", "email": "charlie@example.com", "role": "Guest", "active": false}
  ]
}'''

# Set up node network:
# Text -> [JSON1 (names), JSON2 (emails), JSON3 (roles)] -> Merge -> Text (format)
text_input = Node.create_node(NodeType.TEXT, node_name="text_users")
json_names = Node.create_node(NodeType.JSON, node_name="json_names")
json_emails = Node.create_node(NodeType.JSON, node_name="json_emails")
json_roles = Node.create_node(NodeType.JSON, node_name="json_roles")
merge_node = Node.create_node(NodeType.MERGE, node_name="merge_data")
text_format = Node.create_node(NodeType.TEXT, node_name="text_format")

# Set up text input
text_input._parms["text_string"].set(users_json)
text_input._parms["pass_through"].set(False)

# Extract names
json_names.set_input(0, text_input)
json_names._parms["json_path"].set("users[*].name")

# Extract emails
json_emails.set_input(0, text_input)
json_emails._parms["json_path"].set("users[*].email")

# Extract roles
json_roles.set_input(0, text_input)
json_roles._parms["json_path"].set("users[*].role")

# Merge all three extractions
merge_node.set_input(0, json_names)
merge_node.set_input(1, json_emails)
merge_node.set_input(2, json_roles)
merge_node._parms["single_string"].set(False)

# Format the merged output
text_format.set_input(0, merge_node)
text_format._parms["text_string"].set("User: ")
text_format._parms["prefix"].set(True)
text_format._parms["per_item"].set(True)

# Evaluate
output = text_format.eval()
print(f"\nFormatted output: {output}")

# Verify we have all data merged
verify(len(output), 9, "Merged all extractions (3 names + 3 emails + 3 roles)")

# Verify names present
verify(any("Alice Smith" in item for item in output), True, "Contains Alice Smith")
verify(any("Bob Jones" in item for item in output), True, "Contains Bob Jones")

# Verify emails present
verify(any("alice@example.com" in item for item in output), True, "Contains alice@example.com")
verify(any("bob@example.com" in item for item in output), True, "Contains bob@example.com")

# Verify roles present
verify(any("Admin" in item for item in output), True, "Contains Admin role")
verify(any("Guest" in item for item in output), True, "Contains Guest role")

# Verify prefix added to all
verify(all("User:" in item for item in output), True, "All items have 'User:' prefix")

print("\n=== Test 4: JSON → Split → Process ===")

# Create JSON with a list of tasks
tasks_json = '''{
  "tasks": [
    {"id": 1, "title": "Design homepage", "priority": "high"},
    {"id": 2, "title": "Write documentation", "priority": "medium"},
    {"id": 3, "title": "Fix bug #123", "priority": "high"},
    {"id": 4, "title": "Update dependencies", "priority": "low"},
    {"id": 5, "title": "Code review", "priority": "medium"},
    {"id": 6, "title": "Deploy to staging", "priority": "high"}
  ]
}'''

# Set up node network:
# Text -> JSON (extract titles) -> Split (first 3 vs rest) -> [Text1 (urgent), Text2 (normal)]
text_tasks = Node.create_node(NodeType.TEXT, node_name="text_tasks")
json_tasks = Node.create_node(NodeType.JSON, node_name="json_tasks")
split_tasks = Node.create_node(NodeType.SPLIT, node_name="split_tasks")
text_urgent = Node.create_node(NodeType.TEXT, node_name="text_urgent")
text_normal = Node.create_node(NodeType.TEXT, node_name="text_normal")

# Set up text input
text_tasks._parms["text_string"].set(tasks_json)
text_tasks._parms["pass_through"].set(False)

# Extract all task titles
json_tasks.set_input(0, text_tasks)
json_tasks._parms["json_path"].set("tasks[*].title")

# Split: first 3 items (urgent) vs remainder (normal priority)
split_tasks.set_input(0, json_tasks)
split_tasks._parms["split_expr"].set("[0:3]")

# Format urgent tasks (from main output)
text_urgent.set_input(0, split_tasks, output_index=0)
text_urgent._parms["text_string"].set("[URGENT] ")
text_urgent._parms["prefix"].set(True)
text_urgent._parms["per_item"].set(True)

# Format normal tasks (from remainder output)
text_normal.set_input(0, split_tasks, output_index=1)
text_normal._parms["text_string"].set("[NORMAL] ")
text_normal._parms["prefix"].set(True)
text_normal._parms["per_item"].set(True)

# Evaluate urgent tasks
urgent_output = text_urgent.eval()
print(f"\nUrgent tasks: {urgent_output}")

verify(len(urgent_output), 3, "Split first 3 tasks as urgent")
verify(all("[URGENT]" in item for item in urgent_output), True, "All urgent tasks have [URGENT] prefix")
verify(any("Design homepage" in item for item in urgent_output), True, "Contains first task")
verify(any("Write documentation" in item for item in urgent_output), True, "Contains second task")

# Evaluate normal tasks
normal_output = text_normal.eval()
print(f"\nNormal tasks: {normal_output}")

verify(len(normal_output), 3, "Split remaining 3 tasks as normal")
verify(all("[NORMAL]" in item for item in normal_output), True, "All normal tasks have [NORMAL] prefix")
verify(any("Update dependencies" in item for item in normal_output), True, "Contains fourth task")
verify(any("Deploy to staging" in item for item in normal_output), True, "Contains last task")

print("\n--- Test 4b: Extract with JSON format, then split ---")

# Extract entire task objects as JSON strings
json_tasks._parms["json_path"].set("tasks")
json_tasks._parms["extraction_mode"].set("array")
json_tasks._parms["format_output"].set("json")
json_tasks.set_state(NodeState.UNCOOKED)

# Split into first 2 vs rest
split_tasks._parms["split_expr"].set("[0:2]")
split_tasks.set_state(NodeState.UNCOOKED)

# Get the splits
text_urgent.set_state(NodeState.UNCOOKED)
text_normal.set_state(NodeState.UNCOOKED)

urgent_json = text_urgent.eval()
normal_json = text_normal.eval()

print(f"\nFirst 2 tasks (JSON format): {urgent_json}")
print(f"\nRemaining tasks (JSON format): {normal_json}")

verify(len(urgent_json), 2, "Split first 2 tasks")
verify(len(normal_json), 4, "Split remaining 4 tasks")

# Verify JSON format preserved
verify(all("{" in item and "}" in item for item in urgent_json), True, "Urgent tasks in JSON format")
verify(all("{" in item and "}" in item for item in normal_json), True, "Normal tasks in JSON format")

print("\n=== Tests Complete ===")