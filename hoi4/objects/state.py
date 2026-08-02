from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection
import os
from ..globals import vanilla_path
import math
from charset_normalizer import from_path

def get_top_state_id(parent_dir):
    top_num = 0
    for path in os.scandir(vanilla_path+"/history/states/"):
        try:
            num = int(path.name.split("-",1)[0].strip())
            if num > top_num: top_num = num
        except: pass

    for path in os.scandir(parent_dir+"/history/states/"):
        try:
            num = int(path.name.split("-",1)[0].strip())
            if num > top_num: top_num = num
        except: pass
    return top_num


postbuild_tree_cache_run = False
postbuild_ids_cache = {}


def get_encoding(path):
    # Fast initial detection
    encoding = from_path(path).best().encoding
    normalized = encoding.lower().replace('-', '_')

    # Most files will hit this and skip the BOM check
    if normalized != 'utf_8':
        return encoding

    # Only check BOM if it's detected as plain utf_8
    with open(path, 'rb') as f:
        if f.read(3).startswith(b'\xef\xbb\xbf'):
            return 'utf_8_sig'

    return encoding


class State(fileType):
    def run(self):
        head, tail = os.path.split(self.path)
        parent_dir = os.path.abspath(os.path.join(head, os.pardir))
        
        with open(self.path, "r", encoding="utf-8") as file:
            data = get(file.read())

        namespace = str(data.get("namespace"))
        full_id = str(data.get("id"))
        name = str(data.get("name")).removeprefix("\"").removesuffix("\"")
        parent = str(data.get("parent")[0])
        provinces = data.get("provinces")

        #print(self.path)

        vanilla_file = ""

        for path in os.scandir(parent_dir+"/history/states/"): #Get file that's already in the mod if possible
            if path.name.split("-",1)[0].strip() == parent:
                vanilla_file = path.path
        
        if vanilla_file == "":
            for path in os.scandir(vanilla_path+"/history/states/"): #Else get from vanilla files
                if path.name.split("-",1)[0].strip() == parent:
                    with open(path.path, "r", encoding="utf-8-sig") as file:
                        tdata = get(file.read())

                    vanilla_file = parent_dir+"/history/states/"+path.name
                    write = open(vanilla_file, "w")
                    write.write(format(tdata))
                    write.close()

        if vanilla_file == "":
            print("Error! Parent state ["+parent+"] not found for "+name)
            exit

        with open(vanilla_file, "r", encoding="utf-8") as file:
            vanilla_data = get(file.read()).get("state")

        infrastructure = 0
        try:
            infrastructure = vanilla_data.get("history").get("buildings").get("infrastructure")
        except: pass
        try:
            infrastructure = data.get("history").get("buildings").get("infrastructure")
        except: pass

        owner = "LIB"
        try:
            owner = vanilla_data.get("history").get("owner")
        except: pass
        try:
            owner = data.get("history").get("owner")
        except: pass

        local_supplies = "0.0"
        try:
            local_supplies = vanilla_data.get("local_supplies")
        except: pass

        state_category = "rural"
        try:
            state_category = vanilla_data.get("state_category")
        except: pass
        try:
            state_category = data.get("state_category")
        except: pass

        num_id = get_top_state_id(parent_dir) + 1

        new_data_collection = get("state={}")
        new_data = new_data_collection[0][-1]

        new_data.append(get("id="+str(num_id))[0])
        new_data.append(get("name=\"STATE_"+str(num_id)+"\"")[0])
        new_data.append(get("manpower=0")[0])
        new_data.append(get("state_category="+str(state_category))[0])
        new_data.append(get("resources={"+format(data.get("resources"))+"}")[0])
        new_data.append(get("history={owner="+str(owner)+"}")[0])
        new_data.append(get("provinces={}")[0])
        new_data.append(get("local_supplies="+str(local_supplies))[0])
        
        try:
            impassable = data.get("impassable")
            new_data.append(get("impassable="+str(impassable))[0])
        except:
            try:
                impassable = vanilla_data.get("impassable")
                new_data.append(get("impassable="+str(impassable))[0])
            except: pass

                
                
        try: #Set buildings & infrastructure... this is useless, cut out and replace with text parsing later
            new_data.get("history").get("buildings").get("infrastructure").set(str(infrastructure))
        except:
            try:
                new_data.get("history").get("buildings").append(get("infrastructure="+str(infrastructure))[0])
            except:
                new_data.get("history").append(get("buildings={infrastructure="+str(infrastructure)+"}")[0])


        old_province_total = len(vanilla_data.get("provinces"))
        shared_provinces = []

        for prov in [c for c in provinces]: #Check for provinces shared by old and new states
            for baseprov in vanilla_data.get("provinces"):
                if str(prov).strip() == str(baseprov).strip():
                    shared_provinces.append(int(str(prov).strip()))
                    new_data.get("provinces").append(baseprov)
                    vanilla_data.get("provinces").remove(baseprov)

        for prov in [c for c in provinces]:
            if int(str(prov).strip()) not in shared_provinces:
                new_data.get("provinces").append(prov)

        old_vps = 0
        new_vps = 0

        for pair in [c for c in vanilla_data.get("history")]: #Move VP mappings over
            if str(pair[0]).strip() == "victory_points":
                vp, pts = pair[-1]
                if int(str(vp).strip()) in shared_provinces:
                    new_data.get("history").append(pair)
                    vanilla_data.get("history").remove(pair)
                    new_vps += int(str(pts).removesuffix(".0"))
                else:
                    old_vps += int(str(pts).removesuffix(".0"))

        try:
            for pair in [c for c in vanilla_data.get("history").get("buildings")]: #Move Province Buildings Over
                try:
                    if int(str(pair[0]).strip()) in shared_provinces:
                        new_data.get("history").get("buildings").append(pair)
                        vanilla_data.get("history").get("buildings").remove(pair)
                except: pass
        except: pass
                

        state_size_ratio = len(shared_provinces)/old_province_total #Land Percentages
        state_pop_ratio = (new_vps-old_vps)/100 #Ratio of new to old VPs

        state_resource_ratio = state_size_ratio #Calc amt of stuff (resources) a province should keep
        state_manpower_ratio = min(max(state_size_ratio+(state_pop_ratio*1.25), 0.025), 0.975) #Calc amt of stuff (manpower) a province should keep

        #if "Ohio" in name:
        #    print(str(round(state_resource_ratio*100,2))+"%")
        #    print(str(round(state_manpower_ratio*100,2))+"%")

        try:
            for r in vanilla_data.get("resources"): #Merge up the resources
                res, s, amt = r

                new_amt = str(math.ceil(int(str(amt))*state_resource_ratio))

                try:
                    val = new_data.get("resources").get(res)
                    val.set(int(str(val))+int(new_amt))
                except:
                    new_data.get("resources").append(get(str(res)+str(s)+new_amt)[0])

                amt.set(max(math.ceil(int(str(amt))*(1-state_resource_ratio)),0))
        except: pass


        for pair in vanilla_data.get("history"): #Copy over extra history={} content like cores, demilitarized zones
            if pair[0] != "victory_points" and pair[0] != "owner" and pair[0] != "buildings":
                new_data.get("history").append(get(format(pair))[0])

        n = -1 #Move dynamic modifiers to top so forts etc. don't bug out
        for x in new_data.get("history"):
            n += 1
            if x[0] == "add_dynamic_modifier":
                new_data.get("history").insert(1, new_data.get("history").pop(n))
                n -= 1

        manpower_ratio_muliplier = 1
        try:
            manpower_ratio_muliplier = float(str(data.get("manpower_ratio_mult")))
        except: pass

        manpower = vanilla_data.get("manpower") #Distribute manpower
        new_data.get("manpower").set(max(math.ceil(int(str(manpower))*(state_manpower_ratio*manpower_ratio_muliplier)),0))
        manpower.set(max(math.ceil(int(str(manpower))*(1-(state_manpower_ratio*manpower_ratio_muliplier))),0))

        transfer_all_dockyards = False
        try:
            transfer_all_dockyards = str(data.get("transfer_all_dockyards")) == "yes"
        except: pass

        for b in ["industrial_complex", "arms_factory"]: #Split up factories to new states
            try:
                building = vanilla_data.get("history").get("buildings").get(b)
                r = max(min(state_resource_ratio, 1), 0)
                amt = round(int(str(building).strip()) * r)

                if amt > 0:
                    try:
                        nb = new_data.get("history").get("buildings").get(b)
                        nb.set(int(str(nb))+amt)
                    except:
                        new_data.get("history").get("buildings").append(get(b+"="+str(amt))[0])

                    building.set(int(str(building))-amt)
                    if int(str(building))-amt <= 0:
                        buildings.remove(buildings.get_pair(b))

            except: pass

        if transfer_all_dockyards:
            for b in ["dockyard"]:
                try:
                    buildings = vanilla_data.get("history").get("buildings")
                    building = buildings.get(b)
                    r = max(min(state_resource_ratio, 1), 0)
                    r = 1
                    amt = round(int(str(building).strip()) * r)

                    if amt > 0:
                        try:
                            nb = new_data.get("history").get("buildings").get(b)
                            nb.set(int(str(nb))+amt)
                        except:
                            new_data.get("history").get("buildings").append(get(b+"="+str(amt))[0])

                        building.set(int(str(building))-amt)
                        if int(str(building))-amt <= 0:
                            buildings.remove(buildings.get_pair(b))

                except: pass

        for pair in data.get("history"): #Append custom history={} block contents
            if pair[0] != "owner":
                try:
                    if pair[0] == "add_core_of": raise
                    new_data.get("history").get(pair[0]).set(pair[-1])
                except: 
                    new_data.get("history").append(pair)

        new_data.get("history").append("set_variable = { var = state_event_parent value = "+str(parent)+" }")

        #Write to file
        with open(parent_dir+"/history/states/"+str(num_id)+"-"+full_id.capitalize()+".txt", "w") as file:
            file.write("#Parent: "+str(parent)+"\n"+"#ID: "+str(full_id)+"\n"+format(new_data_collection))

        with open(vanilla_file, "w") as file:
            file.write(format(get("state="+str(vanilla_data))))

        locfile = parent_dir+"/localisation/"+namespace+"_generated_state_names_loc_l_english.yml"
        if not os.path.exists(locfile):
            with open(locfile, "w", encoding="utf-8-sig") as file:
                file.write("l_english: ")
        with open(locfile, "a", encoding="utf-8-sig") as file:
            file.write("\n STATE_"+str(num_id)+": \""+name+"\"")
            

        try:
            with open(parent_dir+"/common/on_actions/"+namespace+"_dynamic_state_on_actions.txt", "r") as file:
                template = file.read()
                if template == "":
                    raise Exception
        except:
            template = """
#Want to block dynamic transfer? Set the "bdt" flag for either state.

on_actions = {

    on_startup = {
        effect = {
            every_state = {
                set_variable = { prev_owner = OWNER }
            }
        }
    }

    on_state_control_changed = {
        effect = {
            FROM.FROM = {
                if = {
                    limit = {
                        NOT = { has_state_flag = bdt }
                        NOT = {
                            check_variable = { prev_owner = OWNER } 
                        }
                    }
                    # Event for state ownership change
                    #<states>
                    
                    #</states>
                    # Update the stored owner
                    set_variable = { prev_owner = OWNER }
                }

            }
        }
    }

    on_monthly = {
        effect = {
            #<every>

            #/every>
        }
    }

    on_monthly = {
        effect = {
            if = {
                limit = {
                    NOT = {
                        has_global_flag = compiler_per_states_fired_monthly_tick
                    }
                }
                set_global_flag = {
                    flag = compiler_per_states_fired_monthly_tick
                    days = 1
                    value = 1
                }
                #<monthly>

                #/monthly>
            }
        }
    }

}
"""

        with open(parent_dir+"/common/on_actions/"+namespace+"_dynamic_state_on_actions.txt", "w") as file:
            state_template = f"""<states>

                    if = {{
                        limit = {{
                            state = {parent}
                            {num_id} = {{
                                NOT = {{ has_state_flag = bdt }}
                                OWNER = {{
                                    check_variable = {{ PREV.PREV.prev_owner = THIS }}
                                }}
                            }}
                        }}
                        {num_id} = {{ transfer_state_to = {parent}.OWNER }}
                    }}"""
            
            contested_state_template = f"""<contested>

                    if = {{
                        limit = {{
                            state = {parent}
                            {num_id} = {{
                                check_variable = {{ has_contested_owner = no }}
                                NOT = {{ has_state_flag = bdt }}
                            }}
                        }}
                        {num_id} = {{ transfer_state_to = {parent}.OWNER }}
                    }}"""
            
            monthly_state_template = f"""<monthly>

                {parent} = {{
                    if = {{
                        limit = {{
                            NOT = {{ has_state_flag = bdt }}
                            {num_id} = {{ NOT = {{ has_state_flag = bdt }} }}
                        }}
                        if = {{
                            limit = {{ is_demilitarized_zone = yes }}
                            {num_id} = {{ set_demilitarized_zone = yes }}
                        }}
                        else_if = {{
                            limit = {{ is_demilitarized_zone = no }}
                            {num_id} = {{ set_demilitarized_zone = no }}
                        }}
                    }}
                }}"""
            
            every_country_template = f"""<every>
            if = {{
                limit = {{
                    {parent} = {{ NOT = {{ has_state_flag = bdt }} }}
                    {num_id} = {{ NOT = {{ has_state_flag = bdt }} }}
                }}
                if = {{
                    limit = {{
                        {parent} = {{ is_core_of = PREV }}
                        {num_id} = {{ NOT = {{ is_core_of = PREV }} }}
                    }}
                    {num_id} = {{ add_core_of = PREV }}
                }}
                if = {{
                    limit = {{
                        {parent} = {{ is_claimed_by = PREV }}
                        {num_id} = {{ NOT = {{ is_claimed_by = PREV }} }}
                    }}
                    {num_id} = {{ add_claim_by = PREV }}
                }}
            }}"""

            template = template.replace("<states>", state_template, 1)
            template = template.replace("<contested>", contested_state_template, 1)
            template = template.replace("<monthly>", monthly_state_template, 1)
            template = template.replace("<every>", every_country_template, 1)

            file.write(template)



    def build(self): #Cache all state id conversions for postbuild
        global postbuild_ids_cache
        
        head, tail = os.path.split(self.path)
        parent_dir = os.path.abspath(os.path.join(head, os.pardir))

        with open(self.path, "r", encoding="utf-8") as file:
            data = get(file.read())

        namespace = str(data.get("namespace"))
        full_id = str(data.get("id"))
        name = str(data.get("name")).removeprefix("\"").removesuffix("\"")
        parent = str(data.get("parent")[0])

        for path in os.scandir(parent_dir+"/history/states/"):
            try:
                if path.name.split("-",1)[1].strip().removesuffix(".txt") == full_id.capitalize():
                    num_id = path.name.split("-",1)[0].strip()
            except: pass

        postbuild_ids_cache[full_id] = num_id

    def postbuild(self): #Replace all $ID with state ids
        global postbuild_tree_cache_run
        global postbuild_ids_cache
        
        head, tail = os.path.split(self.path)
        parent_dir = os.path.abspath(os.path.join(head, os.pardir))
        parent_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))

        if not postbuild_tree_cache_run: #Run once for all state files
            postbuild_tree_cache_run = True

            def scan_subdirs(dir):
                for filepath in os.scandir(dir):
                    if filepath.is_dir() and not filepath.path.endswith("build"):
                        scan_subdirs(filepath.path)
                    elif filepath.path.endswith(".txt") or filepath.path.endswith(".yml"):
                        try:
                            write = False
                            with open(filepath.path, "r", encoding="utf-8-sig") as file:
                                text = file.read()
                                if "$" in text:
                                    write = True

                            if write:
                                encoding = get_encoding(filepath.path)

                                for full, num in postbuild_ids_cache.items():
                                    text = text.replace("$"+full, num)
                                with open(filepath.path, "w", encoding=encoding) as file:
                                    file.write(text)
                        except: pass

            scan_subdirs(parent_dir)



    def clean(self):
        head, tail = os.path.split(self.path)
        parent_dir = os.path.abspath(os.path.join(head, os.pardir))
        
        with open(self.path, "r", encoding="utf-8") as file:
            data = get(file.read())

        namespace = str(data.get("namespace"))
        full_id = str(data.get("id"))
        name = str(data.get("name")).removeprefix("\"").removesuffix("\"")
        parent = str(data.get("parent")[0])

        try:
            for path in os.scandir(parent_dir+"/history/states/"):
                if path.name.split("-",1)[0].strip() == parent:
                    os.remove(path.path)
        except: pass

        try:
            for path in os.scandir(parent_dir+"/history/states/"):
                if path.name.split("-",1)[1].strip() == full_id.capitalize()+".txt":
                    os.remove(path.path)
        except: pass

        try:
            os.remove(parent_dir+"/common/on_actions/"+namespace+"_dynamic_state_on_actions.txt")
        except: pass

        try:
            os.remove(parent_dir+"/localisation/"+namespace+"_generated_state_names_loc_l_english.yml")
        except: pass


    def required_dir(self):
        return ["states"]
    def blocked_dir(self):
        return ["history/states"]