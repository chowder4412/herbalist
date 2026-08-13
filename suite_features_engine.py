"""
Herbalist AI — Suite Features Engine
Provides backend support for:
1. Multi-Currency Local Herb Sourcing & Market Price Estimator (USD, NGN, EUR, GBP, KES, GHS)
2. 7-Day Symptom Recovery Tracker & Patient Consultation History Vault
3. Interactive Kitchen Pot Brew Timer Phase Protocols
4. Interactive Human Body Anatomy Map Symptom Mapping
"""

import sqlite3
from typing import Dict, Any, List

HERB_PRICE_DATABASE = {
    "bitter_leaf": {
        "common_name": "Bitter Leaf (Ewuro / Onugbu / Vernonia)",
        "base_usd_per_100g": 3.50,
        "adulteration_tip": "Check for vibrant dark green dried leaves; avoid yellowish/musty samples which indicate mold.",
        "storage": "Store in an airtight glass jar away from direct sunlight; shelf life 12 months."
    },
    "moringa": {
        "common_name": "Moringa Leaf Powder (Zogale / Drumstick Tree)",
        "base_usd_per_100g": 4.00,
        "adulteration_tip": "Authentic Moringa powder is bright green with a distinct horseradish smell. Brown tint indicates oxidation.",
        "storage": "Keep sealed in a cool, dry pantry; preserve from humidity."
    },
    "neem": {
        "common_name": "Neem Leaf (Dongoyaro / Azadirachta)",
        "base_usd_per_100g": 3.00,
        "adulteration_tip": "Ensure intensely bitter aroma; authentic Neem leaves should be bitter and crisp.",
        "storage": "Store in a dry cloth bag or glass container."
    },
    "ginger": {
        "common_name": "Ginger Root Powder / Dried Slices (Atale / Citta)",
        "base_usd_per_100g": 2.50,
        "adulteration_tip": "Avoid bleached pale yellow powders; authentic unbleached ginger powder has a pungent, warm aroma.",
        "storage": "Store root powder in airtight tins."
    },
    "hibiscus": {
        "common_name": "Hibiscus Roselle Calyx (Zobo / Karkadeh)",
        "base_usd_per_100g": 2.80,
        "adulteration_tip": "High quality calyces are deep ruby-red; avoid crushed blackish residue.",
        "storage": "Keep dry to prevent moisture clumping."
    },
    "ashwagandha": {
        "common_name": "Ashwagandha Root Powder (Indian Ginseng)",
        "base_usd_per_100g": 6.50,
        "adulteration_tip": "Pure root powder has a characteristic earthy horse-like scent with light tan color.",
        "storage": "Store tightly sealed in a glass jar."
    },
    "turmeric": {
        "common_name": "Turmeric Root Powder (Curcuma longa)",
        "base_usd_per_100g": 3.20,
        "adulteration_tip": "Watch for synthetic lead chromate dye additions; authentic turmeric has a rich golden-yellow orange color.",
        "storage": "Keep away from light to prevent curcumin degradation."
    },
    "licorice": {
        "common_name": "Licorice Root Sticks / Powder (Gan Cao)",
        "base_usd_per_100g": 4.80,
        "adulteration_tip": "Authentic licorice root sticks have a yellowish interior bark with intense natural sweetness.",
        "storage": "Store dry at room temperature."
    }
}

CURRENCY_CONVERSION = {
    "USD": {"symbol": "$", "rate": 1.0},
    "NGN": {"symbol": "₦", "rate": 1500.0},
    "EUR": {"symbol": "€", "rate": 0.92},
    "GBP": {"symbol": "£", "rate": 0.79},
    "KES": {"symbol": "KSh", "rate": 130.0},
    "GHS": {"symbol": "₵", "rate": 15.50}
}

