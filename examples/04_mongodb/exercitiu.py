"""
EXERCIȚIU - MongoDB cu PyMongo
===============================

Pornind de la exemplu.py, completează operațiile CRUD de mai jos.
Fiecare exercițiu te ghidează să scrii singur interogările MongoDB.

Rulare:
    pip install pymongo
    # Asigurați-vă că MongoDB rulează local (vezi exemplu.py pentru instrucțiuni)
    python examples/04_mongodb/exercitiu.py
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# ─────────────────────────────────────────────────────────────
# Date de test (nu modifica)
# ─────────────────────────────────────────────────────────────

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

# ─────────────────────────────────────────────────────────────
# Conectare și pregătire (nu modifica)
# ─────────────────────────────────────────────────────────────

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
# Inserează un produs nou în colecție folosind insert_one().
#
# Produsul de adăugat:
#   id: "74", nume: "Samsung Galaxy Book", pret: 849.99,
#   pret_redus: None, rating: 4, numar_reviewuri: 8, marca: "Samsung"
#
# Afișează _id-ul generat automat de MongoDB.
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 1: Inserare produs nou")
print("-" * 40)

produs_nou = {"id": "74", "nume": "Samsung Galaxy Book", "pret": 849.99, "pret_redus": None, "rating": 4,
              "numar_reviewuri": 8, "marca": "Samsung", }

# TODO: inserează produs_nou în colecție cu insert_one()
# rezultat = colectie.insert_one(???)
# print(f"  Produs inserat cu _id: {rezultat.inserted_id}")

print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 2
# Găsește toate produsele cu prețul între $300 și $700 (inclusiv).
# Afișează numele și prețul fiecăruia.
#
# Indicii:
#   - Operatorii MongoDB: $gte (>=), $lte (<=)
#   - Sintaxă: {"pret": {"$gte": 300, "$lte": 700}}
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 2: Produse între $300 și $700")
print("-" * 40)

# TODO: completează filtrul
filtru = {}  # {"pret": {"$gte": ???, "$lte": ???}}

produse_gasite = list(colectie.find(filtru, {"_id": 0, "nume": 1, "pret": 1}))

for p in produse_gasite:
    print(f"  • {p['nume']} - ${p['pret']:.2f}")

print(f"  Total: {len(produse_gasite)} produse\n")

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 3
# Actualizează prețul redus al produsului cu id "64" (HP 250 G6)
# la valoarea 329.99 folosind update_one().
# Afișează documentul înainte și după actualizare.
#
# Indicii:
#   - Filtrul: {"id": "64"}
#   - Operatorul $set: {"$set": {"pret_redus": 329.99}}
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 3: Actualizare preț redus HP 250 G6")
print("-" * 40)

# Înainte
inainte = colectie.find_one({"id": "64"}, {"_id": 0, "nume": 1, "pret": 1, "pret_redus": 1})
print(f"  Înainte: {inainte}")

# TODO: actualizează pret_redus la 329.99 pentru produsul cu id "64"
# colectie.update_one(???, ???)

# După
dupa = colectie.find_one({"id": "64"}, {"_id": 0, "nume": 1, "pret": 1, "pret_redus": 1})
print(f"  După:   {dupa}")
print()

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 4
# Șterge toate produsele cu rating mai mic sau egal cu 2.
# Afișează câte documente au fost șterse.
#
# Indicii:
#   - Operatorul $lte: {"rating": {"$lte": 2}}
#   - delete_many() returnează un obiect cu atributul deleted_count
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 4: Ștergere produse cu rating ≤ 2")
print("-" * 40)

total_inainte = colectie.count_documents({})

# TODO: șterge produsele cu rating <= 2
# rezultat = colectie.delete_many(???)
# print(f"  Șterse: {rezultat.deleted_count} produse")

total_dupa = colectie.count_documents({})
print(f"  Rămase în colecție: {total_dupa} produse\n")

# ─────────────────────────────────────────────────────────────
# EXERCIȚIUL 5
# Folosind aggregation pipeline, calculează prețul mediu grupat
# pe marcă (câmpul "marca") și afișează rezultatele sortate
# descrescător după prețul mediu.
#
# Rezultat așteptat (aproximativ):
#   Lenovo: $739.99
#   Dell:   $699.99
#   ...
#
# Indicii:
#   - Etapa $group: {"_id": "$marca", "pret_mediu": {"$avg": "$pret"}}
#   - Etapa $sort: {"pret_mediu": -1} (-1 = descrescător)
# ─────────────────────────────────────────────────────────────

print("EXERCIȚIUL 5: Preț mediu pe marcă")
print("-" * 40)

# TODO: completează pipeline-ul de aggregation
pipeline = [  # Etapa 1: grupare pe marcă și calcul preț mediu
    # {"$group": {"_id": ???, "pret_mediu": {"$avg": ???}}},

    # Etapa 2: sortare descrescătoare după pret_mediu
    # {"$sort": {???: -1}},
]

rezultate = list(colectie.aggregate(pipeline))

for r in rezultate:
    print(f"  {r.get('_id', '?'):<10} ${r.get('pret_mediu', 0):.2f}")

print()
