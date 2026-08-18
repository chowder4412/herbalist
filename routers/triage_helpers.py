"""
Clinical Triage Intelligence, 3-Layer Intent & Complaint Classifiers, SessionStore, and Conversational Responses
"""

import os
import json
import uuid
import random
from typing import Optional, Dict, Any, List

# Enterprise Distributed Session Storage (Upstash Redis + Fallback)
try:
    from upstash_redis import Redis
    UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL", "")
    UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")
    if UPSTASH_URL and UPSTASH_TOKEN:
        redis_client = Redis(url=UPSTASH_URL, token=UPSTASH_TOKEN)
    else:
        redis_client = None
except Exception:
    redis_client = None


class ClinicalTriageIntelligence:
    """
    Advanced Multi-System Clinical Triage Classifier & Adaptive Question Generator.
    Categorizes complaints across 8 clinical domains and dynamically generates
    targeted diagnostic questions based on missing clinical evidence.
    """
    DOMAINS = {
        "gastroenterology": {
            "keywords": ["stomach", "vomit", "vomiting", "nausea", "diarrhea", "food poisoning", "poo", "stool", "cramps", "ulcer", "gastritis", "acid", "reflux", "gerd", "bloating", "gas", "constipation", "gut"],
            "question": "Did this start abruptly after eating a specific meal or eating out? Are you experiencing nausea, vomiting, watery stools, or burning acid reflux?"
        },
        "endocrinology_metabolic": {
            "keywords": ["diabetes", "diabetic", "sugar", "blood sugar", "glucose", "urination", "thirst", "hba1c", "insulin", "metabolic", "thyroid", "pancreas"],
            "question": "Have you been diagnosed with Type 1 or Type 2 diabetes or pre-diabetes? What is your recent blood sugar level or HbA1c if known, and are you experiencing frequent urination or unquenchable thirst?"
        },
        "nutritional_wasting": {
            "keywords": ["malnutrition", "weight loss", "losing weight", "skinny", "weakness", "fatigue", "appetite", "deficiency", "starving", "anemia", "pale", "iron", "malnourished"],
            "question": "Can you describe your typical daily food intake? Have you noticed involuntary weight loss, extreme physical fatigue, muscle wasting, or hair/nail changes?"
        },
        "dermatology_skin": {
            "keywords": ["skin", "rash", "eczema", "psoriasis", "itch", "itching", "boil", "acne", "spots", "fungal", "ringworm", "lesion", "dermatitis", "hives", "wound", "scalp"],
            "question": "Where on your body is the skin irritation located? Is it red, dry, scaly, oozing, or blistering, and does contact with water, heat, or specific foods trigger it?"
        },
        "cardiovascular": {
            "keywords": ["blood pressure", "hypertension", "high bp", "cholesterol", "palpitations", "heart rate", "circulation", "swollen ankles", "edema"],
            "question": "What is your typical blood pressure reading if known? Are you experiencing leg/ankle swelling (edema), chest tightness, or palpitations?"
        },
        "respiratory": {
            "keywords": ["cough", "bronchitis", "asthma", "wheezing", "phlegm", "mucus", "sinus", "congestion", "throat", "cold", "flu"],
            "question": "Is your cough dry or producing sputum/mucus? Do you experience chest tightness, seasonal allergies, or difficulty breathing when lying flat?"
        },
        "musculoskeletal": {
            "keywords": ["joint", "knee", "back pain", "arthritis", "gout", "rheumatism", "muscle pain", "stiffness", "swelling in joint", "spine", "neck"],
            "question": "Which joints or muscles are affected? Is there visible swelling, warmth, or morning stiffness lasting over 30 minutes?"
        },
        "oncology_cancer": {
            "keywords": ["cancer", "tumor", "tumour", "carcinoma", "chemotherapy", "chemo", "radiation", "leukemia", "lymphoma", "oncology", "sarcoma", "melanoma", "metastasis", "neoplasm", "cytotoxic", "anti-tumor"],
            "question": "Which specific type or stage of cancer has been diagnosed? Are you currently undergoing chemotherapy, radiotherapy, or immunotherapy, or seeking integrative botanical adjunct support to enhance immune function, inhibit tumor angiogenesis, and manage therapy side effects?"
        },
        "neurological_mind": {
            "keywords": ["anxiety", "insomnia", "sleep", "headache", "migraine", "stress", "panic", "memory", "brain fog", "dizziness", "numbness", "neuropathy"],
            "question": "How is your sleep quality and stress level? If experiencing headaches or brain fog — is the pain throbbing, one-sided, or associated with numbness?"
        }
    }

    @classmethod
    def detect_domain(cls, text: str) -> Optional[str]:
        t = text.lower()
        for domain_name, data in cls.DOMAINS.items():
            if any(k in t for k in data["keywords"]):
                return domain_name
        return None

    @classmethod
    def get_domain_question(cls, domain_name: str) -> str:
        return cls.DOMAINS.get(domain_name, {}).get("question", "Could you describe your main symptom in more detail?")


class IntentClassifier:
    """
    3-Layer Intelligent Intent Classification Engine.
    Layer 1  — Keyword matching (fast, fully offline)
    Layer 1.5 — Learned memory lookup (SQLite, offline)
    Layer 2  — Gemini AI fallback
    Layer 3  — Self-learning persistence to DB
    """
    SICK_KEYWORDS = [
        "i have it", "yes", "i'm sick", "im sick", "i am sick",
        "yes i am", "yes i do", "i do", "i'm experiencing", "im experiencing",
        "i feel", "i am feeling", "sick", "unwell", "suffering",
        "i have symptoms", "i am experiencing", "i got it", "i have this",
        "it's me", "its me", "personally", "i am affected",
    ]
    INFO_KEYWORDS = [
        "just info", "info", "i want to learn", "learn", "information",
        "just asking", "curious", "no", "not sick", "i'm fine", "im fine",
        "general", "knowledge", "educate",
        "just want", "only want", "just need", "only need",
        "not experiencing", "not having", "don't have", "do not have",
        "want to know", "want to find out", "want to understand",
        "asking for info", "asking about", "just asking about",
        "only asking", "purely", "academic", "research",
        "not me", "for someone", "for a friend", "hypothetically",
        "theoretical", "educate me", "enlighten me",
    ]

    @classmethod
    def _keyword_match(cls, text: str) -> Optional[str]:
        t = text.strip().lower()
        wants_triage = any(ind in t for ind in cls.SICK_KEYWORDS)
        wants_info   = any(ind in t for ind in cls.INFO_KEYWORDS)
        if wants_triage and not wants_info:
            return "triage"
        if wants_info and not wants_triage:
            return "info"
        return None

    @classmethod
    def classify(cls, user_answer: str, gemini_engine=None, memory_store=None) -> str:
        # Layer 1: Primary Cognitive Reasoning Engine (Gemini 2.0 Flash with Groq Llama 3.3 70B failover)
        if gemini_engine:
            try:
                gemini_result = gemini_engine.classify_intent(user_answer)
                intent     = gemini_result.get("intent", "unclear")
                language   = gemini_result.get("language", "en")
                confidence = gemini_result.get("confidence", 0.0)

                if intent in ("triage", "info") and memory_store:
                    try:
                        memory_store.save_learned_intent(
                            phrase=user_answer,
                            intent=intent,
                            language=language,
                            confidence=confidence,
                            source="ai_engine"
                        )
                    except Exception as se:
                        print(f"[IntentClassifier] Save error: {se}")

                if intent in ("triage", "info"):
                    return intent
            except Exception as e:
                print(f"[IntentClassifier] AI engine reasoning notice: {e}")

        # Layer 2: Learned Memory Cache (SQLite)
        if memory_store:
            try:
                learned = memory_store.lookup_learned_intent(user_answer)
                if learned:
                    return learned
            except Exception as e:
                print(f"[IntentClassifier] Memory lookup error: {e}")

        # Layer 3: Offline Heuristic Matcher
        result = cls._keyword_match(user_answer)
        if result:
            return result

        return "unclear"


