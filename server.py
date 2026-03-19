"""
MCP Server — PDF Highlighter + Formula OCR pour Obsidian + PDF++
Version 3 — Palette étendue + extraction de formules mathématiques via pix2tex

Outils disponibles :
  highlight_pdf        → surligne un passage
  highlight_multiple   → surligne plusieurs passages en une fois
  list_pdf_colors      → liste les couleurs disponibles
  extract_formula      → extrait une formule mathématique en LaTeX via OCR
  extract_all_formulas → détecte et extrait toutes les formules d'une page
"""

import os
import io
import tempfile
from pathlib import Path
from typing import Optional
import pymupdf
from PIL import Image
from mcp.server.fastmcp import FastMCP

# ── Lazy loading pix2tex — ne charge le modèle qu'au premier appel ─────────────
_latex_ocr = None

def get_latex_ocr():
    """Charge le modèle pix2tex une seule fois."""
    global _latex_ocr
    if _latex_ocr is None:
        from pix2tex.cli import LatexOCR
        _latex_ocr = LatexOCR()
    return _latex_ocr


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


def page_to_image(pdf_page, dpi: int = 300) -> Image.Image:
    """Convertit une page PDF ou une zone en image PIL."""
    mat = pymupdf.Matrix(dpi / 72, dpi / 72)
    pix = pdf_page.get_pixmap(matrix=mat, alpha=False)
    img_data = pix.tobytes("png")
    return Image.open(io.BytesIO(img_data))


def crop_region(image: Image.Image, rect: pymupdf.Rect, page: pymupdf.Page, dpi: int = 300) -> Image.Image:
    """Découpe une zone rectangulaire d'une image PIL selon les coordonnées PDF."""
    scale = dpi / 72
    page_height = page.rect.height
    x0 = int(rect.x0 * scale)
    y0 = int(rect.y0 * scale)
    x1 = int(rect.x1 * scale)
    y1 = int(rect.y1 * scale)
    return image.crop((x0, y0, x1, y1))


def image_to_latex(img: Image.Image) -> str:
    """Convertit une image de formule en LaTeX via pix2tex."""
    ocr = get_latex_ocr()
    return ocr(img)


