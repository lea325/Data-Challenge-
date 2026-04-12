"""
ÉTAPE 1 — Conversion HTML → CSV
================================
Ce script fait UNE seule chose :
parser tous les fichiers HTML et exporter un CSV brut.

Structure attendue :
  raw/
    capgemini/   reviews_*.html
    deloitte/    reviews_*.html
    ey/          reviews_*.html
    kpmg/        reviews_*.html
    pwc/         reviews_*.html
    parse_html.py  ← ce fichier

Lancement :
  /usr/local/bin/python3 parse_html.py
"""

import os
import re
import glob
import pandas as pd
from bs4 import BeautifulSoup

# ─────────────────────────────────────────────
# CHEMINS
# ─────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COMPANIES = {
    "Capgemini": os.path.join(BASE_DIR, "capgemini"),
    "Deloitte":  os.path.join(BASE_DIR, "deloitte"),
    "EY":        os.path.join(BASE_DIR, "ey"),
    "KPMG":      os.path.join(BASE_DIR, "kpmg"),
    "PwC":       os.path.join(BASE_DIR, "pwc"),
}

# ─────────────────────────────────────────────
# PARSING
# ─────────────────────────────────────────────

def parse_recommend(review_div):
    icons  = review_div.find_all("span", class_=re.compile(r"rating-icon"))
    labels = review_div.find_all("span", class_=re.compile(r"ratingTitle"))
    result = {}
    for icon, label in zip(icons, labels):
        cls_str = " ".join(icon.get("class", []))
        if "positive" in cls_str:
            val = 1
        elif "negative" in cls_str:
            val = -1
        else:
            val = 0
        result[label.text.strip()] = val
    return result


def parse_one_file(filepath, company_name):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "html.parser")

    reviews = []
    blocks = soup.find_all("div", class_=re.compile(r"reviewDetails"))

    for block in blocks:
        try:
            rating_tag       = block.find("span", class_=re.compile(r"overallRating"))
            rating           = float(rating_tag.text.replace(",", ".")) if rating_tag else None

            date_tag         = block.find("span", class_=re.compile(r"reviewDate"))
            date             = date_tag.text.strip() if date_tag else None

            title_tag        = block.find("a", {"data-test": "review-details-title-link"})
            title            = title_tag.text.strip() if title_tag else None

            employee_tag     = block.find("span", class_=re.compile(r"employee$"))
            employee         = employee_tag.text.strip() if employee_tag else None

            status_tag       = block.find("div", class_=re.compile(r"employeeDetails$"))
            status           = status_tag.text.strip() if status_tag else None

            location_tag     = block.find("span", class_=re.compile(r"location$"))
            location         = location_tag.text.strip() if location_tag else None

            pros_tag         = block.find("span", {"data-test": "review-text-pros"})
            pros             = pros_tag.text.strip() if pros_tag else ""

            cons_tag         = block.find("span", {"data-test": "review-text-cons"})
            cons             = cons_tag.text.strip() if cons_tag else ""

            recommend_data   = parse_recommend(block)
            recommend        = recommend_data.get("Recommander", None)
            approve_ceo      = recommend_data.get("Approbation du PDG", None)
            business_outlook = recommend_data.get("Perspective commerciale", None)

            filename         = os.path.basename(filepath)
            is_french        = "fr" in filename.lower()

            reviews.append({
                "company":          company_name,
                "rating":           rating,
                "date":             date,
                "title":            title,
                "employee":         employee,
                "status":           status,
                "location":         location,
                "pros":             pros,
                "cons":             cons,
                "recommend":        recommend,
                "approve_ceo":      approve_ceo,
                "business_outlook": business_outlook,
                "is_french":        is_french,
                "source_file":      filename,
            })

        except Exception:
            continue

    return reviews


def parse_company_folder(folder_path, company_name):
    html_files = sorted(glob.glob(os.path.join(folder_path, "*.html")))

    if not html_files:
        print(f"  [WARN] Aucun fichier HTML dans : {folder_path}")
        return []

    all_reviews = []
    for filepath in html_files:
        reviews = parse_one_file(filepath, company_name)
        print(f"    {os.path.basename(filepath):45s} → {len(reviews)} avis")
        all_reviews.extend(reviews)

    print(f"  ✓ {company_name} TOTAL : {len(all_reviews)} avis\n")
    return all_reviews


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\nDossier détecté : {BASE_DIR}\n")

    # Vérification des dossiers avant de commencer
    print("Vérification des dossiers :")
    for company, folder in COMPANIES.items():
        status = "OK" if os.path.isdir(folder) else "INTROUVABLE"
        print(f"  {company:12s} → {folder}  [{status}]")
    print()

    print("Parsing en cours...\n")

    all_reviews = []
    for company, folder in COMPANIES.items():
        if not os.path.isdir(folder):
            print(f"  [SKIP] {company} — dossier introuvable : {folder}\n")
            continue
        print(f"[{company}]")
        all_reviews.extend(parse_company_folder(folder, company))

    if not all_reviews:
        print("❌ Aucun avis trouvé. Vérifiez vos dossiers.")
        exit()

    df = pd.DataFrame(all_reviews)

    total   = len(df)
    fr_only = df["is_french"].sum()

    print("=" * 50)
    print(f"Total avis parsés  : {total:,}")
    print(f"Dont avis français : {fr_only:,}")
    print(f"Dont avis globaux  : {total - fr_only:,}")
    print()
    print("Volume par cabinet :")
    print(df.groupby("company")["rating"].count().to_string())
    print()
    print("Avis français par cabinet :")
    print(df[df["is_french"] == True].groupby("company")["rating"].count().to_string())
    print("=" * 50)

    # Export — même nom que votre fichier existant
    csv_path = os.path.join(BASE_DIR, "CSV_V2.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"\n✅ CSV exporté : {csv_path}")
    print("   Prochaine étape : cleaning.py")