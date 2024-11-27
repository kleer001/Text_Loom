from typing import Any, Dict
import warnings

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

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        from core.undo_manager import UndoManager
        
        cls._validate_key(key)
        exists = key in cls._instance
        
        # Push state before modifying
        if exists:
            UndoManager().push_state(f"Update global: {key}")
        else:
            UndoManager().push_state(f"Add global: {key}")
            
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
            cls._instance.clear()
            UndoManager().push_state("Flush all globals")

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