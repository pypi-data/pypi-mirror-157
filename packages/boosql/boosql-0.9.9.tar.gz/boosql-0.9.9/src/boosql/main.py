from .initializer import Initializer
import sys

class Database:
    def __init__(self, path:str="my_database.db", obfuscate:bool=True):
        self.initer = Initializer("\\".join(sys.argv[0].split("\\")[:-1])+f"\\{path}", obfuscate)
        self.manager = self.initer._manager
    
    def create(self):
        self.initer.create_file()
    
    def open_prepared_workspace(self):
        self.manager.open_workspace()
    
    def create_workspace(self, name):
        self.manager.create_workspace(name)
    
    def _get_items(self):
        return self.manager._items
    
    def get_workspace_name(self):
        return self.manager.__wname
    
    def add_item(self, item:list=[]):
        self.manager.add_item(item)
    
    def get_item(self, index:int=-1):
        if not index == -1:
            return self.manager.get_item(index)
    
    def edit_item(self, index:int=-1, new_item:list=[]):
        if not index == -1:
            return self.manager.replace_item(new_item, index)
    
    def remove_item(self, index:int=-1):
        if not index == -1:
            self.manager.remove_item(index)
    
    def allow_edit(self):
        self.initer.allow_manage()
    
    def disallow_edit(self):
        self.initer.disallow_manage()