---
name: xmind
description: >
  Create and revise XMind mind map files (.xmind). Use this skill when the user asks to create a mind map,
  mindmap, XMind file, or brainstorming diagram. Supports versioned workflows with `.source.json` sidecar
  files for incremental revisions.
---

# XMind Workflow

## Two modes

- **`create`** (default when no `.source.json` exists): Build JSON, render `.xmind`
- **`revise`** (default when `.source.json` or `.latest.json` exists): Edit only changed nodes, render new version

## Quick start — create

1. Build a JSON object with `path` and `sheets` fields
2. Write to a temp file, then run:

```bash
node <skill-dir>/scripts/create_xmind.mjs < /tmp/xmind_input.json
```

## Versioned workflow — revise

```bash
# Extract existing .xmind to editable source
node <skill-dir>/scripts/extract_xmind.mjs /abs/path/map.xmind

# Clone source to next version
node <skill-dir>/scripts/prepare_revision.mjs --source /abs/path/map_v01.source.json

# Render .xmind from source
node <skill-dir>/scripts/create_xmind.mjs --source /abs/path/map_v02.source.json
```

## JSON Input Format

### Legacy (stdin with `path`)

```json
{
  "path": "/Users/user/Desktop/my_mindmap.xmind",
  "sheets": [{ "title": "Sheet 1", "rootTopic": { "title": "Central Topic", "children": [...] } }]
}
```

### Versioned (source.json)

```json
{
  "document": { "title": "Map", "stem": "map", "version": 2, "detail": "lean" },
  "sheets": [
    {
      "title": "Main",
      "rootTopic": { "id": "root", "title": "Central Topic", "children": [{ "id": "b1", "title": "Branch 1" }] }
    }
  ]
}
```

## Topic Properties

| Field | Type | Description |
|-------|------|-------------|
| `title` | string (required) | Topic title |
| `children` | array of topics | Child topics |
| `notes` | string or `{plain?, html?}` | Notes. HTML supports: `<strong>`, `<u>`, `<ul>`, `<ol>`, `<li>`, `<br>`. NOT `<code>`. |
| `href` | string | External URL link |
| `attachment` | string | Absolute path to a file to attach (embedded in the .xmind). Mutually exclusive with `href`. |
| `linkToTopic` | string | Title of another topic to link to (internal `xmind:#id` link, works across sheets) |
| `linkToTopicId` | string | ID of another topic to link to |
| `labels` | string[] | Tags/labels |
| `markers` | string[] | Marker IDs: `task-done`, `task-start`, `priority-1` to `priority-9` |
| `callouts` | string[] | Callout text bubbles |
| `boundaries` | `{range, title?}[]` | Visual grouping of children. Range: `"(start,end)"` |
| `summaryTopics` | `{range, title}[]` | Summary topics spanning children ranges |
| `structureClass` | string | Layout (see below) |
| `shape` | string | Topic shape (see shapes below) |
| `position` | `{x, y}` | Absolute position (only for detached topics in free-positioning sheets) |
| `image` | `{src}` | Embedded image reference, e.g. `{"src": "xap:resources/img.png"}` |
| `styleProperties` | object | Inline style overrides: `fo:font-size`, `fo:font-weight`, `fo:color`, `svg:fill`, etc. |

### Topic shapes

- `org.xmind.topicShape.roundedRect` — rounded rectangle (default)
- `org.xmind.topicShape.diamond` — diamond (conditions/decisions)
- `org.xmind.topicShape.ellipserect` — ellipse (start/end)
- `org.xmind.topicShape.rect` — rectangle
- `org.xmind.topicShape.underline` — underline only
- `org.xmind.topicShape.circle` — circle
- `org.xmind.topicShape.parallelogram` — parallelogram (I/O)

### Layout structures

