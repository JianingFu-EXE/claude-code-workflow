---
name: notebook-query
description: >
  Query NotebookLM and add answers as floating topics in an XMind file.
  For quick research questions that get captured directly into your mind maps.
---

# Notebook Query — NotebookLM to XMind with Zotero Links

Query NotebookLM for answers, find the referenced papers in Zotero, and add them as floating topics in XMind with clickable PDF annotation links.

## When to Use This Skill

Trigger when user:
- Asks a research question and wants the answer written to an XMind file as a floating topic
- Mentions "floating topic", "add to xmind", "write this to my mindmap"
- Specifies both a NotebookLM notebook AND an XMind file for the answer
- Says something like "In notebook X, I want to know Y and write it to Z.xmind"

## Prerequisites

- **NotebookLM** skill authenticated (`"C:\Users\jf844\AppData\Local\anaconda3\envs\DSAC\python.exe" scripts/run.py auth_manager.py status` in notebooklm skill dir)
- **Zotero MCP** server running (provides `zotero_*` tools)
- **XMind** skill available for reading/writing .xmind files
- Papers referenced must be in both NotebookLM AND Zotero library

## Workflow

### Step 1: Parse User Request

Extract from user's message:
- **Question**: What they want to know
- **Notebook**: Which NotebookLM notebook to query (by name or ID)
- **XMind file**: Path to the .xmind file to update

Example user request:
> "In notebook GFM/GFL, I want to know which paper used discrete switching between GFM and GFL and write this in GFM.xmind as floating"

Parsed:
- Question: "Which paper used discrete switching between GFM and GFL?"
- Notebook: "GFM/GFL" (search by name)
- XMind file: "GFM.xmind"

### Step 2: Find the Notebook

```bash
# List notebooks to find the right one
"C:\Users\jf844\AppData\Local\anaconda3\envs\DSAC\python.exe" "~/.claude/skills/notebooklm/scripts/run.py" notebook_manager.py list

# Or search by topic
"C:\Users\jf844\AppData\Local\anaconda3\envs\DSAC\python.exe" "~/.claude/skills/notebooklm/scripts/run.py" notebook_manager.py search --query "GFM"
```

### Step 3: Query NotebookLM

```bash
"C:\Users\jf844\AppData\Local\anaconda3\envs\DSAC\python.exe" "~/.claude/skills/notebooklm/scripts/run.py" ask_question.py \
  --question "Which paper used discrete switching between GFM and GFL?" \
  --notebook-id <notebook-id>
```

**CRITICAL:** Follow up if needed! NotebookLM answers end with "Is that ALL you need to know?" — if the answer is incomplete, ask follow-up questions to get:
- Specific paper titles
- Author names
- Key claims or quotes that answer the question

### Step 4: Find Papers in Zotero

For each paper mentioned by NotebookLM:

```
# Search for the paper
zotero_search_items(query: "paper title or author")

# Or semantic search for the specific claim
zotero_semantic_search(query: "the specific claim from NotebookLM")
```

Record the **item key** for each found paper.

### Step 5: Get Annotations and Build Links

For each paper found:

```
# Get the paper's children (to find PDF attachment)
zotero_get_item_children(item_key: "<key>")

# Get existing annotations
zotero_get_annotations(item_key: "<key>")
```

**Build Zotero links:**

For PDF annotations (highlights):
```
zotero://open-pdf/library/items/<PDF_ITEM_KEY>?annotation=<ANNOTATION_KEY>
```

For item-level links (fallback if no specific annotation):
```
zotero://select/library/items/<ITEM_KEY>
```

**Finding the right annotation:**
- Match NotebookLM's referenced content to existing annotations
- If the content isn't highlighted, use item-level link and note what to highlight

### Step 6: Read Existing XMind File

```bash
node "~/.claude/skills/paper-atlas/scripts/read_xmind.mjs" "<path-to-xmind-file>"
```

Parse to get the existing structure (root topic, sheet title).

### Step 7: Build Floating Topic with Zotero Links

Create a floating topic with paper children, each linked to Zotero:

