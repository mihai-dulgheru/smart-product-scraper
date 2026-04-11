"""
config.py - Configurări globale pentru Smart Product Scraper.

Acest modul centralizează toate constantele și setările proiectului:
URL-uri, headere HTTP, selectori CSS, căi de fișiere și configurări LLM.
Studenții pot modifica aceste valori pentru a adapta scraper-ul la alt site.
"""

import os
from pathlib import Path

# === Directoare de lucru ===
# Directorul rădăcină al proiectului (un nivel deasupra src/)
BASE_DIR = Path(__file__).resolve().parent.parent
# Directorul unde se salvează fișierele JSON/CSV generate
DATA_DIR = BASE_DIR / "data"

# === URL-uri target ===
# Site-ul de practică pentru scraping (webscraper.io - creat special pentru exerciții)
BASE_URL = "https://webscraper.io/test-sites/e-commerce/allinone"
# Pagina cu laptopuri - conține produse cu preț, descriere, rating
TARGET_URL = f"{BASE_URL}/computers/laptops"

# === Headere HTTP ===
# User-Agent simulează un browser real pentru a evita blocarea de către server.
# Fără acest header, unele site-uri returnează eroare 403 (Forbidden).
HEADERS = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/131.0.0.0 Safari/537.36"), "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7", }

# Timeout pentru request-uri HTTP (în secunde)
REQUEST_TIMEOUT = 30

# === Selectori CSS ===
# Acești selectori sunt specifici pentru webscraper.io.
# Pentru alt site, trebuie inspectați și actualizați manual (sau folosită metoda LLM).
SELECTORI = {  # Containerul fiecărui produs (card)
    "produs": "div.card.thumbnail",  # Numele complet al produsului (atributul title conține numele întreg)
    "nume": "a.title",  # Prețul afișat (ex: "$299.99")
    "pret": "h4.price span[itemprop='price']",  # Descrierea produsului
    "descriere": "p.description",  # Numărul de review-uri
    "review_count": "span[itemprop='reviewCount']",  # Rating-ul (atributul data-rating de pe elementul <p>)
    "rating": "div.ratings p[data-rating]",  # Link-ul către pagina produsului
    "link": "a.title", }

# === Configurări LLM (Metoda 3 - bonus) ===
# Cheile API se citesc din fișierul .env (nu le hardcodați niciodată în cod!)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Modelul LLM folosit pentru extragere adaptivă
# GPT-4o-mini este recomandat: rapid, ieftin și suficient de capabil
LLM_MODEL_OPENAI = "gpt-4o-mini"
LLM_MODEL_ANTHROPIC = "claude-haiku-4-5-20241022"

# Numărul maxim de caractere din HTML trimis către LLM
# (modelele au o fereastră de context limitată - trimitem doar o porțiune)
LLM_MAX_HTML_CHARS = 50_000

# === Configurări Playwright (Metoda 2) ===
# Timpul maxim de așteptare pentru încărcarea paginii (milisecunde)
PLAYWRIGHT_TIMEOUT = 60_000
# Browserul folosit (chromium, firefox sau webkit)
PLAYWRIGHT_BROWSER = "chromium"
