#!/usr/bin/env python3
"""Cut the web fonts down to the characters this site actually uses.

    python3 tools/subset-fonts.py

Fontshare ships faces covering far more of Unicode than a French page needs.
Subsetting to the Latin range plus French diacritics and typographic
punctuation removes roughly 57% of the bytes, which matters here because the
fonts are the heaviest part of the critical path.

Masters live in build/fonts-full/ and are never shipped. The subset output in
public/fonts/ is what the site serves, and it is versioned.

After running this, run tools/check-glyphs.py against a fresh build: a missing
glyph is silent at build time and shows up as a fallback letter in the browser.
"""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MASTERS = ROOT / "build" / "fonts-full"
OUTPUT = ROOT / "public" / "fonts"

# Basic Latin, Latin-1 accents covering the whole French alphabet including
# the cedilla, the OE ligature, guillemets, curly quotes and the narrow
# no-break space French typography puts before double punctuation.
UNICODES = ",".join([
    "U+0020-007E",
    "U+00A0", "U+00A7", "U+00A9", "U+00AB", "U+00BB", "U+00B0",
    "U+00C0-00CF", "U+00D4", "U+00D9-00DC",
    "U+00E0-00EF", "U+00F4", "U+00F9-00FC", "U+00FF",
    "U+0152-0153", "U+0178",
    "U+2010-2011", "U+2018-2019", "U+201C-201D",
    "U+2022", "U+2026", "U+202F", "U+20AC",
])

# Kerning and contextual alternates are what make the display face look like
# the specimen. Dropping them would save bytes and cost the typography.
LAYOUT_FEATURES = "kern,liga,calt"


def main() -> int:
    if not MASTERS.is_dir() or not any(MASTERS.glob("*.woff2")):
        print(f"No master fonts in {MASTERS.relative_to(ROOT)}")
        print("Download the full faces there before subsetting.")
        return 1

    OUTPUT.mkdir(parents=True, exist_ok=True)
    total_before = total_after = 0

    for master in sorted(MASTERS.glob("*.woff2")):
        target = OUTPUT / master.name
        result = subprocess.run(
            [
                "uvx", "--quiet", "--from", "fonttools[woff]", "pyftsubset",
                str(master),
                "--flavor=woff2",
                f"--unicodes={UNICODES}",
                f"--layout-features={LAYOUT_FEATURES}",
                f"--output-file={target}",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Subsetting failed for {master.name}:\n{result.stderr}")
            return 1

        before, after = master.stat().st_size, target.stat().st_size
        total_before += before
        total_after += after
        print(f"  {master.name:<28} {before:>6,} -> {after:>6,} bytes"
              f"  (-{100 - after * 100 // before}%)")

    print(f"\ntotal {total_before:,} -> {total_after:,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
