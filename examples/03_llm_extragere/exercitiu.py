"""
EXERCIȚIU - Metoda 3: Extragere cu LLM
=======================================

Pornind de la exemplu.py, vei modifica promptul și vei adăuga
validări pentru a înțelege cum influențează promptul calitatea
răspunsurilor LLM.

Rulare:
    pip install python-dotenv requests beautifulsoup4 anthropic

    Creați un fișier .env în directorul proiectului cu:
    ANTHROPIC_API_KEY=sk-ant-...

    python examples/03_llm_extragere/exercitiu.py
"""

import json
import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

URL = "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"
HEADERS = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/131.0.0.0 Safari/537.36")}

# ─────────────────────────────────────────────────────────────
# Descărcăm și curățăm HTML-ul (cod deja scris - nu modifica)
# ─────────────────────────────────────────────────────────────

print("Se descarcă și curăță HTML-ul...")
raspuns = requests.get(URL, headers=HEADERS, timeout=30)
raspuns.raise_for_status()

soup = BeautifulSoup(raspuns.text, "html.parser")
for tag in soup.find_all(["script", "style", "nav", "footer", "header", "noscript"]):
    tag.decompose()

html_curat = str(soup)[:50_000]
print(f"HTML curățat: {len(html_curat)} caractere\n")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 1
# Scrie un prompt care cere LLM-ului să extragă DOAR numele
# și prețul fiecărui produs, ca o listă JSON simplificată.
#
# Formatul dorit al răspunsului:
#   [{"nume": "Asus VivoBook...", "pret": 295.99}, ...]
#
# Indicii:
#   - Fii explicit: specifică exact câmpurile dorite
#   - Cere răspuns EXCLUSIV JSON, fără text suplimentar
#   - Specifică tipul datelor: pret ca float, fără simbolul $
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 1: Prompt pentru nume și preț")
print("-" * 50)

# TODO: completează promptul de mai jos
PROMPT_EX1 = """Analizează HTML-ul următor și extrage toate produsele.

Pentru fiecare produs returnează:
- ???: numele produsului
- ???: prețul ca număr (ex: 295.99)

Returnează EXCLUSIV un array JSON valid. Fără text suplimentar.

HTML:
"""

print("Promptul tău:")
print(PROMPT_EX1.strip())
print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 2
# Apelează API-ul Anthropic cu promptul din Exercițiul 1 și
# afișează rezultatele.
#
# Indicii:
#   - Verifică dacă ANTHROPIC_API_KEY este setat
#   - Modelul recomandat: claude-haiku-4-5-20251001 (rapid și ieftin)
#   - temperature=0 → răspuns deterministic (important pentru JSON)
#   - Parsează răspunsul cu json.loads()
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 2: Apel API și afișare rezultate")
print("-" * 50)


def apeleaza_llm(prompt: str, html: str) -> str:
    """Trimite HTML-ul la Claude și returnează răspunsul text."""
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY nu este setat în fișierul .env!")

    client = anthropic.Anthropic(api_key=api_key)

    # TODO: completează apelul API
    raspuns = client.messages.create(model="claude-haiku-4-5-20251001", max_tokens=2048,
                                     # TODO: adaugă parametrul system cu instrucțiuni pentru model
                                     # system="...",
                                     messages=[{"role": "user", "content": prompt + html}], temperature=0, )

    return raspuns.content[0].text.strip()


try:
    print("Se apelează API-ul Anthropic...")
    text_raspuns = apeleaza_llm(PROMPT_EX1, html_curat)
    produse = json.loads(text_raspuns)

    print(f"LLM a returnat {len(produse)} produse:\n")
    for p in produse[:3]:
        print(f"  • {p}")

    if len(produse) > 3:
        print(f"  ... și încă {len(produse) - 3} produse.")

except ValueError as e:
    print(f"[EROARE] {e}")
except json.JSONDecodeError as e:
    print(f"[EROARE JSON] {e}")
    print(f"Răspuns primit: {text_raspuns[:300]}")

print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 3
# Modifică promptul pentru a extrage și un câmp suplimentar:
# dacă laptopul are SSD sau HDD (din câmpul "descriere").
#
# Formatul dorit:
#   [{"nume": "...", "pret": 295.99, "stocare": "HDD"}, ...]
#
# Indicii:
#   - Informația despre stocare se află în descrierea produsului
#     (ex: "256GB SSD" sau "500GB HDD")
#   - Cere LLM-ului să returneze "SSD", "HDD" sau "necunoscut"
#   - Dacă nu găsește informația, să returneze null
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 3: Prompt extins cu tip stocare")
print("-" * 50)

# TODO: scrie un prompt nou care extrage și tipul de stocare
PROMPT_EX3 = """TODO: completează promptul

HTML:
"""

print("Promptul tău:")
print(PROMPT_EX3.strip())
print()