class ComplaintClassifier:
    """Cognitive Universal Complaint & Inquiry Classifier Powered by Gemini/Groq with Self-Learning."""

    KNOWLEDGE_PATTERNS = [
        "what is", "what are", "what's", "whats",
        "how to", "how do", "how can",
        "tell me about", "explain", "describe",
        "medication for", "medicine for", "remedy for", "treatment for", "cure for",
        "herb for", "herbs for", "plant for", "plants for",
        "can you treat", "can you cure", "can you help with",
        "what treats", "what cures", "what helps",
        "is there a", "are there any",
        "benefits of", "uses of", "side effects of",
        "difference between",
        "what causes", "why does", "why do",
    ]

    SYMPTOM_PATTERNS = [
        "i have", "i am having", "i'm having", "im having",
        "i feel", "i'm feeling", "im feeling",
        "i am experiencing", "i'm experiencing",
        "i suffer", "i'm suffering", "im suffering",
        "my head", "my stomach", "my body", "my chest", "my back", "my knee", "my leg", "my arm", "my eye",
        "it hurts", "it pains", "i can't sleep", "i cant sleep",
        "i've been", "ive been", "i have been",
        "been having", "been feeling", "been experiencing",
        "woke up with", "started feeling", "noticed",
        "pain in my", "ache in my", "swelling in my",
        "since yesterday", "since last", "for days", "for weeks", "for months",
    ]

    GREETING_PATTERNS = [
        "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
        "greetings", "howdy", "who are you", "what can you do", "help", "start",
        "hi doctor", "hello doctor", "hi dr", "hello dr", "doc", "doctor",
        "good day", "yo", "wassup", "sup"
    ]

    SYMPTOM_TERMS = [
        "pain", "ache", "fever", "malaria", "typhoid", "ulcer", "cough", "vomit", "nausea",
        "headache", "rash", "dizzy", "fatigue", "weakness", "diarrhea", "stool", "bleed",
        "burn", "itch", "swelling", "infection", "pressure", "hypertension", "diabetes",
        "sugar", "asthma", "cold", "flu", "sore", "throat", "cramps", "insomnia", "sleepless",
        "constipation", "bloating", "indigestion", "heartburn", "migraine", "arthritis", "stiffness"
    ]

    OUT_OF_DOMAIN_PATTERNS = [
        "crypto", "bitcoin", "trading", "bot", "stock", "forex", "python", "javascript",
        "code", "coding", "software", "football", "soccer", "champions league", "premier league",
        "ronaldo", "messi", "politics", "president", "election", "weather", "forecast",
        "cake", "movie", "song", "lyrics", "car repair", "engine", "homework", "math",
        "calculate", "who is the richest", "joke", "tell me a joke"
    ]

    BOTANICAL_TERMS = [
        "herb", "herbal", "plant", "plants", "leaf", "leaves", "root", "roots", "bark", "seed", "seeds",
        "tea", "tincture", "decoction", "bitter leaf", "vernonia", "moringa", "neem", "turmeric",
        "curcumin", "ginger", "garlic", "hibiscus", "zobo", "ashwagandha", "ginseng", "tulsi",
        "aloe", "guava", "papaya", "pawpaw", "eucalyptus", "feverfew", "ginkgo", "milk thistle",
        "valerian", "chamomile", "peppermint", "clove", "cinnamon", "cymbopogon", "lemongrass",
        "orange", "citrus", "lemon", "lime", "vitamin", "vitamin c", "supplement", "diet", "nutrition",
        "food", "fruit", "honey", "honeycomb", "apple cider", "baobab", "shea butter"
    ]

    @classmethod
    def extract_demographics(cls, text: str) -> dict:
        import re
        demographics = {}
        t = text.strip()

        # Extract Age
        m_age = re.search(r"\b(?:i am|i'm|im|age|am)\s*(\d{1,2})\s*(?:years|yrs|yr)?\s*(?:old)?\b", t, re.I)
        if not m_age:
            m_age = re.search(r"^\s*(\d{1,2})\s*(?:years|yrs|yr)?\s*(?:old)?\s*$", t, re.I)
        if m_age:
            try:
                age_val = int(m_age.group(1))
                if 1 <= age_val <= 120:
                    demographics["age"] = age_val
            except Exception:
                pass

        # Extract Gender
        m_gen = re.search(r"\b(?:i am|i'm|im)\s*(?:a\s*)?(male|female|man|woman|boy|girl)\b", t, re.I)
        if m_gen:
            g = m_gen.group(1).lower()
            demographics["gender"] = "Female" if g in ("female", "woman", "girl") else "Male"

        # Extract Name
        m_name = re.search(r"\b(?:my name is|i am called|call me)\s+([a-zA-Z]+)\b", t, re.I)
        if m_name:
            demographics["name"] = m_name.group(1).title()

        # Extract Location
        m_loc = re.search(r"\b(?:i am from|i live in|i'm in|living in)\s+([a-zA-Z\s]+)\b", t, re.I)
        if m_loc:
            demographics["location"] = m_loc.group(1).strip().title()

        return demographics

    @classmethod
    def extract_condition_topic(cls, text: str) -> str:
        t = text.strip().lower().rstrip("?").rstrip(".").strip()
        for prefix in [
            "what are the symptoms of", "what are the symptoms for", "what are symptoms of", "what are symptoms for",
            "what is the symptom of", "what is the symptom for", "what is the medication for", "what is the medicine for",
            "what is the remedy for", "what is the treatment for", "what is the cure for", "what are the herbs for",
            "what are the herbal remedies for", "what is the herbal remedy for", "what are the herbal treatments for",
            "what are the herbs to treat", "what is the best herb for", "what is the best medicine for",
            "what is", "what are", "what's", "whats", "how to treat", "how to cure", "how to manage", "how do you treat",
            "how should i prepare", "how do i prepare", "how to prepare", "how to take", "can i take", "is it safe to",
            "is it safe", "tell me about", "tell me", "what about", "medication for", "medicine for", "remedy for",
            "treatment for", "cure for", "symptoms of", "symptom of", "herb for", "herbs for", "plant for", "plants for",
            "explain", "describe", "what causes"
        ]:
            if t.startswith(prefix):
                t = t[len(prefix):].strip()
                break
        return t.strip() or text.strip()

    @classmethod
    def classify(cls, complaint: str, gemini_engine=None, memory_store=None) -> dict:
        extracted_topic = cls.extract_condition_topic(complaint)
        c_clean = complaint.strip().lower().rstrip("!.?,")

        # Fast Check: Greetings
        if c_clean in cls.GREETING_PATTERNS or any(c_clean == g or (c_clean.startswith(g + " ") and len(c_clean.split()) <= 3) for g in cls.GREETING_PATTERNS):
            return {"category": "greeting", "condition_topic": "", "source": "greeting_rule"}

        # Fast Check: Out of Domain / Non-Medical
        has_health_kw = any(w in c_clean for w in cls.SYMPTOM_TERMS) or any(b in c_clean for b in cls.BOTANICAL_TERMS)
        if any(ood in c_clean for ood in cls.OUT_OF_DOMAIN_PATTERNS) and not has_health_kw:
            return {"category": "out_of_domain", "condition_topic": "", "source": "out_of_domain_rule"}

        # Fast Check: Demographics & Profile Introductions (e.g. "I am 18 years old", "I am a male")
        demographics = cls.extract_demographics(complaint)
        has_symptom_kw = any(w in c_clean for w in cls.SYMPTOM_TERMS)

        if demographics and not has_symptom_kw:
            return {
                "category": "demographics",
                "condition_topic": "",
                "demographics": demographics,
                "source": "demographics_rule"
            }

        # Fast Check: Botanical Knowledge & Remedy Inquiries
        has_botanical = any(b in c_clean for b in cls.BOTANICAL_TERMS)
        has_knowledge_pattern = (
            any(p in c_clean for p in cls.KNOWLEDGE_PATTERNS) or
            any(c_clean.startswith(p) for p in ["tell me", "what", "how", "can i", "can ", "is it", "which", "should i", "why", "does ", "will "]) or
            "?" in complaint
        )

        if (has_botanical or has_knowledge_pattern) and not any(p in c_clean for p in cls.SYMPTOM_PATTERNS):
            return {
                "category": "knowledge",
                "condition_topic": extracted_topic or complaint.strip(),
                "demographics": demographics,
                "source": "botanical_knowledge_rule"
            }

        # Layer 1: Primary Cognitive Reasoning Engine (Gemini 2.0 Flash + Groq Llama 3.3 70B failover)
        if gemini_engine:
            try:
                result = gemini_engine.classify_complaint_query(complaint)
                cat = result.get("category", "unclear")
                lang = result.get("language", "en")
                conf = result.get("confidence", 0.0)
                topic = result.get("condition_topic", "").strip() or extracted_topic

                if cat in ("knowledge", "symptom", "greeting", "out_of_domain") and memory_store:
                    try:
                        memory_store.save_learned_intent(
                            phrase=complaint,
                            intent=cat,
                            language=lang,
                            confidence=conf,
                            source="ai_engine"
                        )
                    except Exception as se:
                        print(f"[ComplaintClassifier] Memory save notice: {se}")

                if cat != "unclear":
                    return {"category": cat, "condition_topic": topic, "demographics": demographics, "source": "gemini_groq"}
            except Exception as ge:
                print(f"[ComplaintClassifier] AI engine classification notice: {ge}")

        # Layer 2: Learned Memory Cache (SQLite)
        if memory_store:
            try:
                learned_cat = memory_store.lookup_learned_intent(complaint)
                if learned_cat and learned_cat in ("knowledge", "symptom", "greeting", "out_of_domain"):
                    return {"category": learned_cat, "condition_topic": extracted_topic, "demographics": demographics, "source": "memory"}
            except Exception as e:
                print(f"[ComplaintClassifier] Memory lookup error: {e}")

        # Layer 3: Offline Heuristic Pattern Matcher
        is_knowledge = any(c_clean.startswith(p) or p in c_clean for p in cls.KNOWLEDGE_PATTERNS)
        is_symptom = any(p in c_clean for p in cls.SYMPTOM_PATTERNS) or has_symptom_kw

        if is_knowledge and not is_symptom:
            return {"category": "knowledge", "condition_topic": extracted_topic, "demographics": demographics, "source": "keyword"}
        if is_symptom and not is_knowledge:
            return {"category": "symptom", "condition_topic": "", "demographics": demographics, "source": "keyword"}

        return {"category": "unclear", "condition_topic": extracted_topic, "demographics": demographics, "source": "fallback"}


