# 🛒 Smart Product Scraper

**Scraper inteligent de produse** - proiect demonstrativ pentru seminarul de **Big Data și Securitate Cibernetică**,
masteratul SIMPRE 2025-2026.

Proiectul ilustrează trei metode de web scraping, de la clasic la AI, folosind site-ul de
practică [Web Scraper Test Sites](https://webscraper.io/test-sites/e-commerce/allinone).

---

## Cuprins

- [Descriere](#descriere)
- [Arhitectură](#arhitectură)
- [Pre-rechizite](#pre-rechizite)
- [Instalare](#instalare)
- [Configurare](#configurare)
- [Mod de Rulare](#mod-de-rulare)
- [Exemple de Output](#exemple-de-output)
- [Structura Datelor Extrase](#structura-datelor-extrase)
- [Metode de Scraping](#metode-de-scraping)
- [Structura Proiectului](#structura-proiectului)
- [Depanare](#depanare)

---

## Descriere

Acest proiect demonstrează pipeline-ul complet de colectare a datelor din web, parcurgând trei etape fundamentale ale
unui sistem Big Data:

1. **Colectare** - preluarea HTML-ului de pe un site web (HTTP GET sau browser headless)
2. **Procesare** - extragerea și curățarea datelor (parsing HTML, conversie prețuri la valori numerice)
3. **Stocare** - salvarea datelor structurate în format JSON și CSV

Sunt implementate **trei metode de scraping**, fiecare reprezentând un nivel diferit de complexitate:

| Metodă               | Fișier                  | Descriere                                                                                     |
|----------------------|-------------------------|-----------------------------------------------------------------------------------------------|
| **Clasică**          | `scraper_requests.py`   | `requests` + `BeautifulSoup` - simplu, rapid, ideal pentru pagini statice                     |
| **Browser Headless** | `scraper_playwright.py` | `Playwright` - simulează un browser real, funcționează pe pagini dinamice (JavaScript)        |
| **AI / LLM**         | `scraper_llm.py`        | Trimite HTML-ul unui model de limbaj (GPT-4o-mini / Claude Haiku) care extrage datele adaptiv |

---

## Arhitectură

```
┌─────────────────────────────────────────────────────────┐
│                       main.py                           │
│              (orchestrare + selecție metodă)            │
├─────────────┬─────────────────────┬─────────────────────┤
│  Metoda 1   │     Metoda 2        │     Metoda 3        │
│  requests   │    Playwright       │    LLM (bonus)      │
│  + BS4      │  (browser headless) │  (OpenAI/Anthropic) │
├─────────────┴─────────────────────┴─────────────────────┤
│                      parser.py                          │
│         (curățare date, conversie prețuri → float)      │
├─────────────────────────────────────────────────────────┤
│                     storage.py                          │
│              (salvare JSON + CSV în data/)              │
└─────────────────────────────────────────────────────────┘
```

---

## Pre-rechizite

- **Python 3.10+** - [python.org/downloads](https://www.python.org/downloads/)
- **pip** - inclus în instalarea Python
- **Git** - [git-scm.com](https://git-scm.com/)
- **(Opțional)** Cheie API OpenAI sau Anthropic - doar pentru metoda LLM (bonus)

---

## Instalare

### 1. Clonare repository

```bash
git clone https://github.com/mihai-dulgheru/smart-product-scraper.git
cd smart-product-scraper
```

### 2. Creare mediu virtual (recomandat)

```bash
# Creare mediu virtual
python -m venv venv

# Activare (Windows)
venv\Scripts\activate

# Activare (macOS / Linux)
source venv/bin/activate
```

### 3. Instalare dependințe

```bash
pip install -r requirements.txt
```

### 4. Instalare browser Playwright (doar pentru Metoda 2)

```bash
playwright install chromium
```

---

## Configurare

### Configurare de bază

Fișierul `src/config.py` conține toate setările proiectului. Valorile implicite funcționează fără modificări pentru
site-ul de test.

### Configurare LLM (opțional - doar pentru Metoda 3)

Creați un fișier `.env` în rădăcina proiectului:

```bash
cp .env.example .env
```

Editați `.env` și adăugați cheia API:

```env
# Alegeți unul dintre provideri:
OPENAI_API_KEY=sk-...
# sau
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Mod de Rulare

### Rulare cu metoda implicită (requests + BeautifulSoup)

```bash
python src/main.py
```

### Alegerea metodei de scraping

```bash
# Metoda 1: Clasică (requests + BeautifulSoup)
python src/main.py --metoda requests

# Metoda 2: Browser headless (Playwright)
python src/main.py --metoda playwright

# Metoda 3: AI/LLM (necesită cheie API în .env)
python src/main.py --metoda llm
```

### Alegerea formatului de output

```bash
# Salvare doar JSON (implicit)
python src/main.py --format json

# Salvare doar CSV
python src/main.py --format csv

# Salvare ambele formate
python src/main.py --format toate
```

### Exemplu complet

```bash
python src/main.py --metoda playwright --format toate
```

---

## Exemple de Output

### Output în consolă

```
[INFO] Pornire scraper cu metoda: requests
[INFO] Se accesează: https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops
[INFO] HTML preluat cu succes (200 OK)
[INFO] S-au extras 6 produse
[INFO] Date salvate în data/products.json
[INFO] Date salvate în data/products.csv
[INFO] Scraping finalizat cu succes!
```

### Structura JSON (`data/products.json`)

```json
[
  {
    "id": "cart-881",
    "nume": "Packard 255 G2",
    "pret": 439.99,
    "pret_redus": null,
    "descriere": "Packard 255 G2, 15.6\" HD...",
    "rating": 2,
    "numar_review-uri": 8,
    "url": "https://webscraper.io/test-sites/e-commerce/allinone/product/881"
  },
  {
    "id": "cart-882",
    "nume": "Acer Aspire ES1-512",
    "pret": 391.99,
    "pret_redus": null,
    "descriere": "Acer Aspire ES1-512, 15.6\" HD...",
    "rating": 3,
    "numar_review-uri": 14,
    "url": "https://webscraper.io/test-sites/e-commerce/allinone/product/882"
  }
]
```

### Structura CSV (`data/products.csv`)

```csv
id,nume,pret,pret_redus,descriere,rating,numar_review-uri,url
cart-881,Packard 255 G2,439.99,,Packard 255 G2 15.6" HD...,2,8,https://webscraper.io/...
cart-882,Acer Aspire ES1-512,391.99,,Acer Aspire ES1-512 15.6" HD...,3,14,https://webscraper.io/...
```

---

## Structura Datelor Extrase

Fiecare produs extras conține următoarele câmpuri:

| Câmp               | Tip             | Descriere                                             |
|--------------------|-----------------|-------------------------------------------------------|
| `id`               | `str`           | Identificatorul unic al produsului (ex: `"cart-881"`) |
| `nume`             | `str`           | Numele complet al produsului                          |
| `pret`             | `float`         | Prețul original, valoare numerică (ex: `439.99`)      |
| `pret_redus`       | `float \| null` | Prețul redus, dacă există; altfel `null`              |
| `descriere`        | `str`           | Descrierea produsului                                 |
| `rating`           | `int`           | Numărul de stele (1-5)                                |
| `numar_review-uri` | `int`           | Numărul de recenzii                                   |
| `url`              | `str`           | Link-ul direct către pagina produsului                |

> **Notă:** Prețurile sunt întotdeauna valori numerice (`float`), nu string-uri cu monedă inclusă. Conversia din
`"$439.99"` → `439.99` se face automat în `parser.py`.

---

## Metode de Scraping

### Metoda 1: Clasică (`requests` + `BeautifulSoup`)

- **Când o folosești:** Site-uri statice, al căror conținut HTML este complet la încărcarea paginii
- **Avantaje:** Rapidă, consum minim de resurse, simplă de implementat
- **Dezavantaje:** Nu funcționează pe pagini care generează conținut via JavaScript (SPA)

### Metoda 2: Browser Headless (`Playwright`)

- **Când o folosești:** Site-uri dinamice (SPA, React, Angular) care generează conținut cu JavaScript
- **Avantaje:** Funcționează pe orice site, simulează un utilizator real
- **Dezavantaje:** Mai lentă, consum mai mare de resurse (lansează un browser real)

### Metoda 3: AI / LLM (bonus)

- **Când o folosești:** Când vrei extragere adaptivă, fără selectori CSS hardcodați
- **Avantaje:** Funcționează pe orice structură HTML, nu necesită mentenanță la schimbări de layout
- **Dezavantaje:** Cost per request (API), limitat de fereastra de context a modelului

---

## Structura Proiectului

```
smart-product-scraper/
├── README.md                 # Acest fișier
├── requirements.txt          # Dependințe Python
├── .env.example              # Template variabile de mediu
├── .gitignore                # Fișiere ignorate de Git
│
├── src/
│   ├── config.py             # Configurări (URL-uri, headere, căi)
│   ├── scraper_requests.py   # Metoda 1: requests + BeautifulSoup
│   ├── scraper_playwright.py # Metoda 2: Playwright (browser headless)
│   ├── scraper_llm.py        # Metoda 3: LLM (bonus)
│   ├── parser.py             # Curățare și validare date
│   ├── storage.py            # Salvare JSON / CSV
│   └── main.py               # Punct de intrare (CLI)
│
├── data/                     # Output generat automat
│   ├── products.json
│   └── products.csv
│
└── examples/
    └── sample_output.json    # Exemplu de referință
```

---

## Depanare

| Problemă                                                   | Soluție                                                               |
|------------------------------------------------------------|-----------------------------------------------------------------------|
| `ModuleNotFoundError: No module named 'bs4'`               | Rulați `pip install -r requirements.txt`                              |
| `playwright._impl._errors.Error: Executable doesn't exist` | Rulați `playwright install chromium`                                  |
| Playwright nu funcționează pe WSL                          | Instalați dependințele de sistem: `sudo npx playwright install-deps`  |
| `OPENAI_API_KEY not found`                                 | Creați fișierul `.env` cu cheia API (vezi secțiunea Configurare)      |
| Pagina returnează HTML gol                                 | Site-ul folosește JavaScript - treceți la metoda `playwright`         |
| Prețuri extrase ca string-uri                              | Verificați funcția `curata_pret()` din `parser.py`                    |
| `ConnectionError` / `Timeout`                              | Verificați conexiunea la internet; creșteți timeout-ul în `config.py` |
