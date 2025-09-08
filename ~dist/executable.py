import hoi4.compiler
import sys

print("Running build file in "+sys.argv[-1])
try:
    hoi4.compiler.Build(sys.argv[-1]).build()
except Exception as e:
    print()
    print(e)
print()
input("Press Enter to Exit.")