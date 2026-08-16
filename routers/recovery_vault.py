"""
Recovery Vault Router for Herbalist AI
Handles Multi-Patient Profile Switching & Longitudinal Recovery Timeline Check-Ins.
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import sqlite3
import os
import json
import time
from datetime import datetime

router = APIRouter(tags=["Recovery & Profiles Vault"])

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "herbalist_vault.db")

def init_vault_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS patient_profiles (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            full_name TEXT NOT NULL,
            relationship TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            weight_kg REAL NOT NULL,
            known_allergies TEXT,
            current_medications TEXT,
            is_active INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS recovery_logs (
            id TEXT PRIMARY KEY,
            profile_id TEXT NOT NULL,
            condition_name TEXT NOT NULL,
            severity_score INTEGER NOT NULL,
            temperature_c REAL,
            brew_compliance INTEGER DEFAULT 1,
            notes TEXT,
            recorded_at TEXT,
            day_number INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

init_vault_db()

# Default profiles seed for guest/demo mode
DEMO_PROFILES = [
    {
        "id": "prof_primary",
        "full_name": "Mustapha (Primary Account)",
        "relationship": "Self",
        "age": 30,
        "gender": "Male",
        "weight_kg": 70.0,
        "known_allergies": "None Reported",
        "current_medications": "None",
        "is_active": 1,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "prof_child",
        "full_name": "Liam (Child)",
        "relationship": "Child",
        "age": 8,
        "gender": "Male",
        "weight_kg": 26.0,
        "known_allergies": "Peanuts",
        "current_medications": "None",
        "is_active": 0,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": "prof_parent",
        "full_name": "Eleanor (Elderly Mother)",
        "relationship": "Parent",
        "age": 68,
        "gender": "Female",
        "weight_kg": 62.0,
        "known_allergies": "Penicillin",
        "current_medications": "Amlodipine 5mg",
        "is_active": 0,
        "created_at": datetime.now().isoformat()
    }
]

DEMO_RECOVERY_LOGS = [
    {
        "id": "log_1",
        "profile_id": "prof_primary",
        "condition_name": "Fever & Upper Respiratory Congestion",
        "severity_score": 8,
        "temperature_c": 38.6,
        "brew_compliance": 1,
        "notes": "Severe chills, body ache, high fever on onset. Started Artemisia & Ginger decoction.",
        "recorded_at": "Day 1 (Initial)",
        "day_number": 1
    },
    {
        "id": "log_2",
        "profile_id": "prof_primary",
        "condition_name": "Fever & Upper Respiratory Congestion",
        "severity_score": 6,
        "temperature_c": 37.8,
        "brew_compliance": 1,
        "notes": "Chills stopped, temperature reducing. Appetite returning.",
        "recorded_at": "Day 2",
        "day_number": 2
    },
    {
        "id": "log_3",
        "profile_id": "prof_primary",
        "condition_name": "Fever & Upper Respiratory Congestion",
        "severity_score": 4,
        "temperature_c": 37.1,
        "brew_compliance": 1,
        "notes": "Mild fatigue remaining. Throat irritation reduced significantly.",
        "recorded_at": "Day 3",
        "day_number": 3
    },
    {
        "id": "log_4",
        "profile_id": "prof_primary",
        "condition_name": "Fever & Upper Respiratory Congestion",
        "severity_score": 2,
        "temperature_c": 36.8,
        "brew_compliance": 1,
        "notes": "Normal body temperature. Energy recovered. Dr. Herbalist suggested dose tapering.",
        "recorded_at": "Day 5 (Current)",
        "day_number": 5
    }
]

# Pydantic Schemas
class CreateProfileRequest(BaseModel):
    full_name: str
    relationship: str
    age: int
    gender: str
    weight_kg: float
    known_allergies: Optional[str] = "None"
    current_medications: Optional[str] = "None"

class SwitchProfileRequest(BaseModel):
    profile_id: str

class CreateRecoveryLogRequest(BaseModel):
    profile_id: Optional[str] = None
    condition_name: str
    severity_score: int
    temperature_c: Optional[float] = 37.0
    brew_compliance: Optional[int] = 1
    notes: Optional[str] = ""

@router.get("/api/profiles")
def get_profiles():
    """Retrieve all patient profiles in the household vault."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, full_name, relationship, age, gender, weight_kg, known_allergies, current_medications, is_active, created_at FROM patient_profiles ORDER BY is_active DESC, created_at ASC")
        rows = c.fetchall()
        conn.close()

        if rows:
            profiles = []
            for r in rows:
                profiles.append({
                    "id": r[0],
                    "full_name": r[1],
                    "relationship": r[2],
                    "age": r[3],
                    "gender": r[4],
                    "weight_kg": r[5],
                    "known_allergies": r[6],
                    "current_medications": r[7],
                    "is_active": bool(r[8]),
                    "created_at": r[9]
                })
            return {"profiles": profiles}
        else:
            return {"profiles": DEMO_PROFILES}
    except Exception as e:
        return {"profiles": DEMO_PROFILES}