class DynamicResponseGenerator:
    """Generates dynamic responses for greetings, clarifications, and out-of-domain guardrails."""

    GREETING_TEMPLATES = [
        (
            "Hello! I am **Dr. Herbalist**, your integrative medical doctor and botanical phytotherapy specialist. 🌿\n\n"
            "I have access to a pharmacopeia of **100+ verified medicinal plants** spanning African Phytotherapy, Ayurveda, Traditional Chinese Medicine, and Western Herbalism.\n\n"
            "To begin your consultation, please describe your primary symptom or health concern. For example:\n"
            "• *\"Persistent headaches and fatigue\"*\n"
            "• *\"High blood sugar and frequent urination\"*\n"
            "• *\"Joint pain in both knees\"*\n"
            "• *\"Anxiety and difficulty sleeping\"*\n\n"
            "I will ask you targeted diagnostic questions before prescribing your personalized botanical remedy."
        ),
        (
            "Welcome! 🌿 I'm **Dr. Herbalist**, your AI Clinical Phytotherapy Specialist.\n\n"
            "Whether you need an evidence-based clinical diagnosis, kitchen decoction recipes, or dosage math for traditional herbs, I'm here to help.\n\n"
            "What health concern or symptom brings you here today? (e.g., *\"stomach cramps after eating\"*, *\"elevated blood pressure\"*, or *\"chronic sleep trouble\"*)."
        ),
        (
            "Greetings! 🌿 **Dr. Herbalist** at your service — Senior Medical Doctor and Herbal Pharmacopeia Specialist.\n\n"
            "I blend modern clinical diagnostics with peer-reviewed botanical phytotherapy.\n\n"
            "Please tell me what symptom or health issue you're experiencing, or ask about any medicinal plant!"
        )
    ]

    CLARIFICATION_TEMPLATES = [
        (
            "I noticed you're asking about **{topic}**. I want to make sure I guide you accurately! 🌿\n\n"
            "Are you currently experiencing symptoms related to this condition, or would you like general educational information?\n\n"
            "• Reply **\"I have it\"** or **\"yes, I'm sick\"** — I'll start a personalized diagnostic consultation.\n"
            "• Reply **\"just info\"** or **\"I want to learn\"** — I'll share botanical knowledge directly."
        ),
        (
            "Regarding **{topic}** 🌿 — to give you the most helpful response:\n\n"
            "Are you asking because you are personally experiencing this right now, or are you looking for general herbal research/information?\n\n"
            "• Say *\"I am experiencing it\"* or *\"yes, I'm sick\"* for a clinical diagnosis & custom remedy.\n"
            "• Say *\"Just looking for info\"* or *\"I want to learn\"* for traditional herb profiles & bioactive mechanisms."
        ),
        (
            "Thanks for asking about **{topic}**! 🌿\n\n"
            "Would you prefer a **personal clinical consultation** (if you have active symptoms), or **educational herbal information**?\n\n"
            "• Reply **\"Personal consultation\"** or **\"I have symptoms\"**\n"
            "• Reply **\"General info\"** or **\"Just research\"**"
        )
    ]

    OUT_OF_DOMAIN_TEMPLATES = [
        (
            "I am **Dr. Herbalist**, an AI Senior Medical Doctor and Botanical Phytotherapy Specialist. 🌿\n\n"
            "My clinical focus is strictly on health consultations, medical diagnosis, herbal pharmacopeia, and bioactive remedies.\n\n"
            "I cannot answer non-medical pop culture or general trivia queries such as *\"{complaint}\"*.\n\n"
            "Please feel free to ask about any symptom, illness, or medicinal herb!"
        ),
        (
            "As **Dr. Herbalist**, my expertise is dedicated to human medicine and natural phytotherapy 🌿.\n\n"
            "I'm unable to assist with off-topic queries like *\"{complaint}\"*.\n\n"
            "Whenever you're ready, ask me a health-related question or share a symptom you'd like diagnosed."
        )
    ]

    @classmethod
    def get_greeting(cls, patient_name: str = "") -> str:
        greeting = random.choice(cls.GREETING_TEMPLATES)
        if patient_name and patient_name not in ("PATIENT_GUEST", "Patient"):
            greeting = f"Welcome back, **{patient_name}**! 🌿\n\n" + greeting
        return greeting

    @classmethod
    def get_clarification(cls, topic: str, emergency_prefix: str = "") -> str:
        topic_clean = topic or "a health condition"
        template = random.choice(cls.CLARIFICATION_TEMPLATES)
        msg = template.format(topic=topic_clean)
        if emergency_prefix:
            msg = f"{emergency_prefix}{msg}"
        return msg

    @classmethod
    def get_out_of_domain(cls, complaint: str) -> str:
        template = random.choice(cls.OUT_OF_DOMAIN_TEMPLATES)
        return template.format(complaint=complaint)


