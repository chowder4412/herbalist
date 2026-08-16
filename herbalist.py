"""
Herbalist AI — Integrative Botanical Medicine & Clinical Intelligence Facade
Provides backwards-compatible facade for all core models, specialists, safety engines, and AIDoctor.
"""

from core import (
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
    EmergencyRedFlagChecker,
    PIIScrubber,
    HerbDrugInteractionEngine,
    SpecialPopulationSafetyEngine,
    DeterministicDosingEngine,
    RegionalAfricanNameResolver,
    MedicalKnowledgeBase,
    OptometrySpecialist,
    MedicalEducator,
    PhytotherapySpecialist,
    NaturalFormulationEngine,
    PubMedRAGEngine,
    VisionAIScanner,
    GeminiClinicalEngine,
    AIDoctor,
    safe_print,
    demo_ai_medical_doctor,
    __all__,
)

if __name__ == "__main__":
    demo_ai_medical_doctor()