from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection, Value
import os
from .. import globals
from .embeddable import Embeddable
from ..utils.file_utils import Gfx

class Project(Embeddable):
    def get_embeddable(self):
        return {"name": "$ROOT", "desc": "$ROOT_desc"}

    def run_sp(self, group, id, data):
        type = str(data.get_pop("type"))
        cost = str(data.get_pop("cost"))

        data.append(Pair("specialization","=","specialization_"+type))

        data.append(Pair("breakthrough_cost","=",Collection(Pair("specialization_land","=",cost))))

        text = """
        allowed = { has_dlc = "Gotterdammerung" }
        generic_prototype_rewards = {
        	sp_land_generic_reward_scientist_xp_1
        	sp_land_generic_reward_scientist_xp_2
        	sp_land_generic_reward_scientist_xp_3
        	sp_land_generic_reward_army_xp_1
        	sp_land_generic_reward_army_xp_2
        	sp_land_generic_reward_army_xp_3
        	sp_land_generic_reward_major_progress_1
        	sp_land_generic_reward_major_progress_2
        	sp_land_generic_reward_major_progress_3
        	sp_land_generic_reward_test_failure_1
        	sp_land_generic_reward_test_failure_2
        	sp_land_generic_reward_test_failure_3
        	sp_land_generic_reward_resource_scarcity
        }""".replace("land", type)

        data.extend(get(text))

        Gfx(self.path, "GFX_"+id, "special_project/project_icons/"+id+".dds", group)

        return data

    def run(self):
        head, tail = os.path.split(self.path)
        locfile = "generated_special_project_"+tail.split(".")[0]
        with open(self.path, "r") as file:
            data = get(file.read())
        super().run(data, locfile, self.get_embeddable())

        projects = {}

        for sp in data:
            projects[sp[0]] = self.run_sp(tail.split(".")[0]+"_special_projects", sp[0], sp[-1])

        os.makedirs(globals.mod+"common/special_projects/projects/", exist_ok=True)
        with open(globals.mod+"common/special_projects/projects/generated_"+tail.split(".")[0]+".txt", "w") as file:
            col = Collection()
            for id, sp in projects.items():
                col.append(Pair(id,"=",sp))
            file.write(format(col))

    def clean(self):
        pass