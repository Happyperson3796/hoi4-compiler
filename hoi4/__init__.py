#HASH = 6f51aa6faea036508b8d98e400adbbe68c926c27782d07f3cb20bbc9cc2f9135
import hashlib
import os
import re
import requests

def hash_directory(path):
    sha = hashlib.sha256()
    for root, dirs, files in os.walk(path):
        for file in sorted(files):
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'rb') as f:
                    sha.update(f.read())
    return sha.hexdigest()

with open(__file__, "r") as file:
    text = file.read()
if text.startswith("#HASH"): text = "\n".join(text.splitlines()[1:])
with open(__file__, "w") as file:
    file.write(text)

package_dir = os.path.dirname(os.path.abspath(__file__))
hash = hash_directory(package_dir)

with open(__file__, "r") as file:
    text = file.read()
text = "#HASH = "+hash+"\n"+text
with open(__file__, "w") as file:
    file.write(text)

def get_remote_variable_value(repo, file_path, token=None):
    url = f'https://raw.githubusercontent.com/{repo}/{file_path}'
    headers = {'Cache-Control': 'no-cache', 'Authorization': f'token {token}'} if token else {}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch remote file: {response.status_code} {response.text}")
    r = response.text.splitlines()[0]
    if not r.startswith("#HASH"): raise Exception(f"Failed to fetch remote file hash!")
    return r.split("=")[-1].strip()

# === Remote repo config ===
repo = "Happyperson3796/hoi4-compiler"
file_path = "refs/heads/main/hoi4/__init__.py"
token = "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"

# === Compare ===
remote_value = get_remote_variable_value(repo, file_path, token)

print(f"Local Version:  {hash}")
print(f"Remote Version: {remote_value}")

if hash == remote_value:
    print("! Versions match.")
else:
    print("X Versions do NOT match.")