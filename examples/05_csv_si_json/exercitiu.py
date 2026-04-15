"""
EXERCIȚIU - Lucrul cu fișiere CSV și JSON
==========================================

Pornind de la exemplu.py, completează funcțiile și operațiile
de citire/scriere pentru CSV și JSON.

Rulare (nu necesită instalare - module din stdlib Python):
    python examples/05_csv_si_json/exercitiu.py
"""

import csv
from pathlib import Path

# Directorul unde salvăm fișierele generate
DIR_OUTPUT = Path(__file__).parent / "output_exercitii"
DIR_OUTPUT.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────
# Date de test (nu modifica)
# ─────────────────────────────────────────────────────────────

PRODUSE = [{"id": "60", "nume": "Asus VivoBook X441NA-GA190", "pret": 295.99, "pret_redus": None, "rating": 3,
            "numar_reviewuri": 14},
           {"id": "62", "nume": "Lenovo ThinkPad X240", "pret": 1099.99, "pret_redus": 899.99, "rating": 5,
            "numar_reviewuri": 31},
           {"id": "64", "nume": "HP 250 G6", "pret": 399.99, "pret_redus": None, "rating": 4, "numar_reviewuri": 7},
           {"id": "66", "nume": "Acer Aspire 3 A315-21", "pret": 249.99, "pret_redus": 199.99, "rating": 2,
            "numar_reviewuri": 3},
           {"id": "68", "nume": "Dell Inspiron 3576", "pret": 699.99, "pret_redus": 549.99, "rating": 5,
            "numar_reviewuri": 42}, ]

COLOANE_CSV = ["id", "nume", "pret", "pret_redus", "rating", "numar_reviewuri"]

print("=" * 60)
print("  EXERCIȚIU CSV & JSON")
print("=" * 60)
print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 1
# Scrie lista PRODUSE într-un fișier JSON numit "produse.json"
# în folderul DIR_OUTPUT.
#
# Cerințe:
#   - Fișierul trebuie să fie lizibil (indent=2)
#   - Caracterele românești (ș, ț, ă) să nu fie codificate
#     ca \uXXXX (folosește ensure_ascii=False)
#   - Afișează numărul de bytes al fișierului creat
#
# Indicii:
#   - Deschide fișierul cu open(..., "w", encoding="utf-8")
#   - Folosește json.dump(PRODUSE, fisier, ...)
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 1: Scriere JSON")
print("-" * 40)

cale_json = DIR_OUTPUT / "produse.json"

# TODO: scrie PRODUSE în fișierul cale_json
# with open(cale_json, ???, encoding="utf-8") as f:
#     json.dump(???)

# TODO: afișează dimensiunea fișierului creat
# print(f"  Fișier creat: {cale_json.name} ({cale_json.stat().st_size} bytes)")
print(f"  Fișier creat: {cale_json.name} (??? bytes)")
print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 2
# Citește fișierul JSON creat la Exercițiul 1 și:
#   a) Afișează câte produse conține
#   b) Afișează numele produsului cel mai scump
#
# Indicii:
#   - Deschide fișierul cu open(..., encoding="utf-8")
#   - Folosește json.load(fisier) pentru deserializare
#   - max(lista, key=lambda p: p["pret"]) găsește maximul
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 2: Citire JSON")
print("-" * 40)

# TODO: citește fișierul JSON
produse_citite = []
# with open(cale_json, encoding="utf-8") as f:
#     produse_citite = json.load(f)

print(f"  Produse citite: {len(produse_citite)}")

# TODO: găsește și afișează produsul cel mai scump
cel_mai_scump = None  # max(produse_citite, key=???)
print(f"  Cel mai scump: ???")
print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 3
# Scrie lista PRODUSE într-un fișier CSV numit "produse.csv"
# în folderul DIR_OUTPUT, respectând ordinea coloanelor din
# COLOANE_CSV.
#
# Cerințe:
#   - Prima linie trebuie să conțină header-ul cu numele coloanelor
#   - Fișierul trebuie să fie compatibil cu Excel (encoding utf-8-sig)
#   - Afișează conținutul fișierului după scriere
#
# Indicii:
#   - Deschide fișierul cu open(..., "w", newline="", encoding="utf-8-sig")
#   - Folosește csv.DictWriter cu fieldnames=COLOANE_CSV
#   - Apelează writer.writeheader() înainte de a scrie datele
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 3: Scriere CSV")
print("-" * 40)

