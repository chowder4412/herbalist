"""
Routers Package for Herbalist AI
Exposes all sub-routers and register_routers helper for FastAPI.
"""

from fastapi import FastAPI

from .common import router as common_router
from .auth import (
    router as auth_router,
    create_jwt_token,
    verify_jwt_token,
    get_auth_token_from_request,
    RegisterRequest,
    LoginRequest,
    VerifyOtpRequest,
    ResendOtpRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest
)
from .admin import (
    router as admin_router,
    GLOBAL_FEATURE_FLAGS,
    ADMIN_RAG_CITATIONS,
    RagIngestRequest,
    FeatureFlagRequest
)
from .analytics import (
    router as analytics_router,
    HerbDrugCheckRequest,
    SyntheticSubstituteRequest,
    PharmacopeiaExploreRequest,
    ConsultationRequest,
    HerbSourcingRequest,
    SymptomTrackerRequest
)
from .diagnose import (
    router as diagnose_router,
    DiagnoseRequest,
    LabUploadRequest,
    VisionScanRequest,
    session_manager
)
from .recovery_vault import router as recovery_vault_router
from .triage_helpers import (
    ClinicalTriageIntelligence,
    IntentClassifier,
    ComplaintClassifier,
    DynamicResponseGenerator,
    SessionStore,
    generate_conversational_doctor_response,
    generate_knowledge_medical_answer
)

def register_routers(app: FastAPI):
    """Mount all API routers onto the FastAPI application"""
    app.include_router(common_router)
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(analytics_router)
    app.include_router(diagnose_router)
    app.include_router(recovery_vault_router)


__all__ = [
    "common_router",
    "auth_router",
    "admin_router",
    "analytics_router",
    "diagnose_router",
    "recovery_vault_router",
    "register_routers",
    # Auth helpers
    "create_jwt_token",
    "verify_jwt_token",
    "get_auth_token_from_request",
    # Models
    "RegisterRequest",
    "LoginRequest",
    "VerifyOtpRequest",
    "ResendOtpRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "RagIngestRequest",
    "FeatureFlagRequest",
    "HerbDrugCheckRequest",
    "SyntheticSubstituteRequest",
    "PharmacopeiaExploreRequest",
    "ConsultationRequest",
    "HerbSourcingRequest",
    "SymptomTrackerRequest",
    "DiagnoseRequest",
    "LabUploadRequest",
    "VisionScanRequest",
    # Global state & helpers
    "GLOBAL_FEATURE_FLAGS",
    "ADMIN_RAG_CITATIONS",
    "session_manager",
    "ClinicalTriageIntelligence",
    "IntentClassifier",
    "ComplaintClassifier",
    "DynamicResponseGenerator",
    "SessionStore",
    "generate_conversational_doctor_response",
    "generate_knowledge_medical_answer"
]
