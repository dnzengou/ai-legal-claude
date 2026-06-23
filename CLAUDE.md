# AI Legal Assistant — Claude Code Skills Suite

Production-ready legal analysis system. 16 skills, 5 parallel agents, PDF report generation.

## What This Does

Drops into Claude Code as slash commands. No server. No subscription. Runs on your existing Claude Code + Anthropic API.

```
/legal review <file>          → 5 parallel agents → scored contract report
/legal risks <file>           → clause-by-clause risk scoring
/legal compare <f1> <f2>      → side-by-side contract diff
/legal plain <file>           → legalese → plain English
/legal negotiate <file>       → counter-proposals + email template
/legal missing <file>         → missing protections finder
/legal batch <f1> <f2> ...    → multi-contract parallel review
/legal due-diligence <file>   → investment/M&A 5-lens due diligence review
/legal nda <description>      → generate custom NDA
/legal terms <url>            → generate Terms of Service
/legal privacy <url>          → generate Privacy Policy
/legal agreement <type>       → generate business agreements
/legal freelancer <file>      → freelancer-perspective review
/legal gig-economy <file>     → gig worker / platform contract review
/legal compliance <url>       → GDPR/CCPA/ADA/PCI/HIPAA gap analysis
/legal report-pdf             → professional PDF from latest review
```

## Architecture

```
legal/SKILL.md               ← main router (invoked by /legal)
skills/<name>/SKILL.md       ← 16 sub-skills, each handles one command
agents/legal-*.md            ← 5 specialist agents (spawned in parallel by /legal review)
scripts/generate_legal_pdf.py ← ReportLab PDF builder
scripts/extract_review_json.py ← parses review markdown → JSON for PDF
templates/                   ← output templates
```

## How /legal review Works (5-Agent CoT Pipeline)

```
User: /legal review contract.pdf
  │
  ├─ Phase 1: Ingest & classify contract
  │
  ├─ Phase 2: Spawn 5 agents IN PARALLEL
  │   ├─ [20%] legal-clauses.md    → clause inventory
  │   ├─ [25%] legal-risks.md      → risk scores
  │   ├─ [20%] legal-compliance.md → regulatory checks
  │   ├─ [15%] legal-terms.md      → obligations timeline
  │   └─ [20%] legal-recommendations.md → specific fixes
  │
  └─ Phase 3: Aggregate → Contract Safety Score → CONTRACT-REVIEW.md
```

## Output Files

All generated files land in the current working directory:

| Command | Output File |
|---------|-------------|
| `/legal review` | `CONTRACT-REVIEW-[name]-[date].md` |
| `/legal risks` | `RISK-ANALYSIS-[date].md` |
| `/legal compare` | `CONTRACT-COMPARISON-[date].md` |
| `/legal negotiate` | `NEGOTIATION-STRATEGY-[name].md` |
| `/legal nda` | `NDA-[parties]-[date].md` |
| `/legal terms` | `TERMS-OF-SERVICE-[company]-[date].md` |
| `/legal privacy` | `PRIVACY-POLICY-[company]-[date].md` |
| `/legal agreement` | `AGREEMENT-[type]-[date].md` |
| `/legal batch` | `BATCH-REVIEW-[date].md` |
| `/legal due-diligence` | `DUE-DILIGENCE-[target]-[date].md` |
| `/legal report-pdf` | `CONTRACT-REVIEW-REPORT.pdf` |

## CoT Multi-Agent Examples

### Example 1: Freelancer reviewing a client contract
```
/legal review client-contract.pdf
# → Safety score, all risks, negotiation priorities in ~60 seconds

/legal negotiate client-contract.pdf
# → Counter-proposals + ready-to-send email

/legal report-pdf
# → Professional PDF to send to the client
```

### Example 2: Startup due diligence batch
```
/legal batch vendor1.pdf vendor2.pdf vendor3.pdf
# → Parallel review of all 3, comparative risk table, highest-risk flagged first
```

