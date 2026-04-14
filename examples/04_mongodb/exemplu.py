"""
EXEMPLU DIDACTIC - MongoDB cu PyMongo
======================================

Acest fișier demonstrează operațiile CRUD de bază cu MongoDB folosind
biblioteca PyMongo, în contextul proiectului de scraping.

Rulare:
    pip install pymongo
    # Asigurați-vă că MongoDB rulează local:
    #   - Windows: porniți serviciul MongoDB din Services sau rulați mongod.exe
    #   - Linux:   sudo systemctl start mongod
    #   - Docker:  docker run -d -p 27017:27017 mongo
    python examples/04_mongodb/exemplu.py

Ce este MongoDB?
  → Bază de date NoSQL orientată pe documente.
  → Documentele sunt stocate în format BSON (similar cu JSON).
  → Ideal pentru date semi-structurate (ex: produse cu câmpuri opționale).
  → Comparație cu SQL:
        SQL           MongoDB
        ────────────────────────────
        Table         Collection
        Row           Document
        Column        Field
        PRIMARY KEY   _id (ObjectId)
"""

from datetime import datetime

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError

# ─────────────────────────────────────────────────────────────
# DATE DE TEST (simulate ca și cum ar fi venite din scraper)
# ─────────────────────────────────────────────────────────────

PRODUSE_EXEMPLU = [{"id": "60", "nume": "Asus VivoBook X441NA-GA190", "pret": 295.99, "pret_redus": None,
                    "descriere": "Laptop, Intel Celeron N3350 1.1GHz, 4GB, 500GB, Linux", "rating": 3,
                    "numar_reviewuri": 14, "url": "https://webscraper.io/test-sites/e-commerce/allinone/product/60",
                    "colectat_la": datetime.now(), },
                   {"id": "62", "nume": "Lenovo ThinkPad X240", "pret": 1099.99, "pret_redus": 899.99,
                    "descriere": "Ultrabook, Intel Core i5-4300U 1.9GHz, 8GB, 256GB SSD, Win10", "rating": 5,
                    "numar_reviewuri": 31, "url": "https://webscraper.io/test-sites/e-commerce/allinone/product/62",
                    "colectat_la": datetime.now(), },
                   {"id": "64", "nume": "HP 250 G6", "pret": 399.99, "pret_redus": None,
                    "descriere": "Laptop, Intel Core i3-6006U 2GHz, 4GB, 1TB, FreeDOS", "rating": 4,
                    "numar_reviewuri": 7, "url": "https://webscraper.io/test-sites/e-commerce/allinone/product/64",
                    "colectat_la": datetime.now(), },
                   {"id": "66", "nume": "Acer Aspire 3 A315-21", "pret": 249.99, "pret_redus": None,
                    "descriere": "Laptop, AMD E2-9000e 1.5GHz, 4GB, 500GB, Linux", "rating": 2, "numar_reviewuri": 3,
                    "url": "https://webscraper.io/test-sites/e-commerce/allinone/product/66",
                    "colectat_la": datetime.now(), },
                   {"id": "68", "nume": "Dell Inspiron 3576", "pret": 699.99, "pret_redus": 549.99,
                    "descriere": "Laptop, Intel Core i5-8250U 1.6GHz, 8GB, 256GB SSD + 1TB HDD, Win10", "rating": 5,
                    "numar_reviewuri": 42, "url": "https://webscraper.io/test-sites/e-commerce/allinone/product/68",
                    "colectat_la": datetime.now(), }, ]

separator = "─" * 60

# ─────────────────────────────────────────────────────────────
# PASUL 1: CONECTARE LA MONGODB
# ─────────────────────────────────────────────────────────────

print(f"\n{'═' * 60}")
print("  EXEMPLU MONGODB - Smart Product Scraper")
print(f"{'═' * 60}\n")

print("PASUL 1: Conectare la MongoDB...")

# MongoClient acceptă un URI de conexiune.
# Formate uzuale:
#   - Local: mongodb://localhost:27017
#   - Cu autentificare: mongodb://user:parola@localhost:27017
#   - MongoDB Atlas: mongodb+srv://user:parola@cluster.mongodb.net/
client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=3000)

try:
    # ping verifică dacă serverul răspunde (nu creează nicio bază de date)
    client.admin.command("ping")
    print("  → Conectat cu succes la MongoDB!\n")
