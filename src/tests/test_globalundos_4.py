import sys, os
import warnings
from typing import List, Any

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from core.global_store import GlobalStore
from core.undo_manager import UndoManager

def print_state():
    print(f"Globals: {GlobalStore.list()}")
    print(f"Undo text: {UndoManager().get_undo_text()}")
    print(f"Redo text: {UndoManager().get_redo_text()}")
    print(f"Redo stack length: {len(UndoManager().redo_stack)}\n")

def test_basic_operations():
    print("\n=== Testing Basic Operations ===")
    print("Initial state:")
    print_state()

    print("Setting AB = 6")
    GlobalStore.set("AB", 6)
    print_state()

    print("Setting FOO = 'apples'")
    GlobalStore.set("FOO", "apples")
    print_state()

    print("Setting BAR = 42")
    GlobalStore.set("BAR", 42)
    print_state()

def test_undo_redo():
    print("\n=== Testing Undo/Redo Operations ===")
    
    print("Performing first undo:")
    UndoManager().undo()
    print_state()

    print("Performing second undo:")
    UndoManager().undo()
    print_state()

    print("Performing first redo:")
    UndoManager().redo()
    print_state()

    print("Performing second redo:")
    UndoManager().redo()
    print_state()

def test_cut_operations():
    print("\n=== Testing Cut Operations ===")
    
    print("Cutting FOO")
    GlobalStore.cut("FOO")
    print_state()
    
    print("Undoing cut:")
    UndoManager().undo()
    print_state()
    
    print("Redoing cut:")
    UndoManager().redo()
    print_state()

def test_flush_operations():
    print("\n=== Testing Flush Operations ===")
    
    print("Adding multiple values:")
    GlobalStore.set("TEST1", 100)
    GlobalStore.set("TEST2", 200)
    print_state()
    
    print("Flushing all globals:")
    GlobalStore.flush_all_globals()
    print_state()
    
    print("Undoing flush:")
    UndoManager().undo()
    print_state()

def test_validation():
    print("\n=== Testing Validation Rules ===")
    
    invalid_keys = [
        "ab",           # lowercase
        "$ABC",        # starts with $
        "A",           # too short
        "ABC123",      # contains numbers
        "ABC_DEF"      # contains underscore
    ]
    
    for key in invalid_keys:
        try:
            print(f"\nTrying invalid key: {key}")
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                GlobalStore.set(key, "test")
        except ValueError as e:
            print(f"Caught expected error: {str(e)}")
            if w:
                print(f"Warning message: {str(w[-1].message)}")

def test_update_existing():
    print("\n=== Testing Update Operations ===")
    
    print("Setting initial value:")
    GlobalStore.set("TEST", 100)
    print_state()
    
    print("Updating existing value:")
    GlobalStore.set("TEST", 200)
    print_state()
    
    print("Undoing update:")
    UndoManager().undo()
    print_state()

def run_all_tests():
    GlobalStore.flush_all_globals()
    UndoManager().undo_stack.clear()
    UndoManager().redo_stack.clear()
    
    print("Starting comprehensive global store tests...")
    
    test_basic_operations()
    test_undo_redo()
    test_cut_operations()
    test_flush_operations()
    test_validation()
    test_update_existing()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    run_all_tests()