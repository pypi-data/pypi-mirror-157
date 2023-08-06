from .exception import Exception

class InvalidPathException(Exception):
    def __init__(self, path):
        Exception.__init__(self, "InvalidPath", f"Your path: {path}")
    
    def display(self):
        self.execute()