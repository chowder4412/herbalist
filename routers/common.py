"""
Common Endpoints: Health Checks, Static Assets, PWA Manifest & Service Worker
"""

import os
import time
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse

router = APIRouter(tags=["Common"])


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

