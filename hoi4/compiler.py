from . import filetypes
import os
import shutil
import distutils.dir_util
import json
import hashlib
import re
import time
from tqdm import tqdm
import builtins
import requests
import webbrowser

from . import globals
from .objects import hoipy

oprint = builtins.print


def nprint(*args, **kwargs):
    def sanitize(arg):
        return str(arg).replace(os.path.expanduser("~").split("\\")[-1].strip(), "$USER")

    args = [sanitize(arg) for arg in args]
    oprint(*args, **kwargs)


builtins.print = nprint


def scandir(dir):  # Sorted scandir: 1b, 2z, 3a, ab, bz, ca
    if not dir.strip().endswith("states"):
        return os.scandir(dir)

    entries = list(os.scandir(dir))
    entries.sort(
        key=lambda x: (int(re.match(r'\d+', x.name).group()) if re.match(r'\d+', x.name) else float('inf'), x.name))
    return entries


def compute_file_hash(file_path):
    hash_func = hashlib.new("sha256")
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):  # chunks of 8192 bytes
            hash_func.update(chunk)
    return hash_func.hexdigest()


def compute_directory_hash(dir_path):
    sha256 = hashlib.sha256()
    all_files = []
    for root, _, files in os.walk(dir_path):
        for names in files:
            all_files.append(os.path.join(root, names))

    all_files.sort()

    for file_path in all_files:
        if file_path.endswith("build.hoi4") or file_path.endswith("build.hoi"): continue
        relative_path = os.path.relpath(file_path, dir_path)
        sha256.update(relative_path.encode('utf-8'))

        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                sha256.update(chunk)
    return sha256.hexdigest()


def scan(home_dir):
    Scan(home_dir)


class Scan:
    def __init__(self, home_dir):

        self.running_files = 0

        self.home_dir = home_dir
        self.hashes = []
        self.runnable = []

        def rerun():
            self.scan(self.home_dir)
            self.execute()
            if self.running_files > 0:
                self.running_files = 0
                rerun()

        rerun()

    def scan(self, dir):  # Base scan func
        for path in scandir(dir):
            if path.is_dir() and path.name != ".build" and path.name != "Hoi4 modding tools":
                self.scan(path.path)
            elif filetypes.should_run(path.path):
                hash = compute_file_hash(path.path)
                if hash not in self.hashes:
                    self.hashes.append(hash)

                    self.runnable.append(filetypes.get(path.path))
                    self.running_files += 1

    def execute(self):
        bar = tqdm(filetypes.order())
        for o in bar:
            bar.set_description(f"Processing: {o}")
            start = time.time()

            for r in [x for x in self.runnable]:
                if isinstance(r, o):
                    self.runnable.remove(r)
                    r.run()
                    bar.set_postfix_str(str(round(time.time() - start, 1)) + " Seconds")