### Example 3: Website compliance audit
```
/legal compliance https://mysite.com
# → GDPR/CCPA/ADA/PCI scorecard + prioritized fix list

/legal privacy https://mysite.com
# → Generated compliant privacy policy

/legal terms https://mysite.com
# → Generated Terms of Service
```

## Installation

**Mac/Linux:**
```bash
./install.sh
```

**Windows:**
```powershell
.\install.ps1
```

**PDF reports require Python + ReportLab:**
```bash
pip install reportlab
```

## Rules for Claude When Working in This Repo

1. Legal outputs always include the disclaimer — never omit it
2. Output markdown files to the current working directory unless the user specifies otherwise
3. Never claim to provide legal advice — only legal analysis and document drafting assistance
4. Always surface risks even when the user seems to want a green light
5. All file names use the templates defined above — stay consistent
6. Risk levels: 🔴 High (7-10), 🟡 Medium (4-6), 🟢 Low (1-3)


---

## Changelog

### 2026-06-23 — EvoMetaClaw Epoch 3 — 4 Mutations, 16 Skills, New investment_ma Niche

- **M1 MUTATE legal-nda** (KafCa token-trim): 15-item verbose section list → compact 15-row table. 3-line `--- PLAIN ENGLISH ---` annotation blocks → inline `> **Plain English:** ...` format. Output template collapsed §3–§15 to shorthand reference. Added "No verbose per-section repetition" guideline. ~28% output token reduction.
- **M2 MUTATE legal-terms** (KafCa token-trim): 16 verbose subsections (2.1–2.16) with bullet lists → compact 3-column table (§ | Section | Key clause · Include when). Output template collapsed §3–§15. Added "No redundant subsection repetition" guideline. ~25% output token reduction.
- **M3 MUTATE legal-review**: Phase 1.4 Compliance Pre-Detection added after metadata extraction. Scans for SOC2 signals (`SOC 2`, `AICPA`, `Type II`, `audit report`, `trust service criteria`) and CAN-SPAM signals (`commercial email`, `unsubscribe`, `opt-out`, `bulk email`). Passes `COMPLIANCE_FLAGS` to all 5 subagents. CAN-SPAM penalty: $51,744/email surfaced proactively.
- **M4 SPLICE legal-review + legal-compare → legal-due-diligence** (new skill, 16th command): Investment/M&A due diligence specialist. 5-lens framework: deal-killers (30%), liability exposure (25%), IP & technology (20%), revenue & customer risk (15%), reps/warranties (10%). Change-of-control analysis mandatory on every contract. Due Diligence Score 0–100. Command: `/legal due-diligence <file> [comparison-file]`.
- **All 7 EvoMetaClaw state files updated**: `population.json` (epoch→3, pop_size→16, legal-due-diligence born provisional), `lineage.json` (epoch 3 nodes + edges), `q_table.json` (all 11 Q-states through epoch 3), `circuit_breaker_log.json` (pre/post epoch 3), `matrix_thoughts.json` (epoch 3 entry), `config.yml` (pop_size 15→16), `legal-orchestration-genome.md` (v3 — due-diligence routing, investment_ma niche, epoch 4 queue).
- **Install scripts updated**: `install.sh` and `install.ps1` both updated to 16 Skills, added `legal-gig-economy` (was missing) and `legal-due-diligence` to SKILLS arrays. Command reference updated with all 16 commands.
- **README updated**: All 16 Commands table, `legal-gig-economy` row added to Document Generation, `legal-due-diligence` row added to Contract Analysis.
- **EvoMetaClaw epoch 3 complete**: population_size=16, diversity=0.92 (new niche), circuit_breaker=healthy. 3 mutations ACCEPT (avg 0.863), 1 ACCEPT_PROVISIONAL (legal-due-diligence, fitness=0.0, monitor 3 sessions). Epoch 4 queue: legal-privacy KafCa trim, legal-agreement KafCa trim, SOC2 full section in legal-compliance, legal-due-diligence fitness calibration, SPLICE → legal-portfolio-review.

