"""
Deterministic Dosing Engine and Clark's Body-Mass Scaler
"""

from typing import Dict, Any


class DeterministicDosingEngine:
    """
    Deterministic Clinical Dosage & Decoction Calculator.
    Uses Clark's Body-Mass Scaling Rule to calculate exact daily milligram targets,
    water volume, steeping duration, and teacup schedule deterministically.
    """

    @classmethod
    def calculate_dosage(cls, weight_kg: float = 70.0, age: int = 35, severity: int = 5) -> Dict[str, Any]:
        """
        Calculates exact dose scaling based on Clark's Rule:
        Dose_patient = Dose_adult * (Weight_kg / 70)
        """
        clamped_weight = max(10.0, min(150.0, float(weight_kg)))
        clamped_age = max(1, min(100, int(age)))
        clamped_sev = max(1, min(10, int(severity)))

        # Base adult reference weight is 70kg
        scale_factor = clamped_weight / 70.0

        # Adjust for severity (scale factor between 0.8x and 1.3x)
        severity_multiplier = 0.8 + (clamped_sev * 0.05)
        adjusted_factor = scale_factor * severity_multiplier

        # Standard daily bioactive target (reference: 300mg adult baseline)
        daily_bioactive_mg = round(300.0 * adjusted_factor, 1)

        # Fluid volume & Decoction pots math (Dynamically scales 1L, 2L, 3L, 4L based on body mass & severity)
        if clamped_weight < 30:
            water_volume_liters = 1.0
            teacup_volume_ml = 75
        elif clamped_weight < 85 and clamped_sev < 8:
            water_volume_liters = 2.0
            teacup_volume_ml = 150
        elif clamped_weight < 110 or clamped_sev >= 8:
            water_volume_liters = 3.0
            teacup_volume_ml = 200
        else:
            water_volume_liters = 4.0
            teacup_volume_ml = 250

        # Dosing frequency based on severity
        if clamped_sev >= 8:
            frequency_text = "4 times daily (after meals & before sleep)"
            times_per_day = 4
        elif clamped_sev >= 5:
            frequency_text = "3 times daily (morning, afternoon, evening after meals)"
            times_per_day = 3
        else:
            frequency_text = "2 times daily (morning & evening after meals)"
            times_per_day = 2

        per_dose_mg = round(daily_bioactive_mg / times_per_day, 1)

        # Steeping/Boiling duration (Roots/Bark = boiling 30 min; Leaves = steep 15 min)
        pot_simmer_minutes = 30 if clamped_weight >= 40 else 20

        return {
            "clamped_weight_kg": clamped_weight,
            "clamped_age": clamped_age,
            "scale_factor": round(scale_factor, 2),
            "daily_bioactive_need_mg": daily_bioactive_mg,
            "per_dose_mg": per_dose_mg,
            "water_volume_liters": water_volume_liters,
            "teacup_volume_ml": teacup_volume_ml,
            "times_per_day": times_per_day,
            "dosing_schedule": f"{teacup_volume_ml} mL (1 teacup) warm, {frequency_text} [~{per_dose_mg} mg bioactives per dose]",
            "pot_recipe_instructions": (
                f"STEP 1: Measure {water_volume_liters} Liters of clean drinking water into a standard cooking pot.\n"
                f"STEP 2: Wash fresh botanical leaves/roots thoroughly under clean water.\n"
                f"STEP 3: Place ingredients into the pot, bring to a rolling boil, then reduce heat and simmer covered for {pot_simmer_minutes} minutes.\n"
                f"STEP 4: Strain out plant solids. Allow liquid to cool to warm temperature.\n"
                f"STEP 5: Drink {teacup_volume_ml} mL {frequency_text}. Refrigerate remaining liquid for up to 48 hours."
            )
        }
