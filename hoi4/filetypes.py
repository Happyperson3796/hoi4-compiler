from .filetype import fileType
from . import focus, achievements, nation, merge_file, flag, pull_file, state, append_file
import os

def clean_suffix(path):
    return str(path).replace("\\","/").replace("//","/").removesuffix("/").removesuffix("/").removeprefix("/").removeprefix("/").strip()

def get(path: str):
    if path.endswith(".pull"):
        return pull_file.Pulled(path)
    elif path.endswith(".focus"):
        return focus.Focus(path)
    elif path.endswith(".achievement"):
        return achievements.Achievement(path)
    elif path.endswith(".nation"):
        return nation.Nation(path)
    elif path.endswith(".state"):
        return state.State(path)
    elif path.endswith(".merge"):
        return merge_file.Merged(path)
    elif path.endswith(".append"):
        return append_file.Appended(path)
    elif path.endswith(".flag.tga"):
        return flag.Flag(path)
    else:
        return fileType(path)

def should_run(path: str):
    file = get(path)
    if type(file) == fileType:
        return False
    
    head, tail = os.path.split(path)
    
    if len(file.required_dir()) > 0: #Directory Requirements (Ex: must be in /countries/)
        cont = False
        for d in file.required_dir():
            if clean_suffix(head).endswith(clean_suffix(d)):
                cont = True
                break
        if not cont:
            file.required_dir_error()
            return False
        
    if len(file.blocked_dir()) > 0: #Blocked Directories (Ex: must not be in /history/countries/)
        for d in file.blocked_dir():
            if clean_suffix(head).endswith(clean_suffix(d)):
                file.blocked_dir_error()
                return False

    return True