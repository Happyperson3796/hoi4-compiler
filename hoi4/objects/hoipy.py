from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection
import os
from .. import globals
import json
import subprocess
import sys

hoipy_allowed = False

def run_function(filepath, func_name, *args):
    file_dir = os.path.dirname(os.path.abspath(filepath))
    args_json = json.dumps(args)

    code = f"""
import json, sys
ns = {{}}
_orig_stdout = sys.stdout
sys.stdout = sys.stderr
try:
    exec(open(r'{filepath}').read(), ns)
    result = ns['{func_name}'](*json.loads(r'''{args_json}'''))
finally:
    sys.stdout = _orig_stdout

print(json.dumps(result))
"""

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=file_dir,
        capture_output=True,
        text=True
    )

    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return json.loads(result.stdout.strip())

class HoiPy(fileType):
    def run(self):

        if not hoipy_allowed:
            print("\nHoiPy execution is disabled! Set run_unsafe to true in the build config.")
            return
        
        run_function(self.path, "run")

    def clean(self):

        if not hoipy_allowed:
            print("\nHoiPy execution is disabled! Set run_unsafe to true in the build config.")
            return

        run_function(self.path, "clean")