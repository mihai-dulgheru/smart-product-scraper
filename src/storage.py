"""
storage.py - Funcții pentru salvarea datelor extrase în fișiere locale.

Suportă două formate de output:
  - JSON: format ierarhic, ușor de citit și de procesat programatic
  - CSV: format tabular, compatibil cu Excel, Google Sheets, pandas

În pipeline-ul Big Data, acest pas corespunde etapei de STOCARE.
"""

import csv
import json
import logging
from pathlib import Path

from config import DATA_DIR

logger = logging.getLogger(__name__)

# Câmpurile (coloanele) din fișierul CSV, în ordinea dorită
CAMPURI_CSV = ["id", "nume", "pret", "pret_redus", "descriere", "rating", "numar_review-uri", "url"]


def _asigura_director_output():
    """
    Creează directorul data/ dacă nu există deja.

    Folosim exist_ok=True pentru a evita o eroare dacă directorul
    a fost deja creat într-o rulare anterioară.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def salveaza_json(produse: list[dict], nume_fisier: str = "products.json") -> Path:
    """
    Salvează lista de produse într-un fișier JSON.

    JSON (JavaScript Object Notation) este formatul standard pentru
    schimbul de date structurate pe web. Este ușor de citit atât de
    oameni, cât și de mașini.

    Argumente:
        produse: Lista de dicționare, fiecare reprezentând un produs.
        nume_fisier: Numele fișierului de output (implicit: products.json).

    Returnează:
        Calea completă către fișierul salvat.

    Exemplu output:
        [
          {
            "id": "60",
            "nume": "Asus VivoBook X441NA-GA190",
            "pret": 295.99,
            ...
          }
        ]
    """
    _asigura_director_output()
    cale_fisier = DATA_DIR / nume_fisier

    try:
        with open(cale_fisier, "w", encoding="utf-8") as f:
            # ensure_ascii=False păstrează caracterele speciale (ă, î, ș, ț)
            # indent=2 formatează JSON-ul pentru lizibilitate
            json.dump(produse, f, ensure_ascii=False, indent=2)

        logger.info(f"Date salvate în {cale_fisier}")
        return cale_fisier

    except OSError as e:
        logger.error(f"Eroare la salvarea JSON: {e}")
        raise


def salveaza_csv(produse: list[dict], nume_fisier: str = "products.csv") -> Path:
    """
    Salvează lista de produse într-un fișier CSV.

    CSV (Comma-Separated Values) este un format tabular simplu,
    compatibil cu orice program de calcul tabelar (Excel, Google Sheets)
    și cu biblioteca pandas din Python.

    Argumente:
        produse: Lista de dicționare, fiecare reprezentând un produs.
        nume_fisier: Numele fișierului de output (implicit: products.csv).

    Returnează:
        Calea completă către fișierul salvat.
    """
    _asigura_director_output()
    cale_fisier = DATA_DIR / nume_fisier

    try:
        with open(cale_fisier, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPURI_CSV)
            # Scriem header-ul (prima linie cu numele coloanelor)
            writer.writeheader()
            # Scriem fiecare produs ca o linie în CSV
            for produs in produse:
                writer.writerow(produs)

        logger.info(f"Date salvate în {cale_fisier}")
        return cale_fisier

    except OSError as e:
        logger.error(f"Eroare la salvarea CSV: {e}")
        raise


def afiseaza_rezumat(produse: list[dict]):
    """
    Afișează un rezumat al datelor extrase în consolă.

    Util pentru verificarea rapidă a rezultatelor, fără a deschide
    fișierele JSON/CSV.

    Argumente:
        produse: Lista de produse extrase.
    """
    if not produse:
        logger.warning("Nu s-au extras produse.")
        return

    print(f"\n{'=' * 60}")
    print(f" REZUMAT: {len(produse)} produse extrase")
    print(f"{'=' * 60}")

    for i, produs in enumerate(produse[:5], start=1):
        pret_redus = produs.get("pret_redus")
        pret_info = f"${produs['pret']:.2f}"
        if pret_redus is not None:
            pret_info += f" → ${pret_redus:.2f} (reducere)"

        print(f"\n  {i}. {produs['nume']}")
        print(f"     Preț: {pret_info}")
        print(f"     ID: {produs['id']} | Rating: {'⭐ ' * produs.get('rating', 0)}")

    if len(produse) > 5:
        print(f"\n  ... și încă {len(produse) - 5} produse")

    print(f"\n{'=' * 60}\n")
