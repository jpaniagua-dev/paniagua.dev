#!/usr/bin/env python3
"""Grade the studio portrait so it belongs to the site palette.

    python3 tools/grade-portrait.py

The source is a low-key studio shot: roughly 60% of it is clipped to pure
#000000. Two problems follow. Pure black is banned on the page, and a clipped
black rectangle dropped on an off-white layout reads as a foreign object
rather than a composition.

The fix is a linear shadow lift. Each channel is remapped from [0, 255] onto
[floor, 255], where floor is the site's warm near-black. Highlights stay at
255 because the mapping is anchored there, so the face keeps its modelling
while the background settles onto a page token instead of a void.

Cutting the subject out is not an option: the sweater is black against a
clipped black backdrop, so there is no edge to key on.
"""

import pathlib
import sys

from PIL import Image, ImageEnhance

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / "build" / "photo" / "portrait-source.jpg"
TARGET = ROOT / "src" / "assets" / "portrait.jpg"

# The page substrate, #050506, split per channel. The studio backdrop is
# clipped to pure black in the source; lifting it exactly onto the page colour
# makes the frame disappear and leaves only the lit side of the face.
#
# An earlier version lifted it to #191817 for a pale page. On this substrate
# that reads as a grey rectangle pasted onto the layout.
FLOOR = (5, 5, 6)

# The lift is almost nil here, so contrast is pushed a little further to keep
# the face reading against a background that is now the same value as the page.
CONTRAST = 1.14


def lift_shadows(image: Image.Image, floor: tuple[int, int, int]) -> Image.Image:
    """Map each channel from [0,255] onto [floor,255], anchored at white."""
    tables = []
    for channel_floor in floor:
        span = 255 - channel_floor
        tables.extend(
            round(channel_floor + value * span / 255) for value in range(256)
        )
    return image.point(tables)


def main() -> int:
    if not SOURCE.exists():
        print(f"Source portrait not found: {SOURCE}")
        return 1

    image = Image.open(SOURCE).convert("RGB")
    # Contrast first, lift second. The other order pushes the floor back up
    # off the page colour, and the frame reappears as a faint grey edge.
    graded = lift_shadows(ImageEnhance.Contrast(image).enhance(CONTRAST), FLOOR)

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    # Quality 88 is the point where this image stops improving visibly. The
    # build pipeline derives every responsive size from this master, so it is
    # encoded once, generously, and never re-compressed by hand.
    graded.save(TARGET, quality=88, optimize=True, progressive=True)

    corner = graded.getpixel((5, 5))
    print(f"{TARGET.relative_to(ROOT)}  {graded.size[0]}x{graded.size[1]}")
    print(f"  {TARGET.stat().st_size:,} bytes")
    print(f"  background now #{corner[0]:02x}{corner[1]:02x}{corner[2]:02x}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
