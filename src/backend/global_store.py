from typing import Any, Dict

class GlobalStore:
    """
    A Singleton class for storing and managing key-value pairs globally.
    All methods do what they say on the tin. 
    """

    _instance: Dict[str, Any] = {}

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        cls._instance[key] = value

    @classmethod
    def get(cls, key: str) -> Any:
        return cls._instance[key]

    @classmethod
    def cut(cls, key: str) -> None:
        cls._instance.pop(key, None)

    @classmethod
    def list(cls) -> Dict[str, Any]:
        return dict(cls._instance)

    @classmethod
    def has(cls, key: str) -> bool:
        return key in cls._instance