cale_csv = DIR_OUTPUT / "produse.csv"

# TODO: scrie PRODUSE în fișierul CSV
# with open(cale_csv, ???, newline="", encoding="utf-8-sig") as f:
#     writer = csv.DictWriter(f, fieldnames=???)
#     writer.writeheader()
#     for produs in PRODUSE:
#         writer.writerow(produs)

# Afișare conținut (nu modifica)
if cale_csv.exists():
    print(f"  Conținut {cale_csv.name}:")
    with open(cale_csv, encoding="utf-8-sig") as f:
        for linie in f:
            print(f"    {linie}", end="")
    print()
else:
    print("  [Fișierul CSV nu a fost creat încă]")

print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 4
# Citește fișierul CSV creat la Exercițiul 3 și convertește
# tipurile de date la valorile corecte.
#
# Problema: CSV stochează totul ca string. Trebuie să convertești:
#   - "pret" și "pret_redus" → float (sau None dacă e gol/"None")
#   - "rating" și "numar_reviewuri" → int
#
# Completează funcția converteste_rand() de mai jos.
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 4: Citire CSV cu conversie tipuri")
print("-" * 40)


def converteste_rand(rand: dict) -> dict:
    """
    Primește un rând din CSV (toate valorile sunt string-uri)
    și returnează un dict cu tipurile corecte.
    """
    return {"id": rand["id"], "nume": rand["nume"],  # TODO: convertește la float
            "pret": rand["pret"],  # TODO: convertește la float dacă nu e gol/None, altfel None
            "pret_redus": rand["pret_redus"],  # TODO: convertește la int
            "rating": rand["rating"],  # TODO: convertește la int
            "numar_reviewuri": rand["numar_reviewuri"], }


# Citim și convertim (nu modifica structura, doar funcția de sus)
if cale_csv.exists():
    with open(cale_csv, newline="", encoding="utf-8-sig") as f:
        randuri_brute = list(csv.DictReader(f))

    produse_convertite = [converteste_rand(r) for r in randuri_brute]

    print("  Tipurile după conversie:")
    for p in produse_convertite:
        print(f"  • {p['nume']:<35} "
              f"pret={type(p['pret']).__name__}, "
              f"rating={type(p['rating']).__name__}, "
              f"pret_redus={type(p['pret_redus']).__name__}")
else:
    print("  [Creează mai întâi fișierul CSV la Exercițiul 3]")

print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 5
# Filtrează produsele cu reducere din lista PRODUSE și
# salvează-le într-un fișier JSON separat ("produse_reducere.json").
# Adaugă câmpul "economie" (pret - pret_redus) la fiecare produs.
#
# Rezultat așteptat (produse cu pret_redus != None + câmpul economie):
#   [
#     {"id": "62", "nume": "Lenovo...", ..., "economie": 200.0},
#     {"id": "66", "nume": "Acer...", ..., "economie": 50.0},
#     {"id": "68", "nume": "Dell...", ..., "economie": 150.0}
#   ]
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 5: Produse cu reducere → JSON")
print("-" * 40)

cale_reduceri = DIR_OUTPUT / "produse_reducere.json"

# TODO: filtrează produsele cu pret_redus != None
produse_cu_reducere = []
for produs in PRODUSE:
    if produs["pret_redus"] is not None:
        # TODO: creează un dict nou cu toate câmpurile + "economie"
        produs_cu_economie = dict(produs)  # copie superficială
        produs_cu_economie["economie"] = 0.0  # TODO: calculează economie
        produse_cu_reducere.append(produs_cu_economie)

# TODO: scrie produse_cu_reducere în cale_reduceri (JSON cu indent=2)

print(f"  Produse cu reducere: {len(produse_cu_reducere)}")
for p in produse_cu_reducere:
    print(f"  • {p['nume']:<35} economie: ${p['economie']:.2f}")

print()
