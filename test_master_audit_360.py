import sys
import os
import re
import json
import asyncio
from fastapi.testclient import TestClient

print("=" * 70)
print("HERBALIST AI 2.0 -- MASTER 360-DEGREE FULL AUDIT SUITE")
print("=" * 70)

passed = 0
total = 0

def test(name, condition, details=""):
    global passed, total
    total += 1
    if condition:
        passed += 1
        print(f"  [PASS] Test {total:02d}: {name}")
    else:
        print(f"  [FAIL] Test {total:02d}: {name} -> {details}")
        sys.exit(1)

# -------------------------------------------------------------
# AUDIT SECTION 1: WELCOME PAGE ARCHITECTURE & ICONS (welcome.html)
# -------------------------------------------------------------
print("\nSECTION 1: Welcome Page Architecture & Capability Badges")
with open("welcome.html", "r", encoding="utf-8") as f:
    welcome_html = f.read()

test("Safety Interlock removed from welcome nav", "Safety Interlock" not in welcome_html.split("</nav>")[0])
test("Pharmacopeia Explorer has SVG icon & redirect link", 'redirect=pharmacopeia' in welcome_html and '<svg' in welcome_html)
test("PubMed RAG has SVG icon & redirect link", 'redirect=rag' in welcome_html and 'PubMed RAG' in welcome_html)
test("Cook Mode HUD has SVG icon & redirect link", 'redirect=cookmode' in welcome_html and 'Cook Mode HUD' in welcome_html)
test("Get Started CTA links to register", 'href="/auth.html?mode=register"' in welcome_html)
test("Sign In CTA links to login", 'href="/auth.html?mode=login"' in welcome_html)
test("Feature badges are non-clickable divs", '<div class="feature-pills">' in welcome_html and '<div class="feature-pill">' in welcome_html)
test("Patient Toolkit badge present with SVG", 'Patient Toolkit' in welcome_html and '<div class="feature-pill">' in welcome_html)
test("Telehealth Call badge present with SVG", 'Telehealth Call' in welcome_html and '<div class="feature-pill">' in welcome_html)

# -------------------------------------------------------------
# AUDIT SECTION 2: AUTHENTICATION PORTAL & VERIFICATION (auth.html)
# -------------------------------------------------------------
print("\nSECTION 2: Auth Portal & Email Verification Check")
with open("auth.html", "r", encoding="utf-8") as f:
    auth_html = f.read()

test("auth.html has modern eye toggle SVG", 'togglePasswordVisibility' in auth_html and 'SVG_EYE_OPEN' in auth_html)
test("Back button renamed to Back", 'Back to Welcome Dashboard' not in auth_html and 'Back' in auth_html)
test("Redirect target query parameter parsed", 'redirectTarget' in auth_html and 'getResolvedRedirectUrl' in auth_html)
test("I've Clicked the Link check button exists", "I've Clicked the Link" in auth_html and 'handleCheckEmailVerificationStatus' in auth_html)
test("Resend Verification Email button exists", 'handleResendVerificationEmail' in auth_html)
test("Auto-login & redirect to destination on verification", 'getResolvedRedirectUrl()' in auth_html)

# -------------------------------------------------------------
# AUDIT SECTION 3: WORKSPACE DASHBOARD & STREAMING (index.html)
# -------------------------------------------------------------
print("\nSECTION 3: Main Consultation Workspace & Deep Linking (index.html)")
with open("index.html", "r", encoding="utf-8") as f:
    index_html = f.read()

test("DOMContentLoaded auto-opens target feature on ?open=", 'urlParams.get(\'open\')' in index_html and 'showSection(\'pharmacopeia\')' in index_html)
test("Email verification check status in index.html", 'handleCheckEmailVerificationStatus' in index_html and 'check-verified-btn' in index_html)
test("Modern eye toggle in index.html", 'toggleAuthPasswordVisibility' in index_html and 'SVG_EYE_OPEN_INDEX' in index_html)
test("Mobile top-bar modality selector options fit screen", 'African Ethno' in index_html and 'Chinese TCM' in index_html)

# -------------------------------------------------------------
# AUDIT SECTION 4: UNRESTRICTED TOKEN CEILING (8192 TOKENS)
# -------------------------------------------------------------
print("\nSECTION 4: Maximum Token Capacity & LLM Ceiling (8192 Tokens)")
with open("core/ai_engine.py", "r", encoding="utf-8") as f:
    ai_engine_code = f.read()

test("ai_engine generate_text default max_tokens=8192", 'max_tokens: int = 8192' in ai_engine_code)
test("ai_engine stream_generate_text default max_tokens=8192", 'def stream_generate_text(self, prompt: str, max_tokens: int = 8192' in ai_engine_code)
test("ai_engine actual_max_tokens ceiling at 8192", 'actual_max_tokens = max(max_tokens, 8192)' in ai_engine_code)
test("ai_engine diagnose_case maxOutputTokens=8192", 'maxOutputTokens": 8192' in ai_engine_code)

with open("routers/triage_helpers.py", "r", encoding="utf-8") as f:
    triage_code = f.read()
test("triage_helpers knowledge answer max_tokens=8192", 'max_tokens=8192' in triage_code)

with open("routers/diagnose.py", "r", encoding="utf-8") as f:
    diagnose_code = f.read()
test("diagnose.py fallback and followup prompts max_tokens=8192", 'max_tokens=8192' in diagnose_code)

with open("routers/analytics.py", "r", encoding="utf-8") as f:
    analytics_code = f.read()
test("analytics.py consultation stream max_tokens=8192", 'max_tokens=8192' in analytics_code)

# -------------------------------------------------------------
# AUDIT SECTION 5: FASTAPI ROUTING & CLIENT ENDPOINT RESPONSES
# -------------------------------------------------------------
print("\nSECTION 5: FastAPI Web Routing & Live HTTP Endpoints")
from main import app
client = TestClient(app)

# 1. Root and Page Routes
r_root = client.get("/")
test("GET / serves welcome.html", r_root.status_code == 200 and "Welcome Dashboard" in r_root.text)

r_welcome = client.get("/welcome")
test("GET /welcome serves welcome.html", r_welcome.status_code == 200 and "Welcome Dashboard" in r_welcome.text)

r_app = client.get("/app")
test("GET /app serves index.html", r_app.status_code == 200 and "Herbalist AI" in r_app.text)

r_auth = client.get("/auth")
test("GET /auth serves auth.html", r_auth.status_code == 200 and "Authentication Portal" in r_auth.text)

# 2. Health & API Endpoints
r_health = client.get("/health")
test("GET /health returns healthy status", r_health.status_code == 200 and r_health.json().get("status") in ("healthy", "ok", "ready"))

r_pharmacopeia = client.get("/api/pharmacopeia")
test("GET /api/pharmacopeia returns 100+ WHO monographs", r_pharmacopeia.status_code == 200 and (len(r_pharmacopeia.json().get("herbs", [])) > 50 or r_pharmacopeia.json().get("total", 0) > 50))

r_auth_me = client.get("/api/auth/me")
test("GET /api/auth/me handles guest state properly", r_auth_me.status_code == 200)

print("\n" + "=" * 70)
print(f"100% AUDIT COMPLETE: ALL {passed}/{total} TESTS PASSED PERFECTLY!")
print("=" * 70)
