import re
import os
from typing import Optional, Dict

import inspect



class LoopManager:

    """
    A singleton manager for handling loop iteration states in Text Loom's node system.

    This class tracks the current iteration state for each looper node in the system,
    allowing nodes within loops to access their current iteration context. It uses
    a path-based key system to maintain separate loop counters for different looper nodes.

    Path Key Format:
    - Keys are prefixed with 'loop_'
    - Followed by the full path of the looper node
    Example: 'loop_/root/mylooper'

    Methods:
    get_current_loop(path): Gets iteration count for a node's containing loop
        Example: iteration = loop_manager.get_current_loop('/root/myloop/node1')
        Returns 0 if no loop context is found (failsafe behavior)
    
    set_loop(looper_name, value): Sets or clears loop iteration state
        Example: loop_manager.set_loop('/root/myloop', 5)  # Set to iteration 5
                loop_manager.set_loop('/root/myloop', None)  # Clear loop state
    
    clean_stale_loops(looper_name): Removes loop tracking for inactive loopers
        Example: loop_manager.clean_stale_loops('/root/oldloop')

    The class maintains thread safety through singleton pattern implementation and
    provides cleanup methods to prevent memory leaks from stale loop contexts.
    """

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
        #print(f"♺ Get_Current_LOOP: Returning {current_loop} for {path} with {current_loop}")
        if current_loop == None: #because if we don't it'll error out if we don't cook the loop, better to have something than error out
            return 0
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

