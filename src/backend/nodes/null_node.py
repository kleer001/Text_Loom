from typing import Any, Dict, Optional, Tuple
from base_classes import Node, NodeType, NodeState

class NullNode(Node):
    """
    Represents a Null Node in the workspace.
    
    The Null Node is a simple pass-through node that doesn't modify its input.
    It has a single input and can connect its output to multiple other nodes.
    """

    def __init__(self, name: str, path: str, position: Tuple[float, float], node_type: NodeType):
        """
        Initialize a new NullNode.

        Args:
            name (str): The name of the node.
            path (str): The path of the node in the workspace hierarchy.
            position (Tuple[float, float]): The initial position of the node (x, y).
            node_type (NodeType): The type of the node (should be NodeType.NULL).
        """
        super().__init__(name, path, position, node_type)
        self._input_value: Any = None

    def process(self) -> None:
        """
        Process the input data.

        For a Null Node, this simply passes the input to the output without modification.
        """
        # The Null Node doesn't modify the input, so we just need to update its state
        self.set_state(NodeState.UNCHANGED)

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
            "type": self.type().value,
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
            position=tuple(data["position"]),
            node_type=NodeType.NULL
        )
        if "input_value" in data:
            node._input_value = data["input_value"]
        return node
