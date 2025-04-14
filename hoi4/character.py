from .filetype import fileType
from .pdxscript import get, format, Pair, Collection
import os
from .filetypes import fileType
from . import globals
import shutil

class Subideology(fileType):
    def run(self):
        head, tail = os.path.split(self.path)
        parent_dir = os.path.abspath(os.path.join(head, os.pardir))
        


    def clean(self):
        head, tail = os.path.split(self.path)
        parent_dir = os.path.abspath(os.path.join(head, os.pardir))



    def required_dir(self):
        return ["characters"]
    def blocked_dir(self):
        return ["common/characters"]