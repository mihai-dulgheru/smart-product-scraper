"""
scraper_playwright.py - Metoda 2: Scraping cu browser headless (Playwright).

Diferența față de Metoda 1 (requests):
  - requests descarcă doar HTML-ul static (ce trimite serverul inițial)
  - Playwright lansează un browser REAL (Chromium), execută JavaScript-ul paginii
    și returnează HTML-ul complet randat

Când este nevoie de Playwright?
  - Când conținutul paginii este generat dinamic cu JavaScript (React, Angular, Vue)
  - Când trebuie să simulăm interacțiuni: click, scroll, completare formulare
  - Când site-ul are protecții anti-bot care verifică execuția JavaScript

Dezavantaje: mai lent (~2-5 secunde per pagină vs. ~0.3 secunde cu requests),
consum mai mare de memorie (lansează un proces de browser).
"""

import logging

from config import BASE_URL, PLAYWRIGHT_BROWSER, PLAYWRIGHT_TIMEOUT, SELECTORI, TARGET_URL
from parser import (construieste_url_complet, curata_pret, extrage_id_produs, extrage_rating, extrage_review_count,
                    valideaza_produs, )

logger = logging.getLogger(__name__)


def preia_html_playwright(url: str) -> str:
    """
    Descarcă conținutul HTML al unei pagini folosind un browser headless.

    „Headless” înseamnă că browserul rulează fără interfață grafică - nu vedeți
    nicio fereastră, dar intern execută tot ce face un browser normal:
    descarcă HTML, CSS, JS, execută scripturile și randează pagina.

    Pași:
      1. Lansăm un browser Chromium invizibil
      2. Navigăm la URL-ul dorit
      3. Așteptăm ca pagina să se încarce complet (inclusiv JavaScript)
      4. Extragem HTML-ul final (după randare)
      5. Închidem browserul

    Argumente:
        url: Adresa web a paginii de accesat.

    Returnează:
        Conținutul HTML complet al paginii (după execuția JavaScript).
    """
    # Importăm playwright aici (nu la nivel de modul) pentru a nu forța
    # instalarea Playwright dacă studentul folosește doar Metoda 1
    from playwright.sync_api import sync_playwright

    logger.info(f"Se lansează browser headless ({PLAYWRIGHT_BROWSER})...")
    logger.info(f"Se accesează: {url}")

    with sync_playwright() as p:
        # Lansăm browserul în modul headless (fără interfață grafică)
        browser = p.chromium.launch(headless=True)

        # Creăm un context de browser (echivalent cu un tab/fereastră)
        context = browser.new_context(  # Simulăm un browser real cu un User-Agent valid
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/131.0.0.0 Safari/537.36"),
            # Setăm limba și geolocația pentru a primi conținut localizat
            locale="ro-RO", )

        pagina = context.new_page()

        # Navigăm la URL și așteptăm ca rețeaua să fie inactivă
        # "networkidle" = așteptăm să nu mai fie request-uri de rețea active
        # (semn că pagina s-a încărcat complet, inclusiv datele AJAX)
        pagina.goto(url, wait_until="networkidle", timeout=PLAYWRIGHT_TIMEOUT)

        # Așteptăm explicit ca cel puțin un card de produs să apară în DOM
        pagina.wait_for_selector(SELECTORI["produs"], timeout=PLAYWRIGHT_TIMEOUT)

        # Extragem HTML-ul complet al paginii (după randare JS)
        html = pagina.content()

        logger.info(f"HTML preluat cu succes ({len(html)} caractere)")

        # Închidem browserul pentru a elibera memoria
        browser.close()

    return html


def parseaza_produse(html: str) -> list[dict]:
    """
    Extrage produsele din HTML folosind BeautifulSoup.

    Deși HTML-ul a fost preluat cu Playwright, parsarea se face tot cu
    BeautifulSoup - aceeași logică ca în Metoda 1. Diferența este doar
    în modul de obținere a HTML-ului.

    Argumente:
        html: Codul HTML complet al paginii.

    Returnează:
        Lista de dicționare cu datele produselor.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    carduri = soup.select(SELECTORI["produs"])
    logger.info(f"S-au găsit {len(carduri)} carduri de produse")

    produse = []
    for card in carduri:
        # Extragem datele din fiecare card (aceeași logică ca în scraper_requests)
        element_nume = card.select_one(SELECTORI["nume"])
        nume = element_nume.get("title", "").strip() if element_nume else ""

        element_pret = card.select_one(SELECTORI["pret"])
        pret_brut = element_pret.get_text(strip=True) if element_pret else ""
        pret = curata_pret(pret_brut)

        element_descriere = card.select_one(SELECTORI["descriere"])
        descriere = element_descriere.get_text(strip=True) if element_descriere else ""

        element_rating = card.select_one(SELECTORI["rating"])
        rating = extrage_rating(element_rating)

        element_review = card.select_one(SELECTORI["review_count"])
        numar_reviewuri = extrage_review_count(element_review)

        url_relativ = element_nume.get("href", "") if element_nume else ""
        url_complet = construieste_url_complet(url_relativ, BASE_URL)
        id_produs = extrage_id_produs(url_relativ)

        produs = {"id": id_produs, "nume": nume, "pret": pret, "pret_redus": None, "descriere": descriere,
                  "rating": rating, "numar_review-uri": numar_reviewuri, "url": url_complet, }

        if valideaza_produs(produs):
            produse.append(produs)

    logger.info(f"S-au extras {len(produse)} produse valide")
    return produse


def scrape() -> list[dict]:
    """
    Funcția principală a scraper-ului Playwright.

    Orchestrează: lansare browser → navigare → extragere HTML → parsing → date.
    Aceasta este funcția apelată din main.py când se selectează --metoda playwright.

    Returnează:
        Lista de produse extrase.
    """
    try:
        html = preia_html_playwright(TARGET_URL)
        produse = parseaza_produse(html)
        return produse

    except ImportError:
        logger.error("Playwright nu este instalat. Rulați:\n"
                     "  pip install playwright\n"
                     "  playwright install chromium")
        return []

    except Exception as e:
        logger.error(f"Eroare în scraper_playwright: {e}")
        return []
