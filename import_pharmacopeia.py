#!/usr/bin/env python3
"""
================================================================================
🌿 HERBALIST AI — BOTANICAL PHARMACOPEIA DATASET IMPORTER
================================================================================
Imports WHO Monographs, USDA Dr. Duke's Phytochemicals, IMPPAT, PFAF, and custom
CSV/JSON datasets directly into the persistent SQLite/Turso database.

Usage:
  python import_pharmacopeia.py --seed-all
  python import_pharmacopeia.py --file path/to/dataset.csv
  python import_pharmacopeia.py --json path/to/dataset.json
================================================================================
"""

import sys
import os
import json
import csv
import argparse
import logging
from clinical_memory import ClinicalMemoryStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("herbalist.importer")

# Curated Comprehensive WHO / USDA Dr. Duke's / IMPPAT / PFAF Dataset
EXTENDED_BOTANICAL_DATASET = [
    # ── AFRICAN & NIGERIAN PHYTOTHERAPY ──
    ("garcinia_kola", "Bitter Kola", "Garcinia kola", "African Phytotherapy", "Kolaviron, Garcinia biflavonoids GB1 & GB2, Cycloartenol", "Hepatoprotective, Anti-inflammatory, Respiratory support, Antiviral", "Bitter Kola Flavonoid Shield"),
    ("carica_papaya", "Papaya Leaf", "Carica papaya", "African Phytotherapy", "Papain, Carpaine, Chymopapain, Quercetin, Kaempferol", "Thrombocyte booster, Dengue/malaria recovery, Digestive, Anti-ulcer", "Platelet Enhancing Leaf"),
    ("psidium_guajava", "Guava Leaf", "Psidium guajava", "African Phytotherapy", "Quercetin, Guaijaverin, Ursolic acid, Ellagic acid", "Antidiarrheal, Antimicrobial, Hypoglycemic, Cardioprotective", "Antimicrobial Guava Leaf"),
    ("phyllanthus_niruri", "Stonebreaker (Chanca Piedra)", "Phyllanthus niruri", "African Phytotherapy", "Phyllanthin, Hypophyllanthin, Corilagin, Geraniin", "Urolithiasis (kidney stones), Hepatoprotective, Antiviral, Hypouricemic", "Kidney Stone Dissolver"),
    ("gongronema_latifolium", "Utazi / Bush Buck", "Gongronema latifolium", "African Phytotherapy", "Pregnane glycosides, Essential oils, Saponins, Alkaloids", "Hypoglycemic, Anti-inflammatory, Hepatoprotective, Digestive", "Bitters Diabetes Vine"),
    ("vernonia_amygdalina", "Bitter Leaf", "Vernonia amygdalina", "African Phytotherapy", "Vernodalin, Vernolepin, Luteolin, Vernomygdin", "Anti-diabetic, Anti-cancer, Antimalarial, Hepatoprotective", "African Bitter Leaf Cleanse"),
    ("hibiscus_sabdariffa", "Zobo / Roselle", "Hibiscus sabdariffa", "African Phytotherapy", "Delphinidin-3-sambubioside, Cyanidin-3-sambubioside, Hibiscic acid", "Antihypertensive, Hypolipidemic, Diuretic, Nephroprotective", "Hibiscus Vascular Tea"),
    ("cassia_alata", "Ringworm Bush (Asunwon)", "Senna alata", "African Phytotherapy", "Rhein, Chrysophanol, Aloe-emodin, Kaempferol", "Antifungal, Dermatological, Antibacterial, Laxative", "Fungal & Skin Repair Leaf"),
    ("ocimum_gratissimum", "Scent Leaf (Efirin)", "Ocimum gratissimum", "African Phytotherapy", "Eugenol, Thymol, Citral, Linalool", "Antimicrobial, Antispasmodic, Antidiarrheal, Anti-inflammatory", "Eugenol Antimicrobial Leaf"),
    ("moringa_oleifera", "Moringa", "Moringa oleifera", "African Phytotherapy", "Moringinine, Quercetin, Chlorogenic acid, Isothiocyanates", "Nutritive, Hypoglycemic, Antioxidant, Anti-inflammatory", "Nutrient-Dense Superfood"),
    ("garcinia_mangostana", "Mangosteen", "Garcinia mangostana", "African Phytotherapy", "Alpha-mangostin, Gamma-mangostin, Xanthones", "Anti-inflammatory, Anti-cancer, Antioxidant, Antibacterial", "Xanthone Fruit Shield"),
    ("aloe_ferox", "Cape Aloe", "Aloe ferox", "African Phytotherapy", "Aloin, Aloe-emodin, Polymannans, Glycoproteins", "Laxative, Wound healing, Anti-inflammatory, Immune-boosting", "Cape Aloe Skin & Gut Gel"),

    # ── WHO MONOGRAPHS & DR. DUKE'S USDA SEEDS ──
    ("syzygium_cumini", "Jamun / Black Plum", "Syzygium cumini", "Ayurveda", "Jamboline, Ellagic acid, Anthocyanins, Ferulic acid", "Anti-diabetic, Pancreatic beta-cell protector, Hypoglycemic", "Diabetes Jamun Fruit"),
    ("momordica_charantia", "Bitter Melon", "Momordica charantia", "Ayurveda", "Charantin, Vicine, Polypeptide-p, Kuguacin", "Insulin-mimetic, Hypoglycemic, AMPK activator, Lipid lowering", "Insulin-Mimetic Bitter Gourd"),
    ("gymnema_sylvestre", "Gymnema (Gurmar)", "Gymnema sylvestre", "Ayurveda", "Gymnemic acids, Gymnemasaponins, Gurmarin", "Sugar craving blocker, Pancreatic regenerative, Hypoglycemic", "Sugar Destroyer Vine"),
    ("nigella_sativa", "Black Seed (Habbat al-Barakah)", "Nigella sativa", "Arabian & Unani", "Thymoquinone, Thymohydroquinone, Dithymoquinone, Nigellone", "Immunomodulatory, Bronchodilator, Antihypertensive, Neuroprotective", "Prophetic Healing Seed"),
    ("olea_europaea", "Olive Leaf", "Olea europaea", "Arabian & Unani", "Oleuropein, Hydroxytyrosol, Tyrosol, Elenolic acid", "Antihypertensive, Antiviral, Anti-atherosclerotic, Cardioprotective", "Oleuropein Cardiovascular Leaf"),
    ("commiphora_myrrha", "Myrrh", "Commiphora myrrha", "Arabian & Unani", "Furanodiene, Curzerene, Lindestrene, Guggulsterones", "Antimicrobial, Analgesic, Anti-inflammatory, Oral hygiene", "Healing Resin Gum"),
    ("punica_granatum", "Pomegranate Peel", "Punica granatum", "Arabian & Unani", "Punicalagin, Ellagic acid, Gallic acid, Anthocyanins", "Astringent, Antidiarrheal, Antioxidant, Anti-microbial", "Ellagitannin Gut & Heart"),
    ("camellia_sinensis", "Green Tea (EGCG)", "Camellia sinensis", "TCM", "Epigallocatechin gallate (EGCG), L-theanine, Caffeine", "Metabolic rate enhancer, Neuroprotective, Antioxidant, Anti-cancer", "EGCG Polyphenol Extract"),
    ("artemisia_annua", "Sweet Wormwood", "Artemisia annua", "TCM", "Artemisinin, Arteannuin B, Scopoletin, Chrysosplenol", "Antimalarial, Anti-parasitic, Cytotoxic (cancer research)", "Artemisinin Malaria Fighter"),
    ("silybum_marianum", "Milk Thistle", "Silybum marianum", "Western Herbalism", "Silymarin, Silibinin, Silydianin, Silychristin", "Hepatoprotective, Anti-fibrotic, Detoxifying, Anti-inflammatory", "Liver Shield Silymarin"),
    ("hypericum_perforatum", "St. John's Wort", "Hypericum perforatum", "Western Herbalism", "Hypericin, Hyperforin, Flavonoids, Melatonin", "Antidepressant, Anxiolytic, Antiviral, Neuralgia relief", "Mood-Enhancing Flower"),
    ("valeriana_officinalis", "Valerian Root", "Valeriana officinalis", "Western Herbalism", "Valerenic acid, Isovaleric acid, Hesperidin", "Sedative, Sleep architecture enhancer, Antispasmodic", "Natural Sleep Root"),
    ("taraxacum_officinale", "Dandelion Root", "Taraxacum officinale", "Western Herbalism", "Taraxasterol, Inulin, Chicoric acid, Sesquiterpene lactones", "Prebiotic, Diuretic, Hepatoprotective, Cholagogue", "Kidney & Liver Cleanser"),
    ("curcuma_longa", "Turmeric (Curcumin)", "Curcuma longa", "Ayurveda", "Curcumin, Demethoxycurcumin, Bisdemethoxycurcumin, Turmerones", "Anti-inflammatory (NF-kB suppressor), Cardioprotective, Anti-cancer", "Gold Curcumin Compound"),
    ("withania_somnifera", "Ashwagandha", "Withania somnifera", "Ayurveda", "Withanolide A, Withaferin A, Somniferine", "Adaptogenic, Cortisol lowering, Nootropic, Anxiolytic", "Stress-Relieving Indian Ginseng")
]

