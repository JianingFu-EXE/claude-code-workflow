# Thesis XMind Format Specification

> Canonical format for thesis_structure_v*.xmind files. Claude MUST follow this when generating or modifying thesis structure XMind files.

## Sheet Architecture

### Two-Layer Design

The .xmind file has two distinct layers of content:

| Layer | Where | Inline styles | Notes | Refs/LW/Citations | Images | Markers | Labels |
|-------|-------|:---:|:---:|:---:|:---:|:---:|:---:|
| **Overview** | Sheet 0 | NO | NO | NO | YES | YES | YES |
| **Per-chapter detail** | Sheets 1–N | YES | YES | YES | YES | YES | YES |

**The overview is a structural skeleton.** It has the same topic hierarchy, figures, labels, and markers as the detail sheets, but NO inline styles, NO notes, and NO annotation children (⚡ linking words, 📄 references, citation purpose nodes).

**Per-chapter detail sheets are the authoritative source.** They contain the full richness: every inline style, note, linking word, reference, citation purpose node, image, and marker.

### Sheet Structure

| Sheet | Title | Root structureClass | Purpose |
|-------|-------|---------------------|---------|
| 0 | Overview (Tree Table) | `org.xmind.ui.treetable` | Structural skeleton — labels, figs, markers but NO styles/notes/annotations |
| 1–N | Ch {N}: {Short Title} | `org.xmind.ui.logic.right` | Per-chapter detail sheets — FULL content with all annotations |
| Last | Ch1 Missing Figures Checklist | (any) | Tracking sheet for figure creation |

**Rule**: The overview sheet MUST contain ALL structural content at full depth. Per-chapter detail sheets contain the same structure PLUS all annotations. Every figure must appear in both layers.

## Theme (copy verbatim into every sheet)

```json
{
  "centralTopic": {"properties": {"fo:font-family": "NeverMind", "fo:font-size": "28pt", "fo:font-weight": "500", "fo:font-style": "normal", "fo:text-transform": "manual", "fo:text-decoration": "none", "fo:text-align": "center", "fill-pattern": "none", "line-width": "3pt", "line-pattern": "solid", "border-line-width": "2", "border-line-pattern": "inherited", "shape-class": "org.xmind.topicShape.rect", "line-class": "org.xmind.branchConnection.curve", "arrow-end-class": "org.xmind.arrowShape.none", "alignment-by-level": "inherited"}},
  "mainTopic": {"properties": {"fo:font-family": "NeverMind", "fo:font-size": "18pt", "fo:font-weight": "500", "fo:font-style": "normal", "fo:text-transform": "manual", "fo:text-decoration": "none", "fill-pattern": "none", "line-width": "inherited", "line-pattern": "inherited", "border-line-width": "0", "border-line-pattern": "inherited", "shape-class": "org.xmind.topicShape.rect", "line-class": "org.xmind.branchConnection.curve", "arrow-end-class": "inherited", "alignment-by-level": "inherited"}},
  "subTopic": {"properties": {"fo:font-family": "NeverMind", "fo:font-size": "14pt", "fo:font-weight": "400", "fo:font-style": "normal", "fo:text-transform": "manual", "fo:text-decoration": "none", "fill-pattern": "none", "line-width": "inherited", "line-pattern": "inherited", "border-line-width": "0", "border-line-pattern": "inherited", "shape-class": "org.xmind.topicShape.rect", "line-class": "org.xmind.branchConnection.curve", "arrow-end-class": "inherited", "alignment-by-level": "inherited"}}
}
```

## Extensions (overview sheet only)

```json
[{"provider": "org.xmind.ui.skeleton.structure.style", "content": {"centralTopic": "org.xmind.ui.treetable", "floatingTopic": "org.xmind.ui.logic.right"}}]
```

## Topic Hierarchy & Inline Styles (detail sheets only)

Topics in detail sheets use inline `style.properties` to override theme defaults. The hierarchy is depth-based:

| Depth | Role | Title Pattern | Style Properties |
|-------|------|---------------|-----------------|
| D0 | Chapter root | `Chapter N: Title` | `{"fo:font-size": "18", "fo:font-weight": "bold"}` |
| D1 | Section / Preamble | `§N.M Title` or `Preamble (before §N.M)` | `{"fo:font-size": "15", "fo:font-weight": "bold"}` (preamble) or `{"fo:font-size": "16", "fo:font-weight": "bold"}` (section) |
| D2 | Subsection or Paragraph | `§N.M.K Title` or `¶N: Description (~Nw)` | Subsection: `{"fo:font-size": "16", "fo:font-weight": "bold"}`. Paragraph: `{"fo:font-size": "14", "fo:font-weight": "bold"}` |
| D3 | Sentence or Paragraph (under subsection) | `SN: Text...` or `¶N: Description` | Sentence: `{"fo:font-size": "13"}`. Paragraph: `{"fo:font-size": "14", "fo:font-weight": "bold"}` |
| D4 | Sentence (under paragraph under subsection) | `SN: Text...` | `{"fo:font-size": "13"}` |

