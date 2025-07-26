from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection
import os
from ..filetypes import fileType
import PIL

class Flag(fileType):
    def run(self):
        head, tail = os.path.split(self.path)

        name = tail.replace(".flag.tga", ".tga")
        
        try:
            os.makedirs(head+"/medium")
        except: pass
        try:
            os.makedirs(head+"/small")
        except: pass

        with PIL.Image.open(self.path) as img:

            medium = img.resize((41,26))
            small = img.resize((10,7))

            img.save(head+"/"+name)
            medium.save(head+"/medium/"+name)
            small.save(head+"/small/"+name)


    def clean(self):
        head, tail = os.path.split(self.path)

        name = tail.replace(".flag.tga", ".tga")

        try:
            os.remove(head+"/"+name)
        except: pass
        try:
            os.remove(head+"/medium/"+name)
        except: pass
        try:
            os.remove(head+"/small/"+name)
        except: pass
