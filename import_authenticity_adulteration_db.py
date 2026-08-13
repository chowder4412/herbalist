#!/usr/bin/env python3
"""
================================================================================
🌿 HERBALIST AI — DIGITAL PHARMACOPEIA & ADULTERATION AUTHENTICITY ENGINE
================================================================================
Integrates findings from seminal computer vision & molecular authenticity papers:

1. "Digital herbal pharmacopeia as a solution for herbal plant identification based 
   on computer vision" (Riyanta et al., 2025)
   - Benchmark 96% CNN computer vision leaf morphology thresholds for Vision AI.

2. "Medicinal Plants Recommended by WHO: DNA Barcode Identification Associated with 
   Chemical Analyses Guarantees Their Quality" (PLOS ONE / PMC4433216)
   - DNA barcoding markers (matK, rbcL, ITS2) & commercial adulteration detection rules 
     preventing 71% market substitution risks (e.g. Cinnamon, Ginkgo, Ginseng).
================================================================================
"""

import os
import sys
import json
import sqlite3
import logging
from clinical_memory import ClinicalMemoryStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logger = logging.getLogger("herbalist.authenticity")

# ── DNA BARCODE & ADULTERATION ALERT DATASET (PMC4433216 & RIYANTA 2025) ──
ADULTERATION_AUTHENTICITY_DATASET = [
    {
        "herb_id": "AUTH-001",
        "authentic_species": "Cinnamomum verum J.Presl (Ceylon / True Cinnamon)",
        "common_adulterant": "Cinnamomum cassia (L.) J.Presl (Cassia Cinnamon)",
        "adulteration_risk_pct": 71.0,
        "dna_barcode_marker": "matK / ITS2 loci sequence divergence",
        "toxicological_hazard": "Cassia contains high coumarin (up to 1%, hepatotoxic); Ceylon contains trace coumarin (<0.004%)",
        "home_authenticity_test": "Ceylon cinnamon rolls in paper-thin fragile layers with sweet aroma; Cassia is thick, dark brown, hard wood-like single quills with harsh pungent taste.",
        "cv_vision_confidence_threshold": 0.96
    },
    {
        "herb_id": "AUTH-002",
        "authentic_species": "Panax ginseng C.A.Mey. (Asian Ginseng)",
        "common_adulterant": "Panax quinquefolius or Pfaffia paniculata (Brazilian Ginseng)",
        "adulteration_risk_pct": 45.0,
        "dna_barcode_marker": "rbcL / ITS2 region barcode differentiation",
        "toxicological_hazard": "Lacks specific ginsenosides (Rg1, Rb1 ratio); diminished adaptogenic efficacy",
        "home_authenticity_test": "True Panax ginseng root has distinct human-like branching roots with bittersweet ginsenoside taste.",
        "cv_vision_confidence_threshold": 0.95
    },
    {
        "herb_id": "AUTH-003",
        "authentic_species": "Ginkgo biloba L. (Maidenhair Tree)",
        "common_adulterant": "Sophora japonica extract enriched with synthetic quercetin/rutin",
        "adulteration_risk_pct": 60.0,
        "dna_barcode_marker": "matK barcode & HPLC flavonol glycoside ratio analysis",
        "toxicological_hazard": "Adulterated extracts lack terpene trilactones (ginkgolides A, B, C) crucial for cerebral microcirculation",
        "home_authenticity_test": "True Ginkgo extract displays 24% flavonol glycosides + 6% terpene lactones; authentic leaves have unique bi-lobed fan shape.",
        "cv_vision_confidence_threshold": 0.98
    },
    {
        "herb_id": "AUTH-004",
        "authentic_species": "Matricaria chamomilla L. (German Chamomile)",
        "common_adulterant": "Anthemis cotula L. (Stinking Mayweed / Dog Fennel)",
        "adulteration_risk_pct": 30.0,
        "dna_barcode_marker": "ITS2 locus barcoding & essential oil bisabolol profiling",
        "toxicological_hazard": "Anthemis cotula causes severe contact dermatitis, mucous membrane irritation, and nausea",
        "home_authenticity_test": "True German Chamomile flower heads have hollow receptacles with sweet apple-like scent; Mayweed has solid receptacles with acrid foul smell.",
        "cv_vision_confidence_threshold": 0.96
    }
]

