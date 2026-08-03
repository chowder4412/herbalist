import unittest
from herbalist import AIDoctor, MedicalProfile, PhytotherapySpecialist, NaturalFormulationEngine

class TestHerbalistCore(unittest.TestCase):
    
    def test_emergency_red_flags_detection(self):
        """Verify that life-threatening symptoms trigger Emergency Red-Flag detection"""
        # Test chest pain
        is_emerg, msg = AIDoctor.check_emergency_red_flags("I am having severe crushing chest pain radiating to left arm")
        self.assertTrue(is_emerg)
        self.assertIn("CRITICAL SAFETY ALERT", msg)
        self.assertIn("911", msg)

        # Test respiratory distress
        is_emerg, msg = AIDoctor.check_emergency_red_flags("I can't breathe and my throat is closing")
        self.assertTrue(is_emerg)
        self.assertIn("CRITICAL SAFETY ALERT", msg)


        # Test non-emergency complaint
        is_emerg, msg = AIDoctor.check_emergency_red_flags("Mild headache and dry throat")
        self.assertFalse(is_emerg)
        self.assertIsNone(msg)

    def test_pii_phi_scrubbing(self):
        """Verify that email addresses, phone numbers, and SSNs are scrubbed for privacy compliance"""
        raw_text = "My name is John Doe, email john.doe@example.com, phone 555-123-4567, SSN 123-45-6789. I have a fever."
        scrubbed = AIDoctor.scrub_pii_phi(raw_text)
        
        self.assertNotIn("john.doe@example.com", scrubbed)
        self.assertNotIn("555-123-4567", scrubbed)
        self.assertNotIn("123-45-6789", scrubbed)
        self.assertIn("[REDACTED_EMAIL]", scrubbed)
        self.assertIn("[REDACTED_PHONE]", scrubbed)
        self.assertIn("[REDACTED_SSN]", scrubbed)

    def test_herb_drug_interaction_safety(self):
        """Verify that high-risk herb-drug interactions (e.g. St. John's Wort + Sertraline) are flagged"""
        specialist = PhytotherapySpecialist()
        proposed_herbs = ["St. John's Wort", "Berberine"]
        medications = ["Sertraline 50mg daily"]
        
        warnings = specialist.check_herb_drug_interactions(proposed_herbs, medications)
        self.assertTrue(len(warnings) > 0)
        
        high_risk_found = any(w.severity == "High" for w in warnings)
        self.assertTrue(high_risk_found)

if __name__ == "__main__":
    unittest.main()
