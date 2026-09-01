#!/usr/bin/env python3
"""Generate the course landing page listing every slide deck.

Reads slides/*.qmd (the source of truth, always present in the repo) rather
than the rendered output, so decks that were not re-rendered on an
incremental build still get listed.
"""

import html
import re
import sys
from pathlib import Path

SLIDES = Path(__file__).resolve().parent.parent
DOCS = SLIDES / "docs"

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
SUBTITLE = re.compile(r"^subtitle:\s*(.+?)\s*$", re.MULTILINE)
SECTION = re.compile(r"^#\s+(?!#)(.+?)\s*$", re.MULTILINE)
ATTRS = re.compile(r"\{[^}]*\}\s*$")


def day_number(path):
    m = re.search(r"(\d+)", path.stem)
    return int(m.group(1)) if m else 0


def topic(path):
    """First top-level section heading, falling back to the subtitle."""
    text = path.read_text()
    fm = FRONTMATTER.match(text)
    body = text[fm.end():] if fm else text
    m = SECTION.search(body)
    if m:
        return ATTRS.sub("", m.group(1)).strip()
    if fm:
        m = SUBTITLE.search(fm.group(1))
        if m:
            return m.group(1).strip().strip("\"'")
    return ""


def main():
    decks = sorted(SLIDES.glob("day*.qmd"), key=day_number)
    if not decks:
        print("No decks found; not writing index.html", file=sys.stderr)
        return 1

    rows = []
    for deck in decks:
        stem = deck.stem
        label = f"Day {day_number(deck)}" if day_number(deck) else stem
        rows.append(
            f"""      <li class="deck">
        <a class="deck-link" href="{stem}.html">
          <span class="day">{html.escape(label)}</span>
          <span class="topic">{html.escape(topic(deck))}</span>
        </a>
        <a class="pdf" href="{stem}.pdf">PDF</a>
      </li>"""
        )

    syllabus = ""
    if (DOCS / "syllabus.pdf").exists():
        syllabus = '\n      <a href="syllabus.pdf">Syllabus</a>'

    page = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>CSC 4553 &middot; Operating Systems</title>
    <style>
      :root {{
        color-scheme: light dark;
        --bg: #ffffff;
        --fg: #1c1c1c;
        --muted: #666666;
        --accent: #40666e;
        --card: #f5f6f7;
        --border: #e2e4e6;
      }}
      @media (prefers-color-scheme: dark) {{
        :root {{
          --bg: #16181a;
          --fg: #ececec;
          --muted: #9aa0a6;
          --accent: #7fb3bd;
          --card: #202325;
          --border: #2e3235;
        }}
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        padding: 3rem 1.25rem 4rem;
        background: var(--bg);
        color: var(--fg);
        font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
          Helvetica, Arial, sans-serif;
      }}
      main {{ max-width: 44rem; margin: 0 auto; }}
      h1 {{ margin: 0; font-size: 2rem; letter-spacing: -0.01em; }}
      .sub {{ margin: 0.35rem 0 0; color: var(--muted); }}
      .links {{ margin-top: 0.75rem; }}
      .links a {{ color: var(--accent); }}
      ul {{ list-style: none; margin: 2rem 0 0; padding: 0; }}
      .deck {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.9rem 1rem;
        margin-bottom: 0.6rem;
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 8px;
      }}
      .deck-link {{
        flex: 1;
        display: flex;
        flex-wrap: wrap;
        align-items: baseline;
        gap: 0.25rem 0.75rem;
        text-decoration: none;
        color: inherit;
        min-width: 0;
      }}
      .deck-link:hover .day {{ text-decoration: underline; }}
      .day {{ font-weight: 600; color: var(--accent); }}
      .topic {{ color: var(--muted); }}
      .pdf {{
        flex: none;
        font-size: 0.8rem;
        letter-spacing: 0.04em;
        text-decoration: none;
        color: var(--muted);
        border: 1px solid var(--border);
        border-radius: 5px;
        padding: 0.2rem 0.5rem;
      }}
      .pdf:hover {{ color: var(--accent); border-color: var(--accent); }}
    </style>
  </head>
  <body>
    <main>
      <h1>CSC 4553</h1>
      <p class="sub">Operating Systems &middot; Fall 2026</p>
      <p class="links">{syllabus}
      </p>
      <ul>
{chr(10).join(rows)}
      </ul>
    </main>
  </body>
</html>
"""

    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "index.html").write_text(page)
    print(f"Wrote {DOCS / 'index.html'} with {len(decks)} deck(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
