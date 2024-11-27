from typing import Any, Dict
import warnings
from core.undo_manager import UndoManager


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
        cls._validate_key(key)
        old_value = cls._instance.get(key, None)
        exists = key in cls._instance
        
        def undo_func(target_cls, k, existed, old):
            if existed:
                target_cls._instance[k] = old
            else:
                target_cls._instance.pop(k, None)
                
        cls._instance[key] = value
        
        UndoManager().add_action(
            undo_func,
            (cls, key, exists, old_value),
            f"Set global: {key}",
            cls.set,
            (key, value)
        )

    @classmethod
    def cut(cls, key: str) -> None:
        cls._validate_key(key)
        if key in cls._instance:
            old_value = cls._instance[key]
            cls._instance.pop(key)
            
            UndoManager().add_action(
                cls.set,
                (key, old_value),
                f"Cut global: {key}",
                cls.cut,
                (key,)
            )

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
    
    @classmethod
    def flush_all_globals(cls):
        if cls._instance:
            old_state = dict(cls._instance)
            cls._instance.clear()
            
            def restore_state(target_cls, state):
                target_cls._instance.clear()
                target_cls._instance.update(state)
            
            UndoManager().add_action(
                restore_state,
                (cls, old_state),
                "Flush all globals",
                cls.flush_all_globals,
                ()
            )