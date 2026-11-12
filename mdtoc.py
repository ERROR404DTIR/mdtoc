#!/usr/bin/env python3
"""mdtoc - generate or update a table of contents for Markdown files.

Usage:
  mdtoc README.md            print the TOC to stdout
  mdtoc README.md --write    update the block between the markers in place
  mdtoc README.md --check    exit 1 if the block is out of date (for CI)

Put these two markers in your file where the TOC should live:
  <!-- toc -->
  <!-- tocstop -->
"""
import argparse
import re
import sys
from pathlib import Path

START, END = "<!-- toc -->", "<!-- tocstop -->"
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def slugify(text):
    """GitHub-style heading anchor."""
    text = LINK.sub(r"\1", text)
    text = re.sub(r"[`*~]", "", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def headings(text):
    """Yield (level, title) for every heading outside code fences."""
    out, fence = [], None
    for line in text.splitlines():
        m = FENCE.match(line)
        if m:
            if fence is None:
                fence = m.group(1)[0]
            elif m.group(1)[0] == fence:
                fence = None
            continue
        if fence:
            continue
        h = HEADING.match(line)
        if h:
            out.append((len(h.group(1)), h.group(2)))
    return out


def build_toc(text, lo, hi):
    seen, lines = {}, []
    for level, title in headings(text):
        slug = slugify(title)
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        if n:
            slug += f"-{n}"
        if lo <= level <= hi:
            label = LINK.sub(r"\1", title)
            lines.append(f"{'  ' * (level - lo)}- [{label}](#{slug})")
    return "\n".join(lines)


def update(text, toc):
    """Replace the block between the markers; None if markers are missing."""
    a, b = text.find(START), text.find(END)
    if a == -1 or b == -1 or b < a:
        return None
    return text[: a + len(START)] + "\n\n" + toc + "\n\n" + text[b:]


def main(argv=None):
    p = argparse.ArgumentParser(prog="mdtoc", description="Markdown table of contents generator.")
    p.add_argument("files", nargs="+", help="Markdown files")
    p.add_argument("--min", type=int, default=2, dest="lo", help="shallowest heading level (default 2)")
    p.add_argument("--max", type=int, default=4, dest="hi", help="deepest heading level (default 4)")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("-w", "--write", action="store_true", help="update files in place")
    mode.add_argument("-c", "--check", action="store_true", help="exit 1 if a TOC is out of date")
    a = p.parse_args(argv)
    if not 1 <= a.lo <= a.hi <= 6:
        p.error("need 1 <= --min <= --max <= 6")

    code = 0
    for name in a.files:
        path = Path(name)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            print(f"mdtoc: {e}", file=sys.stderr)
            code = 2
            continue
        toc = build_toc(text, a.lo, a.hi)
        if not (a.write or a.check):
            print(toc)
            continue
        new = update(text, toc)
        if new is None:
            print(f"{name}: no {START} / {END} markers found", file=sys.stderr)
            code = 2
        elif new == text:
            print(f"{name}: up to date")
        elif a.check:
            print(f"{name}: out of date")
            code = max(code, 1)
        else:
            path.write_text(new, encoding="utf-8")
            print(f"{name}: updated")
    return code


if __name__ == "__main__":
    sys.exit(main())
