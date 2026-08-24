from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection, Jom
from .pull_file import Pulled
import os

class MergedV2(fileType):
    def execute(data: Jom, base_file: str, subpath: str, reverse: bool, key_path: str, header: int):
        subpath = subpath.removeprefix("/").removesuffix("/").split("/")

        has_subpath = True
        if "".join(subpath).replace("/", "").strip() == "":
            has_subpath = False

        if not os.path.exists(base_file): #Create if not found
            with open(base_file, "w") as file:
                t = ""
                if has_subpath:
                    for x in subpath:
                        t += x+"={"
                    for x in subpath:
                        t += "}"
                file.write(t)

        with open(base_file, "r") as file:
            base = get(file.read())
            subbase = base.get(subpath[0]) if has_subpath else base
            assert isinstance(subbase, Collection)
            if has_subpath:
                for p in subpath[1:]:
                    subbase = subbase.get(p)

        suboverride = data.get(subpath[0]) if has_subpath else data
        if has_subpath:
            for p in subpath[1:]:
                suboverride = suboverride.get(p)

        subbase.merge(suboverride, reverse, key_path, header)

        with open(base_file, "w") as file:
            file.write(format(base))

    def run(self):
        head, tail = os.path.split(self.path)

        with open(self.path, "r") as file:
            raw = get(file.read())

        for data in raw:
            assert isinstance(data, Pair)
            base_file = data.key_data().unquote().strip()
            subpath = data.value().get_pop("path", "").unquote().strip()
            key_path = data.value().get_pop("key_path", "").unquote().strip()
            reverse = data.value().get_pop("reverse", "no").bool()
            pull = data.value().get_pop("pull", "").unquote().strip()
            header = int(data.value().get_pop("header", "0").unquote().strip())

            if pull != "": Pulled.execute(head, pull+"/"+base_file, base_file)

            MergedV2.execute(data[-1], head+"/"+base_file, subpath, reverse, key_path, header)

    def clean(self):
        pass