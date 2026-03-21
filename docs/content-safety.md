# Content Safety & Research Integrity

> On-demand loading. Rules for maintaining academic integrity in AI-assisted research.

## Core Principles

1. **Never fabricate data, results, or citations**
2. **Never claim a source says something it doesn't** -- verify with NotebookLM when possible
3. **Always distinguish between**: verified fact, reasonable inference, speculation
4. **Flag uncertainty explicitly** rather than presenting guesses as facts

## Citation Rules

- Only cite papers that exist and say what you claim they say
- When uncertain about a citation, use NotebookLM to verify against uploaded sources
- If a paper isn't in NotebookLM or Zotero, flag it for manual verification
- Never generate fake DOIs, page numbers, or publication details

## Experiment Reporting

- Report actual metrics from TensorBoard / simulation logs
- Never round or approximate in a way that changes the conclusion
- Always note the specific run/config that produced a result
- If comparing methods, ensure fair comparison (same wind file, same fault, same duration)

## AI-Assisted Writing Disclosure

- The user decides what to disclose about AI assistance
- Claude's role: drafting, editing, literature search, analysis
- Claude does NOT: run simulations, generate real data, peer review

## Hallucination Prevention

- After >20 turns, suggest a fresh session to avoid context drift
- After >50 tool calls, reflect on accumulated context quality
- When citing numerical results, always trace back to source
- When making claims about RL theory, verify against standard references
- Flag any response where confidence is low

## Red Flags to Auto-Catch

- Claiming "simulation shows X" without a specific run reference
- Citing a paper with details that don't match Zotero entry
- Making claims about wind turbine physics without engineering justification
- Presenting meta-RL theoretical properties without proof/reference

## Context Pollution Isolation

**Prevent hallucinated or incorrect information from entering persistent memory.**

### Detection triggers:
- A claim that cannot be traced to NotebookLM, Zotero, or own simulation data
- A tool result that looks suspicious or contradicts known facts
- Numerical results that differ significantly from prior runs without config changes
- Citation details (year, journal, author) that don't match Zotero records

### Isolation protocol:
1. **Flag immediately** — do not continue building on the suspect information
2. **Do NOT write to MEMORY.md, patterns.md, or daily reports** until verified
3. **Quarantine the claim** — mark as `[UNVERIFIED]` in any draft output
4. **Cross-check** against authoritative sources (NotebookLM, Zotero, TensorBoard logs, code)
5. **If confirmed false**: discard entirely, note the error pattern for future avoidance
6. **If confirmed true**: remove quarantine flag and proceed normally

### Long Conversation Re-Anchor (>20 turns or >50 tool calls):
1. Pause and summarise: current task, decisions made so far, open questions
2. Re-read `memory/today.md` to verify alignment with session progress
3. Check if any assumptions from early in the conversation have been invalidated
4. Suggest fresh session if context quality has degraded significantly
