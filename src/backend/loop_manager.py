import re
from typing import Optional, Dict

class LoopManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoopManager, cls).__new__(cls)
            cls._instance._loops: Dict[str, int] = {}
        return cls._instance

    def get_loop_var_name(self, path: str, depth: int) -> str:
        safe_path = re.sub(r"[^a-zA-Z0-9_]", "_", path)
        var_name = f"loop_{safe_path}_{depth}"
        print(f"get_loop_var_name: Returning {var_name}")
        return var_name

    def get_current_loop(self, path: str, depth: int) -> Optional[int]:
        var_name = self.get_loop_var_name(path, depth)
        current_loop = self._loops.get(var_name)
        print(f"get_current_loop: Returning {current_loop}")
        return current_loop

    def set_loop(self, path: str, depth: int, value: Optional[int]) -> None:
        var_name = self.get_loop_var_name(path, depth)
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