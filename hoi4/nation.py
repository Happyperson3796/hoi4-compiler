from .filetype import fileType
from .pdxscript import get, format, Pair, Collection
import os
from .filetypes import fileType
import json

class Nation(fileType):
    def run(self):
        head, tail = os.path.split(self.path)
        
        with open(self.path, "r") as file:
            data = json.load(file)

        



    def clean(self):
        head, tail = os.path.split(self.path)
