#!/usr/bin/env python3
"""Generate the favicon and the social share card.

    python3 tools/generate-images.py

Both are derived from the tokens in src/styles/global.css and from the same
portrait the hero uses, so a share on LinkedIn looks like the page it links
to. Fonts are downloaded into build/ on first run.

Re-run after any change to the palette, the wordmark or the tagline.
"""

import pathlib
import re
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
PORTRAIT = ROOT / "src" / "assets" / "portrait.jpg"

# Dark-substrate tokens, kept in sync with src/styles/global.css
PAPER = (5, 5, 6)
INK = (242, 241, 237)
MUTED = (139, 139, 133)
ACCENT = (129, 140, 248)
ACCENT_2 = (192, 132, 252)

WORDMARK = "PANIAGUA.DEV"
TAGLINE = "Sole proprietorship, Geneva"
FOOTNOTE = "Expert Front-End & Workflow Digitalisation"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/126.0 Safari/537.36"
)


def font(family: str, weight: int, size: int) -> ImageFont.FreeTypeFont:
    """Load a Fontshare face, downloading the TrueType build on first use.

    Pillow cannot read woff2, which is what the site ships, so the generator
    pulls the TrueType variant of the same face instead.
    """
    BUILD.mkdir(exist_ok=True)
    path = BUILD / f"{family}-{weight}.ttf"

    if not path.exists():
        css_url = f"https://api.fontshare.com/v2/css?f[]={family}@{weight}"
        request = urllib.request.Request(css_url, headers={"User-Agent": USER_AGENT})
        css = urllib.request.urlopen(request, timeout=30).read().decode()
        match = re.search(r"url\('(//[^']+\.ttf)'\)", css)
        if match is None:
            raise RuntimeError(f"no TrueType build offered for {family}@{weight}")
        data = urllib.request.urlopen(
            urllib.request.Request("https:" + match.group(1),
                                   headers={"User-Agent": USER_AGENT}),
            timeout=30,
        ).read()
        path.write_bytes(data)
        print(f"  downloaded font: {path.name}")

    return ImageFont.truetype(str(path), size)


def build_share_card() -> pathlib.Path:
    """1200x630 card echoing the hero: copy on the left, portrait on the right."""
    width, height = 1200, 630
    card = Image.new("RGB", (width, height), PAPER)

    # Portrait column, cropped to fill rather than squashed.
    column = 430
    portrait = Image.open(PORTRAIT).convert("RGB")
    scale = max(column / portrait.width, height / portrait.height)
    resized = portrait.resize(
        (round(portrait.width * scale), round(portrait.height * scale)),
        Image.LANCZOS,
    )
    left = (resized.width - column) // 2
    # Bias the crop upward so the face is not cut at the chin.
    top = max(0, (resized.height - height) // 2 - round(height * 0.06))
    card.paste(resized.crop((left, top, left + column, top + height)),
               (width - column, 0))

    draw = ImageDraw.Draw(card)
    margin = 72

    draw.text((margin, 214), WORDMARK, font=font("switzer", 900, 62), fill=INK)
    draw.text((margin, 306), TAGLINE, font=font("switzer", 400, 27), fill=MUTED)
    # The accent is a two-stop ramp on the site, so the rule carries it too.
    for offset in range(96):
        blend = offset / 95
        colour = tuple(
            round(ACCENT[c] + (ACCENT_2[c] - ACCENT[c]) * blend) for c in range(3)
        )
        draw.rectangle([margin + offset, 372, margin + offset, 376], fill=colour)
    draw.text((margin, 410), FOOTNOTE, font=font("switzer", 400, 21), fill=MUTED)

    target = ROOT / "public" / "og-image.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    card.save(target, optimize=True)
    return target


def build_favicon() -> pathlib.Path:
    """180x180 monogram, also serving as the apple-touch-icon."""
    side = 180
    # Drawn oversized then downscaled: smooth corners without hand-rolled
    # antialiasing.
    scale = 4
    large = side * scale

    corners = Image.new("L", (large, large), 0)
    ImageDraw.Draw(corners).rounded_rectangle(
        [0, 0, large - 1, large - 1], radius=large // 5, fill=255
    )

    # Diagonal ramp behind the monogram, the same one the site uses on rules.
    plate = Image.new("RGB", (large, large))
    pixels = plate.load()
    for x in range(large):
        for y in range(large):
            blend = (x / large + y / large) / 2
            pixels[x, y] = tuple(
                round(ACCENT[c] + (ACCENT_2[c] - ACCENT[c]) * blend) for c in range(3)
            )
    glyph_font = font("switzer", 900, int(large * 0.62))

    # Centre on the glyph's real pixels: the mark reserves descender space it
    # does not use, so box-centring would sit visibly high.
    probe = Image.new("L", (large, large), 0)
    ImageDraw.Draw(probe).text(
        (large // 2, large // 2), "P", font=glyph_font, fill=255, anchor="mm"
    )
    box = probe.getbbox()

    ImageDraw.Draw(plate).text(
        (large // 2 - (box[0] + box[2] - large) // 2,
         large // 2 - (box[1] + box[3] - large) // 2),
        # Dark on the ramp, not light: paper on indigo is 2.6:1 and the mark
        # would be unreadable at tab size. Ink on it is 6.8:1.
        "P", font=glyph_font, fill=PAPER if PAPER[0] < 128 else (5, 5, 6),
        anchor="mm",
    )

    icon = Image.new("RGBA", (large, large), (0, 0, 0, 0))
    icon.paste(plate, (0, 0), corners)
    icon = icon.resize((side, side), Image.LANCZOS)

    target = ROOT / "public" / "favicon.png"
    icon.save(target, optimize=True)

    # Browsers request /favicon.ico on their own even when a <link> points
    # elsewhere. Without it, every visit logs a 404.
    icon.save(ROOT / "public" / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    return target


def main() -> int:
    if not PORTRAIT.exists():
        print(f"Portrait not found: {PORTRAIT}")
        print("Run tools/grade-portrait.py first.")
        return 1

    for build in (build_share_card, build_favicon):
        path = build()
        print(f"{path.name}  {path.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
