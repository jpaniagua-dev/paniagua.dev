#!/usr/bin/env python3
"""Capture the page as it actually renders, before calling anything done.

    npm run build && python3 tools/screenshots.py

The first version of this site shipped without ever being looked at, which is
how a missing space in a headline and a broken mobile row both reached the
client. Three captures, every time: desktop light, desktop dark, and 390px.

Writes into build/shots/, which is not versioned.
"""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "shots"
URL = "http://127.0.0.1:8787/"

SHOTS = [
    ("desktop-light", ["--viewport-size=1440,1000", "--color-scheme=light", "--full-page"]),
    ("desktop-dark", ["--viewport-size=1440,1000", "--color-scheme=dark", "--full-page"]),
    ("mobile-light", ["--viewport-size=390,844", "--color-scheme=light", "--full-page"]),
]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    for name, flags in SHOTS:
        target = OUT / f"{name}.png"
        result = subprocess.run(
            ["npx", "playwright", "screenshot", *flags,
             "--wait-for-timeout=1200", URL, str(target)],
            capture_output=True, text=True, cwd=ROOT,
        )
        if result.returncode != 0:
            print(f"{name}: failed\n{result.stderr}", file=sys.stderr)
            print(f"Is the preview running? scripts/tailnet-preview.sh start dist",
                  file=sys.stderr)
            return 1
        print(f"  {target.relative_to(ROOT)}  {target.stat().st_size:,} bytes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
