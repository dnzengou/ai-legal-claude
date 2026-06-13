# Accessibility Statement — AI Legal Assistant

**Conformance target:** [WCAG 2.1 Level AA](https://www.w3.org/TR/WCAG21/), aligned with
US [Section 508](https://www.section508.gov/) and the EU
[Accessibility Act (EAA)](https://ec.europa.eu/social/main.jsp?catId=1202).

**Last reviewed:** 2026-06-13
**Maintainer:** [github.com/dnzengou/ai-legal-claude](https://github.com/dnzengou/ai-legal-claude)

---

## Why this matters

Legal documents change lives. A contract review that a blind reader cannot
follow, or that a colorblind freelancer misreads, is not "accessible-enough" —
it is broken. We treat accessibility defects as functional bugs and ship fixes
on the same priority track as security issues.

---

## Conformance by surface

### Generated PDF reports (`scripts/generate_legal_pdf.py`)

| WCAG SC | What we do | Notes |
|---------|------------|-------|
| 1.3.1 Info & Relationships | Sections marked with semantic headings; data presented in real Tables, not visual approximations | ReportLab `Table` flowables |
| 1.4.1 Use of Color | Every risk indicator carries a **shape** (▲ ■ ●) and a **text label** (HIGH/MEDIUM/LOW) in addition to color | Bar chart uses hatched/dotted/solid fills |
| 1.4.3 Contrast (Minimum) | All foreground text ≥4.5:1 on white; UI elements ≥3:1 | Palette tuned: danger #b91c1c (5.9:1), warning #92400e (7.8:1), success #166534 (7.4:1) |
| 1.4.4 Resize Text | 11pt body / 9pt minimum, with 16pt line-height; vector layout zooms cleanly | No text in raster images |
| 2.4.2 Page Titled | PDF `/Title` set to "Contract Review Report — {contract type}" | Visible in Reader title bar |
| 2.4.6 Headings & Labels | Section headings describe content; tables have explicit header rows | ReportLab TableStyle marks row 0 as header |
| 3.1.1 Language of Page | PDF `/Lang` set to `en-US` via `canvas.setLanguage()` | Per-page hook |
| 3.3.2 Labels or Instructions | Every clause block uses the same 4-label structure: What it says · Why it matters · What you could lose · Recommended change | Plain-language, no jargon |

### Markdown outputs (templates + generated review files)

- Risk levels combine three cues: **shape** (▲ ■ ●), **text** (HIGH/MEDIUM/LOW), **emoji color** (🔴🟡🟢).
- Logical heading order — `##` Section, `###` Sub-section, `####` Clause. No skipped levels.
- Tables include header rows for assistive-tech navigation.
- Plain-English summaries written at ~grade-9 reading level.

### Repo presentation (README, banner SVG, install scripts)

- `assets/banner.svg` exposes `role="img"`, `<title>`, and `<desc>` so screen readers announce a meaningful summary.
- Decorative elements (grid, terminal-window chrome, scale-of-justice icon) marked `aria-hidden="true"`.
- README images carry descriptive `alt` text.
- CLI command names use simple, predictable verbs (`review`, `risks`, `compare`) — no special characters to type.

---

## Known limitations

1. **PDF/UA tagging.** ReportLab does not yet produce fully PDF/UA-1 tagged output. We set `/Lang`, metadata, and use semantic structures, but full structure tree tagging requires additional tooling. Tracked as a future enhancement.
2. **Spoken pronunciation.** Acronyms (NDA, GDPR, HIPAA, CCPA) may be pronounced letter-by-letter by some screen readers. The plain-English summary in every report compensates for this.
3. **Localized output.** Output is currently English only. Translation pipelines for FR/ES/DE are scoped but not yet shipped.

---

## How we test

| Check | Tool / method |
|-------|---------------|
| Color contrast | Manual ratio calculation against `#ffffff` background using the WCAG formula; numbers documented inline in `scripts/generate_legal_pdf.py` COLORS dict |
| PDF metadata | `pdfinfo` / `mutool show <file.pdf> trailer` |
| Screen-reader feel | NVDA on Windows, VoiceOver on macOS — read aloud, verify clause structure is followable |
| Patterns visible in monochrome | Print preview → Grayscale; HIGH/MEDIUM/LOW must remain distinguishable |

---

## Reporting an accessibility bug

Please open an issue at
**[github.com/dnzengou/ai-legal-claude/issues](https://github.com/dnzengou/ai-legal-claude/issues)**
with the label `accessibility`. Include:

- What you were trying to do (e.g., "read a generated review with VoiceOver").
- What broke or was unclear.
- Your assistive tech + version (e.g., "NVDA 2024.4 on Windows 11").
- A screenshot or recording, if possible.

We aim to acknowledge accessibility issues within **48 hours** and ship a fix or workaround within **two weeks**. Security and accessibility issues take precedence over feature work.

---

## Disability is not a special case

Most "accessibility features" — high contrast, clear language, predictable layout, keyboard-friendly tooling — make the product better for everyone. We build with that mindset from the start, not as a retrofit.
