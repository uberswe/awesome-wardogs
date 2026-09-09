#!/usr/bin/env python3
"""Remove every line that contains a given URL from a Markdown file.

Usage:
    remove_link.py README.md https://example.com/dead-page

When the removed line is a list item, any list items nested directly under it
are removed as well so no orphaned sub-bullets are left behind. The script
prints the removed lines and exits with status 1 if nothing changed.
"""

import re
import sys

LIST_ITEM = re.compile(r"^(\s*)[-*+]\s")


def indent_of(line):
    match = LIST_ITEM.match(line)
    return len(match.group(1)) if match else None


def url_matcher(url):
    # Match the URL only when it is not followed by another URL character, so
    # that https://example.com/ does not also match https://example.com/page.
    return re.compile(re.escape(url) + r"(?![^\s()<>\[\]\"'])")


def remove_url(lines, url):
    matcher = url_matcher(url)
    kept = []
    removed = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not matcher.search(line):
            kept.append(line)
            index += 1
            continue

        removed.append(line)
        parent_indent = indent_of(line)
        index += 1
        if parent_indent is None:
            continue
        # Drop nested list items that belong to the removed parent.
        while index < len(lines):
            child_indent = indent_of(lines[index])
            if child_indent is None or child_indent <= parent_indent:
                break
            removed.append(lines[index])
            index += 1
    return kept, removed


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    path, url = sys.argv[1], sys.argv[2]

    with open(path, encoding="utf-8") as handle:
        lines = handle.read().split("\n")

    kept, removed = remove_url(lines, url)
    if not removed:
        print(f"No line in {path} contains {url}")
        return 1

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(kept))

    print(f"Removed {len(removed)} line(s) from {path}:")
    for line in removed:
        print(f"  {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