class SessionStore:
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self.redis = redis_client
        self._gemini_engine = None
        self._memory_store = None

    def _save_session(self, session_id: str, session_data: Dict[str, Any]):
        self._sessions[session_id] = session_data
        if self.redis:
            try:
                self.redis.set(f"session:{session_id}", json.dumps(session_data), ex=3600)
            except Exception as e:
                print(f"[Upstash Redis] Sync save notice: {e}")

    def create_session(self, complaint: str, age: int, gender: str, weight_kg: float, user_id: Optional[str] = None, patient_id: Optional[str] = None, dob: Optional[str] = None) -> str:
        session_id = f"SESS_{user_id.replace('USER_', '') if user_id else str(uuid.uuid4())[:8]}"
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "patient_id": patient_id or "PATIENT_GUEST",
            "dob": dob or "",
            "phase": "onset",
            "complaint": complaint,
            "age": age,
            "gender": gender,
            "weight_kg": weight_kg,
            "collected": {
                "complaint": complaint,
                "onset": None,
                "duration": None,
                "character": None,
                "severity": None,
                "medications": None
            },
            "conversation": []
        }
        self._save_session(session_id, session_data)
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        if self.redis:
            try:
                val = self.redis.get(f"session:{session_id}")
                if val:
                    if isinstance(val, str):
                        return json.loads(val)
                    elif isinstance(val, dict):
                        return val
            except Exception as e:
                print(f"[Upstash Redis] Sync read notice: {e}")
        return self._sessions.get(session_id)

    def advance_session(self, session_id: str, user_answer: str):
        session = self.get_session(session_id)
        if not session:
            return None, None, False

        current_phase = session.get("phase", "onset")

        # 1. SMART TOPIC SHIFT / KNOWLEDGE QUESTION DETECTION
        # Check if the user is asking a NEW question or switching condition topic
        classification = ComplaintClassifier.classify(
            user_answer,
            gemini_engine=getattr(self, '_gemini_engine', None),
            memory_store=getattr(self, '_memory_store', None)
        )
        query_cat = classification.get("category", "")
        extracted_topic = classification.get("condition_topic") or ComplaintClassifier.extract_condition_topic(user_answer)
        u_clean = user_answer.strip().lower()

        is_question_pattern = any(u_clean.startswith(p) for p in [
            "what is", "what are", "what's", "whats", "how to", "how do", "how can",
            "tell me about", "explain", "describe", "can you", "is there", "why does",
            "why do", "what causes", "symptoms of", "remedy for", "herb for"
        ]) or "?" in user_answer

        # If user asked a new question or pivoted topic (e.g., from fever to malaria, or asking about herbs)
        if query_cat == "knowledge" or is_question_pattern:
            new_topic = extracted_topic or user_answer.strip()
            session["condition_topic"] = new_topic
            session["original_question"] = user_answer
            session["info_mode"] = True
            session["phase"] = "ready"
            session["conversation"].append({"role": "patient", "text": user_answer})
            self._save_session(session_id, session)
            return None, session, True

        # 2. CONVERSATIONAL FOLLOW-UP DETECTION
        # If the session is already in info_mode + ready (knowledge answer was already given),
        # and the user sends a casual follow-up (e.g., "I'm not feeling any symptoms, just curious"),
        # mark this as a conversational follow-up so the system uses AI + conversation history
        # instead of blindly regenerating the same knowledge monograph.
        if current_phase == "ready" and session.get("info_mode"):
            session["conversation"].append({"role": "patient", "text": user_answer})
            session["_is_followup"] = True  # Signal to diagnose.py that this is a follow-up, not a repeat
            session["_followup_message"] = user_answer  # The actual current message
            self._save_session(session_id, session)
            return None, session, True

        if current_phase == "intent_clarification":
            intent = IntentClassifier.classify(
                user_answer,
                gemini_engine=getattr(self, '_gemini_engine', None),
                memory_store=getattr(self, '_memory_store', None)
            )

            if intent == "triage":
                session["phase"] = "onset"
                session["collected"]["onset"] = None
                first_question = "When did you first notice this symptom? How long have you been experiencing it?"
                session["conversation"].append({"role": "patient", "text": user_answer})
                session["conversation"].append({"role": "doctor", "text": first_question})
                self._save_session(session_id, session)
                return first_question, session, False

            elif intent == "info":
                session["phase"] = "ready"
                session["info_mode"] = True
                session["conversation"].append({"role": "patient", "text": user_answer})
                self._save_session(session_id, session)
                return None, session, True

            else:
                clarify_msg = (
                    "I want to make sure I help you in the best way! 🌿\n\n"
                    "Could you let me know:\n"
                    "• **Are you personally experiencing symptoms?** — say *\"yes, I have it\"* or *\"I am sick\"*\n"
                    "• **Or do you just want to learn about herbal remedies?** — say *\"just information\"* or *\"I want to learn\"*"
                )
                session["conversation"].append({"role": "patient", "text": user_answer})
                session["conversation"].append({"role": "doctor", "text": clarify_msg})
                self._save_session(session_id, session)
                return clarify_msg, session, False

        if current_phase in session["collected"]:
            session["collected"][current_phase] = user_answer

        session["conversation"].append({"role": "patient", "text": user_answer})

        all_text = (session.get("complaint", "") + " " + " ".join([c.get("text", "") for c in session.get("conversation", [])])).lower()
        detected_domain = ClinicalTriageIntelligence.detect_domain(all_text)

        if len(user_answer.strip().split()) < 2 and current_phase not in ["severity", "medications"] and current_phase != "intent_clarification":
            clarifying_q = f"To help me pinpoint your exact condition, could you share a bit more detail about your {current_phase} (e.g. what triggered it, how it feels, or associated symptoms)?"
            session["conversation"].append({"role": "doctor", "text": clarifying_q})
            self._save_session(session_id, session)
            return clarifying_q, session, False

        domain_question = ClinicalTriageIntelligence.get_domain_question(detected_domain) if detected_domain else "Is the symptom constant or does it come and go? How often does it occur?"

        SOCRATES_QUESTIONS = {
            "onset": {
                "question": "When did you first notice this symptom? How long have you been experiencing it?",
                "follow_up": "condition_deepdive" if detected_domain else "duration"
            },
            "condition_deepdive": {
                "question": domain_question,
                "follow_up": "duration"
            },
            "duration": {
                "question": "Is the symptom constant or does it come and go? How often does it occur?",
                "follow_up": "character"
            },
            "character": {
                "question": "Can you describe the nature of the symptom? For example, if it's pain — is it sharp, dull, throbbing, or burning?",
                "follow_up": "severity"
            },
            "severity": {
                "question": "On a scale of 1–10 (10 being the worst), how severe is this symptom right now?",
                "follow_up": "medications"
            },
            "medications": {
                "question": "Are you currently taking any medications (prescription or OTC)? This avoids herb-drug interactions.",
                "follow_up": "ready"
            }
        }

        next_phase = SOCRATES_QUESTIONS.get(current_phase, {}).get("follow_up", "ready")
        session["phase"] = next_phase

        if next_phase == "ready":
            self._save_session(session_id, session)
            return None, session, True
        else:
            next_q = SOCRATES_QUESTIONS[next_phase]["question"]
            session["conversation"].append({"role": "doctor", "text": next_q})
            self._save_session(session_id, session)
            return next_q, session, False

    def delete_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]
        if self.redis:
            try:
                self.redis.delete(f"session:{session_id}")
            except Exception:
                pass