### 2026-06-13 — EvoMetaClaw Epoch 2 — 4 Mutations, State Complete

- **M1 MUTATE legal-plain** (KafCa token-trim): Removed original-text quoting (single largest token waste — user has the contract). Flags changed to inline emoji format (`⚠️ WATCH OUT:` / `🔍 SURPRISINGLY BROAD:` / `🔒 HIDDEN OBLIGATION:` / `❗ CONTRADICTS EXPECTATIONS:`). Section template changed from verbose block to compact `### §X Title / 1-2 sentence / flag` format. "No original text quoting." added as first important guideline. Estimated ~30% output token reduction.
- **M2 CALIBRATE legal-gig-economy**: Fitness calibrated 0.0 → 0.76 (provisional status cleared) after structural audit confirmed 14 analysis lenses, complete Gig Safety Score formula, 4 contract types fully handled. Ready for session-signal fitness tracking in epoch 3.
- **M3 MUTATE legal-review**: Gig Worker / Platform row added to Phase 1.2 contract-type classification table — detection signals: `gig, marketplace, platform fee, per-project, task, escrow, Upwork, Fiverr, Toptal`. Completes routing triangle: review detects → orchestrator routes → gig-economy analyses.
- **M4 MUTATE legal-orchestrator**: Gig routing signal added to routing table (P0). Genome promoted to v2. Matrix Thought updated to epoch 2 state. GRPO epoch 3 queue populated (5 mutations).
- **All 6 EvoMetaClaw state files updated**: `population.json` (epoch→2, pop_size→15, gig fitness calibrated, niche_stats), `lineage.json` (epoch 2 nodes + edges), `q_table.json` (all 7 Q-states filled for epoch 1+2), `circuit_breaker_log.json` (pre/post epoch 2 events), `matrix_thoughts.json` (epoch 2 entry with mutations, cells, Q-gate), `config.yml` (pop_size 14→15).
- **EvoMetaClaw epoch 2 complete**: population_size=15, diversity=0.91, circuit_breaker=healthy. All 4 Q-gate decisions ACCEPT (avg confidence 0.878). Epoch 3 queue: NDA/Terms KafCa trim, gig fitness signal collection, SOC2+CAN-SPAM detection, SPLICE legal-review+legal-compare → legal-due-diligence.

### 2026-06-13 — Accessibility-First Visual Redesign (WCAG 2.1 AA)

UX/UI overhaul of every visual surface — PDFs, markdown templates, banner, README — with WCAG 2.1 Level AA conformance and triple-redundant risk indicators (shape + text + color). Driven by KafCade + KafCa: terse code, no premature abstraction, RRSS principles. Sets the baseline so disability-adjusted output is the default, not a flag.

