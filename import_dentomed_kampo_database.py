#!/usr/bin/env python3
"""
================================================================================
🌿 HERBALIST AI — DENTOMED / TOYAMA WAKAN-YAKU KAMPO DATABASE IMPORTER & SYNC
================================================================================
Integrates the Traditional Medical & Pharmaceutical Database (TradMPD / DentoMed)
from the Institute of Natural Medicine, University of Toyama, Japan 
(https://dentomed.toyama-wakan.net/en/) into Herbalist AI.

Focus: Japanese Kampo Traditional Medicine (Wakan-yaku), Crude Natural Drugs,
       Active Phytochemistry, and LC-MS Biological Target Profiles.
================================================================================
"""

import os
import sys
import json
import sqlite3
import logging
from clinical_memory import ClinicalMemoryStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("herbalist.dentomed")

# ── DENTOMED / TOYAMA WAKAN-YAKU KAMPO SEED DATASET ──
DENTOMED_KAMPO_DATASET = [
    {
        "formula_code": "KM-001",
        "kampo_name": "Kakuon-to (Kakkonto / Pueraria Decoction)",
        "japanese_kanji": "葛根湯",
        "crude_drugs": "Pueraria Root (Kudzu), Ephedra Herb, Ginger, Jujube, Cinnamon Bark, Paeonia Root, Glycyrrhiza",
        "active_bioactives": "Puerarin, Daidzein, Ephedrine, Gingerols, Cinnamaldehyde, Paeoniflorin, Glycyrrhizin",
        "clinical_indications": "Acute common cold, fever, upper back & neck stiffness, viral rhinitis, headache",
        "biological_targets": "TNF-alpha / IL-6 cytokine inhibition, COX-2 anti-inflammatory, diaphorite antipyretic",
        "traditional_dosing": "Warm decoction taken 3 times daily before meals"
    },
    {
        "formula_code": "KM-002",
        "kampo_name": "Rikkunshi-to (Six-Gentlemen Decoction)",
        "japanese_kanji": "六君子湯",
        "crude_drugs": "Ginseng, Atractylodes Rhizome, Poria Sclerotium, Glycyrrhiza, Citrus Unshiu Peel, Pinellia Tuber, Ginger, Jujube",
        "active_bioactives": "Ginsenosides, Atractylenolides, Hesperidin, Homogentisic acid, Glycyrrhizin",
        "biological_targets": "Ghrelin receptor sensitization, gastric emptying acceleration, anti-dyspepsia",
        "clinical_indications": "Functional dyspepsia, anorexia, GERD acid reflux, chronic gastritis, post-chemotherapy nausea",
        "traditional_dosing": "1 teacup 3 times daily before meals"
    },
    {
        "formula_code": "KM-003",
        "kampo_name": "Hochu-ekki-to (Bupleurum & Ginseng Decoction)",
        "japanese_kanji": "補中益気湯",
        "crude_drugs": "Ginseng, Atractylodes, Astragalus Root, Angelica Root, Bupleurum, Citrus Peel, Cimicifuga, Glycyrrhiza, Ginger, Jujube",
        "active_bioactives": "Astragalosides, Ginsenosides, Ferulic acid, Saikosaponins, Hesperidin",
        "biological_targets": "Immune system T-cell enhancement, cellular ATP energy production, anti-fatigue",
        "clinical_indications": "Chronic fatigue syndrome, post-illness weakness, organ ptosis, general immune exhaustion",
        "traditional_dosing": "Warm infusion twice daily"
    },
    {
        "formula_code": "KM-004",
        "kampo_name": "Shakuyaku-kanzo-to (Peony & Licorice Decoction)",
        "japanese_kanji": "芍薬甘草湯",
        "crude_drugs": "Paeonia Root (Peony), Glycyrrhiza (Licorice Root)",
        "active_bioactives": "Paeoniflorin, Glycyrrhizin, Isoliquiritigenin",
        "biological_targets": "Neuromuscular junction twitch relaxation, smooth muscle antispasmodic",
        "clinical_indications": "Acute muscle cramps, leg cramps, nocturnal calf spasms, abdominal colic",
        "traditional_dosing": "Single warm dose taken at onset of cramp/spasm"
    },
    {
        "formula_code": "KM-005",
        "kampo_name": "Shosaiko-to (Minor Bupleurum Decoction)",
        "japanese_kanji": "小柴胡湯",
        "crude_drugs": "Bupleurum Root, Scutellaria Root (Skullcap), Ginseng, Pinellia, Ginger, Jujube, Glycyrrhiza",
        "active_bioactives": "Saikosaponin A & D, Baicalin, Baicalein, Wogonin, Ginsenosides",
        "biological_targets": "Hepatoprotective, NF-kB hepatic fibrosis inhibitor, immune anti-viral",
        "clinical_indications": "Chronic hepatitis, liver dysfunction, subacute respiratory infections, intercostal fullness",
        "traditional_dosing": "3 times daily between meals"
    },
    {
        "formula_code": "KM-006",
        "kampo_name": "Orengedoku-to (Coptis Detox Decoction)",
        "japanese_kanji": "黄連解毒湯",
        "crude_drugs": "Coptis Rhizome, Scutellaria Root, Phellodendron Bark, Gardenia Fruit",
        "active_bioactives": "Berberine, Baicalin, Palmatine, Geniposide",
        "biological_targets": "Potent broad-spectrum antibacterial, endothelial vascular inflammation reducer, anti-hyperthermia",
        "clinical_indications": "Hypertensive heat flush, acute gastritis, irritability, eczema heat rash, insomnia",
        "traditional_dosing": "1 teacup twice daily"
    },
    {
        "formula_code": "KM-007",
        "kampo_name": "Hachimi-jio-gan (Eight-Ingredient Rehmannia Pill)",
        "japanese_kanji": "八味地黄丸",
        "crude_drugs": "Rehmannia Root, Cornus Fruit, Dioscorea Rhizome, Alisma Rhizome, Poria, Moutan Bark, Cinnamon Bark, Processed Aconite",
        "active_bioactives": "Catalpol, Loganin, Paeonol, Alisol, Cinnamaldehyde",
        "biological_targets": "Renal hemodynamics enhancement, insulin sensitivity improvement, anti-aging metabolic tonic",
        "clinical_indications": "Lumbago lower back pain, nocturnal polyuria, diabetic nephropathy support, cold extremities in elderly",
        "traditional_dosing": "Taken warm morning and evening"
    }
]

