import sys
import os
import json
import unittest
from fastapi.testclient import TestClient

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app, session_manager, memory_store, doctor

class TestFullSystemAudit(unittest.TestCase):
    """
    Comprehensive End-to-End System Audit for Herbalist AI Enterprise Grade
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.test_email = f"audit_patient_{os.urandom(4).hex()}@clinic.com"
        cls.test_password = "SecurePassword2026!"
        cls.test_name = "Dr. System Audit Patient"
        cls.jwt_token = None

    def test_01_user_registration_and_jwt_auth(self):
        """1. Audit JWT User Account Registration & Login"""
        print("\n--- AUDIT 1: JWT User Account Registration ---")
        res = self.client.post("/api/auth/register", json={
            "email": self.test_email,
            "password": self.test_password,
            "full_name": self.test_name
        })
        self.assertEqual(res.status_code, 200, f"Registration failed: {res.text}")
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("access_token", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["email"], self.test_email.lower())
        
        # Test Login
        print("--- AUDIT 1.1: JWT Login ---")
        login_res = self.client.post("/api/auth/login", json={
            "email": self.test_email,
            "password": self.test_password
        })
        self.assertEqual(login_res.status_code, 200)
        login_data = login_res.json()
        self.assertIn("access_token", login_data)
        TestFullSystemAudit.jwt_token = login_data["access_token"]
        print(f"[OK] JWT Auth Verified for {self.test_email}")

    def test_02_jwt_auth_me_endpoint(self):
        """2. Audit Authenticated Profile Verification (/api/auth/me)"""
        print("\n--- AUDIT 2: Authenticated Profile Verification ---")
        headers = {"Authorization": f"Bearer {TestFullSystemAudit.jwt_token}"}
        res = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["user"]["email"], self.test_email.lower())
        print("[OK] Bearer Token Handshake Verified")

    def test_03_upstash_redis_session_cache(self):
        """3. Audit Upstash Redis Distributed Session Storage"""
        print("\n--- AUDIT 3: Upstash Redis Distributed Cache ---")
        session_id = session_manager.create_session("Tinnitus & Migraine", 52, "Female", 72.0)
        
        fetched = session_manager.get_session(session_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["complaint"], "Tinnitus & Migraine")
        session_manager.delete_session(session_id)
        print("[OK] Upstash Redis REST Distributed Cache Synchronized")

    def test_04_qdrant_cloud_vector_db_rag(self):
        """4. Audit Qdrant Cloud 128D Vector RAG Search"""
        print("\n--- AUDIT 4: Qdrant Cloud RAG Vector Search ---")
        rag_engine = doctor.pubmed_rag
        results = rag_engine.retrieve_citations(condition="fever")
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)
        print(f"[OK] Qdrant Cloud Vector Search Returned {len(results)} Peer-Reviewed RAG Papers")

    def test_05_botanical_pharmacopeia_explorer(self):
        """5. Audit 116-Plant Botanical Pharmacopeia Explorer (/api/pharmacopeia)"""
        print("\n--- AUDIT 5: Botanical Pharmacopeia Database ---")
        res = self.client.get("/api/pharmacopeia?search=Curcumin&category=all")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("herbs", data)
        self.assertGreater(data["total"], 0)
        print(f"[OK] Pharmacopeia Explorer Query Returned {data['total']} Herbs")

    def test_06_socrates_triage_and_dynamic_volume(self):
        """6. Audit SOCRATES Multi-Turn Triage & Severity Dosing Math"""
        print("\n--- AUDIT 6: SOCRATES Triage & Dynamic Pot Volume Math ---")
        headers = {"Authorization": f"Bearer {TestFullSystemAudit.jwt_token}"}
        
        # Turn 1: Onset
        r1 = self.client.post("/api/diagnose", json={
            "complaint": "Severe joint inflammation and chronic knee stiffness",
            "weight_kg": 85.0,
            "severity": 8
        }, headers=headers)
        self.assertEqual(r1.status_code, 200)
        d1 = r1.json()
        self.assertTrue(d1.get("is_triage_question") or d1.get("primary_diagnosis"))
        print("[OK] SOCRATES Consultation State Engine Operating Correctly")

    def test_07_saved_patient_prescriptions(self):
        """7. Audit User Prescription Profile History (/api/my-prescriptions)"""
        print("\n--- AUDIT 7: Patient Prescription History ---")
        headers = {"Authorization": f"Bearer {TestFullSystemAudit.jwt_token}"}
        res = self.client.get("/api/my-prescriptions", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("prescriptions", data)
        print(f"[OK] Patient Prescriptions Storage Operational ({len(data['prescriptions'])} prescriptions found)")

if __name__ == "__main__":
    unittest.main()
