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
        exists = key in cls._instance
        old_value = cls._instance.get(key) if exists else None
        cls._instance[key] = value
        
        if exists:
            UndoManager().add_action(
                lambda k, v: cls._instance.__setitem__(k, v),
                (key, old_value),
                f"Update global: {key}",
                lambda k, v: cls._instance.__setitem__(k, v),
                (key, value)
            )
        else:
            UndoManager().add_action(
                lambda k: cls._instance.pop(k, None),
                (key,),
                f"Add global: {key}",
                lambda k, v: cls._instance.__setitem__(k, v),
                (key, value)
            )

    @classmethod
    def cut(cls, key: str) -> None:
        cls._validate_key(key)
        if key in cls._instance:
            old_value = cls._instance[key]
            cls._instance.pop(key)
            
            UndoManager().add_action(
                lambda k, v: cls._instance.__setitem__(k, v),
                (key, old_value),
                f"Cut global: {key}",
                lambda k: cls._instance.pop(k, None),
                (key,)
            )

    @classmethod
    def flush_all_globals(cls):
        if cls._instance:
            old_state = dict(cls._instance)
            cls._instance.clear()
            
            UndoManager().add_action(
                lambda state: cls._instance.update(state),
                (old_state,),
                "Flush all globals",
                lambda: cls._instance.clear(),
                ()
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
    
