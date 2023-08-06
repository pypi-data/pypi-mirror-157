from .exceptions.invalidpath import InvalidPathException
from .exceptions.unknownerrorfile import UnknownErrorFileException
from .manager import Manager
from base64 import *
from binascii import *

class Initializer:
    def __init__(self, path, obfuscate):
        self.path = path
        self.__obf = obfuscate
        
        self.invalid_path = InvalidPathException(self.path)
        self.uef = UnknownErrorFileException(self.path)
        self._manager = Manager(self)
    
    def create_file(self):
        try:
            with open(self.path, 'w', encoding='cp037') as db:
                db.write(b85encode("BOOSQL-FILE-DB-TYPE.INIT\nSTART".encode()).hex() if self.__obf else "BOOSQL-FILE-DB-TYPE.INIT\nSTART")
                db.close()
            self._manager.read_file()
        except:
            self.uef.display()

    def open_file(self):
        try:
            with open(self.path, 'r', encoding='cp037') as db:
                result = b85decode(bytes.fromhex(db.read()).decode()).decode() if self.__obf else db.read()
                db.close()
            return result
        except:
            self.invalid_path.display()
    
    def write(self, string):
        try:
            with open(self.path, 'w', encoding='cp037') as db:
                db.write(b85encode(string.encode()).hex() if self.__obf else string)
                db.close()
        except:
            self.uef.display()
    
    def allow_manage(self):
        self._manager.allowed = True
        self._manager.path = self.path
    
    def disallow_manage(self):
        self._manager.allowed = False
        self._manager.path = ""