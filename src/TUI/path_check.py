import sys, os
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(src_dir)

print(f"Current directory: {current_dir}")
print(f"Src directory: {src_dir}")
print(f"Python path: {sys.path}")

print(f"Contents of {src_dir}:")
for item in os.listdir(src_dir):
    print(f"  {item}")

print("\nTrying to import modules individually:")

modules_to_import = [
    'backend.base_classes',
    'backend.flowstate_manager',
    'backend.undo_manager'
]

for module in modules_to_import:
    try:
        __import__(module)
        print(f"Successfully imported {module}")
    except ImportError as e:
        print(f"Error importing {module}: {e}")

print(f"\nCurrent working directory: {os.getcwd()}")
