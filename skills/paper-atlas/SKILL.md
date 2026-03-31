---
name: paper-atlas
description: >
  Read an XMind paper outline, use NotebookLM to find relevant papers and content,
  then annotate Zotero highlights and link them back into the XMind mind map.
  Orchestrates xmind + notebooklm + zotero-mcp for literature mapping.
---

# Paper Atlas — Literature Mapping Skill

Automate the workflow of mapping literature references onto a paper outline in XMind, using NotebookLM for source-grounded paper discovery and Zotero MCP for annotation linking.

## When to Use This Skill

Trigger when user:
- Wants to fill an XMind outline with literature references
- Mentions "paper atlas", "literature map", "fill outline with papers"
- Has an .xmind file representing a paper structure and wants papers linked
- Asks to connect their XMind outline to Zotero annotations via NotebookLM
- Says "I need proof" — provide supporting evidence with paper titles included

## Prerequisites

- **Zotero MCP** server running (provides `zotero_*` tools)
- **NotebookLM** skill authenticated (`"C:\Users\jf844\AppData\Local\anaconda3\envs\DSAC\python.exe" scripts/run.py auth_manager.py status` in notebooklm skill dir)
- **XMind** skill available for writing .xmind files
- User's research papers already uploaded to both Zotero library and NotebookLM notebook

## Complete Workflow

### Phase 1: Read the XMind Outline

```bash
node "<skill-dir>/scripts/read_xmind.mjs" "<path-to-xmind-file>"
```

This outputs JSON with the full hierarchy and a readable `outline` field. Parse the hierarchy to understand:
- The paper's overall topic (root node)
- Major sections (level 1 children)
- Subsections and specific topics that need literature support (deeper levels)
- Any existing hrefs/notes already present

Identify **leaf nodes** and **sections without children** — these are the slots to fill with papers.

### Phase 2: Formulate Questions for NotebookLM

Analyze the outline and generate targeted questions. For each section that needs papers, formulate questions like:

| Outline Section | Question Type | Example |
|---|---|---|
| Classification with named methods | Representative papers | "What are the key papers for PEARL, MAML, and RL2 in meta-reinforcement learning?" |
| "Why use X for Y" | Motivation/justification | "What reasons do papers give for using meta-RL in fault-tolerant control?" |
| Paper Review section | Contributions survey | "Who has applied meta-learning to fault-tolerant control, and what are their main contributions?" |
| Methodology section | Technical details | "What specific algorithms or architectures are proposed for X?" |

**Rules for question formulation:**
1. Reference specific terms from the outline to ground the question
2. Ask for paper names, authors, and specific content — not just summaries
3. Ask one focused question per section, not combined mega-questions
4. Include context: "According to [parent topic], ..."

### Phase 3: Query NotebookLM

Run questions using the notebooklm skill. The skill directory is at `~/.claude/skills/notebooklm/`.

```bash
"C:\Users\jf844\AppData\Local\anaconda3\envs\DSAC\python.exe" "~/.claude/skills/notebooklm/scripts/run.py" ask_question.py --question "<question>" --notebook-id <id>
```

**CRITICAL:** Follow the NotebookLM follow-up protocol. After each answer:
1. Check if the answer names specific papers with enough detail
2. If not, ask follow-up questions to get paper titles, authors, and specific claims
3. Continue until you have concrete paper names and content references for each outline section

Collect from each NotebookLM answer:
- **Paper titles** mentioned
- **Specific claims or content** referenced (quotes or paraphrases)
- **Which outline section** each paper/content maps to

### Phase 4: Find Papers in Zotero and Get Annotations

For each paper identified by NotebookLM:

#### 4a. Search for the paper in Zotero
Use the Zotero MCP tools:
```
zotero_search_items(query: "paper title or author")
```
or for better matching:
```
zotero_semantic_search(query: "the specific claim or topic")
```

Record the **item key** for each found paper.

#### 4b. Get existing annotations
```
zotero_get_annotations(item_key: "<key>")
```

Check if the content NotebookLM referenced is already highlighted. If an annotation matches the referenced content, record its annotation key.

#### 4c. If no matching annotation exists — create a note
If the specific content isn't already highlighted, use:
```
zotero_create_note(item_key: "<key>", content: "Referenced content: <the specific claim>")
```

**Note:** The MCP server may not support creating PDF annotations directly. In that case:
1. Record the item key and the PDF attachment key (from `zotero_get_item_children`)
2. Present the user with a list of content to highlight manually in Zotero
3. After the user highlights, re-run `zotero_get_annotations` to get the annotation keys

### Phase 5: Generate Zotero Links

Build zotero:// URIs for each reference:

**For PDF annotations (highlights):**
```
zotero://open-pdf/library/items/<PDF_ITEM_KEY>?&annotation=<ANNOTATION_KEY>
```

**For item-level links (fallback):**
```
zotero://select/library/items/<ITEM_KEY>
```

To get the PDF_ITEM_KEY, use `zotero_get_item_children(item_key)` and find the attachment with `contentType: "application/pdf"`.

### Phase 6: Update XMind with Linked Papers

