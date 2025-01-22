import ast
import os
import sys
from pathlib import Path

def analyze_syntax(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return ast.parse(f.read())

def scan_dir(directory):
    min_version = (3, 0)
    version_features = {
        (3, 5): {'AsyncFor', 'AsyncWith', 'Await'},
        (3, 6): {'FormattedValue', 'JoinedStr'},
        (3, 7): {'AsyncGen'},
        (3, 8): {'NamedExpr'},
        (3, 9): {'Match', 'MatchAs', 'MatchOr', 'MatchStar'},
        (3, 10): {'Match', 'Pattern', 'MatchValue', 'MatchSingleton'},
        (3, 11): {'TypeAlias', 'TypeVar'},
        (3, 12): {'TypeVarTuple', 'ParamSpec'}
    }

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                try:
                    tree = analyze_syntax(Path(root) / file)
                    for node in ast.walk(tree):
                        node_type = type(node).__name__
                        for version, features in version_features.items():
                            if node_type in features:
                                min_version = max(min_version, version)
                except Exception as e:
                    print(f"Error processing {file}: {e}", file=sys.stderr)

    return min_version

if __name__ == '__main__':
    directory = 'src'
    min_py_version = scan_dir(directory)
    print(f"Minimum Python version required: {min_py_version[0]}.{min_py_version[1]}")