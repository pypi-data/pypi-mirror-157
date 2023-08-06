from .exception import Exception

class UnknownErrorFileException(Exception):
    def __init__(self, path):
        Exception.__init__(self, "UnknownError", f"BooSQL can't create file at path: {path}")
    
    def display(self):
        self.execute()