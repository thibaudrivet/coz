# setup.ps1 — Lanceur du workflow Obsidian + Zotero + Claude + Anki
# Exécute avec : powershell -ExecutionPolicy Bypass -File setup.ps1

$ErrorActionPreference = "Stop"

# ── Couleurs console ────────────────────────────────────────────────────────────
function Write-Header {
    param([string]$text)
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  $text" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
}

function Write-Ok   { param([string]$t); Write-Host "  ✅ $t" -ForegroundColor Green }
function Write-Warn { param([string]$t); Write-Host "  ⚠️  $t" -ForegroundColor Yellow }
function Write-Err  { param([string]$t); Write-Host "  ❌ $t" -ForegroundColor Red }
function Write-Info { param([string]$t); Write-Host "  ℹ️  $t" -ForegroundColor White }

# ── Bannière ───────────────────────────────────────────────────────────────────
Clear-Host
Write-Host ""
Write-Host "  🧠 WORKFLOW SETUP — Obsidian + Zotero + Claude + Anki" -ForegroundColor Cyan
Write-Host "  ────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "  Ce script va configurer ton environnement de recherche." -ForegroundColor White
Write-Host ""

# ── Étape 1 : Vérifier Python 3.11 ────────────────────────────────────────────
Write-Header "ÉTAPE 1 — Détection de Python 3.11"

$python311 = $null
$candidates = @(
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\python.exe",
    "C:\Python311\python.exe",
    "C:\Program Files\Python311\python.exe"
)

foreach ($candidate in $candidates) {
    if (Test-Path $candidate) {
        $python311 = $candidate
        Write-Ok "Python 3.11 trouvé : $candidate"
        break
    }
}

if (-not $python311) {
    # Essai via py launcher
    try {
        $ver = & py -3.11 --version 2>&1
        if ($ver -match "3\.11") {
            $python311 = "py -3.11"
            Write-Ok "Python 3.11 disponible via py launcher"
        }
    } catch {}
}

if (-not $python311) {
    Write-Err "Python 3.11 introuvable."
    Write-Info "Télécharge-le sur : https://www.python.org/downloads/release/python-3119/"
    Write-Info "Assure-toi de cocher 'Add Python to PATH' lors de l'installation."
    Read-Host "Appuie sur Entrée pour quitter"
    exit 1
}

# ── Étape 2 : Vérifier Node.js ─────────────────────────────────────────────────
Write-Header "ÉTAPE 2 — Détection de Node.js"

try {
    $nodeVer = & node --version 2>&1
    Write-Ok "Node.js détecté : $nodeVer"
} catch {
    Write-Err "Node.js introuvable."
    Write-Info "Télécharge-le sur : https://nodejs.org (version LTS)"
    Read-Host "Appuie sur Entrée pour quitter"
    exit 1
}

try {
    $npmVer = & npm --version 2>&1
    Write-Ok "npm détecté : v$npmVer"
} catch {
    Write-Err "npm introuvable (normalement inclus avec Node.js)."
    exit 1
}

# ── Étape 3 : Vérifier Claude Desktop ─────────────────────────────────────────
Write-Header "ÉTAPE 3 — Détection de Claude Desktop"

$claudeConfig = "$env:APPDATA\Claude\claude_desktop_config.json"
$claudeDir    = "$env:APPDATA\Claude"

if (Test-Path $claudeDir) {
    Write-Ok "Claude Desktop détecté ($claudeDir)"
} else {
    Write-Warn "Claude Desktop non trouvé dans AppData."
    Write-Info "Télécharge-le sur : https://claude.ai/download"
    Write-Info "Le script continuera mais tu devras relancer après installation."
    $null = New-Item -ItemType Directory -Path $claudeDir -Force
}

# ── Étape 4 : Lancer le script Python de configuration ────────────────────────
Write-Header "ÉTAPE 4 — Lancement de la configuration interactive"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pySetup   = Join-Path $scriptDir "setup.py"

if (-not (Test-Path $pySetup)) {
    Write-Err "Fichier setup.py introuvable dans le même dossier que setup.ps1"
    Write-Info "Assure-toi que setup.ps1 et setup.py sont dans le même dossier."
    Read-Host "Appuie sur Entrée pour quitter"
    exit 1
}

Write-Info "Lancement de setup.py avec Python 3.11..."
Write-Host ""

try {
    if ($python311 -eq "py -3.11") {
        & py -3.11 $pySetup $python311
    } else {
        & $python311 $pySetup $python311
    }
    $exitCode = $LASTEXITCODE
} catch {
    Write-Err "Erreur lors de l'exécution de setup.py : $_"
    Read-Host "Appuie sur Entrée pour quitter"
    exit 1
}

if ($exitCode -eq 0) {
    Write-Host ""
    Write-Header "SETUP TERMINÉ AVEC SUCCÈS 🎉"
    Write-Ok "Ton environnement de recherche est configuré."
    Write-Host ""
    Write-Info "Prochaines étapes :"
    Write-Host "    1. Ouvre Obsidian et vérifie la structure du vault" -ForegroundColor White
    Write-Host "    2. Ouvre Zotero et active l'API locale (Édition → Paramètres → Avancé)" -ForegroundColor White
    Write-Host "    3. Redémarre Claude Desktop complètement" -ForegroundColor White
    Write-Host "    4. Teste avec : 'Liste les fichiers de mon vault Obsidian'" -ForegroundColor White
    Write-Host ""
} else {
    Write-Err "Le setup s'est terminé avec des erreurs (code $exitCode)."
    Write-Info "Consulte les messages ci-dessus pour plus de détails."
}

Read-Host "Appuie sur Entrée pour fermer"
