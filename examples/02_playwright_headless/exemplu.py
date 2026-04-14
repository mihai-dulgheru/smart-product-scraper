"""
EXEMPLU DIDACTIC - Metoda 2: Playwright (browser headless)
===========================================================

Acest fișier demonstrează scraping-ul cu browser real (headless),
necesar pentru paginile care generează conținut cu JavaScript.

Rulare:
    pip install playwright beautifulsoup4
    playwright install chromium
    python examples/02_playwright_headless/exemplu.py

De ce Playwright și nu requests?
  → Unele site-uri (React, Angular, Vue) nu trimit HTML complet la GET.
    Trimit un HTML „schelet” + cod JavaScript care populează pagina.
    requests primește doar scheletul. Playwright execută și JavaScript-ul.
"""

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL = "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"

# ─────────────────────────────────────────────────────────────
# PASUL 1: Lansăm browserul headless și navigăm la pagină
# ─────────────────────────────────────────────────────────────

print("Pasul 1: Se lansează browserul Chromium headless...")
print("  (headless = fără interfață grafică, dar cu motor JS complet)\n")

with sync_playwright() as p:
    # Lansăm Chromium în modul headless.
    # headless=False → browserul devine vizibil (util pentru debugging).
    browser = p.chromium.launch(headless=True)

    # Un „context” izolează starea browserului (cookie-uri, localStorage).
    # Echivalentul unui profil de browser sau al unui tab în modul incognito.
    context = browser.new_context(user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                                              "Chrome/131.0.0.0 Safari/537.36"), locale="ro-RO", )

    # O „pagină” corespunde unui tab de browser.
    pagina = context.new_page()

    # ─────────────────────────────────────────────────────────────
    # PASUL 2: Navigăm și așteptăm încărcarea completă
    # ─────────────────────────────────────────────────────────────

    print("Pasul 2: Se navighează la URL și se așteaptă încărcarea...")

    # wait_until="networkidle" = așteptăm să nu mai fie request-uri HTTP active.
    # Alternativă: "domcontentloaded" (mai rapid, dar poate prinde pagina înainte
    # ca JavaScript-ul să fi populat conținutul dinamic).
    pagina.goto(URL, wait_until="networkidle", timeout=60_000)

    # Așteptăm explicit ca primul card de produs să fie prezent în DOM.
    # Aceasta garantează că JavaScript-ul a terminat de randat produsele.
    pagina.wait_for_selector("div.card.thumbnail", timeout=60_000)

    print("  → Pagina s-a încărcat complet!\n")

    # ─────────────────────────────────────────────────────────────
    # PASUL 3 (opțional): Interacțiuni cu pagina
    # ─────────────────────────────────────────────────────────────

    # Playwright poate face mult mai mult decât să citească HTML:

    # Exemplu: scroll până la sfârșitul paginii (pentru lazy loading)
    # pagina.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # Exemplu: click pe butonul „Următoarea pagină”
    # pagina.click("a.next")

    # Exemplu: completare câmp de căutare
    # pagina.fill("input[name='search']", "laptop")
    # pagina.press("input[name='search']", "Enter")

    # Exemplu: așteptare element specific (ex: spinner de încărcare dispare)
    # pagina.wait_for_selector(".loading", state="hidden")

    # ─────────────────────────────────────────────────────────────
    # PASUL 4: Extragem HTML-ul complet (după execuția JavaScript)
    # ─────────────────────────────────────────────────────────────

    print("Pasul 3: Se extrage HTML-ul final (după randare JS)...")
    html = pagina.content()
    print(f"  → HTML extras: {len(html)} caractere\n")

    # Închidem browserul pentru a elibera memoria (RAM + proces OS)
    browser.close()

# ─────────────────────────────────────────────────────────────
# PASUL 5: Parsăm HTML-ul cu BeautifulSoup (identic cu Metoda 1)
# ─────────────────────────────────────────────────────────────

print("Pasul 4: Se parsează HTML-ul cu BeautifulSoup...")

soup = BeautifulSoup(html, "html.parser")
carduri = soup.select("div.card.thumbnail")

print(f"  → S-au găsit {len(carduri)} carduri de produse\n")

produse = []

for i, card in enumerate(carduri, start=1):
    element_nume = card.select_one("a.title")
    nume = element_nume.get("title", "").strip() if element_nume else "N/A"

    element_pret = card.select_one("h4.price span[itemprop='price']")
    pret_text = element_pret.get_text(strip=True) if element_pret else "$0"
    pret = float(pret_text.replace("$", "").replace(",", ""))

    element_rating = card.select_one("div.ratings p[data-rating]")
    rating = int(element_rating.get("data-rating", 0)) if element_rating else 0

    element_review = card.select_one("span[itemprop='reviewCount']")
    numar_review = int(element_review.get_text(strip=True)) if element_review else 0

    url_relativ = element_nume.get("href", "") if element_nume else ""
    url_complet = f"https://webscraper.io{url_relativ}"

    produse.append(
        {"id": url_relativ.split("/")[-1] if url_relativ else str(i), "nume": nume, "pret": pret, "rating": rating,
         "numar_reviewuri": numar_review, "url": url_complet, })

# ─────────────────────────────────────────────────────────────
# PASUL 6: Afișăm rezultatele
# ─────────────────────────────────────────────────────────────

print(f"Pasul 5: Rezultate ({len(produse)} produse):\n")
print(f"{'─' * 60}")

for produs in produse[:3]:
    print(f"  Nume:   {produs['nume']}")
    print(f"  Preț:   ${produs['pret']:.2f}")
    print(f"  Rating: {'★' * produs['rating']}{'☆' * (5 - produs['rating'])}")
    print(f"{'─' * 60}")

if len(produse) > 3:
    print(f"\n  ... și încă {len(produse) - 3} produse.\n")

# ─────────────────────────────────────────────────────────────
# REZUMAT CONCEPTUAL
# ─────────────────────────────────────────────────────────────
#
# Comparație requests vs. Playwright:
#
#   requests                      Playwright
#   ──────────────────────────    ───────────────────────────────
#   Trimite HTTP GET              Lansează browser Chromium real
#   Primește HTML static          Execută tot JavaScript-ul
#   Nu poate face click/scroll    Poate simula orice interacțiune
#   ~0.3s per pagină              ~2-5s per pagină
#   ~5 MB RAM                     ~150 MB RAM
#
# CÂND SĂ FOLOSEȘTI PLAYWRIGHT:
#   ✓ Pagini SPA (React, Angular, Vue)
#   ✓ Conținut încărcat prin AJAX după eveniment scroll
#   ✓ Formulare care necesită completare și submit
#   ✓ Site-uri cu protecții anti-bot bazate pe execuție JS
#
# CÂND REQUESTS ESTE SUFICIENT:
#   ✓ Site-uri cu HTML static (bloguri, documentații, e-commerce clasic)
#   ✓ API-uri REST care returnează JSON direct
