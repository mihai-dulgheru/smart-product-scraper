"""
EXEMPLU DIDACTIC - Lucrul cu fișiere CSV și JSON
=================================================

Acest fișier demonstrează operațiile esențiale cu cele două formate
de stocare a datelor structurate cel mai des folosite în scraping:

  - JSON (JavaScript Object Notation): format ierarhic, ideal pentru
    date cu structuri imbricate sau câmpuri opționale.

  - CSV (Comma-Separated Values): format tabular, ideal pentru date
    uniforme, compatibil cu Excel, Google Sheets și pandas.

Rulare (nu necesită instalare - module din stdlib Python):
    python examples/05_csv_si_json/exemplu.py

Module folosite:
    json → inclus în Python (stdlib)
    csv → inclus în Python (stdlib)
    os / pathlib → incluse în Python (stdlib)
"""

import csv
import json
import os
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# DATE DE TEST
# ─────────────────────────────────────────────────────────────

PRODUSE = [{"id": "60", "nume": "Asus VivoBook X441NA-GA190", "pret": 295.99, "pret_redus": None,
            "descriere": "Laptop, Intel Celeron N3350 1.1GHz, 4GB, 500GB, Linux", "rating": 3, "numar_reviewuri": 14,
            "url": "https://webscraper.io/test-sites/e-commerce/allinone/product/60", },
           {"id": "62", "nume": "Lenovo ThinkPad X240", "pret": 1099.99, "pret_redus": 899.99,
            "descriere": "Ultrabook, Intel Core i5-4300U 1.9GHz, 8GB, 256GB SSD, Win10", "rating": 5,
            "numar_reviewuri": 31, "url": "https://webscraper.io/test-sites/e-commerce/allinone/product/62", },
           {"id": "64", "nume": "HP 250 G6", "pret": 399.99, "pret_redus": None,
            "descriere": "Laptop, Intel Core i3-6006U 2GHz, 4GB, 1TB, FreeDOS", "rating": 4, "numar_reviewuri": 7,
            "url": "https://webscraper.io/test-sites/e-commerce/allinone/product/64", },
           {"id": "66", "nume": "Acer Aspire 3 A315-21", "pret": 249.99, "pret_redus": 199.99,
            "descriere": "Laptop, AMD E2-9000e 1.5GHz, 4GB, 500GB, Linux", "rating": 2, "numar_reviewuri": 3,
            "url": "https://webscraper.io/test-sites/e-commerce/allinone/product/66", },
           {"id": "68", "nume": "Dell Inspiron 3576", "pret": 699.99, "pret_redus": 549.99,
            "descriere": "Laptop, Intel Core i5-8250U 1.6GHz, 8GB, 256GB SSD + 1TB HDD, Win10", "rating": 5,
            "numar_reviewuri": 42, "url": "https://webscraper.io/test-sites/e-commerce/allinone/product/68", }, ]

# Directorul unde salvăm fișierele generate de acest exemplu
DIR_OUTPUT = Path(__file__).parent / "output"
DIR_OUTPUT.mkdir(exist_ok=True)  # creăm folderul dacă nu există

separator = "─" * 60

print(f"\n{'═' * 60}")
print("  EXEMPLU CSV & JSON - Smart Product Scraper")
print(f"{'═' * 60}\n")

# ══════════════════════════════════════════════════════════════
#  PARTEA 1: JSON
# ══════════════════════════════════════════════════════════════

print(f"{separator}")
print("  PARTEA 1: JSON")
print(f"{separator}\n")

# ─────────────────────────────────────────────────────────────
# 1A: SCRIERE JSON
# ─────────────────────────────────────────────────────────────

print("1A. Scriere JSON - json.dump()\n")

cale_json = DIR_OUTPUT / "produse.json"

# open() cu encoding="utf-8" → obligatoriu pentru caractere non-ASCII (ă, î, ș)
with open(cale_json, "w", encoding="utf-8") as f:
    # json.dump(obiect, fisier, ...) → scrie direct în fișier
    # json.dumps(obiect, ...)        → returnează un string (fără fișier)
    json.dump(PRODUSE, f, ensure_ascii=False,  # păstrează ă, î, ș, ț ca atare (nu le codifică \uXXXX)
              indent=2,  # indentare 2 spații → fișier lizibil de oameni
              )

print(f"  → Fișier scris: {cale_json}")
print(f"  → Dimensiune:   {os.path.getsize(cale_json)} bytes\n")

# Afișăm primele 10 linii pentru a vedea cum arată fișierul
print("  Primele 10 linii din fișier:")
with open(cale_json, encoding="utf-8") as f:
    for i, linie in enumerate(f):
        if i >= 10:
            print("  ...")
            break
        print(f"  {linie}", end="")
