import cmd
from base_classes import NodeEnvironment, Node, NodeType

class NodeShell(cmd.Cmd):
    intro = 'Welcome to the node shell. Type help or ? to list commands.\n'
    prompt = '>>> '

    def __init__(self):
        super().__init__()
        self.env = NodeEnvironment()

    def default(self, line):
        """Execute the input as Python code."""
        try:
            result = self.env.execute(f"_ = {line}")
            print(result)
        except Exception as e:
            print(f"Error: {str(e)}")

    def do_exit(self, arg):
        """Exit the shell."""
        print("Exiting...")
        return True

    def do_help(self, arg):
        """Show help message."""
        if arg:
            try:
                help_text = self.env.execute(f"help({arg})")
                if help_text is None:
                    print(f"No help available for '{arg}'")
            except Exception:
                print(f"No help available for '{arg}'")
        else:
            print("Welcome to the Node Shell!")
            print("You can execute any Python code directly.")
            print("\nAvailable classes and methods:")
            print("  Node.create_node(node_type, node_name)")
            print("  NodeEnvironment.list_nodes()")
            print("\nUseful classes and objects:")
            print("  Node, NodeType")
            print("\nExamples:")
            print("  >>> Node.create_node(NodeType.NULL, 'test')")
            print("  >>> print(NodeEnvironment.list_nodes())")
            print("  >>> help(Node)")

def main():
    NodeShell().cmdloop()

if __name__ == "__main__":
    main()

