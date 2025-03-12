from .filetype import fileType
from . import focus, achievements, nation, merge_file, flag, pull_file

def get(path: str):
    if path.endswith(".pull"):
        return pull_file.Pulled(path)
    elif path.endswith(".focus"):
        return focus.Focus(path)
    elif path.endswith(".achievement"):
        return achievements.Achievement(path)
    elif path.endswith(".nation"):
        return nation.Nation(path)
    elif path.endswith(".merge"):
        return merge_file.Merged(path)
    elif path.endswith(".flag.tga"):
        return flag.Flag(path)
    else:
        return fileType(path)

def should_run(path: str):
    if type(get(path)) == fileType:
        return False
    return True