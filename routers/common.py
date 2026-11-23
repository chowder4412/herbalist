import os
import time
import collections
import threading
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import FileResponse

router = APIRouter(tags=["Common"])


class SlidingWindowRateLimiter:
    """Thread-safe in-memory sliding window rate limiter"""
    def __init__(self):
        self._lock = threading.Lock()
        self._hits = collections.defaultdict(collections.deque)

    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        """Returns True if allowed, False if rate limit exceeded"""
        now = time.time()
        with self._lock:
            q = self._hits[key]
            cutoff = now - window_seconds
            while q and q[0] < cutoff:
                q.popleft()
            if len(q) >= max_requests:
                return False
            q.append(now)
            return True

    def get_client_ip(self, request: Request) -> str:
        """Extract best client IP considering reverse proxy headers"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client and request.client.host:
            return request.client.host
        return "127.0.0.1"

    def enforce(self, request: Request, scope_prefix: str, max_requests: int, window_seconds: int = 60):
        """Enforces rate limit or raises HTTP 429 Too Many Requests"""
        ip = self.get_client_ip(request)
        key = f"{scope_prefix}:{ip}"
        allowed = self.check_rate_limit(key, max_requests=max_requests, window_seconds=window_seconds)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded for {scope_prefix}. Please wait a moment before trying again.",
                headers={"Retry-After": str(window_seconds)}
            )


rate_limiter = SlidingWindowRateLimiter()


@router.get("/health")
@router.get("/api/health")
async def health_check():
    """Health check endpoint for production monitoring"""
    return {
        "status": "healthy",
        "service": "Herbalist AI",
        "version": "2.0.0",
        "timestamp": int(time.time()),
        "uptime": "active"
    }


@router.get("/manifest.json")
async def get_manifest():
    return FileResponse("manifest.json", media_type="application/json")


@router.get("/sw.js")
async def get_service_worker():
    return FileResponse("sw.js", media_type="application/javascript")


@router.get("/favicon.ico", include_in_schema=False)
async def get_favicon():
    svg_favicon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🌿</text></svg>'
    return Response(content=svg_favicon, media_type="image/svg+xml")


@router.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
@router.api_route("/welcome", methods=["GET", "HEAD"], include_in_schema=False)
@router.api_route("/welcome.html", methods=["GET", "HEAD"], include_in_schema=False)
async def serve_welcome():
    welcome_path = os.path.join(os.getcwd(), "welcome.html")
    if os.path.exists(welcome_path):
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        return FileResponse(welcome_path, media_type="text/html", headers=headers)
    # Fallback to index if welcome doesn't exist
    index_path = os.path.join(os.getcwd(), "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Welcome page not found")


@router.api_route("/auth", methods=["GET", "HEAD"], include_in_schema=False)
@router.api_route("/login", methods=["GET", "HEAD"], include_in_schema=False)
@router.api_route("/register", methods=["GET", "HEAD"], include_in_schema=False)
@router.api_route("/auth.html", methods=["GET", "HEAD"], include_in_schema=False)
async def serve_auth():
    auth_path = os.path.join(os.getcwd(), "auth.html")
    if os.path.exists(auth_path):
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        return FileResponse(auth_path, media_type="text/html", headers=headers)
    index_path = os.path.join(os.getcwd(), "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Auth page not found")


@router.api_route("/app", methods=["GET", "HEAD"], include_in_schema=False)
@router.api_route("/consult", methods=["GET", "HEAD"], include_in_schema=False)
@router.api_route("/index.html", methods=["GET", "HEAD"], include_in_schema=False)
async def serve_index():
    index_path = os.path.join(os.getcwd(), "index.html")
    if os.path.exists(index_path):
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        return FileResponse(index_path, media_type="text/html", headers=headers)
    raise HTTPException(status_code=404, detail="Index file not found")


# ══════════════════════════════════════════════════════════════
# 100% FREE STUDIO-GRADE NEURAL VOICE SYNTHESIS ENDPOINT
# ══════════════════════════════════════════════════════════════
NEURAL_VOICE_MAP = {
    "en_ng": "en-NG-EzinneNeural",      # Dr. Aisha (Nigerian English Lead)
    "ha": "en-NG-AbeoNeural",           # Dr. Yusuf (Hausa Physician)
    "yo": "en-NG-AbeoNeural",           # Dr. Adewale (Yoruba Healer)
    "ig": "en-NG-EzinneNeural",         # Dr. Chioma (Igbo Pharmacognosist)
    "sw": "sw-KE-ZuriNeural",           # Dr. Juma (Swahili Dawa Asili)
    "fr": "fr-FR-DeniseNeural",         # Dr. Monique (French Phytotherapy)
    "es": "es-ES-ElviraNeural",         # Dra. Elena (Spanish Fitoterapia)
    "ar": "ar-EG-SalmaNeural",          # Dr. Tariq (Arabic Al-Tibb)
    "zh": "zh-CN-XiaoxiaoNeural",       # Dr. Chen (Chinese TCM Lead)
    "en_gb": "en-GB-SoniaNeural",       # Dr. Oliver (UK Pharmacologist)
    "en_us": "en-US-JennyNeural"        # Dr. Sarah (US Integrative Medicine)
}


@router.get("/api/tts/stream")
@router.post("/api/tts/stream")
async def stream_neural_voice(
    text: str = "",
    voice: str = "en_ng",
    rate: str = "+0%",
    pitch: str = "+0Hz"
):
    """
    100% Free Studio-Quality 24kHz HD Neural Speech Synthesis.
    Provides native Nigerian English, Swahili, French, Spanish, Arabic, Chinese and English accents.
    """
    if not text or len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text parameter cannot be empty")

    target_voice = NEURAL_VOICE_MAP.get(voice.lower(), voice)
    if "-" not in target_voice:
        target_voice = NEURAL_VOICE_MAP.get("en_ng")

    clean_text = text[:2000].replace("*", "").replace("#", "").replace("`", "").replace("<", "").replace(">", "").strip()

    try:
        import edge_tts
        import io
        from fastapi.responses import Response

        communicate = edge_tts.Communicate(clean_text, target_voice, rate=rate, pitch=pitch)
        audio_stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])

        audio_bytes = audio_stream.getvalue()
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=500, detail="No audio bytes generated")

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=dr_herbalist_voice.mp3",
                "Cache-Control": "public, max-age=86400"
            }
        )
    except Exception as e:
        print(f"[Neural Voice Warning] Edge-TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS synthesis error: {str(e)}")


