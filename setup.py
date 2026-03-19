#!/usr/bin/env python3
"""
setup.py — Configuration interactive du workflow de recherche
Obsidian + Zotero + Claude Desktop + Anki + PDF Highlighter

Usage : appelé automatiquement par setup.ps1
"""

import sys
import os
import json
import shutil
import subprocess
import urllib.request
import zipfile
import tempfile
from pathlib import Path


# ── Helpers console ────────────────────────────────────────────────────────────

def c(text, color):
    colors = {
        "cyan":   "\033[96m", "green":  "\033[92m",
        "yellow": "\033[93m", "red":    "\033[91m",
        "white":  "\033[97m", "gray":   "\033[90m",
        "reset":  "\033[0m",
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"

def header(text):
    print()
    print(c("─" * 55, "cyan"))
    print(c(f"  {text}", "cyan"))
    print(c("─" * 55, "cyan"))

def ok(text):   print(c(f"  ✅ {text}", "green"))
def warn(text): print(c(f"  ⚠️  {text}", "yellow"))
def err(text):  print(c(f"  ❌ {text}", "red"))
def info(text): print(c(f"  ℹ️  {text}", "white"))
def step(text): print(c(f"\n  → {text}...", "gray"))

def ask(prompt, default=None):
    if default:
        result = input(c(f"\n  {prompt} [{default}] : ", "cyan")).strip()
        return result if result else default
    return input(c(f"\n  {prompt} : ", "cyan")).strip()

def confirm(prompt, default=True):
    suffix = "[O/n]" if default else "[o/N]"
    result = input(c(f"\n  {prompt} {suffix} : ", "cyan")).strip().lower()
    if not result:
        return default
    return result in ("o", "oui", "y", "yes")


# ── Détection de l'environnement ───────────────────────────────────────────────

def find_python311():
    """Retourne le chemin vers Python 3.11."""
    python_exe = sys.executable
    ver = sys.version_info
    if ver.major == 3 and ver.minor == 11:
        return python_exe
    # Cherche dans les chemins standards
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python311" / "python.exe",
        Path("C:/Python311/python.exe"),
        Path("C:/Program Files/Python311/python.exe"),
    ]
    for c_path in candidates:
        if c_path.exists():
            return str(c_path)
    return python_exe  # fallback


def find_npm():
    """Retourne le chemin vers npm."""
    npm = shutil.which("npm")
    if npm:
        return npm
    # Cherche dans nodejs
    nodejs_npm = Path("C:/Program Files/nodejs/npm.cmd")
    if nodejs_npm.exists():
        return str(nodejs_npm)
    return None


def pip_install(python_exe, *packages):
    """Installe des packages pip."""
    cmd = [python_exe, "-m", "pip", "install", "--quiet", *packages]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr


def npm_install_global(npm_exe, package):
    """Installe un package npm globalement."""
    result = subprocess.run(
        [npm_exe, "install", "-g", package],
        capture_output=True, text=True
    )
    return result.returncode == 0, result.stderr


# ── Structure du vault ─────────────────────────────────────────────────────────

VAULT_FOLDERS = [
    "00 - MOC",
    "10 - Notes de lecture",
    "20 - Notes permanentes",
    "30 - Projets",
    "40 - Ressources/pdf_highlight_mcp",
    "90 - Claude/Notes de lecture",
    "90 - Claude/Notes permanentes",
    "90 - Claude/Synthèses",
    "Bibliographie/Zotero/all_pdf",
    "_templates",
]