Build the updated XMind JSON structure. For each outline section that received papers:

**Add paper children with Zotero hyperlinks:**

**IMPORTANT: Notes MUST always start with the full paper title first!**

```json
{
  "title": "Paper Title (Author, Year)",
  "href": "zotero://open-pdf/library/items/M8EJIWCZ?&annotation=WM9ENHUA",
  "notes": {
    "html": "<strong>Paper:</strong> Full Paper Title Here<br><br><strong>Key finding:</strong> <font color='#c3272b'>The specific highlighted content</font><br><br><strong>Relevance:</strong> Supports the claim that..."
  }
}
```

**For papers with multiple relevant highlights, add sub-children:**
```json
{
  "title": "Paper Title (Author, Year)",
  "href": "zotero://select/library/items/ITEMKEY",
  "children": [
    {
      "title": "Claim 1: Brief description",
      "href": "zotero://open-pdf/library/items/PDFKEY?&annotation=ANN1"
    },
    {
      "title": "Claim 2: Brief description",
      "href": "zotero://open-pdf/library/items/PDFKEY?&annotation=ANN2"
    }
  ]
}
```

### Phase 7: Write the Updated XMind

Use the xmind skill's create script to write the enriched mind map:

```bash
node "~/.claude/skills/xmind/scripts/create_xmind.mjs" < /tmp/xmind_input.json
```

The output path should be the same file (overwrite) or a new file like `<original>_enriched.xmind` — ask the user.

## Output Format in XMind

The final XMind structure for the demo example would look like:

```
MetaRL-FTC
├── Meta Reinforcement Learning
│   ├── Classification
│   │   ├── PEARL
│   │   │   ├── Rakelly et al. 2019 → zotero://open-pdf/...?annotation=...
│   │   │   └── Key insight: ... → zotero://open-pdf/...?annotation=...
│   │   ├── MAML
│   │   │   └── Finn et al. 2017 → zotero://open-pdf/...?annotation=...
│   │   └── RL2
│   │       └── Duan et al. 2016 → zotero://open-pdf/...?annotation=...
│   └── Meta RL for Fault Tolerant Control
│       ├── Why use MetaRL to handle FTC
│       │   ├── Reason 1: ... → zotero://...
│       │   └── Reason 2: ... → zotero://...
│       └── Paper Review
│           ├── Author2023 - Contribution summary → zotero://...
│           └── Author2024 - Contribution summary → zotero://...
```

## Important Rules

1. **Never fabricate paper titles or citations.** All papers must come from NotebookLM (grounded in user's documents) and be verified in Zotero.
2. **Preserve the original outline structure.** Only add children — never rename or remove existing nodes.
3. **Every paper node must have an `href`** pointing to a zotero:// link.
4. **Ask the user before overwriting** the original .xmind file.
5. **If a paper from NotebookLM isn't in Zotero**, tell the user and skip it (or add it without a link, labeled clearly).
6. **Batch the NotebookLM questions** — ask all questions first, then process Zotero in bulk. This avoids back-and-forth delays.
7. **Present a summary before writing** — show the user which papers map to which sections and get confirmation before generating the final XMind.
8. **ALWAYS put the full paper title FIRST in branch notes.** Every `notes.html` field must start with `<strong>Paper:</strong> Full Paper Title` before any other content (key findings, relevance, etc.). This is mandatory for all paper branches added from NotebookLM feedback.

## Manual Highlight Workflow

When the Zotero MCP can't create PDF annotations directly, present the user with a highlight task list:

```
Papers to highlight in Zotero:
1. [Paper Title] — Page X: "exact quote to highlight"
2. [Paper Title] — Page Y: "exact quote to highlight"
...

After highlighting, say "done" and I'll fetch the annotation keys.
```

Then re-query `zotero_get_annotations` for each paper and match the new annotations to build the links.

## Error Handling

- **Paper not in Zotero**: Skip and report. Suggest user imports it.
- **NotebookLM rate limit**: Pause and inform user. Resume when possible.
- **No matching annotations**: Use item-level link (`zotero://select/...`) as fallback.
- **XMind read fails**: Check file path, ensure it's a valid .xmind file.

## "I Need Proof" Workflow

When the user says "I need proof" for any claim made during the atlas workflow, provide supporting evidence in this format:

**Required format — always include paper title:**
```
**Proof for: [the claim being supported]**

**Paper Title** (Author, Year)
> "Exact quote or annotation from the paper that supports this claim"
[View in Zotero](zotero://open-pdf/library/items/PDFKEY?annotation=ANNKEY)
```

**Multiple sources format:**
```
**Proof for: [the claim being supported]**

1. **Paper Title A** (Author, Year)
   > "Supporting quote from paper A"
   [View in Zotero](zotero://...)

2. **Paper Title B** (Author, Year)
   > "Supporting quote from paper B"
   [View in Zotero](zotero://...)
```

**Rules for providing proof:**
1. **Always include the full paper title** — never omit it
2. Include author and year when available
3. Provide the exact quote or annotation that supports the claim
4. Include Zotero link when available (item-level link as fallback)
5. If no proof exists in the sources, say so explicitly rather than fabricating
