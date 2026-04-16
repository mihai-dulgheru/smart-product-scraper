"""
SOLUȚIE - Lucrul cu fișiere CSV și JSON

Rulare (nu necesită instalare - module din stdlib Python):
    python examples/05_csv_si_json/solutie.py
"""

import csv
import json
from pathlib import Path

DIR_OUTPUT = Path(__file__).parent / "output_exercitii"
DIR_OUTPUT.mkdir(exist_ok=True)

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
print("  SOLUȚIE CSV & JSON")
print("=" * 60)
print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 1
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 1: Scriere JSON")
print("-" * 40)

cale_json = DIR_OUTPUT / "produse.json"

with open(cale_json, "w", encoding="utf-8") as f:
    json.dump(PRODUSE, f, ensure_ascii=False, indent=2)

print(f"  Fișier creat: {cale_json.name} ({cale_json.stat().st_size} bytes)")
print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 2
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 2: Citire JSON")
print("-" * 40)

with open(cale_json, encoding="utf-8") as f:
    produse_citite = json.load(f)

print(f"  Produse citite: {len(produse_citite)}")

cel_mai_scump = max(produse_citite, key=lambda p: p["pret"])
print(f"  Cel mai scump: {cel_mai_scump['nume']} (${cel_mai_scump['pret']:.2f})")
print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 3
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 3: Scriere CSV")
print("-" * 40)

cale_csv = DIR_OUTPUT / "produse.csv"

with open(cale_csv, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=COLOANE_CSV)
    writer.writeheader()
    for produs in PRODUSE:
        writer.writerow(produs)

if cale_csv.exists():
    print(f"  Conținut {cale_csv.name}:")
    with open(cale_csv, encoding="utf-8-sig") as f:
        for linie in f:
            print(f"    {linie}", end="")
    print()

print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 4
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 4: Citire CSV cu conversie tipuri")
print("-" * 40)


def converteste_rand(rand: dict) -> dict:
    return {"id": rand["id"], "nume": rand["nume"], "pret": float(rand["pret"]),
            "pret_redus": float(rand["pret_redus"]) if rand["pret_redus"] not in ("", "None") else None,
            "rating": int(rand["rating"]), "numar_reviewuri": int(rand["numar_reviewuri"]), }


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

print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 5
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 5: Produse cu reducere → JSON")
print("-" * 40)

cale_reduceri = DIR_OUTPUT / "produse_reducere.json"

produse_cu_reducere = []
for produs in PRODUSE:
    if produs["pret_redus"] is not None:
        produs_cu_economie = dict(produs)
        produs_cu_economie["economie"] = round(produs["pret"] - produs["pret_redus"], 2)
        produse_cu_reducere.append(produs_cu_economie)

with open(cale_reduceri, "w", encoding="utf-8") as f:
    json.dump(produse_cu_reducere, f, ensure_ascii=False, indent=2)

print(f"  Produse cu reducere: {len(produse_cu_reducere)}")
for p in produse_cu_reducere:
    print(f"  • {p['nume']:<35} economie: ${p['economie']:.2f}")

print()
