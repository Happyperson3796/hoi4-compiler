from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection, Value
import os
from .. import globals
import shutil
from pathlib import Path
from ..utils import utils

shifted_provinces = False
potential_province_shifts = {}
complete_province_shifts = []

class StatePatch(fileType):
    def run(self):
        global complete_province_shifts
        global potential_province_shifts
        head, tail = os.path.split(self.path)

        parent = str(Path(head).parent)
        os.makedirs(parent+"/history/states", exist_ok=True)
        
        with open(self.path, "r") as file:
            data = get(file.read())

        for state in data:
            id = state[0]

            for x in os.listdir(globals.vanilla_path+"/history/states/"):
                if x.split("-", 1)[0].strip() == id:
                    vanilla_state = x
                    break

            if not os.path.exists(parent+"/history/states/"+vanilla_state):
                shutil.copyfile(globals.vanilla_path+"/history/states/"+vanilla_state, parent+"/history/states/"+vanilla_state)

            with open(parent+"/history/states/"+vanilla_state, "r") as file:
                state_data = get(file.read())

            provinces = state.value().get("provinces")
            for prov in provinces:
                if str(prov).startswith("-"):
                    prov.set(str(prov).removeprefix("-"))
                    state_provs = state_data[0].value().get("provinces")
                    for x in [y for y in state_provs]:
                        if str(x) == str(prov):
                            potential_province_shifts[prov] = utils.find_strat_region(state_provs[0])
                            state_provs.remove(x)

                else:
                    state_provs = state_data[0].value().get("provinces")
                    complete_province_shifts.append(str(prov))
                    if not str(prov).startswith("$"):
                        utils.add_to_strat_region(utils.find_strat_region(state_provs[0]), prov)
                    state_provs.append(prov)

            state.value().remove(state.value().get_pair("provinces")) #Remove provinces block to avoid merge conflicts if I include that

            history = state_data[0].value().get("history")

            try: #Add or remove buildings
                for x in state.value().get("history").get("buildings"):
                    if str(x[0]).startswith("-"):
                        for y in history.get("buildings"):
                            if y[0] == str(x[0]).removeprefix("-"):
                                history.get("buildings").remove(y)

                state.value().get("history").remove(state.value().get("history").get_pair("buildings"))
            except: pass

            try: #Victory point addition or removal
                pairs = {}
                for potential_vps in [x for x in state.value().get("history")]:
                    if isinstance(potential_vps, Pair) and potential_vps[0] == "victory_points":
                        vps = potential_vps.value()
                        for x in range(len(vps)):
                            if x % 2 == 0:
                                pairs[str(vps[x])] = str(vps[x+1])

                        state.value().get("history").remove(potential_vps)
                            
                
                for potential_vps in history:
                    if isinstance(potential_vps, Pair) and potential_vps[0] == "victory_points":
                        vps = potential_vps.value()
                        for x in range(len(vps)):
                            if x % 2 == 0:
                                vp = str(vps[x])
                                
                                for k in [x for x in pairs.keys()]:
                                    if str(k).startswith("-") and str(k).removeprefix("-") == vp:
                                        history.remove(potential_vps)
                                        pairs.pop(k)

                for k in pairs:
                    collection = Collection()
                    collection.append(Value(k))
                    collection.append(Value(pairs[k]))
                    history.append(Pair("victory_points", "=", collection))

            except: pass
            
            #state_data[0].value().merge(state.value()) #Merge remaining values? need .integrate method for recursive merging of Collections

            with open(parent+"/history/states/"+vanilla_state, "w") as file:
                file.write(format(state_data))

    def postbuild(self):
        global shifted_provinces
        if not shifted_provinces:
            shifted_provinces = True
            for prov, region in potential_province_shifts.items():
                if str(prov) in complete_province_shifts:
                    utils.remove_from_strat_region(region, prov)

    def clean(self):
        head, tail = os.path.split(self.path)

        parent = str(Path(head).parent)
        os.makedirs(parent+"/history/states", exist_ok=True)
        
        with open(self.path, "r") as file:
            data = get(file.read())

        for state in data:
            id = state[0]

            for x in os.listdir(globals.vanilla_path+"/history/states/"):
                if x.split("-", 1)[0].strip() == id:
                    vanilla_state = x
                    break

            try:
                os.remove(parent+"/history/states/"+vanilla_state)
            except: pass


    def required_dir(self):
        return ["states"]
    def blocked_dir(self):
        return ["history/states"]