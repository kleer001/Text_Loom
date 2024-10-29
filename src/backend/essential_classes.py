class NodeEnvironment:
    _instance = None
    nodes: Dict[str, 'Node'] = {}

    def __init__(self):
        self._node_created_callbacks = []
        self._creating_node = False  # Flag to prevent recursive calls
        self.root = PurePosixPath("/")
        self.current_node = None
        self.globals = self._build_globals()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NodeEnvironment, cls).__new__(cls)
            cls._instance.root = PurePosixPath("/")
            cls._instance.current_node = None
            cls._instance.globals = cls._instance._build_globals()
        return cls._instance

    def _build_globals(self) -> Dict[str, Any]:
        return {
            'Node': Node,
            'NodeType': NodeType,
            'current_node': self.current_node,
            'NodeEnvironment': NodeEnvironment,
        }

    def get_namespace(self):
        return {
            'current_node': self.current_node,
            **self.globals
        }

    def execute(self, code):
        try:
            local_vars = {}
            exec(code, self.get_namespace(), local_vars)
            self.globals.update(local_vars)
            return local_vars.get('_') if '_' in local_vars else None
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    def inspect(self):
        print("NodeEnvironment state:")
        print(f"Nodes: {self.nodes}")
        print(f"Globals: {self.globals}")

    @classmethod
    def list_nodes(cls) -> list[str]:
        return list(cls.nodes.keys())
    
    @classmethod
    def node_exists(cls, node_name: str) -> bool:
        return node_name in cls.nodes
    
    @classmethod
    def add_node(cls, node: 'Node'):
        if cls.get_instance()._creating_node:
            return
        cls.get_instance()._creating_node = True
        cls.nodes[node.path()] = node    
        # Call post-registration initialization, for looper node internal node creation
        if hasattr(node.__class__, 'post_registration_init'):
            node.__class__.post_registration_init(node)
        
        cls.get_instance()._creating_node = False

    @classmethod
    def node_from_name(cls, node_name: str) -> Optional['Node']:
        if node_name in cls.nodes:
            return cls.nodes[node_name]
        for path, node in cls.nodes.items(): #because of synsugar to work with only names, not paths
            if node_name == path.split('/')[-1]:
                return node
        return None

    @classmethod
    def create_node(cls, node_type: NodeType, node_name: Optional[str] = None, parent_path: str = "/") -> "Node":


    def set_input(self, input_index: int, input_node: "Node", output_index: int = 0) -> None:
        """Connects an input of this node to an output of another node."""
        if hasattr(self, 'SINGLE_INPUT') and self.SINGLE_INPUT and self._inputs:
            self.add_warning(f"Node type {self.__class__.__name__} accepts only one input. Existing input will be replaced.")
            self._remove_connection(next(iter(self._inputs.values())))

        if input_index in self._inputs:
            self._remove_connection(self._inputs[input_index])

        connection = NodeConnection(input_node, self, output_index, input_index)
        print("New Connection: from input ", self.name(), " to output: ", input_node.name())
        self._inputs[input_index] = connection
        input_node._outputs.setdefault(output_index, []).append(connection)
        # TODO Add undo logic
