#!/usr/bin/env python3
"""
🌿 Herbalist AI — Unified Application Launcher & Engine Manager
Usage:
    python run.py                     (Default: FastAPI engine on port 8000)
    python run.py --engine native      (Native Python standard library HTTP server)
    python run.py --engine node        (Node.js static HTTP server)
    python run.py --port 8080          (Custom port)
"""

import sys
import os
import argparse
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(
        description="🌿 Herbalist AI Unified Server Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Engine Modes:
  fastapi  : Production FastAPI server with Upstash Redis, JWT auth & RAG endpoints (main.py)
  native   : Zero-dependency Python standard library HTTP server (app.py)
  node     : Node.js static HTTP server (server.js)
"""
    )
    parser.add_argument(
        "--engine", "-e",
        choices=["fastapi", "native", "node"],
        default="fastapi",
        help="Server engine to execute (default: fastapi)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8000,
        help="Port number to bind (default: 8000)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind (default: 127.0.0.1)"
    )

    args = parser.parse_args()

    print("=" * 64)
    print(" 🌿 Herbalist AI — Integrative Botanical Medicine AI Doctor")
    print("=" * 64)

    if args.engine == "fastapi":
        try:
            import uvicorn
            from main import app
            print(f"🚀 Starting Production FastAPI Engine on http://{args.host}:{args.port}")
            uvicorn.run("main:app", host=args.host, port=args.port, reload=True)
        except ImportError as err:
            print(f"⚠️  FastAPI/Uvicorn not found ({err}). Falling back to Native HTTP Engine...")
            run_native_engine(args.port)

    elif args.engine == "native":
        run_native_engine(args.port)

    elif args.engine == "node":
        print(f"🚀 Starting Node.js Static Server on port {args.port}...")
        env = os.environ.copy()
        env["PORT"] = str(args.port)
        try:
            subprocess.run(["node", "server.js"], env=env, check=True)
        except FileNotFoundError:
            print("❌ Node.js executable not found in PATH.")
        except Exception as e:
            print(f"❌ Node.js server error: {e}")

def run_native_engine(port: int):
    print(f"🌿 Starting Native Python HTTP Server on http://127.0.0.1:{port}...")
    from app import run as run_app
    run_app(port=port)

if __name__ == "__main__":
    main()