def init_authenticity_schema():
    """Initializes Adulteration & Authenticity SQLite table in clinical_memory.db"""
    memory = ClinicalMemoryStore()
    conn = memory.get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plant_adulteration_authenticity (
            id                              INTEGER PRIMARY KEY AUTOINCREMENT,
            herb_id                         TEXT UNIQUE NOT NULL,
            authentic_species               TEXT NOT NULL,
            common_adulterant               TEXT NOT NULL,
            adulteration_risk_pct           REAL,
            dna_barcode_marker              TEXT,
            toxicological_hazard            TEXT,
            home_authenticity_test          TEXT,
            cv_vision_confidence_threshold  REAL,
            updated_at                      DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_auth_species ON plant_adulteration_authenticity(authentic_species);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_auth_adulterant ON plant_adulteration_authenticity(common_adulterant);')

    conn.commit()
    conn.close()
    logger.info(" Adulteration & Authenticity Database schema initialized successfully.")

def seed_authenticity_database():
    """Seeds DNA Barcoding & Adulteration rules into persistent SQLite storage"""
    init_authenticity_schema()
    memory = ClinicalMemoryStore()
    conn = memory.get_connection()
    cursor = conn.cursor()

    inserted_count = 0
    for a in ADULTERATION_AUTHENTICITY_DATASET:
        cursor.execute('''
            INSERT OR REPLACE INTO plant_adulteration_authenticity
            (herb_id, authentic_species, common_adulterant, adulteration_risk_pct, dna_barcode_marker, toxicological_hazard, home_authenticity_test, cv_vision_confidence_threshold)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            a["herb_id"],
            a["authentic_species"],
            a["common_adulterant"],
            a["adulteration_risk_pct"],
            a["dna_barcode_marker"],
            a["toxicological_hazard"],
            a["home_authenticity_test"],
            a["cv_vision_confidence_threshold"]
        ))
        inserted_count += 1

        # Cross-sync into main semantic_pharmacopeia table for Vision AI & Pharmacopeia Explorer
        herb_key = a["authentic_species"].split()[0].lower() + "_authenticity"
        cursor.execute('''
            INSERT OR REPLACE INTO semantic_pharmacopeia
            (herb_key, common_name, botanical_name, category, active_bioactives, therapeutic_properties, layman_nutrient_name, discovered_from_llm)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            herb_key,
            a["authentic_species"],
            a["authentic_species"],
            "DNA Barcode & Adulteration Authenticity Engine",
            f"DNA Markers: {a['dna_barcode_marker']}",
            f"Adulterant Risk ({a['adulteration_risk_pct']}%): {a['common_adulterant']} | Hazard: {a['toxicological_hazard']}",
            "Purity Verification Test Suite",
            "PMC4433216 & Riyanta et al. Computer Vision 2025"
        ))

    conn.commit()
    conn.close()
    logger.info(f" Adulteration & Authenticity Sync Complete! Cataloged {inserted_count} DNA barcoding adulteration profiles.")
    return inserted_count

def search_authenticity_database(query: str):
    """Searches Adulteration & Authenticity Database by plant species or common name"""
    memory = ClinicalMemoryStore()
    conn = memory.get_connection()
    cursor = conn.cursor()

    q = f"%{query.strip().lower()}%"
    cursor.execute('''
        SELECT herb_id, authentic_species, common_adulterant, adulteration_risk_pct, toxicological_hazard, home_authenticity_test, cv_vision_confidence_threshold
        FROM plant_adulteration_authenticity
        WHERE LOWER(authentic_species) LIKE ? OR LOWER(common_adulterant) LIKE ? OR LOWER(home_authenticity_test) LIKE ?
    ''', (q, q, q))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "herb_id": r[0],
            "authentic_species": r[1],
            "common_adulterant": r[2],
            "adulteration_risk_pct": r[3],
            "toxicological_hazard": r[4],
            "home_authenticity_test": r[5],
            "cv_vision_confidence_threshold": r[6]
        } for r in rows
    ]

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    count = seed_authenticity_database()
    print(f"Authenticity & Adulteration Seeding Result: {count} profiles imported.")
    test_search = search_authenticity_database("Cinnamomum")
    print(f"Authenticity Search Test Result ('Cinnamomum'): {test_search}")
