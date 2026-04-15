"""
EXERCIȚIU - Metoda 1: requests + BeautifulSoup
===============================================

Pornind de la exemplu.py, completează funcțiile de mai jos.
Rulează fișierul după fiecare modificare pentru a vedea rezultatele.

Rulare:
    pip install requests beautifulsoup4
    python examples/01_requests_beautifulsoup/exercitiu.py
"""

import requests
from bs4 import BeautifulSoup

URL = "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"
HEADERS = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/131.0.0.0 Safari/537.36")}

# ─────────────────────────────────────────────────────────────
# Descărcăm pagina (cod deja scris - nu modifica)
# ─────────────────────────────────────────────────────────────

raspuns = requests.get(URL, headers=HEADERS, timeout=30)
raspuns.raise_for_status()
soup = BeautifulSoup(raspuns.text, "html.parser")
carduri = soup.select("div.card.thumbnail")

print(f"Pagina conține {len(carduri)} produse.\n")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 1
# Extrage și afișează DOAR numele și prețul fiecărui produs.
#
# Indicii:
#   - Numele se află în atributul "title" al elementului <a class="title">
#   - Prețul se află în <h4 class="price"><span itemprop="price">
#   - Folosește card.select_one(...) pentru a găsi elementul în card
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 1: Nume și prețuri")
print("-" * 40)

for card in carduri:
    # TODO: extrage numele produsului
    nume = "???"

    # TODO: extrage prețul ca text (ex: "$295.99")
    pret = "???"

    print(f"  {nume} - {pret}")

print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 2
# Găsește și afișează produsele cu rating de 4 stele.
#
# Indicii:
#   - Rating-ul se află în atributul "data-rating" al elementului
#     <p data-rating="..."> din interiorul div.ratings
#   - Folosește int(...) pentru a converti string-ul la număr
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 2: Produse cu rating 4")
print("-" * 40)

for card in carduri:
    element_rating = card.select_one("div.ratings p[data-rating]")
    # TODO: extrage valoarea rating-ului ca int (0 dacă elementul lipsește)
    rating = 0

    element_nume = card.select_one("a.title")
    nume = element_nume.get("title", "N/A").strip() if element_nume else "N/A"

    # TODO: afișează produsul DOAR dacă rating-ul este 4
    pass

print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 3
# Calculează și afișează prețul mediu al tuturor produselor.
#
# Indicii:
#   - Extrage prețul din fiecare card
#   - Convertește "$295.99" → 295.99 cu: float(pret_text.replace("$", ""))
#   - Calculează media: sum(preturi) / len(preturi)
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 3: Preț mediu")
print("-" * 40)

preturi = []

for card in carduri:
    element_pret = card.select_one("h4.price span[itemprop='price']")
    if element_pret:
        pret_text = element_pret.get_text(strip=True)
        # TODO: convertește pret_text la float și adaugă-l în lista preturi
        pass

# TODO: calculează și afișează prețul mediu
# Exemplu de output: "Preț mediu: $499.99"
print("  Preț mediu: ???")
print()
