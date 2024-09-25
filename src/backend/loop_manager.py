import re
import os
from typing import Optional, Dict

import inspect

def print_calfun():
    frame = inspect.stack()[2]
    frame2 = inspect.stack()[3]
    frame3 = inspect.stack()[4]
    frame4 = inspect.stack()[5]
    frame5 = inspect.stack()[6]
    frame5 = inspect.stack()[7]
    calfun = frame.function
    calfun2 = frame2.function
    calfun3 = frame3.function
    calfun4 = frame4.function
    calfun5 = frame4.function
    calfun6 = frame4.function
    print(f"~fP~ {calfun}←{calfun2}←{calfun3}←{calfun4}←{calfun5}←{calfun6}")



class LoopManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoopManager, cls).__new__(cls)
            cls._instance._loops: Dict[str, int] = {}
        return cls._instance

    def get_current_loop(self, path: str) -> Optional[int]:
        # Extract the looper name from the full path
        looper_path = os.path.dirname(path)
        loop_key = f"loop_{looper_path}"
        current_loop = self._loops.get(loop_key)
        print(f"♺ Get_Current_LOOP: Returning {current_loop} for {path} with {current_loop}")
        print_calfun()
        return current_loop

    def set_loop(self, looper_name: str, value: Optional[int]) -> None:
        loop_key = f"loop_{looper_name}"
        if value is None:
            self._loops.pop(loop_key, None)
            print(f"SET-LOOP: Removed loop {loop_key}")
        else:
            self._loops[loop_key] = value
            print(f"SET_LOOP: Set loop {loop_key} to {value}")

    def clean_stale_loops(self, looper_name: str) -> None:
        loop_key = f"loop_{looper_name}"
        if loop_key in self._loops:
            del self._loops[loop_key]
            print(f"clean_stale_loops: Removed loop {loop_key}")
        else:
            print(f"clean_stale_loops: No loop found for {looper_name}")


# Create a single instance of LoopManager
loop_manager = LoopManager()

