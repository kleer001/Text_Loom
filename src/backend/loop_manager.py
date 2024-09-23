import re
import os
from typing import Optional, Dict

class LoopManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoopManager, cls).__new__(cls)
            cls._instance._loops: Dict[str, int] = {}
        return cls._instance

    def get_loop_var_name(self, path: str) -> str:
        # Get the parent folder of the current path
        parent_path = os.path.dirname(path)
        safe_path = re.sub(r"[^a-zA-Z0-9_]", "_", parent_path)
        var_name = f"loop_{parent_path}"
        print(f"get_loop_var_name: Returning {var_name}")
        return var_name

    def get_current_loop(self, path: str) -> Optional[int]:
        var_name = self.get_loop_var_name(path)
        current_loop = self._loops.get(var_name)
        print(f"get_current_loop: Returning {current_loop} for {path}")
        return current_loop

    def set_loop(self, path: str, value: Optional[int]) -> None:
        var_name = self.get_loop_var_name(path)
        if value is None:
            self._loops.pop(var_name, None)
            print(f"set_loop: Removed loop {var_name}")
        else:
            self._loops[var_name] = value
            print(f"set_loop: Set loop {var_name} to {value}")

    def clean_stale_loops(self) -> None:
        self._loops.clear()
        print("clean_stale_loops: Cleared all loops")

# Create a single instance of LoopManager
loop_manager = LoopManager()
