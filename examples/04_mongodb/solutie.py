"""
SOLUȚIE - MongoDB cu PyMongo

Rulare:
    pip install pymongo
    python examples/04_mongodb/solutie.py
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

PRODUSE = [{"id": "60", "nume": "Asus VivoBook X441NA-GA190", "pret": 295.99, "pret_redus": None, "rating": 3,
            "numar_reviewuri": 14, "marca": "Asus"},
           {"id": "62", "nume": "Lenovo ThinkPad X240", "pret": 1099.99, "pret_redus": 899.99, "rating": 5,
            "numar_reviewuri": 31, "marca": "Lenovo"},
           {"id": "64", "nume": "HP 250 G6", "pret": 399.99, "pret_redus": None, "rating": 4, "numar_reviewuri": 7,
            "marca": "HP"},
           {"id": "66", "nume": "Acer Aspire 3 A315-21", "pret": 249.99, "pret_redus": None, "rating": 2,
            "numar_reviewuri": 3, "marca": "Acer"},
           {"id": "68", "nume": "Dell Inspiron 3576", "pret": 699.99, "pret_redus": 549.99, "rating": 5,
            "numar_reviewuri": 42, "marca": "Dell"},
           {"id": "70", "nume": "HP Pavilion 15", "pret": 549.99, "pret_redus": 479.99, "rating": 4,
            "numar_reviewuri": 19, "marca": "HP"},
           {"id": "72", "nume": "Lenovo IdeaPad 330", "pret": 379.99, "pret_redus": None, "rating": 3,
            "numar_reviewuri": 11, "marca": "Lenovo"}, ]

print("Conectare la MongoDB...")
client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=3000)

try:
    client.admin.command("ping")
    print("  → Conectat!\n")
except ConnectionFailure:
    print("  [EROARE] MongoDB nu rulează. Pornește serviciul și reîncearcă.")
    exit(1)

db = client["scraper_db"]
colectie = db["exercitii_produse"]
colectie.drop()
colectie.insert_many(PRODUSE)
print(f"  Colecție resetată cu {len(PRODUSE)} produse.\n")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 1
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 1: Inserare produs nou")
print("-" * 40)

produs_nou = {"id": "74", "nume": "Samsung Galaxy Book", "pret": 849.99, "pret_redus": None, "rating": 4,
              "numar_reviewuri": 8, "marca": "Samsung", }

rezultat = colectie.insert_one(produs_nou)
print(f"  Produs inserat cu _id: {rezultat.inserted_id}")

print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 2
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 2: Produse între $300 și $700")
print("-" * 40)

filtru = {"pret": {"$gte": 300, "$lte": 700}}

produse_gasite = list(colectie.find(filtru, {"_id": 0, "nume": 1, "pret": 1}))

for p in produse_gasite:
    print(f"  • {p['nume']} - ${p['pret']:.2f}")

print(f"  Total: {len(produse_gasite)} produse\n")

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 3
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 3: Actualizare preț redus HP 250 G6")
print("-" * 40)

inainte = colectie.find_one({"id": "64"}, {"_id": 0, "nume": 1, "pret": 1, "pret_redus": 1})
print(f"  Înainte: {inainte}")

colectie.update_one({"id": "64"}, {"$set": {"pret_redus": 329.99}})

dupa = colectie.find_one({"id": "64"}, {"_id": 0, "nume": 1, "pret": 1, "pret_redus": 1})
print(f"  După:   {dupa}")
print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 4
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 4: Ștergere produse cu rating ≤ 2")
print("-" * 40)

total_inainte = colectie.count_documents({})

rezultat = colectie.delete_many({"rating": {"$lte": 2}})
print(f"  Șterse: {rezultat.deleted_count} produse")

total_dupa = colectie.count_documents({})
print(f"  Rămase în colecție: {total_dupa} produse\n")

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 5
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 5: Preț mediu pe marcă")
print("-" * 40)

pipeline = [{"$group": {"_id": "$marca", "pret_mediu": {"$avg": "$pret"}}}, {"$sort": {"pret_mediu": -1}}, ]

rezultate = list(colectie.aggregate(pipeline))

for r in rezultate:
    print(f"  {r.get('_id', '?'):<10} ${r.get('pret_mediu', 0):.2f}")

print()

client.close()
