"""
scraper_requests.py - Metoda 1: Scraping clasic cu requests + BeautifulSoup.

Aceasta este cea mai simplă metodă de web scraping:
  1. Trimitem un HTTP GET request către server (ca un browser care accesează o pagină)
  2. Primim HTML-ul paginii ca text
  3. Parsăm HTML-ul cu BeautifulSoup și extragem datele dorite

Avantaje: rapid, consum minim de resurse, simplu de implementat.
Dezavantaje: NU funcționează pe pagini care generează conținut cu JavaScript (SPA).
"""

import logging

import requests
from bs4 import BeautifulSoup

from config import HEADERS, REQUEST_TIMEOUT, SELECTORI, TARGET_URL, BASE_URL
from parser import (construieste_url_complet, curata_pret, extrage_id_produs, extrage_rating, extrage_review_count,
                    valideaza_produs, )

logger = logging.getLogger(__name__)


def preia_html(url: str) -> str:
    """
    Descarcă conținutul HTML al unei pagini web folosind HTTP GET.

    Aceasta este echivalentul programatic al acțiunii „deschide o pagină în browser”.
    Serverul primește cererea noastră și returnează codul HTML al paginii.

    Argumente:
        url: Adresa web completă a paginii de accesat.

    Returnează:
        Conținutul HTML al paginii, ca string.

    Excepții:
        requests.RequestException: Dacă request-ul eșuează (server indisponibil,
            eroare de rețea, timeout etc.)
    """
    logger.info(f"Se accesează: {url}")

    # Trimitem request-ul HTTP GET cu headere personalizate
    raspuns = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)

    # Verificăm că serverul a răspuns cu succes (cod 200)
    # Dacă primim 404 (Not Found) sau 500 (Server Error), se aruncă o excepție
    raspuns.raise_for_status()

    logger.info(f"HTML preluat cu succes ({raspuns.status_code} OK, {len(raspuns.text)} caractere)")
    return raspuns.text


def parseaza_produse(html: str) -> list[dict]:
    """
    Extrage lista de produse din HTML-ul paginii folosind selectori CSS.

    BeautifulSoup parsează HTML-ul și creează un arbore DOM (Document Object Model)
    pe care îl putem interoga cu selectori CSS - similar cu document.querySelector()
    din JavaScript.

    Argumente:
        html: Codul HTML complet al paginii, ca string.

    Returnează:
        O listă de dicționare, fiecare conținând datele unui produs.
    """
    # Creăm obiectul BeautifulSoup care parsează HTML-ul
    # "html.parser" este parserul inclus în Python (nu necesită instalare separată)
    soup = BeautifulSoup(html, "html.parser")

    # Găsim toate cardurile de produse pe pagină
    carduri = soup.select(SELECTORI["produs"])
    logger.info(f"S-au găsit {len(carduri)} carduri de produse")

    produse = []
    for card in carduri:
        produs = _extrage_date_produs(card)
        # Validăm produsul - nu salvăm date incomplete
        if valideaza_produs(produs):
            produse.append(produs)

    logger.info(f"S-au extras {len(produse)} produse valide")
    return produse


def _extrage_date_produs(card) -> dict:
    """
    Extrage datele unui singur produs dintr-un card HTML.

    Fiecare card de produs pe webscraper.io are următoarea structură:
        <div class="card thumbnail">
            <h4 class="price"><span itemprop="price">$299.99</span></h4>
            <a class="title" href="/product/60" title="Nume complet">Nume trun...</a>
            <p class="description">Descriere completă</p>
            <div class="ratings">
                <span itemprop="reviewCount">14</span>
                <p data-rating="3">⭐⭐⭐</p>
            </div>
        </div>

    Argumente:
        card: Elementul BeautifulSoup reprezentând un card de produs.

    Returnează:
        Un dicționar cu datele curățate ale produsului.
    """
    # --- Extragem numele produsului ---
    # Atributul "title" al link-ului conține numele complet (netrunchiat)
    element_nume = card.select_one(SELECTORI["nume"])
    nume = element_nume.get("title", "").strip() if element_nume else ""

    # --- Extragem prețul ---
    element_pret = card.select_one(SELECTORI["pret"])
    pret_brut = element_pret.get_text(strip=True) if element_pret else ""
    pret = curata_pret(pret_brut)

    # --- Extragem descrierea ---
    element_descriere = card.select_one(SELECTORI["descriere"])
    descriere = element_descriere.get_text(strip=True) if element_descriere else ""

    # --- Extragem rating-ul ---
    element_rating = card.select_one(SELECTORI["rating"])
    rating = extrage_rating(element_rating)

    # --- Extragem numărul de review-uri ---
    element_review = card.select_one(SELECTORI["review_count"])
    numar_reviewuri = extrage_review_count(element_review)

    # --- Extragem URL-ul și ID-ul produsului ---
    url_relativ = element_nume.get("href", "") if element_nume else ""
    url_complet = construieste_url_complet(url_relativ, BASE_URL)
    id_produs = extrage_id_produs(url_relativ)

    return {"id": id_produs, "nume": nume, "pret": pret, "pret_redus": None,  # Acest site nu are prețuri reduse
            "descriere": descriere, "rating": rating, "numar_review-uri": numar_reviewuri, "url": url_complet, }


def scrape() -> list[dict]:
    """
    Funcția principală a scraper-ului clasic.

    Orchestrează întregul proces: preluare HTML → parsing → returnare date.
    Aceasta este funcția apelată din main.py.

    Returnează:
        Lista de produse extrase (dicționare).
    """
    try:
        html = preia_html(TARGET_URL)
        produse = parseaza_produse(html)
        return produse

    except requests.ConnectionError:
        logger.error("Eroare de conexiune. Verificați conexiunea la internet.")
        return []

    except requests.Timeout:
        logger.error(f"Timeout - serverul nu a răspuns în {REQUEST_TIMEOUT} secunde.")
        return []

    except requests.HTTPError as e:
        logger.error(f"Eroare HTTP: {e}")
        return []

    except Exception as e:
        logger.error(f"Eroare neașteptată în scraper_requests: {e}")
        return []
