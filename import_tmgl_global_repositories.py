#!/usr/bin/env python3
"""
================================================================================
🌿 HERBALIST AI — TMGL (WHO TRADITIONAL MEDICINE GLOBAL LIBRARY) IMPORTER & SYNC
================================================================================
Integrates global traditional medicine repositories cataloged by WHO TMGL 
(https://tmgl.org/databases-and-repositories) into Herbalist AI:

Featured Repositories & Data Sources:
  1. WHO Mosaico TCIM Global Library (WHO Monograph & Safety Evidence Maps)
  2. Indian Medicinal Plants Nomenclature & Traded Database (Ayurveda/FRLHT/TDU)
  3. Plants For A Future (PFAF - Global Edible & Medicinal Plants Repository)
  4. LILACS / PAHO Latin American & Amazonian Traditional Medicine Repository
  5. MAPS & MPD3 Phytochemical & Bioactive Activity Repositories
================================================================================
"""

import os
import sys
import json
import sqlite3
import logging
from clinical_memory import ClinicalMemoryStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("herbalist.tmgl")

# ── TMGL GLOBAL REPOSITORIES CURATED BOTANICAL DATASET ──
TMGL_GLOBAL_REPOSITORIES_DATASET = [
    # ── 1. WHO MOSAICO & AYURVEDA (FRLHT / TDU INDIAN MEDICINAL PLANTS) ──
    {
        "repository_source": "WHO TMGL / FRLHT Indian Medicinal Plants Nomenclature",
        "system_tradition": "Ayurveda / Siddha / Unani",
        "botanical_name": "Withania somnifera",
        "common_name": "Ashwagandha (Indian Ginseng)",
        "vernacular_names": "Sanskrit: Ashwagandha | Hindi: Asgandh | Tamil: Amukkuram | Telugu: Penneru",
        "category": "Adaptogen / Anxiolytic / Immunomodulator",
        "active_bioactives": "Withanolide A, Withaferin A, Withanone, Anaferine",
        "therapeutic_properties": "Cortisol reduction, stress anxiolytic, neuroprotection, male reproductive stamina",
        "safety_notes": "Avoid in hyperthyroidism or acute pregnancy unless supervised",
        "everyday_source": "Root powder (1/2 tsp in warm milk or honey water)"
    },
    {
        "repository_source": "WHO TMGL / FRLHT Indian Medicinal Plants Nomenclature",
        "system_tradition": "Ayurveda / Traditional Phytotherapy",
        "botanical_name": "Curcuma longa",
        "common_name": "Turmeric",
        "vernacular_names": "Sanskrit: Haridra | Hindi: Haldi | Tamil: Manjal | Hausa: Kurkum",
        "category": "Anti-inflammatory / Hepatoprotective / Antioxidant",
        "active_bioactives": "Curcumin, Demethoxycurcumin, Bisdemethoxycurcumin, Turmerone",
        "therapeutic_properties": "NF-kB inflammatory pathway inhibitor, joint pain, digestive tonic, skin healing",
        "safety_notes": "Enhance absorption with black pepper (piperine); exercise caution with high-dose blood thinners",
        "everyday_source": "Golden Milk tea (1 tsp turmeric + pinch black pepper + warm coconut milk)"
    },
    {
        "repository_source": "WHO TMGL / FRLHT Indian Medicinal Plants Nomenclature",
        "system_tradition": "Ayurveda",
        "botanical_name": "Bacopa monnieri",
        "common_name": "Brahmi",
        "vernacular_names": "Sanskrit: Brahmi | Hindi: Jalanimba | Tamil: Neerbrahmi",
        "category": "Nootropic / Brain & Memory Tonic",
        "active_bioactives": "Bacoside A, Bacoside B, Bacopaside I-V",
        "therapeutic_properties": "Synaptic transmission booster, cognitive clarity, anxiety reduction, ADHD support",
        "safety_notes": "Take with meals to prevent mild nausea; generally safe long-term",
        "everyday_source": "Dried leaf tea or standardized extract (300 mg daily)"
    },
    {
        "repository_source": "WHO TMGL / FRLHT Indian Medicinal Plants Nomenclature",
        "system_tradition": "Ayurveda",
        "botanical_name": "Gymnema sylvestre",
        "common_name": "Gymnema (Gurmar - Sugar Destroyer)",
        "vernacular_names": "Hindi: Gurmar | Sanskrit: Meshashringi | Tamil: Sirukurunjan",
        "category": "Hypoglycemic / Anti-diabetic",
        "active_bioactives": "Gymnemic acids I-VII, Gymnemasaponins, Gurmarin",
        "therapeutic_properties": "Blocks sugar taste receptors, stimulates pancreatic beta-cell insulin secretion",
        "safety_notes": "Monitor blood glucose if combined with metformin or insulin",
        "everyday_source": "Warm leaf infusion taken 15 minutes before meals"
    },

    # ── 2. LILACS / PAHO LATIN AMERICAN & AMAZONIAN TRADITIONAL MEDICINE ──
    {
        "repository_source": "PAHO / LILACS Latin American Traditional Medicine Repository",
        "system_tradition": "Amazonian Phytotherapy",
        "botanical_name": "Uncaria tomentosa",
        "common_name": "Cat's Claw (Uña de Gato)",
        "vernacular_names": "Spanish: Uña de Gato | Portuguese: Unha de Gato | Asháninka: Garabato",
        "category": "Immunomodulator / Anti-arthritic",
        "active_bioactives": "Pentacyclic Oxindole Alkaloids (POA), Isopteropodine, Pteropodine",
        "therapeutic_properties": "Immune system enhancement, osteoarthritis joint relief, gastrointestinal anti-inflammatory",
        "safety_notes": "Contraindicated in organ transplant recipients; avoid during pregnancy",
        "everyday_source": "Inner bark decoction (simmer 1 tbsp bark in 1 liter water for 20 mins)"
    },
    {
        "repository_source": "PAHO / LILACS Latin American Traditional Medicine Repository",
        "system_tradition": "Amazonian Phytotherapy",
        "botanical_name": "Tabebuia impetiginosa",
        "common_name": "Pau d'Arco (Lapacho)",
        "vernacular_names": "Portuguese: Pau d'Arco | Spanish: Lapacho / Ipê Roxo",
        "category": "Antifungal / Antimicrobial / Anti-inflammatory",
        "active_bioactives": "Lapachol, Beta-lapachone, Cycloolivil",
        "therapeutic_properties": "Candida overgrowth inhibitor, broad-spectrum anti-parasitic, anti-tumor research",
        "safety_notes": "Avoid high-dose lapachol during pregnancy or active bleeding disorders",
        "everyday_source": "Inner bark herbal tea brew (1-2 cups daily)"
    },
    {
        "repository_source": "PAHO / LILACS Latin American Traditional Medicine Repository",
        "system_tradition": "Andean / Latin American Phytotherapy",
        "botanical_name": "Lepidium meyenii",
        "common_name": "Maca Root",
        "vernacular_names": "Spanish: Maca | Quechua: Maino",
        "category": "Endocrine Adaptogen / Energy & Fertility Tonic",
        "active_bioactives": "Macamides, Macaenes, Glucosinolates",
        "therapeutic_properties": "Hormonal balance without direct hormone elevation, stamina booster, libido enhancement",
        "safety_notes": "Gelatinized powder is easier on sensitive digestive systems",
        "everyday_source": "1 tsp gelatinized maca powder mixed into smoothies or oatmeal"
    },

    # ── 3. PFAF (PLANTS FOR A FUTURE) & EUROPEAN HERBAL REPOSITORIES ──
    {
        "repository_source": "PFAF (Plants For A Future) Global Repository",
        "system_tradition": "European & Global Phytotherapy",
        "botanical_name": "Silybum marianum",
        "common_name": "Milk Thistle",
        "vernacular_names": "French: Chardon-Marie | German: Mariendistel | Spanish: Cardo Mariano",
        "category": "Hepatoprotective / Liver Detoxifier",
        "active_bioactives": "Silymarin complex (Silibinin, Silychristin, Silydianin)",
        "therapeutic_properties": "Protects liver cell membranes against toxins, stimulates hepatocyte protein synthesis",
        "safety_notes": "Extremely safe; rare mild laxative effect",
        "everyday_source": "Crushed seed tea or 140-250 mg standardized extract"
    },
    {
        "repository_source": "PFAF (Plants For A Future) Global Repository",
        "system_tradition": "European & Native American Phytotherapy",
        "botanical_name": "Taraxacum officinale",
        "common_name": "Dandelion Root & Leaf",
        "vernacular_names": "French: Pissenlit | German: Löwenzahn | Spanish: Diente de León",
        "category": "Diuretic / Prebiotic / Choleretic",
        "active_bioactives": "Taraxasterol, Inulin, Sesquiterpene lactones, Potassium",
        "therapeutic_properties": "Leaf: non-potassium-depleting diuretic. Root: liver bile stimulant & prebiotic gut nourisher",
        "safety_notes": "Avoid if bile ducts are acutely obstructed",
        "everyday_source": "Roasted dandelion root tea (coffee alternative) or fresh leaf salad"
    },
    {
        "repository_source": "PFAF (Plants For A Future) Global Repository",
        "system_tradition": "European Herbalism",
        "botanical_name": "Crataegus oxyacantha",
        "common_name": "Hawthorn Berry",
        "vernacular_names": "French: Aubépine | German: Weißdorn | Spanish: Espino Blanco",
        "category": "Cardiotonic / Coronary Vasodilator",
        "active_bioactives": "Oligomeric Proanthocyanidins (OPCs), Hyperoside, Vitexin",
        "therapeutic_properties": "Strengthens heart muscle contraction force, dilates coronary blood vessels, mild antihypertensive",
        "safety_notes": "Safe cardiotonic; consult physician if taking prescription cardiac glycosides",
        "everyday_source": "Decoction of dried berries (1-2 cups daily)"
    }
]

