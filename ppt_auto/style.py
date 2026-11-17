"""Style commun à tous les graphiques : couleurs de la charte, police, grille."""
import matplotlib
matplotlib.use("Agg")      # pas de fenêtre : on génère seulement des images
import matplotlib.pyplot as plt
from cycler import cycler

VERT_CLAIR, VERT, VERT_FONCE, GRIS = "#9CC9B4", "#00915A", "#00543A", "#8C8C8C"
PALETTE = [VERT_CLAIR, VERT, VERT_FONCE, GRIS]   # ordre : T-1 puis T, etc.


def apply():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],  # 1re police dispo
        "font.size": 12,
        "axes.prop_cycle": cycler(color=PALETTE),
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.axisbelow": True,
        "grid.color": "#DDDDDD",
        "legend.frameon": False,
        "savefig.dpi": 200,
    })
