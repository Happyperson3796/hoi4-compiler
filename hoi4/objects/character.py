from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection, Value
import os
from .. import globals
import shutil

class Character(fileType):
    def run(self):
        head, tail = os.path.split(self.path)
        parent_dir = os.path.abspath(os.path.join(head, os.pardir))
        
        with open(self.path, "r") as file:
            data = get(file.read())

        namespace = str(data.get("namespace"))
        id = str(data.get("id"))

        os.makedirs(parent_dir+"/common/characters/", exist_ok=True)
        os.makedirs(parent_dir+"/interface/", exist_ok=True)
        os.makedirs(parent_dir+"/gfx/leaders/"+namespace, exist_ok=True)
        os.makedirs(parent_dir+"/gfx/interface/ideas/"+namespace, exist_ok=True)
        os.makedirs(parent_dir+"/history/general/", exist_ok=True)
        os.makedirs(parent_dir+"/history/countries/", exist_ok=True)

        small_portrait = True
        try:
            shutil.move(head+"/"+id+"_small.dds", parent_dir+"/gfx/interface/ideas/"+namespace+"/"+id+"_small.dds")
            gfx_path = parent_dir+"/interface/"+namespace+"_generated_ideas.gfx"
            if not os.path.exists(gfx_path):
                with open(gfx_path, "w", encoding="utf-8") as file:
                    file.write("spriteTypes = {}")

            with open(gfx_path, "r", encoding="utf-8") as file:
                gfx = get(file.read())

            gfx[0].value().append(get(f"SpriteType = {{ name = \"GFX_idea_{namespace}_{id}\" texturefile = \"gfx/interface/ideas/{namespace}/{id}_small.dds\" }}")[0])

            with open(gfx_path, "w", encoding="utf-8") as file:
                file.write(format(gfx))
        except FileNotFoundError: small_portrait = False

        large_portrait = True
        try:
            shutil.move(head+"/"+id+".dds", parent_dir+"/gfx/leaders/"+namespace+"/"+id+".dds")
            gfx_path = parent_dir+"/interface/"+namespace+"_generated_leader_portraits.gfx"
            if not os.path.exists(gfx_path):
                with open(gfx_path, "w", encoding="utf-8") as file:
                    file.write("spriteTypes = {}")

            with open(gfx_path, "r", encoding="utf-8") as file:
                gfx = get(file.read())

            gfx[0].value().append(get(f"SpriteType = {{ name = \"GFX_portrait_{namespace}_{id}\" texturefile = \"gfx/leaders/{namespace}/{id}.dds\" }}")[0])

            with open(gfx_path, "w", encoding="utf-8") as file:
                file.write(format(gfx))
        except FileNotFoundError: large_portrait = False



        characters_path = parent_dir+"/common/characters/"+namespace+"_generated.txt"
        if not os.path.exists(characters_path):
            with open(characters_path, "w", encoding="utf-8-sig") as file:
                file.write("characters = {}")

        with open(characters_path, "r", encoding="utf-8-sig") as file:
            characters_full = get(file.read())
            characters = characters_full[0].value()
            characters.append(Pair(id, "=", Value(Collection())))
            characters = characters[-1].value()

        portraits_included = False

        for x in data:
            if x[0] != "namespace" and x[0] != "id":
                if x[0] == "portraits":
                    portraits_included = True
                characters.append(x)

        if not portraits_included:
            portraits = "portraits = {"

            if large_portrait and small_portrait:
                portraits += f"civilian = {{ large = \"GFX_portrait_{namespace}_{id}\" }}"
                portraits += f"army = {{ large = \"GFX_portrait_{namespace}_{id}\"  small = \"GFX_idea_{namespace}_{id}\" }}"
            elif large_portrait:
                portraits += f"civilian = {{ large = \"GFX_portrait_{namespace}_{id}\" }}"
                portraits += f"army = {{ large = \"GFX_portrait_{namespace}_{id}\" }}"
            elif small_portrait:
                portraits += f"army = {{ small = \"GFX_idea_{namespace}_{id}\" }}"

            characters.append(get(portraits+"}")[0])

        with open(characters_path, "w", encoding="utf-8-sig") as file:
            file.write(format(characters_full))









    def clean(self):
        head, tail = os.path.split(self.path)
        parent_dir = os.path.abspath(os.path.join(head, os.pardir))

        with open(self.path, "r") as file:
            data = get(file.read())

        namespace = str(data.get("namespace"))
        id = str(data.get("id"))

        try:
            os.remove(parent_dir+"/common/characters/"+namespace+"_generated.txt")
        except: pass

        try:
            os.remove(parent_dir+"/interface/"+namespace+"_generated_ideas.gfx")
        except: pass

        try:
            os.remove(parent_dir+"/interface/"+namespace+"_generated_leader_portraits.gfx")
        except: pass

    def required_dir(self):
        return ["characters"]
    def blocked_dir(self):
        return ["common/characters"]