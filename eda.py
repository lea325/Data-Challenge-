"""
ÉTAPE 3 — EDA (Exploratory Data Analysis)
==========================================
Input  : bigfour_clean.csv (286,498 avis)
Output : graphiques PNG + insights dans le terminal

5 cabinets : Capgemini, Deloitte, EY, KPMG, PwC

Analyse sur 2 niveaux :
  - GLOBAL  : tous les avis (puissance statistique)
  - FRANÇAIS: is_french=True (pertinence marché France)

Lancement :
  /usr/local/bin/python3 eda.py
"""

import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from collections import Counter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT    = os.path.join(BASE_DIR, "bigfour_clean.csv")

# ── PwC ajouté ──
COLORS = {
    "Capgemini": "#0070AD",
    "Deloitte":  "#86BC25",
    "EY":        "#2E2E38",
    "KPMG":      "#00338D",
    "PwC":       "#D04A02",
}
COMPANIES = list(COLORS.keys())

def savefig(name):
    path = os.path.join(BASE_DIR, name)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ {name}")

def bar_colors(index):
    return [COLORS.get(c, "#888") for c in index]

# ─────────────────────────────────────────────────────────────
# CHARGEMENT
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("CHARGEMENT")
print("="*60)

df     = pd.read_csv(INPUT, encoding="utf-8-sig")
df_fr  = df[df["is_french"] == True].copy()
df_glo = df[df["is_french"] == False].copy()

print(f"Total   : {len(df):,}")
print(f"Français: {len(df_fr):,}")
print(f"Global  : {len(df_glo):,}")

print("\nVolume par cabinet :")
print(df.groupby("company")["rating"].count().to_string())

# ─────────────────────────────────────────────────────────────
# EDA 1 — NOTES MOYENNES GLOBAL VS FRANÇAIS
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("EDA 1 — NOTES MOYENNES GLOBAL VS FRANÇAIS")
print("="*60)

note_glo = df_glo.groupby("company")["rating"].mean().round(2)
note_fr  = df_fr.groupby("company")["rating"].mean().round(2)

print("Global :")
print(note_glo.sort_values(ascending=False).to_string())
print("\nFrançais :")
print(note_fr.sort_values(ascending=False).to_string())

x = np.arange(len(COMPANIES))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 6))
bars1 = ax.bar(x - width/2, [note_glo.get(c, 0) for c in COMPANIES],
               width, label="Global", color=[COLORS[c] for c in COMPANIES], alpha=0.9)
bars2 = ax.bar(x + width/2, [note_fr.get(c, 0) for c in COMPANIES],
               width, label="Français", color=[COLORS[c] for c in COMPANIES], alpha=0.4,
               edgecolor=[COLORS[c] for c in COMPANIES], linewidth=2)

ax.set_ylim(0, 5)
ax.set_ylabel("Note moyenne /5")
ax.set_title("Note moyenne — Global vs Français (5 cabinets)", fontsize=14, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(COMPANIES)
ax.legend()
ax.spines[["top","right"]].set_visible(False)

for bar in list(bars1) + list(bars2):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.05,
            f"{bar.get_height():.2f}", ha="center", fontsize=9, fontweight="bold")

savefig("eda1_notes_global_vs_fr.png")

# ─────────────────────────────────────────────────────────────
# EDA 2 — DISTRIBUTION DES NOTES PAR CABINET
# Grille 2x3 pour accueillir les 5 cabinets
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("EDA 2 — DISTRIBUTION DES NOTES")
print("="*60)

fig, axes = plt.subplots(2, 3, figsize=(15, 8))
axes = axes.flatten()

for i, company in enumerate(COMPANIES):
    sub    = df[df["company"] == company]
    counts = sub["rating"].value_counts().sort_index()
    pct    = counts / counts.sum() * 100
    axes[i].bar(pct.index, pct.values, color=COLORS[company], edgecolor="white")
    axes[i].set_title(company, fontsize=13, fontweight="bold")
    axes[i].set_xlabel("Note")
    axes[i].set_ylabel("% d'avis")
    axes[i].set_ylim(0, 60)
    axes[i].spines[["top","right"]].set_visible(False)
    for x_val, y_val in zip(pct.index, pct.values):
        axes[i].text(x_val, y_val+0.5, f"{y_val:.0f}%", ha="center", fontsize=9)
    note_moy = sub["rating"].mean()
    print(f"{company}: note moy={note_moy:.2f} | 5★={pct.get(5.0,0):.0f}% | 1★={pct.get(1.0,0):.0f}%")

