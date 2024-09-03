class UndoManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UndoManager, cls).__new__(cls)
            cls._instance.undo_stack = []
            cls._instance.redo_stack = []
        return cls._instance

    def undo(self):
        if self.undo_stack:
            action, args = self.undo_stack.pop()
            action(*args)
            self.redo_stack.append((action, args))

    def redo(self):
        if self.redo_stack:
            action, args = self.redo_stack.pop()
            action(*args)
            self.undo_stack.append((action, args))

