from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection
from ..objects import pull_file
from .. import globals
import os
from ..utils import file_utils
from ..utils import utils

postbuild_tree_cache_run = False
postbuild_ids_cache = {}
victory_point_gen = {}
highest = 0
added = 0

class Provinces(fileType):
    def run(self):
        with open(self.path, "r") as file:
            data = get(file.read())

        head, tail = os.path.split(self.path)

        id = str(data.get("id")).strip()

        provinces = data.get_pop("provinces")
        unsorted = len(provinces) > 0 and provinces[0][0] == "rgb"

        if unsorted:
            provinces_data = provinces
            provinces = Collection()
            for x in range(len(provinces_data)):
                provinces.append(Pair(str(x+1),"=",Collection(provinces_data[x])))

        for province in provinces:
            prefix = province[0]
            province = province[-1]
            for pair in data:
                has = False
                for x in province:
                    if x[0] == pair[0]:
                        has = True
                        break
                if not has:
                    province.append(pair)
            new_id = id+"_"+prefix
            province.get("id").set(new_id)

            with open(head+"/generated_"+new_id+".province", "w") as file:
                file.write(format(province))

    def clean(self):
        pass

generated_vp_file = False

class Province(fileType):
    def run(self):
        global postbuild_ids_cache
        global highest
        global added
        global victory_point_gen
        head, tail = os.path.split(self.path)
        head = "/".join(head.split("\\")[:-1])

        base_file = "map/definition.csv"
        dest_file = "definition.csv"

        pull_file.Pulled.execute(head, base_file, dest_file)

        with open(self.path, "r") as file:
            data = get(file.read())

        rgb = data.get("rgb")

        this = rgb[0]+";"+rgb[1]+";"+rgb[2]+";"+data.get("type")+";"+str(data.get("coastal").bool()).lower()+";"+data.get("terrain")+";"+data.get("continent")

        new_id = 0
        if highest == 0:
            with open(head+"/"+dest_file, "r") as file:
                text = file.read()
                for line in text.splitlines():
                    id = int(line.split(";")[0])
                    if ";" in line and not line.strip().startswith("#"):
                        if id > highest:
                            highest = id

        added += 1
        new_id = highest + added

        with open(head+"/"+dest_file, "r") as file:
            text = file.read()
            for line in text.splitlines():
                id = int(line.split(";")[0])
                if this in line:
                    new_id = id
                    break

        postbuild_ids_cache[str(data.get("id")).strip()] = new_id

        vp = data.get("vp", 0).int()
        if vp != 0: victory_point_gen[new_id] = vp

        if this not in text:
            with open(head+"/"+dest_file, "a") as file:
                file.write("\n"+str(new_id)+";"+this)

        name = data.get("name", "").unquote()
        if not name == "":
            locfile = globals.mod+"/localisation/"+globals.mod_namespace+"_generated_province_names_loc_l_english.yml"
            if not os.path.exists(locfile):
                with open(locfile, "w", encoding="utf-8-sig") as file:
                    file.write("l_english: ")
            with open(locfile, "a", encoding="utf-8-sig") as file:
                file.write("\n  VICTORY_POINTS_"+str(new_id)+": \""+name+"\"")

        region = data.get("region").int()
        if region >= 0:
            utils.add_to_strat_region(region, new_id)

    def build(self):
        global generated_vp_file
        if not generated_vp_file:
            generated_vp_file = True

            text = ""
            for id, vp in victory_point_gen.items():
                text += f"\n    set_victory_points = {{ province = {id}    value = {vp} }}"

            if text != "":
                with open(globals.mod+"common/on_actions/generated_province_victory_points_"+globals.mod_namespace+".txt", "w") as file:
                    file.write("on_actions = { on_startup = { effect = { "+text+"\n} } }")

    def finalbuild(self): #Replace all $ID with province ids
        global postbuild_tree_cache_run
        global postbuild_ids_cache
        
        head, tail = os.path.split(self.path)

        if not postbuild_tree_cache_run: #Run once for all province files
            postbuild_tree_cache_run = True

            def scan_subdirs(dir):
                for filepath in os.scandir(dir):
                    if filepath.is_dir() and not filepath.path.endswith("build"):
                        scan_subdirs(filepath.path)
                    elif filepath.path.endswith(".txt") or filepath.path.endswith(".yml") or filepath.path.endswith(".csv"):
                        try:
                            write = False
                            with open(filepath.path, "r", encoding="utf-8-sig") as file:
                                text = file.read()
                                if "$" in text:
                                    write = True

                            if write:
                                encoding = file_utils.get_encoding(filepath.path)

                                for full, num in postbuild_ids_cache.items():
                                    text = text.replace("$"+full, str(num))
                                with open(filepath.path, "w", encoding=encoding) as file:
                                    file.write(text)
                        except: pass

            scan_subdirs(globals.mod)

    def clean(self):
        pass