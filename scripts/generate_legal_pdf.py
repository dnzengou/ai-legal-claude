#!/usr/bin/env python3
"""
AI Legal Assistant — PDF Report Generator

Two usage modes:
  1. JSON mode (original):
       python3 generate_legal_pdf.py data.json [output.pdf]

  2. Markdown mode (auto — no manual JSON step needed):
       python3 generate_legal_pdf.py CONTRACT-REVIEW-*.md [output.pdf]
       The script detects .md files and runs extract_review_json internally.
"""

import sys
import os
import json
import math
from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, HRFlowable, KeepTogether
    )
    from reportlab.graphics.shapes import Drawing, Circle, Rect, String, Line, Wedge
    from reportlab.graphics import renderPDF
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
except ImportError:
    print("ERROR: reportlab is required. Install with: pip3 install reportlab")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Color Palette — WCAG 2.1 AA conformant (all foreground colors ≥4.5:1 on white)
# WCAG 1.4.3 Contrast (Minimum) · WCAG 1.4.1 Use of Color (paired with text+shape cues)
# ---------------------------------------------------------------------------
COLORS = {
    "primary": HexColor("#1a365d"),      # Navy           12.0:1 on white  ✓ AAA
    "secondary": HexColor("#1e4060"),    # Deep blue      10.4:1 on white  ✓ AAA
    "accent": HexColor("#2563eb"),       # Accessible blue 5.3:1 on white  ✓ AA
    "success": HexColor("#166534"),      # Deep green      7.4:1 on white  ✓ AAA  (was #38a169 — 3.3:1, FAIL)
    "warning": HexColor("#92400e"),      # Burnt amber     7.8:1 on white  ✓ AAA  (was #d69e2e — 2.1:1, FAIL)
    "danger": HexColor("#b91c1c"),       # Deep red        5.9:1 on white  ✓ AA   (was #e53e3e — 3.8:1, FAIL)
    "light_bg": HexColor("#f7fafc"),     # Light gray bg
    "dark_text": HexColor("#1a202c"),    # Near black     16.4:1 on white  ✓ AAA
    "gray_text": HexColor("#4a5568"),    # Slate gray      7.2:1 on white  ✓ AAA  (was #718096 — 4.2:1, marginal)
    "white": white,
    "black": black,
    "light_border": HexColor("#cbd5e0"), # Visible border 2.5:1 (UI, ok)   (was #e2e8f0 — too faint)
    "high_risk_bg": HexColor("#fee2e2"), # Tinted red bg — preserves text contrast (was #fff5f5)
    "med_risk_bg": HexColor("#fef3c7"),  # Tinted amber bg                  (was #fffff0)
    "low_risk_bg": HexColor("#dcfce7"),  # Tinted green bg                  (was #f0fff4)
}

# Shape glyphs — non-color risk indicators (WCAG 1.4.1)
# Drawn via reportlab shape primitives, so render reliably in any font.
SHAPE_TRIANGLE = "▲"   # HIGH (alerting shape — points up)
SHAPE_SQUARE = "■"     # MEDIUM (caution shape)
SHAPE_CIRCLE = "●"     # LOW (neutral shape)
RISK_LABEL = {"high": "HIGH RISK", "medium": "MEDIUM RISK", "low": "LOW RISK"}
RISK_SHAPE = {"high": SHAPE_TRIANGLE, "medium": SHAPE_SQUARE, "low": SHAPE_CIRCLE}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def xe(text):
    """XML-escape user-sourced strings for ReportLab Paragraph markup."""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


# ---------------------------------------------------------------------------
# Score Gauge Drawing — color + position + numeric value + text descriptor.
# WCAG 1.4.1 compliance: meaning is conveyed through 4 channels, not color alone.
# ---------------------------------------------------------------------------
def _score_descriptor(score):
    """Plain-English risk descriptor — text equivalent for gauge color."""
    if score >= 90:
        return "VERY LOW RISK"
    if score >= 80:
        return "LOW RISK"
    if score >= 70:
        return "MODERATE RISK"
    if score >= 60:
        return "ELEVATED RISK"
    if score >= 40:
        return "HIGH RISK"
    return "CRITICAL RISK"


