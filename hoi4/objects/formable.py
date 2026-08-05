from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection, reformat
import os
from .. import globals
import shutil
import json
import colorsys

class Formable(fileType):
    def define(self):
        with open(self.path, "r") as file:
            data = get(file.read())[0]

        id = data[0]
        data = data[-1]

        return id, data

    def run(self):
        head, tail = os.path.split(self.path)
        parent_dir = os.path.abspath(os.path.join(head, os.pardir))

        id, data = self.define()

        namespace = str(data.get("namespace"))

        name = str(data.get("name")).replace("\"", "")
        name_adj = str(data.get("name_adj")).replace("\"", "")
        name_def = str(data.get("name_def")).replace("\"", "")
        extra_loc = data.get("extra_loc", Collection())
        color = data.get("color")
        allowed = data.get("allowed")
        states = data.get("states")
        extras = data.get("extras", Collection())
        claims = data.get("claims", Collection())
        gfx = str(data.get("gfx", "GFX_decision_cat_generic_hre"))
        tier = str(data.get("tier", "1"))
        exclusive = str(data.get("exclusive", "yes"))
        on_formed = data.get("on_formed", Collection())
        extra_reqs = data.get("extra_reqs", Collection())
        alt_req = data.get("alt_req", Collection())
        hist_player = str(data.get("hist_player", "yes"))
        ai = str(data.get("ai", "yes"))
        hist_ai = str(data.get("hist_ai", "no"))

        cosmetic_tag =  str(data.get("cosmetic_tag", "")).replace("\"", "")

        if tier == "0":
            tier_color = "§g"
        elif tier == "1":
            tier_color = "§R"
        elif tier == "2":
            tier_color = "§O"
        elif tier == "3":
            tier_color = "§2"
        elif tier == "4":
            tier_color = "§G"
        elif tier == "5":
            tier_color = "§0"

        else: tier_color = "§R"

        conversion_list = [] #Add any custom states
        if os.path.exists(parent_dir+"/history/states/"):
            for path in os.scandir(parent_dir+"/history/states/"):
                with open(path.path, "r") as file:
                    text = file.readlines()

                if text[0].startswith("#Parent:") and text[1].startswith("#ID:"):
                    parent = text[0].removeprefix("#Parent:").strip()
                    state = path.name.split("-",1)[0].strip()

                    state_id = "$"+text[1].removeprefix("#ID:").strip()

                    conversion_list.append((parent, state, state_id))

        def convert_states(c):
            for state in [x for x in c]:
                if not str(state).startswith("-"):
                    for x, y, z in conversion_list:
                        if x == str(state):
                            c.append(z)

        convert_states(states)
        convert_states(extras)
        convert_states(claims)

        def clean_states(c): #Remove any states marked with -
            for state in [x for x in c]:
                if str(state).startswith("-"):
                    c.remove(state)
                    state = str(state).removeprefix("-")
                    for y in [x for x in c]:
                        if str(y) == state:
                            c.remove(y)

        clean_states(states)
        clean_states(extras)
        clean_states(claims)


        os.makedirs(parent_dir+"/localisation/", exist_ok=True)
        loc_file = parent_dir+"/localisation/"+namespace+"_dynamic_formable_loc_l_english.yml"

        if not os.path.exists(loc_file):
            with open(loc_file, "w", encoding="utf-8-sig") as file:
                file.write("""l_english:
  generic_dynamic_formable_events.1.t:0 "[ROOT.GetNameDefCap]"
  generic_dynamic_formable_events.1.desc:0 "[ROOT.GetOldNameDefCap] has formed [ROOT.GetNameDef]"
  generic_dynamic_formable_events.1.a:0 "Ok"
  controls_highlighted_states:0 "Controls all highlighted states"
  core_highlighted_states:0 "Allows integration for all highlighted states"
  formable_allow_integration:0 "Allows Integration of §H[PREV.GetName]§!"\n\n""")

        with open(loc_file, "a", encoding="utf-8-sig") as file:
            tier_desc = f"\\n\\n{tier_color}Tier {tier} Formable§!"
            if exclusive != "yes": tier_desc = ""

            template = f"""
  formable_{id}_category:0 "Form {name_def}"
  formable_{id}_category_desc:0 "Form {name_def}{tier_desc}"
  formable_view_{id}:0 "View Cores"
  formable_form_{id}:0 "Form {name_def}"
  formable_apply_{id}:0 "Re-Apply Cosmetic"
  {id}_formable_cosmetic:0 "{name}"
  {id}_formable_cosmetic_ADJ:0 "{name_adj}"
  {id}_formable_cosmetic_DEF:0 "{name_def}"
  formable_{id}_core:0 "Integrate [FROM.GetName]"
  formable_{id}_core_desc:0 "Cores [FROM.GetName] once over 50% compliance"
  form_exclusive_nation_tier_{tier}:0 "Has not formed a Tier {tier} Nation"
"""
            
            for x in extra_loc:
                k = str(x[0]).replace("$", id+"_formable_cosmetic")
                v = "\""+str(x[-1]).removeprefix("\"").removesuffix("\"")+"\""
                template += "  "+k+":0 "+v+"\n"

            if exclusive == "yes":
                template += f"  formable_form_{id}_desc:0 \"{tier_color}Tier {tier} Formable§!\"\n"

            file.write(template)


        os.makedirs(parent_dir+"/common/countries/", exist_ok=True)
        cosmetics_file = parent_dir+"/common/countries/"+namespace+"_dynamic_formable_cosmetics.merge_temp"

        if not os.path.exists(cosmetics_file):
            with open(cosmetics_file, "w") as file:
                file.write("#cosmetic.txt\n\n")

        rgb = color
        for x in range(len(rgb)):
            rgb.value[x] = int(str(rgb[x]))

        color = colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])
        color = colorsys.hsv_to_rgb(color[0], color[1]/0.6, color[2]/0.8)
        colors = []
        for x in range(len(color)):
            colors.append(str(round(color[x])))
        color = colors

        with open(cosmetics_file, "a") as file:
            template = id+"_formable_cosmetic = { color = rgb { "+" ".join(color)+" }  color_ui = rgb { "+str(" ".join(color))+" } }\n"
            file.write(template)


        os.makedirs(parent_dir+"/common/decisions/categories/", exist_ok=True)
        categories_file = parent_dir+"/common/decisions/categories/"+namespace+"_formable_categories.txt"

        with open(categories_file, "a") as file:
            template = f"""formable_{id}_category = {{
    icon = generic_formable_nations
    priority = 0
    picture = {gfx}
    allowed = {{}}
}}
"""
            file.write(template)




        os.makedirs(parent_dir+"/common/decisions/", exist_ok=True)
        categories_file = parent_dir+"/common/decisions/"+namespace+"_dynamic_formable_decisions.txt"
        with open(categories_file, "a") as file:

            if ai == "yes": ai_prio = 200
            else: ai_prio = 0

            hist_ai_can_form = f"""
            modifier = {{
                factor = 0
                is_historical_focus_on = yes
            }}"""
            if hist_ai == "yes": hist_ai_can_form = ""

            hist_player_can_form = ""
            if hist_player == "no":
                hist_player_can_form = "is_historical_focus_on = no"

            exclusive_can_form = ""
            exclusive_no_tier_flag = ""
            if exclusive == "yes":
                exclusive_can_form = f"""custom_trigger_tooltip = {{
                tooltip = form_exclusive_nation_tier_{tier}
                hidden_trigger = {{
                    NOT = {{ has_country_flag = form_exclusive_nation_tier_{tier} }}
                }}
            }}
"""
                exclusive_no_tier_flag = f"NOT = {{ has_country_flag = form_exclusive_nation_tier_{tier} }}"



            text = f"""
# $ID
formable_$ID_category = {{
    formable_view_$ID = {{
        on_map_mode = decision_view_only
        icon = generic_form_nation

        allowed = {{
            OR = {{
                original_tag = $TAGS
            }}
        }}

        available = {{
            always = no
        }}

        visible = {{
            OR = {{
                original_tag = $TAGS
            }}
            {exclusive_no_tier_flag}
            NOT = {{ has_global_flag = form_$ID_flag }}
        }}

        highlight_states = {{
            highlight_state_targets = {{
                state = $ADD_CORES
            }}
            highlight_color_while_active = 0
            highlight_color_before_active = 0
        }}

        complete_effect = {{
            effect_tooltip = {{
                $ADD_CORES = {{ PREV = {{ custom_effect_tooltip = formable_allow_integration }} }}
            }}
        }}

        ai_will_do = {{
            factor = 0
        }}
    }}

    formable_form_$ID = {{
        on_map_mode = decision_view_only
        icon = generic_form_nation

        allowed = {{
            OR = {{
                original_tag = $TAGS
                $ALT_REQ
            }}
        }}

        available = {{
            {exclusive_can_form}
            {hist_player_can_form}
            $REQS
            controls_state = $CONTROLS_STATES

        }}

        visible = {{
            OR = {{
                original_tag = $TAGS
            }}
            {exclusive_no_tier_flag}
            NOT = {{ has_global_flag = form_$ID_flag }}
        }}

        highlight_states = {{
            highlight_state_targets = {{
                state = $CONTROLS_STATES
            }}
            highlight_color_while_active = 1
            highlight_color_before_active = 1
        }}

        complete_effect = {{
            $ON_FORMED
            set_cosmetic_tag = $ID_formable_cosmetic
            
            custom_effect_tooltip = core_highlighted_states

            hidden_effect = {{
                add_state_claim = $ADD_CLAIMS
            }}

            hidden_effect = {{
                $ADD_CORES = {{ set_state_flag = $ID_core_state    add_claim_by = ROOT }}
            }}

            hidden_effect = {{
                news_event = {{ id = generic_dynamic_formable_events.1 hours = 6 }}
                set_global_flag = form_$ID_flag
                set_country_flag = form_$ID_flag
                
                $EXCLUSIVE
            }}
        }}

        ai_will_do = {{
            factor = {ai_prio}{hist_ai_can_form}
        }}
    }}

    formable_apply_$ID = {{
        on_map_mode = decision_view_only
        icon = generic_form_nation

        allowed = {{
            OR = {{
                original_tag = $TAGS
            }}
        }}

        available = {{
        }}

        visible = {{
            has_country_flag = form_$ID_flag
            NOT = {{ has_cosmetic_tag = $ID_formable_cosmetic }}
        }}

        complete_effect = {{
            set_cosmetic_tag = $ID_formable_cosmetic
        }}

        ai_will_do = {{
            #factor = 200
            factor = 0
        }}
    }}

    formable_$ID_core = {{
        state_target = any_controlled_state
        visible = {{
            has_country_flag = form_$ID_flag
        }}
        target_trigger = {{
            FROM = {{
                has_state_flag = $ID_core_state
                is_controlled_by = ROOT
                NOT = {{
                    is_core_of = ROOT
                }}
            }}
        }}
        on_map_mode = map_and_decisions_view
        icon = generic_form_nation
        cost = 10
        days_remove = 70
        modifier = {{
            political_power_cost = 0.10
        }}
        remove_effect = {{
            FROM = {{
                if = {{
                    limit = {{ OR = {{ compliance > 50    impassable = yes }} }}
                    add_core_of = ROOT
                }}
                else = {{
                    add_compliance = 20
                    if = {{ 
                        limit = {{
                            ROOT = {{ is_ai = yes }}
                        }}
                        add_compliance = 15
                        ROOT = {{ add_political_power = 25 }}
                    }}
                }}
            }}
        }}
        ai_will_do = {{
            factor = 500
        }}
    }}

}}

"""

            if cosmetic_tag != "": text = text.replace("$ID_formable_cosmetic", cosmetic_tag)
            text = text.replace("$ID", id)
            text = text.replace("$GFX", gfx)

            t_exclusive = ""
            if exclusive == "yes":
                t_exclusive = "set_country_flag = form_exclusive_nation_tier_"+tier
            text = text.replace("$EXCLUSIVE", t_exclusive)

            text = text.splitlines()

            extras.extend(states)
            loop = {"TAGS": allowed, "CONTROLS_STATES": states, "ADD_CORES": extras, "ADD_CLAIMS": claims, "ON_FORMED": format(on_formed).split("\n"), "REQS": format(extra_reqs).split("\n"), "ALT_REQ": format(alt_req).split("\n")}
            for ln in range(len(text)):
                for x in loop:
                    temp_list = []
                    if "$"+x in text[ln]:
                        for tag in loop[x]:
                            line = text[ln].replace("$"+x, str(tag))
                            temp_list.append(line)

                        text.pop(ln)
                        text.insert(ln, "\n".join(temp_list))

            text = "\n".join(text)
            file.write(text)



        os.makedirs(parent_dir+"/events/", exist_ok=True)
        generic_events = parent_dir+"/events/"+namespace+"_generic_dynamic_formable_events.txt"

        if not os.path.exists(generic_events):
            with open(generic_events, "w") as file:
                file.write("""add_namespace = generic_dynamic_formable_events

#Generic formable
news_event = {
	id = generic_dynamic_formable_events.1
	title = generic_dynamic_formable_events.1.t
	desc = generic_dynamic_formable_events.1.desc
	picture = GFX_news_event_generic_parliament

	is_triggered_only = yes
	major = yes
	
	option = {
		name = generic_dynamic_formable_events.1.a
		trigger = {}
	}
}""")


    def clean(self):
        head, tail = os.path.split(self.path)
        parent_dir = os.path.abspath(os.path.join(head, os.pardir))

        id, data = self.define()

        namespace = str(data.get("namespace"))

        try:
            os.remove(parent_dir+"/localisation/"+namespace+"_dynamic_formable_loc_l_english.yml")
        except: pass

        try:
            os.remove(parent_dir+"/common/countries/"+namespace+"_dynamic_formable_cosmetics.merge_temp")
        except: pass

        try:
            os.remove(parent_dir+"/common/decisions/categories/"+namespace+"_formable_categories.txt")
        except: pass

        try:
            os.remove(parent_dir+"/common/decisions/"+namespace+"_dynamic_formable_decisions.txt")
        except: pass

        try:
            os.remove(parent_dir+"/events/"+namespace+"_generic_dynamic_formable_events.txt")
        except: pass


    def required_dir(self):
        return ["formables"]
    def blocked_dir(self):
        return ["common/formables"]



class JsonFormable(Formable):
    def define(self):
        file = open(self.path, "r")
        data = json.loads(file.read())
        file.close()

        temp = {}
        for k in data.keys(): #Not case sensitive
            temp[k.lower()] = data[k]
        data = temp

        data["color"] = data["color"].removeprefix("rgb(").removesuffix(")").strip().replace(",", " ").replace("  ", " ").split(" ")

        data = reformat(data)

        for x in ["on_formed", "extra_reqs", "alt_req"]: #Unrwap json strings into pdxscript
            try:
                var = data.get(x)
                var.set(get("0 = {"+str(var).removeprefix("\"").removesuffix("\"")+"}")[0][-1])
            except: pass

        id = str(data.get("id"))
        data.remove(data.get_pair("id"))

        return id, data