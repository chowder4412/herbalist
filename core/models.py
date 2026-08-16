"""
Models, Enums, and Dataclasses for Herbalist AI
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class EmotionalResponse(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    DECIDER = "decider"


@dataclass
class SOCRATESTriage:
    """Standardized SOCRATES Medical Symptom Assessment Protocol"""
    site_location: str  # e.g., "Abdomen", "Chest", "Joints", "General Systemic"
    onset_speed: str  # "Sudden acute", "Gradual progressive", "Chronic intermittent"
    character_pain: str  # "Sharp", "Dull ache", "Burning", "Throbbing", "Tightness"
    radiation: str  # "Radiates to back", "Radiates to arm", "Localized"
    associations: List[str]  # e.g., ["Nausea", "Fever", "Fatigue", "Dizziness"]
    time_course: str  # "Worse in morning", "Constant", "After meals", "Nighttime"
    exacerbating_relieving: str  # "Relieved by rest", "Worse with exercise", "Worse after food"
    severity_score_1_to_10: int  # 1 to 10 scale


@dataclass
class LabBiomarkers:
    """Patient Lab Test Biomarkers & Telemetry Profile"""
    weight_kg: float = 70.0
    fasting_glucose_mg_dl: Optional[float] = None
    hba1c_percentage: Optional[float] = None
    alt_liver_enzyme_u_l: Optional[float] = None
    ast_liver_enzyme_u_l: Optional[float] = None
    bp_systolic: Optional[float] = None
    bp_diastolic: Optional[float] = None


@dataclass
class PubMedCitation:
    """Peer-reviewed medical journal & WHO pharmacopeia citation with DOI/PMID"""
    title: str
    journal: str
    doi: str
    pmid: str
    evidence_level: str
    key_findings: str


@dataclass
class VisionScanResult:
    """Multimodal Vision AI Scanner result for plant verification or visual symptoms"""
    scan_type: str
    detected_item: str
    authenticity_confidence: float
    freshness_grade: str
    safety_notes: List[str]


@dataclass
class MedicalProfile:
    """Complete patient medical profile and history with SOCRATES triage & body weight"""
    patient_id: str
    age: int
    gender: str
    medical_history: List[str]
    current_symptoms: List[str]
    medications: List[str]
    allergies: List[str]
    lifestyle_factors: Dict[str, Any]
    family_history: List[str]
    vital_signs: Dict[str, float]
    lab_results: Dict[str, Any]
    imaging_results: List[str]
    risk_factors: List[str]
    previous_diagnoses: List[str]
    weight_kg: float = 70.0
    socrates_triage: Optional[SOCRATESTriage] = None
    lab_biomarkers: Optional[LabBiomarkers] = None


@dataclass
class HerbalRemedy:
    """Evidence-based botanical remedy and phytotherapy profile"""
    common_name: str
    botanical_name: str
    active_compounds: List[str]
    therapeutic_actions: List[str]
    clinical_indications: List[str]
    recommended_dosage: str
    safety_warnings: List[str]


@dataclass
class HerbDrugInteraction:
    """Safety evaluation of interaction between herbal remedies and conventional pharmaceuticals"""
    herb_name: str
    drug_class_or_name: str
    severity: str  # "High", "Moderate", "Mild"
    mechanism: str
    clinical_recommendation: str


@dataclass
class NaturalIngredient:
    """Medicinal plant, herb, fruit, spice, bark, or natural extract profile"""
    common_name: str
    botanical_name: str
    category: str  # "Medicinal Herb/Plant", "Medicinal Fruit", "Spice/Bark/Resin", "Extract Base/Carrier"
    part_used: str  # "Leaf", "Rhizome/Root", "Fruit Pulp/Juice", "Bark", "Peel", "Seed", "Extract"
    active_bioactives: List[str]
    therapeutic_properties: List[str]
    potency_rating_per_gram: float  # Bioactive potency rating (mg per gram)
    clinical_indications: List[str]
    safety_cautions: List[str]
    layman_nutrient_name: str = ""
    common_food_sources: List[str] = None
    household_measurement: str = ""


@dataclass
class NaturalFormulation:
    """Compounded multi-ingredient botanical remedy with medicine concentration math, layman kitchen recipes, and dynamic body requirement calculations"""
    formulation_id: str
    formulation_name: str
    target_condition: str
    ingredients: List[Dict[str, Any]]
    preparation_method: str
    total_volume_ml: float
    total_active_bioactives_mg: float
    concentration_mg_per_ml: float
    concentration_percentage_wv: float
    dosage_volume_ml: float
    dosing_frequency: str
    treatment_duration: str
    preparation_recipe_steps: List[str]
    storage_and_safety: List[str]
    layman_explanation: str = ""
    household_kitchen_recipe: List[str] = None
    household_dose_schedule: str = ""
    body_requirement_summary: str = ""
    bioactive_match_score: float = 0.0


@dataclass
class MedicalDiagnosis:
    """AI-generated medical diagnosis with confidence scoring, RAG PubMed citations & Body Weight Dosing Math"""
    primary_diagnosis: str
    differential_diagnoses: List[str]
    confidence_score: float
    supporting_evidence: List[str]
    recommended_tests: List[str]
    treatment_plan: List[str]
    prognosis: str
    red_flags: List[str]
    follow_up_timeline: str
    specialist_referral: Optional[str]
    herbal_recommendations: List[str] = None
    herb_drug_safety_warnings: List[str] = None
    natural_formulation: Optional[NaturalFormulation] = None
    prescription_card: Optional[str] = None
    pubmed_citations: List[PubMedCitation] = None
    vision_scan_result: Optional[VisionScanResult] = None
    weight_adjusted_dosing_summary: str = ""


@dataclass
class ResearchDiscovery:
    """Medical research discovery or breakthrough"""
    discovery_id: str
    research_area: str
    hypothesis: str
    findings: str
    significance_level: float
    clinical_implications: List[str]
    further_research_needed: List[str]
    potential_applications: List[str]
    publication_potential: str
    breakthrough_score: float


@dataclass
class TeachingModule:
    """Medical education and training module"""
    module_id: str
    specialty: str
    difficulty_level: int  # 1-10
    learning_objectives: List[str]
    content_outline: List[str]
    practical_exercises: List[str]
    assessment_criteria: List[str]
    prerequisite_knowledge: List[str]
    estimated_duration: str
