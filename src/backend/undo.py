import pickle
from typing import Callable, Optional

class UndoManager:
    def __init__(self, undo_depth: int = -1, debug: bool = True):
        self.undo_stack = []
        self.redo_stack = []
        self.undo_depth = undo_depth
        self.debug = debug
        self.undo_limit_reached = False

    def execute(self, command: Callable, undo_command: Callable):
        if self.debug:
            print(f"Executing command: {command.__name__}")

        if self.undo_depth != -1 and len(self.undo_stack) >= self.undo_depth:
            if not self.undo_limit_reached:
                print("Warning: Undo limit reached.")
                self.undo_limit_reached = True
            self.undo_stack.pop(0)  # Remove the oldest command to maintain the limit

        self.undo_stack.append((command, undo_command))
        self.redo_stack.clear()
        command()

    def undo(self):
        if self.can_undo:
            command, undo_command = self.undo_stack.pop()
            self.redo_stack.append((command, undo_command))
            if self.debug:
                print(f"Undoing command: {undo_command.__name__}")
            undo_command()
        else:
            print("Error: No actions to undo.")

    def redo(self):
        if self.can_redo:
            command, undo_command = self.redo_stack.pop()
            self.undo_stack.append((command, undo_command))
            if self.debug:
                print(f"Redoing command: {command.__name__}")
            command()
        else:
            print("Error: No actions to redo.")

    @property
    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0

    def serialize(self) -> bytes:
        return pickle.dumps((self.undo_stack, self.redo_stack))

    def deserialize(self, data: bytes):
        self.undo_stack, self.redo_stack = pickle.loads(data)
        if self.debug:
            print("UndoManager state deserialized.")

    def set_undo_depth(self, depth: int):
        self.undo_depth = depth
        self.undo_limit_reached = False  # Reset warning flag

""" Example usage with the Bottle class
class Bottle:
    def __init__(self, undo_manager: UndoManager):
        self._color = [1.0, 1.0, 1.0]
        self.undo_manager = undo_manager

    def set_color(self, rgb: list[float]):
        old_color = self._color[:]
        self._color = rgb
        self.undo_manager.execute(
            lambda: self.set_color(rgb),  # Redo action
            lambda: self.set_color(old_color)  # Undo action
        )

    def get_color(self) -> list[float]:
        return self._color
"""