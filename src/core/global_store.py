from typing import Any, Dict
import warnings


class GlobalStore:
    """
    A Singleton class for storing and managing key-value pairs globally.
    All key names must be at least two characters long and in all caps.
    """

    _instance: Dict[str, Any] = {}
    
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

    def set(cls, key: str, value: Any) -> None:
        cls._validate_key(key)
        cls._instance[key] = value

    def get(cls, key: str) -> Any:
        cls._validate_key(key)
        return cls._instance.get(key)

    def cut(cls, key: str) -> None:
        cls._validate_key(key)
        cls._instance.pop(key, None)

    def list(cls) -> Dict[str, Any]:
        return dict(cls._instance)

    def has(cls, key: str) -> bool:
        cls._validate_key(key)
        return key in cls._instance
    
    def flush_all_globals(cls):
        cls._instance.clear()