print("\n")

# ─────────────────────────────────────────────────────────────
# 1B: CITIRE JSON
# ─────────────────────────────────────────────────────────────

print("1B. Citire JSON - json.load()\n")

with open(cale_json, encoding="utf-8") as f:
    # json.load(fisier)  → deserializează JSON din fișier în obiecte Python
    # json.loads(string) → deserializează JSON dintr-un string Python
    produse_citite = json.load(f)

print(f"  → {len(produse_citite)} produse citite din JSON\n")
print(f"  → Tipul returnat: {type(produse_citite)}")
print(f"  → Tipul primului element: {type(produse_citite[0])}\n")

# Accesăm datele exact ca pe un dicționar Python obișnuit
print("  Produsele citite:")
for p in produse_citite:
    pret_redus = p["pret_redus"]
    info_pret = f"${p['pret']:.2f}"
    if pret_redus is not None:
        economie = p["pret"] - pret_redus
        info_pret += f" → ${pret_redus:.2f} (economie ${economie:.2f})"
    print(f"  • {p['nume']:<35} {info_pret}")
print()

# ─────────────────────────────────────────────────────────────
# 1C: MODIFICARE DATE ȘI RESCRIERE JSON
# ─────────────────────────────────────────────────────────────

print("1C. Modificare și rescriere JSON\n")

# Adăugăm un câmp nou tuturor produselor (ex: disponibilitate)
for produs in produse_citite:
    produs["disponibil"] = True

# Modificăm prețul unui produs specific
for produs in produse_citite:
    if produs["id"] == "64":
        produs["pret_redus"] = 349.99
        print(f"  → HP 250 G6: reducere adăugată → ${produs['pret_redus']}")

# Rescriem fișierul cu datele actualizate
cale_json_actualizat = DIR_OUTPUT / "produse_actualizate.json"
with open(cale_json_actualizat, "w", encoding="utf-8") as f:
    json.dump(produse_citite, f, ensure_ascii=False, indent=2)

print(f"  → Fișier rescris: {cale_json_actualizat}\n")

# ─────────────────────────────────────────────────────────────
# 1D: JSON → STRING ȘI STRING → JSON (fără fișier)
# ─────────────────────────────────────────────────────────────

print("1D. Conversie JSON ↔ string Python (fără fișier)\n")

# Util pentru: trimitere prin HTTP, stocare în baze de date, logging
un_produs = PRODUSE[0]

# Obiect Python → string JSON
sir_json = json.dumps(un_produs, ensure_ascii=False, indent=2)
print(f"  json.dumps() → string de {len(sir_json)} caractere:")
print(f"  {sir_json[:80]}...\n")

# String JSON → obiect Python
produs_reconstituit = json.loads(sir_json)
print(f"  json.loads() → dict cu cheile: {list(produs_reconstituit.keys())}\n")

# ─────────────────────────────────────────────────────────────
# 1E: TRATAREA TIPURILOR SPECIALE ÎN JSON
# ─────────────────────────────────────────────────────────────

print("1E. Tipuri Python ↔ JSON\n")

# Tabelul de conversie Python → JSON:
print("  Python          JSON")
print("  ─────────────────────────────")
print("  dict            object  { }")
print("  list, tuple     array   [ ]")
print("  str             string  \"...\"")
print("  int, float      number  123 / 1.5")
print("  True / False    true / false")
print("  None            null")
print()

# Demonstrație: None → null în JSON
exemplu = {"valoare": None, "activ": True, "scor": 4.5}
print(f"  Python: {exemplu}")
print(f"  JSON:   {json.dumps(exemplu)}\n")

# ══════════════════════════════════════════════════════════════
#  PARTEA 2: CSV
# ══════════════════════════════════════════════════════════════

print(f"{separator}")
print("  PARTEA 2: CSV")
print(f"{separator}\n")

# Coloanele CSV (ordinea în fișier)
COLOANE = ["id", "nume", "pret", "pret_redus", "descriere", "rating", "numar_reviewuri", "url"]

# ─────────────────────────────────────────────────────────────
# 2A: SCRIERE CSV
# ─────────────────────────────────────────────────────────────

print("2A. Scriere CSV - csv.DictWriter()\n")

cale_csv = DIR_OUTPUT / "produse.csv"

# newline=""  → obligatoriu pe Windows pentru a preveni linii goale între rânduri
# encoding="utf-8-sig" → adaugă BOM (Byte Order Mark) pentru compatibilitate Excel
with open(cale_csv, "w", newline="", encoding="utf-8-sig") as f:
    # DictWriter scrie dicționare Python ca rânduri CSV
    # fieldnames = lista ordonată a coloanelor
    writer = csv.DictWriter(f, fieldnames=COLOANE)

    # Scriem prima linie cu numele coloanelor (header)
    writer.writeheader()

    # Scriem fiecare produs ca un rând CSV
    for produs in PRODUSE:
        writer.writerow(produs)

