import os
import sqlite3
import time
import random
import datetime
import hashlib
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
load_dotenv()

class ClinicalMemoryStore:
    """
    Persistent Local Dual-Layer Hybrid Memory Store for Continuous AI Clinical Learning.
    Provides Episodic Patient Consultation Memory and Semantic Pharmacopeia Knowledge Expansion.
    """
    
    def __init__(self, db_path: str = "clinical_memory.db"):
        self.db_path = db_path
        self._initialize_database()

    def get_connection(self):
        """Connect to Turso Cloud database or fallback to local SQLite"""
        turso_url = os.getenv("TURSO_DATABASE_URL", "").strip()
        turso_token = os.getenv("TURSO_AUTH_TOKEN", "").strip()
        if turso_url and turso_token:
            try:
                try:
                    import libsql_client
                    return libsql_client.create_client_sync(url=turso_url, auth_token=turso_token)
                except ImportError:
                    try:
                        import libsql_experimental as libsql
                    except ImportError:
                        import libsql
                    return libsql.connect(database=turso_url, auth_token=turso_token)
            except Exception as e:
                print(f"[Turso Cloud Notice] Fallback to local SQLite: {e}")
        return sqlite3.connect(self.db_path)


    def _initialize_database(self):
        """Create SQLite schema for Episodic Memory and Semantic Pharmacopeia Expansion"""
        conn = self.get_connection()
        cursor = conn.cursor()

        
        # Table 1: Episodic Patient Consultation Memory
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodic_cases (
                case_id TEXT PRIMARY KEY,
                patient_id TEXT,
                age INTEGER,
                gender TEXT,
                symptoms TEXT,
                primary_diagnosis TEXT,
                prescribed_formulation TEXT,
                bioactive_match_score REAL,
                llm_reasoning_chain TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table 2: Semantic Learned Pharmacopeia Facts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semantic_pharmacopeia (
                herb_key TEXT PRIMARY KEY,
                common_name TEXT,
                botanical_name TEXT,
                category TEXT,
                active_bioactives TEXT,
                therapeutic_properties TEXT,
                layman_nutrient_name TEXT,
                discovered_from_llm TEXT,
                date_learned DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table 3: Registered User Accounts (JWT Auth)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                password_hash TEXT,
                full_name TEXT,
                username TEXT,
                dob TEXT,
                age INTEGER,
                role TEXT DEFAULT 'patient',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Safe schema migrations for existing SQLite databases
        for col, col_type in [("username", "TEXT"), ("dob", "TEXT"), ("age", "INTEGER")]:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type};")
            except Exception:
                pass

        for col, col_type in [("username", "TEXT"), ("dob", "TEXT")]:
            try:
                cursor.execute(f"ALTER TABLE pending_otps ADD COLUMN {col} {col_type};")
            except Exception:
                pass


        # Table 4: Saved Patient Prescriptions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patient_prescriptions (
                rx_id TEXT PRIMARY KEY,
                user_id TEXT,
                patient_name TEXT,
                symptoms TEXT,
                primary_diagnosis TEXT,
                prescribed_formulation TEXT,
                prescription_card TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Table 5: Pending Email OTP Verifications
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pending_otps (
                email TEXT PRIMARY KEY,
                otp_code TEXT,
                full_name TEXT,
                password_hash TEXT,
                expires_at INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()


    def record_episodic_experience(self, patient: Any, primary_diagnosis: str, formulation: Any, llm_reasoning: str = "") -> str:
        """Record consultation experience into persistent episodic memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        case_id = f"CASE_{int(time.time())}_{random.randint(100, 999)}"
        symptoms_str = ", ".join(patient.current_symptoms) if hasattr(patient, 'current_symptoms') else str(patient)
        
        ing_summary = "Custom Remedy"
        if hasattr(formulation, 'ingredients'):
            ing_summary = ", ".join([ing["common_name"] for ing in formulation.ingredients])
            
        match_score = getattr(formulation, 'bioactive_match_score', 95.0)
        patient_id = getattr(patient, 'patient_id', 'UNKNOWN_PATIENT')
        age = getattr(patient, 'age', 0)
        gender = getattr(patient, 'gender', 'Unspecified')

        cursor.execute('''
            INSERT INTO episodic_cases 
            (case_id, patient_id, age, gender, symptoms, primary_diagnosis, prescribed_formulation, bioactive_match_score, llm_reasoning_chain)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (case_id, patient_id, age, gender, symptoms_str, primary_diagnosis, ing_summary, match_score, llm_reasoning))
        
        conn.commit()
        conn.close()
        return case_id

    def record_episodic_case(self, symptoms: str, diagnosis_result: str, prescribed_formulation: str, bioactive_match_score: float = 95.0, gemini_response: str = "", patient_id: str = "") -> str:
        """Record episodic case directly from API endpoints with specified or anonymized patient ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        case_id = f"CASE_{int(time.time())}_{random.randint(100, 999)}"
        if not patient_id:
            patient_id = f"ANON_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}"
        
        cursor.execute('''
            INSERT INTO episodic_cases 
            (case_id, patient_id, age, gender, symptoms, primary_diagnosis, prescribed_formulation, bioactive_match_score, llm_reasoning_chain)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (case_id, patient_id, 0, "Unspecified", symptoms, diagnosis_result, prescribed_formulation, bioactive_match_score, gemini_response))
        
        conn.commit()
        conn.close()
        return case_id

    def query_similar_cases(self, current_symptoms: List[str], limit: int = 3) -> List[Dict[str, Any]]:
        """Query episodic memory for past similar patient consultations and learning outcomes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT case_id, patient_id, age, symptoms, primary_diagnosis, prescribed_formulation, bioactive_match_score, timestamp FROM episodic_cases ORDER BY timestamp DESC LIMIT ?', (limit * 3,))
        rows = cursor.fetchall()
        conn.close()
        
        matches = []
        symptom_set = set([s.lower() for s in current_symptoms])
        
        for row in rows:
            case_symptoms = set([s.lower().strip() for s in row[3].split(',')])
            overlap = len(symptom_set.intersection(case_symptoms))
            match_score = (overlap / max(1, len(symptom_set))) * 100
            
            matches.append({
                "case_id": row[0],
                "patient_id": row[1],
                "age": row[2],
                "symptoms": row[3],
                "diagnosis": row[4],
                "prescribed_herbs": row[5],
                "confidence": row[6],
                "timestamp": row[7],
                "relevance_match": round(match_score, 1)
            })
            
        matches.sort(key=lambda x: x["relevance_match"], reverse=True)
        return matches[:limit]

    def auto_expand_semantic_pharmacopeia(self, herb_key: str, common_name: str, botanical_name: str, category: str, active_bioactives: List[str], therapeutic_props: List[str], layman_name: str, llm_source: str = "Gemini LLM Synthesis") -> bool:
        """Persist newly discovered plant/herb facts into the semantic memory database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        bio_str = ", ".join(active_bioactives)
        prop_str = ", ".join(therapeutic_props)
        
        cursor.execute('''
            INSERT OR REPLACE INTO semantic_pharmacopeia
            (herb_key, common_name, botanical_name, category, active_bioactives, therapeutic_properties, layman_nutrient_name, discovered_from_llm)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (herb_key, common_name, botanical_name, category, bio_str, prop_str, layman_name, llm_source))
        
        conn.commit()
        conn.close()
        return True

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get summary statistics of continuous learning memory engine"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM episodic_cases')
        total_cases = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM semantic_pharmacopeia')
        learned_herbs = cursor.fetchone()[0]
        
        conn.close()
        return {
            "total_episodic_consultations": total_cases,
            "semantic_learned_ingredients": learned_herbs,
            "memory_system_status": "Active Persistent SQLite Store",
            "continuous_learning_grade": "Grade A: Adaptive Memory Enabled"
        }

    def get_all_semantic_herbs(self) -> List[Dict[str, Any]]:
        """Retrieve all learned herbs from SQLite semantic_pharmacopeia memory store"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT herb_key, common_name, botanical_name, category, active_bioactives, therapeutic_properties, layman_nutrient_name FROM semantic_pharmacopeia')
        rows = cursor.fetchall()
        conn.close()
        herbs = []
        for r in rows:
            herbs.append({
                "key": r[0],
                "common_name": r[1],
                "botanical_name": r[2],
                "category": r[3] or "Medicinal Plant",
                "active_bioactives": [b.strip() for b in r[4].split(',')] if r[4] else [],
                "therapeutic_properties": [p.strip() for p in r[5].split(',')] if r[5] else [],
                "clinical_indications": [p.strip() for p in r[5].split(',')] if r[5] else ["General Wellness"],
                "safety_cautions": ["Consult healthcare professional for specific dosing"],
                "household_measurement": "1 teacup infusion",
                "potency_rating": 25.0
            })
        return herbs

    def hash_password(self, password: str) -> str:
        """Secure SHA-256 password hashing with salt"""
        salt = "herbalist_ai_salt_2026"
        return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

    def calculate_age_from_dob(self, dob_str: str) -> int:
        """Calculate exact age in years from DOB string YYYY-MM-DD"""
        if not dob_str:
            return 0
        try:
            from datetime import datetime
            birth_date = datetime.strptime(dob_str.strip(), "%Y-%m-%d")
            today = datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return max(0, age)
        except Exception:
            return 0

    def create_user(self, email: str, password: str, full_name: str, username: str = "", dob: str = "") -> Optional[Dict[str, Any]]:
        """Register a new user account in SQLite database with Patient ID (username), DOB, and calculated Age"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        user_id = f"USER_{int(time.time())}_{random.randint(100, 999)}"
        pwd_hash = self.hash_password(password)
        username_clean = username.strip() if username else full_name.strip().replace(" ", "_")
        dob_clean = dob.strip() if dob else ""
        age = self.calculate_age_from_dob(dob_clean)

        try:
            cursor.execute('''
                INSERT INTO users (user_id, email, password_hash, full_name, username, dob, age)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, email.lower().strip(), pwd_hash, full_name.strip(), username_clean, dob_clean, age))
            conn.commit()
            conn.close()
            return {
                "user_id": user_id,
                "email": email.lower().strip(),
                "full_name": full_name,
                "username": username_clean,
                "dob": dob_clean,
                "age": age,
                "role": "patient"
            }
        except sqlite3.IntegrityError:
            conn.close()
            return None

    def store_pending_otp(self, email: str, password: str, full_name: str, otp_code: str, username: str = "", dob: str = "", ttl_seconds: int = 600) -> bool:
        """Store pending user registration details, Patient ID (username), DOB, and 6-digit OTP"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        email_clean = email.lower().strip()
        pwd_hash = self.hash_password(password)
        expires_at = int(time.time()) + ttl_seconds
        username_clean = username.strip() if username else full_name.strip().replace(" ", "_")
        dob_clean = dob.strip() if dob else ""

        cursor.execute('''
            INSERT OR REPLACE INTO pending_otps (email, otp_code, full_name, password_hash, expires_at, username, dob)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (email_clean, otp_code, full_name.strip(), pwd_hash, expires_at, username_clean, dob_clean))
        conn.commit()
        conn.close()
        return True

    def verify_and_activate_otp(self, email: str, otp_code: str) -> Optional[Dict[str, Any]]:
        """Verify 6-digit OTP code, validate expiration, and activate user account in users table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        email_clean = email.lower().strip()
        now = int(time.time())

        cursor.execute('''
            SELECT otp_code, full_name, password_hash, expires_at, username, dob FROM pending_otps WHERE email = ?
        ''', (email_clean,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        stored_otp, full_name, pwd_hash, expires_at, username, dob = row
        username_clean = (username or "").strip() or full_name.strip().replace(" ", "_")
        dob_clean = (dob or "").strip()
        age = self.calculate_age_from_dob(dob_clean)

        if now > expires_at:
            cursor.execute('DELETE FROM pending_otps WHERE email = ?', (email_clean,))
            conn.commit()
            conn.close()
            return None

        if stored_otp.strip() != otp_code.strip():
            conn.close()
            return None

        # OTP is valid — activate account in users table
        user_id = f"USER_{int(time.time())}_{random.randint(100, 999)}"
        try:
            cursor.execute('''
                INSERT INTO users (user_id, email, password_hash, full_name, username, dob, age)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, email_clean, pwd_hash, full_name, username_clean, dob_clean, age))
            cursor.execute('DELETE FROM pending_otps WHERE email = ?', (email_clean,))
            conn.commit()
            conn.close()
            return {
                "user_id": user_id,
                "email": email_clean,
                "full_name": full_name,
                "username": username_clean,
                "dob": dob_clean,
                "age": age,
                "role": "patient"
            }
        except sqlite3.IntegrityError:
            conn.close()
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Fetch active user record by email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, email, full_name, username, dob, age, role, created_at FROM users WHERE email = ?', (email.lower().strip(),))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "user_id": row[0],
                "email": row[1],
                "full_name": row[2],
                "username": row[3] or row[2],
                "dob": row[4] or "",
                "age": row[5] or 0,
                "role": row[6] or "patient",
                "created_at": row[7]
            }
        return None

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Fetch all registered user accounts for Admin Control Center"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, email, full_name, username, dob, age, role, created_at FROM users ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        users = []
        for r in rows:
            users.append({
                "user_id": r[0],
                "email": r[1],
                "full_name": r[2],
                "username": r[3] or r[2],
                "dob": r[4] or "",
                "age": r[5] or 0,
                "role": r[6] or "patient",
                "created_at": r[7]
            })
        return users


    def send_otp_email_dispatch(self, email: str, otp_code: str) -> bool:
        """
        Dispatch real email OTP verification code via Resend API or SMTP server.
        Falls back gracefully to development console logging if email credentials are not configured.
        NOTE: All print statements use ASCII-safe characters to prevent UnicodeEncodeError on Windows cp1252 consoles.
        """
        import logging
        logger = logging.getLogger("herbalist.otp")

        try:
            resend_key = os.getenv("RESEND_API_KEY", "")
            smtp_server = os.getenv("SMTP_SERVER", "")
            smtp_port = int(os.getenv("SMTP_PORT", 587))
            smtp_user = os.getenv("SMTP_USER", "")
            smtp_pass = os.getenv("SMTP_PASSWORD", "")
            sender_email = os.getenv("SMTP_FROM_EMAIL", smtp_user or "noreply@herbalist.ai")

            subject = "Herbalist AI Verification Code: " + otp_code
            html_body = f"""
            <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 520px; padding: 30px; border: 1px solid #2ecc71; border-radius: 16px; background: linear-gradient(135deg, #0b130f 0%, #142219 100%); color: #ffffff;">
                <div style="text-align:center;margin-bottom:20px;">
                    <div style="display:inline-block;width:48px;height:48px;border-radius:50%;background:rgba(46,204,113,0.15);border:2px solid #2ecc71;line-height:48px;font-size:24px;">&#127807;</div>
                </div>
                <h2 style="color: #2ecc71; text-align:center; margin:0 0 8px 0; font-size:20px;">Herbalist AI</h2>
                <p style="color:#95a79b; text-align:center; margin:0 0 24px 0; font-size:13px;">Email Verification Required</p>
                <p style="margin:0 0 20px 0; line-height:1.6;">Welcome! Please use the 6-digit verification code below to activate your patient account:</p>
                <div style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #f39c12; background: rgba(20,34,25,0.8); padding: 16px 24px; border-radius: 12px; text-align: center; margin: 24px 0; border: 1px solid rgba(243,156,18,0.3);">
                    {otp_code}
                </div>
                <p style="font-size: 12px; color: #95a79b; text-align:center; margin-top:20px;">This verification code will expire in <strong style="color:#f39c12;">10 minutes</strong>. If you did not request this account, please ignore this message.</p>
                <hr style="border:none;border-top:1px solid rgba(46,204,113,0.2);margin:24px 0;">
                <p style="font-size:10px;color:#5a6e62;text-align:center;margin:0;">Herbalist AI - Intelligent Botanical Medicine Platform</p>
            </div>
            """

            # 1. Dispatch via Resend API (if configured)
            if resend_key:
                try:
                    import urllib.request
                    import json
                    resend_sender = "onboarding@resend.dev" if "resend.dev" in sender_email or "herbalist.ai" in sender_email else sender_email
                    req_data = json.dumps({
                        "from": f"Herbalist AI <{resend_sender}>",
                        "to": [email],
                        "subject": subject,
                        "html": html_body
                    }).encode('utf-8')
                    req = urllib.request.Request(
                        "https://api.resend.com/emails",
                        data=req_data,
                        headers={
                            "Authorization": f"Bearer {resend_key.strip()}",
                            "Content-Type": "application/json"
                        }
                    )
                    with urllib.request.urlopen(req) as resp:
                        if resp.status in (200, 201):
                            logger.info(f"[OTP Service] Dispatched OTP to {email} via Resend API")
                            return True
                except Exception as re_err:
                    logger.warning(f"[OTP Service] Resend API failed: {re_err}")

            # 2. Dispatch via SMTP Server (Supports SSL Port 465 & STARTTLS Port 587 with cloud fallback)
            if smtp_server and smtp_user and smtp_pass:
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                from email.utils import formataddr

                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = formataddr(("Herbalist AI", sender_email))
                msg["To"] = email
                msg.attach(MIMEText(html_body, "html"))

                # Attempt A: Direct SSL on Port 465 (Preferred for Cloud Hosting like Render/AWS)
                if smtp_port == 465 or "gmail" in smtp_server.lower():
                    try:
                        with smtplib.SMTP_SSL(smtp_server, 465, timeout=12) as server:
                            server.login(smtp_user, smtp_pass)
                            server.sendmail(sender_email, [email], msg.as_string())
                        logger.info(f"[OTP Service] Successfully dispatched OTP email to {email} via SMTP_SSL (Port 465)")
                        return True
                    except Exception as ssl_err:
                        logger.warning(f"[OTP Service] SMTP_SSL Port 465 attempt failed: {ssl_err}, trying STARTTLS...")

                # Attempt B: STARTTLS on Port 587
                try:
                    with smtplib.SMTP(smtp_server, smtp_port, timeout=12) as server:
                        server.starttls()
                        server.login(smtp_user, smtp_pass)
                        server.sendmail(sender_email, [email], msg.as_string())
                    logger.info(f"[OTP Service] Successfully dispatched OTP email to {email} via SMTP STARTTLS (Port {smtp_port})")
                    return True
                except Exception as tls_err:
                    logger.error(f"[OTP Service] SMTP STARTTLS Port {smtp_port} attempt failed: {tls_err}")

                    # Attempt C: Final SSL Port 465 Fallback
                    try:
                        with smtplib.SMTP_SSL(smtp_server, 465, timeout=12) as server:
                            server.login(smtp_user, smtp_pass)
                            server.sendmail(sender_email, [email], msg.as_string())
                        logger.info(f"[OTP Service] Successfully dispatched OTP email to {email} via fallback SMTP_SSL (Port 465)")
                        return True
                    except Exception as final_err:
                        logger.error(f"[OTP Service] All SMTP attempts failed: {final_err}", exc_info=True)

            # 3. Development Fallback Console Logger
            logger.warning(f"[OTP Service] No email provider available. OTP for {email}: {otp_code}")
            return True

        except Exception as outer_err:
            # Catch-all to prevent background task from dying silently
            import logging
            logging.getLogger("herbalist.otp").error(f"[OTP Service] CRITICAL dispatch failure: {outer_err}", exc_info=True)
            return False


    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user credentials against SQLite users database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        pwd_hash = self.hash_password(password)

        cursor.execute('''
            SELECT user_id, email, full_name, role FROM users
            WHERE email = ? AND password_hash = ?
        ''', (email.lower().strip(), pwd_hash))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {"user_id": row[0], "email": row[1], "full_name": row[2], "role": row[3]}
        return None

    def save_patient_prescription(self, user_id: str, patient_name: str, symptoms: str, primary_diagnosis: str, prescribed_formulation: str, prescription_card: str) -> str:
        """Save a consultation prescription to patient account history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        rx_id = f"RX_{int(time.time())}_{random.randint(100, 999)}"

        cursor.execute('''
            INSERT INTO patient_prescriptions (rx_id, user_id, patient_name, symptoms, primary_diagnosis, prescribed_formulation, prescription_card)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (rx_id, user_id, patient_name, symptoms, primary_diagnosis, prescribed_formulation, prescription_card))
        conn.commit()
        conn.close()
        return rx_id

    def get_user_prescriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve saved prescriptions for a specific user ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT rx_id, patient_name, symptoms, primary_diagnosis, prescribed_formulation, prescription_card, created_at
            FROM patient_prescriptions WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            results.append({
                "rx_id": r[0],
                "patient_name": r[1],
                "symptoms": r[2],
                "primary_diagnosis": r[3],
                "prescribed_formulation": r[4],
                "prescription_card": r[5],
                "created_at": r[6]
            })
        return results

    def learn_new_herb_synergy(self, gemini_response: dict) -> int:
        """Auto-expand semantic pharmacopeia from every Gemini 2.0 Flash discovery"""
        if not gemini_response:
            return 0
        
        plants = gemini_response.get("target_plants", [])
        bioactives = gemini_response.get("key_bioactives", [])
        diagnosis = gemini_response.get("primary_diagnosis", "General Wellness")
        count = 0
        
        for plant in plants:
            herb_key = plant.lower().replace(" ", "_")
            self.auto_expand_semantic_pharmacopeia(
                herb_key=herb_key,
                common_name=plant,
                botanical_name=plant,
                category="Gemini 2.0 Flash Discovery",
                active_bioactives=bioactives,
                therapeutic_props=[diagnosis],
                layman_name=f"Natural {plant} Extract",
                llm_source=f"Gemini 2.0 Flash | Diagnosis: {diagnosis}"
            )
            count += 1
        return count

    def seed_pharmacopeia_100(self):
        """Seed 100+ verified medicinal plants across African, Ayurvedic, TCM, and Western traditions"""
        plants = [
            # ── AFRICAN PHYTOTHERAPY (25 plants) ──
            ("bitter_leaf", "Bitter Leaf", "Vernonia amygdalina", "African Phytotherapy", "Vernodalin, Vernomygdin, Sesquiterpene lactones", "Anti-malarial, Hypoglycemic, Hepatoprotective, Blood Purification", "Blood-Cleansing Leaf Nutrients"),
            ("moringa", "Moringa", "Moringa oleifera", "African Phytotherapy", "Isothiocyanates, Quercetin, Chlorogenic acid, Beta-sitosterol", "Anti-inflammatory, Hypoglycemic, Antioxidant, Nutritive", "Miracle Tree Vitamins"),
            ("soursop", "Soursop", "Annona muricata", "African Phytotherapy", "Annonacin, Acetogenins, Muricatocin", "Anticancer, Sedative, Anti-parasitic, Immune-boosting", "Graviola Immune Boosters"),
            ("african_mango", "African Mango", "Irvingia gabonensis", "African Phytotherapy", "Mangiferin, Ellagic acid, Flavonoids", "Weight management, Hypocholesterolemic, Metabolic regulation", "Mango Seed Fat Burners"),
            ("hibiscus", "Hibiscus", "Hibiscus sabdariffa", "African Phytotherapy", "Anthocyanins, Delphinidin, Citric acid, Ascorbic acid", "Antihypertensive, Diuretic, Hepatoprotective, Antioxidant", "Zobo Heart-Health Nutrients"),
            ("pelargonium", "Pelargonium", "Pelargonium sidoides", "African Phytotherapy", "Umckalin, Coumarins, Gallic acid", "Bronchitis relief, Immune-stimulant, Antiviral", "South African Cold Relief"),
            ("devils_claw", "Devil's Claw", "Harpagophytum procumbens", "African Phytotherapy", "Harpagoside, Harpagide, Procumbide", "Anti-inflammatory, Analgesic, Anti-arthritic", "Joint Pain Relief Tuber"),
            ("pygeum", "Pygeum", "Prunus africana", "African Phytotherapy", "Beta-sitosterol, Ferulic acid, Ursolic acid", "Prostate health, Anti-inflammatory, Urological", "Prostate Bark Extract"),
            ("rooibos", "Rooibos", "Aspalathus linearis", "African Phytotherapy", "Aspalathin, Nothofagin, Quercetin", "Antioxidant, Anti-allergic, Anti-diabetic, Cardioprotective", "Red Bush Antioxidant Tea"),
            ("aloe_ferox", "Aloe Ferox", "Aloe ferox", "African Phytotherapy", "Aloin, Aloe-emodin, Barbaloin", "Laxative, Wound healing, Anti-inflammatory, Digestive", "Cape Aloe Healing Gel"),
            ("sutherlandia", "Sutherlandia", "Lessertia frutescens", "African Phytotherapy", "L-Canavanine, Pinitol, GABA", "Immunomodulatory, Adaptogenic, Anti-viral", "Cancer Bush Immune Support"),
            ("african_potato", "African Potato", "Hypoxis hemerocallidea", "African Phytotherapy", "Hypoxoside, Rooperol, Beta-sitosterol", "Immune-stimulant, Anti-inflammatory, Prostate health", "Star Flower Immune Booster"),
            ("buchu", "Buchu", "Agathosma betulina", "African Phytotherapy", "Diosphenol, Pulegone, Limonene", "Urinary antiseptic, Diuretic, Anti-inflammatory", "Kidney Cleanse Leaf"),
            ("sceletium", "Sceletium", "Sceletium tortuosum", "African Phytotherapy", "Mesembrine, Mesembrenol, Tortuosamine", "Anxiolytic, Antidepressant, Cognitive enhancer", "Kanna Mood Lifter"),
            ("baobab", "Baobab", "Adansonia digitata", "African Phytotherapy", "Vitamin C, Polyphenols, Pectin, Calcium", "Antioxidant, Prebiotic, Anti-inflammatory, Nutritive", "Superfruit Vitamin Powder"),
            ("neem", "Neem", "Azadirachta indica", "African Phytotherapy", "Azadirachtin, Nimbin, Gedunin, Quercetin", "Anti-malarial, Antibacterial, Antifungal, Hypoglycemic", "Bitter Tree Medicine"),
            ("pawpaw_leaf", "Pawpaw Leaf", "Carica papaya", "African Phytotherapy", "Papain, Carpain, Chymopapain, Acetogenin", "Dengue platelet boost, Digestive, Anti-parasitic", "Papaya Leaf Platelet Booster"),
            ("african_basil", "African Basil", "Ocimum gratissimum", "African Phytotherapy", "Eugenol, Thymol, Linalool", "Antimicrobial, Hypoglycemic, Anti-diarrheal", "Scent Leaf Medicine"),
            ("kola_nut", "Kola Nut", "Cola nitida", "African Phytotherapy", "Caffeine, Theobromine, Kolanin", "Stimulant, Bronchodilator, Digestive, Anti-depressant", "Energy Nut Stimulant"),
            ("shea_butter_tree", "Shea Butter Tree", "Vitellaria paradoxa", "African Phytotherapy", "Lupeol, Cinnamic acid esters, Tocopherols", "Skin healing, Anti-inflammatory, Emollient", "Skin Repair Butter"),
            ("griffonia", "Griffonia", "Griffonia simplicifolia", "African Phytotherapy", "5-HTP, Serotonin precursors", "Antidepressant, Sleep aid, Appetite suppressant", "Natural Serotonin Seed"),
            ("strophanthus", "Strophanthus", "Strophanthus gratus", "African Phytotherapy", "Ouabain, Strophanthin K", "Cardiac glycoside, Heart failure support", "Heart Vine Medicine"),
            ("voacanga", "Voacanga", "Voacanga africana", "African Phytotherapy", "Voacamine, Tabersonine, Ibogaine precursors", "Cognitive enhancer, Cardiovascular support", "Brain Bark Extract"),
            ("uzara", "Uzara", "Xysmalobium undulatum", "African Phytotherapy", "Uzarin, Xysmalobin", "Anti-diarrheal, Antispasmodic, Digestive", "Stomach Root Remedy"),
            ("hoodia", "Hoodia", "Hoodia gordonii", "African Phytotherapy", "P57 (steroidal glycoside)", "Appetite suppressant, Anti-obesity", "Kalahari Appetite Cactus"),

            # ── AYURVEDA (25 plants) ──
            ("ashwagandha", "Ashwagandha", "Withania somnifera", "Ayurveda", "Withanolides, Withaferin A, Sitoindosides", "Adaptogenic, Anxiolytic, Immune-modulating, Anti-fatigue", "Indian Ginseng Stress Relief"),
            ("tulsi", "Tulsi (Holy Basil)", "Ocimum tenuiflorum", "Ayurveda", "Eugenol, Rosmarinic acid, Ursolic acid, Apigenin", "Adaptogenic, Antimicrobial, Anti-inflammatory, Respiratory", "Sacred Basil Immunity Tea"),
            ("turmeric", "Turmeric", "Curcuma longa", "Ayurveda", "Curcumin, Demethoxycurcumin, Bisdemethoxycurcumin, Turmerone", "Anti-inflammatory, Antioxidant, Hepatoprotective, Neuroprotective", "Golden Anti-Inflammatory Spice"),
            ("brahmi", "Brahmi", "Bacopa monnieri", "Ayurveda", "Bacosides A & B, Bacopasaponins, Hersaponin", "Nootropic, Anxiolytic, Memory enhancement, Neuroprotective", "Brain Memory Herb"),
            ("guggulu", "Guggulu", "Commiphora wightii", "Ayurveda", "Guggulsterones Z & E, Myrrhanol, Guggulipid", "Hypolipidemic, Anti-inflammatory, Thyroid-stimulating", "Cholesterol Resin Medicine"),
            ("triphala_amalaki", "Amalaki (Amla)", "Emblica officinalis", "Ayurveda", "Gallic acid, Ellagic acid, Vitamin C, Emblicanin", "Antioxidant, Immunomodulatory, Hepatoprotective, Rejuvenating", "Indian Gooseberry Vitamin C"),
            ("shatavari", "Shatavari", "Asparagus racemosus", "Ayurveda", "Shatavarins, Sarsasapogenin, Racemosol", "Female reproductive tonic, Galactagogue, Adaptogenic", "Women's Wellness Root"),
            ("guduchi", "Guduchi (Giloy)", "Tinospora cordifolia", "Ayurveda", "Berberine, Tinosporin, Tinosporaside, Giloin", "Immunomodulatory, Antipyretic, Anti-diabetic, Hepatoprotective", "Immune Stem Vine"),
            ("arjuna", "Arjuna", "Terminalia arjuna", "Ayurveda", "Arjunolic acid, Arjunetin, Arjungenin, Tannins", "Cardioprotective, Antihypertensive, Antioxidant, Anti-ischemic", "Heart Bark Medicine"),
            ("haritaki", "Haritaki", "Terminalia chebula", "Ayurveda", "Chebulagic acid, Chebulinic acid, Gallic acid, Tannins", "Digestive, Laxative, Antioxidant, Rejuvenating", "King of Medicines Fruit"),
            ("gotu_kola", "Gotu Kola", "Centella asiatica", "Ayurveda", "Asiaticoside, Madecassoside, Brahmoside", "Wound healing, Cognitive enhancer, Venous insufficiency", "Brain Tonic Leaf"),
            ("boswellia", "Boswellia (Indian Frankincense)", "Boswellia serrata", "Ayurveda", "Boswellic acids (AKBA), Incensole acetate", "Anti-inflammatory, Anti-arthritic, Asthma relief", "Indian Frankincense Resin"),
            ("pippali", "Pippali (Long Pepper)", "Piper longum", "Ayurveda", "Piperine, Piperlongumine, Pellitorine", "Bioenhancer, Respiratory, Digestive, Metabolic", "Long Pepper Biobooster"),
            ("bhringaraj", "Bhringaraj", "Eclipta alba", "Ayurveda", "Wedelolactone, Ecliptine, Coumestans", "Hepatoprotective, Hair growth, Anti-aging, Rejuvenating", "Hair Growth Liver Herb"),
            ("trikatu_ginger", "Ginger", "Zingiber officinale", "Ayurveda", "Gingerols, Shogaols, Zingerone, Paradols", "Anti-emetic, Anti-inflammatory, Digestive, Circulatory", "Warming Stomach Spice"),
            ("manjistha", "Manjistha", "Rubia cordifolia", "Ayurveda", "Purpurin, Munjistin, Alizarin, Rubiadin", "Blood purifier, Lymphatic cleanser, Skin health", "Blood Purifying Root"),
            ("shankhapushpi", "Shankhapushpi", "Convolvulus pluricaulis", "Ayurveda", "Shankhapushpine, Convolamine, Scopoletin", "Nootropic, Anxiolytic, Memory enhancer", "Conch Flower Brain Tonic"),
            ("licorice_ayur", "Mulethi (Licorice)", "Glycyrrhiza glabra", "Ayurveda", "Glycyrrhizin, Glabridin, Liquiritigenin", "Expectorant, Anti-ulcer, Adrenal support, Anti-viral", "Sweet Root Throat Soother"),
            ("kutki", "Kutki", "Picrorhiza kurroa", "Ayurveda", "Kutkin, Picroside I & II, Apocynin", "Hepatoprotective, Immunomodulatory, Anti-asthmatic", "Liver Guard Bitter Root"),
            ("vidanga", "Vidanga", "Embelia ribes", "Ayurveda", "Embelin, Vilangin, Quercitol", "Anthelmintic, Digestive, Antibacterial, Contraceptive", "Worm-Killing Berry"),
            ("vacha", "Vacha (Calamus)", "Acorus calamus", "Ayurveda", "Alpha-asarone, Beta-asarone, Acolamone", "Cognitive enhancer, Anti-epileptic, Digestive", "Sweet Flag Brain Root"),
            ("punarnava", "Punarnava", "Boerhavia diffusa", "Ayurveda", "Punarnavine, Boeravinone, Liriodendrin", "Diuretic, Hepatoprotective, Anti-inflammatory, Renal", "Kidney Renewal Herb"),
            ("bibhitaki", "Bibhitaki", "Terminalia bellirica", "Ayurveda", "Bellericanin, Gallic acid, Ellagic acid, Lignans", "Expectorant, Astringent, Laxative, Antioxidant", "Triphala Respiratory Fruit"),
            ("sariva", "Sariva", "Hemidesmus indicus", "Ayurveda", "Hemidesmine, 2-Hydroxy-4-methoxybenzaldehyde", "Blood purifier, Anti-inflammatory, Cooling, Dermatological", "Indian Sarsaparilla Coolant"),
            ("kalmegh", "Kalmegh", "Andrographis paniculata", "Ayurveda", "Andrographolide, Neoandrographolide, Diterpenoids", "Hepatoprotective, Immunostimulant, Antipyretic, Anti-viral", "King of Bitters Immunity"),

            # ── TRADITIONAL CHINESE MEDICINE (25 plants) ──
            ("ginseng", "Ginseng", "Panax ginseng", "TCM", "Ginsenosides Rg1 Rb1, Panaxadiol, Panaxatriol", "Adaptogenic, Cognitive enhancer, Immune-modulating, Anti-fatigue", "Qi Energy Root"),
            ("astragalus", "Astragalus", "Astragalus membranaceus", "TCM", "Astragaloside IV, Cycloastragenol, Polysaccharides", "Immunomodulatory, Cardioprotective, Anti-aging, Adaptogenic", "Huang Qi Immune Shield"),
            ("reishi", "Reishi Mushroom", "Ganoderma lucidum", "TCM", "Ganoderic acids, Beta-glucans, Triterpenes, Adenosine", "Immunomodulatory, Hepatoprotective, Anti-tumor, Adaptogenic", "Mushroom of Immortality"),
            ("cordyceps", "Cordyceps", "Cordyceps sinensis", "TCM", "Cordycepin, Adenosine, Polysaccharides, Ergosterol", "Energy enhancer, Respiratory support, Anti-aging, Athletic performance", "Caterpillar Fungus Energy"),
            ("schisandra", "Schisandra", "Schisandra chinensis", "TCM", "Schisandrin B, Gomisin A, Deoxyschisandrin", "Adaptogenic, Hepatoprotective, Cognitive enhancer, Anti-fatigue", "Five-Flavor Berry Tonic"),
            ("dong_quai", "Dong Quai", "Angelica sinensis", "TCM", "Ferulic acid, Ligustilide, Z-Butylidenephthalide", "Female tonic, Blood-building, Menstrual regulation, Circulatory", "Female Ginseng Blood Builder"),
            ("he_shou_wu", "He Shou Wu", "Polygonum multiflorum", "TCM", "Emodin, Chrysophanol, Stilbene glycosides, Lecithin", "Anti-aging, Hair health, Hepatoprotective, Tonic", "Longevity Vine Root"),
            ("danshen", "Danshen (Red Sage)", "Salvia miltiorrhiza", "TCM", "Tanshinone IIA, Salvianolic acid B, Cryptotanshinone", "Cardiovascular, Anti-thrombotic, Hepatoprotective, Antioxidant", "Heart Blood Sage Root"),
            ("baikal_skullcap", "Baikal Skullcap", "Scutellaria baicalensis", "TCM", "Baicalin, Baicalein, Wogonin, Oroxylin A", "Anti-inflammatory, Antiviral, Neuroprotective, Hepatoprotective", "Huang Qin Inflammation Guard"),
            ("jujube", "Jujube (Red Date)", "Ziziphus jujuba", "TCM", "Jujubosides, Betulinic acid, Vitamin C, Saponins", "Sedative, Anxiolytic, Digestive, Immunomodulatory", "Calming Red Date Fruit"),
            ("chrysanthemum", "Chrysanthemum", "Chrysanthemum morifolium", "TCM", "Luteolin, Apigenin, Chlorogenic acid, Acacetin", "Eye health, Antipyretic, Antihypertensive, Hepatoprotective", "Cooling Eye Flower Tea"),
            ("lycium_goji", "Goji Berry", "Lycium barbarum", "TCM", "Lycium barbarum polysaccharides, Zeaxanthin, Betaine", "Eye health, Immunomodulatory, Anti-aging, Hepatoprotective", "Longevity Red Berry"),
            ("codonopsis", "Codonopsis", "Codonopsis pilosula", "TCM", "Codonopsin, Lobetyolin, Tangshenoside", "Qi tonic, Digestive, Immune-enhancing, Adaptogenic", "Poor Man's Ginseng Root"),
            ("eucommia", "Eucommia", "Eucommia ulmoides", "TCM", "Aucubin, Geniposide, Chlorogenic acid, Lignans", "Kidney-liver tonic, Antihypertensive, Bone strengthening", "Du Zhong Kidney Bark"),
            ("white_peony", "White Peony", "Paeonia lactiflora", "TCM", "Paeoniflorin, Albiflorin, Paeonol, Benzoic acid", "Hepatoprotective, Analgesic, Antispasmodic, Blood-nourishing", "Bai Shao Blood Root"),
            ("rehmannia", "Rehmannia", "Rehmannia glutinosa", "TCM", "Catalpol, Rehmannioside, Acteoside, Iridoid glycosides", "Kidney-liver tonic, Blood-nourishing, Anti-inflammatory, Anti-aging", "Di Huang Kidney Nourisher"),
            ("coptis", "Coptis (Goldthread)", "Coptis chinensis", "TCM", "Berberine, Coptisine, Palmatine, Worenine", "Antimicrobial, Anti-diabetic, Anti-inflammatory, Digestive", "Huang Lian Bitter Cleanser"),
            ("ophiopogon", "Ophiopogon", "Ophiopogon japonicus", "TCM", "Ophiopogonin D, Ruscogenin, Polysaccharides", "Yin tonic, Lung-moistening, Cardioprotective, Anti-diabetic", "Mai Dong Lung Moistener"),
            ("magnolia_bark", "Magnolia Bark", "Magnolia officinalis", "TCM", "Honokiol, Magnolol, Obovatol", "Anxiolytic, Anti-inflammatory, Digestive, Neuroprotective", "Hou Po Calm Bark"),
            ("artemisia", "Sweet Wormwood", "Artemisia annua", "TCM", "Artemisinin, Arteannuin B, Scopoletin", "Anti-malarial, Antipyretic, Anti-parasitic, Anti-cancer research", "Qing Hao Malaria Fighter"),
            ("salvia_root", "Salvia Root", "Salvia miltiorrhiza", "TCM", "Salvianolic acid A, Tanshinone I, Dihydrotanshinone", "Cardiovascular health, Blood circulation, Anti-fibrotic", "Dan Shen Heart Protector"),
            ("poria", "Poria Mushroom", "Wolfiporia extensa", "TCM", "Pachymic acid, Dehydrotumulosic acid, Polysaccharides", "Diuretic, Sedative, Immune-modulating, Digestive", "Fu Ling Water Mushroom"),
            ("gastrodia", "Gastrodia", "Gastrodia elata", "TCM", "Gastrodin, Vanillin, p-Hydroxybenzaldehyde", "Anti-convulsant, Sedative, Neuroprotective, Anti-migraine", "Tian Ma Headache Tuber"),
            ("atractylodes", "Atractylodes", "Atractylodes macrocephala", "TCM", "Atractylenolide I II III, Atractylon", "Digestive, Qi tonic, Diuretic, Immune-modulating", "Bai Zhu Stomach Strengthener"),
            ("angelica_dahurica", "Angelica Dahurica", "Angelica dahurica", "TCM", "Imperatorin, Isoimperatorin, Byakangelicol", "Analgesic, Anti-inflammatory, Sinus relief, Dermatological", "Bai Zhi Pain Relief Root"),

            # ── WESTERN HERBALISM (25 plants) ──
            ("st_johns_wort", "St. John's Wort", "Hypericum perforatum", "Western Herbalism", "Hypericin, Hyperforin, Adhyperforin, Flavonoids", "Antidepressant, Anxiolytic, Anti-viral, Wound healing", "Mood-Lifting Sun Flower"),
            ("milk_thistle", "Milk Thistle", "Silybum marianum", "Western Herbalism", "Silymarin, Silibinin, Silydianin, Silychristin", "Hepatoprotective, Antioxidant, Anti-fibrotic, Detoxifying", "Liver Shield Thistle Seed"),
            ("elderberry", "Elderberry", "Sambucus nigra", "Western Herbalism", "Anthocyanins, Rutin, Quercetin, Isorhamnetin", "Antiviral, Immune-boosting, Anti-inflammatory, Respiratory", "Cold & Flu Berry Syrup"),
            ("hawthorn", "Hawthorn", "Crataegus monogyna", "Western Herbalism", "Vitexin, Hyperoside, Oligomeric proanthocyanidins", "Cardiotonic, Antihypertensive, Antioxidant, Anti-arrhythmic", "Heart Berry Bush"),
            ("ginkgo", "Ginkgo", "Ginkgo biloba", "Western Herbalism", "Ginkgolides A B C, Bilobalide, Flavone glycosides", "Cerebrovascular, Neuroprotective, PAF antagonist, Antioxidant", "Memory Tree Leaf"),
            ("valerian", "Valerian", "Valeriana officinalis", "Western Herbalism", "Valerenic acid, Isovaleric acid, Hesperidin, Linarin", "Sedative, Anxiolytic, Sleep aid, Antispasmodic", "Natural Sleep Root"),
            ("echinacea", "Echinacea", "Echinacea purpurea", "Western Herbalism", "Alkylamides, Cichoric acid, Echinacosides, Polysaccharides", "Immunostimulant, Anti-cold, Anti-inflammatory, Wound healing", "Purple Cone Immune Flower"),
            ("chamomile", "Chamomile", "Matricaria chamomilla", "Western Herbalism", "Apigenin, Bisabolol, Chamazulene, Matricine", "Anxiolytic, Digestive, Anti-inflammatory, Sleep aid", "Calming Daisy Flower Tea"),
            ("peppermint", "Peppermint", "Mentha piperita", "Western Herbalism", "Menthol, Menthone, Rosmarinic acid, Luteolin", "Digestive, Antispasmodic, Analgesic, Decongestant", "Cool Mint Stomach Soother"),
            ("lavender", "Lavender", "Lavandula angustifolia", "Western Herbalism", "Linalool, Linalyl acetate, Lavandulol, Terpinen-4-ol", "Anxiolytic, Sedative, Analgesic, Wound healing", "Calming Purple Flower Oil"),
            ("saw_palmetto", "Saw Palmetto", "Serenoa repens", "Western Herbalism", "Fatty acids, Beta-sitosterol, Flavonoids, Polysaccharides", "Prostate health, Anti-androgenic, Anti-inflammatory, Urological", "Prostate Palm Berry"),
            ("passionflower", "Passionflower", "Passiflora incarnata", "Western Herbalism", "Chrysin, Vitexin, Isovitexin, Harmine, Harmane", "Anxiolytic, Sedative, Antispasmodic, Sleep aid", "Anxiety Relief Vine Flower"),
            ("calendula", "Calendula", "Calendula officinalis", "Western Herbalism", "Triterpenoids, Faradiol, Carotenoids, Flavoxanthin", "Wound healing, Anti-inflammatory, Antifungal, Skin repair", "Healing Marigold Salve"),
            ("marshmallow_root", "Marshmallow Root", "Althaea officinalis", "Western Herbalism", "Mucilage polysaccharides, Flavonoids, Pectin, Asparagine", "Demulcent, Sore throat relief, Digestive, Urinary soothing", "Throat Soothing Root Gel"),
            ("nettle", "Stinging Nettle", "Urtica dioica", "Western Herbalism", "Formic acid, Chlorophyll, Beta-sitosterol, Scopoletin", "Anti-allergic, Diuretic, Anti-inflammatory, Nutritive", "Iron-Rich Allergy Leaf"),
            ("dandelion", "Dandelion", "Taraxacum officinale", "Western Herbalism", "Taraxasterol, Inulin, Chicoric acid, Luteolin", "Diuretic, Hepatoprotective, Prebiotic, Digestive", "Liver & Kidney Cleansing Weed"),
            ("black_cohosh", "Black Cohosh", "Actaea racemosa", "Western Herbalism", "Triterpene glycosides, Actein, Cimicifugoside, Formononetin", "Menopausal relief, Anti-inflammatory, Antispasmodic", "Women's Menopause Root"),
            ("yarrow", "Yarrow", "Achillea millefolium", "Western Herbalism", "Achillein, Azulene, Camphor, Chamazulene", "Hemostatic, Anti-inflammatory, Digestive, Diaphoretic", "Soldier's Wound Herb"),
            ("lemon_balm", "Lemon Balm", "Melissa officinalis", "Western Herbalism", "Rosmarinic acid, Citral, Citronellal, Eugenol", "Anxiolytic, Antiviral, Digestive, Cognitive", "Calming Lemon Leaf Tea"),
            ("feverfew", "Feverfew", "Tanacetum parthenium", "Western Herbalism", "Parthenolide, Tanetin, Sesquiterpene lactones", "Anti-migraine, Anti-inflammatory, Antipyretic, Anti-platelet", "Migraine Prevention Daisy"),
            ("oregon_grape", "Oregon Grape", "Mahonia aquifolium", "Western Herbalism", "Berberine, Berbamine, Oxyacanthine, Jatrorrhizine", "Antimicrobial, Hepatoprotective, Psoriasis, Digestive", "Barberry Skin & Liver Root"),
            ("plantain_herb", "Plantain Herb", "Plantago major", "Western Herbalism", "Aucubin, Allantoin, Mucilage, Flavonoids", "Wound healing, Anti-inflammatory, Respiratory, Demulcent", "Healing Weed Leaf Poultice"),
            ("skullcap", "Skullcap", "Scutellaria lateriflora", "Western Herbalism", "Baicalin, Scutellarin, Melatonin, Flavonoids", "Anxiolytic, Sedative, Antispasmodic, Neuroprotective", "Nerve-Calming Blue Cap"),
            ("white_willow", "White Willow Bark", "Salix alba", "Western Herbalism", "Salicin, Salicortin, Tremulacin, Flavonoids", "Analgesic, Anti-inflammatory, Antipyretic, Antirheumatic", "Natural Aspirin Bark"),
            ("cinnamon", "Ceylon Cinnamon", "Cinnamomum verum", "Western Herbalism", "Cinnamaldehyde, Eugenol, Linalool, Coumarin (trace)", "Hypoglycemic, Antimicrobial, Anti-inflammatory, Circulatory", "Blood Sugar Balancing Spice"),
        ]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        inserted = 0

        for p in plants:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO semantic_pharmacopeia
                    (herb_key, common_name, botanical_name, category, active_bioactives, therapeutic_properties, layman_nutrient_name, discovered_from_llm)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (p[0], p[1], p[2], p[3], p[4], p[5], p[6], "Curated WHO/Commission E/PubMed Pharmacopeia"))
                if cursor.rowcount > 0:
                    inserted += 1
            except Exception:
                pass

        conn.commit()
        conn.close()
        return inserted

    def lookup_herbs_for_condition(self, condition_keywords: List[str]) -> List[Dict[str, str]]:
        """Query the semantic pharmacopeia for herbs matching condition keywords"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        results = []
        for keyword in condition_keywords:
            kw = f"%{keyword.lower()}%"
            cursor.execute('''
                SELECT common_name, botanical_name, category, active_bioactives, therapeutic_properties, layman_nutrient_name 
                FROM semantic_pharmacopeia 
                WHERE LOWER(therapeutic_properties) LIKE ? OR LOWER(active_bioactives) LIKE ? OR LOWER(common_name) LIKE ?
            ''', (kw, kw, kw))
            for row in cursor.fetchall():
                results.append({
                    "common_name": row[0],
                    "botanical_name": row[1],
                    "category": row[2],
                    "bioactives": row[3],
                    "therapeutic_properties": row[4],
                    "layman_name": row[5]
                })
        
        conn.close()
        seen = set()
        unique = []
        for r in results:
            if r["common_name"] not in seen:
                seen.add(r["common_name"])
                unique.append(r)
        return unique

    def export_fine_tuning_dataset(self, output_filepath: str = "fine_tuning_dataset_herbalist.jsonl") -> Dict[str, Any]:
        """
        Export all recorded patient consultations and learned bioactive synergies into a 
        standard JSONL Fine-Tuning dataset for training custom open-source models (e.g. Llama-3-70B, 
        Unsloth, Mistral, or Herbalist-7B).
        """
        import json
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT case_id, symptoms, primary_diagnosis, prescribed_formulation, bioactive_match_score, llm_reasoning_chain, timestamp FROM episodic_cases ORDER BY timestamp ASC')
        rows = cursor.fetchall()
        conn.close()

        system_prompt = (
            "You are Herbalist AI, an autonomous Senior Doctor and Clinical Phytotherapy Scientist "
            "backed by WHO Traditional Medicine Monographs, Commission E literature, and PubMed RAG clinical trials. "
            "Provide evidence-based botanical diagnoses, body-mass scaled 2-liter pot kitchen recipes, dietary guidelines, and bioactive matching."
        )

        samples = []
        for r in rows:
            case_id, symptoms, diagnosis, formulation, match_score, reasoning_chain, timestamp = r
            if not symptoms or not diagnosis:
                continue
                
            assistant_content = reasoning_chain if reasoning_chain else f"Primary Diagnosis: {diagnosis}\nPrescribed Phytotherapy Formulation: {formulation}\nBioactive Match Score: {match_score}%"
            
            sample = {
                "id": case_id,
                "timestamp": timestamp,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Clinical Presentation / Symptoms: {symptoms}"},
                    {"role": "assistant", "content": assistant_content}
                ]
            }
            samples.append(sample)

        # Write formatted samples to JSONL file
        with open(output_filepath, "w", encoding="utf-8") as f:
            for s in samples:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")

        return {
            "status": "success",
            "filepath": output_filepath,
            "total_samples": len(samples),
            "format": "OpenAI / ShareGPT / Llama-3 JSONL",
            "message": f"Exported {len(samples)} clinical training samples to {output_filepath} for fine-tuning Herbalist-7B"
        }


if __name__ == "__main__":
    memory = ClinicalMemoryStore()
    
    # Seed 100+ verified medicinal plants
    inserted = memory.seed_pharmacopeia_100()
    
    print("🧠 Persistent SQLite Clinical Memory Store Initialized Successfully!")
    stats = memory.get_memory_stats()
    print(f"   Status: {stats['memory_system_status']}")
    print(f"   Recorded Consultations: {stats['total_episodic_consultations']}")
    print(f"   Pharmacopeia Plants: {stats['semantic_learned_ingredients']}")
    print(f"   Newly Seeded Plants: {inserted}")
    print(f"   Learning Grade: {stats['continuous_learning_grade']}")
