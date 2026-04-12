"""
ÉTAPE 2 — NETTOYAGE DU CSV
===========================
Input  : CSV_V2.csv (avis bruts — Capgemini, Deloitte, EY, KPMG, PwC)
Output : bigfour_clean.csv (tous les avis nettoyés)

On garde TOUT (global + français).
La colonne is_french permettra de filtrer dans l'EDA.

Lancement :
  /usr/local/bin/python3 cleaning.py
"""

import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT    = os.path.join(BASE_DIR, "CSV_V2.csv")
OUTPUT   = os.path.join(BASE_DIR, "bigfour_clean.csv")

# Les 5 cabinets attendus dans le dataset
EXPECTED_COMPANIES = ["Capgemini", "Deloitte", "EY", "KPMG", "PwC"]

# ─────────────────────────────────────────────────────────────
# ÉTAPE 1 — CHARGEMENT
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("ÉTAPE 1 — CHARGEMENT")
print("="*60)

df = pd.read_csv(INPUT, encoding="utf-8-sig")

print(f"Lignes totales  : {len(df):,}")
print(f"Colonnes        : {len(df.columns)}")
print(f"\nColonnes : {list(df.columns)}")
print(f"\nTypes :")
print(df.dtypes.to_string())

print("\nCabinets détectés dans le CSV :")
print(df.groupby("company")["rating"].count().to_string())

# Vérification que PwC est présent
missing = [c for c in EXPECTED_COMPANIES if c not in df["company"].unique()]
if missing:
    print(f"\n[WARN] Cabinets manquants : {missing}")
    print("       Relancez parse_html.py pour les inclure.")
else:
    print("\n✓ Tous les cabinets sont présents (Capgemini, Deloitte, EY, KPMG, PwC)")

# ─────────────────────────────────────────────────────────────
# ÉTAPE 2 — DOUBLONS
# Les fichiers HTML se chevauchent sur les numéros d'avis.
# On supprime les lignes identiques sur les colonnes clés.
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("ÉTAPE 2 — SUPPRESSION DES DOUBLONS")
print("="*60)

avant = len(df)
df = df.drop_duplicates(subset=["company", "date", "pros", "cons"])
apres = len(df)

print(f"Lignes avant           : {avant:,}")
print(f"Lignes après           : {apres:,}")
print(f"Doublons supprimés     : {avant - apres:,}")

# ─────────────────────────────────────────────────────────────
# ÉTAPE 3 — VALEURS MANQUANTES
# - rating manquant → ligne inutilisable, on supprime
# - pros/cons vides → remplacés par "" pour ne pas
#   casser les analyses textuelles plus tard
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("ÉTAPE 3 — VALEURS MANQUANTES")
print("="*60)

print("Valeurs manquantes par colonne :")
print(df.isnull().sum().to_string())

avant = len(df)
df = df.dropna(subset=["rating"])
print(f"\nLignes supprimées (rating manquant) : {avant - len(df):,}")

df["pros"] = df["pros"].fillna("")
df["cons"] = df["cons"].fillna("")
print("pros et cons vides → remplacés par chaîne vide ✓")

# ─────────────────────────────────────────────────────────────
# ÉTAPE 4 — VÉRIFICATION DES NOTES
# La note doit être entre 1.0 et 5.0.
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("ÉTAPE 4 — VÉRIFICATION DES NOTES (1.0 → 5.0)")
print("="*60)

avant = len(df)
df = df[df["rating"].between(1.0, 5.0)]
print(f"Notes aberrantes supprimées : {avant - len(df):,}")

print("\nDistribution des notes :")
print(df["rating"].value_counts().sort_index().to_string())

print("\nNote moyenne par cabinet :")
print(df.groupby("company")["rating"].mean().round(2).to_string())

# ─────────────────────────────────────────────────────────────
# ÉTAPE 5 — CONVERSION DES DATES
# "31 mars 2024" → datetime + colonnes year et month
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("ÉTAPE 5 — CONVERSION DES DATES")
print("="*60)

MOIS_FR = {
    "janv": "01", "févr": "02", "mars": "03", "avr":  "04",
    "mai":  "05", "juin": "06", "juil": "07", "août": "08",
    "sept": "09", "oct":  "10", "nov":  "11", "déc":  "12"
}

def parse_date_fr(d):
    if not d or pd.isna(d):
        return pd.NaT
    d = str(d).strip()
    for fr, num in MOIS_FR.items():
        d = d.replace(fr + ".", num).replace(fr, num)
    try:
        return pd.to_datetime(d, format="%d %m %Y")
    except Exception:
        return pd.to_datetime(d, dayfirst=True, errors="coerce")

df["date_parsed"] = df["date"].apply(parse_date_fr)
df["year"]        = df["date_parsed"].dt.year
df["month"]       = df["date_parsed"].dt.month

ok  = df["date_parsed"].notna().sum()
nok = df["date_parsed"].isna().sum()

print(f"Dates converties   : {ok:,}")
print(f"Dates non lisibles : {nok:,}")
print(f"Période couverte   : {int(df['year'].min())} → {int(df['year'].max())}")

# ─────────────────────────────────────────────────────────────
# ÉTAPE 6 — COLONNE is_current
# "Employé actuel..." → True / "Ancien employé" → False
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("ÉTAPE 6 — STATUT EMPLOYÉ (is_current)")
print("="*60)

df["is_current"] = df["status"].str.contains("actuel", case=False, na=False)

print("Actuel vs Ancien par cabinet :")
pivot = df.groupby(["company", "is_current"])["rating"].count().unstack()
pivot.columns = ["Anciens", "Actuels"]
print(pivot.to_string())

# ─────────────────────────────────────────────────────────────
# ÉTAPE 7 — RÉSUMÉ GLOBAL VS FRANÇAIS
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("ÉTAPE 7 — GLOBAL VS FRANÇAIS (5 cabinets)")
print("="*60)

df_fr  = df[df["is_french"] == True]
df_glo = df[df["is_french"] == False]

print(f"Avis totaux   : {len(df):,}")
print(f"Avis français : {len(df_fr):,}")
print(f"Avis globaux  : {len(df_glo):,}")

print("\nNote moyenne GLOBAL par cabinet :")
print(df_glo.groupby("company")["rating"].mean().round(2).to_string())

print("\nNote moyenne FRANÇAIS par cabinet :")
print(df_fr.groupby("company")["rating"].mean().round(2).to_string())

print("\nVolume FRANÇAIS par cabinet :")
print(df_fr.groupby("company")["rating"].count().to_string())

print("\nTaux de recommandation FRANÇAIS par cabinet :")
print(df_fr.groupby("company")["recommend"].apply(
    lambda x: (x == 1).sum() / len(x) * 100
).round(1).to_string())

# ─────────────────────────────────────────────────────────────
# ÉTAPE 8 — RÉSUMÉ FINAL
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("ÉTAPE 8 — RÉSUMÉ FINAL")
print("="*60)

print(f"Lignes finales : {len(df):,}")
print(f"Colonnes       : {list(df.columns)}")

# ─────────────────────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────────────────────

df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")

print(f"\n✅ CSV propre exporté : {OUTPUT}")
print("   Prochaine étape : eda.py")