BODY_ANATOMY_MAPPING = {
    "brain_head": {
        "zone_name": "Head & Nervous System",
        "common_symptoms": ["Migraine Headache", "Insomnia / Sleep Issues", "Brain Fog & Fatigue", "Stress & Anxiety"],
        "recommended_query": "I am experiencing severe migraines and mental exhaustion from stress."
    },
    "chest_lungs": {
        "zone_name": "Chest & Respiratory System",
        "common_symptoms": ["Asthma & Wheezing", "Chronic Dry Cough", "Bronchial Mucus Congestion"],
        "recommended_query": "I have persistent chest tightness, cough, and bronchial mucus congestion."
    },
    "heart_vascular": {
        "zone_name": "Cardiovascular & Circulation",
        "common_symptoms": ["High Blood Pressure (Hypertension)", "Poor Peripheral Circulation", "Ankle Swelling (Edema)"],
        "recommended_query": "I want to manage my elevated blood pressure and improve circulation naturally."
    },
    "upper_stomach": {
        "zone_name": "Upper GI & Stomach Lining",
        "common_symptoms": ["Acid Reflux / GERD", "Burning Gastritis", "Peptic Ulcer Irritation"],
        "recommended_query": "My upper stomach burns badly after eating and I have acid reflux."
    },
    "lower_gut": {
        "zone_name": "Lower GI & Colon Health",
        "common_symptoms": ["Bloating & Gas", "Constipation", "Irritable Bowel Syndrome"],
        "recommended_query": "I struggle with chronic bloating, gut cramping, and sluggish bowel motility."
    },
    "pelvis_genital": {
        "zone_name": "Pelvic & Endocrine System",
        "common_symptoms": ["Dysmenorrhea (Period Pain)", "Prostate Swelling", "Low Vitality & Libido"],
        "recommended_query": "I need botanical support for painful menstrual cramps and hormonal balance."
    },
    "joints_spine": {
        "zone_name": "Musculoskeletal & Spine",
        "common_symptoms": ["Lower Back Pain", "Osteoarthritis Joint Stiffness", "Rheumatoid Inflammation"],
        "recommended_query": "I have chronic lower back ache and stiff, inflamed knee joints."
    },
    "skin_whole_body": {
        "zone_name": "Dermatology & Whole Body Immune",
        "common_symptoms": ["Eczema & Skin Rash", "Chronic Fatigue Syndrome", "Low Immune Resistance"],
        "recommended_query": "I wake up exhausted every day and have skin rashes and low immunity."
    }
}


def estimate_herb_price(herb_key: str, weight_g: int = 250, currency: str = "USD") -> Dict[str, Any]:
    """Calculates crude herb market price across multiple global currencies"""
    herb = HERB_PRICE_DATABASE.get(herb_key.lower())
    if not herb:
        herb = HERB_PRICE_DATABASE["bitter_leaf"]
    
    curr = CURRENCY_CONVERSION.get(currency.upper(), CURRENCY_CONVERSION["USD"])
    weight_factor = weight_g / 100.0
    
    base_usd = herb["base_usd_per_100g"] * weight_factor
    converted_val = round(base_usd * curr["rate"], 2)
    min_val = round(converted_val * 0.85, 2)
    max_val = round(converted_val * 1.20, 2)
    
    return {
        "status": "success",
        "herb_name": herb["common_name"],
        "weight_grams": weight_g,
        "currency": currency.upper(),
        "currency_symbol": curr["symbol"],
        "estimated_price": f"{curr['symbol']}{converted_val:,.2f}",
        "price_range": f"{curr['symbol']}{min_val:,.2f} – {curr['symbol']}{max_val:,.2f}",
        "adulteration_tip": herb["adulteration_tip"],
        "storage_instructions": herb["storage"]
    }


def init_symptom_tracker_db(db_path: str = "clinical_memory.db"):
    """Creates symptom_recovery_logs table if not existing"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS symptom_recovery_logs (
            log_id TEXT PRIMARY KEY,
            patient_id TEXT,
            prescription_id TEXT,
            day_number INTEGER,
            severity_score INTEGER,
            tea_cups_consumed INTEGER,
            symptom_notes TEXT,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def log_daily_recovery(patient_id: str, prescription_id: str, day_number: int, severity_score: int, tea_cups: int, notes: str = "", db_path: str = "clinical_memory.db") -> Dict[str, Any]:
    """Records daily recovery progress score (1-10 scale)"""
    init_symptom_tracker_db(db_path)
    import time, uuid
    log_id = f"LOG-{int(time.time())}-{uuid.uuid4().hex[:4]}"
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO symptom_recovery_logs (log_id, patient_id, prescription_id, day_number, severity_score, tea_cups_consumed, symptom_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (log_id, patient_id, prescription_id, day_number, severity_score, tea_cups, notes))
    conn.commit()
    
    # Calculate recovery progress percentage
    cur.execute("""
        SELECT day_number, severity_score FROM symptom_recovery_logs
        WHERE patient_id = ? AND prescription_id = ?
        ORDER BY day_number ASC
    """, (patient_id, prescription_id))
    rows = cur.fetchall()
    conn.close()
    
    improvement_pct = 0.0
    if len(rows) >= 2:
        initial_sev = rows[0][1]
        current_sev = rows[-1][1]
        if initial_sev > 0:
            improvement_pct = round(((initial_sev - current_sev) / initial_sev) * 100.0, 1)
            
    return {
        "status": "success",
        "log_id": log_id,
        "day_number": day_number,
        "current_severity": severity_score,
        "tea_cups_logged": tea_cups,
        "recovery_improvement_pct": max(0.0, improvement_pct),
        "message": f"Day {day_number} recovery log saved successfully."
    }
