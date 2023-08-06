from .parser import Parser
from base64 import *

class Manager:
    def __init__(self, initer):
        self.allowed = False
        self.path = ""
        
        self.initer = initer
        self.parser = Parser(self.initer)
        
        self.__wname = ""
        self.__workspaced = False
        self.__current_db = "BOOSQL-FILE-DB-TYPE.BOOSQL\nSTART BOOSQL-FILE-DB-TYPE.BOOSQL"
        self._items = []
    
    def read_file(self):
        return self.initer.open_file()
    
    def clear_empty_lines(self):
        # This function was created dua empty lines problem. It also fixes big file size, if it have big size.
        pre_processed = self.__current_db.split("\n")
        
        for line in pre_processed:
            if line == "":
                pre_processed.remove("")
                
        self.__current_db = "\n".join(pre_processed)
    
    def replace(self, old_string, new_string):
        if self.allowed:
            self.__current_db = self.__current_db.replace(old_string, new_string)
            self.clear_empty_lines()
            self.initer.write(self.__current_db)
        else:
            print("BooSQL=PermissionsWarning\n Your action can't be executed, because you haven't needed permissions.")
    
    def write(self, string):
        if self.allowed:
            self.__current_db += "\n" + string
            self.initer.write(self.__current_db)
        else:
            print("BooSQL=PermissionsWarning\n Your action can't be executed, because you haven't needed permissions.")
    
    def open_workspace(self):
        parsed = self.parser.__parse_all__()
        self.__current_db = parsed[2]
        self._items = parsed[1]
        self.__workspaced = parsed[0]
    
    def create_workspace(self, name):
        if not self.__workspaced:
            self.__workspaced = True
            self.__wname = name
            self.write(f"OBJ::TYPE=WORKSPACE::NAME={name}")
        else:
            print("BooSQL=WorkspaceWarning\n Your action can't be executed, because you haven't workspace, create it by db.create_workspace()")

    def add_item(self, item):
        if self.__workspaced:
            itemc = list(map(lambda x: b64encode(str(x).encode()).decode(), item))
            itemc.insert(0, b64encode(str(len(self._items)).encode()).decode())
            self._items.append(itemc)
            self.write(f"OBJ::TYPE=ITEM::{self._items[len(self._items)-1]}")
    
    def get_item(self, index):
        return list(map(lambda x: b64decode(x).decode(), self._items[index]))
    
    def replace_item(self, new_item, index):
        if self.__workspaced:
            itemc = list(map(lambda x: b64encode(str(x).encode()).decode(), new_item))
            itemc.insert(0, b64encode(str(index).encode()).decode())
            old_item = self._items[index]
            self._items.remove(self._items[index])
            self._items.insert(index, itemc)
            self.replace(f"OBJ::TYPE=ITEM::{old_item}", f"OBJ::TYPE=ITEM::{self._items[index]}")
    
    def remove_item(self, index):
        if self.__workspaced:
            self._items.remove(self._items[index])
            
            for item in range(index, len(self._items)):
                self._items[item][0] = b64encode(str(int(b64decode(self._items[item][0]).decode())-1).encode()).decode()
            
            self.__current_db = f"BOOSQL-FILE-DB-TYPE.BOOSQL\nSTART BOOSQL-FILE-DB-TYPE.BOOSQL\nOBJ::TYPE=WORKSPACE::NAME={self.__wname}"
            
            for item in self._items:
                self.write(f"OBJ::TYPE=ITEM::{item}")
            
            self.initer.write(self.__current_db)