# 🧠 Academic Research Workflow: Obsidian + Zotero + Claude + PDF++ + Anki

A complete workflow for academic research combining bibliography management, note-taking, AI assistance, and spaced repetition.

> Originally built for urban geography and urban economics research, but adaptable to any academic field.

---

## Overview

```
Article / PDF found
        ↓
[Zotero] → captures metadata + PDF via browser connector
        ↓
[ZotMoov] → copies PDF into Obsidian vault with stable filename
        ↓
[Claude Desktop] → reads Zotero + vault, creates structured note
        ↓
[MCP Highlighter] → highlights PDF with color-coded annotations
        ↓
[pix2tex OCR] → extracts mathematical formulas as LaTeX
        ↓
[Obsidian + PDF++] → clickable note, annotated PDF, rendered equations
        ↓
[Anki] → spaced repetition flashcards synced from the note
```

---

## Requirements

| Tool | Version | Link |
|------|---------|------|
| Windows 10/11 | — | — |
| Obsidian | 1.x | [obsidian.md](https://obsidian.md) |
| Zotero | 7.x | [zotero.org](https://www.zotero.org) |
| Anki | latest | [apps.ankiweb.net](https://apps.ankiweb.net) |
| Node.js | LTS (v20+) | [nodejs.org](https://nodejs.org) |
| Python | 3.11 | [python.org](https://www.python.org) |
| pix2tex | latest | installed automatically via setup |
| Claude Desktop | latest | [claude.ai/download](https://claude.ai/download) |
| Everything *(optional)* | latest | [voidtools.com](https://www.voidtools.com) |

> ⚠️ If you have multiple Python versions installed, always use **Python 3.11** for every `pip` command in this guide.

> 💡 **Everything** is an optional but highly recommended file search tool for Windows. It indexes your entire drive instantly — very useful for locating PDFs by filename and diagnosing issues with the `all_pdf` folder.

---

## Quick Setup (Recommended)

Instead of configuring everything manually, run the automated setup script:

1. Clone or download this repository
2. Right-click `setup.ps1` → **Run with PowerShell**
3. Follow the interactive prompts

The script will automatically:
- Detect Node.js and Python 3.11
- Create the vault folder structure
- Install all Python and npm dependencies
- Download and install Obsidian plugins from GitHub
- Copy `server.py` into your vault
- Generate `claude_desktop_config.json` with the correct paths

> ⚠️ If PowerShell blocks execution, run this first in an admin terminal:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

### What still requires manual setup after the script

| Step | Where |
|------|-------|
| Enable Zotero local API | Zotero → Edit → Settings → Advanced |
| Install & configure ZotMoov | Zotero → Tools → Add-ons |
| Install AnkiConnect | Anki → Tools → Add-ons → code `2055492159` |
| Paste the system prompt | Claude Desktop → Profile |
| Restart Claude Desktop | Taskbar icon → right-click → Quit |

---

## Part 1 — Obsidian

### 1.1 Vault Structure

Create the following folder structure (or adapt to your own):

```
Vault/
├── 00 - MOC/                    # Maps of Content — thematic indexes
├── 10 - Literature Notes/       # One note per article/book (validated)
├── 20 - Permanent Notes/        # Atomic ideas, key concepts (validated)
├── 30 - Projects/               # Research project notes
├── 40 - Resources/              # Methods, tools, scripts
│   └── pdf_highlight_mcp/
│       └── server.py            ← PDF highlighting script
├── 90 - Claude/                 ← all Claude-generated content goes here
│   ├── Literature Notes/
│   ├── Permanent Notes/
│   └── Syntheses/
└── Bibliography/
    └── Zotero/
        └── all_pdf/             ← all PDFs with stable filenames
```

### 1.2 Plugins to Install

In Obsidian → Settings → Community Plugins → Browse:

| Plugin | Purpose |
|--------|---------|
| **PDF++** | Advanced PDF viewer + clickable annotations |
| **Local REST API** | Bridge between Obsidian and external tools |
| **Dataview** | Dynamic queries on your notes |
| **Flashcards** (by Reupload) | Sync flashcards from notes to Anki |

### 1.3 Configure Local REST API

1. Enable the Local REST API plugin
2. Go to its settings → copy the generated **API key**
3. Note the port (default: **27124**)

### 1.4 Configure the Flashcards Plugin

In the Flashcards plugin settings:

| Setting | Value |
|---------|-------|
| Default deck name | `Research::Urban Geography` |
| Flashcards #tag | `basic` |
| Inline card separator | `::` |
| Source support | ✅ enabled |
| Inline ID support | ✅ enabled |
| Code highlight support | ✅ enabled (if you use Python/GIS code) |
| Folder-based deck name | ✅ enabled |

---

## Part 2 — Zotero

### 2.1 Zotero Plugins to Install

| Plugin | Link | Purpose |
|--------|------|---------|
| **Better BibTeX** | [retorque.re/zotero-better-bibtex](https://retorque.re/zotero-better-bibtex/installation/) | Stable citation keys |
| **ZotMoov** | [github.com/wileyyugioh/zotmoov](https://github.com/wileyyugioh/zotmoov/releases) | Copies PDFs into vault |

Installation: Zotero → Tools → Add-ons → gear icon → *Install Add-on From File* → select the `.xpi`

### 2.2 Configure ZotMoov

Zotero → Edit → Settings → **ZotMoov**:

| Setting | Value |
|---------|-------|
| Directory to Move/Copy Files To | `P:\Obsidian Vaults\Research\Bibliography\Zotero\all_pdf` |
| File Behavior | **Copy** |
| Automatically Move/Copy When Added | ✅ checked |
| Automatically Move/Copy to Subdirectory | ☐ unchecked |

### 2.3 Enable Zotero Local API

Zotero → Edit → Settings → **Advanced**:
- Check **"Allow other applications on this computer to communicate with Zotero"**

### 2.4 Migrate Existing PDFs

To copy all your existing PDFs into `all_pdf` in one go:
1. Select your entire library (`Ctrl+A`)
2. Right-click → **ZotMoov → Move/Copy Files**

---

## Part 3 — Anki

### 3.1 Install AnkiConnect

In Anki → Tools → Add-ons → Get Add-ons → enter code: **`2055492159`**

Restart Anki. It must remain **open in the background** for sync to work.

### 3.2 How Flashcard Sync Works

Claude automatically generates a `## Flashcards` section at the end of each literature note:

```markdown
## Flashcards
#basic

What is urban densification?::Increase in population or building density within an existing urban area, distinct from urban sprawl.

What method do Broitman & Koomen use to measure densification?::Population density variation at grid cell level (500m × 500m) over 1990–2010.

How to read a shapefile with GeoPandas?::
    import geopandas as gpd
    gdf = gpd.read_file("file.shp")
```

To sync to Anki: in Obsidian, press `Ctrl+P` → *Flashcards: Sync to Anki*

---

## Part 4 — Claude Desktop

### 4.1 Installation

Download and install [Claude Desktop](https://claude.ai/download).

> ℹ️ Claude Desktop requires an Anthropic account with API credits or a subscription.

### 4.2 Install Node.js and the Obsidian MCP Server

```powershell
# Check Node.js
node --version

# Install official Anthropic filesystem MCP server
npm install -g @modelcontextprotocol/server-filesystem

# Verify
where mcp-server-filesystem
```

### 4.3 Install Python Dependencies

```powershell
C:\Users\YOUR_NAME\AppData\Local\Programs\Python\Python311\python.exe -m pip install pymupdf mcp zotero-mcp
```

### 4.4 Copy the Highlighting Script

Copy `server.py` (provided in this repository) to:
```
P:\Obsidian Vaults\Research\40 - Resources\pdf_highlight_mcp\server.py
```

### 4.5 Configure claude_desktop_config.json

Open `%APPDATA%\Claude\claude_desktop_config.json` and replace its content with:

```json
{
  "preferences": {
    "coworkWebSearchEnabled": true,
    "coworkScheduledTasksEnabled": false,
    "ccdScheduledTasksEnabled": false
  },
  "mcpServers": {
    "obsidian-vault": {
      "command": "C:\\Users\\YOUR_NAME\\AppData\\Roaming\\npm\\mcp-server-filesystem.cmd",
      "args": ["P:\\Obsidian Vaults\\Research"]
    },
    "zotero": {
      "command": "C:\\Users\\YOUR_NAME\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\zotero-mcp.exe",
      "env": {
        "ZOTERO_LOCAL": "true",
        "ZOTERO_LIBRARY_TYPE": "user"
      }
    },
    "pdf-highlighter": {
      "command": "C:\\Users\\YOUR_NAME\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
      "args": [
        "P:\\Obsidian Vaults\\Research\\40 - Resources\\pdf_highlight_mcp\\server.py"
      ],
      "env": {
        "VAULT_PATH": "P:\\Obsidian Vaults\\Research"
      }
    }
  }
}
```

> ⚠️ Replace `YOUR_NAME` with your Windows username everywhere.

### 4.6 Configure the System Prompt

In Claude Desktop → click your avatar → **Profile** → paste the content of `claude_system_prompt_v6.md` into the "What would you like Claude to know about you?" field.

### 4.7 Verify the Connection

Fully restart Claude Desktop (right-click taskbar icon → Quit).

Verify there are **no MCP error messages**. Test with:

```
List the files at the root of my Obsidian vault
```
```
List the collections in my Zotero library
```
```
List the available highlighting colors
```

---

## Part 4b — Mathematical Formula Extraction (pix2tex)

Papers in economics and urban economics often contain dense mathematical notation. The PDF highlighter server includes two tools powered by [pix2tex](https://github.com/lukas-blecher/LaTeX-OCR) to extract formulas as LaTeX directly into your notes.

### How it works
```
Formula detected in PDF (image or encoded text)
        ↓
pix2tex OCR → converts to LaTeX
        ↓
Claude inserts in note :
$$\hat{\beta} = (X'X)^{-1}X'y$$
```

### Usage in Claude Desktop

**Extract a specific formula** (with manual coordinates):
```
Extract the formula at the bottom of page 8 of [article]
```

**Extract all formulas on a page automatically**:
```
Extract all formulas from page 5 of [article]
```

Claude will highlight the detected zones in purple in the PDF and return the LaTeX ready to paste into your note.

### Notes on accuracy

- pix2tex may write the same formula in a different but mathematically equivalent form — this is normal
- For best results, use `extract_formula` with manual coordinates on complex or multi-line equations
- Scanned PDFs without a text layer may require higher DPI — the script uses 216 DPI by default

---

## Part 5 — Daily Workflow

### Checklist Before Starting

Before opening Claude Desktop, always have:
- ✅ External drive plugged in and mounted as `P:`
- ✅ Obsidian open with the vault
- ✅ Zotero open in the background
- ✅ Anki open in the background

### Creating a Literature Note

In Claude Desktop:

```
Create a literature note for the article by [Author] [Year] on [topic].
```

Claude will automatically:
1. Search Zotero for the article metadata
2. Find the PDF in `all_pdf`
3. Identify key citations (Category A) and contextual passages (Category B)
4. Highlight everything in the PDF with color-coded annotations
5. Create the note in `90 - Claude/Literature Notes/` with clickable PDF++ links
6. Generate 4–8 flashcards in the `## Flashcards` section
7. Propose permanent notes and links to existing vault notes

### Syncing Flashcards to Anki

After validating a note:
1. Make sure Anki is open
2. `Ctrl+P` → *Flashcards: Sync to Anki*
3. Cards appear in Anki under `Research::Urban Geography`

### Validating and Moving a Note

When satisfied with a Claude-generated note in `90 - Claude/`:
1. Open the note in Obsidian
2. Read and correct if needed
3. Move it to the appropriate folder (`10 - Literature Notes/`, etc.)
4. Change `statut: "à valider"` to `statut: "validée"`

---

## Part 6 — PDF Color System

### Citations (→ inserted in the Obsidian note)

| Color | Purpose |
|-------|---------|
| 🟡 yellow | General citation, main argument |
| 🟢 green | Result / empirical data / statistic |
| 🔵 blue | Definition / key concept |
| 🔴 red | Critical point / limitation / debate |
| 🟣 purple | Method / methodological approach |
| 🟠 orange | Hypothesis / research question |

### Contextual Passages (→ highlighted in PDF only)

| Color | Purpose | Priority |
|-------|---------|----------|
| 🩷 pink | Direct link to my research | 1 |
| 🩵 cyan | Conclusion / general implication | 2 |
| 🍋 lime | Key methodological passage | 3 |
| 🩶 gray | Keyword / technical term | 4 |

---

## Troubleshooting

### "MCP Server disconnected"

1. Make sure Obsidian AND Zotero are open
2. Make sure the external drive is mounted as `P:`
3. Check paths in `claude_desktop_config.json` (double backslashes `\\`)
4. Check logs: `%APPDATA%\Claude\logs\`

### PDF not found by the highlighter

- Check that ZotMoov copied the PDF to `all_pdf`
- Filename must follow: `Author(s) - Year - Title.pdf`
- Re-run ZotMoov on your entire library: Ctrl+A → right-click → ZotMoov → Move/Copy Files
- Use **Everything** to search your entire drive by filename instantly

### Text not highlighted in PDF

- The PDF may be a scanned image without a text layer — OCR required
- Try with a shorter excerpt (6–8 words)
- Close the PDF in Obsidian before running the highlighter

### Flashcards not appearing in Anki

- Make sure Anki is open with AnkiConnect installed
- Check that the `#basic` tag is on the line right after `## Flashcards`
- Try `Ctrl+P` → *Flashcards: Sync to Anki* again

### Python "No module named encodings" error

Multiple Python versions conflict. Use the full path to Python 3.11:
```powershell
C:\Users\YOUR_NAME\AppData\Local\Programs\Python\Python311\python.exe -m pip install ...
```

---

## Setting Up on a Second PC

1. Install all prerequisites (Obsidian, Zotero, Anki, Node.js, Python, Claude Desktop)
2. **Set the same drive letter** for the external drive:
   - Disk Management → right-click external drive → Change Drive Letter → `P:`
3. Copy `claude_desktop_config.json` adapting `YOUR_NAME`
4. Reinstall Python and Node.js dependencies
5. The vault and PDFs are already on the drive — nothing to migrate

---

## Files in This Repository

| File | Description |
|------|-------------|
| `server.py` | MCP PDF highlighting server |
| `claude_system_prompt_v6.md` | System prompt for Claude Desktop |
| `setup.ps1` | PowerShell launcher — run this to start setup |
| `setup.py`  | Interactive Python setup script (called by setup.ps1) |
| `README.md` | This file (English) |
| `LISEZMOI.md` | French version |
