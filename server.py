"""
MCP Server — PDF Highlighter pour Obsidian + PDF++
Version 2 — Palette étendue avec surlignage contextuel

Couleurs disponibles :
  Citations (priorité 1) :
    yellow  → citation générale
    green   → résultat / donnée empirique
    blue    → définition / concept clé
    red     → point critique / à débattre
    purple  → méthode
    orange  → hypothèse

  Contextuel (priorité 2-5) :
    pink    → lien avec ma recherche (priorité 2)
    cyan    → conclusion / implication (priorité 3)
    lime    → passage méthodologique clé (priorité 4)
    gray    → mot-clé / terme technique (priorité 5)
"""

import os
from pathlib import Path
from typing import Optional
import pymupdf
from mcp.server.fastmcp import FastMCP

# ── Configuration ──────────────────────────────────────────────────────────────
VAULT_PATH = Path(os.getenv("VAULT_PATH", r"P:\Obsidian Vaults\Recherche"))
PDF_DIR = VAULT_PATH / "Bibliographie" / "Zotero" / "all_pdf"

# Palette complète en RGB normalisé (0-1)
COLORS = {
    # ── Citations ──────────────────────────────────────────────
    "yellow":  (1.0,  1.0,  0.0),    # Citation générale
    "green":   (0.0,  0.9,  0.0),    # Résultat / donnée empirique
    "blue":    (0.0,  0.6,  1.0),    # Définition / concept clé
    "red":     (1.0,  0.0,  0.0),    # Point critique / à débattre
    "purple":  (0.6,  0.0,  0.9),    # Méthode / approche
    "orange":  (1.0,  0.55, 0.0),    # Hypothèse / question de recherche

    # ── Contextuel ─────────────────────────────────────────────
    "pink":    (1.0,  0.5,  0.75),   # Lien avec ma recherche
    "cyan":    (0.0,  0.9,  0.9),    # Conclusion / implication
    "lime":    (0.75, 1.0,  0.0),    # Passage méthodologique clé
    "gray":    (0.75, 0.75, 0.75),   # Mot-clé / terme technique
}

COLOR_DESCRIPTIONS = {
    "yellow":  "Citation générale (priorité 1)",
    "green":   "Résultat / donnée empirique (priorité 1)",
    "blue":    "Définition / concept clé (priorité 1)",
    "red":     "Point critique / à débattre (priorité 1)",
    "purple":  "Méthode / approche (priorité 1)",
    "orange":  "Hypothèse / question de recherche (priorité 1)",
    "pink":    "Lien avec ma recherche (priorité 2)",
    "cyan":    "Conclusion / implication (priorité 3)",
    "lime":    "Passage méthodologique clé (priorité 4)",
    "gray":    "Mot-clé / terme technique (priorité 5)",
}

mcp = FastMCP("pdf-highlighter")


# ── Fonctions utilitaires ───────────────────────────────────────────────────────

def find_pdf(pdf_name: str) -> tuple:
    """Trouve le PDF dans all_pdf, avec recherche partielle si nécessaire."""
    pdf_path = PDF_DIR / pdf_name
    if pdf_path.exists():
        return pdf_path, pdf_name

    stem = Path(pdf_name).stem
    matches = list(PDF_DIR.glob(f"*{stem}*"))
    if matches:
        return matches[0], matches[0].name

    words = stem.split()[:4]
    for word in words:
        matches = list(PDF_DIR.glob(f"*{word}*"))
        if matches:
            return matches[0], matches[0].name

    return None, pdf_name


def highlight_text_in_page(
    pdf_page,
    text: str,
    color: str,
    comment: Optional[str] = None,
) -> bool:
    """Surligne un texte dans une page PDF. Retourne True si trouvé."""
    quads = pdf_page.search_for(text, quads=True)

    if not quads:
        short = " ".join(text.split()[:6])
        quads = pdf_page.search_for(short, quads=True)

    if not quads:
        return False

    stroke_color = COLORS.get(color, COLORS["yellow"])

    for quad in quads:
        annot = pdf_page.add_highlight_annot(quad)
        annot.set_colors(stroke=stroke_color)
        if comment:
            info = annot.info
            info["content"] = comment
            info["title"] = "Claude"
            annot.set_info(info)
        annot.update()

    return True


# ── Outils MCP ─────────────────────────────────────────────────────────────────