MOC_FILES = {
    "00 - MOC/MOC Villes et systèmes de villes.md": "# MOC — Villes et systèmes de villes\n\n## Articles clés\n\n## Concepts\n\n## Projets liés\n",
    "00 - MOC/MOC Economie urbaine.md": "# MOC — Économie urbaine\n\n## Articles clés\n\n## Concepts\n\n## Projets liés\n",
    "00 - MOC/MOC Méthodes quantitatives.md": "# MOC — Méthodes quantitatives\n\n## Articles clés\n\n## Concepts\n\n## Scripts\n",
    "90 - Claude/README.md": (
        "# Dossier Claude\n\n"
        "Toutes les notes créées automatiquement par Claude sont ici.\n\n"
        "**À faire :** relire, valider, corriger les flashcards si besoin, "
        "puis déplacer dans les dossiers principaux (10, 20, 30...).\n\n"
        "## Statuts\n"
        "- `statut: \"à valider\"` → en attente de relecture\n"
        "- `statut: \"validée\"` → prête à être déplacée\n"
    ),
}

# ── Plugins Obsidian ───────────────────────────────────────────────────────────

OBSIDIAN_PLUGINS = [
    {
        "id": "obsidian-local-rest-api",
        "name": "Local REST API",
        "repo": "coddingtonbear/obsidian-local-rest-api",
        "required": True,
    },
    {
        "id": "dataview",
        "name": "Dataview",
        "repo": "blacksmithgu/obsidian-dataview",
        "required": True,
    },
    {
        "id": "pdfplus",
        "name": "PDF++",
        "repo": "RyotaUshio/obsidian-pdf-plus",
        "required": True,
    },
    {
        "id": "flashcards-obsidian",
        "name": "Flashcards",
        "repo": "reusanble/flashcards-obsidian",
        "required": True,
    },
]


