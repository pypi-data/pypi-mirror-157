import sys

class Exception:
    def __init__(self, name, reason):
        self.name = name
        self.reason = reason
    
    def execute(self):
        print(f"BooSQL={self.name}\n {self.reason}")
        sys.exit(0)