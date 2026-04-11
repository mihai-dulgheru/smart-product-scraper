"""
main.py - Punct de intrare principal pentru Smart Product Scraper.

Acest modul orchestrează întregul pipeline de scraping:
  1. Parsează argumentele din linia de comandă (metoda de scraping, formatul de output)
  2. Încarcă variabilele de mediu din fișierul .env (chei API pentru LLM)
  3. Apelează scraper-ul selectat (requests / playwright / llm)
  4. Salvează datele extrase în formatul dorit (JSON / CSV / ambele)
  5. Afișează un rezumat în consolă

Exemple de utilizare:
    python src/main.py                          # Metoda implicită (requests), output JSON
    python src/main.py --metoda playwright      # Browser headless
    python src/main.py --metoda llm             # AI/LLM (bonus)
    python src/main.py --format toate           # Salvare JSON + CSV
    python src/main.py --metoda requests --format csv
"""

import argparse
import logging
import sys
import time
from pathlib import Path

# Adăugăm directorul src/ la PYTHONPATH pentru a permite importuri relative
# (necesar când rulăm scriptul din rădăcina proiectului: python src/main.py)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from storage import afiseaza_rezumat, salveaza_csv, salveaza_json


def configureaza_logging():
    """
    Configurează sistemul de logging pentru întreaga aplicație.

    Logging-ul este esențial pentru debugging și monitorizare:
      - INFO: mesaje despre progresul normal al execuției
      - WARNING: situații neașteptate dar netratabile ca erori
      - ERROR: erori care împiedică funcționarea normală

    Formatul include timestamp-ul, nivelul și mesajul - util pentru
    a înțelege cronologia evenimentelor la depanare.
    """
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s",
                        handlers=[logging.StreamHandler(sys.stdout)], )


def incarca_env():
    """
    Încarcă variabilele de mediu din fișierul .env (dacă există).

    Fișierul .env conține date sensibile (chei API) care NU trebuie
    incluse în codul sursă sau în Git. Biblioteca python-dotenv le
    citește și le face disponibile prin os.getenv().

    Dacă python-dotenv nu este instalat, variabilele trebuie setate
    manual în sistem (export OPENAI_API_KEY=... pe Linux/macOS).
    """
    try:
        from dotenv import load_dotenv

        # Căutăm .env în directorul rădăcină al proiectului
        env_path = Path(__file__).resolve().parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            logging.getLogger(__name__).info("Variabile de mediu încărcate din .env")
        else:
            logging.getLogger(__name__).debug("Fișierul .env nu a fost găsit (opțional)")
    except ImportError:
        # python-dotenv nu este instalat - nu este o eroare critică
        pass


def parseaza_argumente() -> argparse.Namespace:
    """
    Parsează argumentele din linia de comandă.

    Argumentele disponibile:
      --metoda: Metoda de scraping (requests, playwright, llm)
      --format: Formatul de output (json, csv, toate)

    Returnează:
        Obiect Namespace cu valorile argumentelor.
    """
    parser = argparse.ArgumentParser(description="Smart Product Scraper - Extrage date de pe site-uri e-commerce",
                                     epilog="Exemplu: python src/main.py --metoda playwright --format toate", )

    parser.add_argument("--metoda", choices=["requests", "playwright", "llm"], default="requests",
                        help="Metoda de scraping: requests (clasică), playwright (browser), llm (AI bonus). Implicit: requests", )

    parser.add_argument("--format", choices=["json", "csv", "toate"], default="json",
                        help="Formatul de output: json, csv sau toate. Implicit: json", )

    return parser.parse_args()


def selecteaza_scraper(metoda: str):
    """
    Importă și returnează funcția scrape() corespunzătoare metodei alese.

    Folosim import dinamic (lazy import) pentru a nu încărca toate
    dependințele la pornire - de exemplu, Playwright nu trebuie
    instalat dacă studentul folosește doar metoda requests.

    Argumente:
        metoda: Numele metodei ("requests", "playwright" sau "llm").

    Returnează:
        Funcția scrape() a modulului corespunzător.
    """
    if metoda == "requests":
        import scraper_requests
        return scraper_requests.scrape

    elif metoda == "playwright":
        import scraper_playwright
        return scraper_playwright.scrape

    elif metoda == "llm":
        import scraper_llm
        return scraper_llm.scrape

    else:
        raise ValueError(f"Metodă necunoscută: {metoda}")


def salveaza_date(produse: list[dict], format_output: str):
    """
    Salvează produsele extrase în formatul specificat.

    Argumente:
        produse: Lista de produse de salvat.
        format_output: "json", "csv" sau "toate".
    """
    if format_output in ("json", "toate"):
        salveaza_json(produse)

    if format_output in ("csv", "toate"):
        salveaza_csv(produse)


def main():
    """
    Funcția principală - orchestrează întregul pipeline de scraping.

    Pipeline-ul Big Data în miniatură:
      1. CONFIGURARE → logging, variabile de mediu, argumente CLI
      2. COLECTARE   → scraper-ul ales descarcă și parsează datele
      3. STOCARE     → datele sunt salvate în JSON/CSV
      4. RAPORTARE   → rezumat afișat în consolă
    """
    # Pasul 0: Configurare
    configureaza_logging()
    incarca_env()
    args = parseaza_argumente()
    logger = logging.getLogger(__name__)

    logger.info(f"Pornire scraper cu metoda: {args.metoda}")
    logger.info(f"Format output: {args.format}")

    # Măsurăm durata execuției (util pentru compararea metodelor)
    timp_start = time.time()

    # Pasul 1: Colectare - rulăm scraper-ul ales
    try:
        functie_scrape = selecteaza_scraper(args.metoda)
        produse = functie_scrape()
    except Exception as e:
        logger.error(f"Eroare fatală în scraper: {e}")
        sys.exit(1)

    # Verificăm dacă s-au extras produse
    if not produse:
        logger.warning("Nu s-au extras produse. Verificați URL-ul și conexiunea.")
        sys.exit(1)

    # Pasul 2: Stocare - salvăm datele
    salveaza_date(produse, args.format)

    # Pasul 3: Raportare - afișăm rezumatul
    timp_total = time.time() - timp_start
    afiseaza_rezumat(produse)
    logger.info(f"Scraping finalizat cu succes în {timp_total:.2f} secunde!")


if __name__ == "__main__":
    main()
