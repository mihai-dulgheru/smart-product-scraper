"""
EXERCIȚIU - Metoda 2: Playwright (browser headless)
====================================================

Pornind de la exemplu.py, completează sarcinile de mai jos.
Fiecare exercițiu extinde exemplul de bază cu o nouă capacitate
a browserului headless.

Rulare:
    pip install playwright beautifulsoup4
    playwright install chromium
    python examples/02_playwright_headless/exercitiu.py
"""

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL_LAPTOPURI = "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"
URL_TABLETE = "https://webscraper.io/test-sites/e-commerce/allinone/computers/tablets"

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 1
# Navighează la pagina de laptopuri și numără câte produse există.
# Afișează titlul paginii (tag-ul <title>) și numărul de produse.
#
# Indicii:
#   - pagina.title() returnează titlul paginii
#   - pagina.content() returnează HTML-ul complet după execuția JS
#   - soup.select("div.card.thumbnail") găsește cardurile de produse
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 1: Titlu pagină și număr produse")
print("-" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                                              "Chrome/131.0.0.0 Safari/537.36"))
    pagina = context.new_page()

    pagina.goto(URL_LAPTOPURI, wait_until="networkidle", timeout=60_000)
    pagina.wait_for_selector("div.card.thumbnail", timeout=60_000)

    # TODO: obține titlul paginii și afișează-l
    titlu = "???"  # Hint: pagina.title()
    print(f"  Titlu: {titlu}")

    html = pagina.content()
    soup = BeautifulSoup(html, "html.parser")
    carduri = soup.select("div.card.thumbnail")

    # TODO: afișează numărul de produse găsite
    print(f"  Produse: ???")

    browser.close()

print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 2
# Navighează la pagina de tablete și extrage primele 3 produse
# (nume + preț). Compară structura HTML cu cea de la laptopuri
# - sunt identici selectori CSS?
#
# Indicii:
#   - Folosește același flux ca în exemplu.py
#   - Selectorul pentru titlu: a.title (atributul "title")
#   - Selectorul pentru preț: h4.price span[itemprop='price']
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 2: Primele 3 tablete")
print("-" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    pagina = context.new_page()

    # TODO: navighează la URL_TABLETE și așteaptă încărcarea
    # pagina.goto(...)
    # pagina.wait_for_selector(...)

    html = pagina.content()
    soup = BeautifulSoup(html, "html.parser")
    carduri = soup.select("div.card.thumbnail")

    print(f"  Tablete găsite: {len(carduri)}")
    print()

    # TODO: extrage și afișează primele 3 tablete (nume + preț)
    for card in carduri[:3]:
        nume = "???"
        pret = "???"
        print(f"  • {nume} - {pret}")

    browser.close()

print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 3
# Navighează la pagina de laptopuri și fă un screenshot.
# Salvează imaginea ca "screenshot_laptopuri.png" în același
# director cu acest fișier.
#
# Indicii:
#   - pagina.screenshot(path="calea/fisierului.png") salvează imaginea
#   - Folosește __file__ pentru a construi calea absolută:
#       from pathlib import Path
#       cale = Path(__file__).parent / "screenshot_laptopuri.png"
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 3: Screenshot pagină")
print("-" * 50)

from pathlib import Path

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    pagina = browser.new_page()

    pagina.goto(URL_LAPTOPURI, wait_until="networkidle", timeout=60_000)
    pagina.wait_for_selector("div.card.thumbnail", timeout=60_000)

    # TODO: construiește calea pentru screenshot și salvează imaginea
    cale_screenshot = Path(__file__).parent / "screenshot_laptopuri.png"
    # pagina.screenshot(path=???)

    print(f"  Screenshot salvat: {cale_screenshot}")
    print(f"  Fișierul există: {cale_screenshot.exists()}")

    browser.close()

print()