# Cacher la 6ème case vide
axes[5].set_visible(False)

plt.suptitle("Distribution des notes par cabinet (Global)", fontsize=14, fontweight="bold")
savefig("eda2_distribution_notes.png")

# ─────────────────────────────────────────────────────────────
# EDA 3 — ÉVOLUTION DES NOTES DANS LE TEMPS
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("EDA 3 — ÉVOLUTION DES NOTES DANS LE TEMPS")
print("="*60)

df["year"] = pd.to_numeric(df["year"], errors="coerce")
pivot = (df[df["year"] >= 2015]
         .groupby(["year", "company"])["rating"]
         .mean().unstack().round(2))

print(pivot.to_string())

fig, ax = plt.subplots(figsize=(12, 6))
for company in COMPANIES:
    if company in pivot.columns:
        ax.plot(pivot.index, pivot[company], marker="o", lw=2.5,
                label=company, color=COLORS[company])
        last_year = pivot[company].dropna().index[-1]
        last_val  = pivot[company].dropna().iloc[-1]
        ax.annotate(f"{last_val:.2f}", xy=(last_year, last_val),
                    xytext=(5, 0), textcoords="offset points",
                    fontsize=9, color=COLORS[company], fontweight="bold")

ax.set_ylim(2, 5)
ax.set_ylabel("Note moyenne")
ax.set_title("Évolution des notes (2015-2024) — 5 cabinets", fontsize=14, fontweight="bold")
ax.legend()
ax.spines[["top","right"]].set_visible(False)
savefig("eda3_evolution_temps.png")

# ─────────────────────────────────────────────────────────────
# EDA 4 — TAUX DE RECOMMANDATION
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("EDA 4 — TAUX DE RECOMMANDATION")
print("="*60)

for scope, data in [("Global", df_glo), ("Français", df_fr)]:
    reco = data.groupby("company")["recommend"].apply(
        lambda x: (x == 1).sum() / len(x) * 100
    ).round(1)
    print(f"\n{scope} :")
    print(reco.sort_values(ascending=False).to_string())

reco_fr = df_fr.groupby("company")["recommend"].apply(
    lambda x: (x == 1).sum() / len(x) * 100
).round(1).sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(reco_fr.index, reco_fr.values,
              color=bar_colors(reco_fr.index), edgecolor="white", width=0.5)
ax.set_ylim(0, 100)
ax.set_ylabel("% recommandent")
ax.set_title("Taux de recommandation — Avis Français (5 cabinets)", fontsize=14, fontweight="bold")
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.spines[["top","right"]].set_visible(False)
for bar, val in zip(bars, reco_fr.values):
    ax.text(bar.get_x()+bar.get_width()/2, val+1,
            f"{val:.0f}%", ha="center", fontweight="bold", fontsize=12)
savefig("eda4_recommandation_fr.png")

# ─────────────────────────────────────────────────────────────
# EDA 5 — ACTUELS VS ANCIENS
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("EDA 5 — ACTUELS VS ANCIENS EMPLOYÉS")
print("="*60)

df["is_current"] = df["is_current"].astype(bool)
note_current = df[df["is_current"] == True].groupby("company")["rating"].mean().round(2)
note_former  = df[df["is_current"] == False].groupby("company")["rating"].mean().round(2)

print("Actuels :")
print(note_current.to_string())
print("\nAnciens :")
print(note_former.to_string())
print("\nÉcart (Actuels - Anciens) :")
print((note_current - note_former).round(2).to_string())

x = np.arange(len(COMPANIES))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(x - width/2, [note_current.get(c, 0) for c in COMPANIES],
       width, label="Actuels", color=[COLORS[c] for c in COMPANIES], alpha=0.9)
