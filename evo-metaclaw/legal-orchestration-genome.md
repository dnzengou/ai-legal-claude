---
genome_id: legal-orchestrator-v3
lineage: [legal-orchestrator-v1, legal-orchestrator-v2]
fitness: 0.82
niche: contract_review
age: 3
mutation_rate: 0.12
conversation_signals: [gig-economy-routing-added, gig-economy-type-detection, due-diligence-routing-added, investment-ma-niche]
memory_units: [epoch1-mutations-accepted, epoch2-calibration, epoch3-splice-due-diligence]
---

# Legal Orchestration Genome — EvoMetaClaw

## Role
Meta-orchestrator for the 16-skill AI Legal Assistant.
Selects, sequences, and evolves which skills fire for each user request.
Learns from every session via CONVERSATION_SIGNAL_CAPTURE.

## Skill Routing (Evolved)

| Signal Pattern | Niche | Skills to Activate | Priority |
|---|---|---|---|
| `review \| analyze \| check` + file | contract_review | legal-review (→5 agents) | P0 |
| `risk \| danger \| risky \| expose` | contract_review | legal-risks | P0 |
| `compare \| diff \| versus` + 2 files | contract_review | legal-compare | P1 |
| `plain \| explain \| translate` | contract_review | legal-plain | P2 |
| `negotiate \| counter \| push back` | contract_review | legal-negotiate | P1 |
| `missing \| protect \| gap` | compliance | legal-missing | P1 |
| `batch \| multiple \| all contracts` | contract_review | legal-batch | P1 |
| `nda \| non-disclosure` | document_generation | legal-nda | P0 |
| `terms \| tos \| terms of service` | document_generation | legal-terms | P0 |
| `privacy \| gdpr \| ccpa` | document_generation | legal-privacy | P0 |
| `agreement \| contract \| template` | document_generation | legal-agreement | P1 |
| `freelancer \| contractor \| 1099` | compliance | legal-freelancer | P0 |
| `gig \| platform \| marketplace \| upwork \| fiverr \| toptal` | compliance | legal-gig-economy | P0 |
| `due diligence \| m&a \| acquisition \| investment \| investor \| deal-killer \| change of control` | investment_ma | legal-due-diligence | P0 |
| `compliance \| audit \| regulation` | compliance | legal-compliance | P0 |
| `pdf \| report \| export` | reporting | legal-report-pdf | P2 |

## Evolution Signals to Capture

- User corrects a risk rating → adjust scoring weights
- User requests skill not in suite → flag for AUTO_SKILL_SUMMARIZE
- User reports PDF crash → reinforce xml-escape path in genome fitness
- Parallel agent timeout → reduce subagent depth, adjust circuit breaker threshold

## Matrix Thought (Epoch 3 State)

```
Niches        : [contract_review, document_generation, compliance, reporting, investment_ma]
Epoch 1 done  : HIPAA full ✅ · legal-gig-economy born ✅ · batch niche-routing ✅
Epoch 2 done  : legal-plain KafCa trim ✅ · gig routing ✅ · gig fitness 0.76 ✅ · review gig-detect ✅
Epoch 3 done  : legal-nda KafCa trim ✅ · legal-terms KafCa trim ✅ ·
                legal-review SOC2+CAN-SPAM Phase 1.4 ✅ ·
                SPLICE legal-due-diligence born (investment_ma niche) ✅ ·
                16-skill count, all installers updated ✅

+1 epoch      : legal-due-diligence fitness calibration (3+ sessions required)
+2 epoch      : legal-privacy + legal-agreement KafCa trim
+3 epoch      : legal-compliance SOC2 full section (mirror HIPAA pattern)
+5 epoch      : SPLICE legal-review + legal-batch → legal-portfolio-review (VC/PE niche)

High-value cells:
  investment_ma × epoch3 × accuracy × future      → legal-due-diligence born ✅ · monitor sessions
  document_generation × epoch3 × cost × functional → nda + terms trimmed ✅ · privacy/agreement next
  contract_review × epoch3 × safety × functional   → SOC2/CAN-SPAM pre-detection live ✅
  reporting × current × safety × structural        → xml-escape + WCAG AA + /Lang ✅ · stable
```

## GRPO Mutations Queued (Epoch 4)

1. `legal-due-diligence` → fitness calibration (requires 3+ session observations first)
2. `legal-privacy` → KafCa token-trim (~20% reduction target)
3. `legal-agreement` → KafCa token-trim (~25% reduction target)
4. `legal-compliance` → add SOC2 full audit section (Type I vs Type II distinction, scope)
5. SPLICE: `legal-review` + `legal-batch` → `legal-portfolio-review` (VC/PE fund multi-company niche)

## Circuit Breaker State

```json
{"stagnation_count": 0, "diversity_score": 0.92, "self_evo_depth": 0, "status": "healthy", "epoch": 3, "new_niche": "investment_ma"}
```