def detect_formula_regions(page: pymupdf.Page) -> list:
    """
    Détecte les zones probables de formules mathématiques dans une page.
    Stratégie : cherche les blocs d'images et les zones avec peu de texte
    entre des lignes espacées (pattern typique des formules display).
    """
    regions = []

    # 1. Images intégrées dans la page (formules rendues comme images)
    img_list = page.get_images(full=True)
    for img_info in img_list:
        xref = img_info[0]
        rects = page.get_image_rects(xref)
        for rect in rects:
            # Filtre : ignorer les très grandes images (figures) et les très petites (icônes)
            width = rect.x1 - rect.x0
            height = rect.y1 - rect.y0
            if 20 < height < 200 and width > 30:
                regions.append({
                    "type": "image",
                    "rect": rect,
                    "xref": xref,
                })

    # 2. Blocs de texte avec caractères mathématiques typiques
    blocks = page.get_text("dict")["blocks"]
    for block in blocks:
        if block.get("type") != 0:
            continue
        block_text = " ".join(
            span["text"]
            for line in block.get("lines", [])
            for span in line.get("spans", [])
        )
        # Heuristique : présence de caractères mathématiques courants
        math_chars = set("∑∫∂∇αβγδεζηθλμπσφψω=≤≥≠±×÷√∞")
        math_score = sum(1 for c in block_text if c in math_chars)
        has_greek = any(c in block_text for c in "αβγδεζηθλμπσφψω")
        has_fraction_pattern = "/" in block_text and any(c.isdigit() for c in block_text)

        if math_score >= 2 or has_greek or has_fraction_pattern:
            rect = pymupdf.Rect(block["bbox"])
            # Ajoute un peu de marge autour
            rect = pymupdf.Rect(
                rect.x0 - 5, rect.y0 - 5,
                rect.x1 + 5, rect.y1 + 5
            )
            regions.append({
                "type": "text_math",
                "rect": rect,
                "preview": block_text[:80],
            })

    return regions


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
    Gère citations (insérées dans la note) et passages contextuels (PDF uniquement).

    Args:
        pdf_name:  Nom exact du fichier PDF
        citations: Liste de dicts avec : citation, page, color, comment (optionnel)

                   Couleurs citations (→ insérées dans la note) :
                     yellow | green | blue | red | purple | orange

                   Couleurs contextuelles (→ PDF uniquement) :
                     pink | cyan | lime | gray
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
def extract_formula(
    pdf_name: str,
    page: int,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    add_highlight: bool = True,
) -> str:
    """
    Extrait une formule mathématique d'une zone précise du PDF et la convertit en LaTeX.

    Args:
        pdf_name:      Nom exact du fichier PDF
        page:          Numéro de page (commence à 1)
        x0, y0:        Coordonnées du coin supérieur gauche de la zone (en points PDF)
        x1, y1:        Coordonnées du coin inférieur droit de la zone (en points PDF)
        add_highlight: Ajoute un surlignage violet sur la zone dans le PDF (défaut: True)

    Returns:
        La formule en LaTeX prête à insérer dans Obsidian (format $...$ ou $$...$$)

    Note sur les coordonnées :
        Dans un PDF standard (A4), la page fait environ 595 × 842 points.
        Pour estimer les coordonnées, divise la page en grille :
        x=0 (gauche) → x=595 (droite), y=0 (haut) → y=842 (bas)
    """
    pdf_path, pdf_name = find_pdf(pdf_name)
    if not pdf_path:
        return f"❌ PDF introuvable : {pdf_name}"

    doc = pymupdf.open(str(pdf_path))
    page_idx = page - 1

    if page_idx < 0 or page_idx >= len(doc):
        doc.close()
        return f"❌ Page {page} invalide."

    pdf_page = doc[page_idx]
    rect = pymupdf.Rect(x0, y0, x1, y1)

    # Vérification que le rect est dans la page
    page_rect = pdf_page.rect
    if not page_rect.contains(rect):
        rect = rect & page_rect  # intersection

    if rect.is_empty:
        doc.close()
        return "❌ Zone vide ou hors de la page."

    # Capture de la zone en haute résolution
    try:
        mat = pymupdf.Matrix(3.0, 3.0)  # 216 DPI pour meilleure précision OCR
        clip_pix = pdf_page.get_pixmap(matrix=mat, clip=rect, alpha=False)
        img_data = clip_pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
    except Exception as e:
        doc.close()
        return f"❌ Erreur lors de la capture de la zone : {e}"

    # OCR avec pix2tex
    try:
        latex = image_to_latex(img)
        latex = latex.strip()
    except Exception as e:
        doc.close()
        return f"❌ Erreur OCR pix2tex : {e}"

    # Surlignage optionnel de la zone (couleur violette = méthode)
    if add_highlight:
        try:
            annot = pdf_page.add_rect_annot(rect)
            annot.set_colors(stroke=COLORS["purple"])
            annot.set_border(width=1.5)
            info = annot.info
            info["content"] = f"Formule extraite : {latex}"
            info["title"] = "Claude"
            annot.set_info(info)
            annot.update()
            doc.save(str(pdf_path), incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP)
        except Exception:
            pass  # Le surlignage est optionnel, on ne bloque pas si ça échoue

    doc.close()

    # Formatage LaTeX pour Obsidian
    # Formule inline si courte, display si longue
    is_display = len(latex) > 30 or any(cmd in latex for cmd in [
        r"\frac", r"\sum", r"\int", r"\prod", r"\begin", r"\lim"
    ])

    if is_display:
        obsidian_latex = f"$$\n{latex}\n$$"
    else:
        obsidian_latex = f"${latex}$"

    relative_path = f"Bibliographie/Zotero/all_pdf/{pdf_name}"
    pdf_link = f"[[{relative_path}#page={page}]]"

    return (
        f"✅ Formule extraite — page {page}\n\n"
        f"**LaTeX à insérer dans la note :**\n"
        f"```\n{obsidian_latex}\n```\n\n"
        f"**Rendu :** {obsidian_latex}\n\n"
        f"**Lien vers la page :** {pdf_link}"
    )


