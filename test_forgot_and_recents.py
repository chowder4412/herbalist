import unittest
import time
import json
from main import app, memory_store
from fastapi.testclient import TestClient

class TestForgotAndPasswordRecents(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_email = f"user_forgot_test_{int(time.time())}@herbalist.ai"
        self.test_pass_orig = "OriginalPass123!"
        self.test_pass_new = "NewSecretPass456!"

    def test_forgot_password_100_percent(self):
        """Confirm 100% end-to-end functionality of Forgot Password & Reset Flow"""
        # Step 1: Create user account directly in memory_store
        user = memory_store.create_user(
            email=self.test_email,
            password=self.test_pass_orig,
            full_name="Forgot Tester",
            username="forgot_tester",
            dob="1995-04-10"
        )
        self.assertIsNotNone(user, "Failed to create initial test user")

        # Step 2: Initiate Forgot Password
        resp = self.client.post("/api/auth/forgot-password", json={"email": self.test_email})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")

        # Step 3: Fetch the generated OTP from SQLite
        conn = memory_store.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT otp_code FROM password_reset_otps WHERE email = ?", (self.test_email,))
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row, "Password reset OTP was not stored in SQLite")
        otp_code = row[0]
        self.assertEqual(len(otp_code), 6)

        # Step 4: Submit Reset Password request
        reset_resp = self.client.post("/api/auth/reset-password", json={
            "email": self.test_email,
            "otp_code": otp_code,
            "new_password": self.test_pass_new
        })
        self.assertEqual(reset_resp.status_code, 200)
        reset_data = reset_resp.json()
        self.assertEqual(reset_data["status"], "success")
        self.assertIn("access_token", reset_data)

        # Step 5: Verify login works with NEW password and fails with OLD password
        old_login = self.client.post("/api/auth/login", json={
            "email": self.test_email,
            "password": self.test_pass_orig
        })
        self.assertEqual(old_login.status_code, 401, "Old password should be rejected after reset")

        new_login = self.client.post("/api/auth/login", json={
            "email": self.test_email,
            "password": self.test_pass_new
        })
        self.assertEqual(new_login.status_code, 200, "New password must authenticate successfully")
        self.assertIn("access_token", new_login.json())
        print(f"\n[OK 100% VERIFIED] Forgot Password & Reset Flow passed perfectly for {self.test_email}!")

    def test_new_consultation_added_to_recents(self):
        """Confirm that starting a consultation automatically populates the Recents list"""
        symptom_text = f"Severe chronic stomach pain and indigestion since last week {int(time.time())}"
        
        # Step 1: Submit new consultation
        diag_resp = self.client.post("/api/diagnose", json={
            "complaint": symptom_text,
            "age": 30,
            "gender": "Female",
            "weight_kg": 65.0
        })
        self.assertEqual(diag_resp.status_code, 200)

        # Step 2: Query /api/recents
        recents_resp = self.client.get("/api/recents")
        self.assertEqual(recents_resp.status_code, 200)
        recents_data = recents_resp.json()
        self.assertIn("recents", recents_data)
        
        recents_list = recents_data["recents"]
        self.assertGreater(len(recents_list), 0, "Recents list should not be empty after submitting a consultation")
        
        found = any(r["symptoms"] == symptom_text or symptom_text[:30] in r["symptoms"] for r in recents_list)
        self.assertTrue(found, "The newly created consultation was not found in the Recents list!")
        print(f"\n[OK 100% VERIFIED] New consultation successfully appended to Recents list ({len(recents_list)} items in Recents)!")

if __name__ == "__main__":
    unittest.main()
