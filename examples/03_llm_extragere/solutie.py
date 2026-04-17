"""
SOLUȚIE - Metoda 3: Extragere cu LLM

Rulare:
    pip install python-dotenv requests beautifulsoup4 anthropic

    Creați un fișier .env în directorul proiectului cu:
    ANTHROPIC_API_KEY=sk-ant-...

    python examples/03_llm_extragere/solutie.py
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
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 1: Prompt pentru nume și preț")
print("-" * 50)

PROMPT_EX1 = """Analizează HTML-ul următor și extrage toate produsele.

Pentru fiecare produs returnează un obiect JSON cu câmpurile:
- "nume": numele complet al produsului
- "pret": prețul ca număr float, fără simboluri valutare (ex: 295.99)

Returnează EXCLUSIV un array JSON valid. Fără text suplimentar, fără markdown.

HTML:
"""

print("Promptul tău:")
print(PROMPT_EX1.strip())
print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 2
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 2: Apel API și afișare rezultate")
print("-" * 50)


def apeleaza_llm(prompt: str, html: str) -> str:
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY nu este setat în fișierul .env!")

    client = anthropic.Anthropic(api_key=api_key)

    raspuns = client.messages.create(model="claude-haiku-4-5-20251001", max_tokens=2048,
                                     system="Ești un expert în extragerea de date structurate din HTML. Răspunzi EXCLUSIV cu JSON valid, fără niciun text suplimentar.",
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
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 3: Prompt extins cu tip stocare")
print("-" * 50)

PROMPT_EX3 = """Analizează HTML-ul următor și extrage toate produsele.

Pentru fiecare produs returnează un obiect JSON cu câmpurile:
- "nume": numele complet al produsului
- "pret": prețul ca număr float, fără simboluri valutare (ex: 295.99)
- "stocare": tipul de stocare - returnează "SSD", "HDD" sau null dacă nu se poate determina

Returnează EXCLUSIV un array JSON valid. Fără text suplimentar, fără markdown.

HTML:
"""

print("Promptul tău:")
print(PROMPT_EX3.strip())
print()

try:
    print("Se apelează API-ul Anthropic...")
    text_raspuns = apeleaza_llm(PROMPT_EX3, html_curat)
    produse = json.loads(text_raspuns)

    print(f"LLM a returnat {len(produse)} produse:\n")
    for p in produse[:3]:
        stocare = p.get("stocare") or "necunoscut"
        print(f"  • {p.get('nume', 'N/A')} - ${p.get('pret', 0):.2f} [{stocare}]")

    if len(produse) > 3:
        print(f"  ... și încă {len(produse) - 3} produse.")

except ValueError as e:
    print(f"[EROARE] {e}")
except json.JSONDecodeError as e:
    print(f"[EROARE JSON] {e}")
    print(f"Răspuns primit: {text_raspuns[:300]}")

print()