def get_github_latest_release(repo: str) -> tuple[str, str] | tuple[None, None]:
    """Récupère l'URL du dernier release GitHub d'un plugin Obsidian."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "setup-script"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            tag = data.get("tag_name", "")
            for asset in data.get("assets", []):
                name = asset["name"]
                if name.endswith(".zip") or name == "main.zip":
                    return tag, asset["browser_download_url"]
            # Fallback : construire l'URL depuis les assets standards
            for asset in data.get("assets", []):
                if asset["name"] in ("main.js", "manifest.json"):
                    base = asset["browser_download_url"].rsplit("/", 1)[0]
                    return tag, base
    except Exception:
        pass
    return None, None


def install_obsidian_plugin(vault_path: Path, plugin: dict) -> bool:
    """Télécharge et installe un plugin Obsidian dans le vault."""
    plugin_dir = vault_path / ".obsidian" / "plugins" / plugin["id"]
    plugin_dir.mkdir(parents=True, exist_ok=True)

    # Fichiers à télécharger
    base_url = f"https://github.com/{plugin['repo']}/releases/latest/download"
    files = ["main.js", "manifest.json", "styles.css"]

    success = False
    for filename in files:
        url = f"{base_url}/{filename}"
        dest = plugin_dir / filename
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "setup-script"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                dest.write_bytes(resp.read())
            success = True
        except Exception:
            pass  # styles.css est optionnel

    return success


def enable_obsidian_plugin(vault_path: Path, plugin_id: str):
    """Active un plugin dans community-plugins.json."""
    config_path = vault_path / ".obsidian" / "community-plugins.json"
    if config_path.exists():
        plugins = json.loads(config_path.read_text(encoding="utf-8"))
    else:
        plugins = []

    if plugin_id not in plugins:
        plugins.append(plugin_id)
        config_path.write_text(json.dumps(plugins, indent=2), encoding="utf-8")


# ── Configuration Claude Desktop ───────────────────────────────────────────────

def find_python_scripts_dir(python_exe: str) -> Path:
    """Trouve le dossier Scripts de Python 3.11."""
    return Path(python_exe).parent / "Scripts"


def find_npm_global_dir() -> Path | None:
    """Trouve le dossier global npm."""
    try:
        result = subprocess.run(
            ["npm", "root", "-g"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            # npm root -g retourne .../node_modules, on veut le parent
            return Path(result.stdout.strip()).parent
    except Exception:
        pass
    # Fallback Windows
    appdata = os.environ.get("APPDATA", "")
    return Path(appdata) / "npm" if appdata else None


def generate_claude_config(
    vault_path: Path,
    python_exe: str,
    server_py_path: Path,
) -> dict:
    """Génère le contenu de claude_desktop_config.json."""
    scripts_dir = find_python_scripts_dir(python_exe)
    npm_dir = find_npm_global_dir()

    # Chemin vers mcp-server-filesystem
    if npm_dir:
        mcp_filesystem = str(npm_dir / "mcp-server-filesystem.cmd")
    else:
        mcp_filesystem = "mcp-server-filesystem"

    # Chemin vers zotero-mcp
    zotero_mcp = str(scripts_dir / "zotero-mcp.exe")

    config = {
        "preferences": {
            "coworkWebSearchEnabled": True,
            "coworkScheduledTasksEnabled": False,
            "ccdScheduledTasksEnabled": False,
        },
        "mcpServers": {
            "obsidian-vault": {
                "command": mcp_filesystem,
                "args": [str(vault_path)],
            },
            "zotero": {
                "command": zotero_mcp,
                "env": {
                    "ZOTERO_LOCAL": "true",
                    "ZOTERO_LIBRARY_TYPE": "user",
                },
            },
            "pdf-highlighter": {
                "command": python_exe,
                "args": [str(server_py_path)],
                "env": {
                    "VAULT_PATH": str(vault_path),
                },
            },
        },
    }
    return config


# ── Script principal ───────────────────────────────────────────────────────────

def main():
    print()
    print(c("  🧠 SETUP — Workflow de Recherche Académique", "cyan"))
    print(c("  Obsidian + Zotero + Claude Desktop + Anki", "gray"))
    print()

    python_exe = find_python311()
    npm_exe    = find_npm()

    # ── 1. Chemin du vault ─────────────────────────────────────────────────────
    header("1 / 6 — Chemin du vault Obsidian")

    info("Exemple : P:\\Obsidian Vaults\\Recherche")
    info("         D:\\Mes Documents\\Vault")

    while True:
        vault_input = ask("Chemin complet de ton vault Obsidian")
        vault_path  = Path(vault_input.strip('"').strip("'"))
        if vault_path.exists():
            ok(f"Vault trouvé : {vault_path}")
            break
        elif confirm(f"Le dossier '{vault_path}' n'existe pas. Le créer ?", default=True):
            vault_path.mkdir(parents=True, exist_ok=True)
            ok(f"Dossier créé : {vault_path}")
            break
        else:
            warn("Saisis un chemin valide.")

    # ── 2. Structure du vault ──────────────────────────────────────────────────
    header("2 / 6 — Création de la structure du vault")

    for folder in VAULT_FOLDERS:
        folder_path = vault_path / folder
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
            ok(f"Créé : {folder}")
        else:
            info(f"Existe déjà : {folder}")

    # Création des fichiers MOC et README
    for rel_path, content in MOC_FILES.items():
        file_path = vault_path / rel_path
        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")
            ok(f"Créé : {rel_path}")
        else:
            info(f"Existe déjà : {rel_path}")

    # ── 3. Copie de server.py ──────────────────────────────────────────────────
    header("3 / 6 — Installation du serveur MCP PDF Highlighter")

    script_dir  = Path(__file__).parent
    source_py   = script_dir / "server.py"
    dest_dir    = vault_path / "40 - Ressources" / "pdf_highlight_mcp"
    dest_py     = dest_dir / "server.py"

    if source_py.exists():
        shutil.copy2(source_py, dest_py)
        ok(f"server.py copié dans {dest_py}")
    else:
        warn("server.py introuvable dans le dossier du script.")
        warn("Copie-le manuellement dans : 40 - Ressources/pdf_highlight_mcp/")

    # ── 4. Dépendances Python et npm ───────────────────────────────────────────
    header("4 / 6 — Installation des dépendances")

    # pip
    pip_packages = ["pymupdf", "mcp", "zotero-mcp", "pix2tex", "Pillow"]
    step(f"Installation pip : {', '.join(pip_packages)}")

    for package in pip_packages:
        step(f"pip install {package}")
        success, stderr = pip_install(python_exe, package)
        if success:
            ok(f"{package} installé")
        else:
            warn(f"{package} — problème : {stderr[:100]}")

    # npm
    if npm_exe:
        step("npm install -g @modelcontextprotocol/server-filesystem")
        success, stderr = npm_install_global(npm_exe, "@modelcontextprotocol/server-filesystem")
        if success:
            ok("mcp-server-filesystem installé")
        else:
            warn(f"mcp-server-filesystem — problème : {stderr[:100]}")
    else:
        warn("npm introuvable — installe Node.js puis relance le setup.")

    # ── 5. Plugins Obsidian ────────────────────────────────────────────────────
    header("5 / 6 — Installation des plugins Obsidian")

    obsidian_config_dir = vault_path / ".obsidian"
    obsidian_config_dir.mkdir(exist_ok=True)

    # Active les plugins tiers
    config_path = obsidian_config_dir / "config"
    if not config_path.exists():
        config_path.write_text(
            json.dumps({"enabledCssSnippets": [], "theme": ""}, indent=2),
            encoding="utf-8"
        )

    if confirm("Télécharger et installer les plugins Obsidian depuis GitHub ?", default=True):
        for plugin in OBSIDIAN_PLUGINS:
            step(f"Installation de {plugin['name']}")
            success = install_obsidian_plugin(vault_path, plugin)
            if success:
                enable_obsidian_plugin(vault_path, plugin["id"])
                ok(f"{plugin['name']} installé et activé")
            else:
                warn(f"{plugin['name']} — échec du téléchargement (réseau ?)")
                info(f"Installe-le manuellement depuis Obsidian → Plugins tiers")
    else:
        info("Plugins ignorés — installe-les manuellement depuis Obsidian.")

    # ── 6. Claude Desktop config ───────────────────────────────────────────────
    header("6 / 6 — Génération de claude_desktop_config.json")

    claude_config_path = Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    claude_config_path.parent.mkdir(parents=True, exist_ok=True)

    config = generate_claude_config(
        vault_path  = vault_path,
        python_exe  = python_exe,
        server_py_path = dest_py,
    )

    # Préserve les préférences existantes si le fichier existe déjà
    if claude_config_path.exists():
        try:
            existing = json.loads(claude_config_path.read_text(encoding="utf-8"))
            if "preferences" in existing:
                config["preferences"] = existing["preferences"]
            info("Fichier existant trouvé — préférences préservées.")
        except Exception:
            pass

        if confirm("Écraser le claude_desktop_config.json existant ?", default=True):
            # Backup
            backup = claude_config_path.with_suffix(".json.backup")
            shutil.copy2(claude_config_path, backup)
            ok(f"Backup créé : {backup}")
        else:
            info("Config Claude Desktop inchangée.")
            claude_config_path = None

    if claude_config_path:
        claude_config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        ok(f"Config générée : {claude_config_path}")

    # ── Récapitulatif ──────────────────────────────────────────────────────────
    print()
    print(c("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "green"))
    print(c("  🎉 SETUP TERMINÉ", "green"))
    print(c("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "green"))
    print()
    print(c("  Actions manuelles restantes :", "yellow"))
    print(c("  1. Zotero → Édition → Paramètres → Avancé → activer l'API locale", "white"))
    print(c("  2. Zotero → Installer ZotMoov et le configurer", "white"))
    print(c("  3. Anki → Installer AnkiConnect (code : 2055492159)", "white"))
    print(c("  4. Claude Desktop → Profile → coller claude_system_prompt_v6.md", "white"))
    print(c("  5. Redémarrer Claude Desktop complètement", "white"))
    print()
    print(c("  Fichiers générés :", "gray"))
    print(c(f"  • {dest_py}", "gray"))
    if claude_config_path:
        print(c(f"  • {claude_config_path}", "gray"))
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
