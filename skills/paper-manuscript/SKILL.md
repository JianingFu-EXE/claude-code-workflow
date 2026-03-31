---
name: paper-manuscript
description: >
  Full academic paper manuscripting workflow: analyse teacher papers, build a paper
  structure in XMind, assign reference papers via NotebookLM + Zotero, draft linking
  sentences, and write new .tex manuscript files in the Overleaf git repo. Designed
  for the Meta-RL for Wind Turbine FTC project but applicable to any IEEE journal paper.
---

# Paper Manuscript Skill

End-to-end workflow for writing a structured IEEE journal paper manuscript. Covers structure generation, reference assignment, linking-sentence drafting, and `.tex` file creation against the Overleaf repo.

## When to Use This Skill

Trigger when user says any of the following:
- "I want a rough structure relating to `<topic>`. Teacher papers are in `<location>`."
- "Write now" — execute Step 4 (manuscript writing) immediately on the current XMind plan.
- "Find references for the structure" — run Step 1 (reference paper selection).
- "Assign tasks to the papers" — run Step 2 (task assignment + linking sentences).
- "Draft the introduction / abstract / problem formulation / ..."

---

## Tools Required

| Tool | Purpose |
|---|---|
| NotebookLM skill | Source-grounded paper discovery; query user's uploaded library |
| Zotero MCP | Retrieve annotations, search papers, verify citations |
| XMind skill | Read/write `.xmind` outline files |
| Bash / git | Write `.tex` files into the Overleaf repo, commit |

---

## Workflow Overview

```
Step 0: Analyse teacher papers → generate XMind outline with rough structure
Step 1: Find reference papers for each paragraph slot → populate XMind branches
Step 2: Assign paper tasks + write linking sentences in XMind
(Step 3: optional — request more logical-chain info before drafting)
Step 4: Write manuscript → new .tex file in Overleaf repo
```

---

## Step 0 — Teacher Paper Analysis

**Trigger:** User provides topic + teacher paper location.

### Goal
Identify the role each teacher paper plays:
- **Writing style model** — papers with exemplary academic prose structure
- **Research problem model** — papers that study the same problem
- **Method model** — papers that use similar methods with clear justification

### Action
1. Use NotebookLM or Zotero to read teacher papers.
2. Generate an XMind file with the following **canonical paper structure**:

#### Canonical Paper Structure (Meta-RL for IPC+FTC)

```
Root: <Paper Title>
├── Abstract
│   ├── Background:     [what domain, why it matters]
│   ├── Research Problem: [the specific problem being solved]
│   ├── Research Gap:   [what existing methods fail to do]
│   ├── Hypothesis:     [why the proposed method bridges the gap]
│   ├── Method:         [high-level description of approach]
│   ├── Analysis:       [key evaluation metric, e.g. DEL]
│   └── Conclusion:     [one-sentence takeaway]
├── Introduction
│   ├── Opening:            [hook / broad context]
│   ├── <Topic 1>:          [first literature thread]
│   ├── <Topic 2>:          [second literature thread]
│   ├── ...
│   └── Contribution:
│       ├── <Contribution 1>
│       ├── <Contribution 2>
│       └── <Contribution 3>
├── Problem Formulation
│   ├── Control Problem:    [verbal description of control task]
│   ├── MDP Formulation:
│   │   ├── Actions
│   │   ├── States
│   │   └── Reward
│   └── Fault Models:       [actuator fault, sensor fault, etc.]
├── Proposed Method
│   ├── Background Review:  [related algorithms with brief justification]
│   └── Applied Technologies:
│       ├── <Module 1>:     [name + what it does]
│       └── <Module 2>:     [name + what it does]
├── Simulation and Analysis
│   ├── Setup:              [simulator, turbine model, scenarios]
│   ├── Ablation Study:
│   │   ├── Baseline 1: ...
│   │   └── Baseline 2: ...
│   └── Results:
│       ├── Nominal performance
│       └── Fault-tolerant performance
└── Conclusion
```

> **Note:** Adapt branch names to the specific paper topic. The structure above is the default for the Meta-RL IPC-FTC project.

---

## Step 1 — Reference Paper Selection

**Trigger:** "Find references for the structure."

### Procedure
1. Read the current XMind outline (use the XMind read script to extract the full topic hierarchy).
2. For each paragraph slot / leaf node, formulate a targeted NotebookLM question (see paper-atlas skill for question strategy).
3. Retrieve source-grounded answers with specific paper titles, authors, and claims.
4. Build the XMind JSON and write the enriched `.xmind` file directly using the XMind skill script:

