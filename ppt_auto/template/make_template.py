"""
DÉMO UNIQUEMENT : simule le template que tu fais à la main dans PowerPoint.
Chez toi, tu ne gardes pas ce fichier : tu nommes les objets de ton vrai PPT (Alt+F10).
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

VERT, VERT_FONCE, GRIS = RGBColor(0, 0x91, 0x5A), RGBColor(0, 0x54, 0x3A), RGBColor(0x33, 0x33, 0x33)
BLANC = RGBColor(255, 255, 255)

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.33), Inches(7.5)


def new_slide(titre=None, n=None):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    if titre:
        bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.12))
        bar.fill.solid(); bar.fill.fore_color.rgb = VERT; bar.line.fill.background()
        text(s, Inches(0.5), Inches(0.3), Inches(12.3), Inches(0.8), [titre], 26, bold=True, color=VERT_FONCE)
        text(s, Inches(0.5), Inches(7.05), Inches(9), Inches(0.35), ["ALM Treasury – Comité ALM {trim}"], 10)
        text(s, Inches(12.0), Inches(7.05), Inches(0.8), Inches(0.35), [str(n)], 10, align=PP_ALIGN.RIGHT)
    return s


def text(s, x, y, w, h, lignes, size=15, bold=False, color=GRIS, align=PP_ALIGN.LEFT, name=None):
    tb = s.shapes.add_textbox(x, y, w, h)
    if name:
        tb.name = name
    tf = tb.text_frame; tf.word_wrap = True
    for i, ligne in enumerate(lignes):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.space_after = Pt(6)
        r = p.add_run(); r.text = ligne
        r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color
    return tb


def table(s, name, rows, cols, box, n_hdr=1, merges=(), corner=""):
    gf = s.shapes.add_table(rows, cols, *box); gf.name = name
    t = gf.table
    for (r1, c1), (r2, c2) in merges:
        t.cell(r1, c1).merge(t.cell(r2, c2))
    for r in range(rows):
        for c in range(cols):
            cell = t.cell(r, c)
            if cell.is_spanned:
                continue
            p = cell.text_frame.paragraphs[0]; run = p.add_run(); run.text = "0"
            run.font.size = Pt(12); p.alignment = PP_ALIGN.CENTER if c else PP_ALIGN.LEFT
            if r < n_hdr:
                run.font.bold = True; run.font.color.rgb = BLANC
                cell.fill.solid(); cell.fill.fore_color.rgb = VERT if r == 0 else VERT_FONCE
            elif r == rows - 1 and name in ("table_nii", "table_depots"):
                run.font.bold = True                          # ligne Total en gras
    t.cell(0, 0).text_frame.paragraphs[0].runs[0].text = corner
    return gf


def img(s, name, x, y, w, h):
    ph = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h); ph.name = name
    ph.text_frame.text = f"[{name}]"


I = Inches

# 1. Couverture
s = new_slide()
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid(); bg.fill.fore_color.rgb = VERT_FONCE; bg.line.fill.background()
text(s, I(0.8), I(2.6), I(11.5), I(1.2), ["Comité ALM – {trim}"], 44, bold=True, color=BLANC)
text(s, I(0.8), I(3.8), I(11.5), I(0.6), ["ALM Treasury · Arrêté au {date_arrete}"], 20, color=BLANC)

# 2. Synthèse : tableau KPI + texte
s = new_slide("Synthèse – {trim}", 2)
table(s, "table_kpi", 5, 4, (I(0.5), I(1.4), I(7.2), I(2.6)), corner="Indicateur")
text(s, I(8.1), I(1.4), I(4.7), I(5.3), [
    "• Gap total de {gap_total} M€, en {gap_sens} de {gap_var} M€.",
    "• NII de {nii_total} M€ sur le trimestre, en {nii_sens} de {nii_var_pct}.",
    "• Encours de dépôts de {depots_total} M€ ({depots_var_pct}).",
    "• Pire scénario EVE : {eve_pire_scen} ({eve_pire} M€).",
], 15, name="txt_synthese")

# 3. Tableau de gap (en-têtes 2 niveaux)
s = new_slide("Gap de taux par bucket – {trim} vs {trim_prec}", 3)
table(s, "table_gap", 12, 7, (I(0.5), I(1.3), I(12.3), I(5.4)), n_hdr=2,
      merges=[((0, 1), (0, 3)), ((0, 4), (0, 6)), ((0, 0), (1, 0))], corner="Bucket")

# 4. Graphique gap + commentaire
s = new_slide("Gap par bucket", 4)
img(s, "img_gap", I(0.5), I(1.2), I(12.3), I(4.6))
text(s, I(0.5), I(5.9), I(12.3), I(1.1), [
    "• Le gap total s'établit à {gap_total} M€, en {gap_sens} de {gap_var} M€ vs {trim_prec}.",
    "• Le bucket le plus exposé est {bucket_max} ({gap_max} M€).",
], name="txt_gap")

# 5. Graphique NII historique + commentaire
s = new_slide("Évolution du NII trimestriel", 5)
img(s, "img_nii", I(0.5), I(1.2), I(12.3), I(4.6))
text(s, I(0.5), I(5.9), I(12.3), I(1.1), [
    "• Le NII atteint {nii_total} M€ au {trim}, en {nii_sens} de {nii_var_pct} sur le trimestre.",
    "• Principal contributeur : {nii_comp_max} (+{nii_comp_var} M€).",
], name="txt_nii")

# 6. Tableau NII par composante + commentaire
s = new_slide("NII par composante (M€)", 6)
table(s, "table_nii", 5, 5, (I(0.5), I(1.4), I(12.3), I(2.6)), corner="Composante")
text(s, I(0.5), I(4.5), I(12.3), I(1.0), [
    "• Hausse portée par {nii_comp_max} (+{nii_comp_var} M€).",
], name="txt_nii_table")

# 7. Dépôts : tableau + graphique + commentaire
s = new_slide("Encours de dépôts (M€)", 7)
table(s, "table_depots", 7, 4, (I(0.5), I(1.4), I(6.0), I(3.4)), corner="Produit")
img(s, "img_depots", I(6.8), I(1.2), I(6.0), I(4.5))
text(s, I(0.5), I(5.9), I(12.3), I(1.1), [
    "• Encours total de {depots_total} M€ ({depots_var_pct} vs {trim_prec}).",
    "• Plus forte hausse : {depot_hausse} (+{depot_hausse_var} M€) ; plus forte baisse : {depot_baisse} (-{depot_baisse_var} M€).",
], name="txt_depots")

# 8. Tableau sensibilités (en-têtes 2 niveaux)
s = new_slide("Sensibilités EVE / NII – scénarios réglementaires (M€)", 8)
table(s, "table_sens", 8, 5, (I(0.5), I(1.4), I(12.3), I(3.8)), n_hdr=2,
      merges=[((0, 1), (0, 2)), ((0, 3), (0, 4)), ((0, 0), (1, 0))], corner="Scénario")
text(s, I(0.5), I(5.6), I(12.3), I(1.0), [
    "• Scénarios les plus défavorables : {eve_pire_scen} pour l'EVE ({eve_pire} M€), {nii_pire_scen} pour le NII ({nii_pire} M€).",
], name="txt_sens_table")

# 9. Graphique ΔEVE
s = new_slide("ΔEVE par scénario", 9)
img(s, "img_sens", I(0.5), I(1.2), I(12.3), I(4.8))
text(s, I(0.5), I(6.1), I(12.3), I(0.8), [
    "• Pire scénario au {trim} : {eve_pire_scen} ({eve_pire} M€).",
], name="txt_sens")

# 10. Gap cumulé
s = new_slide("Gap cumulé par bucket", 10)
img(s, "img_gap_cumul", I(0.5), I(1.2), I(12.3), I(4.8))
text(s, I(0.5), I(6.1), I(12.3), I(0.8), [
    "• Point bas du gap cumulé : {cumul_min} M€ sur le bucket {cumul_min_bucket}.",
], name="txt_gap_cumul")

prs.save(Path(__file__).parent / "template.pptx")
print("Template démo créé")
