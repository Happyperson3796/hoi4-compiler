from hoi4.pdxscript import get, format, Pair, Collection
print("A rough example of merging two files using the pdxscript parser.")
override = input("Override: ").strip()
base = input("Base: ").strip()

with open(override, "r") as file:
    override = get(file.read())

with open(base, "r") as file:
    base = get(file.read())

base.merge(override)

with open("output.txt", "w") as file:
    file.write(format(base))