except ConnectionFailure:
    print("  [EROARE] Nu s-a putut conecta la MongoDB.")
    print("  Asigurați-vă că serviciul MongoDB rulează:")
    print("    - Windows: net start MongoDB")
    print("    - Linux:   sudo systemctl start mongod")
    print("    - Docker:  docker run -d -p 27017:27017 mongo\n")
    exit(1)

# Selectăm (sau creăm automat) baza de date "scraper_db"
# MongoDB creează baza de date lazy: la primul insert, nu acum.
db = client["scraper_db"]

# Selectăm (sau creăm) colecția "produse"
# O colecție ≈ un tabel SQL, dar fără schemă fixă.
colectie = db["produse"]

# Ștergem datele anterioare pentru a porni demonstrația curat
colectie.drop()
print(f"  (Colecția 'produse' resetată pentru demonstrație)\n")

# ─────────────────────────────────────────────────────────────
# PASUL 2: INSERT - Inserare documente
# ─────────────────────────────────────────────────────────────

print(f"{separator}")
print("PASUL 2: INSERT - Inserare documente")
print(f"{separator}\n")

# --- insert_one: inserăm un singur document ---
print("  2a. insert_one() - inserare produs individual:")
rezultat_unul = colectie.insert_one(PRODUSE_EXEMPLU[0])

# MongoDB generează automat un _id unic (ObjectId) pentru fiecare document
print(f"      Produs inserat cu _id: {rezultat_unul.inserted_id}\n")

# --- insert_many: inserăm mai multe documente dintr-o dată ---
print("  2b. insert_many() - inserare mai multor produse simultan:")
rezultat_multi = colectie.insert_many(PRODUSE_EXEMPLU[1:])
print(f"      {len(rezultat_multi.inserted_ids)} produse inserate")
print(f"      ID-uri: {[str(oid) for oid in rezultat_multi.inserted_ids[:2]]}...\n")

# ─────────────────────────────────────────────────────────────
# PASUL 3: READ - Interogare documente
# ─────────────────────────────────────────────────────────────

print(f"{separator}")
print("PASUL 3: READ - Interogare documente")
print(f"{separator}\n")

# --- find_one: găsim un singur document ---
print("  3a. find_one() - primul produs din colecție:")
produs = colectie.find_one()
print(f"      Găsit: {produs['nume']} (${produs['pret']})\n")

# --- find cu filtru simplu ---
print("  3b. find() cu filtru simplu - produse cu rating 5:")
produse_top = list(colectie.find({"rating": 5}))
for p in produse_top:
    print(f"      • {p['nume']} - ${p['pret']:.2f}")
print()

# --- find cu operatori de comparație ---
# Operatori MongoDB: $gt (>), $gte (>=), $lt (<), $lte (<=), $ne (!=)
print("  3c. find() cu operatori - produse între $300 și $800:")
produse_medii = list(colectie.find({"pret": {"$gte": 300, "$lte": 800}}))
for p in produse_medii:
    print(f"      • {p['nume']} - ${p['pret']:.2f}")
print()

# --- find cu proiecție (selectăm doar câmpurile dorite) ---
# 1 = include câmpul, 0 = exclude câmpul
# _id este inclus implicit; îl excludem explicit cu _id: 0
print("  3d. find() cu proiecție - doar nume și preț:")
produse_partial = list(colectie.find({}, {"_id": 0, "nume": 1, "pret": 1}))
for p in produse_partial:
    print(f"      • {p}")
print()

# --- find cu sort și limit ---
print("  3e. find() cu sort și limit - top 3 cele mai scumpe:")
top_scumpe = list(colectie.find({}, {"_id": 0, "nume": 1, "pret": 1}).sort("pret", DESCENDING).limit(3))
for i, p in enumerate(top_scumpe, 1):
    print(f"      {i}. {p['nume']} - ${p['pret']:.2f}")
print()

# --- Filtrare după câmp cu valoare null ---
print("  3f. find() - produse fără reducere (pret_redus: null):")
fara_reducere = colectie.count_documents({"pret_redus": None})
print(f"      {fara_reducere} produse fără reducere\n")

# ─────────────────────────────────────────────────────────────
# PASUL 4: UPDATE - Actualizare documente
# ─────────────────────────────────────────────────────────────

