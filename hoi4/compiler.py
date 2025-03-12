from . import filetypes
import os
import shutil
import distutils.dir_util
import json
import hashlib


def compute_file_hash(file_path, algorithm='sha256'):
    """Compute the hash of a file using the specified algorithm."""
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as file:
        # Read the file in chunks of 8192 bytes
        while chunk := file.read(8192):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def sub_scan(dir, parsed_files = []): #Scan all subdirs and files
    running_files = 0

    for path in os.scandir(dir):
        if path.is_dir() and path.name != "build" and path.name != "Hoi4 modding tools":
            running_files += sub_scan(path.path)
        elif filetypes.should_run(path.path):
            if filetypes.should_run(path.path):
                hash = compute_file_hash(path.path)

                if hash not in parsed_files:
                    head, tail = os.path.split(path.path)

                    filetypes.get(path.path).run()
                    running_files += 1

                    parsed_files.append(hash)

    return running_files


def scan(dir, parsed_files = []): #Base scan func
    running_files = sub_scan(dir, parsed_files)

    if running_files > 0:
        scan(dir, parsed_files)




class Build():
    def __init__(self, mod_path):
        self.mod = mod_path.removesuffix("/").removesuffix("\\")

        #print("Created a new Build for "+str(self.mod))

        try:
            with open("build.hoi4", "r") as file:
                self.data = json.load(file)
        except:
            print("No build file found")
            self.data = {
                "excludes": [],
                "overrides": ""
            }

        if os.path.exists(self.mod+"/build"):
            self.deposit_compiler_files(self.mod+"/build")
            shutil.rmtree(self.mod+"/build")
        self.clean()

        self.parsed_files = []

    def collect_compiler_files(self, dir=""):
        if dir == "": dir = self.mod
        for path in os.scandir(dir):
            if path.is_dir() and path.name != "build":
                self.collect_compiler_files(path.path)
            else:
                if filetypes.should_run(path.path):
                    build_path = self.mod+"\\build\\"+path.path.removeprefix(self.mod)
                    build_dir = build_path.removesuffix(path.name)

                    os.makedirs(build_dir, exist_ok=True)

                    shutil.copy(path.path, build_path)
                    
                    os.remove(path.path)

    def deposit_compiler_files(self, dir=""):
        if dir == "": dir = self.mod

        for path in os.scandir(dir):
            if path.is_dir():
                self.deposit_compiler_files(path.path)
            else:
                orig_path = self.mod+"/"+path.path.removeprefix(self.mod+"/build")
                os.makedirs(os.path.split(orig_path)[0], exist_ok=True)
                shutil.copyfile(path.path, orig_path)
                os.remove(path.path)

    def clean_empty_dirs(self, dir=""):
        if dir == "": dir = self.mod
        for path in os.scandir(dir):
            if path.is_dir():
                self.clean_empty_dirs(path.path)

        if len(os.listdir(dir)) == 0:
            os.rmdir(dir)

    def clean(self, dir=""):
        if dir == "": dir = self.mod
        for path in os.scandir(dir):
            if path.is_dir() and path.name != "build":
                self.clean(path.path)
            else:
                if filetypes.should_run(path.path):
                    filetypes.get(path.path).clean()

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
        for file in os.scandir(self.data["overrides"].replace("$USER", os.path.expanduser("~"))):
            if file.is_dir():
                if file.name.startswith(tail+"_overrides"):
                    overrides.append(file.path)
        overrides.sort(reverse=True)

        print("Applying overrides for "+tail)

        for override in overrides:
            print("Applying "+override+"...")
            for file in os.scandir(override):
                if not self.exclude(file.name):
                    if file.is_file():
                        shutil.copyfile(file.path, self.mod+"/"+file.name)
                    else:
                        distutils.dir_util.copy_tree(file.path, self.mod+"/"+file.name)
                    
            #scan(self.mod, self.parsed_files)

    def build(self):
        self.apply_overrides()
        scan(self.mod, self.parsed_files)

        print("Cleaning build files...")
        self.collect_compiler_files()

        print("Cleaning empty dirs...")
        self.clean_empty_dirs()


