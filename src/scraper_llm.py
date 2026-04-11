"""
scraper_llm.py - Metoda 3 (bonus): Scraping adaptiv cu AI / LLM.

Aceasta este abordarea modernă, fundamentat diferită de metodele clasice:
  - NU folosim selectori CSS hardcodați (fragili la schimbări de layout)
  - Trimitem HTML-ul paginii unui model de limbaj (GPT-4o-mini sau Claude Haiku)
  - Modelul „înțelege” semantic structura paginii și extrage datele automat
  - Rezultatul vine direct în format JSON structurat

Avantaje: adaptiv (funcționează pe orice site fără a scrie selectori),
          rezistent la schimbări de layout.
Dezavantaje: cost per request (API), limitat de fereastra de context a modelului,
             mai lent decât parsarea locală.

Acest fișier demonstrează integrarea cu DOUĂ API-uri: OpenAI și Anthropic.
Studentul alege în funcție de cheia API disponibilă.
"""

import json
import logging

import requests
from bs4 import BeautifulSoup

from config import (ANTHROPIC_API_KEY, HEADERS, LLM_MAX_HTML_CHARS, LLM_MODEL_ANTHROPIC, LLM_MODEL_OPENAI,
                    OPENAI_API_KEY, REQUEST_TIMEOUT, TARGET_URL, )

logger = logging.getLogger(__name__)

# Prompt-ul trimis către LLM - instrucțiuni clare pentru extragerea datelor
# Un prompt bine scris este esențial pentru rezultate consistente
PROMPT_EXTRACTIE = """Analizează următorul HTML al unei pagini de e-commerce și extrage TOATE produsele.

Pentru fiecare produs, returnează un obiect JSON cu exact aceste câmpuri:
- "id": identificatorul unic al produsului (din URL sau atribute HTML)
- "nume": numele complet al produsului
- "pret": prețul ca număr (float), FĂRĂ simboluri monetare
- "pret_redus": prețul redus ca număr (float) sau null dacă nu există
- "descriere": descrierea produsului
- "rating": rating-ul ca număr întreg (1-5)
- "numar_review-uri": numărul de recenzii ca număr întreg
- "url": URL-ul relativ către pagina produsului

IMPORTANT:
- Prețurile TREBUIE să fie valori numerice (ex: 299.99), NU string-uri (ex: "$299.99")
- Dacă un câmp nu este disponibil, folosește null
- Returnează DOAR un array JSON valid, fără text suplimentar
- Nu include markdown, backticks sau alte formatări - doar JSON pur

HTML-ul paginii:
"""


