import sys
from core.base_classes import *  # replace 'xyz' with the actual name of your module

um = UndoManager()

while True:
    try:
        expression = input(">>> ")
        result = eval(expression, {'__builtins__': __builtins__}, {**locals(), **globals()})
        print(result)
    except Exception as e:
        print(e)