@mcp.tool()
def highlight_pdf(
    pdf_name: str,
    citation: str,
    page: int,
    color: str = "yellow",
    comment: Optional[str] = None,
) -> str:
    """
    Surligne un texte dans un PDF et retourne un lien PDF++ cliquable.

    Args:
        pdf_name:  Nom exact du fichier PDF
        citation:  Texte exact à surligner
        page:      Numéro de page (commence à 1)
        color:     yellow | green | blue | red | purple | orange | pink | cyan | lime | gray
        comment:   Commentaire optionnel sur l'annotation
    """
    pdf_path, pdf_name = find_pdf(pdf_name)
    if not pdf_path:
        return f"❌ PDF introuvable : {pdf_name}\nVérifie dans {PDF_DIR}"

    doc = pymupdf.open(str(pdf_path))
    page_idx = page - 1

    if page_idx < 0 or page_idx >= len(doc):
        doc.close()
        return f"❌ Page {page} invalide. Le PDF a {len(doc)} pages."

    found = highlight_text_in_page(doc[page_idx], citation, color, comment)

    if not found:
        doc.close()
        return (
            f"❌ Texte non trouvé à la page {page}.\n"
            f"Citation : '{citation}'\n"
            f"Conseil : réduis la citation aux 6-8 premiers mots."
        )

    doc.save(str(pdf_path), incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP)
    doc.close()

    relative_path = f"Bibliographie/Zotero/all_pdf/{pdf_name}"
    pdf_link = f"[[{relative_path}#page={page}]]"

    return (
        f"✅ Surlignage effectué ({color}) — page {page}\n\n"
        f"> \"{citation}\"\n"
        f"> {pdf_link}"
    )


@mcp.tool()
def highlight_multiple(
    pdf_name: str,
    citations: list,
) -> str:
    """
    Surligne plusieurs passages d'un coup dans un PDF.
    Gère à la fois les citations (insérées dans la note) et les passages contextuels
    (surlignés dans le PDF uniquement, non insérés dans la note).

    Args:
        pdf_name:  Nom exact du fichier PDF
        citations: Liste de dicts avec les clés :
                   - citation (str) : texte à surligner
                   - page (int)     : numéro de page
                   - color (str)    : couleur de surlignage
                   - comment (str)  : commentaire optionnel

                   Couleurs citations (→ insérées dans la note) :
                     yellow  → citation générale
                     green   → résultat / donnée empirique
                     blue    → définition / concept clé
                     red     → point critique / à débattre
                     purple  → méthode
                     orange  → hypothèse

                   Couleurs contextuelles (→ surlignées dans le PDF uniquement) :
                     pink    → lien avec ma recherche
                     cyan    → conclusion / implication
                     lime    → passage méthodologique clé
                     gray    → mot-clé / terme technique
    """
    pdf_path, pdf_name = find_pdf(pdf_name)
    if not pdf_path:
        return f"❌ PDF introuvable : {pdf_name}"

    doc = pymupdf.open(str(pdf_path))
    results = []
    errors = []

    for item in citations:
        citation = item.get("citation", "")
        page = item.get("page", 1)
        color = item.get("color", "yellow")
        comment = item.get("comment", None)

        page_idx = page - 1
        if page_idx < 0 or page_idx >= len(doc):
            errors.append(f"Page {page} invalide : '{citation[:40]}'")
            continue

        found = highlight_text_in_page(doc[page_idx], citation, color, comment)

        if not found:
            errors.append(f"Texte non trouvé p.{page} [{color}] : '{citation[:50]}'")
            continue

        results.append({
            "citation": citation,
            "page": page,
            "color": color,
            "is_citation": color in ["yellow", "green", "blue", "red", "purple", "orange"],
        })

    doc.save(str(pdf_path), incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP)
    doc.close()

    citations_found = [r for r in results if r["is_citation"]]
    contextual_found = [r for r in results if not r["is_citation"]]

    relative_path = f"Bibliographie/Zotero/all_pdf/{pdf_name}"
    output = f"✅ {len(results)} surlignage(s) dans {pdf_name}\n"
    output += f"   └ {len(citations_found)} citation(s) · {len(contextual_found)} passage(s) contextuel(s)\n\n"

    if citations_found:
        output += "**Citations à insérer dans la note :**\n\n"
        for r in citations_found:
            link = f"[[{relative_path}#page={r['page']}]]"
            output += f"> \"{r['citation']}\"\n"
            output += f"> {link}  `{r['color']}`\n\n"

    if contextual_found:
        output += "**Passages contextuels surlignés dans le PDF :**\n"
        for r in contextual_found:
            output += f"- p.{r['page']} [{r['color']}] : \"{r['citation'][:70]}\"\n"

    if errors:
        output += f"\n⚠️ {len(errors)} non trouvé(s) :\n"
        for e in errors:
            output += f"- {e}\n"

    return output


@mcp.tool()
def list_pdf_colors() -> str:
    """
    Liste toutes les couleurs disponibles pour le surlignage et leur signification.
    """
    output = "**Couleurs de surlignage disponibles :**\n\n"
    output += "*Citations (insérées dans la note Obsidian) :*\n"
    for color in ["yellow", "green", "blue", "red", "purple", "orange"]:
        output += f"- `{color}` — {COLOR_DESCRIPTIONS[color]}\n"
    output += "\n*Contextuelles (surlignées dans le PDF uniquement) :*\n"
    for color in ["pink", "cyan", "lime", "gray"]:
        output += f"- `{color}` — {COLOR_DESCRIPTIONS[color]}\n"
    return output


# ── Point d'entrée ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")
