from textual.message import Message
from core.parm import ParameterType
from dataclasses import dataclass

class NodeSelected(Message):
    def __init__(self, node_path: str) -> None:
        self.node_path = node_path
        super().__init__()

class ParameterChanged(Message):
    def __init__(self, node_path: str, param_name: str, new_value: str, param_type: ParameterType) -> None:
        self.node_path = node_path
        self.param_name = param_name
        self.new_value = new_value
        self.param_type = param_type
        super().__init__()

class ScrollMessage(Message):
    def __init__(self, direction: int):
        self.direction = direction
        super().__init__()

class NodeTypeSelected(Message):
    def __init__(self, node_type: str) -> None:
        self.node_type = node_type
        super().__init__()

class OutputMessage(Message):
    def __init__(self, output_data: list[str]) -> None:
        self.output_data = output_data
        super().__init__()

class NodeAdded(Message):
    def __init__(self, node_path: str, node_type: str) -> None:
        self.node_path = node_path
        self.node_type = node_type
        super().__init__()

class NodeDeleted(Message):
    def __init__(self, node_path: str) -> None:
        self.node_path = node_path
        super().__init__()

class ConnectionAdded(Message):
    def __init__(self, from_node: str, to_node: str) -> None:
        self.from_node = from_node
        self.to_node = to_node
        super().__init__()

class ConnectionDeleted(Message):
    def __init__(self, from_node: str, to_node: str) -> None:
        self.from_node = from_node
        self.to_node = to_node
        super().__init__()

class GlobalAdded(Message):
    def __init__(self, key: str, value: any) -> None:
        self.key = key
        self.value = value
        super().__init__()

class GlobalDeleted(Message):
    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__()

class GlobalChanged(Message):
    def __init__(self, key: str, value: any) -> None:
        self.key = key
        self.value = value
        super().__init__()