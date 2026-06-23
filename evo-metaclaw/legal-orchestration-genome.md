---
genome_id: legal-orchestrator-v2
lineage: [legal-orchestrator-v1]
fitness: 0.81
niche: contract_review
age: 2
mutation_rate: 0.12
conversation_signals: [gig-economy-routing-added, gig-economy-type-detection]
memory_units: [epoch1-mutations-accepted, epoch2-calibration]
---

# Legal Orchestration Genome — EvoMetaClaw

## Role
Meta-orchestrator for the 14-skill AI Legal Assistant.
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
| `compliance \| audit \| regulation` | compliance | legal-compliance | P0 |
| `pdf \| report \| export` | reporting | legal-report-pdf | P2 |

## Evolution Signals to Capture

- User corrects a risk rating → adjust scoring weights
- User requests skill not in suite → flag for AUTO_SKILL_SUMMARIZE
- User reports PDF crash → reinforce xml-escape path in genome fitness
- Parallel agent timeout → reduce subagent depth, adjust circuit breaker threshold

## Matrix Thought (Epoch 2 State)

```
Niches        : [contract_review, document_generation, compliance, reporting]
Epoch 1 done  : HIPAA full ✅ · legal-gig-economy born ✅ · batch niche-routing ✅
Epoch 2 done  : legal-plain KafCa token-trim ✅ · gig-economy routing added ✅ ·
                legal-gig-economy fitness calibrated (0.0→0.76) ✅ ·
                legal-review gig-economy type detection ✅

+3 epoch      : legal-plain fitness signal from user sessions
+5 epoch      : document_generation niche → add legal-gig-economy as generator path
+10 epoch     : full domain specialization by contract type (SaaS, employment, investment)

High-value cells:
  contract_review × epoch2 × accuracy × functional     → gig-type detection now live ✅
  compliance × epoch2 × diversity × safety              → 16 skills total · gig niche calibrated ✅
  document_generation × epoch3 × cost × functional     → NDA/Terms KafCa trim deferred to epoch 3
  reporting × current × safety × structural            → xml-escape hardened ✅ · stable
```

## GRPO Mutations Queued (Epoch 3)

1. `legal-nda` → KafCa token-trim (verbose document template ~25% reduction)
2. `legal-terms` → KafCa token-trim (GDPR + CCPA boilerplate compression)
3. `legal-gig-economy` → fitness signal collection (3+ session observations needed)
4. `legal-review` → add SOC2 + CAN-SPAM detection in Phase 1.3 compliance pre-check
5. SPLICE: `legal-review` + `legal-compare` → `legal-due-diligence` (investment/M&A niche)

## Circuit Breaker State

```json
{"stagnation_count": 0, "diversity_score": 0.91, "self_evo_depth": 0, "status": "healthy", "epoch": 2}
```