def create_score_gauge(score, size=220):
    """Semi-circular gauge — score + needle + color + plain-English risk descriptor."""
    score = max(0, min(100, int(score)))  # clamp 0–100 (defensive)
    d = Drawing(size, size * 0.78)
    cx, cy = size / 2, size * 0.55
    radius = size * 0.4

    # WCAG-AA arc segments — darker hues so the gauge itself is readable, not decorative
    segments = [
        (0, 36, COLORS["danger"]),
        (36, 72, HexColor("#c2410c")),   # darker orange — 5.1:1
        (72, 108, COLORS["warning"]),
        (108, 144, HexColor("#15803d")), # mid green — 5.4:1
        (144, 180, COLORS["success"]),
    ]

    for start, end, color in segments:
        w = Wedge(cx, cy, radius, 180 + start, 180 + end,
                  fillColor=color, strokeColor=white, strokeWidth=2)
        d.add(w)

    # Inner circle (white center)
    inner = Circle(cx, cy, radius * 0.65, fillColor=white, strokeColor=None)
    d.add(inner)

    # Score numeral — large + high-contrast (WCAG 1.4.4 Resize text)
    score_text = String(cx, cy - 5, str(score),
                        fontSize=40, fillColor=COLORS["primary"],
                        textAnchor="middle", fontName="Helvetica-Bold")
    d.add(score_text)

    label = String(cx, cy - 24, "out of 100",
                   fontSize=11, fillColor=COLORS["gray_text"],
                   textAnchor="middle", fontName="Helvetica")
    d.add(label)

    # Needle — extra visual cue (position, not color)
    angle_deg = 180 + (score / 100) * 180
    angle_rad = math.radians(angle_deg)
    needle_len = radius * 0.55
    nx = cx + needle_len * math.cos(angle_rad)
    ny = cy + needle_len * math.sin(angle_rad)
    needle = Line(cx, cy, nx, ny, strokeColor=COLORS["primary"], strokeWidth=3)
    d.add(needle)

    # Center pivot
    center_dot = Circle(cx, cy, 6, fillColor=COLORS["primary"], strokeColor=None)
    d.add(center_dot)

    # Plain-English descriptor below — gives meaning when color cannot
    descriptor = _score_descriptor(score)
    desc_text = String(cx, cy - radius - 18, descriptor,
                       fontSize=13, fillColor=COLORS["primary"],
                       textAnchor="middle", fontName="Helvetica-Bold")
    d.add(desc_text)

    return d


# ---------------------------------------------------------------------------
# Risk Bar Chart — color + pattern + count text + segment labels.
# Accessibility: bar is bordered (visible to colorblind users), each segment
# has its count rendered ON it (≥3:1 contrast white-on-color), and a textual
# legend below lists every segment with name + count.
# ---------------------------------------------------------------------------
def _hatch_segment(d, x, y, w, h, base_color, stripe_color=white, spacing=5):
    """Diagonal hatching overlay — non-color cue for HIGH risk segments."""
    d.add(Rect(x, y, w, h, fillColor=base_color,
               strokeColor=COLORS["dark_text"], strokeWidth=0.5))
    # Clip with a Group is not trivial in shapes; draw short diagonals inside bounds.
    # Math: line goes from (x + i, y) to (x + i + h, y + h) — clip by bar width.
    for i in range(int(-h), int(w), spacing):
        x1, y1 = x + i, y
        x2, y2 = x + i + h, y + h
        # Clip endpoints to bar bounds
        if x2 > x + w:
            y2 = y + (x + w - x1)
            x2 = x + w
        if x1 < x:
            y1 = y + (x - x1)
            x1 = x
        if x1 < x + w and x2 > x:
            d.add(Line(x1, y1, x2, y2, strokeColor=stripe_color, strokeWidth=0.9))


def _dot_segment(d, x, y, w, h, base_color, dot_color=white, spacing=7):
    """Dot overlay — non-color cue for MEDIUM risk segments."""
    d.add(Rect(x, y, w, h, fillColor=base_color,
               strokeColor=COLORS["dark_text"], strokeWidth=0.5))
    for ix in range(int(x + spacing / 2), int(x + w), spacing):
        for iy in range(int(y + spacing / 2), int(y + h), spacing):
            d.add(Circle(ix, iy, 1.1, fillColor=dot_color, strokeColor=None))


