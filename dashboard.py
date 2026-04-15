# -*- coding: utf-8 -*-
"""
DASHBOARD STREAMLIT — Investisseur RH
Capgemini · Deloitte · EY · KPMG · PwC
Lancez : /usr/local/bin/python3 -m streamlit run dashboard.py
"""

import os
import re
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from collections import Counter
from wordcloud import WordCloud

st.set_page_config(
    page_title="Attractivité Employeur · Big Five",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

.stApp { background: #F8F8F6; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #111111; }
.block-container { padding-top: 1.2rem !important; max-width: 1400px; }
header[data-testid="stHeader"] { background: transparent; height: 0; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E8E8E4;
}
[data-testid="stSidebar"] * { color: #111111 !important; }
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #999999 !important;
}

/* ── Titres ── */
.main-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.1rem;
    font-weight: 700;
    color: #111111;
    line-height: 1.1;
    margin: 0;
}
.main-badge {
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #999999;
    margin-top: 0.3rem;
}
.sec-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: #111111;
    margin: 1.6rem 0 0.7rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.sec-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #E8E8E4;
}
.chart-caption {
    font-size: 0.75rem;
    color: #999999;
    margin-top: -0.5rem;
    margin-bottom: 0.5rem;
    line-height: 1.5;
}

/* ── KPI Cards ── */
.kpi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.75rem; margin-bottom: 1.2rem; }
.kpi {
    background: #FFFFFF;
    border: 1px solid #E8E8E4;
    border-radius: 10px;
    padding: 1rem 1.1rem;
    border-top: 3px solid var(--c);
    transition: box-shadow 0.2s;
}
.kpi:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
.kpi-name { font-size: 0.68rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #999999; margin-bottom: 0.4rem; }
.kpi-val  { font-family: 'Syne', sans-serif; font-size: 1.85rem; font-weight: 700; color: #111111; line-height: 1; }
.kpi-unit { font-size: 0.85rem; color: #CCCCCC; font-weight: 400; }
.kpi-sub  { font-size: 0.72rem; color: #AAAAAA; margin-top: 0.3rem; line-height: 1.4; }

/* ── Info boxes ── */
.ibox {
    background: #FFFFFF;
    border: 1px solid #E8E8E4;
    border-left: 3px solid #111111;
    border-radius: 0 8px 8px 0;
    padding: 0.85rem 1rem;
    font-size: 0.82rem;
    color: #444444;
    line-height: 1.65;
    margin: 0.4rem 0 0.8rem;
}
.ibox.warn  { border-left-color: #D4922A; background: #FFFBF4; }
.ibox.alert { border-left-color: #C84040; background: #FFF8F8; }
.ibox.good  { border-left-color: #3A9D6A; background: #F4FBF7; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1.5px solid #E8E8E4;
    gap: 0;
    padding: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #AAAAAA;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    border-radius: 0;
    padding: 0.65rem 1.4rem;
    border-bottom: 2px solid transparent;
    margin-bottom: -1.5px;
}
.stTabs [aria-selected="true"] {
    color: #111111 !important;
    border-bottom: 2px solid #111111 !important;
    background: transparent !important;
}

/* ── Tableaux ── */
.dataframe { font-size: 0.82rem !important; }

/* ── Recommandations ── */
.reco-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 0.8rem; }
.reco-card {
    background: #FFFFFF;
    border: 1px solid #E8E8E4;
    border-radius: 10px;
    padding: 1.3rem 1.4rem;
}
.reco-tag {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 3px 9px;
    border-radius: 4px;
    margin-bottom: 0.6rem;
}
.tag-buy   { background: #EAF7EF; color: #2D8B5C; }
.tag-watch { background: #FEF6E8; color: #B87820; }
.tag-avoid { background: #FDECEC; color: #B83030; }
.reco-name { font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 700; color: #111111; margin-bottom: 0.5rem; }
.reco-body { font-size: 0.81rem; color: #555555; line-height: 1.65; }

/* ── Footer ── */
.footer { font-size: 0.7rem; color: #CCCCCC; text-align: center; padding: 2rem 0 1rem; letter-spacing: 0.05em; }

/* ── Divider ── */
hr { border-color: #E8E8E4 !important; margin: 1rem 0 !important; }

/* ── Metrics override ── */
[data-testid="stMetric"] { background: #FFFFFF; border: 1px solid #E8E8E4; border-radius: 10px; padding: 1rem; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# DONNÉES
# ══════════════════════════════════════════════

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COLORS = {
    "Capgemini": "#0070AD",
    "Deloitte":  "#4CAF82",
    "EY":        "#888888",
    "KPMG":      "#2D5FA6",
    "PwC":       "#C74B1E",
}
COMPANIES = list(COLORS.keys())

STOPWORDS = {
    "de","le","la","les","et","en","un","une","des","du","au","aux","pas","mais",
    "très","plus","sur","par","pour","avec","que","qui","est","à","ou","ne","se",
    "ce","il","elle","ils","elles","je","on","nous","vous","dans","d","l","c",
    "j","n","s","y","m","qu","the","and","a","i","is","it","of","to","are",
    "peu","bien","assez","trop","peut","avoir","être","faire","tout","si","car",
    "dont","où","quand","aussi","même","autres","autre","cette","ces","avoir",
    "work","good","company","great","people","management","time","place","very",
}

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#444444", size=11),
    xaxis=dict(gridcolor="#F0F0EE", zerolinecolor="#F0F0EE", linecolor="#E8E8E4"),
    yaxis=dict(gridcolor="#F0F0EE", zerolinecolor="#F0F0EE", linecolor="#E8E8E4"),
    margin=dict(l=20, r=20, t=36, b=20),
)

L_H = dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.12, font=dict(size=10))
L_V = dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10))

def hex_rgba(h, a=0.12):
    h = h.lstrip("#")
    return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})"

@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(BASE_DIR, "bigfour_clean.csv.gz"), encoding="utf-8-sig", compression="gzip")
    df["date_parsed"] = pd.to_datetime(df["date_parsed"], errors="coerce")
    df["year"]        = pd.to_numeric(df["year"], errors="coerce")
    df["is_current"]  = df["is_current"].astype(bool)
    return df

def top_words(series, n=15):
    text  = " ".join(series.dropna().astype(str).tolist()).lower()
    words = re.findall(r'\b[a-zàâäéèêëîïôùûüç]{4,}\b', text)
    return Counter([w for w in words if w not in STOPWORDS]).most_common(n)

try:
    df = load_data()
except FileNotFoundError:
    st.error("Fichier bigfour_clean.csv introuvable — lancez d'abord cleaning.py")
    st.stop()

# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='padding:0.6rem 0 1.2rem'>
        <div style='font-family:Syne,sans-serif;font-size:1.05rem;font-weight:700;color:#111'>
            Attractivité RH
        </div>
        <div style='font-size:0.72rem;color:#AAAAAA;margin-top:3px'>
            Big Five du Conseil · France & Global
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    selected_companies = st.multiselect(
        "Cabinets analysés",
        options=COMPANIES,
        default=COMPANIES,
    )
    if not selected_companies:
        selected_companies = COMPANIES

    st.markdown("---")

    scope = st.radio(
        "Périmètre",
        ["Tout", "France", "Global"],
        horizontal=True,
    )

    year_min = int(df["year"].min())
    year_max = int(df["year"].max())
    year_range = st.slider("Période", year_min, year_max, (2018, year_max))

    statut = st.radio(
        "Statut employé",
        ["Tous", "Actuels", "Anciens"],
        horizontal=True,
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem;color:#CCCCCC;line-height:1.9'>
        Data Challenge<br>
        Master IMC & D5<br>
        Paris I · Panthéon-Sorbonne<br>
        Avril 2026<br><br>
        Source : Glassdoor<br>
        286 498 avis · 2008–2024
    </div>
    """, unsafe_allow_html=True)

# Filtres
dff = df[df["company"].isin(selected_companies)]
dff = dff[dff["year"].between(year_range[0], year_range[1])]
if statut == "Actuels":
    dff = dff[dff["is_current"] == True]
elif statut == "Anciens":
    dff = dff[dff["is_current"] == False]
if scope == "France":
    dff = dff[dff["is_french"] == True]
elif scope == "Global":
    dff = dff[dff["is_french"] == False]

dff_fr  = dff[dff["is_french"] == True]
dff_glo = dff[dff["is_french"] == False]

# ══════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════

c1, c2 = st.columns([4,1])
with c1:
    st.markdown('<div class="main-title">Attractivité Employeur</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-badge">Vision Investisseur RH · Glassdoor · France & Global</div>', unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div style='text-align:right;padding-top:0.4rem'>
        <div style='font-family:Syne,sans-serif;font-size:1.8rem;font-weight:700;color:#111'>{len(dff):,}</div>
        <div style='font-size:0.68rem;color:#AAAAAA;letter-spacing:0.1em;text-transform:uppercase'>avis analysés</div>
        <div style='font-size:0.75rem;color:#CCCCCC;margin-top:2px'>{len(dff_fr):,} FR · {len(dff_glo):,} Global</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# ONGLETS
# ══════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Vue d'ensemble",
    "France vs Global",
    "Analyse RH",
    "Verbatims",
    "Score Investisseur",
])

# ══════════════════════════════════════════════
# TAB 1 — VUE D'ENSEMBLE
# ══════════════════════════════════════════════

with tab1:

    # KPI
    kpi_html = '<div class="kpi-grid">'
    for company in selected_companies:
        sub  = dff[dff["company"] == company]
        note = sub["rating"].mean() if len(sub) else 0
        reco = (sub["recommend"] == 1).mean() * 100 if len(sub) else 0
        nb   = len(sub)
        c    = COLORS.get(company, "#888888")
        kpi_html += f"""
        <div class="kpi" style="--c:{c}">
            <div class="kpi-name">{company}</div>
            <div class="kpi-val">{note:.2f}<span class="kpi-unit"> /5</span></div>
            <div class="kpi-sub">{reco:.0f}% recommandent<br>{nb:,} avis</div>
        </div>"""
    kpi_html += '</div>'
    st.markdown(kpi_html, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="sec-title">Note moyenne par cabinet</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-caption">Toutes sources confondues — global et France</div>', unsafe_allow_html=True)
        means = dff.groupby("company")["rating"].mean().reindex(selected_companies)
        fig = go.Figure(go.Bar(
            x=means.index.tolist(), y=means.values.tolist(),
            marker_color=[COLORS.get(c,"#888") for c in means.index],
            marker_line_width=0,
            text=[f"{v:.2f}" for v in means.values],
            textposition="outside",
            textfont=dict(size=12, color="#111111", family="Syne"),
        ))
        fig.update_layout(**LAYOUT, yaxis_range=[0,5.5], yaxis_title="Note /5",
            showlegend=False, legend=L_V)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="sec-title">Évolution des notes 2018–2024</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-caption">Tendance annuelle — pic universel en 2022</div>', unsafe_allow_html=True)
        pivot = (dff[dff["year"] >= 2018]
                 .groupby(["year","company"])["rating"].mean().unstack())
        fig2 = go.Figure()
        for company in selected_companies:
            if company in pivot.columns:
                fig2.add_trace(go.Scatter(
                    x=pivot.index.tolist(),
                    y=pivot[company].tolist(),
                    name=company,
                    line=dict(color=COLORS.get(company,"#888"), width=2.5),
                    mode="lines+markers", marker=dict(size=5),
                ))
        fig2.update_layout(**LAYOUT, yaxis_range=[2.5,5], yaxis_title="Note moyenne",
            hovermode="x unified", legend=L_H)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="sec-title">Distribution des notes</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-caption">Répartition en % — une distribution bimodale (1★ et 5★ élevés) signale une polarisation</div>', unsafe_allow_html=True)
    dist_cols = st.columns(len(selected_companies))
    for i, company in enumerate(selected_companies):
        sub    = dff[dff["company"] == company]
        counts = sub["rating"].value_counts().sort_index()
        pct    = (counts / counts.sum() * 100).round(1)
        fig_d  = go.Figure(go.Bar(
            x=[f"{int(r)}★" for r in pct.index],
            y=pct.values.tolist(),
            marker_color=COLORS.get(company,"#888"),
            marker_line_width=0,
            text=[f"{v:.0f}%" for v in pct.values],
            textposition="outside",
            textfont=dict(size=9),
        ))
        fig_d.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#444444", size=9),
            yaxis=dict(gridcolor="#F0F0EE", range=[0,70]),
            xaxis=dict(gridcolor="rgba(0,0,0,0)"),
            margin=dict(l=5,r=5,t=28,b=5),
            title=dict(text=company, font=dict(size=10, color=COLORS.get(company,"#888"), family="Syne")),
            showlegend=False, height=195,
        )
        dist_cols[i].plotly_chart(fig_d, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 — FRANCE VS GLOBAL
# ══════════════════════════════════════════════

with tab2:

    note_fr  = dff_fr.groupby("company")["rating"].mean().reindex(selected_companies)
    note_glo = dff_glo.groupby("company")["rating"].mean().reindex(selected_companies)

    st.markdown('<div class="sec-title">Notes moyennes — France vs Global</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-caption">Barre pleine = Global · Barre transparente = France</div>', unsafe_allow_html=True)
    fig_fg = go.Figure()
    fig_fg.add_trace(go.Bar(
        name="Global", x=selected_companies,
        y=[note_glo.get(c,0) for c in selected_companies],
        marker_color=[COLORS.get(c,"#888") for c in selected_companies],
        opacity=0.95, offsetgroup=0, marker_line_width=0,
        text=[f"{note_glo.get(c,0):.2f}" for c in selected_companies],
        textposition="outside",
    ))
    fig_fg.add_trace(go.Bar(
        name="France", x=selected_companies,
        y=[note_fr.get(c,0) for c in selected_companies],
        marker_color=[COLORS.get(c,"#888") for c in selected_companies],
        opacity=0.35, offsetgroup=1,
        marker_line_color=[COLORS.get(c,"#888") for c in selected_companies],
        marker_line_width=1.5,
        text=[f"{note_fr.get(c,0):.2f}" for c in selected_companies],
        textposition="outside",
    ))
    fig_fg.update_layout(**LAYOUT, barmode="group", yaxis_range=[0,5.5],
        yaxis_title="Note /5", legend=L_H)
    st.plotly_chart(fig_fg, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown('<div class="sec-title">Écart Global → France</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-caption">Vert = les employés FR notent mieux · Rouge = ils sont plus sévères</div>', unsafe_allow_html=True)
        ecarts = {}
        for c in selected_companies:
            g = note_glo.get(c, 0) or 0
            f = note_fr.get(c, 0) or 0
            ecarts[c] = round(f - g, 2)
        fig_e = go.Figure(go.Bar(
            x=list(ecarts.keys()), y=list(ecarts.values()),
            marker_color=["#3A9D6A" if v>=0 else "#C84040" for v in ecarts.values()],
            text=[f"{v:+.2f}" for v in ecarts.values()],
            textposition="outside", marker_line_width=0,
        ))
        fig_e.add_hline(y=0, line_color="#E8E8E4", line_width=1.5)
        fig_e.update_layout(**LAYOUT, yaxis_title="Écart (FR − Global)",
            showlegend=False, legend=L_V)
        st.plotly_chart(fig_e, use_container_width=True)
        st.markdown("""<div class="ibox">
        <b>Signal clé :</b> Capgemini, seul cabinet français du panel, enregistre la plus forte chute
        entre sa note globale et sa note France (−0.27). Un cabinet qui performe moins bien
        sur son propre marché d'origine est un signal d'alerte structurel.
        </div>""", unsafe_allow_html=True)

    with col_d:
        st.markdown('<div class="sec-title">Volume d\'avis France par cabinet</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-caption">Seuil recommandé : 500 avis pour une fiabilité statistique</div>', unsafe_allow_html=True)
        vol_fr = dff_fr.groupby("company")["rating"].count().reindex(selected_companies).fillna(0)
        fig_v = go.Figure(go.Bar(
            x=vol_fr.index.tolist(), y=vol_fr.values.tolist(),
            marker_color=[COLORS.get(c,"#888") for c in vol_fr.index],
            text=[f"{int(v):,}" for v in vol_fr.values],
            textposition="outside", marker_line_width=0,
        ))
        fig_v.add_hline(y=500, line_dash="dot", line_color="#D4922A",
                        annotation_text="Seuil de fiabilité (500)",
                        annotation_font=dict(size=10, color="#D4922A"))
        fig_v.update_layout(**LAYOUT, yaxis_title="Nombre d'avis FR",
            showlegend=False, legend=L_V)
        st.plotly_chart(fig_v, use_container_width=True)
        st.markdown("""<div class="ibox warn">
        <b>Prudence :</b> Deloitte (160), EY (240) et PwC (222) sont sous le seuil de 500 avis.
        Leurs scores France sont indicatifs mais non représentatifs statistiquement.
        Seuls Capgemini (4 053) et KPMG (2 491) offrent un volume fiable.
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-title">Radar — Recommandation · Approbation PDG · Perspective commerciale</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-caption">Comparaison France (pointillé) vs Global (plein) pour chaque cabinet</div>', unsafe_allow_html=True)
    radar_cols = st.columns(len(selected_companies))
    cats = ["Recommandation", "Appro. PDG", "Perspective"]
    for i, company in enumerate(selected_companies):
        sub_fr  = dff_fr[dff_fr["company"] == company]
        sub_glo = dff_glo[dff_glo["company"] == company]

        def rv(sub):
            if len(sub) == 0: return [0,0,0]
            return [
                (sub["recommend"]==1).mean()*100,
                (sub["approve_ceo"]==1).mean()*100,
                (sub["business_outlook"]==1).mean()*100,
            ]

        vg = rv(sub_glo); vf = rv(sub_fr)
        c  = COLORS.get(company,"#888888")
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(
            r=vg+[vg[0]], theta=cats+[cats[0]], fill="toself", name="Global",
            line=dict(color=c, width=2), fillcolor=hex_rgba(c, 0.1),
        ))
        fig_r.add_trace(go.Scatterpolar(
            r=vf+[vf[0]], theta=cats+[cats[0]], fill="toself", name="France",
            line=dict(color="#111111", width=1.5, dash="dot"),
            fillcolor="rgba(17,17,17,0.04)",
        ))
        fig_r.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0,100], gridcolor="#EEEEEE",
                                tickfont=dict(size=7, color="#CCCCCC")),
                angularaxis=dict(gridcolor="#EEEEEE", tickfont=dict(size=8, color="#555555")),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#444444", size=9),
            showlegend=(i==0),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=8), orientation="h"),
            margin=dict(l=20,r=20,t=28,b=10),
            title=dict(text=company, font=dict(color=c, size=10, family="Syne")),
            height=215,
        )
        radar_cols[i].plotly_chart(fig_r, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 — ANALYSE RH
# ══════════════════════════════════════════════

with tab3:

    col_e, col_f = st.columns(2)
    note_act = dff[dff["is_current"]==True].groupby("company")["rating"].mean().reindex(selected_companies)
    note_anc = dff[dff["is_current"]==False].groupby("company")["rating"].mean().reindex(selected_companies)
    ecart_ret = (note_act - note_anc).round(2)

    with col_e:
        st.markdown('<div class="sec-title">Rétention — Actuels vs Anciens</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-caption">Un fort écart signifie que les employés partent très déçus</div>', unsafe_allow_html=True)
        fig_ret = go.Figure()
        fig_ret.add_trace(go.Bar(
            name="Actuels", x=selected_companies,
            y=[note_act.get(c,0) for c in selected_companies],
            marker_color=[COLORS.get(c,"#888") for c in selected_companies],
            opacity=1.0, offsetgroup=0, marker_line_width=0,
            text=[f"{note_act.get(c,0):.2f}" for c in selected_companies],
            textposition="outside",
        ))
        fig_ret.add_trace(go.Bar(
            name="Anciens", x=selected_companies,
            y=[note_anc.get(c,0) for c in selected_companies],
            marker_color=[COLORS.get(c,"#888") for c in selected_companies],
            opacity=0.35, offsetgroup=1,
            marker_line_color=[COLORS.get(c,"#888") for c in selected_companies],
            marker_line_width=1.5,
            text=[f"{note_anc.get(c,0):.2f}" for c in selected_companies],
            textposition="outside",
        ))
        fig_ret.update_layout(**LAYOUT, barmode="group", yaxis_range=[0,5.5],
            yaxis_title="Note /5", legend=L_H)
        st.plotly_chart(fig_ret, use_container_width=True)

    with col_f:
        st.markdown('<div class="sec-title">Risque de rétention</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-caption">Seuil critique à 0.30 pts — au-delà, le turnover devient coûteux</div>', unsafe_allow_html=True)
        colors_r = ["#C84040" if v>=0.35 else "#D4922A" if v>=0.2 else "#3A9D6A"
                    for v in ecart_ret.fillna(0).values]
        fig_risk = go.Figure(go.Bar(
            x=ecart_ret.fillna(0).values.tolist(),
            y=ecart_ret.index.tolist(),
            orientation="h",
            marker_color=colors_r,
            text=[f"{v:.2f} pts" for v in ecart_ret.fillna(0).values],
            textposition="outside", marker_line_width=0,
        ))
        fig_risk.add_vline(x=0.3, line_dash="dot", line_color="#C84040",
                           annotation_text="Seuil critique (0.30)",
                           annotation_font=dict(size=9, color="#C84040"))
        fig_risk.update_layout(**LAYOUT, xaxis_title="Écart de note (Actuels − Anciens)",
            showlegend=False, legend=L_V)
        st.plotly_chart(fig_risk, use_container_width=True)
        st.markdown("""<div class="ibox alert">
        <b>Capgemini dépasse largement le seuil critique (0.43 pts).</b> Les employés qui quittent
        le cabinet le font avec une note 0.43 points inférieure à ceux qui restent —
        signe d'un désenchantement profond et d'un risque image employeur durable.
        </div>""", unsafe_allow_html=True)

    col_g, col_h = st.columns(2)

    with col_g:
        st.markdown('<div class="sec-title">Taux de recommandation — France</div>', unsafe_allow_html=True)
        reco_fr = dff_fr.groupby("company")["recommend"].apply(
            lambda x: (x==1).sum()/len(x)*100 if len(x)>0 else 0
        ).reindex(selected_companies)
        fig_rc = go.Figure(go.Bar(
            x=reco_fr.index.tolist(), y=reco_fr.values.tolist(),
            marker_color=[COLORS.get(c,"#888") for c in reco_fr.index],
            text=[f"{v:.0f}%" for v in reco_fr.values],
            textposition="outside", marker_line_width=0,
        ))
        fig_rc.update_layout(**LAYOUT, yaxis_range=[0,115], yaxis_title="%",
            showlegend=False, legend=L_V)
        st.plotly_chart(fig_rc, use_container_width=True)

    with col_h:
        st.markdown('<div class="sec-title">Approbation du PDG — France</div>', unsafe_allow_html=True)
        appro = dff_fr.groupby("company")["approve_ceo"].apply(
            lambda x: (x==1).sum()/len(x)*100 if len(x)>0 else 0
        ).reindex(selected_companies)
        fig_ap = go.Figure(go.Bar(
            x=appro.index.tolist(), y=appro.values.tolist(),
            marker_color=[COLORS.get(c,"#888") for c in appro.index],
            text=[f"{v:.0f}%" for v in appro.values],
            textposition="outside", marker_line_width=0,
        ))
        fig_ap.update_layout(**LAYOUT, yaxis_range=[0,115], yaxis_title="%",
            showlegend=False, legend=L_V)
        st.plotly_chart(fig_ap, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 — VERBATIMS
# ══════════════════════════════════════════════

with tab4:

    st.markdown('<div class="sec-title">Analyse NLP des verbatims — Avis France</div>', unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    selected_co_nlp = col_s1.selectbox("Cabinet", options=selected_companies)
    col_type = col_s2.radio("Type d'avis", ["Avantages", "Inconvénients"], horizontal=True)
    col_key  = "pros" if col_type == "Avantages" else "cons"
    cmap     = "Blues" if col_key == "pros" else "Reds"

    sub_nlp = dff_fr[dff_fr["company"] == selected_co_nlp]
    col_wc, col_top = st.columns([3, 2])

    with col_wc:
        st.markdown(f'<div class="chart-caption">Nuage de mots — {selected_co_nlp} · {col_type} · Avis France</div>', unsafe_allow_html=True)
        text_wc = " ".join(sub_nlp[col_key].dropna().astype(str).tolist())
        if text_wc.strip():
            wc = WordCloud(
                width=900, height=400,
                background_color="#F8F8F6",
                stopwords=STOPWORDS, max_words=60,
                colormap=cmap, prefer_horizontal=0.85,
            ).generate(text_wc)
            fig_wc, ax_wc = plt.subplots(figsize=(10,4.5))
            fig_wc.patch.set_facecolor("#F8F8F6")
            ax_wc.imshow(wc, interpolation="bilinear")
            ax_wc.axis("off")
            st.pyplot(fig_wc)
            plt.close()

    with col_top:
        st.markdown('<div class="chart-caption">Top 12 mots les plus fréquents</div>', unsafe_allow_html=True)
        words = top_words(sub_nlp[col_key], n=12)
        if words:
            w_df = pd.DataFrame(words, columns=["Mot","Occurrences"])
            fig_bar = go.Figure(go.Bar(
                x=w_df["Occurrences"].tolist(), y=w_df["Mot"].tolist(),
                orientation="h",
                marker_color=COLORS.get(selected_co_nlp,"#888"),
                marker_line_width=0,
            ))
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#444444", size=11),
                yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
                xaxis=dict(gridcolor="#F0F0EE"),
                margin=dict(l=10,r=10,t=10,b=10),
                showlegend=False, height=370,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown('<div class="sec-title">Comparaison des inconvénients — tous cabinets</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-caption">Les mots dominants dans les CONS révèlent les risques RH structurels de chaque cabinet</div>', unsafe_allow_html=True)
    nlp_cols = st.columns(len(selected_companies))
    for i, company in enumerate(selected_companies):
        sub   = dff_fr[dff_fr["company"] == company]
        words = top_words(sub["cons"], n=7)
        if words:
            w_df = pd.DataFrame(words, columns=["Mot","N"])
            fig_nl = go.Figure(go.Bar(
                x=w_df["N"].tolist(), y=w_df["Mot"].tolist(),
                orientation="h",
                marker_color=COLORS.get(company,"#888"),
                marker_line_width=0,
            ))
            fig_nl.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#444444", size=9),
                yaxis=dict(autorange="reversed", gridcolor="rgba(0,0,0,0)"),
                xaxis=dict(gridcolor="#F0F0EE"),
                margin=dict(l=5,r=5,t=26,b=5),
                title=dict(text=company, font=dict(color=COLORS.get(company,"#888"), size=10, family="Syne")),
                showlegend=False, height=235,
            )
            nlp_cols[i].plotly_chart(fig_nl, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 5 — SCORE INVESTISSEUR
# ══════════════════════════════════════════════

with tab5:

    st.markdown('<div class="sec-title">Méthodologie du score</div>', unsafe_allow_html=True)
    st.markdown("""<div class="ibox">
    <b>Score synthétique = Note moyenne (40%) + Taux de recommandation (30%) + Approbation PDG (30%)</b><br>
    Calculé indépendamment sur les avis globaux et les avis France.
    Le score France est la référence pour un investisseur ciblant le marché hexagonal.
    Le classement global s'inverse par rapport au classement France — signal fort sur la perception locale.
    </div>""", unsafe_allow_html=True)

    def compute_score(data):
        if len(data) == 0: return pd.DataFrame()
        s = data.groupby("company").agg(
            Avis        = ("rating",           "count"),
            Note        = ("rating",           "mean"),
            Reco        = ("recommend",        lambda x: (x==1).mean()*100),
            Appro_PDG   = ("approve_ceo",      lambda x: (x==1).mean()*100),
            Perspective = ("business_outlook", lambda x: (x==1).mean()*100),
        ).round(2)
        s["Score"] = (s["Note"]*0.4 + s["Reco"]/100*5*0.3 + s["Appro_PDG"]/100*5*0.3).round(2)
        return s.sort_values("Score", ascending=False)

    col_s1, col_s2 = st.columns(2)
    sg = compute_score(dff_glo)
    sf = compute_score(dff_fr)

    with col_s1:
        st.markdown('<div class="sec-title">Score Global</div>', unsafe_allow_html=True)
        if not sg.empty:
            sg_d = sg[sg.index.isin(selected_companies)]
            fig_sg = go.Figure(go.Bar(
                x=sg_d.index.tolist(), y=sg_d["Score"].tolist(),
                marker_color=[COLORS.get(c,"#888") for c in sg_d.index],
                text=[f"{v:.2f}" for v in sg_d["Score"].values],
                textposition="outside", marker_line_width=0,
            ))
            fig_sg.update_layout(**LAYOUT, yaxis_range=[0,4], yaxis_title="Score /5",
                showlegend=False, legend=L_V)
            st.plotly_chart(fig_sg, use_container_width=True)

    with col_s2:
        st.markdown('<div class="sec-title">Score France — référence investisseur</div>', unsafe_allow_html=True)
        if not sf.empty:
            sf_d = sf[sf.index.isin(selected_companies)]
            fig_sf = go.Figure(go.Bar(
                x=sf_d.index.tolist(), y=sf_d["Score"].tolist(),
                marker_color=[COLORS.get(c,"#888") for c in sf_d.index],
                text=[f"{v:.2f}" for v in sf_d["Score"].values],
                textposition="outside", marker_line_width=0,
            ))
            fig_sf.update_layout(**LAYOUT, yaxis_range=[0,4], yaxis_title="Score /5",
                showlegend=False, legend=L_V)
            st.plotly_chart(fig_sf, use_container_width=True)

    st.markdown('<div class="sec-title">Tableau détaillé — France</div>', unsafe_allow_html=True)
    if not sf.empty:
        sf_display = sf[sf.index.isin(selected_companies)][
            ["Avis","Note","Reco","Appro_PDG","Perspective","Score"]
        ].copy()
        sf_display.columns = ["Avis FR","Note /5","Recommandation %","Appro. PDG %","Perspective %","Score /5"]
        st.dataframe(
            sf_display.style
                .highlight_max(subset=["Score /5"], color="#EAF7EF")
                .highlight_min(subset=["Score /5"], color="#FDECEC")
                .format({
                    "Note /5":"{:.2f}",
                    "Recommandation %":"{:.1f}",
                    "Appro. PDG %":"{:.1f}",
                    "Perspective %":"{:.1f}",
                    "Score /5":"{:.2f}",
                }),
            use_container_width=True,
        )

    st.markdown('<div class="sec-title">Recommandation Investisseur</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="reco-grid">
        <div class="reco-card">
            <div class="reco-tag tag-buy">Investir</div>
            <div class="reco-name">KPMG</div>
            <div class="reco-body">
                Meilleure note France (3.79), volume d'avis solide (2 491), écart de rétention
                très faible (0.17 pts). Notes stables entre 2019 et 2024. Ambiance et formation
                plébiscitées dans les verbatims français. Cabinet le plus cohérent entre
                performance globale et performance locale.
            </div>
        </div>
        <div class="reco-card">
            <div class="reco-tag tag-watch">Surveiller</div>
            <div class="reco-name">EY · Deloitte · PwC</div>
            <div class="reco-body">
                Bons scores globaux mais volume France insuffisant pour conclure (160 à 240 avis).
                Work-life balance identifié comme point faible récurrent dans les verbatims.
                Deloitte affiche la meilleure stabilité temporelle. À réévaluer dès qu'un
                volume d'avis France suffisant est disponible.
            </div>
        </div>
        <div class="reco-card">
            <div class="reco-tag tag-avoid">Éviter</div>
            <div class="reco-name">Capgemini</div>
            <div class="reco-body">
                Note France la plus basse (3.52), écart de rétention critique (0.43 pts),
                le mot "salaire" cité 957 fois dans les inconvénients. Tendance baissière
                depuis 2022. Paradoxe majeur : seul cabinet français du panel,
                il termine dernier sur son propre marché d'origine.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div class="footer">
Data Challenge · Master IMC & D5 · Paris I Panthéon-Sorbonne · Avril 2026
&nbsp;·&nbsp; Données : Glassdoor
&nbsp;·&nbsp; Python · Pandas · Plotly · Streamlit
</div>
""", unsafe_allow_html=True)