def init_dentomed_schema():
    """Initializes DentoMed / Toyama Wakan Kampo SQLite table in clinical_memory.db"""
    memory = ClinicalMemoryStore()
    conn = memory.get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dentomed_kampo_formulas (
            id                     INTEGER PRIMARY KEY AUTOINCREMENT,
            formula_code           TEXT UNIQUE NOT NULL,
            kampo_name             TEXT NOT NULL,
            japanese_kanji         TEXT,
            crude_drugs            TEXT NOT NULL,
            active_bioactives      TEXT,
            biological_targets     TEXT,
            clinical_indications   TEXT,
            traditional_dosing     TEXT,
            updated_at             DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_dentomed_kampo_name ON dentomed_kampo_formulas(kampo_name);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_dentomed_crude_drugs ON dentomed_kampo_formulas(crude_drugs);')
    conn.commit()
    conn.close()
    logger.info(" DentoMed Kampo (University of Toyama) schema initialized successfully.")

def seed_dentomed_database():
    """Seeds DentoMed / Toyama Wakan Kampo dataset into persistent SQLite storage"""
    init_dentomed_schema()
    memory = ClinicalMemoryStore()
    conn = memory.get_connection()
    cursor = conn.cursor()

    inserted_count = 0
    for k in DENTOMED_KAMPO_DATASET:
        cursor.execute('''
            INSERT OR REPLACE INTO dentomed_kampo_formulas
            (formula_code, kampo_name, japanese_kanji, crude_drugs, active_bioactives, biological_targets, clinical_indications, traditional_dosing)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            k["formula_code"],
            k["kampo_name"],
            k["japanese_kanji"],
            k["crude_drugs"],
            k["active_bioactives"],
            k["biological_targets"],
            k["clinical_indications"],
            k["traditional_dosing"]
        ))
        inserted_count += 1

        # Cross-sync into main semantic_pharmacopeia table for Vision AI & Pharmacopeia Explorer
        herb_key = k["kampo_name"].lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
        cursor.execute('''
            INSERT OR REPLACE INTO semantic_pharmacopeia
            (herb_key, common_name, botanical_name, category, active_bioactives, therapeutic_properties, layman_nutrient_name, discovered_from_llm)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            herb_key,
            k["kampo_name"],
            f"Japanese Kampo ({k['japanese_kanji']})",
            "DentoMed / Toyama Wakan-yaku Kampo",
            k["active_bioactives"],
            f"Indications: {k['clinical_indications']} | Targets: {k['biological_targets']}",
            "Kampo Crude Drug Bioactive Complex",
            "University of Toyama Institute of Natural Medicine (TradMPD)"
        ))

    conn.commit()
    conn.close()
    logger.info(f" DentoMed Sync Complete! Successfully cataloged {inserted_count} Japanese Kampo traditional formulas and crude drugs.")
    return inserted_count

def search_dentomed_kampo(query: str):
    """Searches DentoMed Kampo Database by query string"""
    memory = ClinicalMemoryStore()
    conn = memory.get_connection()
    cursor = conn.cursor()

    q = f"%{query.strip().lower()}%"
    cursor.execute('''
        SELECT formula_code, kampo_name, japanese_kanji, crude_drugs, active_bioactives, biological_targets, clinical_indications, traditional_dosing
        FROM dentomed_kampo_formulas
        WHERE LOWER(kampo_name) LIKE ? OR LOWER(crude_drugs) LIKE ? OR LOWER(clinical_indications) LIKE ? OR LOWER(active_bioactives) LIKE ?
    ''', (q, q, q, q))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "formula_code": r[0],
            "kampo_name": r[1],
            "japanese_kanji": r[2],
            "crude_drugs": r[3],
            "active_bioactives": r[4],
            "biological_targets": r[5],
            "clinical_indications": r[6],
            "traditional_dosing": r[7]
        } for r in rows
    ]

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    count = seed_dentomed_database()
    print(f"DentoMed Kampo Seeding Result: {count} formulas imported.")
    test_search = search_dentomed_kampo("Kakuon-to")
    print(f"DentoMed Kampo Search Test Result ('Kakuon-to'): {test_search}")

