from typing import Any, Dict
import warnings


"""
A singleton key-value store for managing global variables in Text Loom with undo/redo support.

This class provides a centralized storage mechanism for global variables with strict key
validation rules and integration with the undo system.

Key Validation Rules:
- Must be at least 2 characters long
- Must be all uppercase letters
- Cannot start with '$'
Valid keys: 'MYVAR', 'CURRENT_INDEX', 'MAX_DEPTH' 
Invalid keys: 'x', 'myVar', '$TEST', 'lowercase'

Values can be of any type (Any).

Methods:
   set(key, value): Stores a value with undo support
       Example: GlobalStore.set('MAX_ITEMS', 100)
   
   get(key): Retrieves a stored value
       Example: count = GlobalStore.get('TOTAL_COUNT')
   
   cut(key): Removes a key-value pair with undo support
       Example: GlobalStore.cut('TEMP_DATA')
   
   has(key): Checks if a key exists
       Example: if GlobalStore.has('INITIALIZED'): ...
   
   list(): Returns all stored key-value pairs
       Example: all_globals = GlobalStore.list()
   
   flush_all_globals(): Clears all stored values with undo support
       Example: GlobalStore.flush_all_globals()

All modification methods (set, cut, flush_all_globals) automatically integrate
with the undo system by pushing the previous state before making changes.
"""

class GlobalStore:
    _instance: Dict[str, Any] = {}
    
    @classmethod
    def _validate_key(cls, key: str) -> None:        
        if key.startswith('$'):
            warning_message = (
                f"🗝️ Warning: Invalid key format '{key}'. "
                "Keys cannot start with a $"
            )
            warnings.warn(warning_message, UserWarning)
            raise ValueError(warning_message)
        if len(key) < 2 or not key.isupper():
            warning_message = (
                f"🗝️ Warning: Invalid key format '{key}'. "
                "Keys must be at least two characters long and in all caps."
            )
            warnings.warn(warning_message, UserWarning)
            raise ValueError("Invalid key")

    #protype for undo method interface
    @classmethod
    def set(cls, key: str, value: Any) -> None:
        #declare this within method to avoid circular dependency
        from core.undo_manager import UndoManager
        
        cls._validate_key(key)
        exists = key in cls._instance
        
        # Push state before modifying
        if exists:
            UndoManager().push_state(f"Update global: {key}:{value}")
        else:
            UndoManager().push_state(f"Add global: {key}:{value}")
            
        # Modify after pushing state
        cls._instance[key] = value

    @classmethod
    def cut(cls, key: str) -> None:
        from core.undo_manager import UndoManager
        
        cls._validate_key(key)
        if key in cls._instance:
            # Push state before modifying
            UndoManager().push_state(f"Cut global: {key}")
            cls._instance.pop(key)

    @classmethod
    def flush_all_globals(cls) -> None:
        from core.undo_manager import UndoManager
        
        if cls._instance:
            UndoManager().push_state("Flush all globals")
            cls._instance.clear()
            

    @classmethod
    def get(cls, key: str) -> Any:
        cls._validate_key(key)
        return cls._instance.get(key)

    @classmethod
    def list(cls) -> Dict[str, Any]:
        return dict(cls._instance)

    @classmethod
    def has(cls, key: str) -> bool:
        cls._validate_key(key)
        return key in cls._instance