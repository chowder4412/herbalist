import unittest
from fastapi.testclient import TestClient
from main import app
from routers.diagnose import evaluate_maternal_pediatric_safety

class TestFeatures145QA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_feature_1_recents_privacy_and_firestore_readiness(self):
        """Feature 1: Verify Recents is scoped strictly to authenticated users (no guest data leakage)."""
        res = self.client.get("/api/recents")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("recents"), [])
        print("\n[QA AUDIT 1 PASS] Feature 1 Verified: Guest Recents leakage eliminated, ready for user-isolated Firestore sync.")

    def test_feature_4_speech_translate_african_languages(self):
        """Feature 4: Verify speech translation endpoint across Yoruba, Hausa, Igbo, Swahili, French, English."""
        test_instruction = "Boil 20g of dried leaves in 2.0 liters of water for 15 minutes. Drink 1 cup morning and evening."
        
        languages = ["yo", "ha", "ig", "sw", "fr", "en"]
        for lang in languages:
            payload = {
                "text": test_instruction,
                "target_language": lang,
                "persona": "doctor"
            }
            res = self.client.post("/api/audio/speech-translate", json=payload)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["language"], lang)
            self.assertTrue(len(data.get("translated_text", "")) > 5)
            self.assertTrue(len(data.get("phonetic_speech_text", "")) > 5)
            print(f"  * Translated to {data['language']}: {len(data['translated_text'])} chars")
            
        print("[QA AUDIT 4 PASS] Feature 4 Verified: Multi-language African audio translation operational for all dialects.")

    def test_feature_5_pregnancy_safety_lock_engagement(self):
        """Feature 5: Verify Pregnancy Safety Lock eliminates emmenagogues (Rue/Wormwood) and substitutes gentle herbs."""
        mock_formulation = {
            "formulation_name": "Antimalarial Fever Blend",
            "ingredients": [
                {"common_name": "Ruta graveolens (Rue)", "botanical_name": "Ruta graveolens", "mass_grams": 20.0},
                {"common_name": "Artemisia absinthium (Wormwood)", "botanical_name": "Artemisia absinthium", "mass_grams": 15.0},
                {"common_name": "Zingiber officinale (Ginger)", "botanical_name": "Zingiber officinale", "mass_grams": 10.0}
            ]
        }
        
        # Test pregnant patient complaint
        safety_res = evaluate_maternal_pediatric_safety(
            complaint="I have fever and body aches and I am 6 months pregnant",
            age=28,
            is_pregnant=True,
            is_lactating=False,
            formulation_data=mock_formulation
        )
        
        self.assertTrue(safety_res["is_locked"])
        self.assertEqual(safety_res["category"], "PREGNANCY_SAFETY_LOCK")
        self.assertEqual(len(safety_res["substitutions"]), 2)  # Rue and Wormwood should be substituted
        
        # Verify contraindicated herbs were replaced with safe German Chamomile / Ginger
        remaining_names = [ing["common_name"] for ing in mock_formulation["ingredients"]]
        self.assertNotIn("Ruta graveolens (Rue)", remaining_names)
        self.assertNotIn("Artemisia absinthium (Wormwood)", remaining_names)
        self.assertTrue(any("Chamomile" in name for name in remaining_names))
        
        print("\n[QA AUDIT 5A PASS] Feature 5 Verified: Pregnancy Safety Lock active, emmenagogues eliminated and replaced.")

    def test_feature_5_pediatric_safety_lock_and_clarks_rule(self):
        """Feature 5: Verify Pediatric Safety Lock applies Clark's rule mass scaling for young children (age < 12)."""
        mock_formulation = {
            "formulation_name": "Pediatric Soothing Tea",
            "ingredients": [
                {"common_name": "Salix alba (Willow Bark)", "botanical_name": "Salix alba", "mass_grams": 30.0},
                {"common_name": "Matricaria chamomilla", "botanical_name": "Matricaria chamomilla", "mass_grams": 20.0}
            ]
        }
        
        # Test 5-year-old child
        safety_res = evaluate_maternal_pediatric_safety(
            complaint="My 5 year old child has a mild fever",
            age=5,
            is_pregnant=False,
            is_lactating=False,
            formulation_data=mock_formulation
        )
        
        self.assertTrue(safety_res["is_locked"])
        self.assertEqual(safety_res["category"], "PEDIATRIC_SAFETY_LOCK")
        
        # Willow bark should be eliminated (Salicylates / Reye's risk)
        remaining_names = [ing["common_name"] for ing in mock_formulation["ingredients"]]
        self.assertNotIn("Salix alba (Willow Bark)", remaining_names)
        
        # Chamomile mass should be scaled down via Clark's rule (5 / 70 * 20 ≈ 1.4g)
        chamomile_ing = next(ing for ing in mock_formulation["ingredients"] if "Matricaria" in ing.get("botanical_name", ""))
        self.assertLess(chamomile_ing["mass_grams"], 5.0)
        
        print(f"\n[QA AUDIT 5B PASS] Feature 5 Verified: Pediatric Safety Lock active, Willow Bark eliminated, Clark's rule dosage scaled to {chamomile_ing['mass_grams']}g.")

if __name__ == '__main__':
    unittest.main()
