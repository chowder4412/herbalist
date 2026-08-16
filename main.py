"""
Herbalist AI — Integrative Botanical Medicine Production Server
Main application entry point with lifespan lifecycle management, middleware, and router mounts.
"""

import os
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
from dotenv import load_dotenv

# Import Core Domain Models & Specialists
from core import AIDoctor, MedicalProfile
from clinical_memory import ClinicalMemoryStore

# Import Modular Routers & Re-exports
from routers import (
    register_routers,
    common_router,
    auth_router,
    admin_router,
    analytics_router,
    diagnose_router,
    recovery_vault_router,
    # Auth helpers
    create_jwt_token,
    verify_jwt_token,
    get_auth_token_from_request,
    # Schemas
    RegisterRequest,
    LoginRequest,
    VerifyOtpRequest,
    ResendOtpRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    RagIngestRequest,
    FeatureFlagRequest,
    HerbDrugCheckRequest,
    SyntheticSubstituteRequest,
    PharmacopeiaExploreRequest,
    ConsultationRequest,
    HerbSourcingRequest,
    SymptomTrackerRequest,
    DiagnoseRequest,
    LabUploadRequest,
    VisionScanRequest,
    # Global state & helpers
    GLOBAL_FEATURE_FLAGS,
    ADMIN_RAG_CITATIONS,
    session_manager,
    ClinicalTriageIntelligence,
    IntentClassifier,
    ComplaintClassifier,
    DynamicResponseGenerator,
    SessionStore,
    generate_conversational_doctor_response,
    generate_knowledge_medical_answer
)

load_dotenv()

# Global Doctor & Memory Store
doctor = AIDoctor()
memory_store = ClinicalMemoryStore()


# ══════════════════════════════════════════════════════════════
# Lifespan Initialization
# ══════════════════════════════════════════════════════════════
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed WHO, USDA Dr. Duke's, IMPPAT, ANPDB, TMGL, DentoMed, Arctium, Kew/FRLHT, Authenticity, WHO Hub, Excellence, Phytomedicine, Indigenous, Oncology Systems Bio & Aromatherapy on startup
    try:
        import import_pharmacopeia
        import import_anpdb_database
        import import_tmgl_global_repositories
        import import_dentomed_kampo_database
        import import_arctium_lappa_database
        import import_kew_frlht_envis
        import import_authenticity_adulteration_db
        import import_who_global_compliance_hub
        import import_global_excellence_compendium
        import import_phytomedicine_evidence_synthesis
        import import_indigenous_traditional_knowledge
        import import_indigenous_oncology_systems_bio
        import import_aromatherapy_molecular_phytomedicine
        total_plants = import_pharmacopeia.seed_database()
        anpdb_res = import_anpdb_database.seed_anpdb_database()
        tmgl_count = import_tmgl_global_repositories.seed_tmgl_database()
        kampo_count = import_dentomed_kampo_database.seed_dentomed_database()
        arctium_count = import_arctium_lappa_database.seed_arctium_database()
        kew_frlht_res = import_kew_frlht_envis.seed_kew_frlht_database()
        auth_count = import_authenticity_adulteration_db.seed_authenticity_database()
        who_hub_res = import_who_global_compliance_hub.seed_who_hub_database()
        ex_res = import_global_excellence_compendium.seed_excellence_database()
        phyto_res = import_phytomedicine_evidence_synthesis.seed_phytomedicine_database()
        indig_res = import_indigenous_traditional_knowledge.seed_indigenous_database()
        onc_res = import_indigenous_oncology_systems_bio.seed_indigenous_oncology_database()
        aro_res = import_aromatherapy_molecular_phytomedicine.seed_aromatherapy_database()
        print(f"[Herbalist AI] Successfully loaded {total_plants} monographs, ANPDB ({anpdb_res['species_count']} species), WHO TMGL ({tmgl_count}), DentoMed Kampo ({kampo_count}), Arctium ({arctium_count}), Kew/FRLHT ({kew_frlht_res['kew_mpns']}/{kew_frlht_res['frlht_envis']}), Authenticity ({auth_count}), WHO Hub ({who_hub_res['pharmacopoeias']}), Excellence ({ex_res['usp_hmc']}), Phytomedicine ({phyto_res['medlineplus_imppat']}), Indigenous TKDL ({indig_res['tkdl_formulations']}), Oncology Systems Bio ({onc_res['vietherb']}), & AromaDb ({aro_res['aromadb_oils']}) into active memory!")
    except Exception as e:
        print(f"[Herbalist AI] Pharmacopeia seeder notice: {e}")

    api_key_set = bool(os.getenv("GEMINI_API_KEY"))
    if api_key_set:
        print("[Herbalist AI] Google Gemini 2.0 Flash API Key successfully loaded from .env!")
    else:
        print("[Herbalist AI] Warning: GEMINI_API_KEY not found in .env; checking failover engine...")

    groq_key_set = bool(os.getenv("GROQ_API_KEY"))
    if groq_key_set:
        print("[Herbalist AI] Groq Cloud API Key (Llama 3.3 70B / Llama 3.1 8B) successfully loaded as automatic failover engine!")
    else:
        print("[Herbalist AI] Notice: GROQ_API_KEY not set. Optional: add GROQ_API_KEY to .env for free automatic failover protection.")

    # Initialize Trinity of Adaptive Intelligence Engine (Knowledge, Understanding, Wisdom)
    try:
        from trinity_adaptive_intelligence import trinity_engine
        t_stats = trinity_engine.knowledge.get_knowledge_stats()
        print(f"[Herbalist AI] 🌟 Trinity Adaptive Intelligence Engine initialized (Pillars: Knowledge, Understanding, Wisdom | Active Nodes: {t_stats['total_knowledge_nodes']}).")
    except Exception as te:
        print(f"[Herbalist AI] Trinity Engine init notice: {te}")

    # Start Cloud Container Keep-Alive Heartbeat Task (prevents cold starts)
    async def cloud_keep_alive_worker():
        while True:
            await asyncio.sleep(600)
            try:
                import urllib.request
                port = os.environ.get("PORT", "8000")
                urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=5)
            except Exception:
                pass

    keep_alive_task = asyncio.create_task(cloud_keep_alive_worker())

    yield
    keep_alive_task.cancel()


# ══════════════════════════════════════════════════════════════
# FastAPI Application & Middleware Configuration
# ══════════════════════════════════════════════════════════════
app = FastAPI(
    title="Herbalist AI - Integrative Botanical Medicine API",
    description="Production API for integrative AI diagnosis, SOCRATES symptom triage, and botanical phytotherapy compounding.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration
allowed_origins_raw = os.getenv("CORS_ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in allowed_origins_raw.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip HTTP Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Register All API Routers
register_routers(app)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
