import sys
import os
from hoi4 import compiler

if len(sys.argv) > 1:
    file_to_open = sys.argv[1].replace("\\","/").split("/")
    file_to_open.pop(-1)
    file_to_open = "/".join(file_to_open)+"/"
    os.chdir(file_to_open)
    print("Running build file in "+file_to_open)
    try:
        compiler.Build(file_to_open).build()
    except Exception as e:
        print(e)
        print("If access is denied, try adding an exception to your antivirus for 'C:\Program Files (x86)\HoiCompiler\hoic.exe'")
    input("Press any key to exit . . .")
else:
    input("No build file was specified!")