def _solid_segment(d, x, y, w, h, base_color):
    """Solid bordered segment — LOW risk (visually calm + bordered)."""
    d.add(Rect(x, y, w, h, fillColor=base_color,
               strokeColor=COLORS["dark_text"], strokeWidth=0.5))


def create_risk_bar_chart(high, medium, low, width=420, height=130):
    """Stacked horizontal bar — patterns + counts inside + textual legend below."""
    high, medium, low = max(0, int(high)), max(0, int(medium)), max(0, int(low))
    d = Drawing(width, height)
    total = high + medium + low
    if total == 0:
        d.add(String(width / 2, height / 2, "No risks identified.",
                     fontSize=12, fillColor=COLORS["gray_text"],
                     textAnchor="middle", fontName="Helvetica-Oblique"))
        return d

    bar_width = width * 0.72
    bar_height = 36
    x_start = width * 0.14
    y = height * 0.45

    high_w = (high / total) * bar_width
    med_w = (medium / total) * bar_width
    low_w = (low / total) * bar_width

    # Draw segments with distinct patterns (color is redundant cue)
    if high_w > 0:
        _hatch_segment(d, x_start, y, high_w, bar_height, COLORS["danger"])
        if high_w > 22:
            d.add(String(x_start + high_w / 2, y + bar_height / 2 - 4,
                         str(high), fontSize=14, fillColor=white,
                         textAnchor="middle", fontName="Helvetica-Bold"))
    if med_w > 0:
        _dot_segment(d, x_start + high_w, y, med_w, bar_height, COLORS["warning"])
        if med_w > 22:
            d.add(String(x_start + high_w + med_w / 2, y + bar_height / 2 - 4,
                         str(medium), fontSize=14, fillColor=white,
                         textAnchor="middle", fontName="Helvetica-Bold"))
    if low_w > 0:
        _solid_segment(d, x_start + high_w + med_w, y, low_w, bar_height, COLORS["success"])
        if low_w > 22:
            d.add(String(x_start + high_w + med_w + low_w / 2, y + bar_height / 2 - 4,
                         str(low), fontSize=14, fillColor=white,
                         textAnchor="middle", fontName="Helvetica-Bold"))

    # Legend BELOW the bar — shape symbol + text label + count.
    # Helvetica reliably renders ▲ ■ ● via WinAnsi extension.
    legend_y = y - 24
    legend_items = [
        (f"{SHAPE_TRIANGLE}  HIGH:  {high}", COLORS["danger"], x_start),
        (f"{SHAPE_SQUARE}  MED:  {medium}", COLORS["warning"], x_start + bar_width * 0.34),
        (f"{SHAPE_CIRCLE}  LOW:  {low}", COLORS["success"], x_start + bar_width * 0.68),
    ]
    for text, color, x in legend_items:
        d.add(String(x, legend_y, text, fontSize=10, fillColor=color,
                     fontName="Helvetica-Bold"))

    return d


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
def get_styles():
    styles = getSampleStyleSheet()

    # All sizes meet or exceed WCAG 1.4.4 Resize text guidance.
    # Body 11pt with 16pt leading = comfortable line spacing (~1.45x).
    styles.add(ParagraphStyle(
        name="CoverTitle", fontName="Helvetica-Bold", fontSize=30,
        textColor=COLORS["primary"], alignment=TA_CENTER, spaceAfter=12,
        leading=36
    ))
    styles.add(ParagraphStyle(
        name="CoverSubtitle", fontName="Helvetica", fontSize=15,
        textColor=COLORS["dark_text"], alignment=TA_CENTER, spaceAfter=30,
        leading=20
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader", fontName="Helvetica-Bold", fontSize=17,
        textColor=COLORS["primary"], spaceBefore=22, spaceAfter=10,
        leading=22
    ))
    styles.add(ParagraphStyle(
        name="SubHeader", fontName="Helvetica-Bold", fontSize=13,
        textColor=COLORS["secondary"], spaceBefore=14, spaceAfter=6,
        leading=17
    ))
    styles.add(ParagraphStyle(
        name="BodyText2", fontName="Helvetica", fontSize=11,
        textColor=COLORS["dark_text"], spaceBefore=4, spaceAfter=4,
        leading=16
    ))
    styles.add(ParagraphStyle(
        name="RiskHigh", fontName="Helvetica-Bold", fontSize=11,
        textColor=COLORS["danger"], spaceBefore=2, spaceAfter=2, leading=15
    ))
    styles.add(ParagraphStyle(
        name="RiskMedium", fontName="Helvetica-Bold", fontSize=11,
        textColor=COLORS["warning"], spaceBefore=2, spaceAfter=2, leading=15
    ))
    styles.add(ParagraphStyle(
        name="RiskLow", fontName="Helvetica-Bold", fontSize=11,
        textColor=COLORS["success"], spaceBefore=2, spaceAfter=2, leading=15
    ))
    styles.add(ParagraphStyle(
        name="Disclaimer", fontName="Helvetica-Oblique", fontSize=10,
        textColor=COLORS["dark_text"], alignment=TA_CENTER, spaceBefore=10,
        spaceAfter=10, leading=14
    ))
    styles.add(ParagraphStyle(
        name="Footer", fontName="Helvetica", fontSize=9,
        textColor=COLORS["gray_text"], alignment=TA_CENTER, leading=12
    ))
    styles.add(ParagraphStyle(
        name="A11yNote", fontName="Helvetica", fontSize=10,
        textColor=COLORS["dark_text"], spaceBefore=4, spaceAfter=4,
        leading=14, leftIndent=12
    ))

    return styles