ax.bar(x + width/2, [note_former.get(c, 0) for c in COMPANIES],
       width, label="Anciens", color=[COLORS[c] for c in COMPANIES], alpha=0.4,
       edgecolor=[COLORS[c] for c in COMPANIES], linewidth=2)

ax.set_ylim(0, 5)
ax.set_ylabel("Note moyenne /5")
ax.set_title("Note moyenne : Actuels vs Anciens (5 cabinets)", fontsize=14, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(COMPANIES)
ax.legend()
ax.spines[["top","right"]].set_visible(False)
savefig("eda5_actuels_vs_anciens.png")

# ─────────────────────────────────────────────────────────────
# EDA 6 — TOP MOTS PROS/CONS (FR)
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("EDA 6 — TOP MOTS PROS/CONS (FRANÇAIS)")
print("="*60)

STOPWORDS = {
    "de","le","la","les","et","en","un","une","des","du","au","aux","pas","mais",
    "très","plus","sur","par","pour","avec","que","qui","est","à","ou","ne","se",
    "ce","il","elle","ils","elles","je","on","nous","vous","dans","d","l","c",
    "j","n","s","y","m","qu","the","and","a","i","is","it","of","to","are",
    "peu","bien","assez","trop","peut","avoir","être","faire","tout",
    "si","car","dont","où","quand","aussi","même","autres","autre","cette","ces"
}

def top_words(series, n=15):
    text  = " ".join(series.dropna().astype(str).tolist()).lower()
    words = re.findall(r'\b[a-zàâäéèêëîïôùûüç]{4,}\b', text)
    words = [w for w in words if w not in STOPWORDS]
    return Counter(words).most_common(n)

for company in COMPANIES:
    sub = df_fr[df_fr["company"] == company]
    print(f"\n{company} — TOP PROS :")
    print(top_words(sub["pros"]))
    print(f"{company} — TOP CONS :")
    print(top_words(sub["cons"]))

# ─────────────────────────────────────────────────────────────
# EDA 7 — SCORE SYNTHÉTIQUE INVESTISSEUR
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("EDA 7 — SCORE SYNTHÉTIQUE INVESTISSEUR RH")
print("="*60)

summary = df_fr.groupby("company").agg(
    Nb_avis     = ("rating",           "count"),
    Note_moy    = ("rating",           "mean"),
    Taux_reco   = ("recommend",        lambda x: (x == 1).mean() * 100),
    Appro_PDG   = ("approve_ceo",      lambda x: (x == 1).mean() * 100),
    Biz_outlook = ("business_outlook", lambda x: (x == 1).mean() * 100),
).round(2)

summary["Score_final"] = (
    summary["Note_moy"]   * 0.4 +
    summary["Taux_reco"] / 100 * 5 * 0.3 +
    summary["Appro_PDG"] / 100 * 5 * 0.3
).round(2)

summary = summary.sort_values("Score_final", ascending=False)
print(summary.to_string())

print("\nCLASSEMENT FINAL :")
for i, (company, row) in enumerate(summary.iterrows()):
    print(f"  {i+1}. {company} — Score : {row['Score_final']:.2f}/5  ({row['Nb_avis']:,} avis FR)")

# ─────────────────────────────────────────────────────────────
# INSIGHTS CLÉS
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("INSIGHTS CLÉS POUR L'ORAL")
print("="*60)
print("""
1. VOLUME FR  : Capgemini (4 053) et KPMG (2 491) dominent.
                PwC (222), EY (240), Deloitte (160) — volumes faibles, à nuancer.

2. NOTES FR   : PwC meilleur avec KPMG sur le marché français.
                Capgemini = note FR la plus basse malgré volume élevé.

3. RÉTENTION  : Écart Actuels vs Anciens → Capgemini le plus critique.
                PwC à surveiller : comparer avec KPMG.

4. ÉVOLUTION  : Pic 2022 pour tous, baisse générale 2023-2024.
                Qui résiste le mieux à la baisse = cabinet le plus solide.

5. VERBATIMS  : Mots dans les CONS FR = arguments risques pour l'oral.
                PwC FR : comparer avec les autres pour la recommandation finale.
""")

print("✅ EDA terminé — prochaine étape : dashboard Streamlit")