```bash
node ~/.claude/skills/xmind/scripts/create_xmind.mjs < /tmp/refs_input.json
```

Save the output to the same folder as the source XMind outline (the Overleaf repo directory).

### XMind Structure — Features to Use

Build a rich, deeply annotated XMind file using these features:

| Feature | How to use it |
|---|---|
| `structureClass: org.xmind.ui.logic.right` | **Logic chart (right)** — use on every paragraph node for clean hierarchical layout |
| `notes (HTML)` | Every paper node: full content using `<strong>Research Problem:</strong>`, `<strong>Research Gap:</strong>`, `<strong>Hypothesis:</strong>`, `<strong>Methodology:</strong>` as bold section headers, separated by `<br><br>` |
| `labels` | Category tags: `model-based`, `RL-based`, `active-FTC`, `passive-FTC`, `meta-RL-FTC`, `FOWT`, etc. |
| `markers` | `priority-1` for key papers; `priority-2` for supporting; `priority-3` for supplementary; `task-start` on paragraph nodes |
| `callouts` | Key gap insights on critical papers only (e.g. "KEY GAP: instantaneous state cannot distinguish fault from disturbance") |
| `boundaries` | Group papers by sub-category within each paragraph slot (e.g. model-based vs RL-based; active vs passive FTC) |
| `summaryTopics` | One summary per paragraph slot: what the collective papers show / fail to show |
| `linkToTopic` | When a paper already defined in an earlier paragraph is referenced again — link rather than duplicate |
| `relationships` (sheet-level) | **Only between papers** where B directly fixes the gap of A (e.g. PEARL → RL², PEARL → MAML, Xie2025 gap → PEARL). **Do NOT add relationships between paragraph nodes** — the user arranges those manually. |

### Rules for Paper Nodes

- The 4 structured fields (**Research Problem**, **Research Gap**, **Hypothesis**, **Methodology**) go in the `notes` HTML as `<strong>` bold headers — **not as separate child branches**.
- `Hypothesis` must explain *why the method was chosen for that gap*, not just describe the method.
- Do **not** add `[LINK]` callouts or placeholders between paragraphs — the user adds transitions manually.
- Papers belonging to multiple slots: define fully in the first slot, use `linkToTopic` in subsequent slots.
- Group papers within a slot in logical reading order (chronological, or from general to specific).

---

## Step 2 — Task Assignment and Linking Sentences

**Trigger:** After reference papers are assigned in XMind.

### Action
1. Read each reference paper (via Zotero annotations or NotebookLM).
2. In each paper's XMind branch, assign a **specific writing task**:
   - e.g., "Use this paper to justify why temporal context is needed for fault adaptation"
   - e.g., "Cite this for IPC load mitigation effectiveness on offshore turbines"
3. Write **rough linking sentences** between paragraphs to ensure logical flow:
   - Each sentence bridges the conclusion of paragraph N to the opening of paragraph N+1.
   - Ask for more logical-chain information if the connection is non-obvious.

### Optional Step 3 — Logical Chain Clarification
Before drafting, explicitly ask: *"Is there any additional logical reasoning or missing link you want me to establish before I draft?"*

---

## Step 4 — Manuscript Writing

**Trigger:** User says "Write now."

### Action
1. Read the XMind outline — tasks assigned to papers + linking sentences.
2. Open `template.tex` from the Overleaf repo for the header/preamble.
3. Create a **new `.tex` file** (never overwrite the previous manuscript — see File Management rule).
4. Write the full manuscript section by section, following the structure from Step 0.
5. Generate bibliography entries and add them to the `.bib` file.
6. Commit the new file to the Overleaf git repo.

### Writing Execution Rules (per section)

| Section | Guidance |
|---|---|
| Abstract | Follow the 7-field template: Background → Problem → Gap → Hypothesis → Method → Analysis → Conclusion. Keep ≤ 250 words. |
| Introduction | Follow the logical thread from the XMind. Each paragraph = one literature theme. End with numbered contributions. Never list papers by methodology alone. |
| Problem Formulation | Define control task verbally first, then formalise as MDP. Include fault models. |
| Proposed Method | Review foundational algorithms (briefly, with justification). Then describe applied modules with equations. Refer to teacher papers for style. |
| Simulation and Analysis | Present setup, then ablation (each baseline labelled 1, 2, 3...), then main results. Use DEL or other agreed metric. |
| Conclusion | One paragraph: what was done, main finding, limitation/future work. |

