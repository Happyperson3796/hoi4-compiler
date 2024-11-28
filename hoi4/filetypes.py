from .filetype import fileType
from . import focus, achievements, nation

def get(path: str):
    if path.endswith(".focus"):
        return focus.Focus(path)
    elif path.endswith(".achievement"):
        return achievements.Achievement(path)
    elif path.endswith(".nation"):
        return nation.Nation(path)
    else:
        return fileType(path)

def should_run(path: str):
    if type(get(path)) == fileType:
        return False
    return True