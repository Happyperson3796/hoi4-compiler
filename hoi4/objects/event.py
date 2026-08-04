
from .embeddable import Embeddable
from ..pdxscript import get, format, Pair, Collection
import os
from .. import globals

class Event(Embeddable):
    def get_embeddable(self):
        d = {"title": "$ROOT.title", "desc": "$ROOT.desc"}
        for x in ["a","b","c","d","e","f","g","h","i","j","k"]: d[x] = ["$ROOT."+x, "name"]
        return d

    def run(self):
        locfile = "events/"+self.path.split("\\")[-1].removesuffix(".event")
        with open(self.path, "r", encoding="utf-8") as file:
            data = get(file.read())
        super().run(data, locfile, self.get_embeddable())

        for event in data:
            if isinstance(event, Pair) and isinstance(event[-1], Collection):
                event[-1].insert(0, Pair("id","=",event[0]))
                event[0] = "country_event"

        os.makedirs(globals.mod+"events/", exist_ok=True)
        with open(globals.mod+"events/"+self.path.split("\\")[-1].removesuffix(".event")+".txt", "w", encoding="utf-8") as file:
            file.write(format(data))

    def clean(self):
        locfile = "events/"+self.path.split("\\")[-1].removesuffix(".event")
        with open(self.path, "r", encoding="utf-8") as file:
            data = get(file.read())
        super().clean(data, locfile, self.get_embeddable())

        try: os.remove(globals.mod+"events/"+self.path.split("\\")[-1].removesuffix(".event")+".txt")
        except: pass