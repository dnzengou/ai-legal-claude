---
genome_id: legal-orchestrator-v1
lineage: []
fitness: 0.0
niche: contract_review
age: 0
mutation_rate: 0.15
conversation_signals: []
memory_units: []
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
| `compliance \| audit \| regulation` | compliance | legal-compliance | P0 |
| `pdf \| report \| export` | reporting | legal-report-pdf | P2 |

## Evolution Signals to Capture

- User corrects a risk rating → adjust scoring weights
- User requests skill not in suite → flag for AUTO_SKILL_SUMMARIZE
- User reports PDF crash → reinforce xml-escape path in genome fitness
- Parallel agent timeout → reduce subagent depth, adjust circuit breaker threshold

## Matrix Thought (Initial State)

```
Niches        : [contract_review, document_generation, compliance, reporting]
Current epoch : skills accurate but compliance niche underserved (CAN-SPAM, SOC2 missing)
+1 epoch      : mutate legal-compliance to add CAN-SPAM / SOC2 coverage
+3 epoch      : splice legal-review + legal-freelancer → hybrid gig-economy genome
+10 epoch     : full domain specialization by contract type (SaaS, employment, investment)

High-value cells:
  contract_review × current × accuracy × functional   → 5-agent pipeline ✅
  compliance × +1 × diversity × safety                → expand regulatory coverage
  document_generation × +1 × cost × functional        → KafCa token-trim NDA/Terms prompts
  reporting × current × safety × structural           → xml-escape hardened ✅
```

## GRPO Mutations Queued

1. `legal-compliance` → inject CAN-SPAM + SOC2 + HIPAA checks (diversity)
2. `legal-nda` + `legal-freelancer` → splice → `legal-gig-economy` genome
3. `legal-batch` → parallelize per contract-type niche (structural mutation)

## Circuit Breaker State

```json
{"stagnation_count": 0, "diversity_score": 1.0, "self_evo_depth": 0, "status": "healthy"}
```