def _curata_html(html: str) -> str:
    """
    Reduce dimensiunea HTML-ului pentru a se încadra în fereastra de context a LLM-ului.

    Modelele LLM au o limită de tokeni (context window). HTML-ul unei pagini web
    conține mult „zgomot”: scripturi, stiluri, navigare, footer - care nu sunt
    relevante pentru extragerea produselor.

    Această funcție:
      1. Elimină tag-urile <script>, <style>, <nav>, <footer> (irelevante)
      2. Păstrează doar conținutul relevant (produsele)
      3. Trunchiază la LLM_MAX_HTML_CHARS caractere

    Argumente:
        html: HTML-ul complet al paginii.

    Returnează:
        HTML-ul curățat și trunchiat.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Eliminăm elementele irelevante pentru extragerea de date
    for tag in soup.find_all(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    html_curat = str(soup)

    # Trunchiăm dacă depășește limita de caractere
    if len(html_curat) > LLM_MAX_HTML_CHARS:
        logger.warning(f"HTML trunchiat de la {len(html_curat)} la {LLM_MAX_HTML_CHARS} caractere")
        html_curat = html_curat[:LLM_MAX_HTML_CHARS]

    return html_curat


def _extrage_cu_openai(html_curat: str) -> list[dict]:
    """
    Trimite HTML-ul către API-ul OpenAI și primește produsele extrase.

    Folosim modelul GPT-4o-mini - un model rapid și ieftin, suficient de capabil
    pentru extragerea structurată de date din HTML.

    Argumente:
        html_curat: HTML-ul curățat al paginii.

    Returnează:
        Lista de produse extrase (dicționare).
    """
    # Importăm openai doar când este necesar (nu forțăm instalarea)
    from openai import OpenAI

    logger.info(f"Se trimite HTML către OpenAI ({LLM_MODEL_OPENAI})...")

    client = OpenAI(api_key=OPENAI_API_KEY)

    raspuns = client.chat.completions.create(model=LLM_MODEL_OPENAI, messages=[
        {"role": "system", "content": ("Ești un expert în extragerea de date din HTML. "
                                       "Răspunzi EXCLUSIV cu JSON valid, fără text suplimentar."), },
        {"role": "user", "content": PROMPT_EXTRACTIE + html_curat, }, ], temperature=0, )

    continut = raspuns.choices[0].message.content.strip()
    return _parseaza_raspuns_llm(continut)


def _extrage_cu_anthropic(html_curat: str) -> list[dict]:
    """
    Trimite HTML-ul către API-ul Anthropic (Claude) și primește produsele extrase.

    Folosim modelul Claude Haiku - cel mai rapid și ieftin model Claude,
    ideal pentru task-uri de extragere structurată.

    Argumente:
        html_curat: HTML-ul curățat al paginii.

    Returnează:
        Lista de produse extrase (dicționare).
    """
    # Importăm anthropic doar când este necesar
    import anthropic

    logger.info(f"Se trimite HTML către Anthropic ({LLM_MODEL_ANTHROPIC})...")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    raspuns = client.messages.create(model=LLM_MODEL_ANTHROPIC, max_tokens=4096,
                                     messages=[{"role": "user", "content": PROMPT_EXTRACTIE + html_curat, }, ],
                                     system=("Ești un expert în extragerea de date din HTML. "
                                             "Răspunzi EXCLUSIV cu JSON valid, fără text suplimentar."),
                                     temperature=0, )

    continut = raspuns.content[0].text.strip()
    return _parseaza_raspuns_llm(continut)


def _parseaza_raspuns_llm(continut: str) -> list[dict]:
    """
    Parsează răspunsul text al LLM-ului și extrage lista JSON de produse.

    LLM-urile pot returna JSON-ul înconjurat de markdown (```json ... ```).
    Această funcție curăță formatarea și parsează JSON-ul.

    Argumente:
        continut: Răspunsul text al modelului LLM.

    Returnează:
        Lista de dicționare cu produsele extrase.
    """
    # Eliminăm blocurile de cod markdown dacă există (```json ... ```)
    if "```" in continut:
        # Extragem conținutul dintre prima și ultima pereche de ```
        linii = continut.split("```")
        # Partea cu JSON este de obicei al doilea segment
        for segment in linii:
            segment = segment.strip()
            if segment.startswith("json"):
                segment = segment[4:].strip()
            if segment.startswith("["):
                continut = segment
                break

    try:
        produse = json.loads(continut)
        if isinstance(produse, list):
            logger.info(f"LLM a extras {len(produse)} produse")
            return produse
        else:
            logger.error("Răspunsul LLM nu este o listă JSON")
            return []

    except json.JSONDecodeError as e:
        logger.error(f"Eroare la parsarea JSON din răspunsul LLM: {e}")
        logger.debug(f"Conținut primit: {continut[:500]}...")
        return []


def scrape() -> list[dict]:
    """
    Funcția principală a scraper-ului LLM.

    Pipeline:
      1. Descarcă HTML-ul paginii (cu requests - nu avem nevoie de Playwright
         pentru că LLM-ul nu necesită JavaScript executat)
      2. Curăță HTML-ul (elimină scripturi, stiluri, navigare)
      3. Trimite HTML-ul curățat către API-ul LLM disponibil
      4. Parsează și returnează rezultatul

    Returnează:
        Lista de produse extrase.
    """
    # Verificăm dacă avem cel puțin o cheie API configurată
    if not OPENAI_API_KEY and not ANTHROPIC_API_KEY:
        logger.error("Nicio cheie API configurată!\n"
                     "Creați un fișier .env cu OPENAI_API_KEY sau ANTHROPIC_API_KEY.\n"
                     "Consultați .env.example pentru detalii.")
        return []

    try:
        # Pasul 1: Preluăm HTML-ul paginii
        logger.info(f"Se accesează: {TARGET_URL}")
        raspuns = requests.get(TARGET_URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        raspuns.raise_for_status()
        html = raspuns.text
        logger.info(f"HTML preluat cu succes ({len(html)} caractere)")

        # Pasul 2: Curățăm HTML-ul pentru a reduce dimensiunea
        html_curat = _curata_html(html)
        logger.info(f"HTML curățat: {len(html_curat)} caractere")

        # Pasul 3: Trimitem către LLM-ul disponibil
        # Prioritizăm OpenAI (GPT-4o-mini este mai ieftin), dar folosim Anthropic ca alternativă
        if OPENAI_API_KEY:
            produse = _extrage_cu_openai(html_curat)
        else:
            produse = _extrage_cu_anthropic(html_curat)

        return produse

    except ImportError as e:
        logger.error(f"Bibliotecă lipsă: {e}\n"
                     "Instalați cu: pip install openai  sau  pip install anthropic")
        return []

    except requests.RequestException as e:
        logger.error(f"Eroare la preluarea HTML: {e}")
        return []

    except Exception as e:
        logger.error(f"Eroare în scraper_llm: {e}")
        return []
