"""
EXEMPLU DIDACTIC - Metoda 1: requests + BeautifulSoup
======================================================

Acest fișier este un exemplu minimal, care demonstrează cum funcționează scraping-ul clasic pas cu pas.

Rulare:
    pip install requests beautifulsoup4
    python examples/01_requests_beautifulsoup/exemplu.py

Site folosit: https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops
  → Site creat special pentru practică; NU are protecții anti-bot.
"""

import requests
from bs4 import BeautifulSoup

# ─────────────────────────────────────────────
# PASUL 1: Definim URL-ul și headerele HTTP
# ─────────────────────────────────────────────

URL = "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"

# User-Agent spune serverului ce browser „suntem”.
# Fără el, unele servere returnează 403 Forbidden.
HEADERS = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/131.0.0.0 Safari/537.36")}

# ─────────────────────────────────────────────
# PASUL 2: Descărcăm HTML-ul paginii
# ─────────────────────────────────────────────

print("Pasul 2: Se descarcă HTML-ul paginii...")

raspuns = requests.get(URL, headers=HEADERS, timeout=30)

# raise_for_status() aruncă o excepție dacă serverul a returnat o eroare
# (ex: 404 Not Found, 500 Internal Server Error).
# Cod 200 = OK → continuăm.
raspuns.raise_for_status()

print(f"  → Succes! Cod HTTP: {raspuns.status_code}")
print(f"  → HTML primit: {len(raspuns.text)} caractere\n")

# ─────────────────────────────────────────────
# PASUL 3: Parsăm HTML-ul cu BeautifulSoup
# ─────────────────────────────────────────────

print("Pasul 3: Se parsează HTML-ul cu BeautifulSoup...")

# BeautifulSoup transformă șirul HTML într-un arbore de obiecte Python
# pe care îl putem interoga cu selectori CSS sau metode Python.
# "html.parser" este parserul inclus în Python (alternativă: "lxml", mai rapid).
soup = BeautifulSoup(raspuns.text, "html.parser")

# Selectorul CSS "div.card.thumbnail" găsește toate elementele <div>
# care au AMBELE clase CSS: "card" și "thumbnail".
# Echivalentul JavaScript: document.querySelectorAll("div.card.thumbnail")
carduri = soup.select("div.card.thumbnail")

print(f"  → S-au găsit {len(carduri)} carduri de produse\n")

# ─────────────────────────────────────────────
# PASUL 4: Extragem datele din fiecare card
# ─────────────────────────────────────────────

print("Pasul 4: Se extrag datele din fiecare card...\n")

produse = []

for i, card in enumerate(carduri, start=1):
    # --- Numele produsului ---
    # <a class="title" href="/product/60" title="Asus VivoBook X441NA-GA190">
    #     Asus VivoBook... ← text trunchiat
    # </a>
    # Folosim atributul "title" (nu text-ul) pentru că acesta conține
    # numele COMPLET, netrunchiat de CSS.
    element_nume = card.select_one("a.title")
    nume = element_nume.get("title", "").strip() if element_nume else "N/A"

    # --- Prețul ---
    # <h4 class="price"><span itemprop="price">$295.99</span></h4>
    element_pret = card.select_one("h4.price span[itemprop='price']")
    pret_text = element_pret.get_text(strip=True) if element_pret else "$0"
    # Convertim "$295.99" → 295.99 (float)
    pret = float(pret_text.replace("$", "").replace(",", ""))

    # --- Descrierea ---
    # <p class="description">Laptop, Intel Celeron N3350 1.1GHz, ...</p>
    element_descriere = card.select_one("p.description")
    descriere = element_descriere.get_text(strip=True) if element_descriere else ""

    # --- Rating-ul ---
    # <p data-rating="3"> ← atributul data-rating conține valoarea numerică
    element_rating = card.select_one("div.ratings p[data-rating]")
    rating = int(element_rating.get("data-rating", 0)) if element_rating else 0

    # --- Numărul de review-uri ---
    # <span itemprop="reviewCount">14</span>
    element_review = card.select_one("span[itemprop='reviewCount']")
    numar_review = int(element_review.get_text(strip=True)) if element_review else 0

    # --- URL-ul produsului ---
    url_relativ = element_nume.get("href", "") if element_nume else ""
    url_complet = f"https://webscraper.io{url_relativ}"

    produs = {"id": url_relativ.split("/")[-1] if url_relativ else str(i), "nume": nume, "pret": pret,
              "descriere": descriere, "rating": rating, "numar_reviewuri": numar_review, "url": url_complet, }

    produse.append(produs)

# ─────────────────────────────────────────────
# PASUL 5: Afișăm rezultatele
# ─────────────────────────────────────────────

print(f"Pasul 5: Rezultate ({len(produse)} produse extrase):\n")
print(f"{'─' * 60}")

for produs in produse[:3]:  # Afișăm primele 3 pentru brevitate
    print(f"  ID:      {produs['id']}")
    print(f"  Nume:    {produs['nume']}")
    print(f"  Preț:    ${produs['pret']:.2f}")
    print(f"  Rating:  {'★' * produs['rating']}{'☆' * (5 - produs['rating'])} ({produs['numar_reviewuri']} recenzii)")
    print(f"  URL:     {produs['url']}")
    print(f"{'─' * 60}")

if len(produse) > 3:
    print(f"\n  ... și încă {len(produse) - 3} produse.\n")

# ─────────────────────────────────────────────
# REZUMAT CONCEPTUAL
# ─────────────────────────────────────────────
#
# Fluxul acestei metode:
#
#   Browser/requests             Server web
#       │                             │
#       │── GET /computers/laptops ──►│
#       │                             │
#       │◄── HTML static (cod 200)  ──│
#       │                             │
#   BeautifulSoup parsează HTML
#   și extrage datele cu selectori CSS
#
# AVANTAJE:
#   + Rapid (~0.3s per pagină)
#   + Consum minim de resurse
#   + Simplu de implementat
#
# DEZAVANTAJE:
#   - NU funcționează pe pagini cu conținut generat din JavaScript
#     (SPA-uri: React, Angular, Vue)
#   - Selectori CSS fragili: se sparg când site-ul modifică structura HTML
