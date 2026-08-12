#!/usr/bin/env python3
"""Measure what a first visit actually costs, for the Proof section.

    npm run build && python3 tools/measure-page.py

The Proof section publishes these numbers to visitors, so they have to be
honest. Two rules follow. Text assets are counted gzipped, because that is
what Apache sends. The portrait is counted at the variant a 1x desktop
browser picks from the srcset, not at the smallest one available.

Whatever this prints goes into src/data/metrics.ts by hand, so that changing
a number is a deliberate act with its own line in the diff.
"""

import gzip
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

# Rendered CSS width of the portrait at desktop, from the sizes attribute in
# ScenePerson.astro. At a device pixel ratio of 1 the browser picks the
# smallest candidate at least this wide.
PORTRAIT_CSS_WIDTH = 600


def gzipped(path: pathlib.Path) -> int:
    return len(gzip.compress(path.read_bytes(), 9))


def chosen_portrait(html: str) -> tuple[str, int]:
    """Pick the srcset candidate a 1x desktop browser would download."""
    candidates = []
    for match in re.finditer(r"(/assets/portrait[^\s\"]+\.webp)\s+(\d+)w", html):
        path = DIST / match.group(1).lstrip("/")
        if path.exists():
            candidates.append((int(match.group(2)), path))

    if not candidates:
        raise RuntimeError("no portrait candidates found in the built HTML")

    candidates.sort()
    for width, path in candidates:
        if width >= PORTRAIT_CSS_WIDTH:
            return path.name, path.stat().st_size
    return candidates[-1][1].name, candidates[-1][1].stat().st_size


def main() -> int:
    page = DIST / "index.html"
    if not page.exists():
        print("No build found. Run npm run build first.")
        return 1

    html = page.read_text()
    rows: list[tuple[str, int]] = [("index.html (gzip)", gzipped(page))]

    for css in sorted((DIST / "assets").glob("*.css")):
        rows.append((f"{css.name} (gzip)", gzipped(css)))

    fonts = sorted((DIST / "fonts").glob("*.woff2"))
    for face in fonts:
        rows.append((face.name, face.stat().st_size))

    name, size = chosen_portrait(html)
    rows.append((f"{name} (1x)", size))

    width = max(len(label) for label, _ in rows)
    total = 0
    for label, size in rows:
        total += size
        print(f"  {label:<{width}}  {size:>7,} bytes")

    print(f"  {'':<{width}}  {'-' * 13}")
    print(f"  {'first visit':<{width}}  {total:>7,} bytes  ({total / 1024:.0f} KB)")

    # Scripts are inline, so their weight is already inside index.html. What
    # matters for the claim we publish is that no framework runtime ships.
    module_scripts = re.findall(r'<script[^>]+src="([^"]+)"', html)
    print(f"\n  external script files: {len(module_scripts)}")

    # Only resources the browser fetches count against the "no third party"
    # claim. A link in the footer costs nothing until someone clicks it.
    fetched = set(re.findall(r'src="https?://([^/"]+)', html))
    fetched |= set(
        re.findall(r'<link[^>]+rel="(?:stylesheet|preload|preconnect)"[^>]+'
                   r'href="https?://([^/"]+)', html)
    )
    print(f"  third-party hosts fetched: {len(fetched)}"
          + (f" {sorted(fetched)}" if fetched else ""))

    return 0


if __name__ == "__main__":
    sys.exit(main())