def seed_database():
    """Import built-in curated dataset into SQLite/Turso database"""
    memory = ClinicalMemoryStore()
    
    # 1. Seed WHO / Commission E baseline plants from ClinicalMemoryStore
    base_count = memory.seed_pharmacopeia_100()
    
    # 2. Seed extended WHO, USDA Dr. Duke's, IMPPAT, PFAF & African Phytotherapy dataset
    conn = memory.get_connection()
    cursor = conn.cursor()

    for p in EXTENDED_BOTANICAL_DATASET:
        herb_key, common_name, botanical_name, category, active_bioactives, therapeutic_properties, layman_nutrient_name = p
        cursor.execute('''
            INSERT OR REPLACE INTO semantic_pharmacopeia
            (herb_key, common_name, botanical_name, category, active_bioactives, therapeutic_properties, layman_nutrient_name, discovered_from_llm)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (herb_key, common_name, botanical_name, category, active_bioactives, therapeutic_properties, layman_nutrient_name, "WHO / USDA Dr. Duke's / IMPPAT Dataset"))

    conn.commit()

    cursor.execute('SELECT COUNT(*) FROM semantic_pharmacopeia')
    total_count = cursor.fetchone()[0]
    conn.close()

    logger.info(f" Successfully seeded/imported {total_count} total botanical plant monographs into persistent database!")
    return total_count

def import_csv_file(file_path: str):
    """Import plant monographs from custom CSV file"""
    if not os.path.exists(file_path):
        logger.error(f"CSV file not found: {file_path}")
        return 0

    memory = ClinicalMemoryStore()
    conn = memory.get_connection()
    cursor = conn.cursor()
    count = 0

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            common = row.get("common_name", "").strip()
            botanical = row.get("botanical_name", "").strip()
            if not common or not botanical:
                continue

            herb_key = common.lower().replace(" ", "_").replace("'", "")
            category = row.get("category", "General Phytotherapy").strip()
            bioactives = row.get("active_bioactives", "").strip()
            props = row.get("therapeutic_properties", "").strip()
            layman = row.get("layman_nutrient_name", "").strip()

            cursor.execute('''
                INSERT OR REPLACE INTO semantic_pharmacopeia
                (herb_key, common_name, botanical_name, category, active_bioactives, therapeutic_properties, layman_nutrient_name, discovered_from_llm)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (herb_key, common, botanical, category, bioactives, props, layman, f"CSV Import: {os.path.basename(file_path)}"))
            count += 1

    conn.commit()
    conn.close()
    logger.info(f" Successfully imported {count} records from {file_path}")
    return count

