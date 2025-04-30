#HASH = 5c610abd67a550a1afec902fdeefeb9da48ce80adeb20f30b5ed8b35926a11a7
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

def extract_variable_value(text, variable_name):
    pattern = rf'{variable_name}\s*=\s*["\']([^"\']+)["\']'
    match = re.search(pattern, text)
    return match.group(1) if match else None

def get_remote_variable_value(repo, file_path, variable_name, token=None):
    url = f'https://raw.githubusercontent.com/{repo}/{file_path}'
    headers = {'Authorization': f'token {token}'} if token else {}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch remote file: {response.status_code} {response.text}")
    return extract_variable_value(response.text, variable_name)

# === Remote repo config ===
variable_name = "#HASH"
repo = "Happyperson3796/hoi4-compiler"
file_path = "refs/heads/main/hoi4/hoi4.py"
token = "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"

# === Compare ===
remote_value = get_remote_variable_value(repo, file_path, variable_name, token)

print(f"Local {variable_name}:  {hash}")
print(f"Remote {variable_name}: {remote_value}")

if hash == remote_value:
    print("! Versions match.")
else:
    print("X Versions do NOT match.")