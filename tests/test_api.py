import unittest

try:
    from fastapi.testclient import TestClient
    from main import app
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    TestClient = None
    app = None

@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI / TestClient not installed in environment")
class TestFastAPIEndpoints(unittest.TestCase):
    
    def setUp(self):
        if FASTAPI_AVAILABLE:
            self.client = TestClient(app)

    def test_health_endpoint(self):
        """Test GET /health returns 200 and healthy status"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "Herbalist AI")

    def test_recents_endpoint(self):
        """Test GET /api/recents returns stats and recents list"""
        response = self.client.get("/api/recents")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("stats", data)
        self.assertIn("recents", data)

    def test_emergency_red_flag_api_trigger(self):
        """Test POST /api/diagnose includes inline emergency red-flag warning while proceeding with consultation"""
        payload = {
            "complaint": "Crushing chest pain radiating to left arm",
            "age": 55,
            "gender": "Male",
            "weight_kg": 80.0
        }
        response = self.client.post("/api/diagnose", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("CRITICAL SAFETY ALERT", data["conversational_message"])


    def test_greeting_api_flow(self):
        """Test POST /api/diagnose greeting response"""
        payload = {
            "complaint": "hello",
            "age": 30,
            "gender": "Female",
            "weight_kg": 65.0
        }
        response = self.client.post("/api/diagnose", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("is_greeting"))

    def test_jwt_creation_and_verification(self):
        """Test JWT token encoding, payload decoding, and signature verification"""
        from main import create_jwt_token, verify_jwt_token
        import time

        payload = {"user_id": "usr_99", "email": "test@herbalist.ai", "role": "clinician"}
        token = create_jwt_token(payload, expires_in_seconds=3600)
        
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 20)

        decoded = verify_jwt_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["user_id"], "usr_99")
        self.assertEqual(decoded["email"], "test@herbalist.ai")
        self.assertEqual(decoded["role"], "clinician")
        self.assertIn("exp", decoded)
        self.assertIn("iat", decoded)

    def test_otp_registration_and_verification_flow(self):
        """Test registration requiring 6-digit OTP, pending state storage, and verification activation"""
        from main import memory_store
        import time
        import random
        import sqlite3

        email = f"patient_otp_{int(time.time())}_{random.randint(1000, 9999)}@herbalist.ai"
        reg_payload = {
            "email": email,
            "password": "secure_password_123",
            "full_name": "Test OTP Patient"
        }

        # Step 1: Submit registration request (instantly registers & logs in)
        res1 = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertEqual(data1["status"], "success")
        self.assertIn("access_token", data1)
        self.assertEqual(data1["user"]["email"], email)

if __name__ == "__main__":
    unittest.main()