class Build:
    def __init__(self, mod_path):
        self.mod = mod_path.removesuffix("/").removesuffix("\\")
        globals.mod = self.mod + "\\"
        globals.mod_namespace = self.mod.split("\\")[-1]

        # print("Created a new Build for "+str(self.mod))
        if os.path.exists("build.hoi4"):
            build_config = "build.hoi4"
        else:
            build_config = "build.hoi"
        try:
            with open(build_config, "r") as file:
                self.data = json.load(file)
        except Exception as e:
            print("No build file found")
            print(e)
            self.data = {
                "excludes": [],
                "overrides": ""
            }

        if "run_unsafe" in self.data.keys() and self.data["run_unsafe"]:
            hoipy.hoipy_allowed = True
            print("\033[38;5;208mWarning! Unsafe mode is enabled. Do not copy/paste Python files you don't understand.\033[0m")

        if ("full_cleanup" not in self.data.keys()) or (
                "full_cleanup" in self.data.keys() and self.data["full_cleanup"]):
            for path in os.scandir(self.mod):
                if path.is_dir(): shutil.rmtree(path.path)
                if path.is_file() and "build" not in path.name and "modlist" not in path.name: os.remove(path.path)
            print("Full Cleanup...")

        if os.path.exists(self.mod + "/.build"):
            self.deposit_compiler_files(self.mod, self.mod + "/.build")
            shutil.rmtree(self.mod + "/.build")
        self.clean()

    def collect_compiler_files(self, dir=""):  # Collect to /.build/
        if dir == "": dir = self.mod
        for path in scandir(dir):
            if path.is_dir() and path.name != ".build":
                self.collect_compiler_files(path.path)
            else:
                if filetypes.should_run(path.path):
                    build_path = self.mod + "/.build/" + path.path.removeprefix(self.mod)
                    build_dir = build_path.removesuffix(path.name)

                    os.makedirs(build_dir, exist_ok=True)

                    shutil.copy(path.path, build_path)

                    os.remove(path.path)

    def deposit_compiler_files(self, dest, dir=""):  # Deposit from /.build/
        if dir == "": dir = self.mod

        for path in scandir(dir):
            if path.is_dir():
                self.deposit_compiler_files(dest, path.path)
            else:
                orig_path = dest + "/" + path.path.split("/.build")[-1]
                os.makedirs(os.path.split(orig_path)[0], exist_ok=True)
                shutil.copyfile(path.path, orig_path)
                os.remove(path.path)

    def clean_empty_dirs(self, dir=""):
        if dir == "": dir = self.mod
        for path in scandir(dir):
            if path.is_dir():
                self.clean_empty_dirs(path.path)

        if len(os.listdir(dir)) == 0:
            os.rmdir(dir)

    def clean(self, dir=""):
        if dir == "": dir = self.mod
        for path in scandir(dir):
            if path.is_dir() and path.name != ".build":
                self.clean(path.path)
            else:
                if filetypes.should_run(path.path):
                    obj = filetypes.get(path.path)
                    obj.clean()
                    if obj.tmp: os.remove(obj.path)

    def exclude(self, text):
        if text in self.data["excludes"]:
            return True
        elif ".py" in text:
            return True
        elif ".pyr" in text:
            return True
        elif ".git" in text:
            return True
        elif len(text) > 0 and text[0] == "#":
            return True
        else:
            return False

    def apply_overrides(self):
        head, tail = os.path.split(self.mod)

        overrides = []
        for file in scandir(self.data["overrides"].replace("$USER", os.path.expanduser("~")).replace("/", "\\")):
            if file.is_dir():
                if file.name.startswith(tail + "_overrides"):
                    overrides.append(file.path)
        overrides.sort(reverse=True)

        print("Applying overrides for " + tail)

        for override in overrides:
            print("Applying " + override + "...")
            for file in scandir(override):
                if not self.exclude(file.name):
                    if file.is_file():
                        shutil.copyfile(file.path, self.mod + "/" + file.name)
                    else:
                        distutils.dir_util.copy_tree(file.path, self.mod + "/" + file.name)

            # scan(self.mod, self.parsed_files)

    def build_dependencies(self):
        if "depends" not in self.data.keys(): return

        depends = self.data["depends"]
        for depend in [*depends]:
            if not "\\" in depend and depend.endswith(".json"):
                depends.remove(depend)
                with open(globals.mod+"/"+depend, "r") as file:
                    mods = json.load(file)["mods"]
                for mod in mods:
                    text = globals.vanilla_workshop+mod["steamId"]
                    if mod["enabled"]:
                        depends.append(text)

        for depend in [*depends]:
            if " : " in depend:
                depends.remove(depend)
                id, replacement = depend.split(":", 1)
                for x in range(len(depends)):
                    if depends[x].replace("/", "\\").split("\\")[-1].strip() == id.strip():
                        depends[x] = replacement.strip()

        for depend in depends:
            depend = depend.replace("/", "\\")
            name = depend.split("\\")[-1]

            if "check_outdated" not in self.data.keys() or self.data["check_outdated"]:
                workshop_id = depend.replace("\\", "/").removesuffix("/").split("/")[-1].strip()
                if workshop_id and workshop_id.isdigit():
                    steam_time = get_steam_mod_time(workshop_id)
                    local_time = os.path.getmtime(depend) if os.path.exists(depend) else 0

                    if steam_time > local_time:
                        print(f"\033[91mDependency {name} is OUTDATED\033[0m\033[38;5;208m")
                        steam_url = f"steam://openurl/https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
                        webbrowser.open(steam_url)
                    else:
                        print(f"Dependency {name} is up to date.")

            #print("Building dependency \"" + name + "\"...")
            depend = depend.replace("$USER", os.path.expanduser("~")) + "\\"
            d = ".dependency_" + name

            if os.path.exists(self.mod + "/" + d + "/"): shutil.rmtree(self.mod + "/" + d + "/")

            for file in scandir(depend):
                if not self.exclude(file.name):
                    if file.is_file():
                        target_dir = self.mod + "/" + d
                        os.makedirs(target_dir, exist_ok=True)
                        shutil.copyfile(file.path, target_dir + "/" + file.name)
                    elif file.is_dir():
                        distutils.dir_util.copy_tree(file.path, self.mod + "/" + d + "/" + file.name)

            if os.path.exists(self.mod + "/" + d + "/.build"):
                print("Unpacking dependency \"" + name + "\"...")
                self.deposit_compiler_files(self.mod + "/" + d, self.mod + "/" + d + "/.build")
                shutil.rmtree(self.mod + "/" + d + "/.build")

            #print("Cleaning dependency \"" + name + "\"...")
            self.clean(self.mod + "/" + d)

            print("Applying dependency \"" + name + "\"...")
            for file in scandir(self.mod + "/" + d):
                if not file.is_file():
                    distutils.dir_util.copy_tree(file.path, self.mod + "/" + file.name)

            shutil.rmtree(self.mod + "/" + d + "/")

    def fire_build_scripts(self, dir="", mode=0):
        scripts = []

        if dir == "": dir = self.mod
        for path in scandir(dir):
            if path.is_dir():
                self.fire_build_scripts(path.path, mode=mode)
            elif filetypes.should_run(path.path):
                file = filetypes.get(path.path)
                scripts.append(file)

        if mode == -1:
            [file.prebuild() for file in scripts]
        elif mode == 0:
            [file.build() for file in scripts]
        elif mode == 1:
            [file.postbuild() for file in scripts]

    def build(self):
        self.build_dependencies()
        print()

        self.apply_overrides()

        if os.path.exists(globals.mod + "/descriptor.modfile"):
            os.rename(globals.mod + "/descriptor.modfile", globals.mod + "/descriptor.mod")
            print("Unpacked Modfile...")

        start = time.time()

        print("Prebuild scripts...")
        self.fire_build_scripts("", -1)

        print("Running files...")
        scan(self.mod)

        print("Build scripts...")
        self.fire_build_scripts("", 0)

        print("Cleaning build files...")
        self.collect_compiler_files()

        print("Postbuild scripts...")
        self.fire_build_scripts("", 1)

        print("Finished build in " + str(round(time.time() - start, 1)) + " Seconds")

        # print("Cleaning empty dirs...")
        self.clean_empty_dirs()

        print("Build Hash: " + compute_directory_hash(globals.mod)[:5])


def get_steam_mod_time(item_id):
    """Fetches the last update timestamp from Steam."""
    url = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
    data = {'itemcount': 1, 'publishedfileids[0]': item_id}
    try:
        r = requests.post(url, data=data, timeout=10)
        r.raise_for_status()
        details = r.json()['response']['publishedfiledetails'][0]
        return int(details.get('time_updated', 0))
    except Exception as e:
        print(f"Could not check Steam for ID {item_id}: {e}")
        return 0