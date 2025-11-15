print("Creating text nodes (naming them 'greeting' and 'subject')...")
text1 = create('text', 'greeting', text_string="Hello")
text2 = create('text', 'subject', text_string="World")

print("Creating merge node...")
merge = create('merge', 'combine')

print("Connecting nodes...")
connect(text1, merge, target_input=0)
connect(text2, merge, target_input=1)

print("Running workflow...")
result = run(merge)
print(f"Output: {result}")

print("\nNode hierarchy:")
tree()

print("\nInspecting merge node:")
info = inspect(merge)
print(f"  Name: {info['name']}")
print(f"  Type: {info['type']}")
print(f"  Inputs: {info['inputs']}")
print(f"  Connections: {info['connections']}")

print("\nExample complete!")
