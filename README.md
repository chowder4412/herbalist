# 🌿 Herbalist AI — Integrative Botanical Medicine & Clinical Intelligence

> **Evidence-Based Phytotherapy, SOCRATES Symptom Triage, Compound Concentration Calculations, and PubMed/WHO Monograph RAG Engine.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-v2.0-009688.svg)](https://fastapi.tiangolo.com)
[![Qdrant Cloud](https://img.shields.io/badge/VectorDB-Qdrant%20128D-red.svg)](https://qdrant.tech)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)

---

## 📌 Architecture Overview

```
                          ┌─────────────────────────────┐
                          │   Client User Interface     │
                          │   (Web, PWA, Voice Input)   │
                          └──────────────┬──────────────┘
                                         │
                                   HTTP / REST
                                         │
                                         ▼
                          ┌─────────────────────────────┐
                          │   Unified CLI Launcher      │
                          │        (run.py)             │
                          └──────────────┬──────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 │                                               │
                 ▼                                               ▼
  ┌─────────────────────────────┐                 ┌─────────────────────────────┐
  │   Production FastAPI Stack  │                 │    Native Standard Library  │
  │          (main.py)          │                 │          (app.py)           │
  └──────────────┬──────────────┘                 └──────────────┬──────────────┘
                 │                                               │
                 ├───────────────────────┬───────────────────────┤
                 │                       │                       │
                 ▼                       ▼                       ▼
  ┌─────────────────────────────┐ ┌─────────────┐ ┌─────────────────────────────┐
  │    AIDoctor & Compounding   │ │ Upstash     │ │  SQLite Memory Store        │
  │     (herbalist.py)          │ │ Redis Cache │ │  (clinical_memory.db)       │
  └──────────────┬──────────────┘ └─────────────┘ └─────────────────────────────┘
                 │
                 ▼
  ┌─────────────────────────────┐
  │ Qdrant Vector Cloud DB      │
  │ (PubMed RAG / Pharmacopeia) │
  └─────────────────────────────┘
```

---

## 🌟 Key Features

1. **SOCRATES Multi-Turn Diagnostic Triage**:
   - Interactive, conversational symptom collection evaluating *Site, Onset, Character, Radiation, Associations, Time course, Exacerbating factors, and Severity (1–10)*.

2. **Botanical Phytotherapy Compounding Math**:
   - Computes active bioactive mass ($\text{mg}$), total solution volume ($\text{mL}$), bioactive concentration ($\text{mg/mL}$ & $\% w/v$), and precise dosing schedules.
   - Generates step-by-step household kitchen recipes and safety instructions.

3. **Clinical Safety & Safeguards**:
   - **Emergency Red-Flag Interception**: Automatically detects life-threatening conditions (e.g. crushing chest pain, anaphylaxis) and halts triage to mandate immediate 911/ER escalation.
   - **PII/PHI Redaction**: Scrubs email addresses, phone numbers, and SSNs before processing.
   - **Herb-Drug Interaction Matrix**: Checks proposed botanical remedies against pharmaceuticals (e.g. St. John's Wort with SSRIs, Berberine with Metformin).

4. **Continuous Learning & Hybrid RAG**:
   - SQLite episodic memory database tracking patient cases and automatically expanding pharmacopeia knowledge.
   - Qdrant Cloud 128-dimensional dense vector embeddings matching cases with peer-reviewed PubMed clinical trials and WHO Botanical Monographs.

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Installation

```bash
# Clone or navigate to the directory
cd "Herbalist AI"

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration (`.env`)

Create or update `.env` with your API keys:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
QDRANT_URL=https://your-cluster-url.qdrant.tech
QDRANT_API_KEY=your_qdrant_api_key
UPSTASH_REDIS_REST_URL=https://your-redis-url.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_redis_token
JWT_SECRET=herbalist_jwt_secret_key_2026_enterprise
```

---

## 🎮 Execution & Serving Modes

You can run Herbalist AI using the **unified CLI launcher (`run.py`)**:

```bash
# 1. Default Mode — Production FastAPI Engine (Port 8000)
python run.py

# 2. Native Standard Library Mode — Lightweight Zero-Dependency Server
python run.py --engine native

# 3. Node.js Static Server Mode
python run.py --engine node

# 4. Custom Port Override
python run.py --engine fastapi --port 8080
```

### Server Comparison

| Server Engine | Command | Backend File | Best Used For |
| :--- | :--- | :--- | :--- |
| **FastAPI Production** | `python run.py --engine fastapi` | [main.py](file:///c:/Users/user/Desktop/Herbalist%20AI/main.py) | Full production with Upstash Redis, JWT Auth, RAG ingestion & Clinician Analytics |
| **Native HTTP** | `python run.py --engine native` | [app.py](file:///c:/Users/user/Desktop/Herbalist%20AI/app.py) | Lightweight environments, embedded systems, or zero-dependency standard Python |
| **Node.js Static** | `python run.py --engine node` | [server.js](file:///c:/Users/user/Desktop/Herbalist%20AI/server.js) | Static file hosting fallback with automatic port collision recovery |

---

## 🧪 Running Automated Tests

Run the test suite via `pytest`:

```bash
python -m pytest tests/
```

*Includes unit test coverage for Emergency Red Flags, PII Scrubbing, Herb-Drug Interaction Matrix, SQLite Seeding, FastAPI Endpoints, and PyJWT Auth Validation.*

---

## 🌐 API Endpoint Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/diagnose` | Core diagnostic & SOCRATES symptom triage endpoint |
| `GET` | `/health` | Production health check & pharmacopeia status |
| `GET` | `/api/recents` | Recent consultation cases & database statistics |
| `GET` | `/api/clinician/analytics` | Clinician analytics console data |
| `GET` | `/admin` | Admin Control Center web portal |
| `POST` | `/api/admin/rag/ingest` | Ingest new PubMed/WHO citations into Qdrant Cloud 128D DB |
| `DELETE` | `/api/admin/rag/citation/{pmid}` | Remove RAG citation from DB and Admin portal |
| `GET` | `/api/admin/feature-flags` | Fetch global feature toggles |
| `POST` | `/api/admin/feature-flags` | Toggle operational feature flags |

---

## 📄 License & Medical Disclaimer

**Disclaimer:** Herbalist AI is designed as a clinical decision support and educational tool for integrative phytotherapy. It does not replace professional medical evaluation, emergency services, or formal clinical diagnosis. Always consult a qualified healthcare practitioner for medical advice.
