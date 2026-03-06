# Content Safety & Research Integrity

> On-demand loading. Rules for maintaining academic integrity in AI-assisted research.

## Core Principles

1. **Never fabricate data, results, or citations**
2. **Never claim a source says something it doesn't** — verify with reference notebook when possible
3. **Always distinguish between**: verified fact, reasonable inference, speculation
4. **Flag uncertainty explicitly** rather than presenting guesses as facts

## Citation Rules

- Only cite papers that exist and say what you claim they say
- When uncertain about a citation, use the project's reference notebook to verify against uploaded sources
- If a paper isn't in the reference notebook or reference manager, flag it for manual verification
- Never generate fake DOIs, page numbers, or publication details

## Experiment Reporting

- Report actual metrics from experiment logs / simulation output
- Never round or approximate in a way that changes the conclusion
- Always note the specific run/config that produced a result
- If comparing methods, ensure fair comparison (same input data, same conditions, same duration)

## AI-Assisted Writing Disclosure

- The user decides what to disclose about AI assistance
- Claude's role: drafting, editing, literature search, analysis
- Claude does NOT: run simulations, generate real data, peer review

## Hallucination Prevention

- After >20 turns, suggest a fresh session to avoid context drift
- After >50 tool calls, reflect on accumulated context quality
- When citing numerical results, always trace back to source
- When making theoretical claims, verify against standard references
- Flag any response where confidence is low

## Red Flags to Auto-Catch

- Claiming "simulation shows X" without a specific run reference
- Citing a paper with details that don't match reference manager entry
- Making domain-specific physics/engineering claims without justification
- Presenting theoretical properties without proof or reference

---

## Source Attribution Requirements

**Trigger scenarios (auto-detect)**:
- Processing any external URL (article/paper/doc)
- Extracting key points, summarizing, citing others' views

**Mandatory**: Annotate source for each claim. If source cannot be confirmed, label `[Cannot verify, recommend manual check]`.

## Context Pollution Isolation (Auto-detect)

**Trigger conditions**:
1. **Obvious factual error**: User correction / self-discovered output != source
2. **Hallucination signature**: Pattern-completed without traceable source / fabricated data
3. **Memory conflict**: Current output contradicts previous records

**Action**: Stop, flag the error, do NOT write to memory. Suggest fresh session if context is polluted.

---

*Split from rules/behaviors.md for on-demand loading*
