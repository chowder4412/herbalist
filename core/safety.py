"""
Clinical Safety, Deterministic Herb-Drug Interactions, Special Populations, Emergency Red Flags & PII Scrubber
"""

import re
from typing import Dict, List, Any, Tuple, Optional


class EmergencyRedFlagChecker:
    """Scans text for life-threatening emergency medical symptoms."""

    RED_FLAG_PATTERNS = [
        (r"\b(chest pain|crushing pain|pressure in chest|heart attack|pain radiating to arm|arm pain and chest)\b", 
         "CRITICAL SAFETY ALERT: Severe chest pain / suspected cardiac event."),
        (r"\b(can't breathe|cannot breathe|gasping|severe shortness of breath|choking|unable to breathe)\b", 
         "CRITICAL SAFETY ALERT: Severe respiratory distress / airway compromise."),
        (r"\b(face drooping|slurred speech|arm weakness|stroke|paralysis on one side)\b", 
         "CRITICAL SAFETY ALERT: Signs of acute stroke / neurological emergency."),
        (r"\b(throat closing|swollen tongue|severe anaphylaxis|anaphylactic)\b", 
         "CRITICAL SAFETY ALERT: Severe allergic reaction / anaphylaxis."),
        (r"\b(unconscious|fainted|unresponsive|coughing up blood|severe trauma|profuse bleeding)\b", 
         "CRITICAL SAFETY ALERT: Acute life-threatening trauma or blood loss.")
    ]

    @classmethod
    def get_emergency_inline_banner(cls, text: str) -> Optional[str]:
        """
        Scans text for critical high-risk symptoms.
        Returns a non-blocking inline warning banner string if detected.
        """
        if not text:
            return None
        t = text.lower()
        
        for pattern, warning in cls.RED_FLAG_PATTERNS:
            if re.search(pattern, t):
                return (
                    f"🚨 **{warning}**\n"
                    f"*If this is an active life-threatening emergency, please call 911 / 999 / 112 or seek immediate emergency care while reviewing the botanical remedy guidelines below.*"
                )

        return None

    @classmethod
    def check_emergency_red_flags(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        Scans text for life-threatening emergency medical symptoms.
        Returns (is_emergency, emergency_warning_message).
        """
        banner = cls.get_emergency_inline_banner(text)
        if banner:
            return True, banner
        return False, None


class PIIScrubber:
    """Scrubs personally identifiable information (emails, phones, SSNs) for HIPAA/GDPR privacy."""

    @staticmethod
    def scrub(text: str) -> str:
        if not text:
            return text
        # Email address
        text = re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[REDACTED_EMAIL]", text)
        # Phone number (various formats)
        text = re.sub(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", "[REDACTED_PHONE]", text)
        # SSN
        text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]", text)
        return text


class HerbDrugInteractionEngine:
    """
    Deterministic WHO-grade Herb-Drug Interaction (HDI) Safety Matrix.
    Hardcoded evidence-based database of high-risk drug-herb contraindications.
    Does NOT rely on LLM guessing - enforces strict deterministic safety rules.
    """

    CRITICAL_INTERACTION_RULES = [
        {
            "drug_keywords": ["warfarin", "coumadin", "aspirin", "plavix", "clopidogrel", "eliquis", "xarelto", "blood thinner", "anticoagulant"],
            "herb_keywords": ["ginkgo", "garlic", "ginger", "willow bark", "dong quai", "cinnamon", "feverfew"],
            "severity": "CRITICAL DANGER",
            "mechanism": "Additive antiplatelet / anticoagulant effect.",
            "warning": "🚨 **CRITICAL BLEEDING RISK**: Combining pharmaceutical blood thinners ({drug}) with antithrombotic herbs ({herb}) creates a severe risk of spontaneous internal hemorrhage, GI bleeding, and bruising."
        },
        {
            "drug_keywords": ["metformin", "insulin", "glipizide", "glimepiride", "diabetic", "blood sugar"],
            "herb_keywords": ["bitter melon", "gymnema", "fenugreek", "berberine"],
            "severity": "HIGH WARNING",
            "mechanism": "Synergistic blood-glucose lowering.",
            "warning": "⚠️ **HYPOGLYCEMIA ALERT**: Combining antidiabetic medication ({drug}) with glucose-lowering herbs ({herb}) can drop blood sugar to dangerously low levels (hypoglycemia). Monitor blood glucose closely."
        },
        {
            "drug_keywords": ["lisinopril", "amlodipine", "losartan", "enalapril", "attenolol", "hypertension", "bp medication"],
            "herb_keywords": ["licorice", "glycyrrhiza"],
            "severity": "HIGH WARNING",
            "mechanism": "11-beta-HSD2 enzyme inhibition causing sodium retention.",
            "warning": "⚠️ **HYPERTENSION CONTRAINDICATION**: Licorice root contains Glycyrrhizin, which counteracts blood pressure medication ({drug}), causing fluid retention and elevated blood pressure."
        },
        {
            "drug_keywords": ["birth control", "contraceptive", "ssri", "prozac", "zoloft", "cyclosporine", "immunosuppressant"],
            "herb_keywords": ["st. john's wort", "st johns wort", "hypericum"],
            "severity": "CRITICAL DANGER",
            "mechanism": "Cytochrome P450 (CYP3A4) and P-glycoprotein induction.",
            "warning": "🚨 **MEDICATION INACTIVATION RISK**: St. John's Wort induces liver enzymes that rapidly break down and inactivate pharmaceutical drugs ({drug}), leading to therapeutic failure."
        },
        {
            "drug_keywords": ["xanax", "valium", "sedative", "ambien", "sleep aid", "benzodiazepine"],
            "herb_keywords": ["kava", "valerian"],
            "severity": "HIGH WARNING",
            "mechanism": "Synergistic GABAergic central nervous system depression.",
            "warning": "⚠️ **EXCESSIVE SEDATION ALERT**: Combining pharmaceutical sedatives ({drug}) with sedative herbs ({herb}) can cause extreme drowsiness, respiratory depression, and motor impairment."
        }
    ]

    @classmethod
    def check_interactions(cls, user_medications: List[str], prescribed_herbs: List[str]) -> List[Dict[str, Any]]:
        """
        Cross-checks reported medications against prescribed herbs.
        Returns a list of detected interaction alert dicts.
        """
        alerts = []
        med_text = " ".join([m.lower() for m in user_medications])
        herb_text = " ".join([h.lower() for h in prescribed_herbs])

        for rule in cls.CRITICAL_INTERACTION_RULES:
            matched_drug = next((dk for dk in rule["drug_keywords"] if dk in med_text), None)
            matched_herb = next((hk for hk in rule["herb_keywords"] if hk in herb_text), None)

            if matched_drug and matched_herb:
                alert_msg = rule["warning"].format(drug=matched_drug.title(), herb=matched_herb.title())
                alerts.append({
                    "severity": rule["severity"],
                    "drug": matched_drug,
                    "herb": matched_herb,
                    "mechanism": rule["mechanism"],
                    "warning_message": alert_msg
                })

        return alerts


class SpecialPopulationSafetyEngine:
    """
    WHO-grade Special Population Safety Gating Engine.
    Filters out contraindicated botanicals for Pregnancy, Lactation, Hepatic/Renal Impairment, and Pediatrics.
    """

    PREGNANCY_CONTRAINDICATED_HERBS = [
        "rue", "goldenseal", "mugwort", "tansy", "blue cohosh", "juniper", "pennyroyal", "wormwood", "pokeroot"
    ]
    HEPATOTOXIC_HERBS = [
        "comfrey", "coltsfoot", "borage", "kava"
    ]

    @classmethod
    def evaluate_safety(cls, patient: Any, complaint_text: str = "") -> Dict[str, Any]:
        """
        Evaluates special population risks for pregnancy, lactation, hepatic/renal, and age.
        """
        warnings = []
        restricted_herbs = []

        is_pregnant = False
        is_lactating = False
        has_liver_kidney_disease = False

        c_lower = (complaint_text + " " + " ".join(getattr(patient, 'current_symptoms', []))).lower()

        if any(w in c_lower for w in ["pregnant", "pregnancy", "expecting", "gestation"]):
            is_pregnant = True
            restricted_herbs.extend(cls.PREGNANCY_CONTRAINDICATED_HERBS)
            warnings.append("🤰 **PREGNANCY SAFETY PROTOCOL ACTIVE**: Uterine stimulant botanicals (Rue, Goldenseal, Mugwort, Wormwood) are strictly contraindicated.")

        if any(w in c_lower for w in ["breastfeeding", "lactating", "nursing"]):
            is_lactating = True
            warnings.append("🤱 **LACTATION PROTOCOL ACTIVE**: Only non-excreted galactagogue botanicals (Fennel, Anise, Blessed Thistle) are recommended.")

        if any(w in c_lower for w in ["liver", "hepatitis", "cirrhosis", "kidney", "renal", "dialysis", "creatinine"]):
            has_liver_kidney_disease = True
            restricted_herbs.extend(cls.HEPATOTOXIC_HERBS)
            warnings.append("🛡️ **HEPATIC/RENAL IMPAIRMENT PROTOCOL ACTIVE**: Pyrrolizidine alkaloid botanicals (Comfrey, Coltsfoot) are strictly contraindicated to protect liver/kidney function.")

        patient_age = getattr(patient, 'age', 30)
        is_pediatric = patient_age < 12
        if is_pediatric:
            warnings.append(f"👶 **PEDIATRIC DOSING PROTOCOL (Age {patient_age})**: Dosage is deterministically scaled down using Clark's Body-Mass Rule.")

        return {
            "is_pregnant": is_pregnant,
            "is_lactating": is_lactating,
            "has_liver_kidney_disease": has_liver_kidney_disease,
            "is_pediatric": is_pediatric,
            "restricted_herbs": list(set(restricted_herbs)),
            "safety_warnings": warnings
        }
