from typing import Any, Dict, Optional
from base_classes import Node, NodeState

class NullNode(Node):
    """
    Represents a Null Node in the workspace.
    
    The Null Node is a simple pass-through node that doesn't modify its input.
    It has a single input and can connect its output to multiple other nodes.
    """

    def __init__(self, name: Optional[str] = None, path: str = "/", position: list[float] = [0.0, 0.0]):
        """
        Initialize a new NullNode.

        Args:
            name (Optional[str]): The name of the node. If None, a default name will be used.
            path (str): The path of the node in the workspace hierarchy.
            position (list[float]): The initial position of the node [x, y].
        """
        super().__init__(
            name or self._generate_default_name(),
            path,
            position,
            "NullNode"
        )
        self._input_value: Any = None

    @classmethod
    def _generate_default_name(cls) -> str:
        """Generate a default name for the Null Node."""
        return f"NullNode_{Node.get_instance_count() + 1}"

    def process(self) -> None:
        """
        Process the input data.

        For a Null Node, this simply passes the input to the output without modification.
        """
        # The Null Node doesn't modify the input, so we just need to update its state
        self._state = NodeState.UNCHANGED

    def set_input(self, value: Any) -> None:
        """
        Set the input value for the Null Node.

        Args:
            value (Any): The input value to be set.
        """
        self._input_value = value
        self._state = NodeState.UNCOOKED

    def get_output(self) -> Any:
        """
        Get the output value of the Null Node.

        Returns:
            Any: The unmodified input value.
        """
        return self._input_value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the NullNode to a dictionary representation.

        Returns:
            Dict[str, Any]: A dictionary containing the NullNode's data.
        """
        return {
            "name": self.name(),
            "type": "NullNode",
            "path": self.path(),
            "position": self.position(),
            "input_value": self._input_value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NullNode':
        """
        Create a NullNode instance from a dictionary representation.

        Args:
            data (Dict[str, Any]): A dictionary containing the NullNode's data.

        Returns:
            NullNode: A new NullNode instance.
        """
        node = cls(
            name=data["name"],
            path=data["path"],
            position=data["position"]
        )
        node.set_input(data["input_value"])
        return node
