from .filetype import fileType
from .pdxscript import get, format, Pair, Collection
import os
from .filetypes import fileType

class Achievement(fileType):
    def run(self):
        head, tail = os.path.split(self.path)

        with open(self.path, "r") as file:
            collection = get(file.read())

        filename = collection[0][-1].val()
        unique_id = collection[1]

        name = collection[2]
        desc = collection[3]

        locfile = collection[4][-1].val()

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
                if name[0] in x:
                    append = False
            if append:
                index.append("\n  "+name[0]+" "+name[-1].val()+"\n  "+desc[0]+" "+desc[-1].val()+"\n")
            with open(localisation_dir+locfile+".yml", "w", encoding="utf-8-sig") as file:
                file.writelines(index)



    def clean(self):
        head, tail = os.path.split(self.path)

        with open(self.path, "r") as file:
            collection = get(file.read())
        
        file = collection[0][-1].val()
        filepath = head+"/"+file+".txt"

        if os.path.exists(filepath):
            os.remove(filepath)

        locfile = collection[4][-1].val()
        localisation_dir = "/".join(head.replace("\\","/").split("/")[:-2])+"/localisation/"
        if os.path.exists(localisation_dir+locfile+".yml"):
            os.remove(localisation_dir+locfile+".yml")