### Annotation Node Types (detail sheets only — children of sentences)

These are **children of sentence nodes** in detail sheets. They do NOT appear in the overview.

| Type | Title Pattern | Style Properties | Labels | Parent |
|------|---------------|-----------------|--------|--------|
| ⚡ Linking word | `⚡ Word` | `{"fo:font-size": "11", "fo:font-weight": "bold", "fo:color": "#FFFFFF", "svg:fill": "#FF6B35"}` | `["Linking Word"]` | Sentence that starts with the word |
| 📄 Reference | `📄 "Title" — Author (Year)` | `{"fo:font-size": "10", "fo:color": "#555555", "svg:fill": "#E8E0F0"}` | `["Reference"]` | Sentence that cites the source |
| Citation purpose | `Supports: what it supports` | `{"fo:font-size": "9", "fo:color": "#666666", "svg:fill": "#F0ECF5"}` | `["Citation Purpose"]` | 📄 Reference node (its parent) |

**Annotation tree**: `Sentence → ⚡ Linking Word` and `Sentence → 📄 Reference → Citation Purpose`

### Section-Level Linking Words (detail sheets only)

Sections like §2.3 may also have ⚡ linking words as **direct children alongside subsections** (e.g., `⚡ From offline DP to online iterative approximation` sits between subsection nodes). These use the same ⚡ style but serve as section-level narrative connectors rather than sentence annotations.

### Structural Node Types (both layers)

| Type | Title Pattern | Style Properties (detail only) | Labels |
|------|---------------|-------------------------------|--------|
| 🖼️ Figure | `🖼️ FIG N.M: Caption` | `{"fo:font-size": "13"}` | `["FIGURE NEEDED"]` or `["SVG READY — Type"]` |
| 📊 Table | `📊 TABLE N.M: Caption` | `{"fo:font-size": "13"}` | `["TABLE"]` or `["TABLE NEEDED"]` |
| ⚠️ Limitation | `⚠️ ¶N: LIMITATION REVEALED → Name` | `{"fo:font-size": "14", "fo:font-weight": "bold"}` | `["RESEARCH PROBLEM REVEALED"]` |

### Figure Properties

- Figures with `priority-1` marker: `"markers": [{"markerId": "priority-1"}]`
- Completed figures add `task-done`: `"markers": [{"markerId": "priority-1"}, {"markerId": "task-done"}]`
- Completed figures may have embedded images: `"image": {"src": "xap:resources/filename.png"}`
- Figure captions: child node with label `["Figure Caption"]`
- Figure data references: child 📄 node with label `["Reference"]` + citation purpose child

**CRITICAL**: Markers must be objects with string values: `{"markerId": "priority-1"}`. Never nested objects.

## Mandatory Content Rules

1. **Sentence hierarchy**: If a topic has sentence-level children (`S1:`, `S2:`...), they MUST be under a paragraph-level parent (`¶1:`, `¶2:`...). Never place sentences directly under a section.

2. **Figures at paragraph level**: Figure nodes (`🖼️ FIG`) sit as siblings of paragraphs within their section.

3. **Figure captions**: Each figure node should have a child with label `["Figure Caption"]` containing the full caption text.

4. **Linking words**: When a sentence starts with a linking/transition word (However, Furthermore, Crucially, etc.), add a **child** node of that sentence with the ⚡ style. The linking word is a child of the sentence, not a sibling.

5. **References**: When a sentence cites a source, add a **child** 📄 reference node of that sentence. The reference node itself has a **child** citation-purpose node explaining what the reference supports.

6. **Notes** (detail sheets only): Most structural nodes (chapter, section, subsection, paragraph) should have notes explaining purpose, word count, function. Notes format:
   - Simple: `{"plain": {"content": "text"}}`
   - Rich: `{"realHTML": {"content": "<strong>FUNCTION:</strong> text<br>..."}}`

## Notes Guidelines

| Level | Notes content |
|-------|---------------|
| Chapter root | Overall chapter purpose, page estimate, key decisions |
| Section (§) | Section function, relationship to thesis argument |
| Paragraph (¶) | Paragraph function (Context-Setting, Gap Identification, etc.), word count target |
| Figure (🖼️) | Figure description, what it shows, why it matters |
| Reference (📄) | Full citation, which claim it supports |

