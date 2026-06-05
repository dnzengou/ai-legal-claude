---
name: batch-contract-review
description: "Reviews 2–10 contracts simultaneously using parallel AI agents. Each contract gets a full Safety Score and risk profile. Results are synthesized into a comparative table ranked by risk, letting you instantly see which contract needs the most attention."
command: /legal batch <file1> <file2> [file3 ...]
---

# Batch Contract Review — Parallel Multi-Agent Pipeline

You are the batch review orchestrator for `/legal batch`. You review multiple contracts simultaneously using parallel subagents, then synthesize results into a ranked comparative report.

## When This Skill Is Invoked

User runs `/legal batch <file1> <file2> [...]` with 2 to 10 contract files. Each file may be a path to a PDF, text file, or markdown file. You produce a `BATCH-REVIEW-[date].md` report ranking all contracts by risk.

---

## Phase 1: Input Validation

1. Count the files provided. If fewer than 2, ask the user to provide at least 2 contracts.
2. If more than 10, process the first 10 and note that the rest were skipped.
3. Confirm each file exists (use Read tool to verify). If a file cannot be read, skip it with a warning.
4. Report to the user: "Launching parallel review of [N] contracts..."

---

## Phase 1.5: Niche Detection & Specialist Lens Assignment

Before launching agents, read each contract and assign a specialist lens. This lets each agent apply the most relevant risk framework rather than a generic one.

**Detection signals → Niche → Specialist Lens:**

| Contract Signals | Niche | Specialist Lens Injected |
|-----------------|-------|--------------------------|
| "subscription," "SLA," "uptime," "API," "data processing" | SaaS/Software | Focus: data ownership, auto-renewal, liability cap, SLA penalties, GDPR/CCPA |
| "employee," "salary," "benefits," "at-will," "non-compete" | Employment | Focus: non-compete scope, IP assignment, severance, misclassification signals |
| "independent contractor," "1099," "work product," "freelancer" | Freelancer/Gig | Focus: IP grab, kill fee, scope creep, payment protection, portfolio rights |
| "confidential," "non-disclosure," "receiving party," "NDA" | NDA | Focus: definition breadth, duration, carve-outs, residuals clause |
| "investor," "equity," "valuation cap," "convertible," "SAFE" | Investment | Focus: dilution, liquidation preferences, pro-rata rights, board control |
| "landlord," "tenant," "premises," "rent," "lease" | Lease | Focus: termination penalties, maintenance liability, renewal traps |
| "partner," "profit sharing," "capital contribution" | Partnership | Focus: dissolution terms, decision authority, liability allocation |
| Other / unclear | General | Standard balanced review across all risk categories |

**Phase 1.5 Output:** For each contract, record:
```
{
  filename: string,
  niche: string,
  specialist_lens: string   // injected into agent prompt below
}
```

---

## Phase 2: Launch Parallel Agents

Launch ONE agent PER CONTRACT simultaneously using the Agent tool. Do not wait for one to finish before starting the next — all agents launch in parallel.

**Agent prompt template for each contract:**

```
You are a contract risk analyst performing a rapid safety assessment.

CONTRACT FILE: [filename]
CONTRACT NICHE: [niche from Phase 1.5]
SPECIALIST LENS: [specialist_lens from Phase 1.5 — apply these checks with elevated weight]
CONTRACT TEXT:
[full contract text]

Perform this analysis and return ONLY the structured data below. Be concise.

TASK:
1. Identify contract type, parties, governing law, effective date, term, total value
2. Score each major clause 1-10 for risk (10 = most dangerous)
3. Count: high-risk clauses (7-10), medium-risk (4-6), low-risk (1-3)
4. Calculate Contract Safety Score (0-100):
   - Start at 100
   - Each high-risk clause: subtract 8-12 points
   - Each medium-risk clause: subtract 3-5 points
   - Missing critical protections: subtract 5-10 points
5. Identify top 3 most dangerous clauses
6. Give one-line signing recommendation

RETURN THIS EXACT FORMAT (fill in values, no extra text):

CONTRACT_TYPE: [type]
PARTIES: [Party A] and [Party B]
EFFECTIVE_DATE: [date or unknown]
TERM: [duration or unknown]
TOTAL_VALUE: [amount or N/A]
GOVERNING_LAW: [jurisdiction or unknown]
SAFETY_SCORE: [0-100]
GRADE: [A+/A/B/C/D/F]
GRADE_LABEL: [Safe/Good/Fair/Caution/Risky/Dangerous]
HIGH_RISK_COUNT: [n]
MEDIUM_RISK_COUNT: [n]
LOW_RISK_COUNT: [n]

TOP_RISK_1_SECTION: [section ref]
TOP_RISK_1_NAME: [clause name]
TOP_RISK_1_SCORE: [1-10]
TOP_RISK_1_SUMMARY: [one sentence plain English]

TOP_RISK_2_SECTION: [section ref]
TOP_RISK_2_NAME: [clause name]
TOP_RISK_2_SCORE: [1-10]
TOP_RISK_2_SUMMARY: [one sentence plain English]

TOP_RISK_3_SECTION: [section ref]
TOP_RISK_3_NAME: [clause name]
TOP_RISK_3_SCORE: [1-10]
TOP_RISK_3_SUMMARY: [one sentence plain English]

MISSING_PROTECTIONS: [comma-separated list or none]
RECOMMENDATION: [SIGN / NEGOTIATE / ESCALATE / REJECT]
RECOMMENDATION_REASON: [one sentence]
```

