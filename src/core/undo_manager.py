import sys
import json

class UndoManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UndoManager, cls).__new__(cls)
            cls._instance.undo_stack = []
            cls._instance.redo_stack = []
            cls._instance._enabled = True
            cls._instance._memory_limit = 1024 * 1024 * 10  # 10 MB default limit
        return cls._instance

    def undo(self):
        if self._enabled and self.undo_stack:
            action, args, description = self.undo_stack.pop()
            action(*args)
            self.redo_stack.append((action, args, description))
            self.redo_stack.clear()

    def redo(self):
        if self._enabled and self.redo_stack:
            action, args, description = self.redo_stack.pop()
            action(*args)
            self.undo_stack.append((action, args, description))

    def add_action(self, action, args, description):
        if self._enabled:
            self.undo_stack.append((action, args, description))
            self.redo_stack.clear()
            self._check_memory_usage()

    def areEnabled(self) -> bool:
        return self._enabled

    def areDisabled(self) -> bool:
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

    def memoryUsage(self) -> int:
        return sum(sys.getsizeof(item) for item in self.undo_stack + self.redo_stack)

    def memoryUsageLimit(self) -> int:
        return self._memory_limit

    def setMemoryLimit(self, limit: int):
        self._memory_limit = limit
        self._check_memory_usage()

    def clear(self):
        self.undo_stack.clear()
        self.redo_stack.clear()

    def getUndoText(self) -> str:
        return self.undo_stack[-1][2] if self.undo_stack else "No undo available"

    def getRedoText(self) -> str:
        return self.redo_stack[-1][2] if self.redo_stack else "No redo available"

    def exportStack(self) -> str:
        data = {
            "undo_stack": [(func.__name__, args, desc) for func, args, desc in self.undo_stack],
            "redo_stack": [(func.__name__, args, desc) for func, args, desc in self.redo_stack]
        }
        return data

    def importStack(self, filename: str):
        with open(filename, 'r') as f:
            data = json.load(f)
        # Note: This is a simplified version. In a real implementation,
        # you'd need to map function names back to actual functions.
        self.undo_stack = [(eval(func), args, desc) for func, args, desc in data["undo_stack"]]
        self.redo_stack = [(eval(func), args, desc) for func, args, desc in data["redo_stack"]]

    def getStats(self) -> dict:
        return {
            "undo_count": len(self.undo_stack),
            "redo_count": len(self.redo_stack),
            "memory_usage": self.memoryUsage(),
            "memory_limit": self._memory_limit,
            "enabled": self._enabled
        }

    def _check_memory_usage(self):
        while self.memoryUsage() > self._memory_limit and (self.undo_stack or self.redo_stack):
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

    print(f"Undo text: {um.getUndoText()}")
    print(f"Redo text: {um.getRedoText()}")

    um.setMemoryLimit(1024 * 1024)  # Set 1MB limit
    print(f"New memory limit: {um.memoryUsageLimit()} bytes")

    um.exportStack("undo_stack.json")
    um.clear()
    um.importStack("undo_stack.json")

    print("Stats:", um.getStats())


class Node:
    all_nodes = []

    def __init__(self, color="blue"):
        self.color = color
        Node.all_nodes.append(self)
        UndoManager().add_action(self.delete, ())

    def set_color(self, new_color):
        old_color = self.color
        self.color = new_color
        UndoManager().add_action(self.set_color, (old_color,))

    def delete(self):
        if self in Node.all_nodes:
            Node.all_nodes.remove(self)
            state = self.__dict__.copy()
            UndoManager().add_action(Node.recreate, (state,))
            del self

    @classmethod
    def recreate(cls, state):
        new_node = cls.__new__(cls)
        new_node.__dict__.update(state)
        cls.all_nodes.append(new_node)
        UndoManager().add_action(new_node.delete, ())
        return new_node
"""