def generate_knowledge_medical_answer(
    query: str,
    patient_username: str,
    condition_topic: str,
    conversation_history: List[Dict[str, str]] = None,
    matching_herbs: List[Dict[str, Any]] = None,
    emergency_prefix: str = "",
    doctor=None
) -> str:
    """
    Generates a clear, warm, relatable, and crystal-clear medical & botanical response
    in plain everyday language so that anyone who knows how to read can easily understand.
    """
    herbs_summary = ""
    if matching_herbs:
        herbs_summary = "\n".join([
            f"- **{h.get('common_name', '')}** (*{h.get('botanical_name', '')}*): Used part: {h.get('part_used', 'Leaves/Roots')}. Common benefits: {h.get('therapeutic_properties', 'Soothes inflammation & supports healing')}."
            for h in matching_herbs[:5] if isinstance(h, dict)
        ])

    history_str = ""
    if conversation_history:
        recent_turns = conversation_history[-6:]
        history_str = "\n".join([f"[{t.get('role', 'user').title()}]: {t.get('text', '')}" for t in recent_turns])

    history_context = ""
    if history_str:
        history_context = (
            f"\nCONVERSATION HISTORY (most recent exchanges):\n{history_str}\n\n"
            f"IMPORTANT: Read the conversation history above. Do NOT repeat information already given. "
            f"If you already answered this question, provide NEW complementary details or address the "
            f"patient's latest message directly.\n\n"
        )

    prompt = (
        f"You are Dr. Herbalist, a friendly, warm, and highly skilled Senior Integrative Medical Doctor & Botanical Specialist.\n"
        f"You are speaking directly with patient '{patient_username or 'there'}'.\n\n"
        f"{history_context}"
        f"PATIENT'S QUESTION:\n\"{query}\"\n\n"
        f"TOPIC:\n{condition_topic.title()}\n\n"
        f"RELEVANT HERBS IN KNOWLEDGE BASE:\n{herbs_summary if herbs_summary else 'General Botanical Herbs'}\n\n"
        f"CRITICAL COMMUNICATION GUIDELINES:\n"
        f"1. RELATABLE & SIMPLE LANGUAGE: Write in plain, everyday English that is crystal clear, empathetic, and easy to understand for any ordinary reader. Strictly avoid heavy, intimidating medical jargon (e.g. write 'soothes swelling and fights germs' instead of 'downregulates inflammatory cascades', write 'balances body temperature' instead of 'thermal dysregulation').\n"
        f"2. CLEAR, FRIENDLY STRUCTURE:\n"
        f"   - 🌿 **What is happening in the body**: Explain what causes this and what is happening in 2-3 simple, comforting sentences.\n"
        f"   - 🍃 **Best Natural & Herbal Remedies**: Mention 3-4 top proven herbs with their common names and explain in plain words how each one helps (e.g. soothing the skin, stopping itching, cooling fever, easing digestion, fighting bacteria).\n"
        f"   - 💡 **Simple Home Care Tips**: Practical, everyday things the person can do right now at home (e.g. food to eat or avoid, cool water, rest, gentle hygiene).\n"
        f"   - ⚠️ **When to Seek Medical Help**: Simple, clear warning signs that mean they should visit a hospital or clinic.\n"
        f"3. WARM NEXT STEP: Conclude with an open, caring question asking if they or a family member are experiencing this right now, inviting them to share more details if they want a step-by-step personalized home recipe with exact measurements.\n\n"
        f"Format with clean Markdown headers (##), bold text, and bullet points."
    )

    if doctor and getattr(doctor, 'gemini_engine', None):
        try:
            ai_msg = doctor.gemini_engine.generate_text(prompt, max_tokens=900, temperature=0.5)
            if ai_msg and len(ai_msg.strip()) > 50:
                return f"{emergency_prefix}{ai_msg.strip()}"
        except Exception as ge:
            print(f"[Herbalist AI] Knowledge reasoning error: {ge}")

    # High-quality relatable plain-English deterministic fallbacks
    topic_lower = condition_topic.lower()
    
    # 1. Skin Rashes, Eczema, Itching, Skin Allergies
    if any(w in topic_lower for w in ["skin", "rash", "itch", "eczema", "dermatitis", "pimple", "acne", "boil", "ringworm", "hives"]):
        fallback_text = (
            f"## 🌿 Natural Remedies & Doctor's Advice for Skin Rashes\n\n"
            f"You asked: **\"{query}\"**\n\n"
            f"### 🔍 What is Happening to the Skin?\n"
            f"Skin rashes happen when your skin gets irritated, swollen, or reacts to something like heat, an allergic reaction, harsh soaps, or a mild infection. Common signs include redness, itching, small bumps, burning, or dry peeling skin.\n\n"
            f"### 🍃 Best Natural & Herbal Remedies for Skin Rashes\n"
            f"Here are top proven botanicals that gently soothe and heal the skin:\n\n"
            f"• **Aloe Vera Gel**: Immediately cools burning, reduces redness, and hydrates dry, peeling skin.\n"
            f"• **Neem Leaves (Dogonyaro)**: A powerful natural cleanser that fights bacteria and clears up itchy fungal or bacterial rashes.\n"
            f"• **Turmeric & Virgin Coconut Oil**: Mix a pinch of pure turmeric powder with warm coconut oil to form a paste; it relieves swelling and repairs damaged skin.\n"
            f"• **Chamomile or Oatmeal Wash**: Rinsing with cool chamomile tea or an oatmeal soak calms intense itching and stops irritation.\n\n"
            f"### 💡 Simple Home Care & Daily Tips\n"
            f"• **Do not scratch**: Scratching tears the skin and can introduce germs.\n"
            f"• **Keep it clean and cool**: Wash the area gently with mild, fragrance-free soap and pat dry with a clean towel.\n"
            f"• **Wear loose, breathable cotton clothes**: Avoid tight or synthetic fabrics that trap sweat.\n\n"
            f"### ⚠️ When to See a Doctor at a Clinic\n"
            f"Please visit a hospital or clinic right away if:\n"
            f"• The rash spreads very quickly all over your body.\n"
            f"• It is accompanied by high fever, trouble breathing, or swelling of the face and lips.\n"
            f"• You see yellowish pus or open blisters.\n\n"
            f"🌿 *Are you or someone you are caring for dealing with a skin rash right now? If yes, tell me where it is and how long you've had it, and I can give you a step-by-step personalized home recipe!*"
        )
    # 2. Malaria, Fever, Typhoid, Chills
    elif any(w in topic_lower for w in ["malaria", "fever", "typhoid", "chill", "cold", "flu", "cough", "catarrh"]):
        fallback_text = (
            f"## 🌿 Doctor's Guide & Herbal Remedies for Fever & Malaria\n\n"
            f"You asked: **\"{query}\"**\n\n"
            f"### 🔍 What is Happening in the Body?\n"
            f"When your body is fighting off an infection like malaria, a virus, or the flu, your immune system raises your body temperature to help kill the germs. This causes fever, body weakness, headache, shivering chills, and loss of appetite.\n\n"
            f"### 🍃 Best Natural & Herbal Remedies\n"
            f"• **Sweet Annie (Artemisia annua)**: Contains natural *artemisinin*, the world-recognized compound that attacks and clears malaria parasites in the bloodstream.\n"
            f"• **Neem Bark & Leaves (Dogonyaro)**: Traditionally boiled into a cleansing tea that helps lower high fever and purge toxins.\n"
            f"• **Lemongrass & Ginger Tea**: Boiled lemongrass with crushed ginger brings down fever by promoting gentle sweating and relieving headache and body aches.\n"
            f"• **Pawpaw (Papaya) Leaf Extract**: Rich in enzymes that boost platelet levels and strengthen the immune system during severe viral fevers.\n\n"
            f"### 💡 Simple Home Care Tips\n"
            f"• **Drink plenty of fluids**: Drink lots of clean water, coconut water, or warm herbal teas to replace fluids lost from sweating.\n"
            f"• **Rest adequately**: Give your body enough sleep so your white blood cells can fight the infection.\n"
            f"• **Eat light, nourishing foods**: Warm vegetable soups, ripe fruits, and porridge.\n\n"
            f"### ⚠️ Essential Safety & Red Flags\n"
            f"• **Get tested**: If you suspect malaria or typhoid, do a rapid blood test (RDT) or blood smear at a local clinic or pharmacy to be 100% sure.\n"
            f"• **Emergency signs**: Seek immediate emergency hospital care if there is continuous vomiting, confusion, severe yellow eyes (jaundice), or difficulty breathing.\n\n"
            f"🌿 *Are you currently feeling feverish or experiencing body aches? Tell me how many days you've felt this way, and I can prepare a custom natural recovery recipe for you!*"
        )
    # 3. Stomach, Digestion, Ulcer, Acid Reflux, Bloating
    elif any(w in topic_lower for w in ["stomach", "ulcer", "gastric", "gerd", "acid", "bloat", "digestion", "constipat", "diarrhea", "heartburn"]):
        fallback_text = (
            f"## 🌿 Natural Relief & Doctor's Advice for Stomach & Digestive Issues\n\n"
            f"You asked: **\"{query}\"**\n\n"
            f"### 🔍 What is Happening in the Stomach?\n"
            f"Stomach discomfort, bloating, or burning usually happens when the protective stomach lining gets irritated, when stomach acid flows upward into the chest, or when food doesn't digest smoothly in the intestines.\n\n"
            f"### 🍃 Best Natural & Herbal Remedies for Stomach Care\n"
            f"• **Fresh Ginger Root**: A gentle powerhouse that calms nausea, eases stomach cramps, and speeds up healthy digestion.\n"
            f"• **Unripe Plantain Flour / Mash**: Rich in natural compounds that help coat and heal painful stomach ulcers.\n"
            f"• **Peppermint or Spearmint Infusion**: Relaxes tight stomach muscles and helps release trapped gas and bloating.\n"
            f"• **Chamomile Tea**: Soothes inflamed stomach linings and reduces stress-related tummy aches.\n\n"
            f"### 💡 Everyday Habits to Protect Your Stomach\n"
            f"• Eat smaller, frequent meals rather than large heavy plates.\n"
            f"• Avoid overly oily, deeply fried, very spicy foods, and late-night heavy dinners before bed.\n"
            f"• Drink water between meals rather than gulping huge amounts while eating.\n\n"
            f"### ⚠️ When to See a Doctor Immediately\n"
            f"• Severe, sharp stomach pain that doesn't go away.\n"
            f"• Vomiting blood or passing very dark, tar-like stools.\n\n"
            f"🌿 *Are you having stomach pain, gas, or acid reflux right now? Tell me what symptoms you have and when they happen (e.g. before or after food), and I will create a tailored soothing tea recipe!*"
        )
    # 4. Blood Pressure, Hypertension, Heart
    elif any(w in topic_lower for w in ["hypertension", "blood pressure", "bp", "heart", "cardio"]):
        fallback_text = (
            f"## 🌿 Managing Blood Pressure with Natural Herbs & Healthy Habits\n\n"
            f"You asked: **\"{query}\"**\n\n"
            f"### 🔍 Understanding Blood Pressure in Simple Words\n"
            f"Blood pressure is the force of blood pushing against the walls of your blood vessels. When your blood vessels get tight or stiff, your heart has to work much harder to pump blood through your body.\n\n"
            f"### 🍃 Proven Natural Botanicals for Healthy Blood Pressure\n"
            f"• **Hibiscus Flower (Zobo / Sorrel)**: Drinking unsweetened hibiscus tea naturally relaxes blood vessels and helps gently lower high systolic pressure.\n"
            f"• **Fresh Raw Garlic**: Contains *allicin*, which helps keep blood vessels flexible and improves smooth blood circulation.\n"
            f"• **Moringa Oleifera Leaves**: Packed with potassium and antioxidants that support healthy vascular tone and kidney filtration.\n"
            f"• **Hawthorn Berry**: A time-honored botanical that strengthens heart muscle contractions and supports steady heart rhythm.\n\n"
            f"### 💡 Simple Daily Steps to Protect Your Heart\n"
            f"• **Cut back on table salt (sodium)** and processed seasoning cubes.\n"
            f"• Take a brisk 20-minute daily walk to keep blood flowing.\n"
            f"• Practice deep breathing or meditation to keep everyday stress low.\n\n"
            f"### ⚠️ Critical Safety Advice\n"
            f"• Never stop taking prescribed blood pressure medication abruptly without speaking to your doctor.\n"
            f"• Check your blood pressure regularly using a standard home arm cuff.\n\n"
            f"🌿 *Do you know your current blood pressure numbers? Share them with me, and I can suggest a daily natural herbal tea schedule to support your health!*"
        )
    # 5. Joint Pain, Arthritis, Knee, Back, Inflammation
    elif any(w in topic_lower for w in ["joint", "arthritis", "knee", "back", "rheumatism", "gout", "swelling"]):
        fallback_text = (
            f"## 🌿 Natural Relief for Joint Pain, Stiffness & Inflammation\n\n"
            f"You asked: **\"{query}\"**\n\n"
            f"### 🔍 What Causes Joint Pain?\n"
            f"Joint pain and morning stiffness happen when the cushioning cartilage between your bones wears down or when the joint tissues become inflamed and swollen from wear-and-tear, age, or uric acid buildup.\n\n"
            f"### 🍃 Top Natural Herbs for Joint Comfort\n"
            f"• **Turmeric (Curcumin) with Black Pepper**: One of nature's strongest anti-inflammatories; it eases stiffness and reduces joint swelling.\n"
            f"• **White Willow Bark**: Nature's original source of salicin (the plant origin of aspirin) which gently relieves joint aches.\n"
            f"• **Ginger Root**: Blocks inflammatory signals and improves joint flexibility.\n"
            f"• **Frankincense (Boswellia)**: Helps preserve joint cartilage and reduces morning joint tightness.\n\n"
            f"### 💡 Simple Everyday Joint Care\n"
            f"• Apply warm compresses or a warm ginger-infused towel to stiff joints for 15 minutes.\n"
            f"• Engage in low-impact movement like swimming, cycling, or gentle walking to keep joints lubricated.\n"
            f"• Drink plenty of clean water to help flush out inflammatory crystals.\n\n"
            f"🌿 *Which joint is hurting you and how long has it bothered you? Let me know, and I'll prescribe a custom warm herbal decoction and massage oil blend!*"
        )
    # 6. General / Universal Relatable Fallback
    else:
        herb_str = ", ".join([h.get("common_name", "Traditional Botanical") for h in (matching_herbs or [])[:4]]) or "Ginger, Turmeric, Moringa, and Aloe Vera"
        fallback_text = (
            f"## 🌿 Doctor's Guide & Botanical Insights for {condition_topic.title()}\n\n"
            f"You asked: **\"{query}\"**\n\n"
            f"### 🔍 What You Need to Know\n"
            f"**{condition_topic.title()}** is a common health topic. When your body is dealing with this, it is important to support your natural immune defenses and use proven, gentle remedies that help your body heal from within.\n\n"
            f"### 🍃 Helpful Natural Botanicals\n"
            f"Verified medicinal plants often used for this include: **{herb_str}**.\n"
            f"These plants contain natural antioxidants and soothing compounds that calm inflammation, boost vitality, and support total body wellness.\n\n"
            f"### 💡 Everyday Health & Safety Tips\n"
            f"• Stay well-hydrated with clean water and nutrient-rich, unrefined foods.\n"
            f"• If you are experiencing persistent or worsening symptoms, getting a proper checkup at a medical laboratory or clinic is always recommended.\n"
            f"• Always let your doctor know about any herbs you are taking alongside prescription drugs.\n\n"
            f"🌿 *Are you or a family member currently experiencing this? If you'd like, tell me your specific symptoms and I will prepare a personalized herbal recipe with exact brewing instructions for you!*"
        )

    return f"{emergency_prefix}{fallback_text}"