print(f"{separator}")
print("PASUL 4: UPDATE - Actualizare documente")
print(f"{separator}\n")

# --- update_one: actualizăm un singur document ---
# $set actualizează câmpurile specificate (fără a șterge restul documentului)
print("  4a. update_one() - adăugăm reducere la HP 250 G6:")
rezultat = colectie.update_one({"id": "64"},  # filtrul: ce document să actualizăm
                               {"$set": {"pret_redus": 349.99}}  # operația: ce câmp să modificăm
                               )
print(f"      Documente găsite: {rezultat.matched_count}")
print(f"      Documente modificate: {rezultat.modified_count}\n")

# Verificăm actualizarea
hp = colectie.find_one({"id": "64"}, {"_id": 0, "nume": 1, "pret": 1, "pret_redus": 1})
print(f"      HP după actualizare: {hp}\n")

# --- update_many: actualizăm toate documentele care corespund filtrului ---
# $inc incrementează valoarea unui câmp numeric
print("  4b. update_many() - incrementăm rating-ul pentru produsele ieftine (< $300):")
rezultat = colectie.update_many({"pret": {"$lt": 300}}, {"$inc": {"rating": 1}})
print(f"      Documente modificate: {rezultat.modified_count}\n")

# --- upsert: inserează dacă nu există, actualizează dacă există ---
print("  4c. update_one() cu upsert=True - actualizare sau inserare:")
rezultat = colectie.update_one({"id": "999"}, {"$set": {"nume": "Produs Nou Test", "pret": 199.99, "rating": 3}},
                               upsert=True  # dacă id="999" nu există, creează documentul
                               )
print(f"      Document nou creat (upserted_id): {rezultat.upserted_id}\n")

# ─────────────────────────────────────────────────────────────
# PASUL 5: DELETE - Ștergere documente
# ─────────────────────────────────────────────────────────────

print(f"{separator}")
print("PASUL 5: DELETE - Ștergere documente")
print(f"{separator}\n")

# --- delete_one: ștergem un singur document ---
print("  5a. delete_one() - ștergem produsul de test (id: 999):")
rezultat = colectie.delete_one({"id": "999"})
print(f"      Documente șterse: {rezultat.deleted_count}\n")

# --- delete_many: ștergem mai multe documente ---
print("  5b. delete_many() - ștergem produsele cu rating <= 2:")
rezultat = colectie.delete_many({"rating": {"$lte": 2}})
print(f"      Documente șterse: {rezultat.deleted_count}\n")

# Numărul total de documente rămase
total = colectie.count_documents({})
print(f"  Documente rămase în colecție: {total}\n")

# ─────────────────────────────────────────────────────────────
# PASUL 6: INDEXURI - Optimizare interogări
# ─────────────────────────────────────────────────────────────

print(f"{separator}")
print("PASUL 6: INDEXURI - Optimizare interogări")
print(f"{separator}\n")

# Fără index: MongoDB scanează TOATE documentele la fiecare interogare (O(n))
# Cu index: MongoDB folosește structuri B-tree pentru căutare rapidă (O(log n))
# Indexurile sunt esențiale pentru colecții mari (>10.000 documente)

print("  6a. Creare index pe câmpul 'pret' (pentru sortare rapidă):")
colectie.create_index([("pret", ASCENDING)], name="idx_pret")
print("      → Index 'idx_pret' creat\n")

print("  6b. Creare index unic pe câmpul 'id' (previne duplicate):")
colectie.create_index([("id", ASCENDING)], unique=True, name="idx_id_unic")
print("      → Index unic 'idx_id_unic' creat\n")

print("  6c. Listare indexuri existente pe colecție:")
for index in colectie.list_indexes():
    print(f"      • {index['name']}: {index['key']}")
print()

# Test index unic - tentativă de inserare duplicat
print("  6d. Test index unic - inserare duplicat (ar trebui să eșueze):")
try:
    colectie.insert_one({"id": "60", "nume": "Duplicat Test"})
    print("      [?] Duplicatul a fost inserat (neașteptat!)")
except DuplicateKeyError:
    print("      → DuplicateKeyError: indexul unic a blocat duplicatul (corect!)\n")

# ─────────────────────────────────────────────────────────────
# PASUL 7: AGGREGATION PIPELINE (interogări avansate)
# ─────────────────────────────────────────────────────────────

