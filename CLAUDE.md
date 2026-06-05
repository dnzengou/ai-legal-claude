# AI Legal Assistant — Claude Code Skills Suite

Production-ready legal analysis system. 15 skills, 5 parallel agents, PDF report generation.

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
skills/<name>/SKILL.md       ← 14 sub-skills, each handles one command
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