- **PDF generator (`scripts/generate_legal_pdf.py`)** — full rewrite of visual layer:
  - **Palette to WCAG-AA** — danger `#b91c1c` (5.9:1), warning `#92400e` (7.8:1), success `#166534` (7.4:1), gray_text `#4a5568` (7.2:1). Old values (#e53e3e at 3.8:1, #d69e2e at 2.1:1, #38a169 at 3.3:1) failed contrast for normal text. Contrast ratios documented inline in COLORS dict.
  - **Triple-channel risk cues (WCAG 1.4.1)** — every risk indicator pairs a shape (▲ ■ ●), a text label (HIGH/MEDIUM/LOW), and a color. Removing any single channel preserves meaning. Applied to cover gauge descriptor, risk table rows, bar chart, clause headers, accessibility legend.
  - **Risk bar chart redesign** — segments use distinct fill patterns (hatched HIGH, dotted MEDIUM, solid LOW) plus inline counts, bordered for visibility, with a shape-prefixed textual legend below. Readable in monochrome and by colorblind users.
  - **Score gauge upgrade** — adds plain-English risk descriptor ("MODERATE RISK") below the numeric score; needle width bumped; gauge arc colors aligned to WCAG palette.
  - **Larger fonts + line height** — body 10pt → 11pt with 16pt leading; disclaimer 8pt → 10pt; footer 8pt → 9pt. Meets WCAG 1.4.4 Resize Text.
  - **PDF metadata** — `SimpleDocTemplate` now sets `title` (includes contract type), `author`, `subject`, `creator`, `keywords`. Surfaces in Reader title bars and assistive-tech tooling.
  - **PDF `/Lang` tag (WCAG 3.1.1)** — `en-US` written to the catalog via `_set_pdf_language` page hook. Verified present in object 15 of generated PDFs. ReportLab 4.5 does not expose `Canvas.setLanguage()`, so the catalog is written directly via `PDFString`.
  - **Accessibility & Reading Guide section** — every report ends with a dedicated legend page: three-channel encoding explainer, symbol/label/meaning table, conformance bullets, and how to report accessibility bugs.
  - **Score clamping** — defensive `max(0, min(100, ...))` on score input guards against malformed data.
  - **Boundary hardening** — `load_data` catches `json.JSONDecodeError` and `OSError` with actionable messages instead of stack traces; guards `spec.loader` being `None`.
- **Template (`templates/contract-review-template.md`)** — risk labels now lead with shape glyph + text + emoji color: `▲ HIGH RISK 🔴` instead of `🔴 High Risk` alone. Applied to risk dashboard, clause section headers, missing-protections table, and template usage notes. WCAG 1.4.1 enforced as template convention.
- **Banner SVG (`assets/banner.svg`)** — proper accessibility semantics:
  - `role="img"`, `<title>`, `<desc>` so screen readers announce a meaningful summary.
  - Decorative elements (grid, terminal chrome, scale-of-justice icon) marked `aria-hidden="true"`.
  - Subtitle `#8899bb` (4.4:1 borderline) → `#b8c5dd` (7.5:1 AAA) on dark background.
  - Terminal placeholder text `#556688` (1.9:1, failed) → `#8aa0c4` (4.5:1, AA).
  - Footer corrected to "15 skills" (was stale "14") with "accessible PDF reports" tagline.
- **README** — new "Accessibility (WCAG 2.1 AA)" section between Requirements and Docker/ARM, with per-surface conformance table and a practical "what this means in practice" subsection. Links to `assets/ACCESSIBILITY.md`.
- **NEW `assets/ACCESSIBILITY.md`** — full accessibility statement: conformance target (WCAG 2.1 AA + Section 508 + EAA), per-surface checklist mapped to WCAG success criteria, known limitations (PDF/UA tagging deferred, English-only output), testing methodology (NVDA, VoiceOver, monochrome print preview), 48-hour acknowledgement SLA for accessibility bug reports.
- **Verification** — smoke-tested both JSON and Markdown auto-modes; confirmed `/Lang (en-US)` in catalog, title metadata includes contract type, shape glyphs render via Helvetica WinAnsi, no regressions in clause/risk/missing-protection rendering. ARM Docker build will pick up changes via existing `.github/workflows/docker.yml` on push to main.

### 2026-06-05 — EvoMetaClaw Epoch 1 — 3 Mutations, 15 Skills

- **M1 MUTATE legal-compliance**: HIPAA promoted from `flag only` to full audit section (H1–H8). Weight: HIPAA 15%, ADA 10%, CAN-SPAM 5%, COPPA 5%. Civil penalties up to $1.9M/year now surfaced. Scorecard + framework detail + report template updated.
- **M2 SPLICE legal-nda + legal-freelancer → legal-gig-economy** (new skill): Covers gig workers, platform contractors, marketplace agreements (Upwork/Fiverr/Toptal). 10 analysis lenses: IP ownership, payment protection, scope creep, platform clauses, NDA scope, misclassification, non-compete, termination/kill fee, indemnification, dispute resolution. Gig Safety Score 0–100. Command: `/legal gig-economy <file>`.
- **M3 MUTATE legal-batch**: Phase 1.5 niche-routing added. Detects contract type → assigns specialist lens (SaaS, Employment, Freelancer/Gig, NDA, Investment, Lease, Partnership, General). Each parallel agent is now niche-aware. Ranking table includes Niche column.
- **Router updated**: `legal/SKILL.md` routes `/legal gig-economy`. 15 commands now in suite.
- **EvoMetaClaw epoch 1 complete**: population_size=15, diversity=0.93, circuit_breaker=healthy. Q-gate accepted all 3 mutations (M2 provisional — monitor 3 sessions).
- **Epoch 2 queued**: legal-plain KafCa token-trim, legal-gig-economy fitness calibration, legal-review gig-economy type detection.

### 2026-06-04 — EvoMetaClaw Integration + ARM Deploy + Im Hardening

- **Security fix (P0)**: Added `xe()` XML-escape helper in `scripts/generate_legal_pdf.py` — all clause data (name, section, summary, risk_explanation, recommendation) now escaped before ReportLab Paragraph markup. Contracts with `<`, `>`, `&` in clause text no longer crash PDF build.
- **Correctness fix (P1)**: Removed redundant `if total > 0` guards in `create_risk_bar_chart` — already protected by early-return on `total == 0`.
- **EvoMetaClaw injected**: Added `evo-metaclaw/` meta-learning layer — config, orchestration genome, 14-skill population, seeded domain memory, matrix thoughts, circuit breaker, Q-table, lineage. Evolves skill routing from live sessions. Mode: `auto` (idle-window scheduling).
- **ARM deploy**: Added `Dockerfile` (python:3.12-slim, multi-arch) + `.github/workflows/docker.yml` — builds `linux/amd64 + linux/arm64` on push to main, publishes to GHCR.
- **DEVFLOW_SKILL.md synced to v1.1**: Updated D-command platform selection matrix (Fly.io ARM64, Railway, GHCR, Vercel ASGI paths). Was stale at v1.0.
- **EvoMetaClaw epoch 0 matrix**: Compliance niche underserved — CAN-SPAM/SOC2/HIPAA queued for mutation epoch 1. Splice mutation `legal-nda + legal-freelancer → legal-gig-economy` queued for epoch 1 (executed ahead of schedule).

### 2026-05-23 — DevFlow CI Pass
- **Fixed critical bug**: `importlib.util.load_from_spec` → `module_from_spec` in `scripts/generate_legal_pdf.py` (markdown→PDF auto-mode was crashing)
- **Fixed script lookup**: `skills/legal-report-pdf/SKILL.md` now references correct filename `generate_legal_pdf.py` (was `generate_pdf_report.py`)
- **Added `legal-batch` to bash installer**: `install.sh` was missing it (only `install.ps1` had it)
- **Added `legal-batch` to command menu**: now visible in `/legal` menu and routing table in `legal/SKILL.md`
- **Fixed hardcoded dev path**: `generate_sample_contract.py` output path now uses `__file__`-relative path
- **Added `.gitignore`**: covers `__pycache__`, generated review files, PDFs, `.env`
- **Sub-skill count corrected**: 14 sub-skills (was incorrectly listed as 13)

---

## DevFlow — AI Dev Workflow Commands

This project has `DEVFLOW_SKILL.md` in the repo root. Use short commands to drive development:

| Command | Action |
|---------|--------|
| `B` | Build the next roadmap item |
| `I` | Integrate — sync code, docs, state |
| `Im` | Improve — refactor/harden, no new features |
| `E` | Evaluate — structured security/quality audit |
| `C` | Consolidate — remove dead code, extract helpers |
| `Bl` | Blueprint — update living docs |
| `P` | Push — smart commit + push to all remotes |
| `D` | Deploy — auto-detect Netlify/Vercel/GH Pages |
| `CI` | Full pipeline: I → Im → E → C → Bl → P → D |

Combine freely: `B+P+D`, `E Im`, `CI`. See `DEVFLOW_SKILL.md` for full specs.
