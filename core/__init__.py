"""
Herbalist AI Core Clinical & Phytotherapy Package
"""

from .models import (
    EmotionalResponse,
    SOCRATESTriage,
    LabBiomarkers,
    PubMedCitation,
    VisionScanResult,
    MedicalProfile,
    HerbalRemedy,
    HerbDrugInteraction,
    NaturalIngredient,
    NaturalFormulation,
    MedicalDiagnosis,
    ResearchDiscovery,
    TeachingModule,
)

from .safety import (
    EmergencyRedFlagChecker,
    PIIScrubber,
    HerbDrugInteractionEngine,
    SpecialPopulationSafetyEngine,
)

from .dosing import DeterministicDosingEngine

from .knowledge_base import (
    RegionalAfricanNameResolver,
    MedicalKnowledgeBase,
    OptometrySpecialist,
    MedicalEducator,
)

from .phytotherapy import PhytotherapySpecialist

from .formulation import NaturalFormulationEngine

from .rag_engine import PubMedRAGEngine, VisionAIScanner

from .ai_engine import GeminiClinicalEngine

from .doctor import AIDoctor, safe_print, demo_ai_medical_doctor

__all__ = [
    # Models
    "EmotionalResponse",
    "SOCRATESTriage",
    "LabBiomarkers",
    "PubMedCitation",
    "VisionScanResult",
    "MedicalProfile",
    "HerbalRemedy",
    "HerbDrugInteraction",
    "NaturalIngredient",
    "NaturalFormulation",
    "MedicalDiagnosis",
    "ResearchDiscovery",
    "TeachingModule",
    # Safety & Dosing
    "EmergencyRedFlagChecker",
    "PIIScrubber",
    "HerbDrugInteractionEngine",
    "SpecialPopulationSafetyEngine",
    "DeterministicDosingEngine",
    # Knowledge & Specialists
    "RegionalAfricanNameResolver",
    "MedicalKnowledgeBase",
    "OptometrySpecialist",
    "MedicalEducator",
    "PhytotherapySpecialist",
    "NaturalFormulationEngine",
    "PubMedRAGEngine",
    "VisionAIScanner",
    # AI & Orchestrator
    "GeminiClinicalEngine",
    "AIDoctor",
    "safe_print",
    "demo_ai_medical_doctor",
]