- `org.xmind.ui.map.clockwise` — balanced map
- `org.xmind.ui.map.unbalanced` — unbalanced map
- `org.xmind.ui.logic.right` — logic chart (right)
- `org.xmind.ui.org-chart.down` — org chart (down)
- `org.xmind.ui.tree.right` — tree (right)
- `org.xmind.ui.fishbone.leftHeaded` — fishbone
- `org.xmind.ui.timeline.horizontal` — timeline
- `org.xmind.ui.treetable` — tree table

### Task properties

**Simple checkbox** (no dates needed):
- `taskStatus`: `"todo"` or `"done"`

**Planned tasks** (for Gantt/timeline view):

| Field | Type | Description |
|-------|------|-------------|
| `progress` | number 0.0-1.0 | Completion progress |
| `priority` | number 1-9 | Priority (1=highest) |
| `startDate` | ISO 8601 string | Start date |
| `dueDate` | ISO 8601 string | Due date |
| `durationDays` | number | Duration in days (preferred for relative planning) |
| `dependencies` | array | `{targetTitle, type, lag?}` — type: `FS`, `FF`, `SS`, `SF` |

## Sheet properties

| Field | Type | Description |
|-------|------|-------------|
| `title` | string (required) | Sheet title |
| `rootTopic` | topic (required) | Root topic |
| `relationships` | array | `{sourceTitle, targetTitle, title?, shape?}` — connects topics by title |
| `detachedTopics` | array of topics | Free-floating topics (require `freePositioning: true`) |
| `freePositioning` | boolean | Enable free topic positioning |

## Logic / Flow diagrams

For flowcharts, use **free positioning** with **detached topics** and **straight relationships**:

```json
{
  "path": "/tmp/flowchart.xmind",
  "sheets": [{
    "title": "Algorithm",
    "freePositioning": true,
    "rootTopic": { "title": "START", "shape": "org.xmind.topicShape.ellipserect" },
    "detachedTopics": [
      {"title": "IS X > 0?", "position": {"x": 0, "y": 130}, "shape": "org.xmind.topicShape.diamond"},
      {"title": "END", "position": {"x": 0, "y": 260}, "shape": "org.xmind.topicShape.ellipserect"}
    ],
    "relationships": [
      {"sourceTitle": "START", "targetTitle": "IS X > 0?", "shape": "org.xmind.relationshipShape.straight"}
    ]
  }]
}
```

## Inline styles (styleProperties)

Use `styleProperties` for font, color, and fill overrides. Preserved through extract/revise cycles.

```json
{
  "title": "¶1: Introduction",
  "styleProperties": {
    "fo:font-size": "14",
    "fo:font-weight": "bold",
    "fo:color": "#FFFFFF",
    "svg:fill": "#FF6B35"
  }
}
```

Common style keys: `fo:font-size`, `fo:font-weight`, `fo:font-style`, `fo:color`, `svg:fill`, `fo:font-family`.

## Detail modes

- `lean`: titles first, notes only when needed
- `balanced`: short notes on major branches
- `rich`: broader notes when explicitly requested

## Revision rules

- Edit the sidecar `.source.json`, not the `.xmind` archive
- In `revise`, output only the target version path and changed nodes
- Do not restate unchanged branches
- Do not regenerate the whole map unless asked
- Open the newest versioned `.xmind` instead of waiting for overwritten file to refresh

## Working with large files

When reading a PDF or other large file fails, extract text first:

```bash
pdftotext input.pdf /tmp/extracted.txt
```

## Important rules

- The output path MUST end with `.xmind`
- IDs are generated automatically
- Topic references in relationships and dependencies are resolved by title
- HTML notes: only `<strong>`, `<u>`, `<ul>`, `<ol>`, `<li>`, `<br>` supported
- Internal links (`linkToTopic`/`linkToTopicId`) work across sheets
- **Notes should be substantial** — don't just repeat the topic title. Use notes to add explanations, context, key points. Use HTML notes for structured content. Most topics should have notes unless self-explanatory.
- Embedded images are preserved through extract/revise cycles when `importedFrom` is tracked in the document metadata.
