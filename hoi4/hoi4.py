import re
import requests

def extract_variable_value(text, variable_name):
    pattern = rf'{variable_name}\s*=\s*["\']([^"\']+)["\']'
    match = re.search(pattern, text)
    return match.group(1) if match else None

def get_remote_variable_value(owner, repo, branch, file_path, variable_name, token=None):
    url = f'https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}'
    headers = {'Authorization': f'token {token}'} if token else {}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch remote file: {response.status_code} {response.text}")
    return extract_variable_value(response.text, variable_name)

# === Define your local version here ===
VERSION = "1.0.1"
variable_name = "VERSION"

# === Remote repo config ===
owner = "Happyperson3796"
repo = "hoi4-compiler"
branch = "main"
file_path = "hoi4/hoi4.py"  # relative to repo root
token = "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"

# === Compare ===
remote_value = get_remote_variable_value(owner, repo, branch, file_path, variable_name, token)

print(f"Local {variable_name}:  {VERSION}")
print(f"Remote {variable_name}: {remote_value}")

if VERSION == remote_value:
    print("✅ Versions match.")
else:
    print("❌ Versions do NOT match.")


