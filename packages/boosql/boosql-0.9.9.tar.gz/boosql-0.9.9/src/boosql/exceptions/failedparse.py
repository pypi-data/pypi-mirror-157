from .exception import Exception

class FailedParseException(Exception):
    def __init__(self):
        Exception.__init__(self, "FailedParse", f"Parser can't recognize your database file as BooSQL database file. Don't edit .db file please!")
    
    def display(self):
        self.execute()