```json
{
  "title": "Q: Which paper used discrete switching between GFM and GFL?",
  "position": {"x": 400, "y": 0},
  "children": [
    {
      "title": "Smith et al. 2023 - Seamless GFM/GFL Transition",
      "href": "zotero://open-pdf/library/items/ABC123?annotation=XYZ789",
      "notes": {
        "html": "<strong>Paper:</strong> Seamless GFM/GFL Transition<br><br><strong>Key finding:</strong><br>Describes discrete state machine for switching between modes triggered by grid events."
      }
    },
    {
      "title": "Jones et al. 2022 - Hybrid Inverter Control",
      "href": "zotero://open-pdf/library/items/DEF456?annotation=UVW012",
      "notes": {
        "html": "<strong>Paper:</strong> Hybrid Inverter Control<br><br><strong>Key finding:</strong><br>Uses hysteresis-based discrete switching with 100ms transition window."
      }
    }
  ]
}
```

### Step 8: Update XMind File

Build the complete JSON:

```json
{
  "path": "<path-to-xmind-file>",
  "sheets": [
    {
      "title": "<existing-sheet-title>",
      "freePositioning": true,
      "rootTopic": {
        // ... existing root topic structure preserved ...
      },
      "detachedTopics": [
        {
          "title": "Q: <brief question>",
          "position": {"x": 400, "y": 0},
          "children": [
            {
              "title": "<Author Year> - <Brief description>",
              "href": "zotero://open-pdf/library/items/<PDF_KEY>?annotation=<ANN_KEY>",
              "notes": {"html": "<strong>Paper:</strong> Full Paper Title<br><br><strong>Key finding:</strong><br>..."}
            }
          ]
        }
      ]
    }
  ]
}
```

Write and execute:

```bash
node "~/.claude/skills/xmind/scripts/create_xmind.mjs" < /tmp/xmind_input.json
```

## Floating Topic Structure

```
[Floating Topic]
Q: Discrete switching GFM/GFL papers
├── Smith et al. 2023 → zotero://open-pdf/...?annotation=...
│   Notes: Key finding about discrete state machine...
├── Jones et al. 2022 → zotero://open-pdf/...?annotation=...
│   Notes: Hysteresis-based switching approach...
└── Chen et al. 2021 → zotero://select/library/items/...
    Notes: (No specific annotation - item link)
```

## Important Rules

1. **Every paper MUST have an href** — Either annotation link or item-level link
2. **Preserve existing content** — Never modify existing topics
3. **Use annotation links when possible** — `zotero://open-pdf/...?annotation=...` is preferred
4. **Fall back to item links** — Use `zotero://select/...` if no matching annotation
5. **Include key findings in notes** — What specifically answers the question
6. **Follow NotebookLM protocol** — Ask follow-ups until you have specific paper names
7. **Confirm before saving** — Ask user before overwriting their XMind file

## Error Handling

| Problem | Solution |
|---------|----------|
| Paper not in Zotero | Skip and report. Use item link if partial match found. |
| No matching annotation | Use item-level link, note the quote to highlight manually |
| NotebookLM vague answer | Ask follow-up: "What are the specific paper titles and authors?" |
| XMind file doesn't exist | Ask user if they want to create a new file |

## Quick Reference

```bash
# 1. Check NotebookLM auth
"C:\Users\jf844\AppData\Local\anaconda3\envs\DSAC\python.exe" "~/.claude/skills/notebooklm/scripts/run.py" auth_manager.py status

# 2. List notebooks
"C:\Users\jf844\AppData\Local\anaconda3\envs\DSAC\python.exe" "~/.claude/skills/notebooklm/scripts/run.py" notebook_manager.py list

# 3. Query notebook
"C:\Users\jf844\AppData\Local\anaconda3\envs\DSAC\python.exe" "~/.claude/skills/notebooklm/scripts/run.py" ask_question.py --question "..." --notebook-id <id>

# 4. Zotero MCP tools
zotero_search_items(query: "...")
zotero_get_item_children(item_key: "...")
zotero_get_annotations(item_key: "...")

# 5. Read XMind
node "~/.claude/skills/paper-atlas/scripts/read_xmind.mjs" "<file.xmind>"

# 6. Write updated XMind
node "~/.claude/skills/xmind/scripts/create_xmind.mjs" < /tmp/xmind_input.json
```

## Link Format Reference

| Link Type | Format | When to Use |
|-----------|--------|-------------|
| PDF Annotation | `zotero://open-pdf/library/items/<PDF_KEY>?annotation=<ANN_KEY>` | Specific highlight exists |
| Item Select | `zotero://select/library/items/<ITEM_KEY>` | No annotation, opens item in Zotero |

To get PDF_KEY: Use `zotero_get_item_children(item_key)` and find attachment with `contentType: "application/pdf"`.
