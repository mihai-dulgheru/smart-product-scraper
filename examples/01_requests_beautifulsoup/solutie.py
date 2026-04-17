"""
SOLUȚIE - Metoda 1: requests + BeautifulSoup

Rulare:
    pip install requests beautifulsoup4
    python examples/01_requests_beautifulsoup/solutie.py
"""

import requests
from bs4 import BeautifulSoup

URL = "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"
HEADERS = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/131.0.0.0 Safari/537.36")}

raspuns = requests.get(URL, headers=HEADERS, timeout=30)
raspuns.raise_for_status()
soup = BeautifulSoup(raspuns.text, "html.parser")
carduri = soup.select("div.card.thumbnail")

print(f"Pagina conține {len(carduri)} produse.\n")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 1
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 1: Nume și prețuri")
print("-" * 40)

for card in carduri:
    element_nume = card.select_one("a.title")
    nume = element_nume.get("title", "N/A").strip() if element_nume else "N/A"

    element_pret = card.select_one("h4.price span[itemprop='price']")
    pret = element_pret.get_text(strip=True) if element_pret else "$0"

    print(f"  {nume} - {pret}")

print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 2
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 2: Produse cu rating 4")
print("-" * 40)

for card in carduri:
    element_rating = card.select_one("div.ratings p[data-rating]")
    rating = int(element_rating.get("data-rating", 0)) if element_rating else 0

    element_nume = card.select_one("a.title")
    nume = element_nume.get("title", "N/A").strip() if element_nume else "N/A"

    if rating == 4:
        print(f"  • {nume}")

print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 3
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 3: Preț mediu")
print("-" * 40)

preturi = []

for card in carduri:
    element_pret = card.select_one("h4.price span[itemprop='price']")
    if element_pret:
        pret_text = element_pret.get_text(strip=True)
        preturi.append(float(pret_text.replace("$", "").replace(",", "")))

if preturi:
    pret_mediu = sum(preturi) / len(preturi)
    print(f"  Preț mediu: ${pret_mediu:.2f}")

print()
