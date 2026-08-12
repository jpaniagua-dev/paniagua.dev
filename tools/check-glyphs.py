#!/usr/bin/env python3
"""Fail if the built page uses a character the subset fonts do not carry.

    npm run verify

A missing glyph never breaks the build. The browser silently swaps in a
fallback face for that one character, which is the kind of defect that ships
and then gets noticed by a visitor rather than by us.

The check also enforces the typographic rules the design brief sets: no
em-dash and no en-dash anywhere in visible text.
"""

import html as html_module
import pathlib
import re
import sys

from fontTools.ttLib import TTFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Both language routes: the French one carries accents the English one
# never uses, and a subset that covers one may not cover the other.
PAGES = [ROOT / "dist" / "index.html", ROOT / "dist" / "fr" / "index.html"]
FONTS = ROOT / "public" / "fonts"

BANNED = {"—": "em-dash", "–": "en-dash"}


def visible_text(html: str) -> str:
    """Strip scripts, styles and tags, leaving what a reader actually sees."""
    without_code = re.sub(
        r"<(script|style)\b[^>]*>.*?</\1>", " ", html, flags=re.S | re.I
    )
    return html_module.unescape(re.sub(r"<[^>]+>", " ", without_code))


def main() -> int:
    missing_pages = [p for p in PAGES if not p.exists()]
    if missing_pages:
        for page in missing_pages:
            print(f"No build found at {page.relative_to(ROOT)}. Run npm run build.")
        return 1

    text = "".join(visible_text(page.read_text()) for page in PAGES)
    used = {c for c in text if c not in "\n\r\t"}

    failures = 0

    for face in sorted(FONTS.glob("*.woff2")):
        covered = set()
        with TTFont(face) as font:
            for table in font["cmap"].tables:
                covered.update(chr(cp) for cp in table.cmap)
        missing = sorted(used - covered)
        if missing:
            failures += 1
            print(f"{face.name}: {len(missing)} glyph(s) missing")
            for char in missing:
                print(f"  U+{ord(char):04X}  {char!r}")
        else:
            print(f"{face.name}: covers all {len(used)} characters used")

    for char, name in BANNED.items():
        count = text.count(char)
        if count:
            failures += 1
            print(f"{name} found {count} time(s) in visible text. Not allowed.")

    if failures:
        print(f"\n{failures} check(s) failed.")
        return 1

    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
