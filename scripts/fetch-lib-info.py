# scripts/fetch-lib-info.py
import sys
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error

# Supported ecosystems for deps.dev API
SUPPORTED_SYSTEMS = {"npm", "cargo", "pypi", "go", "rubygems", "maven", "nuget"}

# Configuration constants
TIMEOUT_SEC = 10
# Safe User-Agent without personal identifiable information
USER_AGENT = "Managing-Libraries-is-a-drag/1.1 (Google-Antigravity-Skill)"
HEADERS = {"User-Agent": USER_AGENT}

def get_default_version(system: str, encoded_name: str) -> dict:
    """Fetch the default (latest) version. Returns dict with 'version' and 'error'."""
    url = f"https://api.deps.dev/v3alpha/systems/{system}/packages/{encoded_name}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
            data = json.loads(resp.read())
            versions = data.get("versions", [])
            for v in versions:
                if v.get("isDefault"):
                    return {"version": v.get("versionKey", {}).get("version", ""), "error": None}
            return {"version": "", "error": None}
    except urllib.error.HTTPError as e:
        return {"version": "", "error": f"HTTP Error: {e.code}"}
    except urllib.error.URLError as e:
        return {"version": "", "error": f"Network Error: {e.reason}"}
    except json.JSONDecodeError:
        return {"version": "", "error": "JSON Parse Error"}

def get_license_info(system: str, encoded_name: str, version: str) -> dict:
    """Fetch license info for a specific version. Returns dict with 'licenses' and 'error'."""
    encoded_version = urllib.parse.quote(version, safe="")
    url = f"https://api.deps.dev/v3alpha/systems/{system}/packages/{encoded_name}/versions/{encoded_version}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
            data = json.loads(resp.read())
            return {"licenses": data.get("licenses", []), "error": None}
    except urllib.error.HTTPError as e:
        return {"licenses": [], "error": f"HTTP Error: {e.code}"}
    except urllib.error.URLError as e:
        return {"licenses": [], "error": f"Network Error: {e.reason}"}
    except json.JSONDecodeError:
        return {"licenses": [], "error": "JSON Parse Error"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--system", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--version", required=False, default="")
    args = parser.parse_args()

    sys_lower = args.system.lower()
    
    # Base JSON structure for AI to parse
    result = {
        "system": args.system,
        "name": args.name,
        "version": args.version,
        "licenses": [],
        "api_supported": False,
        "error": None
    }

    if sys_lower in SUPPORTED_SYSTEMS:
        result["api_supported"] = True
        encoded_name = urllib.parse.quote(args.name, safe="")
        
        version = args.version
        if not version:
            version_data = get_default_version(sys_lower, encoded_name)
            if version_data["error"]:
                result["error"] = version_data["error"]
            else:
                version = version_data["version"]
                result["version"] = version

        # Raise an explicit error if the default version couldn't be found
        if not version and not result["error"]:
            result["error"] = "No default version found"

        if version and not result["error"]:
            license_data = get_license_info(sys_lower, encoded_name, version)
            if license_data["error"]:
                result["error"] = license_data["error"]
            else:
                result["licenses"] = license_data["licenses"]
    
    # Output raw JSON to stdout
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()