def generate_conversational_doctor_response(
    patient_message: str,
    patient_username: str,
    target_goal: str,
    collected_context: Dict[str, Any] = None,
    pharmacopeia_context: List[Any] = None,
    emergency_prefix: str = "",
    doctor=None,
    modality: str = "auto"
) -> str:
    """Generates a dynamic conversational response via Gemini Clinical Engine with Groq fallback and modality awareness."""
    collected_clean = {k: v for k, v in (collected_context or {}).items() if v}
    collected_str = json.dumps(collected_clean) if collected_clean else "None so far"
    herbs_str = ", ".join([h.get("common_name", "") for h in (pharmacopeia_context or [])[:5] if isinstance(h, dict)])
    
    clean_name = patient_username if (patient_username and patient_username not in ("PATIENT_GUEST", "Guest", "PATIENT_ACTIVE", "Patient")) else ""
    patient_address_instruction = f"Address the patient warmly by their name '{clean_name.split()[0].title()}'." if clean_name else "Address the patient warmly as 'there' or 'friend'. NEVER output 'PATIENT_GUEST' or technical IDs."

    modality_guide = {
        "tcm": "CLINICAL MODALITY: Traditional Chinese Medicine (TCM). Frame etiology through Yin/Yang balance, Qi & Blood circulation, and Zang-Fu organ patterns with monographed Chinese/Kampo botanicals.",
        "ayurveda": "CLINICAL MODALITY: Ayurvedic Medicine. Frame etiology through Tridosha balancing (Vata, Pitta, Kapha), Agni digestive fire, and Rasayana rejuvenating herbs (Ashwagandha, Tulsi, Triphala, Brahmi).",
        "african": "CLINICAL MODALITY: African Indigenous Phytotherapy. Highlight proven African ethnobotanical compendiums (Vernonia amygdalina/Bitter leaf, Moringa, African Ginger, Hibiscus sabdariffa, Garcinia kola).",
        "western": "CLINICAL MODALITY: Western Clinical Herbalism. Focus on pharmacodynamics, active bioactives (flavonoids, alkaloids, terpenes), German Commission E, and receptor affinities.",
        "auto": "CLINICAL MODALITY: Global WHO Synthesis. Harmoniously synthesize Western clinical pharmacology with verified global traditional medicine monographs (WHO/TCM/Ayurveda/African)."
    }.get(modality.lower(), "CLINICAL MODALITY: Global WHO Synthesis.")

    prompt = (
        f"You are Dr. Herbalist (or Dr. Aisha for fluent Nigerian English consultations, or Dr. Bovi for Nigerian Pidgin English consultations), a world-class Senior Integrative Medical Doctor & Botanical Phytotherapy Specialist.\n"
        f"{modality_guide}\n"
        f"You are conducting an active, empathetic medical consultation.\n"
        f"{patient_address_instruction}\n\n"
        f"PATIENT'S LATEST INPUT:\n\"{patient_message}\"\n\n"
        f"CLINICAL EVIDENCE COLLECTED SO FAR:\n{collected_str}\n\n"
        f"RELEVANT PHARMACOPEIA HERBS FOUND IN KNOWLEDGE BASE:\n{herbs_str if herbs_str else 'General Integrative Remedies'}\n\n"
        f"CLINICAL QUESTION / TARGET ITEM NEEDED NEXT:\n{target_goal}\n\n"
        f"REQUIREMENTS FOR THE AI DOCTOR:\n"
        f"1. Respond with genuine clinical warmth, empathy, and logical medical reasoning reflecting the chosen modality.\n"
        f"2. Validate what the patient stated, connecting their symptoms or answers to physiological mechanisms when appropriate.\n"
        f"3. Seamlessly ask the next clinical question ('{target_goal}') in a natural, fluid, conversational way without sounding like a static form.\n"
        f"4. Keep the response concise (2 to 4 sentences max). Use markdown formatting.\n"
        f"5. Start directly with your doctor response (e.g. '🩺 **Dr. Aisha**: ...', '🎤 **Dr. Bovi**: ...', or '🩺 **Dr. Herbalist**: ...'). Do NOT include meta text, labels, or technical IDs."
    )
    
    if doctor and getattr(doctor, 'gemini_engine', None):
        try:
            ai_msg = doctor.gemini_engine.generate_text(prompt, max_tokens=350, temperature=0.6)
            if ai_msg and len(ai_msg.strip()) > 10:
                return f"{emergency_prefix}{ai_msg.strip()}"
        except Exception as ge:
            print(f"[Herbalist AI] Conversational AI reasoning notice: {ge}")

    # If target_goal is a welcome or greeting
    # Resolve doctor title and icon based on modality / persona
    mod_low = modality.lower()
    if "pidgin" in mod_low or "bovi" in mod_low or "pcm" in mod_low:
        doctor_title = "Dr. Bovi"
        doctor_icon = "🎤"
    elif "nigerian" in mod_low or "aisha" in mod_low:
        doctor_title = "Dr. Aisha"
        doctor_icon = "🩺"
    elif "ayurveda" in mod_low or "rajesh" in mod_low or "india" in mod_low:
        doctor_title = "Vaidya Dr. Rajesh"
        doctor_icon = "🕉️"
    elif "swahili" in mod_low or "amani" in mod_low:
        doctor_title = "Dkt. Amani"
        doctor_icon = "🌴"
    else:
        doctor_title = "Dr. Herbalist"
        doctor_icon = "🩺"

    is_greeting_goal = target_goal.startswith("Welcome") or "greeting" in target_goal.lower() or patient_message.strip().lower() in ComplaintClassifier.GREETING_PATTERNS
    user_greet = f" {patient_username}" if (patient_username and patient_username not in ("PATIENT_GUEST", "PATIENT_ACTIVE")) else ""

    if is_greeting_goal:
        if doctor_title == "Dr. Bovi":
            return (
                f"{emergency_prefix}🎤 **Dr. Bovi**: How body{user_greet}? Welcome to Herbalist AI! 🌿\n\n"
                f"I be your herbal medical doctor wey sabi correct natural roots and herbs well well. "
                f"Wetin dey do your body today? Tell me how you dey feel or any herbal remedy wey you wan ask about."
            )
        return (
            f"{emergency_prefix}{doctor_icon} **{doctor_title}**: Hello{user_greet}! Welcome to Herbalist AI. 🌿\n\n"
            f"I am your Integrative Medical Doctor and Botanical Phytotherapy Specialist. "
            f"How can I assist you today? Please feel free to describe any symptoms, health goals, or questions about natural herbal remedies."
        )

    if "introduced their profile details" in target_goal or "Acknowledge their profile" in target_goal:
        import re
        m_age = re.search(r"(\d{1,2})\s*years old", target_goal)
        age_str = f"that you are {m_age.group(1)} years old" if m_age else "your details"
        if doctor_title == "Dr. Bovi":
            return (
                f"{emergency_prefix}🎤 **Dr. Bovi**: I hear you{user_greet}! I don take note say you be {m_age.group(1) if m_age else ''} years. 🌿\n\n"
                f"Wetin dey worry your body today? Feel free to tell me wetin you dey experience (like fever, stomach pain, headache) or any leaf/root wey you wan know about."
            )
        return (
            f"{emergency_prefix}{doctor_icon} **{doctor_title}**: Thank you{user_greet}! I have noted {age_str}. 🌿\n\n"
            f"What health symptoms, discomfort, or wellness goals bring you in today? "
            f"Please feel free to describe how you are feeling (e.g. fever, headaches, stomach pain) or ask any herbal medicine question."
        )

    clean_goal = target_goal.strip()
    return f"{emergency_prefix}{doctor_icon} **{doctor_title}**: Thank you for that detail. {clean_goal}"
