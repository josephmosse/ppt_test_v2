"""Paramètres du run : seule partie à modifier chaque trimestre."""
from pathlib import Path

TRIM = "T4 2026"            # trimestre courant (libellé affiché)
TRIM_PREC = "T3 2026"       # trimestre précédent
DATE_ARRETE = "31/12/2026"

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
TEMPLATE = ROOT / "template" / "template.pptx"
OUTPUT = ROOT / "output" / f"rapport_{TRIM.replace(' ', '_')}.pptx"
