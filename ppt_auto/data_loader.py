"""Chargement et contrôle des données. Aucun calcul de présentation ici."""
from dataclasses import dataclass

import pandas as pd

from config import DATA_DIR, TRIM, TRIM_PREC

RENAME = {"T-1": TRIM_PREC, "T": TRIM}   # noms stables du CSV -> libellés affichés


@dataclass
class Data:
    gap: pd.DataFrame      # bucket x (trimestre, Actifs/Passifs/Gap)
    nii: pd.DataFrame      # trimestre x composante
    depots: pd.DataFrame   # produit x trimestre
    sens: pd.DataFrame     # scénario x (ΔEVE/ΔNII, trimestre)


def _read(name, **kw):
    df = pd.read_csv(DATA_DIR / name, index_col=0, **kw)
    df.index.name = None
    return df


def load() -> Data:
    gap = _read("gap.csv", header=[0, 1]).rename(columns=RENAME, level=0)
    nii = _read("nii.csv")
    depots = _read("depots.csv").rename(columns=RENAME)
    sens = _read("sens.csv", header=[0, 1]).rename(columns=RENAME, level=1)

    # Garde-fous : on s'arrête si les données n'ont pas la forme attendue
    assert gap.shape == (10, 6), f"gap.csv : {gap.shape}"
    assert nii.index[-1] == TRIM, f"nii.csv doit finir par {TRIM}, trouvé {nii.index[-1]}"
    assert list(depots.columns) == [TRIM_PREC, TRIM], f"depots.csv : {list(depots.columns)}"
    assert sens.shape == (6, 4), f"sens.csv : {sens.shape}"
    return Data(gap, nii, depots, sens)
