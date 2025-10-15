"""
parsers.py
Heuristiques / parseurs par domaine.
Ces fonctions tentent d'extraire Prix, Loyer annuel, Charges, Taxe foncière, Rendement, Bail, Locataire.
Elles sont volontairement permissives et retournent un dict de champs.
Ajoute/ajuste les selecteurs CSS ou regex selon les sites que tu veux supporter.
"""

import re
from bs4 import BeautifulSoup
from typing import Optional, Dict

def extract_money(text: str) -> Optional[float]:
    if not text:
        return None
    t = text.replace('\xa0', ' ')
    m = re.search(r'([\d\s][\d\s\.,]{2,})\s*€', t)
    if not m:
        return None
    val = m.group(1).replace(' ', '').replace('\u202f','').replace('.', '').replace(',', '.')
    try:
        return float(val)
    except:
        return None

def extract_pct(text: str) -> Optional[float]:
    if not text:
        return None
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*%', text)
    return float(m.group(1).replace(',', '.')) if m else None

def parse_murscommerciaux(html: str) -> Dict:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    # Heuristics: try some common label patterns used on murscommerciaux
    prix = None; loyer = None; rendement = None; bail = None; locataire = None; charges=None; taxe=None
    # price selectors: look for spans with euro or labels
    for sel in ['.prix', '.price', 'strong']:
        el = soup.select_one(sel)
        if el and '€' in el.get_text():
            prix = extract_money(el.get_text())
            break
    # fallback: regex
    if not prix:
        m = re.search(r'Prix(?: de vente)?[:\s]{0,6}([0-9\s\.,]+)\s*€', text, re.IGNORECASE)
        if m:
            prix = extract_money(m.group(0))
    # loyer
    m = re.search(r'(Loyer|Revenu locatif|Loyers?)[:\s]{0,10}([0-9\s\.,]+)\s*€', text, re.IGNORECASE)
    if m:
        loyer = extract_money(m.group(0))
    # rendement
    m = re.search(r'Rendement[:\s\-]{0,6}(\d+[.,]?\d*)\s*%', text, re.IGNORECASE)
    if m:
        rendement = extract_pct(m.group(1))
    # bail / locataire
    m = re.search(r'(Bail|Type de bail|Échéance bail)[\s:]{0,30}([A-Za-z0-9\s\/\-\.,]+)', text, re.IGNORECASE)
    if m:
        bail = m.group(0)[:200]
    m = re.search(r'(Locataire|Enseigne|Occupant)[:\s]{0,10}([A-Za-z0-9\-\.,\s]+)', text, re.IGNORECASE)
    if m:
        locataire = m.group(0)[:120]
    # charges / taxe
    m = re.search(r'(Charges locatives|Charges)[:\s]{0,10}([0-9\s\.,]+)\s*€', text, re.IGNORECASE)
    if m:
        charges = extract_money(m.group(0))
    m = re.search(r'(Taxe foncière|TF)[:\s]{0,10}([0-9\s\.,]+)\s*€', text, re.IGNORECASE)
    if m:
        taxe = extract_money(m.group(0))
    return {
        "prix_eur": prix, "loyer_annuel_eur": loyer, "charges_eur": charges, "taxe_fonciere_eur": taxe,
        "rendement_brut_pct": rendement, "bail": bail, "locataire": locataire
    }

def parse_seloger(html: str) -> Dict:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    prix=None; loyer=None; rendement=None; bail=None; locataire=None; charges=None; taxe=None
    # SeLoger often uses JSON-LD; try to extract price from meta
    scripts = soup.find_all("script", {"type":"application/ld+json"})
    for s in scripts:
        try:
            if 'price' in s.string:
                m = re.search(r'"price"\s*:\s*"?(?P<p>[\d\.,]+)"?', s.string)
                if m:
                    prix = extract_money(m.group(0))
                    break
        except Exception:
            pass
    # fallback regex
    m = re.search(r'Prix(?: de vente)?[:\s]{0,6}([0-9\s\.,]+)\s*€', text, re.IGNORECASE)
    if m and not prix:
        prix = extract_money(m.group(0))
    m = re.search(r'(Loyer|Revenu locatif)[:\s]{0,10}([0-9\s\.,]+)\s*€', text, re.IGNORECASE)
    if m:
        loyer = extract_money(m.group(0))
    m = re.search(r'Rendement[:\s\-]{0,6}(\d+[.,]?\d*)\s*%', text, re.IGNORECASE)
    if m:
        rendement = extract_pct(m.group(1))
    return {"prix_eur": prix, "loyer_annuel_eur": loyer, "charges_eur": charges, "taxe_fonciere_eur": taxe, "rendement_brut_pct": rendement, "bail": bail, "locataire": locataire}

def parse_leboncoin(html: str) -> Dict:
    # Leboncoin is dynamic; this heuristic uses text regex fallback
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    prix=None; loyer=None; rendement=None; charges=None; taxe=None; bail=None; locataire=None
    m = re.search(r'([0-9\s\.,]+)\s*€', text)
    if m:
        prix = extract_money(m.group(0))
    m = re.search(r'(Loyer|Revenu locatif)[:\s]{0,10}([0-9\s\.,]+)\s*€', text, re.IGNORECASE)
    if m:
        loyer = extract_money(m.group(0))
    m = re.search(r'Rendement[:\s\-]{0,6}(\d+[.,]?\d*)\s*%', text, re.IGNORECASE)
    if m:
        rendement = extract_pct(m.group(1))
    return {"prix_eur": prix, "loyer_annuel_eur": loyer, "charges_eur": charges, "taxe_fonciere_eur": taxe, "rendement_brut_pct": rendement, "bail": bail, "locataire": locataire}

def parse_bureauxlocaux(html: str) -> Dict:
    # Similar heuristics
    return parse_murscommerciaux(html)

def parse_cessionpme(html: str) -> Dict:
    # Try generic
    return parse_murscommerciaux(html)

# Dispatcher
def dispatch_parser(domain: str, html: str) -> Dict:
    domain = domain.lower()
    if 'murscommerciaux' in domain:
        return parse_murscommerciaux(html)
    if 'seloger' in domain:
        return parse_seloger(html)
    if 'leboncoin' in domain:
        return parse_leboncoin(html)
    if 'bureauxlocaux' in domain:
        return parse_bureauxlocaux(html)
    if 'cessionpme' in domain or 'cession' in domain:
        return parse_cessionpme(html)
    # default: generic fallback
    return parse_murscommerciaux(html)
