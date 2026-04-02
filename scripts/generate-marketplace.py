#!/usr/bin/env python3
"""Generates marketplace.json from SKILL.md frontmatter.

Usage:
  python3 scripts/generate-marketplace.py                  # regenerate in-place (preserves version)
  python3 scripts/generate-marketplace.py --bump patch     # bump patch: 1.1.3 -> 1.1.4
  python3 scripts/generate-marketplace.py --bump auto      # set minor=department count, bump patch
  python3 scripts/generate-marketplace.py -o -             # output to stdout instead of file
"""

import argparse
import json
import os
import re

SKILLS_DIR = "skills"
MARKETPLACE_PATH = ".claude-plugin/marketplace.json"

MARKETPLACE_META = {
    "name": "epam-agent-skills",
    "owner": {
        "name": "EPAM Systems",
    },
    "metadata": {
        "description": (
            "Enterprise-grade Agent Skills by EPAM Systems. "
            "Production-tested patterns for iOS, React, Java, .NET, DevOps, and more."
        ),
    },
}


def get_current_version():
    """Read version from existing marketplace.json; fall back to 1.0.0."""
    try:
        with open(MARKETPLACE_PATH) as f:
            return json.load(f)["metadata"]["version"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return "1.0.0"


def bump_version(current, mode, department_count):
    """Bump version string. Mode: 'patch' or 'auto'.

    - patch: increment patch (1.1.3 -> 1.1.4)
    - auto:  set minor=department_count, increment patch (1.1.3 -> 1.<dept_count>.<patch+1>)
    """
    parts = current.split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    if mode == "auto":
        if department_count != minor:
            return f"{major}.{department_count}.0"
        return f"{major}.{minor}.{patch + 1}"
    # patch
    return f"{major}.{minor}.{patch + 1}"


def _frontmatter_flag(skill_md_path, flag):
    """Return True if a boolean flag is set to true in YAML frontmatter."""
    with open(skill_md_path) as f:
        content = f.read()
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False
    return bool(re.search(rf"^{flag}:\s*true\s*$", match.group(1), re.MULTILINE))


def parse_frontmatter(skill_md_path):
    """Extract name, version, and description from YAML frontmatter."""
    with open(skill_md_path) as f:
        content = f.read()

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None, None, None

    frontmatter = match.group(1)

    # Extract name
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else None

    # Extract version (optional)
    version_match = re.search(r"^version:\s*(.+)$", frontmatter, re.MULTILINE)
    version = version_match.group(1).strip() if version_match else None

    # Extract description (single-line or multi-line with >)
    desc_match = re.search(
        r"^description:\s*>\s*\n((?:[ \t]+.+\n?)+)", frontmatter, re.MULTILINE
    )
    if desc_match:
        desc = " ".join(line.strip() for line in desc_match.group(1).splitlines())
    else:
        desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
        desc = desc_match.group(1).strip().strip('"') if desc_match else None

    return name, version, desc


def main():
    parser = argparse.ArgumentParser(description="Generate marketplace.json")
    parser.add_argument(
        "--bump", choices=["patch", "auto"],
        help="Bump version: 'patch' increments patch, 'auto' syncs minor to department count and bumps patch",
    )
    parser.add_argument(
        "-o", "--output", default=MARKETPLACE_PATH,
        help=f"Output file path (default: {MARKETPLACE_PATH}). Use '-' for stdout.",
    )
    args = parser.parse_args()

    plugins = []
    # Collect skills per department for composite entries
    department_skills = {}  # {department_name: [(rel_path, name, description), ...]}

    # Walk nested skill directories (e.g., skills/ios/swiftui-mvvm-architecture/)
    for root, dirs, files in sorted(os.walk(SKILLS_DIR)):
        if "SKILL.md" not in files:
            continue

        skill_md = os.path.join(root, "SKILL.md")
        skill_name = os.path.basename(root)
        # Compute relative path from repo root
        rel_path = os.path.relpath(root, ".")

        name, version, description = parse_frontmatter(skill_md)
        if not name:
            continue
        # Skip internal/meta skills not intended for distribution
        if _frontmatter_flag(skill_md, "internal"):
            continue

        # Track department membership (e.g., skills/ios/foo -> department "ios")
        parts = rel_path.split(os.sep)
        if len(parts) >= 2:
            department = parts[1]
            department_skills.setdefault(department, []).append(
                (rel_path, name, description)
            )

        plugin = {
            "name": name,
            "description": description or "",
            "source": "./",
            "strict": False,
            "skills": [f"./{rel_path}"],
        }
        if version:
            plugin["version"] = version
        plugins.append(plugin)

    # Generate department-level composite entries (departments with 1+ skills)
    department_plugins = []
    for dept, skills in sorted(department_skills.items()):
        skill_names = [s[1] for s in skills]
        skill_paths = [f"./{s[0]}" for s in skills]
        summary = ", ".join(skill_names)
        # Special casing for known department names
        dept_display = {"ios": "iOS", "tvos": "tvOS", "macos": "macOS"}.get(
            dept.lower(), dept.title()
        )
        department_plugins.append(
            {
                "name": dept,
                "description": (
                    f"All {dept_display} department skills: {summary}. "
                    f"Install this to get the complete {dept} skill set."
                ),
                "source": "./",
                "strict": False,
                "skills": skill_paths,
            }
        )

    # Read current version before writing (must happen before file is opened for write)
    current_version = get_current_version()

    # Department entries first, then individual skills
    all_plugins = department_plugins + plugins
    if args.bump:
        version = bump_version(current_version, args.bump, len(department_skills))
    else:
        version = current_version
    metadata = {**MARKETPLACE_META["metadata"], "version": version}
    marketplace = {**MARKETPLACE_META, "metadata": metadata, "plugins": all_plugins}
    output = json.dumps(marketplace, indent=2, ensure_ascii=False)

    if args.output == "-":
        print(output)
    else:
        with open(args.output, "w") as f:
            f.write(output + "\n")
        print(f"Wrote {args.output} (version {version})")


if __name__ == "__main__":
    main()
