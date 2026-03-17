# 🧠 Workflow de recherche : Obsidian + Zotero + Claude + PDF++

Un workflow complet pour la recherche académique en géographie urbaine et économie urbaine, combinant gestion bibliographique, prise de notes et intelligence artificielle.

---

## Vue d'ensemble

```
Article/PDF trouvé
      ↓
[Zotero] → capture métadonnées + PDF
      ↓
[ZotMoov] → copie le PDF dans le vault Obsidian
      ↓
[Claude Desktop] → lit Zotero + vault, crée la note
      ↓
[MCP Highlighter] → surligne le PDF avec couleurs codées
      ↓
[Obsidian + PDF++] → note cliquable, PDF annoté
```

---

## Prérequis

| Outil | Version | Lien |
|-------|---------|------|
| Windows 10/11 | — | — |
| Obsidian | 1.x | [obsidian.md](https://obsidian.md) |
| Zotero | 7.x | [zotero.org](https://www.zotero.org) |
| Node.js | LTS (v20+) | [nodejs.org](https://nodejs.org) |
| Python | 3.11 | [python.org](https://www.python.org) |
| Claude Desktop | dernière version | [claude.ai/download](https://claude.ai/download) |
| Everything (optionnel) | dernière version | [everything](https://www.voidtools.com/downloads/) |

> ⚠️ Si tu as plusieurs versions de Python, utilise **Python 3.11** pour toutes les commandes `pip` de ce guide.

---

## Partie 1 — Obsidian

### 1.1 Structure du vault

Crée la structure suivante (ou adapte la tienne) :

```
Vault/
├── 00 - MOC/
├── 10 - Notes de lecture/
├── 20 - Notes permanentes/
├── 30 - Projets/
├── 40 - Ressources/
│   └── pdf_highlight_mcp/
│       └── server.py          ← script de surlignage
├── 90 - Claude/               ← toutes les créations de Claude
│   ├── Notes de lecture/
│   ├── Notes permanentes/
│   └── Synthèses/
└── Bibliographie/
    └── Zotero/
        └── all_pdf/           ← tous les PDFs
```

### 1.2 Plugins à installer

Dans Obsidian → Paramètres → Plugins tiers → Parcourir :

| Plugin | Utilité |
|--------|---------|
| **PDF++** | Viewer PDF avancé + annotations cliquables |
| **Local REST API** | Pont entre Obsidian et les outils externes |
| **Dataview** | Requêtes dynamiques sur tes notes |

### 1.3 Configurer Local REST API

1. Active le plugin Local REST API
2. Va dans ses paramètres → copie la **clé API** générée
3. Note le port (défaut : **27124**)

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

Pour copier tous tes PDFs existants dans `all_pdf` :
1. Sélectionne toute ta bibliothèque (`Ctrl+A`)
2. Clic droit → **ZotMoov → Move/Copy Files**

---

## Partie 3 — Claude Desktop

### 3.1 Installation

Télécharge et installe [Claude Desktop](https://claude.ai/download).

> ℹ️ Claude Desktop nécessite un compte Anthropic avec crédits API ou abonnement.

### 3.2 Installer Node.js et le serveur MCP Obsidian

```powershell
# Vérifier Node.js
node --version

# Installer le serveur MCP filesystem (Anthropic officiel)
npm install -g @modelcontextprotocol/server-filesystem

# Vérifier
where mcp-server-filesystem
```

### 3.3 Installer les dépendances Python

```powershell
C:\Users\TON_NOM\AppData\Local\Programs\Python\Python311\python.exe -m pip install pymupdf mcp zotero-mcp
```

### 3.4 Copier le script de surlignage

Copie le fichier `server.py` (fourni dans ce dossier) dans :
```
P:\Obsidian Vaults\Recherche\40 - Ressources\pdf_highlight_mcp\server.py
```

### 3.5 Configurer claude_desktop_config.json

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

### 3.6 Configurer le prompt système

Dans Claude Desktop → clique sur ton avatar → **Profile** → colle le contenu du fichier `claude_system_prompt_v5.md` dans le champ "What would you like Claude to know about you?".

### 3.7 Vérifier la connexion

Redémarre Claude Desktop **complètement** (clic droit icône barre des tâches → Quitter).

Au démarrage, vérifie qu'il n'y a **aucun message d'erreur MCP**. Teste avec :

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

## Partie 4 — Utilisation quotidienne

### Checklist avant de démarrer

Avant d'ouvrir Claude Desktop, toujours avoir :
- ✅ DD externe branché et monté sur `P:`
- ✅ Obsidian ouvert avec le vault
- ✅ Zotero ouvert en arrière-plan

### Créer une note de lecture

Dans Claude Desktop :

```
Crée une note de lecture pour l'article de [Auteur] [Année] sur [sujet].
```

Claude va automatiquement :
1. Chercher l'article dans Zotero
2. Trouver le PDF dans `all_pdf`
3. Identifier les citations importantes ET les passages contextuels
4. Surligner tout dans le PDF avec les couleurs appropriées
5. Créer la note dans `90 - Claude/Notes de lecture/` avec les liens cliquables
6. Proposer des notes permanentes et des liens avec les notes existantes

### Valider et déplacer une note

Quand tu es satisfait d'une note créée par Claude dans `90 - Claude/` :
1. Ouvre la note dans Obsidian
2. Relis et corrige si besoin
3. Déplace-la dans le dossier approprié (`10 - Notes de lecture/`, etc.)
4. Change le champ `statut: "à valider"` en `statut: "validée"`

---

## Partie 5 — Système de couleurs PDF

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
- Le nom du fichier doit être au format `Auteur(s) - Année - Titre.pdf`
- Relance ZotMoov sur toute ta bibliothèque (Ctrl+A → clic droit → ZotMoov → Move/Copy Files)

### Le texte n'est pas surligné dans le PDF

- Le PDF est peut-être un scan (image) sans couche texte — l'OCR est nécessaire
- Essaie avec une citation plus courte (6-8 mots)
- Ferme le PDF dans Obsidian avant de lancer le surlignage

### Erreur Python "No module named encodings"

Tu as plusieurs versions de Python. Utilise le chemin complet vers Python 3.11 :
```powershell
C:\Users\TON_NOM\AppData\Local\Programs\Python\Python311\python.exe -m pip install ...
```

---

## Sur un deuxième PC

1. Installe tous les prérequis (Obsidian, Zotero, Node.js, Python, Claude Desktop)
2. **Fixe la même lettre de lecteur** pour le DD externe :
   - Gestion des disques → clic droit DD externe → Modifier la lettre → `P:`
3. Copie le `claude_desktop_config.json` en adaptant `TON_NOM`
4. Réinstalle les dépendances Python et Node.js
5. Le vault et les PDFs sont déjà sur le DD — rien à migrer

---

## Fichiers fournis

| Fichier | Description |
|---------|-------------|
| `server.py` | Serveur MCP de surlignage PDF |
| `claude_system_prompt_v5.md` | Prompt système pour Claude Desktop |
| `README.md` | Ce fichier |
