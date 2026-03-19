# 🧠 Workflow de recherche académique : Obsidian + Zotero + Claude + PDF++ + Anki

Un workflow complet pour la recherche académique combinant gestion bibliographique, prise de notes, assistance IA et répétition espacée.

> Initialement conçu pour la géographie urbaine et l'économie urbaine, mais adaptable à tout domaine académique.

---

## Vue d'ensemble

```
Article / PDF trouvé
        ↓
[Zotero] → capture les métadonnées + PDF via le connecteur navigateur
        ↓
[ZotMoov] → copie le PDF dans le vault Obsidian avec un nom stable
        ↓
[Claude Desktop] → lit Zotero + vault, crée une note structurée
        ↓
[MCP Highlighter] → surligne le PDF avec des annotations colorées
        ↓
[pix2tex OCR] → extrait les formules mathématiques en LaTeX
        ↓
[Obsidian + PDF++] → note cliquable, PDF annoté, équations rendues
        ↓
[Anki] → flashcards de répétition espacée synchronisées depuis la note
```

---

## Prérequis

| Outil | Version | Lien |
|-------|---------|------|
| Windows 10/11 | — | — |
| Obsidian | 1.x | [obsidian.md](https://obsidian.md) |
| Zotero | 7.x | [zotero.org](https://www.zotero.org) |
| Anki | dernière version | [apps.ankiweb.net](https://apps.ankiweb.net) |
| Node.js | LTS (v20+) | [nodejs.org](https://nodejs.org) |
| Python | 3.11 | [python.org](https://www.python.org) |
| Claude Desktop | dernière version | [claude.ai/download](https://claude.ai/download) |
| Everything *(optionnel)* | dernière version | [voidtools.com](https://www.voidtools.com) |

> ⚠️ Si tu as plusieurs versions de Python installées, utilise toujours **Python 3.11** pour chaque commande `pip` de ce guide.

> 💡 **Everything** est un outil de recherche de fichiers optionnel mais très recommandé sous Windows. Il indexe l'intégralité de ton disque instantanément — très utile pour localiser des PDFs par nom de fichier et diagnostiquer des problèmes avec le dossier `all_pdf`.

---

## Installation rapide (recommandé)

Au lieu de tout configurer manuellement, lance le script de setup automatique :

1. Clone ou télécharge ce dépôt
2. Clic droit sur `setup.ps1` → **Exécuter avec PowerShell**
3. Suis les instructions interactives

Le script va automatiquement :
- Détecter Node.js et Python 3.11
- Créer la structure de dossiers du vault
- Installer toutes les dépendances Python et npm
- Télécharger et installer les plugins Obsidian depuis GitHub
- Copier `server.py` dans ton vault
- Générer `claude_desktop_config.json` avec les bons chemins

> ⚠️ Si PowerShell bloque l'exécution, lance d'abord ceci dans un terminal admin :
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

### Ce qui nécessite encore une action manuelle

| Étape | Où |
|-------|----|
| Activer l'API locale Zotero | Zotero → Édition → Paramètres → Avancé |
| Installer et configurer ZotMoov | Zotero → Outils → Extensions |
| Installer AnkiConnect | Anki → Outils → Extensions → code `2055492159` |
| Coller le prompt système | Claude Desktop → Profile |
| Redémarrer Claude Desktop | Icône barre des tâches → clic droit → Quitter |

---

## Partie 1 — Obsidian

### 1.1 Structure du vault

Crée la structure suivante (ou adapte la tienne) :

```
Vault/
├── 00 - MOC/                    # Maps of Content — index thématiques
├── 10 - Notes de lecture/       # Une note par article/livre (validées)
├── 20 - Notes permanentes/      # Idées atomiques, concepts clés (validées)
├── 30 - Projets/                # Notes de projets de recherche
├── 40 - Ressources/             # Méthodes, outils, scripts
│   └── pdf_highlight_mcp/
│       └── server.py            ← script de surlignage PDF
├── 90 - Claude/                 ← toutes les créations de Claude ici
│   ├── Notes de lecture/
│   ├── Notes permanentes/
│   └── Synthèses/
└── Bibliographie/
    └── Zotero/
        └── all_pdf/             ← tous les PDFs avec noms stables
```

### 1.2 Plugins à installer

Dans Obsidian → Paramètres → Plugins tiers → Parcourir :

| Plugin | Utilité |
|--------|---------|
| **PDF++** | Viewer PDF avancé + annotations cliquables |
| **Local REST API** | Pont entre Obsidian et les outils externes |
| **Dataview** | Requêtes dynamiques sur tes notes |
| **Flashcards** (par Reupload) | Synchronise les flashcards vers Anki |

### 1.3 Configurer Local REST API

1. Active le plugin Local REST API
2. Va dans ses paramètres → copie la **clé API** générée
3. Note le port (défaut : **27124**)

### 1.4 Configurer le plugin Flashcards

Dans les paramètres du plugin Flashcards :

| Paramètre | Valeur |
|-----------|--------|
| Default deck name | `Recherche::Géographie urbaine` |
| Flashcards #tag | `basic` |
| Inline card separator | `::` |
| Source support | ✅ activé |
| Inline ID support | ✅ activé |
| Code highlight support | ✅ activé (si tu utilises du code Python/SIG) |
| Folder-based deck name | ✅ activé |

---

## Partie 2 — Zotero

### 2.1 Plugins Zotero à installer

| Plugin | Lien | Utilité |
|--------|------|---------|
| **Better BibTeX** | [retorque.re/zotero-better-bibtex](https://retorque.re/zotero-better-bibtex/installation/) | Clés de citation stables |
| **ZotMoov** | [github.com/wileyyugioh/zotmoov](https://github.com/wileyyugioh/zotmoov/releases) | Copie les PDFs dans le vault |

Installation : Zotero → Outils → Extensions → icône engrenage → *Install Add-on From File* → sélectionne le `.xpi`

### 2.2 Configurer ZotMoov

Zotero → Édition → Paramètres → **ZotMoov** :

| Paramètre | Valeur |
|-----------|--------|
| Directory to Move/Copy Files To | `P:\Obsidian Vaults\Recherche\Bibliographie\Zotero\all_pdf` |
| File Behavior | **Copy** |
| Automatically Move/Copy When Added | ✅ coché |
| Automatically Move/Copy to Subdirectory | ☐ décoché |

### 2.3 Activer l'API locale Zotero

Zotero → Édition → Paramètres → **Avancé** :
- Coche **"Autoriser d'autres applications sur cet ordinateur à communiquer avec Zotero"**

### 2.4 Migrer les PDFs existants

Pour copier tous tes PDFs existants dans `all_pdf` en une fois :
1. Sélectionne toute ta bibliothèque (`Ctrl+A`)
2. Clic droit → **ZotMoov → Move/Copy Files**

---

## Partie 3 — Anki

### 3.1 Installer AnkiConnect

Dans Anki → Outils → Extensions → Obtenir des extensions → code : **`2055492159`**

Redémarre Anki. Il doit rester **ouvert en arrière-plan** pour que la sync fonctionne.

### 3.2 Comment fonctionne la synchronisation

Claude génère automatiquement une section `## Flashcards` à la fin de chaque note de lecture :

```markdown
## Flashcards
#basic

Qu'est-ce que la densification urbaine ?::Augmentation de la densité de population ou de bâti dans une zone urbaine existante, distincte de l'étalement périurbain.

Quel indicateur utilisent Broitman et Koomen pour mesurer la densification ?::Variation de densité de population à l'échelle des cellules de grille (500m × 500m) sur 1990-2010.

Comment lire un shapefile avec GeoPandas ?::
    import geopandas as gpd
    gdf = gpd.read_file("fichier.shp")
```

Pour synchroniser vers Anki : dans Obsidian, `Ctrl+P` → *Flashcards: Sync to Anki*

---

## Partie 4 — Claude Desktop

### 4.1 Installation

Télécharge et installe [Claude Desktop](https://claude.ai/download).

> ℹ️ Claude Desktop nécessite un compte Anthropic avec crédits API ou un abonnement.

### 4.2 Installer Node.js et le serveur MCP Obsidian

```powershell
# Vérifier Node.js
node --version

# Installer le serveur MCP filesystem officiel Anthropic
npm install -g @modelcontextprotocol/server-filesystem

# Vérifier
where mcp-server-filesystem
```

### 4.3 Installer les dépendances Python

```powershell
C:\Users\TON_NOM\AppData\Local\Programs\Python\Python311\python.exe -m pip install pymupdf mcp zotero-mcp
```

### 4.4 Copier le script de surlignage

Copie `server.py` (fourni dans ce dépôt) dans :
```
P:\Obsidian Vaults\Recherche\40 - Ressources\pdf_highlight_mcp\server.py
```

### 4.5 Configurer claude_desktop_config.json

Ouvre `%APPDATA%\Claude\claude_desktop_config.json` et remplace le contenu par :

```json
{
  "preferences": {
    "coworkWebSearchEnabled": true,
    "coworkScheduledTasksEnabled": false,
    "ccdScheduledTasksEnabled": false
  },
  "mcpServers": {
    "obsidian-vault": {
      "command": "C:\\Users\\TON_NOM\\AppData\\Roaming\\npm\\mcp-server-filesystem.cmd",
      "args": ["P:\\Obsidian Vaults\\Recherche"]
    },
    "zotero": {
      "command": "C:\\Users\\TON_NOM\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\zotero-mcp.exe",
      "env": {
        "ZOTERO_LOCAL": "true",
        "ZOTERO_LIBRARY_TYPE": "user"
      }
    },
    "pdf-highlighter": {
      "command": "C:\\Users\\TON_NOM\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
      "args": [
        "P:\\Obsidian Vaults\\Recherche\\40 - Ressources\\pdf_highlight_mcp\\server.py"
      ],
      "env": {
        "VAULT_PATH": "P:\\Obsidian Vaults\\Recherche"
      }
    }
  }
}
```

> ⚠️ Remplace `TON_NOM` par ton nom d'utilisateur Windows partout.

### 4.6 Configurer le prompt système

Dans Claude Desktop → clique sur ton avatar → **Profile** → colle le contenu de `claude_system_prompt_v6.md` dans le champ "What would you like Claude to know about you?".

### 4.7 Vérifier la connexion

Redémarre complètement Claude Desktop (clic droit icône barre des tâches → Quitter).

Vérifie qu'il n'y a **aucun message d'erreur MCP**. Teste avec :

```
Liste les fichiers à la racine de mon vault Obsidian
```
```
Liste les collections de ma bibliothèque Zotero
```
```
Liste les couleurs de surlignage disponibles
```

---

## Partie 4b — Extraction de formules mathématiques (pix2tex)

Les articles en économie et économie urbaine contiennent souvent des notations mathématiques denses. Le serveur MCP inclut deux outils basés sur [pix2tex](https://github.com/lukas-blecher/LaTeX-OCR) pour extraire les formules en LaTeX directement dans tes notes.

### Comment ça marche
```
Formule détectée dans le PDF (image ou texte encodé)
        ↓
pix2tex OCR → convertit en LaTeX
        ↓
Claude insère dans la note :
$$\hat{\beta} = (X'X)^{-1}X'y$$
```

### Utilisation dans Claude Desktop

**Extraire une formule précise** (avec coordonnées manuelles) :
```
Extrais la formule en bas de la page 8 de [article]
```

**Extraire toutes les formules d'une page automatiquement** :
```
Extrais toutes les formules de la page 5 de [article]
```

Claude surligne les zones détectées en violet dans le PDF et retourne le LaTeX prêt à insérer dans ta note.

### Notes sur la précision

- pix2tex peut écrire la même formule d'une façon différente mais mathématiquement équivalente — c'est normal
- Pour les équations complexes ou multi-lignes, préfère `extract_formula` avec des coordonnées manuelles
- Les PDFs scannés sans couche texte peuvent nécessiter un DPI plus élevé — le script utilise 216 DPI par défaut

---

## Partie 5 — Utilisation quotidienne

### Checklist avant de démarrer

Avant d'ouvrir Claude Desktop, toujours avoir :
- ✅ DD externe branché et monté sur `P:`
- ✅ Obsidian ouvert avec le vault
- ✅ Zotero ouvert en arrière-plan
- ✅ Anki ouvert en arrière-plan

### Créer une note de lecture

Dans Claude Desktop :

```
Crée une note de lecture pour l'article de [Auteur] [Année] sur [sujet].
```

Claude va automatiquement :
1. Chercher l'article dans Zotero pour récupérer les métadonnées
2. Trouver le PDF dans `all_pdf`
3. Identifier les citations importantes (Catégorie A) et les passages contextuels (Catégorie B)
4. Surligner tout dans le PDF avec les couleurs appropriées
5. Créer la note dans `90 - Claude/Notes de lecture/` avec les liens PDF++ cliquables
6. Générer 4 à 8 flashcards dans la section `## Flashcards`
7. Proposer des notes permanentes et des liens avec les notes existantes

### Synchroniser les flashcards vers Anki

Après avoir validé une note :
1. Assure-toi qu'Anki est ouvert
2. `Ctrl+P` → *Flashcards: Sync to Anki*
3. Les cartes apparaissent dans Anki sous `Recherche::Géographie urbaine`

### Valider et déplacer une note

Quand tu es satisfait d'une note créée par Claude dans `90 - Claude/` :
1. Ouvre la note dans Obsidian
2. Relis et corrige si besoin
3. Déplace-la dans le bon dossier (`10 - Notes de lecture/`, etc.)
4. Change `statut: "à valider"` en `statut: "validée"`

---

## Partie 6 — Système de couleurs PDF

### Citations (→ insérées dans la note Obsidian)

| Couleur | Usage |
|---------|-------|
| 🟡 yellow | Citation générale, argument principal |
| 🟢 green | Résultat / donnée empirique / statistique |
| 🔵 blue | Définition / concept clé |
| 🔴 red | Point critique / limite / à débattre |
| 🟣 purple | Méthode / approche méthodologique |
| 🟠 orange | Hypothèse / question de recherche |

### Passages contextuels (→ surlignés dans le PDF uniquement)

| Couleur | Usage | Priorité |
|---------|-------|----------|
| 🩷 pink | Lien direct avec ma recherche | 1 |
| 🩵 cyan | Conclusion / implication générale | 2 |
| 🍋 lime | Passage méthodologique clé | 3 |
| 🩶 gray | Mot-clé / terme technique | 4 |

---

## Dépannage

### "MCP Server disconnected"

1. Vérifie que Obsidian ET Zotero sont ouverts
2. Vérifie que le DD externe est bien monté sur `P:`
3. Vérifie les chemins dans `claude_desktop_config.json` (doubles backslashes `\\`)
4. Consulte les logs : `%APPDATA%\Claude\logs\`

### Le PDF n'est pas trouvé par le surligneur

- Vérifie que ZotMoov a bien copié le PDF dans `all_pdf`
- Le nom du fichier doit suivre le format : `Auteur(s) - Année - Titre.pdf`
- Relance ZotMoov sur toute ta bibliothèque : Ctrl+A → clic droit → ZotMoov → Move/Copy Files
- Utilise **Everything** pour rechercher instantanément le fichier sur tout ton disque

### Le texte n'est pas surligné dans le PDF

- Le PDF est peut-être un scan (image) sans couche texte — l'OCR est nécessaire
- Essaie avec une citation plus courte (6-8 mots)
- Ferme le PDF dans Obsidian avant de lancer le surlignage

### Les flashcards n'apparaissent pas dans Anki

- Assure-toi qu'Anki est ouvert avec AnkiConnect installé
- Vérifie que le tag `#basic` est bien sur la ligne juste après `## Flashcards`
- Réessaie `Ctrl+P` → *Flashcards: Sync to Anki*

### Erreur Python "No module named encodings"

Tu as plusieurs versions de Python en conflit. Utilise le chemin complet vers Python 3.11 :
```powershell
C:\Users\TON_NOM\AppData\Local\Programs\Python\Python311\python.exe -m pip install ...
```

---

## Sur un deuxième PC

1. Installe tous les prérequis (Obsidian, Zotero, Anki, Node.js, Python, Claude Desktop)
2. **Fixe la même lettre de lecteur** pour le DD externe :
   - Gestion des disques → clic droit DD externe → Modifier la lettre → `P:`
3. Copie le `claude_desktop_config.json` en adaptant `TON_NOM`
4. Réinstalle les dépendances Python et Node.js
5. Le vault et les PDFs sont déjà sur le DD — rien à migrer

---

## Fichiers dans ce dépôt

| Fichier | Description |
|---------|-------------|
| `server.py` | Serveur MCP de surlignage PDF |
| `claude_system_prompt_fr.md` | Prompt système pour Claude Desktop en français |
| `claude_system_prompt_en.md` | Prompt système pour Claude Desktop en anglais |
| `setup.ps1` | Lanceur PowerShell — exécute ce fichier pour démarrer |
| `setup.py`  | Script Python de configuration interactive (appelé par setup.ps1) |
| `README.md` | Ce fichier (anglais) |
| `LISEZMOI.md` | Ce fichier (français) |
