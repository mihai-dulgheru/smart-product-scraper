"""
EXEMPLU DIDACTIC - Metoda 3: Extragere adaptivă cu LLM (AI)
============================================================

Acest fișier demonstrează o abordare modernă: în loc să scriem selectori
CSS fragili, trimitem HTML-ul unui model de limbaj care „înțelege” semantic
structura paginii și extrage datele automat în format JSON.

Rulare:
    pip install python-dotenv requests beautifulsoup4 anthropic openai

    Creați un fișier .env în directorul proiectului cu:
    ANTHROPIC_API_KEY=sk-ant-...
    OPENAI_API_KEY=sk-proj-...

    python examples/03_llm_extragere/exemplu.py

Alternativ, puteți folosi OpenAI:
    pip install openai
    # set OPENAI_API_KEY=sk-...
    # și schimbați _extrage_cu_anthropic cu _extrage_cu_openai mai jos.

De ce un LLM pentru scraping?
  → Selectori CSS clasici se sparg dacă site-ul modifică structura HTML.
    Un LLM înțelege semantic ce este „prețul” sau „numele produsului”
    indiferent de tag-urile sau clasele CSS folosite.
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
# PROMPTUL TRIMIS CĂTRE LLM
# ─────────────────────────────────────────────────────────────

# Calitatea promptului determină direct calitatea rezultatelor.
# Un prompt bun specifică:
#   1. Ce trebuie extras (câmpurile exacte)
#   2. Formatul așteptat (JSON, tipurile de date)
#   3. Cazuri speciale (null, formate numerice)
#   4. Ce NU trebuie inclus în răspuns (text extra, markdown)

PROMPT = """Analizează HTML-ul următor al unei pagini de e-commerce și extrage TOATE produsele.

Pentru fiecare produs returnează un obiect JSON cu câmpurile:
- "id": identificatorul numeric din URL (ex: 60)
- "nume": numele complet al produsului
- "pret": prețul ca număr float, FĂRĂ simboluri valutare (ex: 295.99)
- "rating": rating-ul ca număr întreg 1-5
- "numar_reviewuri": numărul de recenzii ca număr întreg
- "url": URL-ul relativ al produsului (ex: /product/60)

Returnează EXCLUSIV un array JSON valid. Fără text, fără markdown, fără backticks.

