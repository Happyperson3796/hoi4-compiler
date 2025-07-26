from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection, Value
import os
from .. import globals
import shutil
from pathlib import Path

class StatePatch(fileType):
    def run(self):
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

            provinces = state[-1].val().extract("provinces")
            for prov in provinces:
                if str(prov).startswith("-"):
                    prov.set(prov.val().removeprefix("-"))
                    state_provs = state_data[0][-1].val().extract("provinces")
                    for x in [y for y in state_provs]:
                        if str(x) == str(prov):
                            state_provs.remove(x)

                else:
                    state_provs = state_data[0][-1].val().extract("provinces")
                    state_provs.append(prov)

            state[-1].val().remove(state[-1].val().select("provinces")) #Remove provinces block to avoid merge conflicts if I include that

            history = state_data[0][-1].val().extract("history")

            try: #Add or remove buildings
                for x in state[-1].val().extract("history").extract("buildings"):
                    if x[0].startswith("-"):
                        for y in history.extract("buildings"):
                            if y[0] == x[0].removeprefix("-"):
                                history.extract("buildings").remove(y)

                state[-1].val().extract("history").remove(state[-1].val().extract("history").select("buildings"))
            except: pass

            try: #Victory point addition or removal
                pairs = {}
                for potential_vps in [x for x in state[-1].val().extract("history")]:
                    if isinstance(potential_vps, Pair) and potential_vps[0] == "victory_points":
                        vps = potential_vps[-1].val()
                        for x in range(len(vps)):
                            if x % 2 == 0:
                                pairs[vps[x].val()] = vps[x+1].val()

                        state[-1].val().extract("history").remove(potential_vps)
                            
                
                for potential_vps in history:
                    if isinstance(potential_vps, Pair) and potential_vps[0] == "victory_points":
                        vps = potential_vps[-1].val()
                        for x in range(len(vps)):
                            if x % 2 == 0:
                                vp = vps[x].val()
                                
                                for k in [x for x in pairs.keys()]:
                                    if k.startswith("-") and k.removeprefix("-") == vp:
                                        history.remove(potential_vps)
                                        pairs.pop(k)

                for k in pairs:
                    collection = Collection()
                    collection.append(Value(k))
                    collection.append(Value(pairs[k]))
                    history.append(Pair("victory_points", "=", collection))

            except: pass
            
            #state_data[0][-1].val().merge(state[-1].val()) #Merge remaining values? need .integrate method for recursive merging of Collections

            with open(parent+"/history/states/"+vanilla_state, "w") as file:
                file.write(format(state_data))




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