"""Write the fictional preview as markdown plus one HTML page."""

from __future__ import annotations

import html
from pathlib import Path

from empack import __version__


def write_preview(
    out_dir: Path,
    report: str,
    documents: list[tuple[str, str]],
    generated_at: str,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, markdown in documents:
        (out_dir / f"{name}.md").write_text(markdown, encoding="utf-8")
    index = out_dir / "index.html"
    index.write_text(
        build_index(report, documents, generated_at),
        encoding="utf-8",
    )
    return index


def build_index(
    report: str,
    documents: list[tuple[str, str]],
    generated_at: str,
) -> str:
    nav = "\n".join(
        f'<a href="#{html.escape(name)}">{html.escape(name)}</a>'
        for name, _markdown in documents
    )
    articles = "\n".join(
        _article(name, markdown) for name, markdown in documents
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Eng Manager Skills Pack — fictional preview</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #1c1915;
      --muted: #5e584e;
      --line: #ddd6ca;
      --paper: #f6f3ee;
      --card: #fffdf9;
      --banner: #f3e6d4;
      --banner-ink: #6a3d22;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--paper);
      font-family: Georgia, "Iowan Old Style", "Palatino Linotype", Palatino, serif;
      line-height: 1.5;
    }}
    header, main {{
      width: min(880px, calc(100% - 32px));
      margin: 0 auto;
    }}
    header {{ padding: 32px 0 8px; }}
    h1 {{
      font-size: 2rem;
      line-height: 1.2;
      margin: 0 0 8px;
    }}
    .lede, .meta {{ color: var(--muted); }}
    .command, .report {{
      font-family: ui-monospace, "Cascadia Code", "Source Code Pro", Menlo, Consolas, monospace;
      font-size: 0.92rem;
    }}
    .command {{
      background: var(--card);
      border: 1px solid var(--line);
      padding: 10px 12px;
    }}
    nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px 16px;
      margin: 16px 0;
    }}
    nav a {{ color: var(--ink); }}
    .report {{
      white-space: pre-wrap;
      background: var(--card);
      border: 1px solid var(--line);
      padding: 12px 14px;
    }}
    article {{
      background: var(--card);
      border: 1px solid var(--line);
      padding: 8px 28px 24px;
      margin: 20px 0 32px;
    }}
    article h2, article h3 {{ line-height: 1.25; }}
    blockquote {{
      background: var(--banner);
      color: var(--banner-ink);
      margin: 16px 0;
      padding: 10px 14px;
      border-left: 4px solid var(--banner-ink);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
    }}
    th, td {{
      text-align: left;
      vertical-align: top;
      border-top: 1px solid var(--line);
      padding: 6px 8px;
    }}
    code {{
      font-family: ui-monospace, "Cascadia Code", "Source Code Pro", Menlo, Consolas, monospace;
      font-size: 0.9em;
    }}
    footer {{
      width: min(880px, calc(100% - 32px));
      margin: 0 auto 40px;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <header>
    <h1>Eng Manager Skills Pack</h1>
    <p class="lede">Fictional preview rendered from the four bundled examples. This page is not a record of a real team.</p>
    <p class="command">python3 -m empack demo</p>
    <p class="meta">Generated <time datetime="{html.escape(generated_at)}">{html.escape(generated_at)}</time> by empack {html.escape(__version__)}. READMEs: English, Simplified Chinese, Traditional Chinese, Japanese.</p>
    <nav>{nav}</nav>
    <pre class="report">{html.escape(report.strip())}</pre>
  </header>
  <main>
    {articles}
  </main>
  <footer>
    <p>Each article is the markdown file written beside this page. Facts come from skills/&lt;name&gt;/assets/example-input.json. No usage, download, or feedback numbers are collected here.</p>
  </footer>
</body>
</html>
"""


def _article(name: str, markdown: str) -> str:
    title = html.escape(name)
    return (
        f'<article id="{title}">\n'
        f"<h2>{title}</h2>\n"
        f"{markdown_to_html(markdown)}\n"
        "</article>"
    )


def markdown_to_html(markdown: str) -> str:
    """Render the small markdown subset these templates emit."""
    lines = markdown.splitlines()
    blocks: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("|"):
            table: list[str] = []
            while index < len(lines) and lines[index].startswith("|"):
                table.append(lines[index])
                index += 1
            blocks.append(_table(table))
            continue
        if line.startswith("> "):
            quote: list[str] = []
            while index < len(lines) and lines[index].startswith("> "):
                quote.append(lines[index][2:])
                index += 1
            blocks.append("<blockquote><p>" + "<br>".join(html.escape(item) for item in quote) + "</p></blockquote>")
            continue
        if line.startswith("- ") or line.startswith("  - "):
            items: list[str] = []
            while index < len(lines) and (
                lines[index].startswith("- ") or lines[index].startswith("  - ")
            ):
                depth = 1 if lines[index].startswith("  - ") else 0
                text = lines[index][4:] if depth else lines[index][2:]
                items.append(f"<li>{html.escape(text)}</li>")
                index += 1
            blocks.append("<ul>\n" + "\n".join(items) + "\n</ul>")
            continue
        if line.startswith("### "):
            blocks.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("## "):
            blocks.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("# "):
            blocks.append(f"<h2>{html.escape(line[2:])}</h2>")
        elif line.strip() == "---":
            blocks.append("<hr>")
        elif line.strip() == "":
            pass
        else:
            blocks.append(f"<p>{html.escape(line)}</p>")
        index += 1
    return "\n".join(blocks)


def _table(lines: list[str]) -> str:
    rows: list[list[str]] = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(set(cell) <= {"-", ":"} and cell for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        return ""
    head = "".join(f"<th>{html.escape(cell)}</th>" for cell in rows[0])
    body = "\n".join(
        "<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in row) + "</tr>"
        for row in rows[1:]
    )
    return f"<table>\n<thead><tr>{head}</tr></thead>\n<tbody>\n{body}\n</tbody>\n</table>"