def import_json_file(file_path: str):
    """Import plant monographs from custom JSON file"""
    if not os.path.exists(file_path):
        logger.error(f"JSON file not found: {file_path}")
        return 0

    memory = ClinicalMemoryStore()
    conn = memory.get_connection()
    cursor = conn.cursor()
    count = 0

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if isinstance(data, dict) and "herbs" in data:
            data = data["herbs"]

        for item in data:
            common = item.get("common_name", "").strip()
            botanical = item.get("botanical_name", "").strip()
            if not common or not botanical:
                continue

            herb_key = item.get("herb_key", common.lower().replace(" ", "_").replace("'", ""))
            category = item.get("category", "General Phytotherapy").strip()
            bioactives = item.get("active_bioactives", "")
            if isinstance(bioactives, list):
                bioactives = ", ".join(bioactives)
            props = item.get("therapeutic_properties", "")
            if isinstance(props, list):
                props = ", ".join(props)
            layman = item.get("layman_nutrient_name", "").strip()

            cursor.execute('''
                INSERT OR REPLACE INTO semantic_pharmacopeia
                (herb_key, common_name, botanical_name, category, active_bioactives, therapeutic_properties, layman_nutrient_name, discovered_from_llm)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (herb_key, common, botanical, category, bioactives, props, layman, f"JSON Import: {os.path.basename(file_path)}"))
            count += 1

    conn.commit()
    conn.close()
    logger.info(f" Successfully imported {count} records from {file_path}")
    return count

def main():
    parser = argparse.ArgumentParser(description="Herbalist AI Botanical Pharmacopeia Importer")
    parser.add_argument("--seed-all", action="store_true", help="Seed/import built-in WHO & USDA Dr. Duke's dataset")
    parser.add_argument("--file", type=str, help="Path to custom CSV dataset file")
    parser.add_argument("--json", type=str, help="Path to custom JSON dataset file")

    args = parser.parse_args()

    if args.file:
        import_csv_file(args.file)
    elif args.json:
        import_json_file(args.json)
    else:
        logger.info("No arguments specified. Seeding WHO & USDA Dr. Duke's dataset...")
        seed_database()

if __name__ == "__main__":
    main()
