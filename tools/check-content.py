#!/usr/bin/env python3
"""Verify that no copy was invented.

    python3 tools/check-content.py [--url https://example.org/]

The brief was explicit: reuse the text already published, do not write new
marketing copy. That is easy to promise and easy to drift from, so it is
checked instead.

The page now reads in English while the published reference is largely French,
so the check follows the translation ledger. Every string in
src/data/content.ts must be one of:

  - present on the reference page as it stands, or
  - a key of `derivedFrom`, whose French source is present there, or
  - marked ADDED on the line directly above it.

The comparison ignores case, accents and whitespace, because the site sets
some strings in capitals and rewraps others.

Exit code 1 if any string cannot be accounted for, so this can gate a release.
"""

import argparse
import html as html_module
import pathlib
import re
import sys
import unicodedata
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "src" / "data" / "content.ts"

# The frozen snapshot, not the live URL. Once this redesign is deployed,
# paniagua.dev serves the new site: the reference would replace itself, the
# check would lose its meaning, and it would fail on every French string now
# living under /fr/. The snapshot also removes a network call from CI.
REFERENCE = ROOT / "reference" / "paniagua.dev-2026-08-12.html"

# The code sample lives in its own file, imported raw by the page, so it is
# checked separately from the quoted strings in content.ts.
SNIPPET = ROOT / "src" / "data" / "user-profile.component.ts.txt"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/126.0 Safari/537.36"
)


def normalise(text: str) -> str:
    """Fold case, accents and whitespace so wrapping differences do not matter."""
    stripped = "".join(
        char for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )
    # Curly and straight quotes are interchangeable for this comparison.
    stripped = stripped.replace("’", "'").replace("‘", "'")
    collapsed = " ".join(stripped.lower().split())
    # Stripping tags leaves a space before punctuation that was glued to a
    # closing tag, as in "<strong>workflows</strong>." Close it back up.
    return re.sub(r"\s+([.,;:!?])", r"\1", collapsed)


def reference_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    html = urllib.request.urlopen(request, timeout=30).read().decode("utf-8", "replace")
    html = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    # Content published only inside an attribute is still published content:
    # mailto targets, and the meta description, which never appears as text.
    addresses = " ".join(re.findall(r"mailto:([^\"\'>\s]+)", html))
    metas = " ".join(
        re.findall(r'<meta[^>]+name="(?:description|keywords)"[^>]+content="([^"]*)"',
                   html, re.I)
    )
    # Unescape after stripping tags, never before: &lt;h1&gt; in the code
    # sample would otherwise become a real tag and be removed with the rest.
    stripped = html_module.unescape(re.sub(r"<[^>]+>", " ", html))
    return normalise(stripped + " " + addresses + " " + metas)


def provenance_ledger() -> dict[str, str]:
    """Parse `derivedFrom` into {string: published source}.

    Values are matched across line breaks because the long entries wrap.
    """
    source = CONTENT.read_text()
    block = source[source.index("export const derivedFrom"):]
    pairs = re.findall(
        r"(?:'((?:[^'\\]|\\.)+)'|\"((?:[^\"\\]|\\.)+)\")\s*:\s*"
        r"(?:'((?:[^'\\]|\\.)+)'|\"((?:[^\"\\]|\\.)+)\")",
        block,
        re.S,
    )
    ledger = {}
    for a, b, c, d in pairs:
        english = (a or b).replace("\\'", "'")
        french = (c or d).replace("\\'", "'")
        ledger[english] = french
    return ledger


def declared_strings() -> list[tuple[str, bool]]:
    """Return every quoted string in content.ts, flagged as added or not.

    A string counts as added when the line above it carries an ADDED marker,
    which is how the two company-framing additions are declared.
    """
    source = CONTENT.read_text()
    # The ledger is data about the check, not page copy, so it is excluded.
    source = source[:source.index("export const derivedFrom")]
    lines = source.splitlines()
    found: list[tuple[str, bool]] = []

    for index, line in enumerate(lines):
        if line.lstrip().startswith(("*", "//", "/*")):
            continue
        # Only the comment directly above a value marks it, otherwise one
        # marker would silently cover the entries that follow it.
        added = "ADDED" in lines[index - 1] if index else False
        for match in re.finditer(r"'((?:[^'\\]|\\.){3,})'", line):
            value = match.group(1).replace("\\'", "'")
            if value.startswith(("http", "mailto")) or "/" == value:
                continue
            found.append((value, added))

    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        default=None,
        help="read the reference from a URL instead of the frozen snapshot",
    )
    args = parser.parse_args()

    source = args.url or REFERENCE.as_uri()

    try:
        reference = reference_text(source)
    except Exception as error:  # noqa: BLE001 - the reason is printed, not handled
        print(f"Could not read {source}: {error}")
        return 1

    ledger = provenance_ledger()
    missing: list[str] = []

    # Whitespace is compared away for the code sample. Stripping tags from the
    # reference inserts a space around every highlighted token, turning
    # `signal<string>(` into `signal < string > (`. What is being proved here
    # is that the characters are the published ones, not that the indentation
    # survived a round trip through HTML.
    if SNIPPET.exists():
        squeeze = lambda text: "".join(normalise(text).split())
        if squeeze(SNIPPET.read_text()) not in squeeze(reference):
            missing.append(f"the code sample in {SNIPPET.name}")

    added: list[str] = []
    translated = 0

    for value, is_added in declared_strings():
        if is_added:
            added.append(value)
            continue
        if normalise(value) in reference:
            continue
        if value in ledger:
            if normalise(ledger[value]) in reference:
                translated += 1
                continue
            missing.append(f"{value}  [source absente: {ledger[value][:60]}]")
            continue
        missing.append(value)

    print(f"Reference: {source}")
    print(f"Declared additions ({len(added)}): {', '.join(added) or 'none'}")
    print(f"Derived from a published string: {translated}")

    if missing:
        print(f"\n{len(missing)} string(s) not found in the reference page:")
        for value in missing:
            print(f"  {value[:96]}")
        print("\nEither the copy was invented, or it needs an ADDED marker.")
        return 1

    print("\nEvery other string comes from the reference page.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
