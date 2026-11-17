"""Point d'entrée : python main.py"""
import config
import content
import style
from data_loader import load
from engine import build

if __name__ == "__main__":
    style.apply()
    data = load()
    out = build(config.TEMPLATE, config.OUTPUT, data,
                content.TABLES, content.CHARTS, content.values(data))
    print("Rapport généré :", out)
