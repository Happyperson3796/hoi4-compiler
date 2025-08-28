from .pdxscript import get, format, reformat, Pair, Collection, Value

def convert(l: list):
    r = []
    for x in [x.convert() for x in l]:
        if isinstance(x, list): r.extend(x)
        else: r.append(x)
    return r


class Focus():
    def __init__(self, id: str, icon: str, long: bool, *args, **kwargs):
        self.args = [*args]
        self.kwargs = kwargs
        self.id = id
        self.long = long
        self.icon = icon

    def convert(self):
        focus = Collection([Pair("id","=",Value(self.id)), Pair("icon","=",Value(self.icon))])

        if (self.long): focus.append(Pair("cost","=",Value(str(10))))
        else: focus.append(Pair("cost","=",Value(str(5))))

        focus.extend(self.args)

        for k, v in self.kwargs.items(): #Override any presets with kwargs
            focus.set(Pair(k,"=",v))

        return Pair("focus","=",Value(focus))
    
    def get(self, arg: str, default: Pair = Pair()) -> Pair:
        for x in self.args:
            if isinstance(x, Pair) and x[0] == arg:
                return x
        return default
    
    def set(self, set: Pair):
        g = get(set[0])
        if len(g) > 1:
            g[-1].set(set[-1].val())
        else:
            self.args.append(set)


def exclusive(*args: Focus):
    for x in args:
        mutually_exclusive = Collection()
        for y in args:
            mutually_exclusive.append(Pair("focus","=",y.id))
        x.args.append(Pair("mutually_exclusive","=",Value(mutually_exclusive)))

    return [*args]


def branch(parent: Focus, *children: Focus):
    children = [*children]

    y = 0
    prev = None
    for f in children:
        if prev == None or (prev.get("x", Pair("x","=",Value(0)))[-1].val() == 0 and f.get("x", Pair("x","=",Value(0)))[-1].val() == 0):
            y += 1
        f.args.append(Pair("y","=",Value(y)))
        f.args.append(Pair("relative_position_id","=",Value(parent.id)))

        prev = f

    
    return [parent]+children


def split(*focuses: Focus):
    focuses = [*focuses]

    size = 1
    size += len(focuses)*2

    x = int(-size)

    for f in focuses:
        f.set(Pair("x","=",Value(x)))
        x += 2

    return [*focuses]

class FocusTree():
    def __init__(self, *args):
        self.args = [item for x in args for item in (x if isinstance(x, list) else [x])] #Unpack lists

    def convert(self):
        tree = Collection(convert(self.args))

        return tree
    
    def __str__(self):
        return format(self.convert())

test = FocusTree(

    *branch(
        Focus("begin", "gfx", True),

        *split(
            *exclusive(
                Focus("SEATO_Enhanced_Naval_Patrols", "GFX_goal_generic_navy_battleship", True),
                Focus("SEATO_Peacekeeping_Missions", "GFX_goal_generic_navy_battleship", True)
            ),
        ),

        Focus("P", "gfx", True),
        Focus("1", "gfx", True),
        Focus("2", "gfx", True),
        Focus("3", "gfx", True),
        Focus("4", "gfx", True),
        
    )

)

#print(test)
with open("output.txt", "w") as file: file.write(format(get("focus_tree = {"+str(test)+"}")))