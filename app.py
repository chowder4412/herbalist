import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import os
import sqlite3
import uuid

# Import Herbalist AI Doctor & Clinical Memory
from herbalist import AIDoctor, MedicalProfile
from clinical_memory import ClinicalMemoryStore

# Initialize Doctor & Memory Store
doctor = AIDoctor()
memory_store = ClinicalMemoryStore()

# Seed 100+ pharmacopeia plants on startup
seeded = memory_store.seed_pharmacopeia_100()
if seeded > 0:
    print(f"🌿 Seeded {seeded} new medicinal plants into pharmacopeia database!")

# ══════════════════════════════════════════════════════════════
# SOCRATES Multi-Turn Triage Session Manager
# ══════════════════════════════════════════════════════════════
# Each session tracks: phase, collected data, and conversation history
active_sessions = {}

SOCRATES_QUESTIONS = {
    "onset": {
        "question": "When did you first notice this symptom? How long have you been experiencing it?",
        "key": "onset",
        "follow_up": "duration"
    },
    "duration": {
        "question": "Is the symptom constant or does it come and go? How often does it occur?",
        "key": "duration",
        "follow_up": "character"
    },
    "character": {
        "question": "Can you describe the nature of the symptom? For example, if it's pain — is it sharp, dull, throbbing, or burning?",
        "key": "character",
        "follow_up": "severity"
    },
    "severity": {
        "question": "On a scale of 1–10 (10 being the worst), how severe is this symptom right now?",
        "key": "severity",
        "follow_up": "medications"
    },
    "medications": {
        "question": "Are you currently taking any medications (prescription or over-the-counter)? This is critical to avoid herb-drug interactions.",
        "key": "medications",
        "follow_up": "ready"
    }
}


def create_session(complaint, age, gender, weight_kg):
    """Create a new SOCRATES triage session"""
    session_id = str(uuid.uuid4())[:8]
    active_sessions[session_id] = {
        "session_id": session_id,
        "phase": "onset",
        "complaint": complaint,
        "age": age,
        "gender": gender,
        "weight_kg": weight_kg,
        "collected": {
            "complaint": complaint,
            "onset": None,
            "duration": None,
            "character": None,
            "severity": None,
            "medications": None
        },
        "conversation": []
    }
    return session_id


def advance_session(session_id, user_answer):
    """Advance a SOCRATES session to the next question or final diagnosis"""
    session = active_sessions.get(session_id)
    if not session:
        return None, None, False

    current_phase = session["phase"]

    # Store the user's answer for the current phase
    if current_phase in session["collected"]:
        session["collected"][current_phase] = user_answer

    # Record conversation
    session["conversation"].append({"role": "patient", "text": user_answer})

    # Get next phase
    if current_phase in SOCRATES_QUESTIONS:
        next_phase = SOCRATES_QUESTIONS[current_phase]["follow_up"]
    else:
        next_phase = "ready"

    session["phase"] = next_phase

    if next_phase == "ready":
        # All questions answered — ready for full diagnosis
        return None, session, True
    else:
        # Ask the next SOCRATES question
        next_q = SOCRATES_QUESTIONS[next_phase]["question"]
        session["conversation"].append({"role": "doctor", "text": next_q})
        return next_q, session, False


class HerbalistAPIHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/api/recents' or parsed_path.path == '/api/memory-stats':
            stats = memory_store.get_memory_stats()
            token = self.get_auth_token()
            user_auth = verify_jwt_token(token) if token else None

            recents = []
            if user_auth and ("user_id" in user_auth or "email" in user_auth):
                conn = sqlite3.connect(memory_store.db_path)
                cursor = conn.cursor()
                user_id = user_auth.get("user_id", "")
                user_email = user_auth.get("email", "")
                cursor.execute('SELECT case_id, symptoms, primary_diagnosis, prescribed_formulation, bioactive_match_score, timestamp FROM episodic_cases WHERE patient_id = ? OR patient_id = ? ORDER BY timestamp DESC LIMIT 10', (user_id, user_email))
                rows = cursor.fetchall()
                conn.close()

                for r in rows:
                    recents.append({
                        "case_id": r[0],
                        "title": r[2] if r[2] != "Health Maintenance Examination" else r[1].split(',')[0].title(),
                        "symptoms": r[1],
                        "diagnosis": r[2],
                        "formulation": r[3],
                        "match_score": r[4],
                        "timestamp": r[5]
                    })
                
            response_data = {
                "status": "success",
                "stats": stats,
                "recents": recents
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        elif parsed_path.path == '/favicon.ico':
            svg_favicon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🌿</text></svg>'
            self._set_headers(200, "image/svg+xml")
            self.wfile.write(svg_favicon.encode('utf-8'))
        elif parsed_path.path == '/' or parsed_path.path == '/index.html':
            try:
                with open("index.html", "rb") as f:
                    self._set_headers(200, "text/html")
                    self.wfile.write(f.read())
            except Exception as e:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode('utf-8'))


    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/api/diagnose':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                body = json.loads(post_data.decode('utf-8'))
                complaint = body.get('complaint', 'Health maintenance')
                age = int(body.get('age', 52))
                gender = body.get('gender', 'Female')
                weight_kg = float(body.get('weight_kg', 72.0))
                severity = int(body.get('severity', 7))
                session_id = body.get('session_id', None)
                api_key = body.get('api_key') or os.environ.get("GEMINI_API_KEY", "")
                if api_key:
                    doctor.gemini_engine.api_key = api_key

                # ── CONTINUING AN ACTIVE SOCRATES SESSION ──
                if session_id and session_id in active_sessions:
                    next_question, session, is_ready = advance_session(session_id, complaint)

                    if is_ready:
                        # All triage questions collected — run full diagnosis
                        collected = session["collected"]
                        enriched_complaint = (
                            f"{collected['complaint']}. "
                            f"Onset: {collected.get('onset', 'Not specified')}. "
                            f"Pattern: {collected.get('duration', 'Not specified')}. "
                            f"Character: {collected.get('character', 'Not specified')}. "
                            f"Severity: {collected.get('severity', 'Not specified')}/10. "
                            f"Current medications: {collected.get('medications', 'None reported')}."
                        )

                        # Lookup matching herbs from 100+ pharmacopeia
                        condition_keywords = [w for w in collected['complaint'].lower().split() if len(w) > 3]
                        matching_herbs = memory_store.lookup_herbs_for_condition(condition_keywords[:5])

                        patient = MedicalProfile(
                            age=session["age"],
                            gender=session["gender"],
                            weight_kg=session["weight_kg"],
                            severity=int(collected.get("severity", 7)) if collected.get("severity", "").isdigit() else 7
                        )

                        diagnosis = doctor.comprehensive_medical_analysis(patient, enriched_complaint)
                        
                        # ── AUTO-LEARN: Save case + expand pharmacopeia ──
                        formulation_name = ""
                        match_score = 0
                        if diagnosis.natural_formulation:
                            formulation_name = diagnosis.natural_formulation.formulation_name
                            match_score = diagnosis.natural_formulation.bioactive_match_score

                        memory_store.record_episodic_case(
                            symptoms=collected["complaint"],
                            diagnosis_result=diagnosis.primary_diagnosis,
                            prescribed_formulation=formulation_name,
                            bioactive_match_score=match_score,
                            gemini_response=diagnosis.gemini_raw if hasattr(diagnosis, 'gemini_raw') else ""
                        )

                        # Auto-expand pharmacopeia from Gemini discoveries
                        learn_data = {
                            "target_plants": [h for h in (diagnosis.herbal_recommendations or [])],
                            "key_bioactives": [],
                            "primary_diagnosis": diagnosis.primary_diagnosis
                        }
                        new_herbs = memory_store.learn_new_herb_synergy(learn_data)

                        # Build response
                        formulation_data = None
                        if diagnosis.natural_formulation:
                            f = diagnosis.natural_formulation
                            formulation_data = {
                                "formulation_name": f.formulation_name,
                                "target_condition": f.target_condition,
                                "total_volume_ml": f.total_volume_ml,
                                "total_active_bioactives_mg": f.total_active_bioactives_mg,
                                "concentration_mg_per_ml": f.concentration_mg_per_ml,
                                "dosage_volume_ml": f.dosage_volume_ml,
                                "dosing_frequency": f.dosing_frequency,
                                "layman_explanation": f.layman_explanation,
                                "household_kitchen_recipe": f.household_kitchen_recipe,
                                "household_dose_schedule": f.household_dose_schedule,
                                "body_requirement_summary": f.body_requirement_summary,
                                "bioactive_match_score": f.bioactive_match_score
                            }
                            
                        citations_data = []
                        if diagnosis.pubmed_citations:
                            for c in diagnosis.pubmed_citations:
                                citations_data.append({
                                    "title": c.title,
                                    "journal": c.journal,
                                    "doi": c.doi,
                                    "pmid": c.pmid,
                                    "evidence_level": c.evidence_level,
                                    "key_findings": c.key_findings
                                })

                        response_payload = {
                            "status": "success",
                            "session_id": session_id,
                            "triage_complete": True,
                            "triage_summary": collected,
                            "primary_diagnosis": diagnosis.primary_diagnosis,
                            "confidence_score": diagnosis.confidence_score,
                            "differential_diagnoses": diagnosis.differential_diagnoses,
                            "treatment_plan": diagnosis.treatment_plan,
                            "herbal_recommendations": diagnosis.herbal_recommendations,
                            "safety_warnings": diagnosis.herb_drug_safety_warnings,
                            "prescription_card": diagnosis.prescription_card,
                            "formulation": formulation_data,
                            "pubmed_citations": citations_data,
                            "pharmacopeia_matches": matching_herbs[:8],
                            "new_herbs_learned": new_herbs
                        }

                        # Clean up session
                        del active_sessions[session_id]

                        self._set_headers(200)
                        self.wfile.write(json.dumps(response_payload).encode('utf-8'))
                        return

                    else:
                        # Return the next SOCRATES follow-up question
                        response_payload = {
                            "status": "success",
                            "session_id": session_id,
                            "is_triage_question": True,
                            "triage_phase": active_sessions[session_id]["phase"],
                            "conversational_message": f"🩺 **Dr. Herbalist**: {next_question}",
                            "collected_so_far": {k: v for k, v in active_sessions[session_id]["collected"].items() if v}
                        }
                        self._set_headers(200)
                        self.wfile.write(json.dumps(response_payload).encode('utf-8'))
                        return

                # ── GREETING DETECTION (Only for new consultations without active session) ──
                greeting_words = {"hello", "hi", "hey", "good morning", "good afternoon", "good evening", "greetings", "who are you", "help", "start", "doc", "doctor", "hi doctor", "hello doctor"}
                complaint_clean = complaint.strip().lower()
                is_greeting = complaint_clean in greeting_words
                
                if is_greeting:
                    response_payload = {
                        "status": "success",
                        "is_greeting": True,
                        "conversational_message": (
                            "Hello! I am **Dr. Herbalist**, your integrative medical doctor and botanical phytotherapy specialist. 🌿\n\n"
                            "I have access to a pharmacopeia of **100+ verified medicinal plants** spanning African Phytotherapy, Ayurveda, Traditional Chinese Medicine, and Western Herbalism.\n\n"
                            "To begin your consultation, please describe your primary symptom or health concern. "
                            "For example:\n"
                            "• *\"Persistent headaches and fatigue\"*\n"
                            "• *\"High blood sugar and frequent urination\"*\n"
                            "• *\"Joint pain in both knees\"*\n"
                            "• *\"Anxiety and difficulty sleeping\"*\n\n"
                            "I will ask you a few targeted diagnostic questions before prescribing your personalized botanical remedy."
                        )
                    }
                    self._set_headers(200)
                    self.wfile.write(json.dumps(response_payload).encode('utf-8'))
                    return

                # ── NEW CONSULTATION: Start SOCRATES Triage ──
                session_id = create_session(complaint, age, gender, weight_kg)
                first_question = SOCRATES_QUESTIONS["onset"]["question"]

                active_sessions[session_id]["conversation"].append(
                    {"role": "patient", "text": complaint}
                )
                active_sessions[session_id]["conversation"].append(
                    {"role": "doctor", "text": first_question}
                )

                response_payload = {
                    "status": "success",
                    "session_id": session_id,
                    "is_triage_question": True,
                    "triage_phase": "onset",
                    "conversational_message": (
                        f"Thank you for sharing that. I want to understand your condition thoroughly before prescribing.\n\n"
                        f"🩺 **Dr. Herbalist**: {first_question}"
                    ),
                    "collected_so_far": {"complaint": complaint}
                }
                self._set_headers(200)
                self.wfile.write(json.dumps(response_payload).encode('utf-8'))

            except Exception as e:
                import traceback
                traceback.print_exc()
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode('utf-8'))

def run(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, HerbalistAPIHandler)
    stats = memory_store.get_memory_stats()
    print(f"")
    print(f"╔══════════════════════════════════════════════════════════╗")
    print(f"║    🌿 Herbalist — Integrative Botanical Medicine AI     ║")
    print(f"╠══════════════════════════════════════════════════════════╣")
    print(f"║  Server:  http://127.0.0.1:{port}                       ║")
    print(f"║  Plants:  {str(stats['semantic_learned_ingredients']).ljust(4)} medicinal herbs in pharmacopeia     ║")
    print(f"║  Cases:   {str(stats['total_episodic_consultations']).ljust(4)} recorded consultations              ║")
    print(f"║  Memory:  SQLite Continuous Learning Active             ║")
    print(f"║  Triage:  SOCRATES Multi-Turn Consultation Active       ║")
    print(f"╚══════════════════════════════════════════════════════════╝")
    print(f"")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == '__main__':
    run()
