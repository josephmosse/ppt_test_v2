"""
Moteur générique : ne connaît rien au contenu métier.

Conventions de nommage dans le template (volet Sélection, Alt+F10) :
    table_xxx : tableau rempli par un DataFrame
    img_xxx   : rectangle remplacé par un graphique matplotlib
    {trou}    : dans n'importe quelle zone de texte, remplacé par une valeur
"""
from io import BytesIO
from numbers import Real

import matplotlib.pyplot as plt
from pptx import Presentation


# ---------- utilitaires ----------

def fmt(v, dec=1):
    """Format français : 1250.4 -> '1 250,4'. Les textes passent tels quels."""
    if isinstance(v, Real):           # int, float et types numpy
        return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")
    return str(v)


def fmt_pct(v, dec=1, signe=True):
    """0.0523 -> '+5,2 %'."""
    s = f"{v * 100:+.{dec}f}" if signe else f"{v * 100:.{dec}f}"
    return s.replace(".", ",") + " %"


def set_text(text_frame, text):
    """Remplace le texte du 1er paragraphe en gardant le style du 1er run."""
    p = text_frame.paragraphs[0]
    if p.runs:
        p.runs[0].text = text
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.add_run().text = text


def iter_shapes(prs):
    """(numéro de slide, forme) pour toutes les formes du deck."""
    for n, slide in enumerate(prs.slides, start=1):
        for shape in slide.shapes:
            yield n, shape


# ---------- remplisseurs ----------

def fill_table(shape, df):
    """
    Remplit un tableau du template avec un DataFrame.
    - colonne 0 du tableau = index du DataFrame (libellés de lignes)
    - autant de lignes d'en-tête que de niveaux de colonnes (1 ou 2)
    - en-tête à 2 niveaux : le niveau 1 est écrit dans la 1re cellule de chaque groupe fusionné
    """
    table = shape.table
    n_hdr = df.columns.nlevels
    attendu = (n_hdr + len(df), df.shape[1] + 1)
    reel = (len(table.rows), len(table.columns))
    if attendu != reel:
        raise ValueError(f"{shape.name} : le tableau fait {reel} (lignes, colonnes), "
                         f"les données demandent {attendu}")

    cols = [c if isinstance(c, tuple) else (c,) for c in df.columns]
    for lvl in range(n_hdr):
        prev = None
        for j, col in enumerate(cols, start=1):
            groupe = col[:lvl + 1]               # libellés jusqu'à ce niveau
            if lvl == n_hdr - 1 or groupe != prev:
                set_text(table.cell(lvl, j).text_frame, str(col[lvl]))
                prev = groupe

    for i, (label, row) in enumerate(df.iterrows()):
        set_text(table.cell(n_hdr + i, 0).text_frame, str(label))
        for j, v in enumerate(row, start=1):
            set_text(table.cell(n_hdr + i, j).text_frame, fmt(v))


def fill_image(shape, draw, data):
    """Dessine `draw(ax, data)` à la taille du rectangle, pose l'image, supprime le rectangle."""
    fig, ax = plt.subplots(figsize=(shape.width.inches, shape.height.inches))
    draw(ax, data)
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    shape.part.slide.shapes.add_picture(buf, shape.left, shape.top, shape.width, shape.height)
    shape._element.getparent().remove(shape._element)


def fill_texts(prs, values):
    """Remplace les {trous} dans toutes les zones de texte (paragraphe par paragraphe)."""
    for n, shape in iter_shapes(prs):
        if not shape.has_text_frame:
            continue
        for p in shape.text_frame.paragraphs:
            full = "".join(r.text for r in p.runs)   # un {trou} peut être coupé en plusieurs runs
            if "{" not in full:
                continue
            try:
                p.runs[0].text = full.format_map(values)
            except KeyError as e:
                raise KeyError(f"Slide {n}, '{shape.name}' : pas de valeur pour {e}") from None
            for r in p.runs[1:]:
                r.text = ""


# ---------- orchestration ----------

def build(template, output, data, tables, charts, values):
    """Remplit tout le template, vérifie que rien n'est oublié, sauvegarde."""
    prs = Presentation(template)
    shapes = {s.name: (n, s) for n, s in iter_shapes(prs)}

    # 1. Cohérence template <-> code : chaque objet a son contenu et inversement
    erreurs = []
    for prefix, builders in [("table_", tables), ("img_", charts)]:
        dans_template = {k for k in shapes if k.startswith(prefix)}
        for k in dans_template - builders.keys():
            erreurs.append(f"'{k}' (slide {shapes[k][0]}) n'a pas de fonction associée")
        for k in builders.keys() - dans_template:
            erreurs.append(f"'{k}' est défini dans le code mais absent du template")
    if erreurs:
        raise ValueError("Template et code incohérents :\n  " + "\n  ".join(erreurs))

    # 2. Remplissage
    for name, builder in tables.items():
        fill_table(shapes[name][1], builder(data))
    for name, draw in charts.items():
        fill_image(shapes[name][1], draw, data)
    fill_texts(prs, values)

    # 3. Contrôle final : plus aucun {trou} dans le deck
    restes = [f"slide {n} '{s.name}'" for n, s in iter_shapes(prs)
              if s.has_text_frame and "{" in s.text_frame.text]
    if restes:
        raise ValueError("Trous non remplis : " + ", ".join(restes))

    output.parent.mkdir(parents=True, exist_ok=True)
    prs.save(output)
    return output
