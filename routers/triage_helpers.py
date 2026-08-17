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
            "medication for", "medicine for", "remedy for", "treatment for", "cure for", "symptoms of", "symptom of",
            "herb for", "herbs for", "plant for", "plants for", "tell me about", "explain", "describe", "what causes"
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
                    return {"category": cat, "condition_topic": topic, "source": "gemini_groq"}
            except Exception as ge:
                print(f"[ComplaintClassifier] AI engine classification notice: {ge}")

        # Layer 2: Learned Memory Cache (SQLite)
        if memory_store:
            try:
                learned_cat = memory_store.lookup_learned_intent(complaint)
                if learned_cat and learned_cat in ("knowledge", "symptom", "greeting", "out_of_domain"):
                    return {"category": learned_cat, "condition_topic": extracted_topic, "source": "memory"}
            except Exception as e:
                print(f"[ComplaintClassifier] Memory lookup error: {e}")

        # Layer 3: Offline Heuristic Pattern Matcher
        is_knowledge = any(c_clean.startswith(p) or p in c_clean for p in cls.KNOWLEDGE_PATTERNS)
        is_symptom = any(p in c_clean for p in cls.SYMPTOM_PATTERNS)

        if is_knowledge and not is_symptom:
            return {"category": "knowledge", "condition_topic": extracted_topic, "source": "keyword"}
        if is_symptom and not is_knowledge:
            return {"category": "symptom", "condition_topic": "", "source": "keyword"}

        return {"category": "unclear", "condition_topic": extracted_topic, "source": "fallback"}


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
    Generates a profound, accurate, and empathetic medical & botanical response
    anchored in clinical pathophysiology, pharmacological mechanisms, and phytotherapy.
    """
    herbs_summary = ""
    if matching_herbs:
        herbs_summary = "\n".join([
            f"- **{h.get('common_name', '')}** (*{h.get('botanical_name', '')}*): Part used: {h.get('part_used', '')}. Bioactives: {', '.join(h.get('active_bioactives', [])[:4])}. Actions: {h.get('therapeutic_properties', '')}."
            for h in matching_herbs[:5] if isinstance(h, dict)
        ])

    history_str = ""
    if conversation_history:
        recent_turns = conversation_history[-6:]
        history_str = "\n".join([f"[{t.get('role', 'user').title()}]: {t.get('text', '')}" for t in recent_turns])

    prompt = (
        f"You are Dr. Herbalist, an authoritative, compassionate Senior Integrative Medical Doctor & Botanical Phytotherapy Specialist.\n"
        f"You are consulting with '{patient_username}'.\n\n"
        f"RECENT CONVERSATION CONTEXT:\n{history_str if history_str else 'New consultation'}\n\n"
        f"PATIENT'S CURRENT QUESTION / INQUIRY:\n\"{query}\"\n\n"
        f"CORE TOPIC IDENTIFIED:\n{condition_topic.title()}\n\n"
        f"RELEVANT PHARMACOPEIA MONOGRAPHS IN KNOWLEDGE BASE:\n{herbs_summary if herbs_summary else 'General Botanical Pharmacopeia'}\n\n"
        f"CLINICAL INSTRUCTIONS FOR DR. HERBALIST:\n"
        f"1. DIRECT & ACCURATE MEDICAL ANSWER: Immediately, clearly, and thoroughly answer the patient's specific question regarding {condition_topic}. If they asked for symptoms (e.g. malaria, fever, diabetes), detail the exact clinical stages, hallmark signs, pathophysiology, and distinguishing features.\n"
        f"2. BOTANICAL PHYTOTHERAPY & MECHANISMS: Detail 3 to 5 top evidence-based medicinal plants/herbs indicated for this condition (including active bioactives, mechanisms of action like enzymatic inhibition or cytokine modulation, and traditional preparation methods like teas or decoctions).\n"
        f"3. CLINICAL WISDOM & DIAGNOSTIC GUIDANCE: Highlight critical safety warnings, essential diagnostic laboratory tests (such as Rapid Diagnostic Tests / Blood Smears for malaria, or metabolic bloodwork), red-flag symptoms requiring emergency hospital care, and herb-drug precautions.\n"
        f"4. CONTEXT CONTINUITY: If the patient shifted or compared topics from a previous turn (e.g., from general fever to malaria), acknowledge the relationship intelligently without repeating outdated answers.\n"
        f"5. COMPASSIONATE NEXT STEP: Conclude by warmly asking if they or a loved one are currently experiencing these symptoms, and invite them to share onset/duration if they desire a personalized formulation with precise dosing.\n\n"
        f"Format your response with clean Markdown headers (##), bold text, bullet points, and clinical clarity."
    )

    if doctor and getattr(doctor, 'gemini_engine', None):
        try:
            ai_msg = doctor.gemini_engine.generate_text(prompt, max_tokens=950, temperature=0.45)
            if ai_msg and len(ai_msg.strip()) > 50:
                return f"{emergency_prefix}{ai_msg.strip()}"
        except Exception as ge:
            print(f"[Herbalist AI] Knowledge reasoning error: {ge}")

    # High-quality deterministic fallback
    herb_list = ", ".join([h.get("common_name", "Traditional Botanical") for h in (matching_herbs or [])[:4]])
    fallback_text = (
        f"## Clinical Overview & Botanical Insights for {condition_topic.title()}\n\n"
        f"Regarding your inquiry: **\"{query}\"**\n\n"
        f"### Clinical Pathophysiology & Hallmark Symptoms\n"
        f"**{condition_topic.title()}** involves physiological immune defense and systemic response. Key clinical indicators include thermal dysregulation, bodily fatigue, inflammatory signaling, and localized discomfort.\n\n"
        f"### Evidence-Based Botanical Phytotherapy\n"
        f"Monographed botanical medicine utilizes verified botanicals: **{herb_list or 'Artemisia annua, Willow Bark, Neem, and Ginger'}**.\n"
        f"These herbs contain active phytochemicals that downregulate inflammatory cascades and support physiological equilibrium.\n\n"
        f"### Clinical Diagnostic & Safety Guidance\n"
        f"• If experiencing persistent or severe symptoms, accurate diagnostic testing (such as laboratory bloodwork or diagnostic blood smears) is essential.\n"
        f"• Inform your healthcare clinician of any botanical preparations you are taking to prevent herb-drug interactions.\n\n"
        f"🌿 *Are you or someone you are caring for currently experiencing these symptoms? If so, tell me how long it has been going on, and I can initiate a personalized clinical assessment for you.*"
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
        f"You are Dr. Herbalist (or Dr. Aisha when speaking to Nigerian patients), a world-class Senior Integrative Medical Doctor & Botanical Phytotherapy Specialist.\n"
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
        f"5. Start directly with your doctor response (e.g. '🩺 **Dr. Herbalist**: ...' or '🩺 **Dr. Aisha**: ...'). Do NOT include meta text, labels, or technical IDs."
    )
    
    if doctor and getattr(doctor, 'gemini_engine', None):
        try:
            ai_msg = doctor.gemini_engine.generate_text(prompt, max_tokens=350, temperature=0.6)
            if ai_msg and len(ai_msg.strip()) > 10:
                return f"{emergency_prefix}{ai_msg.strip()}"
        except Exception as ge:
            print(f"[Herbalist AI] Conversational AI reasoning notice: {ge}")

    # If target_goal is a welcome or greeting
    is_greeting_goal = target_goal.startswith("Welcome") or "greeting" in target_goal.lower() or patient_message.strip().lower() in ComplaintClassifier.GREETING_PATTERNS
    doctor_title = "Dr. Aisha" if "nigerian" in modality.lower() else "Dr. Herbalist"
    user_greet = f" {patient_username}" if patient_username else ""

    if is_greeting_goal:
        return (
            f"{emergency_prefix}🩺 **{doctor_title}**: Hello{user_greet}! Welcome to Herbalist AI. 🌿\n\n"
            f"I am your Integrative Medical Doctor and Botanical Phytotherapy Specialist. "
            f"How can I assist you today? Please feel free to describe any symptoms, health goals, or questions about natural herbal remedies."
        )

    clean_goal = target_goal.strip()
    return f"{emergency_prefix}🩺 **{doctor_title}**: Thank you for that detail. {clean_goal}"