## Labels

Labels categorise topic function. Common labels:

| Label | Used on |
|-------|---------|
| `Funnel Opening`, `Scope Narrowing`, `Gap Identification`, `Contribution Preview`, `Roadmap` | Preamble paragraphs |
| `Context-Setting`, `Growth Data`, `Policy Context`, `Technology Trend`, `Narrative Bridge`, `Transition` | §1.1 paragraphs |
| `FOWT Physical Problem`, `FOWT Degradation Problem`, `Category Boundary` | §1.1.4 problems |
| `Review — Conventional`, `Review — NN-Assisted`, `Review — NN Control`, `Review — RL`, `Review — RL + FTC` | Literature review paragraphs |
| `RESEARCH PROBLEM REVEALED`, `Gap → Chapter` | Limitation/gap nodes |
| `Bridge`, `Backward Link`, `Forward Link`, `Compressed Gap`, `Contribution List` | Chapter intro pattern nodes |
| `FIGURE NEEDED`, `FIGURE NEEDED — CRITICAL`, `SVG READY — Type` | Figure status |
| `Reference`, `Citation Purpose`, `Linking Word` | Annotation nodes |
| `Chapter Intro Pattern`, `Chapter Closure` | Section-level role |

## Restructuring Procedure

When restructuring thesis_structure_v*.xmind (moving sections between chapters, adding methodology, etc.):

### Step 1: Source from DETAIL sheets, not overview

**Always deep-copy from per-chapter detail sheets** (Sheets 1–N). These contain all annotations, styles, notes, images, and markers. The overview sheet is a simplified skeleton — copying from it loses all richness.

```python
# CORRECT: deep-copy from detail sheet
section = copy.deepcopy(find_section(v12_detail_sheet_root, "§1.2"))

# WRONG: copying from overview (loses styles, notes, refs, LW, citations)
section = copy.deepcopy(find_section(v12_overview_root, "§1.2"))
```

### Step 2: True deep copy preserving all children

Every topic must be copied with its COMPLETE subtree — including all annotation children:
- ⚡ Linking words (children of sentences)
- 📄 References (children of sentences)
- Citation purpose nodes (children of references)
- Figure caption children
- Figure data reference children
- Embedded images (`"image": {"src": "xap:resources/..."}`)
- Markers (`"markers": [{"markerId": "..."}]`)
- Notes (`"notes": {...}`)
- Labels (`"labels": [...]`)
- Inline styles (`"style": {"properties": {...}}`)

Use `copy.deepcopy()` on the full topic object. Regenerate IDs after copying to avoid duplicates.

### Step 3: Subsection extraction

Subsections (e.g., §2.3.1) are **children of their parent section** (§2.3), not direct children of the chapter root. To extract them:

```python
# §2.3.1 is a child of §2.3, not of the chapter root
parent_section = find_section(chapter_root, "§2.3")
subsection = find_subsection(parent_section, "§2.3.1")
```

Also extract the ⚡ section-level linking words that sit between subsections — they are siblings of the subsections within the parent.

### Step 4: Build overview by stripping annotations

After building detail sheets, generate the overview by walking each detail chapter and stripping:
- Inline styles (don't copy `style.properties`)
- Notes (don't copy `notes`)
- ⚡ Linking word nodes (skip entirely)
- 📄 Reference nodes (skip entirely)
- Citation purpose nodes (skip entirely)

Keep: title, labels, markers, images, children structure, figure nodes.

### Step 5: Renumber figures per chapter

After restructuring, renumber all `🖼️ FIG N.M:` titles sequentially within each chapter:

```python
def renumber_figures(chapter_topic, chapter_num):
    figs = []  # collect all figures in tree order
    # Walk tree, collect fig topics
    for i, fig in enumerate(figs, 1):
        fig["title"] = re.sub(r"FIG \d+\.\d+:", f"FIG {chapter_num}.{i}:", fig["title"])
```

Image `src` paths (`xap:resources/filename.png`) point to ZIP-internal filenames and do NOT need renaming.

### Step 6: Copy resources

Copy all `resources/*` files (embedded PNGs) from the source .xmind into the new .xmind ZIP. These are referenced by `"image": {"src": "xap:resources/filename.png"}` in figure topics.

## Versioning

- **Never overwrite** existing .xmind files. Always create a new `_v{N+1}` version.
- Output path pattern: `<PHD>/MindMap/thesis_structure_v{N}.xmind`
