from .exceptions.failedparse import FailedParseException

class Parser:
    def __init__(self, initer):
        self.initer = initer
    
    def __parse_all__(self):
        db = self.initer.open_file()
        
        workspaced = False
        items = []
        wname = ""

        for line in db.split("\n"):
            if line.startswith("OBJ::TYPE=WORKSPACE::NAME="):
                workspaced = True
                wname = line.split("NAME=")[1]
            elif line.startswith("OBJ::TYPE=ITEM::"):
                items.append(line[16:].replace("[","").replace("]","").replace("'","").replace('"',"").split(", "))
        
        return (workspaced, items, db, wname)