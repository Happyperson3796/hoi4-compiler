
def is_spacing(char):
    return char == " " or char == "\n" or char == "\t" or char == ""

def is_connector(char):
    return char == "=" or char == "<" or char == ">"

def parse(text):
    text += "\n"

    parsed = []
    buffer = ""
    commented = False
    is_quoted = False

    for char in text:
        if char == "\"":
            if is_quoted:
                is_quoted = False
            else:
                is_quoted = True

        if char == "#":
            commented = True
        elif char == "\n":
            commented = False
        if not commented:
            if is_spacing(char) and not is_quoted:
                if buffer != "":
                    parsed.append(buffer)
                buffer = ""
            elif (is_connector(char) or char == "{" or char == "}") and not is_quoted:
                if buffer != "":
                    parsed.append(buffer)
                parsed.append(char)
                buffer = ""
            else:
                buffer += char

    return parsed

class Value():
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    def __repr__(self):
        return str(self.value)

    def get(self, *args):
        return self.value.get(*args)

    def search(self, *args):
        return self.value.search(*args)
    
    def set(self, value):
        if isinstance(self.value, Pair):
            self.value.set(value)
        else:
            self.value = value

    def val(self):
        return self.value

class Collection(list):
    def text(self):
        return "{\n"+"\n".join(map(str, self))+"\n}"

    def __str__(self):
        return self.text()
    def __repr__(self):
        return self.text()
    
    def get(self, search="", debug=False, strict=True, return_pair=False):
        if search == "":
            if isinstance(self[0], Pair):
                return self[0][-1]
            return self[0]

        for x in self.copy():
            check = str(x)
            if isinstance(x, Pair):
                if return_pair:
                    check = x[0]
                else:
                    check = x[0]
                    x = x[-1]

            if debug:
                print(check)

            if (not strict and search in check) or (strict and search == check):
                return x

        raise Exception(("Strict search" if strict else "Search")+" \""+search+"\" not found!")
            
    def search(self, search, debug=False):
        return self.get(search, debug, False)
    
    def retrieve(self, retrieve, default=None):
        """Gets a wrapped value if it exists, otherwise returns default."""
        try:
            return self.get(retrieve, False, True)
        except Exception as e:
            if default != None:
                return default
            else:
                raise e

    def extract(self, retrieve, default=None):
        """Gets and returns unwrapped values."""
        try:
            get = self.get(retrieve, False, True)
            if isinstance(get, Value):
                return get.val()
            else:
                return get
        except Exception as e:
            if default != None:
                return default
            else:
                raise e
                
    def select(self, retrieve, default=None):
        """Gets the entire block, including pair headers. Mainly for .remove()"""
        try:
            return self.get(retrieve, False, True, True)
        except Exception as e:
            if default != None:
                return default
            else:
                raise e
    
    def merge(self, collection, reverse=False):
        this = self

        if len(collection) == 1 and isinstance(collection[0], Pair) and isinstance(collection[0][-1], Value) and isinstance(collection[0][-1].val(), Collection): #Work for grouped collection types like thing = { contents }
            collection = collection[0][-1].val()
            this = self[0][-1].val()

        to_append = Collection()

        for override in collection:
            append = True
            for pair in this:
                if override[0] == pair[0]:
                    append = False
                    pair.set(override[-1])

            if append:
                to_append.append(override)

        if not reverse:
            this.extend(to_append)
        else:
            l = -1
            for x in to_append:
                l += 1
                this.insert(l, x)

    def unwrap(self):
        """Unwrap all Values in the collection"""
        r = Collection()
        for i in [x for x in self]:
            if isinstance(i, Value):
                i = i.val()
            if isinstance(i, Collection):
                i = i.unwrap()

            if isinstance(i, Pair):
                temp = []
                for pn in range(i.size()):
                    if isinstance(i[pn], Value):
                        if isinstance(i[pn].val(), Collection):
                            temp.append(i[pn].val().unwrap())
                        else:
                            temp.append(i[pn].val())
                    else:
                        temp.append(i[pn])
                i = Pair(*temp)

            r.append(i)
        return r

def collect(parsed):
    def collect_value():
        collection = Collection()

        while len(parsed) > 0:
            obj = parsed.pop(0)

            if obj == "}":
                return collection
            
            elif obj == "{":
                collection.append(collect_value())

            else:
                collection.append(obj)

        return collection

    return collect_value()


class Pair():
    holder = []
    def __init__(self, *args):
        self.holder = [*args]

    def text(self):
        return " ".join(map(str, self.holder))

    def __str__(self):
        return self.text()
    def __repr__(self):
        return self.text()
    
    def __getitem__(self, index):
        return self.holder[index]
    
    def __setitem__(self, index, value):
        self.holder[index] = value

    def get(self):
        return self.holder[-1]

    def set(self, value):
        self.holder[-1] = value

    def size(self):
        return len(self.holder)

def merge_pairs(collection):
    merged = Collection()
    while len(collection) > 0:
        x = collection.pop(0)

        if len(collection) > 1 and is_connector(collection[0]):
            if isinstance(collection[1], list):
                collection[1] = merge_pairs(collection[1])
            merged.append(Pair(x, collection.pop(0), Value(collection.pop(0))))
        else:
            merged.append(Value(x))

    return merged


def get(text): #All combined
    return merge_pairs(collect(parse(text)))


def format_compress(text): #Break down odd brackets
    r = ""

    no_newlines = False

    buffer = ""
    for x in text:
        if x != " " and x != "\n":
            buffer += x.strip()

        if buffer.endswith("}"):
            no_newlines = False
        
        elif buffer.endswith("={"):
            buffer = ""

        elif buffer.endswith("{"):
            no_newlines = True

            while r.endswith(" ") or r.endswith("\n"):
                r = r.removesuffix(" ").removesuffix("\n")
            r += " "

        if not no_newlines or x != "\n":
            r += x

            if no_newlines:
                if r.endswith("  "):
                    r = r.removesuffix("  ")
                    r += " "

    return r

def format(merged): #And back to text
    text = ""
    for x in merged:
        text += str(x) + "\n"

    text = text.split("\n")

    indent = 0
    for line in range(len(text)):
        if "}" in text[line] and "{" not in text[line]:
            indent -= 1

        text[line] = indent*"    " + text[line]

        if "{" in text[line] and "}" not in text[line]:
            indent += 1

    text = "\n".join(text)

    return format_compress(text)


def reformat(d):
    """Convert dict/list/json to pdxscript"""
    if isinstance(d, dict):
        r = Collection()
        for k in d.keys():
            r.append(Pair(str(k), "=", Value(reformat(d[k]))))

    elif isinstance(d, list):
        r = Collection()
        for x in d:
            r.append(Value(reformat(x)))

    elif isinstance(d, bool):
        if d == True:
            r = "yes"
        else:
            r = "no"

    elif isinstance(d, int) or isinstance(d, float):
        r = str(d)

    else:
        d = str(d)

        if " " in d.strip() or d.strip() == "":
            d = "\""+d+"\""

        r = d

    return r