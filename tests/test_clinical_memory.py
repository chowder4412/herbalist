import unittest
import os
from clinical_memory import ClinicalMemoryStore

class TestClinicalMemory(unittest.TestCase):
    
    def setUp(self):
        self.test_db = "test_clinical_memory.db"
        try:
            if os.path.exists(self.test_db):
                os.remove(self.test_db)
        except Exception:
            pass
        self.store = ClinicalMemoryStore(db_path=self.test_db)

    def tearDown(self):
        try:
            if os.path.exists(self.test_db):
                os.remove(self.test_db)
        except Exception:
            pass


    def test_seed_pharmacopeia(self):
        """Verify that pharmacopeia seeds 100+ plants on initialization"""
        inserted = self.store.seed_pharmacopeia_100()
        self.assertGreaterEqual(inserted, 100)
        
        stats = self.store.get_memory_stats()
        self.assertGreaterEqual(stats["semantic_learned_ingredients"], 100)

    def test_record_and_query_episodic_case(self):
        """Verify recording an episodic patient consultation and querying similar cases"""
        self.store.seed_pharmacopeia_100()
        
        case_id = self.store.record_episodic_case(
            symptoms="Persistent headaches, high blood pressure",
            diagnosis_result="Hypertension & Tension Headache",
            prescribed_formulation="Hibiscus & Moringa Synergy",
            bioactive_match_score=98.5
        )
        self.assertTrue(case_id.startswith("CASE_"))
        
        matches = self.store.lookup_herbs_for_condition(["pain", "antihypertensive"])
        self.assertGreater(len(matches), 0)

if __name__ == "__main__":
    unittest.main()
