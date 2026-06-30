# scripts/lib-analyze.py
import sys
import json
import argparse
import re
import subprocess
import shutil
from pathlib import Path


def parse_rules() -> list[str]:
    """Parse ignore_packages from references/rules.md YAML front matter."""
    rules_path = Path("references/rules.md")
    if not rules_path.exists():
        sys.stderr.write("Error: references/rules.md not found\n")
        sys.exit(1)

    content = rules_path.read_text(encoding="utf-8")
    match = re.search(r'```yaml\n(.*?)\n```', content, re.DOTALL)
    if not match:
        sys.stderr.write("Error: YAML code block not found in rules.md\n")
        sys.exit(1)

    ignore_match = re.search(r'ignore_packages:\s*\n((?:\s+-\s*".*?"\s*\n?)*)', match.group(1))
    if not ignore_match:
        return []
    return re.findall(r'-\s*"([^"]+)"', ignore_match.group(1))


def detect_ecosystems() -> list[str]:
    """Detect present package ecosystems from manifest files."""
    ecosystems = []
    if Path("package.json").exists():
        ecosystems.append("npm")
    if Path("Cargo.toml").exists():
        ecosystems.append("cargo")
    if Path("pyproject.toml").exists() or Path("requirements.txt").exists():
        ecosystems.append("pypi")
    return ecosystems


def check_tool(tool: str) -> None:
    """Exit with code 2 if a required CLI tool is missing."""
    if not shutil.which(tool):
        sys.stderr.write(f"Error: '{tool}' is not installed or not in PATH\n")
        sys.exit(2)


def check_subcommand(args: list[str]) -> None:
    """Exit with code 2 if a CLI subcommand (e.g. cargo-udeps) is not installed."""
    try:
        subprocess.run(args, capture_output=True, text=True)
    except FileNotFoundError:
        sys.stderr.write(f"Error: '{' '.join(args)}' is not available\n")
        sys.exit(2)


def detect_unused_npm(ignores: list[str]) -> list[tuple[str, str]]:
    check_tool("depcheck")
    # depcheck は未使用パッケージを検出した場合でも非ゼロを返すため、
    # ここでは check=True を使わず stdout の内容だけを見る
    res = subprocess.run(["depcheck", "--json"], capture_output=True, text=True)
    try:
        data = json.loads(res.stdout)
    except json.JSONDecodeError:
        sys.stderr.write(f"Error: depcheck returned invalid JSON: {res.stdout[:200]}\n")
        sys.exit(1)
    unused = data.get("dependencies", []) + data.get("devDependencies", [])
    return [("npm", pkg) for pkg in unused if pkg not in ignores]


def detect_unused_cargo(ignores: list[str]) -> list[tuple[str, str]]:
    check_tool("cargo")
    check_subcommand(["cargo", "udeps", "--help"])
    res = subprocess.run(["cargo", "udeps"], capture_output=True, text=True)
    matches = re.findall(r'unused dependencies:(.*?)(?:\n\n|\Z)', res.stderr, re.DOTALL)
    pkgs = re.findall(r'^\s+(.*?)(?:\s|$)', matches[0], re.MULTILINE) if matches else []
    return [("cargo", pkg) for pkg in pkgs if pkg and pkg not in ignores]


def detect_unused_pypi(ignores: list[str]) -> list[tuple[str, str]]:
    check_tool("pip-check-reqs")
    target = "pyproject.toml" if Path("pyproject.toml").exists() else "requirements.txt"
    res = subprocess.run(["pip-check-reqs", target], capture_output=True, text=True)
    pkgs = re.findall(r'Extra requirement:\s+([^\s]+)', res.stdout)
    return [("pypi", pkg) for pkg in pkgs if pkg not in ignores]


DETECTORS = {
    "npm":   detect_unused_npm,
    "cargo": detect_unused_cargo,
    "pypi":  detect_unused_pypi,
}


def remove_package(eco: str, pkg: str) -> None:
    """Run the appropriate remove command for the ecosystem."""
    if eco == "npm":
        subprocess.run(["npm", "uninstall", pkg], check=True)
    elif eco == "cargo":
        subprocess.run(["cargo", "remove", pkg], check=True)
    elif eco == "pypi":
        if Path("poetry.lock").exists() and shutil.which("poetry"):
            subprocess.run(["poetry", "remove", pkg], check=True)
        elif Path("uv.lock").exists() and shutil.which("uv"):
            subprocess.run(["uv", "remove", pkg], check=True)
        elif Path("requirements.txt").exists():
            req = Path("requirements.txt")
            lines = req.read_text(encoding="utf-8").splitlines(keepends=True)
            req.write_text(
                "".join(l for l in lines
                        if not re.match(rf'^{re.escape(pkg)}(?:[^\w-].*)?$', l.strip(), re.IGNORECASE)),
                encoding="utf-8"
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    ignores = parse_rules()

    ecosystems = detect_ecosystems()
    if not ecosystems:
        sys.stderr.write("Error: no supported manifest file found (package.json / Cargo.toml / pyproject.toml / requirements.txt)\n")
        sys.exit(2)

    to_remove: list[tuple[str, str]] = []
    for eco in ecosystems:
        try:
            to_remove.extend(DETECTORS[eco](ignores))
        except Exception as e:
            sys.stderr.write(f"Error analyzing {eco}: {e}\n")
            sys.exit(1)

    if not args.apply:
        print("Dry-run: the following packages were detected as unused:")
        if to_remove:
            for eco, pkg in to_remove:
                print(f"  [{eco}] {pkg}")
        else:
            print("  (none)")
        sys.exit(0)

    for eco, pkg in to_remove:
        print(f"Removing [{eco}] {pkg} ...")
        try:
            remove_package(eco, pkg)
        except subprocess.CalledProcessError as e:
            sys.stderr.write(f"Error: remove command failed for '{pkg}': {e}\n")
            sys.exit(1)

    print("Cleanup complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()