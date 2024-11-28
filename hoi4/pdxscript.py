
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
            elif is_connector(char) or char == "{" or char == "}":
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
    
    def get(self, search="", debug=False, strict=True):
        if search == "":
            if isinstance(self[0], Pair):
                return self[0][-1]
            return self[0]

        for x in self.copy():
            check = str(x)
            if isinstance(x, Pair):
                check = x[0]
                x = x[-1]

            if debug:
                print(check)

            if (not strict and search in check) or (strict and search == check):
                return x

        raise Exception(("Strict search" if strict else "Search")+" \""+search+"\" not found!")
            
    def search(self, search, debug=False):
        return self.get(search, debug, False)
    
    def merge(self, collection):
        for override in collection:
            append = True
            for pair in self:
                if override[0] == pair[0]:
                    append = False
                    pair.set(override[-1])

            if append:
                self.append(override)

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


def format(merged): #And back to text
    text = ""
    for x in merged:
        text += str(x) + "\n"

    text = text.split("\n")

    indent = 0
    for line in range(len(text)):
        if "}" in text[line]:
            indent -= 1

        text[line] = indent*"    " + text[line]

        if "{" in text[line]:
            indent += 1

    text = "\n".join(text)

    return text