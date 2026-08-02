from collections import deque

def is_spacing(char):
    return char == " " or char == "\n" or char == "\t" or char == ""


def is_connector(char):
    return char == "=" or char == "<" or char == ">" or char == "?=" or char == "!=" or char == "<=" or char == ">="


class Jom:
    def __init__(self, *args, **kwargs):
        pass


class StoredData(Jom):
    def __init__(self, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

    @property
    def __class__(self):
        return self.value.__class__

    def __getattr__(self, name):
        return getattr(self.value, name)

    def __radd__(self, other):
        if isinstance(other, str):
            return other + str(self.value)
        return NotImplemented

    def __add__(self, other):
        return str(self.value) + str(other)

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def __getitem__(self, key):
        return self.value[key]

    def _value(self):
        """Intended for use with type() checks, outside of this should not be needed."""
        return self.value

    def _val(self):
        """Intended for use with type() checks, outside of this should not be needed."""
        return self._value()

    def is_empty(self):
        return self.value == ""

    def unquote(self) -> str:
        if not isinstance(self.value, str): raise Exception("Not a string!")
        return self.value.removeprefix("\"").removesuffix("\"")

    def bool(self) -> bool:
        if not isinstance(self.value, str): raise Exception("Not a string!")
        if self.value == "yes":
            return True
        elif self.value == "no":
            return False
        raise Exception("Not a boolean!")


class Value(StoredData):
    def set(self, value):
        self.value = value

    def immutable(self) -> StoredData:
        return super()


class Pair(Jom):
    def __init__(self, k, c, v, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if type(v) != Value: v = Value(v)
        self.holder = (k, c, v)

    def text(self):
        return " ".join(map(str, self.holder))

    def __str__(self):
        return self.text()

    def __repr__(self):
        return self.text()

    def __getitem__(self, index):
        return self.holder[index]

    def __setitem__(self, index, value):
        temp = list(self.holder)
        temp[index] = value
        if type(temp[-1]) != Value:
            temp[-1] = Value(temp[-1])
        self.holder = tuple(temp)

    def key_data(self):
        """Wrapped p[0]"""
        return StoredData(self[0])

    def key(self):
        """Equivalent to p[0]"""
        return self[0]

    def connector(self):
        """Equivalent to p[1]"""
        return self[1]

    def value(self):
        """Equivalent to p[2], p[-1]"""
        return self[2]

    def copy(self):
        return Pair(*self.holder)


class Collection(Jom, list):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.extend([*args])

    def text(self):
        return "{\n" + "\n".join(map(str, self)) + "\n}"

    def __str__(self):
        return self.text()

    def __repr__(self):
        return self.text()

    def _get(self, search: str, return_pair=False, debug=False):
        """Underlying method, doesn't have a default param and so may throw exceptions."""
        for x in self:
            check = str(x)
            if isinstance(x, Pair):
                if return_pair:
                    check = x[0]
                else:
                    check = x[0]
                    x = x[-1]

            if debug:
                print(check)

            if str(search) == check:
                return x

        raise Exception("\"" + search + "\" not found in Collection:\n" + str(self) + "\n")

    def get(self, retrieve: str, default=None, debug=False):
        """Gets a value if it exists, otherwise returns default."""
        try:
            return self._get(retrieve, False, debug)
        except Exception as e:
            if default is not None:
                if not isinstance(default, StoredData): default = StoredData(default)
                return default
            else:
                raise e

    def get_pair(self, retrieve: str, default=None, debug=False):
        """Gets the Pair. Mainly for .remove()"""
        try:
            return self._get(retrieve, True, debug)
        except Exception as e:
            if default is not None:
                if not isinstance(default, StoredData): default = StoredData(default)
                return default
            else:
                raise e

    def get_pop(self, retrieve: str, default=None, debug=False):
        obj = self.get_pop_pair(retrieve, default, debug)
        try:
            return obj[-1]
        except Exception as e:
            if default is not None:
                if not isinstance(default, StoredData): default = StoredData(default)
                return default
            else:
                raise e

    def get_pop_pair(self, retrieve: str, default=None, debug=False):
        obj = self.get_pair(retrieve, default, debug)
        try:
            self.remove(obj)
        except:
            pass
        return obj

    def put(self, p: Pair, prepend: bool = False):
        """Sets a Pair value, OR appends it to the collection."""
        try:
            self.retrieve(p[0]).set(p[-1])
        except:
            if not prepend:
                self.append(p)
            else:
                self.insert(0, p)

    def merge(self, collection, reverse=False, key_path="", header=0):
        """Critical function that I wrote while sleep deprived"""
        this = self

        to_append = Collection()

        for override in collection:
            append = True
            for pair in this:

                equals = False
                if key_path == "":
                    if override[0] == pair[0]:
                        equals = True
                else:
                    if isinstance(pair, Collection) and override.value().get(
                            key_path).unquote().strip() == pair.value().get(key_path).unquote().strip():
                        equals = True

                if equals:
                    append = False
                    pair[-1].set(override[-1])

            if append:
                to_append.append(override)

        if not reverse:
            this.extend(to_append)
        else:
            l = -1 + header
            for x in to_append:
                l += 1
                this.insert(l, x)

    def copy(self):
        return get(str(self))

    def entries(self):
        """Iterates through all objects in the Collection excluding those containing \"inline\""""
        l = []
        for x in self:
            if type(x) == Pair and "inline" in x[0]: continue
            l.append(x)
        return l


def get(text):  # All combined
    """Returns a text as pdx objects wrapped in a new collection"""
    return merge_pairs(collect(parse(text)))


def parse(text):
    text += "\n"

    parsed = []
    buffer = ""
    commented = False
    is_quoted = False

    for char in text:
        if char == "\"":
            is_quoted = not is_quoted

        if char == "#":
            commented = True
        elif char == "\n":
            commented = False
            
        if not commented:
            if (char == " " or char == "\n" or char == "\t") and not is_quoted:
                if buffer:
                    parsed.append(buffer)
                buffer = ""
                
            elif not is_quoted:
                if char == "=":
                    # Fast index check for complex operators (?=, !=, <=, >=)
                    if buffer and buffer[-1] in "?!<>":
                        prefix = buffer[:-1]
                        if prefix:
                            parsed.append(prefix)
                        parsed.append(buffer[-1] + "=")
                        buffer = ""
                    else:
                        if buffer:
                            parsed.append(buffer)
                        parsed.append("=")
                        buffer = ""
                        
                elif char == "{" or char == "}":
                    if buffer:
                        # Flush any lingering standalone < or > connectors before appending brackets
                        parsed.append(buffer)
                    parsed.append(char)
                    buffer = ""
                    
                elif char == "<" or char == ">":
                    # Isolate < and > in the buffer so they are ready to combine with a potential '='
                    if buffer:
                        parsed.append(buffer)
                    buffer = char
                    
                else:
                    # If buffer is exactly < or > and the current char is NOT =, flush the connector
                    if buffer == "<" or buffer == ">":
                        parsed.append(buffer)
                        buffer = char
                    else:
                        buffer += char
            else:
                buffer += char

    return parsed

def collect(parsed):
    # Convert to deque for O(1) popleft operations
    q = deque(parsed)
    
    def collect_value():
        collection = Collection()
        while len(q) > 0:
            obj = q.popleft()

            if obj == "}":
                return collection
            elif obj == "{":
                collection.append(collect_value())
            else:
                collection.append(obj)

        return collection

    return collect_value()


def merge_pairs(collection):
    merged = Collection()
    q = deque(collection)
    
    while len(q) > 0:
        x = q.popleft()

        if len(q) > 1 and is_connector(q[0]):
            c = q.popleft()
            v = q.popleft()
            
            if isinstance(v, list):
                v = merge_pairs(v)
                
            merged.append(Pair(x, c, Value(v)))
        else:
            merged.append(Value(x))

    return merged


def format(data):
    raw_lines = [(str(x) + "\n") for x in data]
    text = "".join(raw_lines)

    lines = text.split("\n")
    indented = []
    indent = 0
    
    for line in lines:
        if "}" in line and "{" not in line:
            indent -= 1

        indented.append((indent * "    ") + line)

        if "{" in line and "}" not in line:
            indent += 1

    text = "\n".join(indented)

    return format_compress(text)


def format_compress(text): 
    r = []  # Use a list to prevent O(N²) string reallocation
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

            # Replaces while r.endswith(...) string methods
            while r and (r[-1] == " " or r[-1] == "\n"):
                r.pop()
            r.append(" ")

        if not no_newlines or x != "\n":
            r.append(x)

            if no_newlines:
                # Replaces if r.endswith("  ") string deduplication
                if len(r) >= 2 and r[-1] == " " and r[-2] == " ":
                    r.pop()

    return "".join(r)


# def reformat(d):
#    """Convert dict/list/json to pdxscript"""
#    if isinstance(d, dict):
#        r = Collection()
#        for k in d.keys():
#            r.append(Pair(str(k), "=", Value(reformat(d[k]))))
#
#    elif isinstance(d, list):
#        r = Collection()
#        for x in d:
#            r.append(Value(reformat(x)))
#
#    elif isinstance(d, bool):
#        if d == True:
#            r = "yes"
#        else:
#            r = "no"
#
#    elif isinstance(d, int) or isinstance(d, float):
#        r = str(d)
#
#    else:
#        d = str(d)
#
#        if " " in d.strip() or d.strip() == "":
#            d = "\""+d+"\""
#
#        r = d
#
#    return r