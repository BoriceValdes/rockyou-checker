import re
import sys
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle,
    HRFlowable, ListFlowable, ListItem,
)
SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])

text = SRC.read_text(encoding="utf-8")
lines = text.split("\n")

styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    name="H1", parent=styles["Heading1"], fontSize=20, leading=24,
    spaceBefore=18, spaceAfter=10, textColor=colors.HexColor("#1a1a2e"),
))
styles.add(ParagraphStyle(
    name="H2", parent=styles["Heading2"], fontSize=15, leading=19,
    spaceBefore=16, spaceAfter=8, textColor=colors.HexColor("#16213e"),
))
styles.add(ParagraphStyle(
    name="H3", parent=styles["Heading3"], fontSize=12.5, leading=16,
    spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#0f3460"),
))
styles.add(ParagraphStyle(
    name="Body", parent=styles["BodyText"], fontSize=10, leading=14.5,
    spaceAfter=6, fontName="Helvetica",
))
styles.add(ParagraphStyle(
    name="Quote", parent=styles["Body"], leftIndent=12, textColor=colors.HexColor("#444444"),
    borderColor=colors.HexColor("#cccccc"), borderWidth=0, backColor=colors.HexColor("#f5f5f7"),
))
styles.add(ParagraphStyle(
    name="CodeBlock", fontName="Courier", fontSize=7.6, leading=9.6,
    backColor=colors.HexColor("#f4f4f6"), spaceAfter=8, spaceBefore=2,
))
styles.add(ParagraphStyle(
    name="BulletText", parent=styles["Body"], leftIndent=0, spaceAfter=3,
))
styles.add(ParagraphStyle(
    name="TableCell", parent=styles["Body"], fontSize=8.7, leading=11.5, spaceAfter=0,
))

def inline_md(s: str) -> str:
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<link href="\2" color="#0b5fff">\1</link>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*(?!\*)([^*]+)\*(?!\*)", r"<i>\1</i>", s)
    s = re.sub(r"`([^`]+)`", r'<font face="Courier" size="8.7" color="#c7254e">\1</font>', s)
    return s

story = []
i = 0
n = len(lines)

def flush_table(rows):
    data = [[Paragraph(inline_md(c.strip()), styles["TableCell"]) for c in r] for r in rows]
    ncols = len(rows[0])
    avail_width = 170 * mm
    col_w = avail_width / ncols
    t = Table(data, colWidths=[col_w] * ncols, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3460")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7fa")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

while i < n:
    line = lines[i]

    if line.strip() == "":
        i += 1
        continue

    if line.strip() == "---":
        story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#dddddd"), spaceBefore=6, spaceAfter=10))
        i += 1
        continue

    if line.startswith("```"):
        i += 1
        code_lines = []
        while i < n and not lines[i].startswith("```"):
            code_lines.append(lines[i])
            i += 1
        i += 1
        code_text = "\n".join(code_lines)
        story.append(Preformatted(code_text, styles["CodeBlock"]))
        continue

    m = re.match(r"^(#{1,4})\s+(.*)$", line)
    if m:
        level = len(m.group(1))
        content = inline_md(m.group(2).strip())
        style = {1: "H1", 2: "H2", 3: "H3", 4: "H3"}[min(level, 4)]
        story.append(Paragraph(content, styles[style]))
        i += 1
        continue

    if line.strip().startswith(">"):
        quote_lines = []
        while i < n and lines[i].strip().startswith(">"):
            quote_lines.append(lines[i].strip().lstrip(">").strip())
            i += 1
        story.append(Paragraph(inline_md(" ".join(quote_lines)), styles["Quote"]))
        story.append(Spacer(1, 4))
        continue

    if re.match(r"^\|.*\|\s*$", line.strip()):
        table_lines = []
        while i < n and re.match(r"^\|.*\|\s*$", lines[i].strip()):
            table_lines.append(lines[i].strip())
            i += 1
        rows = []
        for tl in table_lines:
            cells = [c for c in tl.strip("|").split("|")]
            if re.match(r"^\s*:?-+:?\s*$", cells[0]) and all(re.match(r"^\s*:?-+:?\s*$", c) for c in cells):
                continue
            rows.append(cells)
        if rows:
            flush_table(rows)
        continue

    if re.match(r"^\s*\d+\.\s+", line):
        items = []
        while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
            txt = re.sub(r"^\s*\d+\.\s+", "", lines[i])
            items.append(ListItem(Paragraph(inline_md(txt), styles["BulletText"])))
            i += 1
        story.append(ListFlowable(items, bulletType="1", start=1, leftIndent=16, spaceAfter=6))
        continue

    if re.match(r"^\s*-\s+", line):
        items = []
        while i < n and re.match(r"^\s*-\s+", lines[i]):
            txt = re.sub(r"^\s*-\s+", "", lines[i])
            items.append(ListItem(Paragraph(inline_md(txt), styles["BulletText"])))
            i += 1
        story.append(ListFlowable(items, bulletType="bullet", start="•", leftIndent=16, spaceAfter=6))
        continue

    para_lines = [line]
    i += 1
    while i < n and lines[i].strip() != "" and not lines[i].startswith("#") and lines[i].strip() != "---" and not lines[i].startswith("```") and not re.match(r"^\|.*\|\s*$", lines[i].strip()) and not re.match(r"^\s*[-\d]", lines[i]):
        para_lines.append(lines[i])
        i += 1
    story.append(Paragraph(inline_md(" ".join(para_lines)), styles["Body"]))

doc = SimpleDocTemplate(
    str(OUT), pagesize=A4,
    leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=18 * mm,
    title="RockYou Checker - README", author="RockYou Checker",
)
doc.build(story)
print(f"OK -> {OUT}")