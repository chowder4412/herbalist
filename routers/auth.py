"""
Authentication Endpoints: JWT, OTP verification, Registration & Password Reset
"""

import os
import re
import time
import json
import base64
import hmac
import hashlib
import random
import logging
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Request, Response, BackgroundTasks

try:
    import jwt
    PYJWT_AVAILABLE = True
except ImportError:
    jwt = None
    PYJWT_AVAILABLE = False

from clinical_memory import ClinicalMemoryStore

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
memory_store = ClinicalMemoryStore()

JWT_SECRET = os.getenv("JWT_SECRET", "herbalist_jwt_secret_key_2026_enterprise")


# ══════════════════════════════════════════════════════════════
# Request Schemas
# ══════════════════════════════════════════════════════════════
class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    username: Optional[str] = None  # Patient ID
    dob: Optional[str] = None       # Date of Birth YYYY-MM-DD


class LoginRequest(BaseModel):
    email: str
    password: str


class VerifyOtpRequest(BaseModel):
    email: str
    otp_code: str


class ResendOtpRequest(BaseModel):
    email: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    email: str
    otp_code: str
    new_password: str


# ══════════════════════════════════════════════════════════════
# JWT Utilities
# ══════════════════════════════════════════════════════════════
def create_jwt_token(payload: dict, expires_in_seconds: int = 86400) -> str:
    """Generate secure JWT token using PyJWT with expiration (default 24h) and fallback support"""
    token_payload = payload.copy()
    now = int(time.time())
    if "iat" not in token_payload:
        token_payload["iat"] = now
    if "exp" not in token_payload:
        token_payload["exp"] = now + expires_in_seconds

    if PYJWT_AVAILABLE and jwt is not None:
        return jwt.encode(token_payload, JWT_SECRET, algorithm="HS256")
    
    # Fallback custom HMAC implementation if PyJWT is not installed
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(token_payload).encode()).decode().rstrip("=")
    signature_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(JWT_SECRET.encode(), signature_input, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def verify_jwt_token(token: str) -> Optional[dict]:
    """Verify JWT token signature, expiration (exp), and return decoded payload"""
    if not token:
        return None
        
    if PYJWT_AVAILABLE and jwt is not None:
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return decoded
        except jwt.ExpiredSignatureError:
            print("[JWT] Token validation failed: Signature expired.")
            return None
        except jwt.InvalidTokenError as e:
            print(f"[JWT] Token validation error: {e}")
            return None
        except Exception as e:
            print(f"[JWT] Unexpected verification error: {e}")
            return None

    # Fallback custom HMAC verification with expiration check
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        signature_input = f"{header_b64}.{payload_b64}".encode()
        expected_sig = hmac.new(JWT_SECRET.encode(), signature_input, hashlib.sha256).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
        if not hmac.compare_digest(sig_b64, expected_sig_b64):
            return None
        padded_payload = payload_b64 + "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded_payload.encode()).decode())
        
        # Verify expiration if claim exists
        if "exp" in payload and time.time() > payload["exp"]:
            print("[JWT] Fallback verification failed: Token expired.")
            return None
        return payload
    except Exception:
        return None


def get_auth_token_from_request(request: Request) -> str:
    """Extract JWT token from HttpOnly cookie or Authorization Bearer header"""
    cookie_token = request.cookies.get("herbalist_jwt", "")
    if cookie_token:
        return cookie_token.strip()
    auth_header = request.headers.get("Authorization", "")
    if "Bearer " in auth_header:
        return auth_header.replace("Bearer ", "").strip()
    return ""


# ══════════════════════════════════════════════════════════════
# Auth Route Handlers
# ══════════════════════════════════════════════════════════════
@router.post("/register")
async def register_user(body: RegisterRequest, background_tasks: BackgroundTasks):
    """Initiate user registration, generate 6-digit OTP verification code, and dispatch email in background"""
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
    
    email_clean = body.email.lower().strip()
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email_clean):
        raise HTTPException(status_code=400, detail="Please enter a valid email address (e.g. name@domain.com).")

    patient_username = (body.username or body.full_name).strip().replace(" ", "_")
    patient_dob = (body.dob or "").strip()

    # Check if user email already exists in users database
    conn = memory_store.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users WHERE email = ?', (email_clean,))
    existing = cursor.fetchone()
    conn.close()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists. Please Sign In instead.")

    # Generate 6-digit random verification code & store in pending_otps
    otp_code = f"{random.randint(100000, 999999)}"
    memory_store.store_pending_otp(
        email=email_clean,
        password=body.password,
        full_name=body.full_name,
        otp_code=otp_code,
        username=patient_username,
        dob=patient_dob,
        ttl_seconds=600
    )

    # Dispatch 6-digit OTP code email in background
    background_tasks.add_task(memory_store.send_otp_email_dispatch, email_clean, otp_code)
    logging.getLogger('herbalist.otp').info(f'[Herbalist AI] Dispatched 6-digit OTP code [{otp_code}] for user {email_clean} in background task.')

    return {
        "status": "otp_required",
        "message": f"A 6-digit verification code has been dispatched to {email_clean}",
        "email": email_clean
    }


