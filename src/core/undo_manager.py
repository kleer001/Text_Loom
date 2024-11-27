import sys
import json
from contextlib import contextmanager
from typing import Optional, List, Tuple, Callable, Any, Union

class UndoGroup:
    def __init__(self, description: str):
        self.description = description
        self.actions: List[Tuple[Callable, tuple, str]] = []

    def add_action(self, action: Callable, args: tuple, description: str):
        self.actions.append((action, args, description))

    def execute_undo(self):
        for action, args, _ in reversed(self.actions):
            action(*args)

    def execute_redo(self):
        for action, args, _ in self.actions:
            action(*args)



class UndoManager:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UndoManager, cls).__new__(cls)
            cls._instance.undo_stack = []
            cls._instance.redo_stack = []
            cls._instance._enabled = True
            cls._instance._memory_limit = 1024 * 1024 * 10
            cls._instance._current_group: Optional[UndoGroup] = None
        return cls._instance

    def add_action(self, action, args, description, redo_action=None, redo_args=None):
        if not self._enabled:
            return

        if self._current_group is not None:
            self._current_group.add_action(action, args, description)
        else:
            self.undo_stack.append((action, args, description, redo_action, redo_args))
            self.redo_stack.clear()
            self._check_memory_usage()

    def undo(self):
        if not self._enabled or not self.undo_stack:
            return False
            
        action, args, description, redo_action, redo_args = self.undo_stack.pop()
        action(*args)
        self.redo_stack.append((action, args, description, redo_action, redo_args))
        return True

    def redo(self):
        if not self._enabled or not self.redo_stack:
            return False
        undo_action, undo_args, description, redo_action, redo_args = self.redo_stack.pop()
        redo_action(*redo_args)
        self.undo_stack.append((undo_action, undo_args, description, redo_action, redo_args))
        return True

    @contextmanager
    def group(self, description: str):
        if self._current_group is not None:
            raise RuntimeError("Nested undo groups are not supported")
        
        group = UndoGroup(description)
        self._current_group = group
        try:
            yield group
        finally:
            self._current_group = None
            if self._enabled and group.actions:
                self.undo_stack.append((group, (), description))
                self.redo_stack.clear()
                self._check_memory_usage()

    def are_enabled(self) -> bool:
        return self._enabled

    def are_disabled(self) -> bool:
        return not self._enabled

    def disable(self) -> bool:
        if self._enabled:
            self._enabled = False
            print("Warning: Undos are now disabled.")
            return True
        return False

    def toggle(self) -> bool:
        self._enabled = not self._enabled
        return self._enabled

    def memory_usage(self) -> int:
        return sum(sys.getsizeof(item) for item in self.undo_stack + self.redo_stack)

    def memory_usage_limit(self) -> int:
        return self._memory_limit

    def set_memory_limit(self, limit: int):
        self._memory_limit = limit
        self._check_memory_usage()

    def clear(self):
        self.undo_stack.clear()
        self.redo_stack.clear()

    def get_undo_text(self) -> str:
        if not self.undo_stack:
            return "No undo available"
        return " -> ".join(action[2] for action in reversed(self.undo_stack))

    def get_redo_text(self) -> str:
        if not self.redo_stack:
            return "No redo available"
        return " -> ".join(action[2] for action in self.redo_stack)

    def export_stack(self) -> dict:
        data = {
            "undo_stack": [(func.__name__, args, desc) for func, args, desc in self.undo_stack],
            "redo_stack": [(func.__name__, args, desc) for func, args, desc in self.redo_stack]
        }
        return data

    def import_stack(self, filename: str):
        with open(filename, 'r') as f:
            data = json.load(f)
        # Note: This is a simplified version. In a real implementation,
        # you'd need to map function names back to actual functions.
        self.undo_stack = [(eval(func), args, desc) for func, args, desc in data["undo_stack"]]
        self.redo_stack = [(eval(func), args, desc) for func, args, desc in data["redo_stack"]]

    def get_stats(self) -> dict:
        return {
            "undo_count": len(self.undo_stack),
            "redo_count": len(self.redo_stack),
            "memory_usage": self.memory_usage(),
            "memory_limit": self._memory_limit,
            "enabled": self._enabled
        }

    def _check_memory_usage(self):
        while self.memory_usage() > self._memory_limit and (self.undo_stack or self.redo_stack):
            if self.undo_stack:
                self.undo_stack.pop(0)
            elif self.redo_stack:
                self.redo_stack.pop(0)

""" Example of how to implement the UNDO stack
# Example usage
if __name__ == "__main__":
    um = UndoManager()

    # Add some actions
    um.add_action(lambda x: x, (1,), "Action 1")
    um.add_action(lambda x: x, (2,), "Action 2")

    print(f"Undo text: {um.get_undo_text()}")
    print(f"Redo text: {um.get_redo_text()}")

    um.set_memory_limit(1024 * 1024)  # Set 1MB limit
    print(f"New memory limit: {um.memory_usage_limit()} bytes")

    um.export_stack("undo_stack.json")
    um.clear()
    um.import_stack("undo_stack.json")

    print("Stats:", um.get_stats())


class FakeNode:
    all_nodes = []
    
    def __init__(self, color="blue"):
        self.color = color
        FakeNode.all_nodes.append(self)
        UndoManager().add_action(
            lambda x: Node.all_nodes.remove(x) if x in Node.all_nodes else None,
            (self,),
            f"Create {id(self)}"
        )

    def set_color(self, new_color):
        old_color = self.color
        self.color = new_color
        UndoManager().add_action(
            setattr,
            (self, "color", old_color),
            f"Set color {id(self)}"
        )

    def delete(self):
        if self in FakeNode.all_nodes:
            idx = FakeNode.all_nodes.index(self)
            FakeNode.all_nodes.remove(self)
            UndoManager().add_action(
                lambda i, n: FakeNode.all_nodes.insert(i, n),
                (idx, self),
                f"Delete {id(self)}"
            )
"""
