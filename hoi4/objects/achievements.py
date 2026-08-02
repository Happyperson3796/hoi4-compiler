from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection
import os

class Achievement(fileType):
    def run(self):
        head, tail = os.path.split(self.path)

        with open(self.path, "r") as file:
            collection = get(file.read())

        filename = str(collection[0].value())
        unique_id = collection[1]

        name = collection[2]
        desc = collection[3]

        locfile = str(collection[4].value())

        achievement = collection[-1]

        filepath = head+"/"+filename+".txt"

        base = Collection()
        base.append(unique_id)

        if os.path.exists(filepath):
            with open(filepath, "r") as file:
                base.merge(get(file.read()))

        with open(filepath, "w") as file:
            achievement_collection = Collection()
            achievement_collection.append(achievement)
            base.merge(achievement_collection)
            file.write(format(base))

        if locfile.strip() != "null" and locfile.strip() != "" and locfile.strip() != "unset":
            localisation_dir = "/".join(head.replace("\\","/").split("/")[:-2])+"/localisation/"
            index = []
            try:
                with open(localisation_dir+locfile+".yml", "r", encoding="utf-8-sig") as file:
                    index = file.readlines()
            except:
                pass
            try:
                index[0] = "l_english:\n"
            except:
                index.append("l_english:\n")
            append = True
            for x in index:
                if str(name[0]) in x:
                    append = False
            if append:
                index.append("\n  "+str(name[0])+" "+str(name.value())+"\n  "+str(desc[0])+" "+str(desc.value())+"\n")
            with open(localisation_dir+locfile+".yml", "w", encoding="utf-8-sig") as file:
                file.writelines(index)



    def clean(self):
        head, tail = os.path.split(self.path)

        with open(self.path, "r") as file:
            collection = get(file.read())
        
        file = str(collection[0].value())
        filepath = head+"/"+file+".txt"

        if os.path.exists(filepath):
            os.remove(filepath)

        locfile = str(collection[4].value())
        localisation_dir = "/".join(head.replace("\\","/").split("/")[:-2])+"/localisation/"
        if os.path.exists(localisation_dir+locfile+".yml"):
            os.remove(localisation_dir+locfile+".yml")