print(f"{separator}")
print("PASUL 7: AGGREGATION PIPELINE")
print(f"{separator}\n")

# Aggregation pipeline = secvență de operații aplicate pe documente
# Similar cu GROUP BY + aggregate functions din SQL
# Fiecare etapă ($match, $group, $sort) transformă documentele

print("  7a. Statistici pe colecție (avg preț, min, max):")

pipeline_statistici = [  # Etapa 1: $group - grupăm TOATE documentele (fără cheie de grupare)
    # și calculăm statistici agregate
    {"$group": {"_id": None, "pret_mediu": {"$avg": "$pret"}, "pret_minim": {"$min": "$pret"},
                "pret_maxim": {"$max": "$pret"}, "numar_produse": {"$sum": 1}, }}]

rezultat = list(colectie.aggregate(pipeline_statistici))
if rezultat:
    stats = rezultat[0]
    print(f"      Număr produse:  {stats['numar_produse']}")
    print(f"      Preț mediu:     ${stats['pret_mediu']:.2f}")
    print(f"      Preț minim:     ${stats['pret_minim']:.2f}")
    print(f"      Preț maxim:     ${stats['pret_maxim']:.2f}\n")

print("  7b. Produse cu reducere, sortate după economie descrescător:")

pipeline_reduceri = [  # Etapa 1: $match - filtrăm doar produsele cu reducere
    {"$match": {"pret_redus": {"$ne": None}}},

    # Etapa 2: $addFields - calculăm economie = pret - pret_redus
    {"$addFields": {"economie": {"$subtract": ["$pret", "$pret_redus"]}}},

    # Etapa 3: $sort - sortăm descrescător după economie
    {"$sort": {"economie": DESCENDING}},

    # Etapa 4: $project - selectăm câmpurile de afișat
    {"$project": {"_id": 0, "nume": 1, "pret": 1, "pret_redus": 1, "economie": 1, }}, ]

for p in colectie.aggregate(pipeline_reduceri):
    print(f"      • {p['nume']}")
    print(f"        ${p['pret']:.2f} → ${p['pret_redus']:.2f} (economie: ${p['economie']:.2f})")
print()

# ─────────────────────────────────────────────────────────────
# PASUL 8: ÎNCHIDERE CONEXIUNE
# ─────────────────────────────────────────────────────────────

client.close()
print(f"{separator}")
print("  Conexiunea la MongoDB a fost închisă.")
print(f"{separator}\n")

# ─────────────────────────────────────────────────────────────
# REZUMAT CONCEPTUAL
# ─────────────────────────────────────────────────────────────
#
# Operații CRUD în MongoDB vs. SQL:
#
#   SQL                              MongoDB (PyMongo)
#   ──────────────────────────────   ──────────────────────────────────
#   INSERT INTO produse (...)        colectie.insert_one({...})
#   INSERT INTO produse VALUES       colectie.insert_many([{...}, {...}])
#   SELECT * FROM produse            colectie.find()
#   SELECT * WHERE pret > 300        colectie.find({"pret": {"$gt": 300}})
#   SELECT nume, pret                colectie.find({}, {"nume": 1, "pret": 1})
#   ORDER BY pret DESC LIMIT 3       .sort("pret", -1).limit(3)
#   UPDATE SET pret_redus=X WHERE    colectie.update_one(filtru, {"$set": {...}})
#   DELETE FROM WHERE                colectie.delete_many(filtru)
#   CREATE INDEX                     colectie.create_index(...)
#   GROUP BY, AVG, COUNT             colectie.aggregate([{"$group": {...}}])
#
# CÂND SĂ FOLOSEȘTI MONGODB ÎN LOC DE SQL:
#   ✓ Date semi-structurate (nu toate produsele au aceleași câmpuri)
#   ✓ Scalare orizontală pentru volume mari de date
#   ✓ Prototipare rapidă (schema flexibilă, fără migrări)
#   ✓ Documente imbricate (ex: produse cu array de review-uri)
#
# CÂND SQL ESTE MAI POTRIVIT:
#   ✓ Date puternic relaționale (JOIN-uri complexe)
#   ✓ Tranzacții ACID stricte (ex: plăți, stocuri)
#   ✓ Raportare și analiză complexă cu GROUP BY