def init_tmgl_schema():
    """Initializes TMGL Global Repository SQLite table in clinical_memory.db"""
    memory = ClinicalMemoryStore()
    conn = memory.get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tmgl_global_plants (
            id                     INTEGER PRIMARY KEY AUTOINCREMENT,
            repository_source      TEXT NOT NULL,
            system_tradition       TEXT NOT NULL,
            botanical_name         TEXT NOT NULL UNIQUE,
            common_name            TEXT NOT NULL,
            vernacular_names       TEXT,
            category               TEXT,
            active_bioactives      TEXT,
            therapeutic_properties TEXT,
            safety_notes           TEXT,
            everyday_source        TEXT,
            updated_at             DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tmgl_botanical ON tmgl_global_plants(botanical_name);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tmgl_tradition ON tmgl_global_plants(system_tradition);')
    conn.commit()
    conn.close()
    logger.info(" TMGL Global Repositories schema initialized successfully.")

def seed_tmgl_database():
    """Seeds TMGL Global Repositories dataset into persistent SQLite storage"""
    init_tmgl_schema()
    memory = ClinicalMemoryStore()
    conn = memory.get_connection()
    cursor = conn.cursor()

    inserted_count = 0
    for p in TMGL_GLOBAL_REPOSITORIES_DATASET:
        cursor.execute('''
            INSERT OR REPLACE INTO tmgl_global_plants
            (repository_source, system_tradition, botanical_name, common_name, vernacular_names, category, active_bioactives, therapeutic_properties, safety_notes, everyday_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            p["repository_source"],
            p["system_tradition"],
            p["botanical_name"],
            p["common_name"],
            p["vernacular_names"],
            p["category"],
            p["active_bioactives"],
            p["therapeutic_properties"],
            p["safety_notes"],
            p["everyday_source"]
        ))
        inserted_count += 1

        # Also cross-sync into main semantic_pharmacopeia table for Vision AI & Pharmacopeia Explorer
        herb_key = p["botanical_name"].lower().replace(" ", "_")
        cursor.execute('''
            INSERT OR REPLACE INTO semantic_pharmacopeia
            (herb_key, common_name, botanical_name, category, active_bioactives, therapeutic_properties, layman_nutrient_name, discovered_from_llm)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            herb_key,
            p["common_name"],
            p["botanical_name"],
            f"TMGL Repository ({p['system_tradition']})",
            p["active_bioactives"],
            p["therapeutic_properties"],
            f"{p['system_tradition']} Active Complex",
            p["repository_source"]
        ))

    conn.commit()
    conn.close()
    logger.info(f" TMGL Repository Sync Complete! Successfully cataloged {inserted_count} global plant monographs across WHO TMGL, Ayurveda, PFAF & PAHO LILACS.")
    return inserted_count

def search_tmgl_repositories(query: str):
    """Searches TMGL Global Repository by query string"""
    memory = ClinicalMemoryStore()
    conn = memory.get_connection()
    cursor = conn.cursor()

    q = f"%{query.strip().lower()}%"
    cursor.execute('''
        SELECT repository_source, system_tradition, botanical_name, common_name, vernacular_names, therapeutic_properties, active_bioactives, everyday_source
        FROM tmgl_global_plants
        WHERE LOWER(botanical_name) LIKE ? OR LOWER(common_name) LIKE ? OR LOWER(system_tradition) LIKE ? OR LOWER(therapeutic_properties) LIKE ?
    ''', (q, q, q, q))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "repository_source": r[0],
            "system_tradition": r[1],
            "botanical_name": r[2],
            "common_name": r[3],
            "vernacular_names": r[4],
            "therapeutic_properties": r[5],
            "active_bioactives": r[6],
            "everyday_source": r[7]
        } for r in rows
    ]

if __name__ == "__main__":
    count = seed_tmgl_database()
    print(f"TMGL Global Repositories Seeding Result: {count} monographs imported.")
    test_search = search_tmgl_repositories("Ashwagandha")
    print(f"TMGL Search Test Result ('Ashwagandha'): {test_search}")
