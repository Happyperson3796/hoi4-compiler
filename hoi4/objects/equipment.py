from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection
import os
from ..filetypes import fileType
import PIL

class Equipment(fileType):
    def run(self):
        head, tail = os.path.split(self.path)

        os.makedirs("common/units/equipment", exist_ok=True)

        with open(self.path, "r") as file:
            data = get(file.read())[0]
        
            id = data[0]
            data: Collection = data[-1].val()

        namespace = data.extract("namespace")

        equipment_file = "common/units/equipment/"+namespace+"_generated_equipment.txt"
        if os.path.exists(equipment_file):
            pass

        

    def clean(self):
        head, tail = os.path.split(self.path)

        with open(self.path, "r") as file:
            data = get(file.read())[0]
        
            id = data[0]
            data: Collection = data[-1].val()

        namespace = data.extract("namespace")

        try:
            os.remove("common/units/equipment/"+namespace+"_generated_equipment.txt")
        except: pass


    def required_dir(self):
        return ["equipment"]
    def blocked_dir(self):
        return ["common/equipment"]