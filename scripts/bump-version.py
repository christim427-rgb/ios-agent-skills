#!/usr/bin/env python3
"""Bumps the repo version, updates marketplace.json, and creates a git tag.

Usage: python3 scripts/bump-version.py             # patch: 1.0.0 → 1.0.1
       python3 scripts/bump-version.py --minor      # minor: 1.0.0 → 1.1.0
       python3 scripts/bump-version.py --major      # major: 1.0.0 → 2.0.0
       python3 scripts/bump-version.py --push       # bump patch + push tag to origin

Run this locally after merging meaningful changes to main.
"""

import argparse
import json
import subprocess
import sys

MARKETPLACE_PATH = ".claude-plugin/marketplace.json"


def bump_version(version: str, part: str) -> str:
    major, minor, patch = map(int, version.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    elif part == "minor":
        return f"{major}.{minor + 1}.0"
    else:
        return f"{major}.{minor}.{patch + 1}"


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--minor", action="store_true", help="Bump minor version")
    group.add_argument("--major", action="store_true", help="Bump major version")
    parser.add_argument("--push", action="store_true", help="Push commit and tag to origin")
    args = parser.parse_args()

    part = "major" if args.major else "minor" if args.minor else "patch"

    with open(MARKETPLACE_PATH) as f:
        data = json.load(f)

    current = data["metadata"]["version"]
    new_version = bump_version(current, part)
    tag = f"v{new_version}"

    # Update marketplace.json
    data["metadata"]["version"] = new_version
    with open(MARKETPLACE_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Regenerate to pick up any structural changes
    output = run(["python3", "scripts/generate-marketplace.py"])
    with open(MARKETPLACE_PATH, "w") as f:
        f.write(output + "\n")

    # Commit the version bump
    run(["git", "add", MARKETPLACE_PATH])
    run(["git", "commit", "-m", f"chore: bump version to {new_version}"])

    # Create annotated tag
    run(["git", "tag", "-a", tag, "-m", f"Release {tag}"])

    print(f"✅ {current} → {new_version}")
    print(f"   tag: {tag}")

    if args.push:
        run(["git", "push", "origin", "HEAD"])
        run(["git", "push", "origin", tag])
        print(f"   pushed to origin")
    else:
        print(f"\nTo publish:")
        print(f"   git push origin HEAD && git push origin {tag}")


if __name__ == "__main__":
    main()