HTML:
"""

# ─────────────────────────────────────────────────────────────
# PASUL 1: Descărcăm și curățăm HTML-ul
# ─────────────────────────────────────────────────────────────

print("Pasul 1: Se descarcă HTML-ul paginii...")
raspuns = requests.get(URL, headers=HEADERS, timeout=30)
raspuns.raise_for_status()
html_brut = raspuns.text
print(f"  → HTML brut: {len(html_brut)} caractere\n")

print("Pasul 2: Se curăță HTML-ul (eliminare scripturi, stiluri, navigare)...")

soup = BeautifulSoup(html_brut, "html.parser")

# Eliminăm elementele irelevante pentru extragerea produselor.
# Scopul: reducem numărul de tokeni trimiși către LLM (= cost mai mic).
# Modelele LLM taxează per token, deci trimitem doar ce este relevant.
for tag in soup.find_all(["script", "style", "nav", "footer", "header", "noscript"]):
    tag.decompose()

html_curat = str(soup)

# Trunchiăm la 50.000 caractere (limitele de context ale modelelor)
# GPT-4o-mini: ~128k tokeni ≈ ~96.000 cuvinte
# Claude Haiku: ~200k tokeni
LIMITA_CARACTERE = 50_000
if len(html_curat) > LIMITA_CARACTERE:
    print(f"  → HTML trunchiat de la {len(html_curat)} la {LIMITA_CARACTERE} caractere")
    html_curat = html_curat[:LIMITA_CARACTERE]

print(f"  → HTML curățat: {len(html_curat)} caractere\n")


# ─────────────────────────────────────────────────────────────
# PASUL 3a: Extragere cu Anthropic Claude
# ─────────────────────────────────────────────────────────────

def _extrage_cu_anthropic(html: str) -> list[dict]:
    """Trimite HTML-ul către Claude și primește JSON structurat."""
    import anthropic

    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY nu este setat în fișierul .env!")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    print("Pasul 3: Se trimite HTML către Claude Haiku...")
    print("  (aceasta poate dura câteva secunde)\n")

    # Apelul API Anthropic:
    #   - model: claude-haiku-4-5 = cel mai rapid și ieftin model Claude
    #   - max_tokens: limita răspunsului (4096 suficient pentru lista de produse)
    #   - temperature=0: răspuns deterministic (nu creativ) - dorim JSON exact
    #   - system: instrucțiuni de rol/comportament pentru model
    raspuns = client.messages.create(model="claude-haiku-4-5-20241022", max_tokens=4096,
                                     system=("Ești un expert în extragerea de date structurate din HTML. "
                                             "Răspunzi EXCLUSIV cu JSON valid, fără niciun text suplimentar."),
                                     messages=[{"role": "user", "content": PROMPT + html}], temperature=0, )

    return raspuns.content[0].text.strip()


# ─────────────────────────────────────────────────────────────
# PASUL 3b: Extragere cu OpenAI GPT (alternativă)
# ─────────────────────────────────────────────────────────────

def _extrage_cu_openai(html: str) -> str:
    """Trimite HTML-ul către GPT-4o-mini și primește JSON structurat."""
    from openai import OpenAI

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY nu este setat în fișierul .env!")

    client = OpenAI(api_key=OPENAI_API_KEY)

    print("Pasul 3: Se trimite HTML către GPT-4o-mini...\n")

    # Apelul API OpenAI folosind formatul chat completions
    raspuns = client.chat.completions.create(model="gpt-4o-mini", messages=[
        {"role": "system", "content": ("Ești un expert în extragerea de date structurate din HTML. "
                                       "Răspunzi EXCLUSIV cu JSON valid, fără niciun text suplimentar."), },
        {"role": "user", "content": PROMPT + html}, ], temperature=0, )

    return raspuns.choices[0].message.content.strip()


# ─────────────────────────────────────────────────────────────
# PASUL 4: Parsăm răspunsul JSON al LLM-ului
# ─────────────────────────────────────────────────────────────

def _parseaza_json(text: str) -> list[dict]:
    """
    Parsează JSON-ul din răspunsul LLM-ului.

    LLM-urile uneori returnează JSON înconjurat de blocuri markdown:
        ```json
        [{"id": 1, ...}]
        ```
    Această funcție curăță formatarea și extrage JSON-ul pur.
    """
    # Eliminăm blocurile markdown dacă există
    if "```" in text:
        for segment in text.split("```"):
            segment = segment.strip()
            if segment.startswith("json"):
                segment = segment[4:].strip()
            if segment.startswith("["):
                text = segment
                break

    try:
        produse = json.loads(text)
        if isinstance(produse, list):
            return produse
        else:
            print(f"  [!] Răspunsul LLM nu este o listă JSON: {text[:200]}")
            return []
    except json.JSONDecodeError as e:
        print(f"  [!] Eroare JSON: {e}")
        print(f"  [!] Răspuns primit: {text[:300]}")
        return []


# ─────────────────────────────────────────────────────────────
# PASUL 5: Rulăm extragerea și afișăm rezultatele
# ─────────────────────────────────────────────────────────────

try:
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if anthropic_key:
        text_json = _extrage_cu_anthropic(html_curat)
    elif openai_key:
        text_json = _extrage_cu_openai(html_curat)
    else:
        raise ValueError("Nicio cheie API configurată!\n"
                         "Asigură-te că ai creat fișierul .env și ai setat "
                         "ANTHROPIC_API_KEY sau OPENAI_API_KEY.")

    produse = _parseaza_json(text_json)

    print(f"Pasul 4: LLM a extras {len(produse)} produse\n")
    print(f"{'─' * 60}")

    for produs in produse[:3]:
        print(f"  ID:      {produs.get('id', 'N/A')}")
        print(f"  Nume:    {produs.get('nume', 'N/A')}")
        print(f"  Preț:    ${produs.get('pret', 0):.2f}")
        rating = produs.get("rating", 0)
        print(f"  Rating:  {'★' * rating}{'☆' * (5 - rating)}")
        print(f"{'─' * 60}")

    if len(produse) > 3:
        print(f"\n  ... și încă {len(produse) - 3} produse.\n")

except ValueError as e:
    print(f"\n[EROARE] {e}\n")

# ─────────────────────────────────────────────────────────────
# REZUMAT CONCEPTUAL
# ─────────────────────────────────────────────────────────────
#
# Fluxul metodei LLM:
#
#   HTML brut
#     → Curățare (eliminare script/style/nav)
#     → Trunchiere (fit în fereastra de context)
#     → Trimitere către API (OpenAI / Anthropic)
#     → Model LLM înțelege semantic structura
#     → Răspuns JSON structurat
#     → Parsare și validare
#
# AVANTAJE vs. selectori CSS:
#   ✓ Funcționează fără modificări pe orice site de e-commerce
#   ✓ Rezistent la redesign-ul site-ului
#   ✓ Poate extrage date din structuri HTML complexe
#
# DEZAVANTAJE:
#   ✗ Cost per cerere (mic, dar există)
#   ✗ Latență mai mare (~1-3s pentru răspunsul API)
#   ✗ Limitat de fereastra de context (nu poate procesa pagini foarte mari)
#   ✗ Necesită cheie API și conexiune la internet