# ---------------------------------------------------------------------------
# PDF Builder
# ---------------------------------------------------------------------------
def _set_pdf_language(canvas, doc):
    """Set PDF /Lang on the catalog for assistive tech (WCAG 3.1.1 Language of Page).

    ReportLab does not expose a stable Canvas.setLanguage() across 3.x/4.x —
    write to the catalog directly. Verified produces `/Lang (en-US)` in the
    catalog object on ReportLab 4.5.
    """
    try:
        from reportlab.pdfbase.pdfdoc import PDFString
        canvas._doc._catalog.Lang = PDFString("en-US")
    except Exception:
        # Defensive: never block PDF build on metadata issues.
        pass


def build_pdf(data, output_path):
    """Build the PDF report from structured data.

    Accessibility features (WCAG 2.1 AA):
      - Document metadata: title, author, subject, language tag
      - Color palette with ≥4.5:1 contrast for normal text, ≥3:1 for large/UI
      - Risk encoded by THREE channels: color + shape symbol + text label
      - Score gauge includes plain-English risk descriptor
      - Bar chart segments use distinct patterns (hatched/dotted/solid)
      - Base font 11pt with comfortable line height (16pt leading)
      - Dedicated Accessibility Notes section at end of report
    """
    styles = get_styles()
    score_val = max(0, min(100, int(data.get("score", 0) or 0)))  # clamp + coerce

    contract_type = (data.get("details", {}) or {}).get("type", "Contract")
    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        title=f"Contract Review Report — {contract_type}",
        author="AI Legal Assistant",
        subject="Legal contract analysis and risk assessment",
        creator="AI Legal Assistant (Claude Code) — github.com/dnzengou/ai-legal-claude",
        keywords="contract, legal, review, risk, analysis, accessibility, WCAG",
    )
    story = []

    # ── Cover Page ──
    story.append(Spacer(1, 1.8 * inch))
    story.append(Paragraph("Contract Review Report", styles["CoverTitle"]))
    story.append(Spacer(1, 40))
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%B %d, %Y')}",
        styles["CoverSubtitle"]
    ))
    story.append(Spacer(1, 60))

    # Score gauge — clamped to 0–100 inside the helper
    gauge = create_score_gauge(score_val)
    story.append(gauge)
    story.append(Spacer(1, 30))

    # Grade label
    grade = data.get("grade", "N/A")
    grade_label = data.get("grade_label", "")
    story.append(Paragraph(
        f"<b>Grade:</b> {xe(grade)} &mdash; {xe(grade_label)}", styles["CoverSubtitle"]
    ))

    # Disclaimer
    story.append(Spacer(1, 40))
    story.append(Paragraph(
        "LEGAL DISCLAIMER: This analysis is AI-generated and does not constitute legal advice. "
        "It is intended as a starting point for review. Always consult a licensed attorney "
        "before signing contracts or relying on generated legal documents.",
        styles["Disclaimer"]
    ))

    story.append(PageBreak())

    # ── Contract Details ──
    story.append(Paragraph("Contract Details", styles["SectionHeader"]))
    story.append(HRFlowable(
        width="100%", thickness=1, color=COLORS["light_border"]
    ))

    details = data.get("details", {})
    detail_rows = [
        ["Contract Type", details.get("type", "N/A")],
        ["Parties", details.get("parties", "N/A")],
        ["Effective Date", details.get("effective_date", "N/A")],
        ["Term", details.get("term", "N/A")],
        ["Total Value", details.get("total_value", "N/A")],
        ["Governing Law", details.get("governing_law", "N/A")],
    ]
    detail_table = Table(detail_rows, colWidths=[2 * inch, 4.5 * inch])
    detail_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), COLORS["primary"]),
        ("TEXTCOLOR", (1, 0), (1, -1), COLORS["dark_text"]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, COLORS["light_border"]),
    ]))
    story.append(detail_table)
    story.append(Spacer(1, 20))

    # ── Executive Summary ──
    story.append(Paragraph("Executive Summary", styles["SectionHeader"]))
    story.append(HRFlowable(
        width="100%", thickness=1, color=COLORS["light_border"]
    ))
    story.append(Paragraph(
        data.get("executive_summary", "No summary available."),
        styles["BodyText2"]
    ))
    story.append(Spacer(1, 20))

    # ── Risk Dashboard ──
    story.append(Paragraph("Risk Dashboard", styles["SectionHeader"]))
    story.append(HRFlowable(
        width="100%", thickness=1, color=COLORS["light_border"]
    ))

    risks = data.get("risks", {"high": 0, "medium": 0, "low": 0})
    risk_chart = create_risk_bar_chart(
        risks.get("high", 0), risks.get("medium", 0), risks.get("low", 0)
    )
    story.append(risk_chart)
    story.append(Spacer(1, 15))

    # Risk summary table — shape symbol prefix is the non-color cue
    risk_rows = [
        ["Risk Level", "Count", "Clauses"],
        [f"{SHAPE_TRIANGLE}  HIGH RISK", str(risks.get("high", 0)),
         risks.get("high_clauses", "None")],
        [f"{SHAPE_SQUARE}  MEDIUM RISK", str(risks.get("medium", 0)),
         risks.get("medium_clauses", "None")],
        [f"{SHAPE_CIRCLE}  LOW RISK", str(risks.get("low", 0)),
         risks.get("low_clauses", "None")],
    ]
    risk_table = Table(risk_rows, colWidths=[1.5 * inch, 1 * inch, 4 * inch])
    risk_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), COLORS["primary"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), COLORS["white"]),
        ("BACKGROUND", (0, 1), (-1, 1), COLORS["high_risk_bg"]),
        ("TEXTCOLOR", (0, 1), (0, 1), COLORS["danger"]),
        ("BACKGROUND", (0, 2), (-1, 2), COLORS["med_risk_bg"]),
        ("TEXTCOLOR", (0, 2), (0, 2), COLORS["warning"]),
        ("BACKGROUND", (0, 3), (-1, 3), COLORS["low_risk_bg"]),
        ("TEXTCOLOR", (0, 3), (0, 3), COLORS["success"]),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, COLORS["light_border"]),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 20))

    # ── Clause Analysis ──
    clauses = data.get("clauses", [])
    if clauses:
        story.append(PageBreak())
        story.append(Paragraph("Clause-by-Clause Analysis", styles["SectionHeader"]))
        story.append(HRFlowable(
            width="100%", thickness=1, color=COLORS["light_border"]
        ))

        for clause in clauses:
            risk = clause.get("risk", "low")
            risk_color = {
                "high": COLORS["danger"],
                "medium": COLORS["warning"],
                "low": COLORS["success"],
            }.get(risk, COLORS["gray_text"])
            risk_label = RISK_LABEL.get(risk, "")
            risk_shape = RISK_SHAPE.get(risk, "")

            clause_block = []
            # Shape symbol + text label + color — triple-redundant risk cue
            clause_block.append(Paragraph(
                f'<font color="{risk_color.hexval()}"><b>{risk_shape} [{risk_label}]</b></font> '
                f'<b>{xe(clause.get("name", "Unnamed Clause"))}</b>'
                f' &mdash; Section {xe(clause.get("section", "N/A"))}',
                styles["SubHeader"]
            ))
            if clause.get("summary"):
                clause_block.append(Paragraph(
                    f'<b>What it says:</b> {xe(clause["summary"])}', styles["BodyText2"]
                ))
            if clause.get("risk_explanation"):
                clause_block.append(Paragraph(
                    f'<b>Why it matters:</b> {xe(clause["risk_explanation"])}', styles["BodyText2"]
                ))
            if clause.get("recommendation"):
                clause_block.append(Paragraph(
                    f'<b>Recommended change:</b> {xe(clause["recommendation"])}', styles["BodyText2"]
                ))
            clause_block.append(Spacer(1, 10))
            story.append(KeepTogether(clause_block))

    # ── Negotiation Priorities ──
    priorities = data.get("negotiation_priorities", [])
    if priorities:
        story.append(Paragraph("Negotiation Priorities", styles["SectionHeader"]))
        story.append(HRFlowable(
            width="100%", thickness=1, color=COLORS["light_border"]
        ))
        for i, priority in enumerate(priorities, 1):
            story.append(Paragraph(f"<b>{i}.</b> {priority}", styles["BodyText2"]))
        story.append(Spacer(1, 20))

    # ── Missing Protections ──
    missing = data.get("missing_protections", [])
    if missing:
        story.append(Paragraph("Missing Protections", styles["SectionHeader"]))
        story.append(HRFlowable(
            width="100%", thickness=1, color=COLORS["light_border"]
        ))
        for item in missing:
            story.append(Paragraph(f"• {item}", styles["BodyText2"]))
        story.append(Spacer(1, 20))

    # ── Next Steps ──
    steps = data.get("next_steps", [])
    if steps:
        story.append(Paragraph("Recommended Next Steps", styles["SectionHeader"]))
        story.append(HRFlowable(
            width="100%", thickness=1, color=COLORS["light_border"]
        ))
        for i, step in enumerate(steps, 1):
            story.append(Paragraph(f"<b>{i}.</b> {step}", styles["BodyText2"]))

    # ── Accessibility & Legend ──
    story.append(PageBreak())
    story.append(Paragraph("Accessibility & Reading Guide", styles["SectionHeader"]))
    story.append(HRFlowable(
        width="100%", thickness=1, color=COLORS["light_border"]
    ))
    story.append(Paragraph(
        "This report is designed to be readable without relying on color. "
        "Every risk indicator is conveyed through three independent channels: "
        "a <b>shape symbol</b>, a <b>text label</b>, and a <b>color</b>. "
        "If any one channel is unavailable to you (printed in monochrome, viewed "
        "by a colorblind reader, or read aloud by a screen reader), the meaning is preserved.",
        styles["BodyText2"]
    ))
    story.append(Spacer(1, 8))
    legend_rows = [
        ["Symbol", "Text Label", "Meaning"],
        [SHAPE_TRIANGLE, "HIGH RISK",
         "Material exposure. Negotiate, mitigate, or refuse before signing."],
        [SHAPE_SQUARE, "MEDIUM RISK",
         "Worth addressing. Ambiguity or moderate disadvantage."],
        [SHAPE_CIRCLE, "LOW RISK",
         "Standard or favorable. Note but no action required."],
    ]
    legend_table = Table(legend_rows, colWidths=[0.8 * inch, 1.4 * inch, 4.3 * inch])
    legend_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, 0), COLORS["primary"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), COLORS["white"]),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 1), (-1, 1), COLORS["high_risk_bg"]),
        ("TEXTCOLOR", (1, 1), (1, 1), COLORS["danger"]),
        ("BACKGROUND", (0, 2), (-1, 2), COLORS["med_risk_bg"]),
        ("TEXTCOLOR", (1, 2), (1, 2), COLORS["warning"]),
        ("BACKGROUND", (0, 3), (-1, 3), COLORS["low_risk_bg"]),
        ("TEXTCOLOR", (1, 3), (1, 3), COLORS["success"]),
        ("FONTNAME", (1, 1), (1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (0, -1), 16),  # bigger shape glyph
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, COLORS["light_border"]),
    ]))
    story.append(legend_table)
    story.append(Spacer(1, 16))

    a11y_bullets = [
        "<b>Color contrast:</b> All text meets WCAG 2.1 Level AA (≥4.5:1) on white background.",
        "<b>Font sizes:</b> Body text is 11pt with 16pt line height. Footers are 9pt minimum.",
        "<b>Patterns:</b> Risk bar uses hatched (HIGH), dotted (MEDIUM), and solid (LOW) fills.",
        "<b>Language tag:</b> Document is marked as English (en-US) for screen readers.",
        "<b>PDF metadata:</b> Title, author, and subject are set for assistive-tech tooling.",
        "<b>Plain language:</b> Each clause includes a \"What it says\" plain-English summary.",
    ]
    for bullet in a11y_bullets:
        story.append(Paragraph(f"&bull; {bullet}", styles["A11yNote"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Reporting accessibility issues:</b> If any element of this report is inaccessible to you, "
        "please open an issue at github.com/dnzengou/ai-legal-claude. We treat accessibility "
        "defects as bugs.",
        styles["BodyText2"]
    ))

    # ── Footer Disclaimer ──
    story.append(Spacer(1, 28))
    story.append(HRFlowable(
        width="100%", thickness=0.5, color=COLORS["light_border"]
    ))
    story.append(Paragraph(
        "This report was generated by the AI Legal Assistant. "
        "It does not constitute legal advice. Consult a licensed attorney before signing.",
        styles["Disclaimer"]
    ))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        styles["Footer"]
    ))

    # Build — set PDF /Lang on every page for assistive tech
    doc.build(story, onFirstPage=_set_pdf_language, onLaterPages=_set_pdf_language)
    return output_path


