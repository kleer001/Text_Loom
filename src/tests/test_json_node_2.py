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

print("\n=== Test 2: JSON in a Looper - Multiple Documents ===")

# Create multiple JSON product documents
products_json = [
    '{"product": {"name": "Laptop", "price": 999, "category": "Electronics"}}',
    '{"product": {"name": "Coffee Mug", "price": 12, "category": "Kitchen"}}',
    '{"product": {"name": "Notebook", "price": 5, "category": "Office"}}',
    '{"product": {"name": "Headphones", "price": 79, "category": "Electronics"}}'
]

# Set up node network: Text (with list) -> Looper -> JSON -> Text (format) -> Output
text_products = Node.create_node(NodeType.TEXT, node_name="text_products")
looper = Node.create_node(NodeType.LOOPER, node_name="looper")
json_node = Node.create_node(NodeType.JSON, node_name="json_extract", parent_path="/looper")
text_format = Node.create_node(NodeType.TEXT, node_name="text_format", parent_path="/looper")
split_node = Node.create_node(NodeType.SPLIT, node_name="split_current", parent_path="/looper")

# Set up text node with all products as a list
text_products._parms["text_string"].set(str(products_json))
text_products._parms["pass_through"].set(False)

# Connect text to looper
looper.set_input(0, text_products)
looper._parms["max_from_input"].set(True)

# Inside looper: split to get current iteration's JSON
split_node.set_input(0, looper._input_node)
split_node._parms["split_expr"].set("[$$L]")

# Inside looper: extract product name from each JSON
json_node.set_input(0, split_node, output_index=0)
json_node._parms["json_path"].set("product.name")
json_node._parms["extraction_mode"].set("array")

# Inside looper: format the output
text_format.set_input(0, json_node)
text_format._parms["text_string"].set("Product: ")
text_format._parms["prefix"].set(True)

# Connect to looper output
looper._output_node.set_input(0, text_format)

# Evaluate
output = looper.eval()

print(f"\nLooper output: {output}")

verify(len(output), 4, "Processed all 4 products")
verify(all("Product:" in item for item in output), True, "All items have prefix")
verify(any("Laptop" in item for item in output), True, "Contains Laptop")
verify(any("Coffee Mug" in item for item in output), True, "Contains Coffee Mug")
verify(any("Notebook" in item for item in output), True, "Contains Notebook")
verify(any("Headphones" in item for item in output), True, "Contains Headphones")

print("\n=== Test 5: Complex Nested Navigation - E-commerce Orders ===")

# Create complex nested JSON (e-commerce orders)
orders_json = '''{
  "orders": [
    {
      "order_id": "ORD001",
      "customer": "Alice",
      "items": [
        {"product": {"name": "Laptop", "sku": "LAP001"}, "quantity": 1},
        {"product": {"name": "Mouse", "sku": "MOU001"}, "quantity": 2}
      ]
    },
    {
      "order_id": "ORD002",
      "customer": "Bob",
      "items": [
        {"product": {"name": "Keyboard", "sku": "KEY001"}, "quantity": 1},
        {"product": {"name": "Monitor", "sku": "MON001"}, "quantity": 1},
        {"product": {"name": "Cable", "sku": "CAB001"}, "quantity": 3}
      ]
    },
    {
      "order_id": "ORD003",
      "customer": "Charlie",
      "items": [
        {"product": {"name": "Headphones", "sku": "HDP001"}, "quantity": 1}
      ]
    }
  ]
}'''

text_orders = Node.create_node(NodeType.TEXT, node_name="text_orders")
json_orders = Node.create_node(NodeType.JSON, node_name="json_orders")

text_orders._parms["text_string"].set(orders_json)
text_orders._parms["pass_through"].set(False)

json_orders.set_input(0, text_orders)

# Test 5a: Extract all product names using deep wildcard path
print("\n--- Test 5a: Deep wildcard path for product names ---")
json_orders._parms["json_path"].set("orders[*].items[*].product.name")
json_orders._parms["extraction_mode"].set("array")

output = json_orders.eval()
print(f"Extracted product names: {output}")

verify(len(output), 6, "Extracted all 6 products from all orders")
verify("Laptop" in output, True, "Contains Laptop")
verify("Mouse" in output, True, "Contains Mouse")
verify("Keyboard" in output, True, "Contains Keyboard")
verify("Monitor" in output, True, "Contains Monitor")
verify("Cable" in output, True, "Contains Cable")
verify("Headphones" in output, True, "Contains Headphones")

# Test 5b: Extract all SKUs using deep wildcard path
print("\n--- Test 5b: Deep wildcard path for SKUs ---")
json_orders._parms["json_path"].set("orders[*].items[*].product.sku")
json_orders.set_state(NodeState.UNCOOKED)

output = json_orders.eval()
print(f"Extracted SKUs: {output}")

verify(len(output), 6, "Extracted all 6 SKUs")
verify("LAP001" in output, True, "Contains LAP001")
verify("CAB001" in output, True, "Contains CAB001")

# Test 5c: Extract customer names (single level wildcard)
print("\n--- Test 5c: Single level wildcard for customers ---")
json_orders._parms["json_path"].set("orders[*].customer")
json_orders.set_state(NodeState.UNCOOKED)

output = json_orders.eval()
print(f"Extracted customers: {output}")

verify(output, ["Alice", "Bob", "Charlie"], "Extracted all customers in order")

# Test 5d: Extract quantities using deep wildcard
print("\n--- Test 5d: Deep wildcard for quantities ---")
json_orders._parms["json_path"].set("orders[*].items[*].quantity")
json_orders.set_state(NodeState.UNCOOKED)

output = json_orders.eval()
print(f"Extracted quantities: {output}")

# Quantities should be: [1, 2, 1, 1, 3, 1] as strings
verify(output, ["1", "2", "1", "1", "3", "1"], "Extracted all quantities (stringified)")

print("\n=== Tests Complete ===")