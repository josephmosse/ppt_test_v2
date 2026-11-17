"""
Contenu métier du rapport : c'est ici qu'on ajoute ou modifie une slide.
    TABLES : nom du tableau dans le template -> fonction(data) qui renvoie un DataFrame
    CHARTS : nom du rectangle img_ -> fonction(ax, data) qui dessine le graphique
    values(data) : dictionnaire des {trous} de texte
"""
import pandas as pd

from config import DATE_ARRETE, TRIM, TRIM_PREC
from engine import fmt, fmt_pct
from style import GRIS, VERT, VERT_CLAIR, VERT_FONCE


def _sens(x):
    return "hausse" if x >= 0 else "baisse"


def _var_table(df):
    """Ajoute une ligne Total et les colonnes de variation à un tableau T-1 / T."""
    out = df[[TRIM_PREC, TRIM]].copy()
    out.loc["Total"] = out.sum()
    out["Var."] = out[TRIM] - out[TRIM_PREC]
    out["Var. %"] = (out["Var."] / out[TRIM_PREC]).map(fmt_pct)
    return out


# ============================ TABLEAUX ============================

def table_kpi(d):
    eve = d.sens["ΔEVE"]
    lignes = {
        "Gap total (M€)": d.gap.xs("Gap", axis=1, level=1).sum(),
        "NII trimestriel (M€)": d.nii.loc[[TRIM_PREC, TRIM]].sum(axis=1),
        "Encours dépôts (M€)": d.depots.sum(),
        "ΔEVE pire scénario (M€)": eve.min(),
    }
    df = pd.DataFrame(lignes).T[[TRIM_PREC, TRIM]]
    df["Var."] = (df[TRIM] - df[TRIM_PREC]).map(lambda v: ("+" if v >= 0 else "") + fmt(v))
    return df


def table_gap(d):
    return d.gap


def table_nii(d):
    return _var_table(d.nii.loc[[TRIM_PREC, TRIM]].T)


def table_depots(d):
    return _var_table(d.depots).drop(columns="Var.")


def table_sens(d):
    return d.sens


TABLES = {
    "table_kpi": table_kpi,
    "table_gap": table_gap,
    "table_nii": table_nii,
    "table_depots": table_depots,
    "table_sens": table_sens,
}


# ============================ GRAPHIQUES ============================

def chart_gap(ax, d):
    d.gap.xs("Gap", axis=1, level=1).plot.bar(ax=ax, width=0.75, rot=0)
    ax.axhline(0, color="grey", lw=0.8)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2)


def chart_nii(ax, d):
    nii = d.nii
    nii.plot.bar(ax=ax, stacked=True, rot=0, width=0.6, color=[VERT, VERT_CLAIR, GRIS])
    for i, total in enumerate(nii.sum(axis=1)):                 # total au-dessus de chaque barre
        ax.text(i, total + 3, fmt(total), ha="center", fontsize=11)
    ax.set_ylim(0, nii.sum(axis=1).max() * 1.12)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=3)


def chart_depots(ax, d):
    d.depots.iloc[::-1].plot.barh(ax=ax, width=0.75)            # inversé : 1er produit en haut
    ax.xaxis.grid(True); ax.yaxis.grid(False)
    h, l = ax.get_legend_handles_labels()
    ax.legend(h[::-1], l[::-1], loc="lower right")      # légende dans l'ordre des barres


def chart_sens(ax, d):
    d.sens["ΔEVE"].plot.bar(ax=ax, width=0.75, rot=0)
    ax.axhline(0, color="grey", lw=0.8)
    ax.set_ylabel("ΔEVE (M€)")
    ax.xaxis.grid(False)
    ax.legend(loc="upper right")


def chart_gap_cumul(ax, d):
    cumul = d.gap.xs("Gap", axis=1, level=1).cumsum()
    for col, color in zip(cumul.columns, [VERT_CLAIR, VERT_FONCE]):
        ax.plot(cumul.index, cumul[col], marker="o", lw=2.5, color=color, label=col)
    ax.axhline(0, color="grey", lw=0.8)
    ax.xaxis.grid(False)
    ax.legend(loc="upper left")


CHARTS = {
    "img_gap": chart_gap,
    "img_nii": chart_nii,
    "img_depots": chart_depots,
    "img_sens": chart_sens,
    "img_gap_cumul": chart_gap_cumul,
}


# ============================ TEXTES ============================

def values(d):
    gap = d.gap.xs("Gap", axis=1, level=1)
    gap_tot, gap_tot_prec = gap[TRIM].sum(), gap[TRIM_PREC].sum()
    bucket_max = gap[TRIM].abs().idxmax()

    nii_t, nii_p = d.nii.loc[TRIM], d.nii.loc[TRIM_PREC]
    nii_var = (nii_t - nii_p)
    comp_max = nii_var.idxmax()

    dep_var = d.depots[TRIM] - d.depots[TRIM_PREC]

    eve, nii_s = d.sens[("ΔEVE", TRIM)], d.sens[("ΔNII", TRIM)]
    cumul = gap[TRIM].cumsum()

    return {
        "trim": TRIM, "trim_prec": TRIM_PREC, "date_arrete": DATE_ARRETE,
        # Gap
        "gap_total": fmt(gap_tot), "gap_sens": _sens(gap_tot - gap_tot_prec),
        "gap_var": fmt(abs(gap_tot - gap_tot_prec)),
        "bucket_max": bucket_max, "gap_max": fmt(gap.loc[bucket_max, TRIM]),
        "cumul_min_bucket": cumul.idxmin(), "cumul_min": fmt(cumul.min()),
        # NII
        "nii_total": fmt(nii_t.sum()), "nii_sens": _sens(nii_var.sum()),
        "nii_var_pct": fmt_pct(nii_var.sum() / nii_p.sum(), signe=False).lstrip("-"),
        "nii_comp_max": comp_max.lower(), "nii_comp_var": fmt(nii_var[comp_max]),
        # Dépôts
        "depots_total": fmt(d.depots[TRIM].sum(), 0),
        "depots_var_pct": fmt_pct(dep_var.sum() / d.depots[TRIM_PREC].sum()),
        "depot_hausse": dep_var.idxmax(), "depot_hausse_var": fmt(dep_var.max()),
        "depot_baisse": dep_var.idxmin(), "depot_baisse_var": fmt(abs(dep_var.min())),
        # Sensibilités
        "eve_pire_scen": eve.idxmin(), "eve_pire": fmt(eve.min()),
        "nii_pire_scen": nii_s.idxmin(), "nii_pire": fmt(nii_s.min()),
    }
