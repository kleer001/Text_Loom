import cmd
import sys
from typing import Dict, Optional
from base_classes import Node, NodeType

class NodeShell(cmd.Cmd):
    intro = "Welcome to the Node Shell. Type '/h' or 'help' for list of commands."
    prompt = ">>> "

    def __init__(self):
        super().__init__()
        self.root = Node("root", "/", [0, 0], NodeType.NULL)
        self.current_node = self.root

    def do_createnode(self, arg):
        """Create a new node. Usage: createnode [node_type] [name]"""
        args = arg.split()
        if not args:
            print("Error: Node type is required.")
            return

        node_type = args[0].upper()
        name = args[1] if len(args) > 1 else None

        try:
            new_node = self.current_node.create_node(NodeType[node_type], name)
            print(f"Created node: {new_node}")
        except KeyError:
            print(f"Error: Invalid node type '{node_type}'")
        except Exception as e:
            print(f"Error creating node: {str(e)}")

    def do_setinput(self, arg):
        """Connect nodes. Usage: setinput [input_node] [input_index] [output_node] [output_index]"""
        args = arg.split()
        if len(args) != 4:
            print("Error: Invalid number of arguments.")
            return

        input_node, input_index, output_node, output_index = args
        try:
            input_node = self._find_node(input_node)
            output_node = self._find_node(output_node)
            if input_node and output_node:
                input_node.set_input(input_index, output_node, output_index)
                print(f"Connected {output_node.name()} to {input_node.name()}")
            else:
                print("Error: One or both nodes not found.")
        except Exception as e:
            print(f"Error connecting nodes: {str(e)}")

    def do_deletenode(self, arg):
        """Delete a node. Usage: deletenode [node_name]"""
        if not arg:
            print("Error: Node name is required.")
            return

        node = self._find_node(arg)
        if node:
            node.destroy()
            print(f"Deleted node: {arg}")
        else:
            print(f"Error: Node '{arg}' not found.")

    def do_listchildren(self, arg):
        """List children of current node or specified node. Usage: listchildren [node_name]"""
        node = self._find_node(arg) if arg else self.current_node
        if node:
            children = node.children()
            if children:
                for child in children:
                    print(f"{child.name()} ({child.type().value})")
            else:
                print("No children.")
        else:
            print(f"Error: Node '{arg}' not found.")

    def do_cd(self, arg):
        """Change current node. Usage: cd [node_name]"""
        if not arg or arg == "/":
            self.current_node = self.root
            print("Changed to root node.")
        else:
            node = self._find_node(arg)
            if node:
                self.current_node = node
                print(f"Changed to node: {node.name()}")
            else:
                print(f"Error: Node '{arg}' not found.")

    def do_pwd(self, arg):
        """Print current node path."""
        print(self.current_node.node_path())

    def do_rename(self, arg):
        """Rename a node. Usage: rename [old_name] [new_name]"""
        args = arg.split()
        if len(args) != 2:
            print("Error: Invalid number of arguments.")
            return

        old_name, new_name = args
        node = self._find_node(old_name)
        if node:
            node.set_name(new_name)
            print(f"Renamed node '{old_name}' to '{new_name}'")
        else:
            print(f"Error: Node '{old_name}' not found.")

    def do_exit(self, arg):
        """Exit the shell."""
        print("Goodbye!")
        return True

    def do_h(self, arg):
        """Print the list of available commands."""
        print("Available commands:")
        for name, func in self.get_names():
            if name.startswith('do_'):
                print(f"  {name[3:]}: {func.__doc__}")

    def _find_node(self, name: str) -> Optional[Node]:
        """Find a node by name in the current node's children."""
        if name == self.current_node.name():
            return self.current_node
        for child in self.current_node.children():
            if child.name() == name:
                return child
        return None

    def default(self, line):
        """Handle invalid commands."""
        print(f"Error: Invalid command '{line}'. Type '/h' for help.")

if __name__ == "__main__":
    NodeShell().cmdloop()
