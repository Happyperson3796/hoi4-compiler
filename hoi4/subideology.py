from .filetype import fileType
from .pdxscript import get, format, Pair, Collection
import os
from .filetypes import fileType
from . import globals
import shutil

class Subideology(fileType):
    def run(self):
        head, tail = os.path.split(self.path)
        



    def clean(self):
        head, tail = os.path.split(self.path)


