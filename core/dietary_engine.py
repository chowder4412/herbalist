"""
Clinical Dietary Intelligence Engine
Translates clinical conditions, body mass, and herbal formulations into evidence-based,
personalized Whole Food Nutrition & Dietary Prescriptions based on WHO 2023 Guidelines.
"""

from typing import Dict, List, Any, Optional
from core.dietary_monographs import DIETARY_MONOGRAPHS, WHO_2023_DIETARY_GUIDELINES


class ClinicalDietaryEngine:
    """
    Integrative Clinical Nutrition Engine.
    Coordinates evidence-based dietary recommendations, food allergy exclusions,
    renal hyperkalemia safety gating, and pharmaceutical/botanical nutrient timing rules.
    """

    def __init__(self):
        self.monographs = DIETARY_MONOGRAPHS
        self.who_guidelines = WHO_2023_DIETARY_GUIDELINES

    def screen_allergies(self, known_allergies: List[str], candidate_foods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Dynamically filters out candidate foods that match patient's known allergies or cross-reactivities.
        """
        if not known_allergies:
            return candidate_foods

        allergies_lower = [a.lower().strip() for a in known_allergies if a]
        safe_foods = []

        # Cross-reactivity mapping
        allergy_cross_reactions = {
            "latex": ["papaya", "banana", "avocado", "chestnut"],
            "melon": ["egusi", "watermelon", "cantaloupe", "cucumber"],
            "allium": ["garlic", "onion", "shallot", "leek", "chive"],
            "legume": ["cowpea", "bean", "peanut", "soybean", "lentil"],
            "gluten": ["wheat", "barley", "rye"]
        }

        for food in candidate_foods:
            food_name = food.get("common_name", "").lower()
            botanical = food.get("botanical_name", "").lower()
            is_allergic = False

            for allergy in allergies_lower:
                if allergy in food_name or allergy in botanical:
                    is_allergic = True
                    break
                # Check cross reactivity
                for allergy_key, reactive_foods in allergy_cross_reactions.items():
                    if allergy_key in allergy:
                        if any(rf in food_name or rf in botanical for rf in reactive_foods):
                            is_allergic = True
                            break

            if not is_allergic:
                safe_foods.append(food)

        return safe_foods

    def apply_renal_hyperkalemia_guardrail(self, is_renal_compromised: bool, recommended_foods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Safety Guardrail: Inverts high-potassium recommendations for Chronic Kidney Disease / Dialysis patients.
        Restricts raw high-potassium juices (coconut water, raw moringa juice, high-potassium bean broths).
        """
        if not is_renal_compromised:
            return {
                "renal_restricted": False,
                "foods": recommended_foods,
                "safety_advisory": None
            }

        # Filter and annotate for CKD
        filtered_foods = []
        restricted_items = []

        for food in recommended_foods:
            nutrients = food.get("key_nutrients", {})
            k_val = nutrients.get("potassium_per_100g", "")
            try:
                k_mg = float(k_val.replace("mg", "").strip())
            except (ValueError, AttributeError):
                k_mg = 0.0

            if k_mg > 400.0 or "cowpea" in food.get("common_name", "").lower():
                restricted_copy = dict(food)
                restricted_copy["renal_modification"] = "Must be boiled in excess water and drained (leached) to reduce potassium by 50% prior to consumption."
                filtered_foods.append(restricted_copy)
                restricted_items.append(food.get("common_name"))
            else:
                filtered_foods.append(food)

        return {
            "renal_restricted": True,
            "foods": filtered_foods,
            "restricted_high_potassium_items": restricted_items,
            "safety_advisory": "⚠️ RENAL SAFETY GUARD: High-potassium foods modified. Restrict unboiled bean broths, coconut water, and raw green juices to prevent hyperkalemia."
        }

    def apply_calcium_iron_separation(self, is_anemic: bool, dietary_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies a 2-hour separation rule between tannin-rich botanical teas / dairy calcium
        and non-heme iron-rich meals (Brown Cowpeas, Sorghum, Moringa).
        """
        if not is_anemic:
            return dietary_plan

        dietary_plan["timing_rule"] = "⏰ CALCIUM-IRON SEPARATION PROTOCOL: Consume iron-dense whole foods (Brown Cowpeas, Sorghum) with Vitamin C (citrus, bell peppers). Separate intake of dairy calcium, black/green tea, or tannin-rich herbs by at least 2 hours to optimize iron absorption."
        return dietary_plan

    def generate_dietary_prescription(
        self,
        condition: str,
        patient_profile: Optional[Dict[str, Any]] = None,
        formulation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates a comprehensive clinical dietary protocol matching the patient's condition,
        body weight, allergies, and herbal prescription.
        """
        patient_profile = patient_profile or {}
        cond_lower = condition.lower() if condition else ""
        known_allergies = patient_profile.get("known_allergies", "")
        if isinstance(known_allergies, str):
            allergies_list = [a.strip() for a in known_allergies.split(",") if a.strip() and a.strip().lower() != "none"]
        else:
            allergies_list = known_allergies or []

        is_renal = any(k in cond_lower for k in ["kidney", "renal", "ckd", "dialysis", "nephro", "egfr"])
        is_anemic = any(k in cond_lower for k in ["anemia", "iron", "fatigue", "hemoglobin", "hgb", "pale"])
        is_diabetic = any(k in cond_lower for k in ["diabetes", "glucose", "glycemic", "insulin", "sugar", "a1c", "metabolic"])
        is_hypertensive = any(k in cond_lower for k in ["hypertension", "blood pressure", "bp", "cardiovascular"])

        # Select candidate foods from monographs
        candidates = list(self.monographs.values())

        # 1. Screen allergies
        safe_foods = self.screen_allergies(allergies_list, candidates)

        # 2. Apply renal hyperkalemia guardrail
        renal_result = self.apply_renal_hyperkalemia_guardrail(is_renal, safe_foods)
        processed_foods = renal_result["foods"]

        # Select top synergistic foods
        synergistic_foods = []
        for food in processed_foods:
            indications = " ".join(food.get("therapeutic_indications", [])).lower()
            if is_diabetic and ("diabetes" in indications or "glycemic" in indications or "insulin" in indications):
                synergistic_foods.append(food)
            elif is_hypertensive and ("hypertension" in indications or "cardiovascular" in indications or "pressure" in indications):
                synergistic_foods.append(food)
            elif is_anemic and ("anemia" in indications or "iron" in indications):
                synergistic_foods.append(food)
            elif any(word in indications for word in cond_lower.split()):
                synergistic_foods.append(food)

        if not synergistic_foods:
            synergistic_foods = processed_foods[:3]

        # Structure synergistic food summaries
        synergistic_summaries = []
        for sf in synergistic_foods[:4]:
            prep = sf.get("culinary_preparation_protocols", ["Cook as whole food"])[0]
            synergistic_summaries.append({
                "food": sf.get("common_name"),
                "botanical": sf.get("botanical_name"),
                "preparation": prep,
                "role": sf.get("who_guideline_category")
            })

        # Foods to strictly avoid
        avoid_items = [
            "Ultra-Processed Foods (NOVA 4): Commercial bouillon seasoning cubes with MSG and trans-fats",
            "Refined white sugar and Non-Sugar Artificial Sweeteners (Aspartame, Sucralose, Saccharin per WHO 2023)",
            "Deep-fried industrial snacks and carbonated high-fructose corn syrup sodas"
        ]
        if is_renal:
            avoid_items.append("Excessive raw high-potassium fluids (unboiled coconut water, raw leafy vegetable smoothies)")
        if is_diabetic:
            avoid_items.append("Refined white wheat flour bread, white rice without fiber pairing, sweetened canned beverages")
        if is_hypertensive:
            avoid_items.append("High-sodium canned preserved foods, salted cured meats, excess table salt (> 5g/day)")

        plan = {
            "title": "Evidence-Based Phytotherapy Dietary Guidance (WHO 2023)",
            "who_fiber_target": ">= 25g naturally occurring dietary fiber daily from whole plant foods",
            "synergistic_foods": synergistic_summaries,
            "foods_to_avoid": avoid_items,
            "heritage_staples": [
                "Brown Cowpeas (Vigna unguiculata) — Soaked 8-12 hrs to degrade phytates, rich in resistant starch & prebiotic fiber.",
                "Heritage Sorghum / Pearl Millet — Gluten-free ancient grains with slow glycemic absorption."
            ],
            "nss_sweetener_advisory": self.who_guidelines["non_sugar_sweeteners_advisory"]["who_guideline_2023"],
            "renal_safety_advisory": renal_result.get("safety_advisory")
        }

        # 3. Apply Calcium-Iron Separation if anemic
        plan = self.apply_calcium_iron_separation(is_anemic, plan)

        return plan
