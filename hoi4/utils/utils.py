import os
from .. import globals
from ..pdxscript import get, format, Pair, Collection
from ..objects import pull_file
import re

cached_region_files = {}
region_cache = {}
province_region_cache = {}

def find_strat_region(province: int) -> int:
    if province in province_region_cache.keys():
        return province_region_cache[province]

    if len(cached_region_files) == 0:
        os.makedirs(globals.mod+"map/strategicregions", exist_ok=True)

        for path in os.scandir(globals.vanilla_path+"map/strategicregions"):
            if path.is_file() and path.name.endswith(".txt"):
                id = int(path.name.split("-")[0].strip())
                with open(path.path, "r") as file:
                    cached_region_files[id] = [str(x).strip() for x in get(file.read()).get("strategic_region").get("provinces")]

        for path in os.scandir(globals.mod+"map/strategicregions"):
            if path.is_file() and path.name.endswith(".txt"):
                id = int(path.name.split("-")[0].strip())
                with open(path.path, "r") as file:
                    cached_region_files[id] = [str(x).strip() for x in get(file.read()).get("strategic_region").get("provinces")]

    for id, region in cached_region_files.items():
        for prov in region:
            if prov == str(province):
                province_region_cache[province] = id
                break

    return province_region_cache[province]

def pull_strat_region(region: int) -> str:
    if region < 0: return

    if region in region_cache.keys():
        return region_cache[region]

    for path in os.scandir(globals.vanilla_path+"map/strategicregions"):
        if path.is_file() and path.name.endswith(".txt"):
            id = int(path.name.split("-")[0].strip())
            if id == region:
                base_file = "map/strategicregions/"+path.name
                dest_file = path.name

                pull_file.Pulled.execute(globals.mod+"map/strategicregions/", base_file, dest_file)
                region_cache[region] = globals.mod+"map/strategicregions/"+dest_file
                break

    return region_cache[region]

def add_to_strat_region(region: int, province: int):
    with open(pull_strat_region(region), "r") as file:
        data = get(file.read())
        data.get("strategic_region").get("provinces").append(str(province))

    with open(pull_strat_region(region), "w") as file:
        file.write(format(data))

def remove_from_strat_region(region: int, province: int):
    with open(pull_strat_region(region), "r") as file:
        data = get(file.read())
        data.get("strategic_region").get("provinces").remove_value(str(province))

    with open(pull_strat_region(region), "w") as file:
        file.write(format(data))

