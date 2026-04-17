"""
SOLUȚIE - Metoda 2: Playwright (browser headless)

Rulare:
    pip install playwright beautifulsoup4
    playwright install chromium
    python examples/02_playwright_headless/solutie.py
"""

from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL_LAPTOPURI = "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"
URL_TABLETE = "https://webscraper.io/test-sites/e-commerce/allinone/computers/tablets"

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 1
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

    titlu = pagina.title()
    print(f"  Titlu: {titlu}")

    html = pagina.content()
    soup = BeautifulSoup(html, "html.parser")
    carduri = soup.select("div.card.thumbnail")

    print(f"  Produse: {len(carduri)}")

    browser.close()

print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 2
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 2: Primele 3 tablete")
print("-" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    pagina = context.new_page()

    pagina.goto(URL_TABLETE, wait_until="networkidle", timeout=60_000)
    pagina.wait_for_selector("div.card.thumbnail", timeout=60_000)

    html = pagina.content()
    soup = BeautifulSoup(html, "html.parser")
    carduri = soup.select("div.card.thumbnail")

    print(f"  Tablete găsite: {len(carduri)}")
    print()

    for card in carduri[:3]:
        element_nume = card.select_one("a.title")
        nume = element_nume.get("title", "N/A").strip() if element_nume else "N/A"

        element_pret = card.select_one("h4.price span[itemprop='price']")
        pret = element_pret.get_text(strip=True) if element_pret else "$0"

        print(f"  • {nume} - {pret}")

    browser.close()

print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 3
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 3: Screenshot pagină")
print("-" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    pagina = browser.new_page()

    pagina.goto(URL_LAPTOPURI, wait_until="networkidle", timeout=60_000)
    pagina.wait_for_selector("div.card.thumbnail", timeout=60_000)

    cale_screenshot = Path(__file__).parent / "screenshot_laptopuri.png"
    pagina.screenshot(path=str(cale_screenshot))

    print(f"  Screenshot salvat: {cale_screenshot}")
    print(f"  Fișierul există: {cale_screenshot.exists()}")

    browser.close()

print()