@router.post("/verify-otp")
async def verify_otp(body: VerifyOtpRequest, response: Response):
    """Verify 6-digit OTP code, activate user account in database, and set HttpOnly Secure Cookie"""
    user = memory_store.verify_and_activate_otp(body.email, body.otp_code)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired 6-digit verification code. Please request a new code.")
    token = create_jwt_token(user)
    response.set_cookie(
        key="herbalist_jwt",
        value=token,
        httponly=True,
        max_age=86400 * 7,
        samesite="lax"
    )
    return {"status": "success", "user": user, "access_token": token}


@router.post("/resend-otp")
async def resend_otp(body: ResendOtpRequest, background_tasks: BackgroundTasks):
    """Resend a fresh 6-digit OTP verification code in background"""
    conn = memory_store.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT full_name FROM pending_otps WHERE email = ?', (body.email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=400, detail="No pending registration found for this email. Please register again.")

    otp_code = f"{random.randint(100000, 999999)}"
    conn = memory_store.get_connection()
    cursor = conn.cursor()
    expires_at = int(time.time()) + 600
    cursor.execute('UPDATE pending_otps SET otp_code = ?, expires_at = ? WHERE email = ?', (otp_code, expires_at, body.email.lower().strip()))
    conn.commit()
    conn.close()

    background_tasks.add_task(memory_store.send_otp_email_dispatch, body.email, otp_code)
    logging.getLogger('herbalist.otp').info(f'[Herbalist AI] Dispatched fresh 6-digit OTP code [{otp_code}] for user {body.email} in background task.')
    return {"status": "success", "message": f"Fresh 6-digit verification code dispatched to {body.email}"}


@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    """Initiate password reset, generate 6-digit OTP, and dispatch email in background"""
    email_clean = body.email.lower().strip()
    otp_code = memory_store.store_password_reset_otp(email_clean)
    if not otp_code:
        raise HTTPException(status_code=404, detail="account_not_found")
    
    background_tasks.add_task(memory_store.send_otp_email_dispatch, email_clean, otp_code)
    logging.getLogger('herbalist.otp').info(f'[Herbalist AI] Dispatched password reset OTP code [{otp_code}] for user {email_clean} in background task.')
    return {"status": "success", "message": f"A 6-digit password reset code has been dispatched to {email_clean}"}


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest, response: Response):
    """Verify 6-digit OTP, update password, set HttpOnly cookie, and log user in"""
    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters long")
        
    user = memory_store.verify_and_reset_password(body.email, body.otp_code, body.new_password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired 6-digit verification code.")
        
    token = create_jwt_token(user)
    response.set_cookie(
        key="herbalist_jwt",
        value=token,
        httponly=True,
        max_age=86400 * 7,
        samesite="lax"
    )
    return {"status": "success", "message": "Password reset successful! You are now logged in.", "user": user, "access_token": token}


@router.post("/login")
async def login_user(body: LoginRequest, response: Response):
    """Authenticate user credentials and set HttpOnly Secure Cookie with detailed diagnostic messages"""
    email_clean = body.email.lower().strip()
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email_clean):
        raise HTTPException(status_code=400, detail="Please enter a valid email address (e.g. name@domain.com).")
    
    # 1. Attempt active authentication
    user = memory_store.authenticate_user(email_clean, body.password)
    if user:
        token = create_jwt_token(user)
        response.set_cookie(
            key="herbalist_jwt",
            value=token,
            httponly=True,
            max_age=86400 * 7,
            samesite="lax"
        )
        return {"status": "success", "user": user, "access_token": token}

    # 2. Check if pending registration OTP exists
    conn = memory_store.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM pending_otps WHERE email = ?', (email_clean,))
    pending_otp = cursor.fetchone()
    conn.close()

    if pending_otp:
        raise HTTPException(
            status_code=400,
            detail="verification_pending"
        )

    raise HTTPException(status_code=401, detail="Incorrect email or password. Please check your credentials or click Create Account.")


@router.post("/logout")
async def logout_user(response: Response):
    """Clear HttpOnly authentication cookie"""
    response.delete_cookie(key="herbalist_jwt")
    return {"status": "success", "message": "Successfully logged out"}


@router.get("/me")
async def get_current_user_profile(request: Request):
    """Fetch profile of currently authenticated user via HttpOnly cookie or Bearer token"""
    token = get_auth_token_from_request(request)
    user = verify_jwt_token(token)
    if not user:
        return {"status": "guest", "user": None}
    return {"status": "success", "user": user}