---

## Core Writing Rules

### 1. Literature Review Rule (CRITICAL)
> **DO NOT list papers' methodology plainly — it has no meaning.**
>
> Every citation must address: **the problem**, **the gap**, and **why the adopted method could solve the problem and bridge the gap**.

**Wrong:**
> "Smith et al. [1] used MAML for adaptation. Jones et al. [2] applied LSTM for temporal modelling."

**Right:**
> "To address the challenge of rapid fault adaptation without retraining, Smith et al. [1] proposed MAML-based meta-learning, demonstrating that gradient-based task adaptation can recover from unseen actuator faults within a single episode. However, this approach relies on a fixed task distribution and ignores the temporal evolution of fault dynamics. Jones et al. [2] addressed this limitation by incorporating LSTM to capture temporal dependencies, yet their method requires fault labels at inference time."

### 2. File Management Rule
- Every major manuscript revision **starts a new `.tex` file**.
- Naming convention: `main_v<N>_<descriptor>.tex` (e.g., `main_v2_introduction.tex`).
- The header/preamble must be copied from `template.tex` — do not recreate it from scratch.

### 3. Bibliography Rule
- Generate complete BibTeX entries for every cited paper.
- Add entries to `IEEEexample.bib` (or project `.bib` file).
- Format: IEEE style. Include DOI where available.
- Never fabricate BibTeX keys or fields — source from Zotero (`zotero_get_item`).

### 4. British English Rule
- The project uses British English throughout.
- Use: *colour, behaviour, optimisation, modelling, analyse, recognise, favour*.
- Avoid American spellings.

---

## Overleaf Repo Reference

| File | Purpose |
|---|---|
| `template.tex` | LaTeX preamble and document class (`IEEEtran, journal`). Always use as header. |
| `main.tex` | Current working manuscript. Do not overwrite — create new file instead. |
| `IEEEexample.bib` | Bibliography database. Add new entries here. |
| `main_revised_background.tex` | Revised background section (separate file — check before drafting background). |

**Commit message format:**
```
Add manuscript draft: <section or version descriptor>
```

---

## Project-Specific Context (Meta-RL for IPC+FTC)

This skill is calibrated for the following research project. Use this context when inferring missing information.

| Element | Value |
|---|---|
| Domain | Offshore wind turbine control |
| Control Task | Individual Pitch Control (IPC) with Fault-Tolerant Control (FTC) |
| Fault Types | Actuator fault, Sensor fault |
| Core Problem | Model-based methods rely on accurate modelling; standard RL ignores temporal fault dynamics |
| Research Gap | Existing RL-FTC methods cannot adapt to unseen actuator dynamics without retraining |
| Hypothesis | Meta-RL with temporal context encoding can adapt to different actuator dynamics at inference time |
| Method | Context-based Meta-RL (PEARL variant) + TCN (temporal pattern extraction) + LSTM (sequential context) |
| Evaluation Metric | DEL (Damage Equivalent Load), rotor speed fluctuation |
| Ablation Baselines | 1. SAC only; 2. MLP context encoder; 3. Load mitigation mission only |

**Key causal relationship:**
> Reinforcement learning's difficulty (*can only see the current state; temporal characteristic is ignored*) **is fixed by** Meta-RL with context-based encoder (*PEARL-style latent context allows adaptation to different actuator dynamics*).

---

## Quality Checklist Before Submitting a Manuscript Draft

- [ ] Every citation is accompanied by: problem + gap + reason for method adoption
- [ ] Introduction ends with clearly numbered contributions (bullet or numbered list)
- [ ] All contributions are specific (turbine-wise / IPC-wise / Meta-RL-FTC-wise)
- [ ] Problem formulation section includes MDP: actions, states (10), reward
- [ ] No American spellings
- [ ] New `.tex` file created (old one preserved)
- [ ] `template.tex` preamble used
- [ ] All cited papers have BibTeX entries in `.bib` file
- [ ] Ablation study labels match the XMind plan

---

## Error Handling

| Situation | Action |
|---|---|
| Paper not in Zotero | Report to user; skip or use item-level link. Suggest importing. |
| NotebookLM returns vague answer | Follow-up with targeted questions (paper title, author, specific claim). |
| No teacher paper provided | Ask user: "Which papers should I use as writing style/method models?" |
| XMind outline missing | Generate outline from scratch using canonical structure above. |
| Unclear logical chain between paragraphs | Explicitly ask user before drafting (Step 3 optional clarification). |
