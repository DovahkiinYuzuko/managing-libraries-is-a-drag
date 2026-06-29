# scripts/lib-docs.py
import sys
import argparse
import re
import json
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path


REGISTRY_URLS = {
    "npm":   "https://www.npmjs.com/package/{name}",
    "pypi":  "https://pypi.org/project/{name}/",
    "cargo": "https://crates.io/crates/{name}",
}


def parse_rules() -> dict:
    """Parse configuration from references/rules.md YAML front matter."""
    rules_path = Path("references/rules.md")
    if not rules_path.exists():
        sys.stderr.write("Error: references/rules.md not found\n")
        sys.exit(2)

    content = rules_path.read_text(encoding="utf-8")
    front_matter = re.search(r'^---\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
    if not front_matter:
        sys.stderr.write("Error: YAML front matter not found in rules.md\n")
        sys.exit(2)

    yaml_str = front_matter.group(1)

    wh_match = re.search(r'warehouse_path:\s*"([^"]+)"', yaml_str)
    lp_match = re.search(r'license_path:\s*"([^"]+)"', yaml_str)
    if not wh_match or not lp_match:
        sys.stderr.write("Error: 'warehouse_path' or 'license_path' missing in rules.md\n")
        sys.exit(2)

    deny_match = re.search(r'deny_licenses:\s*\n((?:\s+-\s*".*?"\s*\n?)*)', yaml_str)
    deny_list = re.findall(r'-\s*"([^"]+)"', deny_match.group(1)) if deny_match else []

    fmt_match = re.search(r'format_template:\s*\|\s*\n((?:\s{2,}.*\n?)*)', yaml_str)
    if not fmt_match:
        sys.stderr.write("Error: 'format_template' missing in rules.md\n")
        sys.exit(2)
    fmt_lines = fmt_match.group(1).rstrip().split("\n")
    fmt = "\n".join(line[2:] if line.startswith("  ") else line for line in fmt_lines) + "\n"

    return {
        "warehouse_path":  wh_match.group(1),
        "license_path":    lp_match.group(1),
        "deny_licenses":   deny_list,
        "format_template": fmt,
    }


def resolve_version(system: str, name: str) -> str | None:
    """Resolve installed version from lock files or local metadata."""
    if system == "npm" and Path("package-lock.json").exists():
        data = json.loads(Path("package-lock.json").read_text(encoding="utf-8"))
        return data.get("packages", {}).get(f"node_modules/{name}", {}).get("version")

    if system == "cargo" and Path("Cargo.lock").exists():
        lines = Path("Cargo.lock").read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if line == f'name = "{name}"' and i + 1 < len(lines):
                v = re.search(r'version = "([^"]+)"', lines[i + 1])
                if v:
                    return v.group(1)

    if system == "pypi":
        try:
            import importlib.metadata
            return importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            pass

    return None


def fetch_license(system: str, name: str, version: str) -> str:
    """Fetch SPDX license identifier(s) from the deps.dev API."""
    encoded = urllib.parse.quote(name, safe="")
    url = f"https://api.deps.dev/v3/systems/{system}/packages/{encoded}/versions/{version}"
    try:
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read())
            licenses = data.get("licenses", [])
            return " OR ".join(licenses) if licenses else "Unknown"
    except urllib.error.URLError as e:
        sys.stderr.write(f"Error: API request failed: {e}\n")
        sys.exit(2)


def check_license(license_str: str, deny_list: list[str], name: str) -> None:
    """Exit with code 1 if the license violates the deny list."""
    for denied in deny_list:
        if denied == "Unknown" and license_str == "Unknown":
            sys.stderr.write(f"Compliance violation: license for '{name}' is Unknown\n")
            sys.exit(1)
        if denied != "Unknown" and denied in license_str:
            sys.stderr.write(f"Compliance violation: '{name}' contains denied license '{denied}'\n")
            sys.exit(1)