@mcp.tool()
def extract_all_formulas(
    pdf_name: str,
    page: int,
) -> str:
    """
    Détecte et extrait automatiquement toutes les formules mathématiques d'une page.
    Utile pour les pages denses en équations (papiers d'économétrie, modèles théoriques).

    Args:
        pdf_name:  Nom exact du fichier PDF
        page:      Numéro de page à analyser (commence à 1)

    Returns:
        Liste de toutes les formules trouvées en LaTeX avec leurs coordonnées
    """
    pdf_path, pdf_name = find_pdf(pdf_name)
    if not pdf_path:
        return f"❌ PDF introuvable : {pdf_name}"

    doc = pymupdf.open(str(pdf_path))
    page_idx = page - 1

    if page_idx < 0 or page_idx >= len(doc):
        doc.close()
        return f"❌ Page {page} invalide."

    pdf_page = doc[page_idx]

    # Détection des zones probables de formules
    regions = detect_formula_regions(pdf_page)

    if not regions:
        doc.close()
        return f"ℹ️ Aucune formule détectée à la page {page}.\nEssaie `extract_formula` avec des coordonnées manuelles."

    results = []
    errors = []
    modified = False

    ocr = get_latex_ocr()

    for i, region in enumerate(regions):
        rect = region["rect"]
        region_type = region["type"]

        try:
            # Capture haute résolution de la zone
            mat = pymupdf.Matrix(3.0, 3.0)
            clip_pix = pdf_page.get_pixmap(matrix=mat, clip=rect, alpha=False)
            img_data = clip_pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))

            # OCR
            latex = ocr(img).strip()

            if not latex or len(latex) < 2:
                continue

            # Surlignage de la zone détectée
            try:
                annot = pdf_page.add_rect_annot(rect)
                annot.set_colors(stroke=COLORS["purple"])
                annot.set_border(width=1.0)
                info = annot.info
                info["content"] = f"Formule {i+1} : {latex}"
                info["title"] = "Claude"
                annot.set_info(info)
                annot.update()
                modified = True
            except Exception:
                pass

            # Format LaTeX pour Obsidian
            is_display = len(latex) > 30 or any(cmd in latex for cmd in [
                r"\frac", r"\sum", r"\int", r"\prod", r"\begin", r"\lim"
            ])
            obsidian_latex = f"$$\n{latex}\n$$" if is_display else f"${latex}$"

            results.append({
                "index": i + 1,
                "type": region_type,
                "rect": f"({rect.x0:.0f}, {rect.y0:.0f}, {rect.x1:.0f}, {rect.y1:.0f})",
                "latex": obsidian_latex,
                "preview": region.get("preview", ""),
            })

        except Exception as e:
            errors.append(f"Zone {i+1} : {e}")

    if modified:
        doc.save(str(pdf_path), incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP)
    doc.close()

    if not results:
        return (
            f"⚠️ {len(regions)} zone(s) détectée(s) mais aucune formule extraite avec succès.\n"
            f"Essaie `extract_formula` avec des coordonnées manuelles.\n"
            + (f"Erreurs : {'; '.join(errors)}" if errors else "")
        )

    relative_path = f"Bibliographie/Zotero/all_pdf/{pdf_name}"
    pdf_link = f"[[{relative_path}#page={page}]]"

    output = f"✅ {len(results)} formule(s) extraite(s) — page {page} {pdf_link}\n\n"
    output += "**Formules à insérer dans la note :**\n\n"

    for r in results:
        output += f"**Formule {r['index']}** *(zone {r['rect']})*\n"
        output += f"```\n{r['latex']}\n```\n\n"

    if errors:
        output += f"\n⚠️ {len(errors)} erreur(s) : {'; '.join(errors)}\n"

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
    output += "\n*Formules mathématiques :*\n"
    output += "- Encadré `purple` — zone de formule extraite par OCR\n"
    return output


# ── Point d'entrée ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")
