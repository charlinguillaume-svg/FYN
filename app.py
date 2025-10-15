import time, re
from dataclasses import dataclass
from typing import Optional, Iterable, List, Dict
import httpx
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from parsers import dispatch_parser, extract_money

st.set_page_config(page_title="MursCommerciaux — Deploy", layout="wide")

HEADERS = {"User-Agent": "Mozilla/5.0 (+compliance; data collection for personal use)"}

@dataclass
class Listing:
    source: str
    url: str
    prix_eur: Optional[float] = None
    loyer_annuel_eur: Optional[float] = None
    charges_eur: Optional[float] = None
    taxe_fonciere_eur: Optional[float] = None
    rendement_brut_pct: Optional[float] = None
    bail: Optional[str] = None
    locataire: Optional[str] = None
    notes: Optional[str] = None

def fetch(url: str, timeout: int = 20) -> Optional[str]:
    try:
        with httpx.Client(timeout=timeout, headers=HEADERS, follow_redirects=True) as client:
            r = client.get(url)
            if r.status_code != 200:
                return None
            return r.text
    except Exception as e:
        return None

def compute_returns_row(prix, loyer, charges, taxe):
    brut=None; net=None
    if prix and loyer and prix>0:
        brut = (loyer / prix) * 100
        net = ((loyer - (charges or 0) - (taxe or 0)) / prix) * 100
    return (round(brut,2) if brut else None, round(net,2) if net else None)

st.title("🔁 Murs Commerciaux — Ready-to-deploy")
with st.sidebar:
    st.header("Paramètres")
    min_yield = st.number_input("Rendement minimum (%)", min_value=0.0, max_value=30.0, value=8.0, step=0.5)
    throttle = st.slider("Délai entre requêtes (sec)", 0.2, 5.0, 1.0, 0.1)
    st.caption("Respecte robots.txt & CGU. Colle uniquement des URLs d'annonces que tu as le droit de consulter.")

st.subheader("1) Colle des URLs (une par ligne)")
seed_text = st.text_area("URLs d'annonces", height=200, placeholder="https://...\\nhttps://...")
if seed_text.strip():
    seeds = [u.strip() for u in seed_text.splitlines() if u.strip()]
else:
    seeds = []

start = st.button("🔁 Mettre à jour maintenant")
df = pd.DataFrame(columns=["Source","URL","Prix de vente (€)","Loyer annuel HT-HC (€)","Charges locatives (€)","Taxe foncière (€)","Rendement brut (%)","Rendement net (%)","Bail","Locataire","Notes"])

if start and seeds:
    rows=[]
    for url in seeds:
        domain = re.sub(r'^https?://(www\.)?','', url).split('/')[0]
        html = fetch(url)
        if not html:
            rows.append({"Source":domain,"URL":url,"Notes":"Fetch KO"})
            continue
        parsed = dispatch_parser(domain, html)
        prix = parsed.get("prix_eur")
        loyer = parsed.get("loyer_annuel_eur")
        charges = parsed.get("charges_eur")
        taxe = parsed.get("taxe_fonciere_eur")
        brut, net = compute_returns_row(prix, loyer, charges, taxe)
        rows.append({
            "Source": domain, "URL": url, "Prix de vente (€)": prix, "Loyer annuel HT-HC (€)": loyer,
            "Charges locatives (€)": charges, "Taxe foncière (€)": taxe,
            "Rendement brut (%)": brut, "Rendement net (%)": net,
            "Bail": parsed.get("bail"), "Locataire": parsed.get("locataire"), "Notes": None
        })
        time.sleep(throttle)
    df = pd.DataFrame(rows)
    df = df[(df["Rendement brut (%)"].fillna(0) >= min_yield) | (df["Rendement net (%)"].fillna(0) >= min_yield)]
st.subheader("Résultats")
st.dataframe(df, use_container_width=True)

if not df.empty:
    st.download_button("💾 Export CSV", data=df.to_csv(index=False).encode("utf-8"), file_name="murs_filtre.csv", mime="text/csv")
    import io
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Deals")
    st.download_button("📥 Export Excel", data=out.getvalue(), file_name="murs_filtre.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