def upsert_warehouse(wh_path: Path, system: str, name: str, full_entry: str) -> None:
    """
    Insert or update a library entry in the warehouse file.
    - The first line of full_entry is the '## system' section header.
    - Creates the section if missing.
    - Replaces the existing entry if found; otherwise inserts alphabetically.
    """
    entry_lines_raw = full_entry.rstrip().splitlines()
    section_header  = entry_lines_raw[0]           # e.g. "## npm"
    body_lines      = entry_lines_raw[1:]           # the bullet lines
    entry_marker    = next(
        (l for l in body_lines if l.startswith("- **[Library Name]:**")), None
    )
    body_with_nl = [l + "\n" for l in body_lines]

    wh_path.parent.mkdir(parents=True, exist_ok=True)
    if not wh_path.exists():
        wh_path.write_text(full_entry.rstrip() + "\n", encoding="utf-8")
        return

    content = wh_path.read_text(encoding="utf-8")
    lines   = content.splitlines(keepends=True)

    sec_start = next(
        (i for i, l in enumerate(lines) if l.rstrip() == section_header), None
    )
    if sec_start is None:
        sep = "" if content.endswith("\n\n") else ("\n" if content.endswith("\n") else "\n\n")
        wh_path.write_text(content + sep + full_entry.rstrip() + "\n", encoding="utf-8")
        return

    sec_end = next(
        (i for i in range(sec_start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines)
    )

    if entry_marker is None:
        return

    entry_start = next(
        (i for i in range(sec_start + 1, sec_end) if lines[i].rstrip() == entry_marker), None
    )

    if entry_start is not None:
        entry_end = next(
            (i for i in range(entry_start + 1, sec_end)
             if lines[i].startswith("- **[Library Name]:**")),
            sec_end
        )
        new_lines = lines[:entry_start] + body_with_nl + lines[entry_end:]
    else:
        insert_at = sec_end
        for i in range(sec_start + 1, sec_end):
            if lines[i].startswith("- **[Library Name]:**"):
                existing = lines[i].replace("- **[Library Name]:** ", "").strip()
                if name.lower() < existing.lower():
                    insert_at = i
                    break
        new_lines = lines[:insert_at] + body_with_nl + lines[insert_at:]

    wh_path.write_text("".join(new_lines), encoding="utf-8")


def upsert_notice(lic_path: Path, name: str, version: str,
                  license_str: str, registry_url: str) -> None:
    """Insert or update a library block in the NOTICE file."""
    entry = f"## {name}\nLicense: {license_str}\nVersion: {version}\nURL: {registry_url}\n\n"
    lic_path.parent.mkdir(parents=True, exist_ok=True)

    if not lic_path.exists():
        lic_path.write_text(entry, encoding="utf-8")
        return

    content = lic_path.read_text(encoding="utf-8")
    if f"## {name}\n" in content:
        content = re.sub(
            rf'^## {re.escape(name)}\n.*?(?=^## |\Z)',
            entry,
            content,
            flags=re.DOTALL | re.MULTILINE,
        )
    else:
        content += entry

    lic_path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--system",      required=True)
    parser.add_argument("--name",        required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--rationale",   required=True)
    parser.add_argument("--version",     required=False)
    parser.add_argument("--license",     required=False)
    args = parser.parse_args()

    rules = parse_rules()

    version     = args.version
    license_str = args.license

    if args.system != "custom":
        if not version:
            version = resolve_version(args.system, args.name)
            if not version:
                sys.stderr.write(f"Error: could not resolve installed version for '{args.name}'\n")
                sys.exit(2)
        license_str = fetch_license(args.system, args.name, version)

    if not license_str:
        license_str = "Unknown"

    check_license(license_str, rules["deny_licenses"], args.name)

    entry = (rules["format_template"]
             .replace("[Language]",     args.system)
             .replace("{Language}",     args.system)
             .replace("[Library Name]", args.name)
             .replace("{Library Name}", args.name)
             .replace("{Description}",  args.description)
             .replace("{Rationale}",    args.rationale)
             .replace("{Version}",      version or "")
             .replace("{License}",      license_str))

    registry_url = REGISTRY_URLS.get(args.system, "").format(name=args.name)

    upsert_warehouse(Path(rules["warehouse_path"]), args.system, args.name, entry)
    upsert_notice(Path(rules["license_path"]), args.name, version or "", license_str, registry_url)

    print(f"Done: '{args.name}' has been added/updated.")
    sys.exit(0)


if __name__ == "__main__":
    main()