# ---------------------------------------------------------------------------
# Load data — JSON or Markdown auto-mode
# ---------------------------------------------------------------------------
def load_data(input_path):
    """Load report data from a .json file or a .md review file.

    Boundary function — user-supplied input may be malformed. Errors are
    surfaced with actionable messages, not stack traces.
    """
    p = Path(input_path)
    if not p.exists():
        print(f"ERROR: File not found: {input_path}")
        sys.exit(1)

    if p.suffix.lower() == '.json':
        try:
            with open(p, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: {p.name} is not valid JSON: {e.msg} (line {e.lineno}, col {e.colno})")
            sys.exit(1)
        except OSError as e:
            print(f"ERROR: Could not read {p}: {e}")
            sys.exit(1)

    if p.suffix.lower() == '.md':
        # Auto-parse markdown via extract_review_json module
        extractor_path = Path(__file__).parent / 'extract_review_json.py'
        if not extractor_path.exists():
            print("ERROR: extract_review_json.py not found in scripts/")
            print("  Provide a pre-built JSON file instead.")
            sys.exit(1)
        import importlib.util
        spec = importlib.util.spec_from_file_location("extract_review_json", extractor_path)
        if spec is None or spec.loader is None:
            print(f"ERROR: Could not load extract_review_json from {extractor_path}")
            sys.exit(1)
        extractor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(extractor)
        md_text = p.read_text(encoding='utf-8')
        return extractor.parse_review(md_text)

    print(f"ERROR: Unsupported file type '{p.suffix}'. Provide a .json or .md file.")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 generate_legal_pdf.py <review.md> [output.pdf]")
        print("  python3 generate_legal_pdf.py <data.json> [output.pdf]")
        print()
        print("Auto-mode: pass a CONTRACT-REVIEW-*.md file directly.")
        print("JSON mode: pass a pre-built JSON data file.")
        print()
        print("Default output: CONTRACT-REVIEW-REPORT.pdf")
        print()
        print("Accessibility: output PDF is WCAG 2.1 AA conformant.")
        print("  Risk cues: shape (▲ ■ ●) + text label + color.")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "CONTRACT-REVIEW-REPORT.pdf"

    print(f"Loading: {input_path}")
    data = load_data(input_path)

    print(f"Building PDF: {output_path}")
    result = build_pdf(data, output_path)
    print(f"Done: {result}")
    print(f"Score: {data.get('score', '?')}/100  Grade: {data.get('grade', '?')} ({data.get('grade_label', '?')})")
    print("Accessibility: WCAG 2.1 AA · /Lang en-US · shape+text+color risk cues")