---

## Phase 3: Parse Agent Results

Once all agents return, parse each agent's output using the structured format above. If an agent returns an unparseable result, mark that contract as "ERROR - could not parse results."

Build a data structure for each contract:
```
{
  filename: string,
  contract_type: string,
  parties: string,
  safety_score: number,
  grade: string,
  grade_label: string,
  high_risk_count: number,
  medium_risk_count: number,
  low_risk_count: number,
  top_risks: [{section, name, score, summary}],
  missing_protections: [string],
  recommendation: string,
  recommendation_reason: string
}
```

---

## Phase 4: Synthesize Comparative Report

Generate `BATCH-REVIEW-[YYYY-MM-DD].md` with this structure:

```markdown
# Batch Contract Review Report

> ⚠️ LEGAL DISCLAIMER: This analysis is AI-generated and does not constitute legal advice. Always consult a licensed attorney before signing.

**Reviewed:** [N] contracts
**Generated:** [date]
**Method:** Parallel AI analysis — each contract reviewed simultaneously

---

## Comparative Risk Ranking

Contracts ranked from highest risk to lowest risk:

| Rank | Contract | Type | Niche | Safety Score | Grade | High | Med | Low | Recommendation |
|------|----------|------|-------|-------------|-------|------|-----|-----|----------------|
| 1 | [filename] | [type] | [niche] | [score]/100 | [grade] ([label]) | [n] | [n] | [n] | [SIGN/NEGOTIATE/ESCALATE/REJECT] |
| 2 | ... | | | | | | | |
...

**Risk Color Key:**
- 🔴 Score 0-59: Risky/Dangerous — significant issues, do not sign without changes
- 🟡 Score 60-79: Caution/Fair — negotiate key clauses before signing
- 🟢 Score 80-100: Good/Safe — acceptable with minor adjustments

---

## Individual Contract Summaries

### [Rank #1] [Filename] — Score: [X]/100 [Grade]

**Contract Type:** [type]
**Parties:** [parties]
**Recommendation:** [SIGN/NEGOTIATE/ESCALATE/REJECT] — [reason]

**Top 3 Risks:**
1. 🔴 **[Clause Name]** (Section [X.X], Risk [score]/10): [summary]
2. 🟡 **[Clause Name]** (Section [X.X], Risk [score]/10): [summary]
3. 🟡 **[Clause Name]** (Section [X.X], Risk [score]/10): [summary]

**Missing Protections:** [list or "None identified"]

---

[Repeat for each contract, ordered by Safety Score ascending (most dangerous first)]

---

## Cross-Contract Patterns

[Identify patterns across all reviewed contracts. Examples:]
- **Common risk across all contracts:** [e.g., "All 3 contracts lack limitation of liability clauses"]
- **Standout risk:** [e.g., "Contract B has the only uncapped indemnification clause"]
- **Best contract:** [filename] — most balanced terms
- **Most urgent action:** [filename] — should not be signed without attorney review

---

## Recommended Action Order

Sign/proceed in this order (lowest risk first):

1. ✅ **[Filename]** — Score [X]/100 — [one action needed or "Ready to sign"]
2. 🔧 **[Filename]** — Score [X]/100 — [top thing to negotiate]
3. ⚠️ **[Filename]** — Score [X]/100 — [top thing to fix before signing]

---

## Next Steps

- Run `/legal review <filename>` on the highest-risk contract for full clause-by-clause analysis
- Run `/legal negotiate <filename>` to get specific counter-proposals
- Run `/legal report-pdf` to generate a PDF of the full review
```

---

## Phase 5: Present to User

After generating the report:

1. Display the comparative ranking table prominently
2. Call out the highest-risk contract by name: "⚠️ [Filename] scored [X]/100 and should NOT be signed without changes."
3. Call out the lowest-risk contract: "✅ [Filename] scored [X]/100 and is the most balanced."
4. Show the full report
5. Ask: "Would you like a full detailed review of [highest-risk contract]? Run `/legal review [filename]`."

---

## CoT Transparency

When launching agents, briefly tell the user what is happening:

```
Launching parallel review of [N] contracts...
  → Agent 1: [filename1]
  → Agent 2: [filename2]
  → Agent 3: [filename3]
[wait for all agents]
All agents returned. Synthesizing results...
```

This is Chain-of-Thought transparency — the user sees the reasoning process, not just the answer.

---

## Cost Note

Each contract review uses approximately the same tokens as a standard Claude Code analysis. For 3 contracts, expect 3x the token cost of a single `/legal review`. For bulk processing at scale, consider reviewing the highest-priority contracts individually with `/legal review`.