print(f"  → Fișier scris: {cale_csv}")
print(f"  → Dimensiune:   {os.path.getsize(cale_csv)} bytes\n")

# Afișăm conținutul fișierului
print("  Conținut fișier CSV:")
with open(cale_csv, encoding="utf-8-sig") as f:
    for linie in f:
        print(f"  {linie}", end="")
print("\n")

# ─────────────────────────────────────────────────────────────
# 2B: CITIRE CSV
# ─────────────────────────────────────────────────────────────

print("2B. Citire CSV - csv.DictReader()\n")

with open(cale_csv, newline="", encoding="utf-8-sig") as f:
    # DictReader citește fiecare rând ca un dicționar Python
    # Cheia = numele coloanei (din linia de header)
    # Valoarea = conținutul celulei (întotdeauna STRING!)
    reader = csv.DictReader(f)

    produse_din_csv = list(reader)

print(f"  → {len(produse_din_csv)} produse citite din CSV\n")

# ATENȚIE: CSV nu păstrează tipurile de date!
# Toate valorile sunt citite ca STRING. Trebuie convertite manual.
primul = produse_din_csv[0]
print("  ATENȚIE - tipurile după citire din CSV:")
print(f"  pret         = {repr(primul['pret'])}  → tip: {type(primul['pret']).__name__}")
print(f"  rating       = {repr(primul['rating'])}     → tip: {type(primul['rating']).__name__}")
print(f"  pret_redus   = {repr(primul['pret_redus'])}  → tip: {type(primul['pret_redus']).__name__}")
print()
print("  Spre deosebire de JSON, care păstrează tipurile:")
primul_json = PRODUSE[0]
print(f"  pret         = {repr(primul_json['pret'])}  → tip: {type(primul_json['pret']).__name__}")
print(f"  rating       = {repr(primul_json['rating'])}      → tip: {type(primul_json['rating']).__name__}")
print(f"  pret_redus   = {repr(primul_json['pret_redus'])}  → tip: {type(primul_json['pret_redus']).__name__}")
print()

# ─────────────────────────────────────────────────────────────
# 2C: CONVERSIE TIPURI DUPĂ CITIRE CSV
# ─────────────────────────────────────────────────────────────

print("2C. Conversie tipuri după citire CSV\n")


def converteste_produs_csv(rand: dict) -> dict:
    """
    Convertește un rând citit din CSV la tipurile corecte.

    CSV stochează totul ca text. Trebuie să convertim manual
    la int, float, None etc.
    """
    return {"id": rand["id"], "nume": rand["nume"], "pret": float(rand["pret"]),
            # Valoarea goală "" sau șirul "None" → None Python
            "pret_redus": float(rand["pret_redus"]) if rand["pret_redus"] not in ("", "None") else None,
            "descriere": rand["descriere"], "rating": int(rand["rating"]),
            "numar_reviewuri": int(rand["numar_reviewuri"]), "url": rand["url"], }


produse_convertite = [converteste_produs_csv(r) for r in produse_din_csv]

print("  După conversie:")
for p in produse_convertite:
    tip_pret = type(p["pret"]).__name__
    tip_rating = type(p["rating"]).__name__
    tip_pret_redus = type(p["pret_redus"]).__name__
    print(f"  • {p['nume']:<35} pret={tip_pret}, rating={tip_rating}, pret_redus={tip_pret_redus}")
print()

# ─────────────────────────────────────────────────────────────
# 2D: CITIRE CSV CA LISTE (csv.reader)
# ─────────────────────────────────────────────────────────────

print("2D. Citire CSV cu csv.reader() (rânduri ca liste, nu dicționare)\n")

with open(cale_csv, newline="", encoding="utf-8-sig") as f:
    reader = csv.reader(f)

    # Primul rând = header-ul cu numele coloanelor
    header = next(reader)
    print(f"  Header: {header}\n")

    # Restul rândurilor = datele
    print("  Primele 2 rânduri de date:")
    for i, rand in enumerate(reader):
        if i >= 2:
            break
        print(f"  Rând {i + 1}: {rand}")
print()

# ─────────────────────────────────────────────────────────────
# 2E: SCRIERE CSV RÂND CU RÂND (append mode)
# ─────────────────────────────────────────────────────────────

print("2E. Adăugare rând nou la fișier existent (append mode)\n")

