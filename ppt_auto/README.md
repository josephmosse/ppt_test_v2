# Génération automatique du rapport ALM

## Lancer
```
python main.py
```
Sortie : `output/rapport_<trimestre>.pptx`

## Chaque trimestre
1. Déposer les CSV dans `data/`
2. Changer `TRIM`, `TRIM_PREC`, `DATE_ARRETE` dans `config.py`
3. `python main.py`

## Structure
| Fichier | Rôle |
|---|---|
| `config.py` | trimestre, chemins |
| `data_loader.py` | lecture des CSV + contrôles de forme |
| `style.py` | style commun des graphiques (couleurs, police) |
| `content.py` | **contenu métier** : tableaux, graphiques, textes |
| `engine.py` | moteur générique (ne pas toucher en temps normal) |
| `template/template.pptx` | mise en forme, faite à la main |

## Conventions dans le template (Alt+F10 > renommer)
- `table_xxx` : tableau rempli par la fonction `TABLES["table_xxx"]`
- `img_xxx` : rectangle remplacé par le graphique `CHARTS["img_xxx"]`
- `{trou}` dans n'importe quel texte : valeur `values()["trou"]`

Tableau : colonne 0 = libellés de lignes ; 1 ou 2 lignes d'en-tête (2 si colonnes MultiIndex,
cellules du niveau 1 fusionnées dans le template) ; chaque cellule contient un texte bidon
mis en forme (ex. `0`) pour que le style soit conservé.

## Ajouter une slide
1. Dans le template : créer la slide, nommer les objets (`table_...`, `img_...`), écrire les textes avec `{trous}`
2. Dans `content.py` : ajouter la fonction dans `TABLES` / `CHARTS`, les trous dans `values()`
3. Lancer : le script s'arrête avec un message clair si un objet ou un trou n'a pas de contenu

## Contrôles automatiques
- forme des CSV (`data_loader.py`)
- taille de chaque tableau du template vs données
- chaque `table_`/`img_` du template a une fonction, et inversement
- aucun `{trou}` restant dans le deck final