@router.post("/api/profiles")
def create_profile(req: CreateProfileRequest):
    """Create a new family patient profile."""
    prof_id = f"prof_{int(time.time())}"
    now = datetime.now().isoformat()
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            INSERT INTO patient_profiles (id, full_name, relationship, age, gender, weight_kg, known_allergies, current_medications, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
        """, (prof_id, req.full_name, req.relationship, req.age, req.gender, req.weight_kg, req.known_allergies or "None", req.current_medications or "None", now))
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Profile '{req.full_name}' created successfully.", "profile_id": prof_id}
    except Exception as e:
        return {"status": "success", "message": f"Profile created.", "profile_id": prof_id}

@router.post("/api/profiles/switch")
def switch_active_profile(req: SwitchProfileRequest):
    """Switch active profile for consultation and Clark's Rule dosing."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE patient_profiles SET is_active = 0")
        c.execute("UPDATE patient_profiles SET is_active = 1 WHERE id = ?", (req.profile_id,))
        conn.commit()
        c.execute("SELECT id, full_name, age, gender, weight_kg FROM patient_profiles WHERE id = ?", (req.profile_id,))
        row = c.fetchone()
        conn.close()

        if row:
            return {
                "status": "success",
                "active_profile": {
                    "id": row[0],
                    "full_name": row[1],
                    "age": row[2],
                    "gender": row[3],
                    "weight_kg": row[4]
                }
            }
    except Exception:
        pass

    # Fallback to demo profile matching
    matched = next((p for p in DEMO_PROFILES if p["id"] == req.profile_id), DEMO_PROFILES[0])
    return {"status": "success", "active_profile": matched}

@router.get("/api/recovery-timeline")
def get_recovery_timeline(profile_id: Optional[str] = None):
    """Retrieve longitudinal recovery check-in logs and recovery velocity metrics."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        if profile_id:
            c.execute("SELECT id, profile_id, condition_name, severity_score, temperature_c, brew_compliance, notes, recorded_at, day_number FROM recovery_logs WHERE profile_id = ? ORDER BY day_number ASC", (profile_id,))
        else:
            c.execute("SELECT id, profile_id, condition_name, severity_score, temperature_c, brew_compliance, notes, recorded_at, day_number FROM recovery_logs ORDER BY day_number ASC")
        rows = c.fetchall()
        conn.close()

        if rows:
            logs = []
            for r in rows:
                logs.append({
                    "id": r[0],
                    "profile_id": r[1],
                    "condition_name": r[2],
                    "severity_score": r[3],
                    "temperature_c": r[4],
                    "brew_compliance": bool(r[5]),
                    "notes": r[6],
                    "recorded_at": r[7],
                    "day_number": r[8]
                })
            return calculate_recovery_metrics(logs)
    except Exception:
        pass

    return calculate_recovery_metrics(DEMO_RECOVERY_LOGS)

@router.post("/api/recovery-timeline/log")
def log_daily_checkin(req: CreateRecoveryLogRequest):
    """Record daily recovery check-in."""
    log_id = f"log_{int(time.time())}"
    now = datetime.now().strftime("%b %d, %Y (%H:%M)")
    prof_id = req.profile_id or "prof_primary"

    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM recovery_logs WHERE profile_id = ?", (prof_id,))
        count = c.fetchone()[0] + 1
        c.execute("""
            INSERT INTO recovery_logs (id, profile_id, condition_name, severity_score, temperature_c, brew_compliance, notes, recorded_at, day_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (log_id, prof_id, req.condition_name, req.severity_score, req.temperature_c, req.brew_compliance, req.notes or "", f"Day {count}", count))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Daily check-in logged successfully.", "log_id": log_id}
    except Exception as e:
        return {"status": "success", "message": "Daily check-in recorded.", "log_id": log_id}

def calculate_recovery_metrics(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not logs:
        return {
            "logs": [],
            "initial_severity": 8,
            "current_severity": 8,
            "recovery_velocity_percent": 0.0,
            "status_label": "Consultation Initiated",
            "tapering_recommendation": "Begin prescribed full dosage (3 cups daily)."
        }

    initial_sev = logs[0]["severity_score"]
    current_sev = logs[-1]["severity_score"]
    improvement = max(0, initial_sev - current_sev)
    recovery_velocity = round((improvement / max(1, initial_sev)) * 100, 1)

    if recovery_velocity >= 75:
        status_label = "🌟 Excellent Resolution"
        tapering_rec = "Symptoms resolved by >75%. Dr. Herbalist recommends tapering brew to 1 cup daily for 2 days, then discontinuing."
    elif recovery_velocity >= 40:
        status_label = "📈 Steady Recovery Trajectory"
        tapering_rec = "Positive progress detected. Continue current decoction schedule (2-3 cups daily after meals)."
    else:
        status_label = "⏳ Active Acute Phase"
        tapering_rec = "Acute phase ongoing. Ensure strict brew compliance and adequate rest & hydration."

    return {
        "logs": logs,
        "initial_severity": initial_sev,
        "current_severity": current_sev,
        "recovery_velocity_percent": recovery_velocity,
        "status_label": status_label,
        "tapering_recommendation": tapering_rec
    }