produs_nou = {"id": "99", "nume": "Samsung Galaxy Book Pro", "pret": 1299.99, "pret_redus": 999.99,
              "descriere": "Laptop ultra-subțire, Intel Core i7, 16GB, 512GB SSD, Win11", "rating": 5,
              "numar_reviewuri": 58, "url": "https://webscraper.io/test-sites/e-commerce/allinone/product/99", }

# mode="a" (append) → adaugă la sfârșitul fișierului existent
with open(cale_csv, "a", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=COLOANE)
    writer.writerow(produs_nou)  # Nu scriem header din nou!

print(f"  → Produs nou adăugat: {produs_nou['nume']}")

# Verificăm numărul total de rânduri
with open(cale_csv, newline="", encoding="utf-8-sig") as f:
    numar_randuri = sum(1 for _ in csv.DictReader(f))
print(f"  → Total produse în CSV acum: {numar_randuri}\n")

# ══════════════════════════════════════════════════════════════
#  PARTEA 3: CONVERSII JSON ↔ CSV
# ══════════════════════════════════════════════════════════════

print(f"{separator}")
print("  PARTEA 3: CONVERSII JSON ↔ CSV")
print(f"{separator}\n")

# ─────────────────────────────────────────────────────────────
# 3A: JSON → CSV
# ─────────────────────────────────────────────────────────────

print("3A. Conversie JSON → CSV\n")

# Citim JSON-ul
with open(cale_json, encoding="utf-8") as f:
    date_json = json.load(f)

# Detectăm automat coloanele din primul document
coloane_detectate = list(date_json[0].keys())
print(f"  Coloane detectate automat: {coloane_detectate}\n")

cale_din_json = DIR_OUTPUT / "din_json.csv"
with open(cale_din_json, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=coloane_detectate)
    writer.writeheader()
    writer.writerows(date_json)  # writerows() = writerow() în buclă

print(f"  → CSV generat din JSON: {cale_din_json}\n")

# ─────────────────────────────────────────────────────────────
# 3B: CSV → JSON
# ─────────────────────────────────────────────────────────────

print("3B. Conversie CSV → JSON\n")

with open(cale_csv, newline="", encoding="utf-8-sig") as f:
    randuri = list(csv.DictReader(f))

cale_din_csv = DIR_OUTPUT / "din_csv.json"
with open(cale_din_csv, "w", encoding="utf-8") as f:
    # Notă: valorile rămân string-uri (CSV nu păstrează tipurile).
    # Pentru tipuri corecte, aplicați converteste_produs_csv() mai întâi.
    json.dump(randuri, f, ensure_ascii=False, indent=2)

print(f"  → JSON generat din CSV: {cale_din_csv}")
print(f"  → {len(randuri)} rânduri convertite\n")

# ══════════════════════════════════════════════════════════════
#  REZUMAT FINAL
# ══════════════════════════════════════════════════════════════

print(f"{separator}")
print("  FIȘIERE GENERATE în examples/05_csv_si_json/output/:")
print(f"{separator}")
for fisier in sorted(DIR_OUTPUT.iterdir()):
    size = os.path.getsize(fisier)
    print(f"  • {fisier.name:<30} {size:>6} bytes")
print()

# ─────────────────────────────────────────────────────────────
# REZUMAT CONCEPTUAL
# ─────────────────────────────────────────────────────────────
#
# Comparație JSON vs. CSV:
#
#   Criteriu            JSON                          CSV
#   ─────────────────   ───────────────────────────── ────────────────────────────
#   Structură           Ierarhică (obiecte imbricate) Tabelară (rânduri + coloane)
#   Tipuri de date      Păstrate (int, float, null)   Pierdute (totul → string)
#   Lizibilitate        Bună (cu indent=2)            Excelentă (simplu)
#   Compatibilitate     API-uri web, baze de date     Excel, Google Sheets, pandas
#   Câmpuri opționale   Suportate natural             Dificil (celule goale)
#   Date imbricate      Suportate (liste în obiecte)  Nu (aplatizare necesară)
#   Dimensiune fișier   Mai mare (chei repetate)      Mai mic (fără chei)
#   Module Python       json (stdlib)                 csv (stdlib)
#
# CÂND SĂ FOLOSEȘTI JSON:
#   ✓ Date cu structuri variate sau imbricate
#   ✓ Comunicare cu API-uri web
#   ✓ Stocare intermediară în pipeline-uri de date
#   ✓ Configurații și metadata
#
# CÂND SĂ FOLOSEȘTI CSV:
#   ✓ Date tabulare uniforme (toate înregistrările au aceleași câmpuri)
#   ✓ Schimb de date cu utilizatori non-tehnici (Excel)
#   ✓ Import în pandas: pd.read_csv("produse.csv")
#   ✓ Volume mari de date simple (mai compact decât JSON)
