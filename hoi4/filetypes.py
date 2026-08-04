from .objects import achievements, append_file, character, equipment, flag, focus, focus_icon, formable, merge_file, nation, pull_file, state, state_patch, subideology, hoipy, submerge, event
from .objects.filetype import fileType
import os

def clean_suffix(path):
    return str(path).replace("\\","/").replace("//","/").removesuffix("/").removesuffix("/").removeprefix("/").removeprefix("/").strip()

def endswith(path: str, suffix: str):
    return path.endswith(suffix) or path.endswith(suffix+"_temp")

def get(path: str):
    if endswith(path, ".pull"):
        return pull_file.Pulled(path)
    elif endswith(path, ".focus"):
        return focus.Focus(path)
    elif endswith(path, ".event"):
        return event.Event(path)
    elif endswith(path, ".achievement"):
        return achievements.Achievement(path)
    elif endswith(path, ".nation"):
        return nation.Nation(path)
    elif endswith(path, ".state_patch"):
        return state_patch.StatePatch(path)
    elif endswith(path, ".state"):
        return state.State(path)
    elif endswith(path, ".formable"):
        return formable.Formable(path)
    elif endswith(path, ".formable.json"):
        return formable.JsonFormable(path)
    elif endswith(path, ".character"):
        return character.Character(path)
    elif endswith(path, ".subideology"):
        return subideology.Subideology(path)
    elif endswith(path, ".equipment"):
        return equipment.Equipment(path)
    elif endswith(path, ".merge"):
        return merge_file.Merged(path)
    elif endswith(path, ".submerge"):
        return submerge.SubMerged(path)
    elif endswith(path, ".append"):
        return append_file.Appended(path)
    elif endswith(path, ".flag.tga"):
        return flag.Flag(path)
    elif endswith(path, ".focus.dds"):
        return focus_icon.FocusIcon(path)
    elif endswith(path, ".hoipy"):
        return hoipy.HoiPy(path)
    else:
        return fileType(path)
    
def order():
    return [
        pull_file.Pulled,
        focus.Focus,
        event.Event,
        achievements.Achievement,
        nation.Nation,
        state_patch.StatePatch,
        state.State,
        formable.Formable,
        formable.JsonFormable,
        character.Character,
        subideology.Subideology,
        equipment.Equipment,
        merge_file.Merged,
        submerge.SubMerged,
        append_file.Appended,
        flag.Flag,
        focus_icon.FocusIcon,
        hoipy.HoiPy,
        fileType
    ]

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