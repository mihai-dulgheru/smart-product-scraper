"""
parser.py - Funcții de parsing și curățare a datelor extrase.

Acest modul transformă datele brute (string-uri HTML) în date curate și structurate.
Exemplu: "$299.99" → 299.99 (float), "14 reviews" → 14 (int).

În pipeline-ul Big Data, acest pas corespunde etapei de PROCESARE / CURĂȚARE.
"""

import logging
import re

logger = logging.getLogger(__name__)


def curata_pret(pret_brut: str) -> float | None:
    """
    Convertește un string de preț într-o valoare numerică (float).

    Elimină simboluri monetare ($, €, lei, RON, USD) și separatori de mii,
    apoi convertește rezultatul la float.

    Exemple:
        "$299.99"   → 299.99
        "1,299.00"  → 1299.0
        "299,99 lei" → 299.99
        ""          → None

    Argumente:
        pret_brut: String-ul brut al prețului, extras din HTML.

    Returnează:
        Valoarea numerică a prețului (float) sau None dacă conversia eșuează.
    """
    if not pret_brut or not pret_brut.strip():
        return None

    try:
        # Eliminăm simboluri monetare și spații
        pret_curat = pret_brut.strip()
        pret_curat = re.sub(r"[$ €]", "", pret_curat)
        pret_curat = re.sub(r"\b(lei|RON|USD|EUR)\b", "", pret_curat, flags=re.IGNORECASE)
        pret_curat = pret_curat.strip()

        # Detectăm formatul european (1.299,99) vs. american (1,299.99)
        # Dacă virgula apare după punct → format european (ex: 1.299,99)
        if re.search(r"\.\d{3},", pret_curat):
            # Format european: punct = separator mii, virgulă = decimal
            pret_curat = pret_curat.replace(".", "").replace(",", ".")
        elif "," in pret_curat and "." not in pret_curat:
            # Virgulă fără punct → virgula este separator zecimal (ex: 299,99)
            pret_curat = pret_curat.replace(",", ".")
        else:
            # Format american sau deja curat: virgulă = separator mii
            pret_curat = pret_curat.replace(",", "")

        return float(pret_curat)

    except (ValueError, AttributeError) as e:
        logger.warning(f"Nu s-a putut converti prețul '{pret_brut}': {e}")
        return None


def extrage_rating(element_rating) -> int:
    """
    Extrage valoarea numerică a rating-ului dintr-un element HTML.

    Pe webscraper.io, rating-ul este stocat ca atribut data-rating pe un element <p>.
    Exemplu: <p data-rating="3"> → 3

    Argumente:
        element_rating: Elementul BeautifulSoup care conține atributul data-rating.

    Returnează:
        Rating-ul ca număr întreg (1-5) sau 0 dacă nu poate fi extras.
    """
    if element_rating is None:
        return 0

    try:
        return int(element_rating.get("data-rating", 0))
    except (ValueError, TypeError):
        return 0


def extrage_review_count(element_review) -> int:
    """
    Extrage numărul de review-uri dintr-un element HTML.

    Exemplu: <span itemprop="reviewCount">14</span> → 14

    Argumente:
        element_review: Elementul BeautifulSoup cu textul numărului de recenzii.

    Returnează:
        Numărul de review-uri (int) sau 0 dacă nu poate fi extras.
    """
    if element_review is None:
        return 0

    try:
        return int(element_review.get_text(strip=True))
    except (ValueError, TypeError):
        return 0


def extrage_id_produs(url_produs: str) -> str:
    """
    Extrage ID-ul produsului din URL-ul paginii de produs.

    Pe webscraper.io, URL-urile au formatul:
        /test-sites/e-commerce/allinone/product/60
    ID-ul este ultima componentă din cale (60).

    Argumente:
        url_produs: URL-ul relativ sau absolut al paginii de produs.

    Returnează:
        ID-ul produsului ca string (ex: "60") sau "necunoscut".
    """
    if not url_produs:
        return "necunoscut"

    # Extragem ultima componentă numerică din URL
    match = re.search(r"/product/(\d+)", url_produs)
    if match:
        return match.group(1)

    # Fallback: ultima parte din URL
    parti = url_produs.rstrip("/").split("/")
    return parti[-1] if parti else "necunoscut"


def construieste_url_complet(url_relativ: str, base_url: str) -> str:
    """
    Transformă un URL relativ în URL absolut.

    Exemplu:
        "/test-sites/e-commerce/allinone/product/60"
        → "https://webscraper.io/test-sites/e-commerce/allinone/product/60"

    Argumente:
        url_relativ: Calea relativă extrasă din atributul href.
        base_url: URL-ul de bază al site-ului.

    Returnează:
        URL-ul complet (absolut).
    """
    if not url_relativ:
        return ""

    if url_relativ.startswith("http"):
        return url_relativ

    # Extragem domeniul din base_url
    # "https://webscraper.io/test-sites/..." → "https://webscraper.io"
    from urllib.parse import urljoin
    domeniu = re.match(r"(https?://[^/]+)", base_url)
    if domeniu:
        return urljoin(domeniu.group(1), url_relativ)

    return url_relativ


def valideaza_produs(produs: dict) -> bool:
    """
    Verifică dacă un produs extras conține datele minime necesare.

    Un produs este considerat valid dacă are cel puțin un nume și un preț.
    Această funcție previne salvarea de date incomplete sau corupte.

    Argumente:
        produs: Dicționarul cu datele produsului.

    Returnează:
        True dacă produsul este valid, False altfel.
    """
    if not produs.get("nume"):
        logger.warning(f"Produs fără nume: {produs}")
        return False

    if produs.get("pret") is None:
        logger.warning(f"Produs fără preț: {produs.get('nume', 'N/A')}")
        return False

    return True
