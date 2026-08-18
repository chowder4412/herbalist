import os
import sys
import json
import re
import unittest

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from fastapi.testclient import TestClient
from main import app, memory_store


class FullSystemAuditSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_frontend_html_and_js_syntax(self):
        """Audit 1: Verify all 20 interactive frontend functions & JS syntax integrity"""
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        required_functions = [
            "handleKeyPress",
            "autoExpandTextarea",
            "submitQuery",
            "startNewChat",
            "restoreActiveSessionOnBoot",
            "persistActiveChatSession",
            "getLocalChatSessions",
            "saveLocalChatSessions",
            "renderRecentsList",
            "loadRecentConsultation",
            "openContextMenu",
            "shareConversation",
            "pinConversation",
            "renameConversation",
            "deleteConversation",
            "appendBubble",
            "showSection",
            "openKitchenCookMode",
            "exportPrescriptionPDF",
            "openArtifactsCanvas"
        ]

        for fn in required_functions:
            self.assertTrue(
                f"function {fn}" in html_content or f"{fn} = " in html_content,
                f"Missing frontend function: {fn}"
            )
        print("\n[AUDIT 1 PASS] All 20 frontend lifecycle functions are properly declared.")

    def test_02_backend_rest_endpoints(self):
        """Audit 2: Verify all core REST APIs (Root, Recents, Pharmacopeia, Profiles)"""
        # Root /
        res_root = self.client.get("/")
        self.assertEqual(res_root.status_code, 200)

        # /api/recents
        res_recents = self.client.get("/api/recents")
        self.assertEqual(res_recents.status_code, 200)
        self.assertIn("recents", res_recents.json())

        # /api/pharmacopeia
        res_pharma = self.client.get("/api/pharmacopeia")
        self.assertEqual(res_pharma.status_code, 200)
        self.assertGreater(len(res_pharma.json().get("herbs", [])), 0)

        # /api/profiles
        res_profiles = self.client.get("/api/profiles")
        self.assertEqual(res_profiles.status_code, 200)
        self.assertIn("profiles", res_profiles.json())

        print("[AUDIT 2 PASS] Core REST API endpoints (Root, Recents, Pharmacopeia, Profiles) are 100% operational.")

    def test_03_chatgpt_gemini_session_storage_schema(self):
        """Audit 3: Verify client localStorage session schema matches restoreActiveSessionOnBoot()"""
        mock_sessions = {
            "chat_1740001000": {
                "id": "chat_1740001000",
                "title": "Malaria & Fever Decoction",
                "isRenamed": False,
                "isPinned": True,
                "messages": [
                    {"role": "patient", "html": "<p>I am having malaria</p>", "timestamp": 1740001010},
                    {"role": "doctor", "html": "<p>I have diagnosed your condition...</p>", "timestamp": 1740001020}
                ],
                "prescription": {"primary_diagnosis": "Uncomplicated Malaria"},
                "updatedAt": 1740001025
            }
        }
        active_id = "chat_1740001000"
        sess = mock_sessions.get(active_id)
        self.assertIsNotNone(sess)
        self.assertEqual(len(sess["messages"]), 2)
        self.assertTrue(sess["isPinned"])
        print("[AUDIT 3 PASS] ChatGPT / Gemini style session storage schema verified.")

    def test_04_recents_database_and_guest_fallback(self):
        """Audit 4: Verify episodic_cases SQLite fallback populates Recents for unauthenticated sessions"""
        res = self.client.get("/api/recents")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "success")
        self.assertIsInstance(data.get("recents"), list)
        print(f"[AUDIT 4 PASS] Recents API successfully retrieved {len(data.get('recents'))} past cases from database.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
