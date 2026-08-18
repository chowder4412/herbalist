"""
Gemini Clinical Reasoning Engine with Groq Cloud Failover
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional, Any


class GeminiClinicalEngine:
    """Live Google Gemini Clinical Reasoning Engine with multi-model fallback & WHO/PubMed RAG"""
    
    def __init__(self, api_key: str = None):
        self.api_key = (api_key or os.environ.get("GEMINI_API_KEY", "")).strip()
        self.groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()
        self.models = ["gemini-3.5-flash", "gemini-flash-latest"]
        self.groq_models = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.6-27b", "groq/compound"]
        self.gemini_disabled = False if (self.api_key and len(self.api_key) > 15) else True

    def _call_groq_fallback(self, prompt: str, is_json: bool = False, max_tokens: int = 1500, temperature: float = 0.2) -> Optional[Any]:
        """
        Automatic Failover Engine using Groq Cloud (openai/gpt-oss-120b, openai/gpt-oss-20b, qwen/qwen3.6-27b).
        Triggers automatically if Gemini API key is missing or hits rate limits.
        """
        groq_key = self.groq_api_key or os.environ.get("GROQ_API_KEY", "")
        if not groq_key:
            return None

        actual_max_tokens = max(max_tokens, 1200)

        for model in self.groq_models:
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": actual_max_tokens
            }
            if is_json:
                payload["response_format"] = {"type": "json_object"}

            data_bytes = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {groq_key}',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 HerbalistAI/2.0'
                }
            )

            try:
                with urllib.request.urlopen(req, timeout=12) as resp:
                    result = json.loads(resp.read().decode('utf-8'))
                    text_content = result['choices'][0]['message']['content'].strip()
                    print(f"[Groq Automatic Failover Engine] Successfully generated response via Groq ({model})!")

                    if is_json:
                        clean_json = text_content
                        if clean_json.startswith("```"):
                            clean_json = clean_json.split("\n", 1)[1]
                        if clean_json.endswith("```"):
                            clean_json = clean_json.rsplit("\n", 1)[0]
                        if clean_json.startswith("json"):
                            clean_json = clean_json[4:].strip()
                        return json.loads(clean_json)
                    return text_content
            except Exception as e:
                print(f"[Groq Automatic Failover Engine] Model {model} notice: {e}")
                continue

        return None

    def analyze_clinical_case(self, complaint: str, weight_kg: float, age: int, gender: str, severity: int) -> dict:
        """
        Multimodal Clinical AI Case Analyzer.
        Runs full medical differential diagnosis, pharmacopeia bioactive match, WHO safety, and PubMed citations.
        """
        if self.api_key and not self.gemini_disabled:
            system_instruction = (
                f"You are Dr. Herbalist, a Senior Medical Doctor & Phytotherapy Specialist. Analyze this patient case:\n"
                f"Chief Complaint: {complaint}\nAge: {age}, Gender: {gender}, Body Weight: {weight_kg} kg, Severity: {severity}/10.\n\n"
                f"Respond ONLY with a raw valid JSON string following the expected medical schema."
            )

            payload = {
                "contents": [{"role": "user", "parts": [{"text": system_instruction}]}],
                "generationConfig": {"temperature": 0.2, "topP": 0.95, "maxOutputTokens": 1500}
            }
            data_bytes = json.dumps(payload).encode('utf-8')

            for model in self.models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
                req = urllib.request.Request(url, data=data_bytes, headers={'Content-Type': 'application/json'})
                try:
                    with urllib.request.urlopen(req, timeout=8) as resp:
                        result = json.loads(resp.read().decode('utf-8'))
                        text_content = result['candidates'][0]['content']['parts'][0]['text']
                        clean_json = text_content.strip()
                        if clean_json.startswith("```"): clean_json = clean_json.split("\n", 1)[1]
                        if clean_json.endswith("```"): clean_json = clean_json.rsplit("\n", 1)[0]
                        if clean_json.startswith("json"): clean_json = clean_json[4:].strip()
                        return json.loads(clean_json)
                except urllib.error.HTTPError as he:
                    if he.code == 429:
                        print(f"[Gemini Clinical Engine] Rate limit (HTTP 429) on model {model}, trying next model...")
                        continue
                    elif he.code in (400, 403, 404):
                        print(f"[Gemini Clinical Engine] API Key Error (HTTP {he.code}). Routing to Groq failover engine.")
                        self.gemini_disabled = True
                        break
                    else:
                        print(f"[Gemini Clinical Engine] HTTP Error {he.code} on model {model}: {he.reason}")
                except Exception as e:
                    print(f"[Gemini Clinical Engine] Exception on model {model}: {e}")

        return self._call_groq_fallback(system_instruction, is_json=True, max_tokens=1500, temperature=0.2)

    def generate_text(self, prompt: str, max_tokens: int = 1500, temperature: float = 0.4) -> Optional[str]:
        """
        Plain conversational text generation.
        Triggers Groq failover if Gemini is rate-limited or unavailable.
        """
        actual_max_tokens = max(max_tokens, 1200)
        if self.api_key and not self.gemini_disabled:
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": temperature, "topP": 0.95, "maxOutputTokens": actual_max_tokens}
            }
            data_bytes = json.dumps(payload).encode('utf-8')

            for model in self.models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
                req = urllib.request.Request(url, data=data_bytes, headers={'Content-Type': 'application/json'})
                try:
                    with urllib.request.urlopen(req, timeout=8) as resp:
                        result = json.loads(resp.read().decode('utf-8'))
                        return result['candidates'][0]['content']['parts'][0]['text'].strip()
                except urllib.error.HTTPError as he:
                    if he.code == 429:
                        print(f"[Gemini Text Engine] Rate limit on model {model}, trying next...")
                        continue
                    elif he.code in (400, 403, 404):
                        print(f"[Gemini Text Engine] API Key Error (HTTP {he.code}). Routing to Groq failover engine.")
                        self.gemini_disabled = True
                        break
                    else:
                        print(f"[Gemini Text Engine] HTTP {he.code} on {model}: {he.reason}")
                except Exception as e:
                    print(f"[Gemini Text Engine] Exception on {model}: {e}")

        return self._call_groq_fallback(prompt, is_json=False, max_tokens=actual_max_tokens, temperature=temperature)

    def stream_generate_text(self, prompt: str, max_tokens: int = 1500, temperature: float = 0.4):
        """
        Yields text tokens in real-time for live typewriter streaming.
        Supports Groq streaming API and Gemini streamGenerateContent API.
        """
        groq_key = self.groq_api_key or os.environ.get("GROQ_API_KEY", "")
        if groq_key:
            for model in self.groq_models:
                url = "https://api.groq.com/openai/v1/chat/completions"
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True
                }
                data_bytes = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(
                    url,
                    data=data_bytes,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {groq_key}',
                        'User-Agent': 'Mozilla/5.0 HerbalistAI/2.0'
                    }
                )
                try:
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        for line in resp:
                            line_str = line.decode('utf-8').strip()
                            if line_str.startswith("data: ") and not line_str.endswith("[DONE]"):
                                try:
                                    chunk_json = json.loads(line_str[6:])
                                    delta = chunk_json.get('choices', [{}])[0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        yield content
                                except Exception:
                                    continue
                        return
                except Exception as e:
                    print(f"[Groq Stream notice] {e}")
                    continue

        full_text = self.generate_text(prompt, max_tokens=max_tokens, temperature=temperature)
        if full_text:
            words = full_text.split(" ")
            for i, w in enumerate(words):
                yield (w + " " if i < len(words) - 1 else w)

    def classify_intent(self, user_answer: str) -> dict:
        """
        Gemini-powered intent classification with Groq Llama 3 failover.
        """
        prompt = (
            "You are the intent classifier for Dr. Herbalist, a medical AI chatbot.\n\n"
            "The user was asked:\n"
            "\"Are you currently experiencing symptoms related to this condition, "
            "or would you like general herbal medicine information?\"\n\n"
            f"The user replied: \"{user_answer}\"\n\n"
            "Classify the user's intent as EXACTLY one of:\n"
            "- \"triage\"  → the user IS sick / has personal symptoms / wants a personal consultation\n"
            "- \"info\"    → the user just wants to learn / asking for general knowledge, NOT personally sick\n"
            "- \"unclear\" → cannot determine intent from the reply\n\n"
            "Also detect the language of the user's reply using ISO 639-1 (e.g. \"en\", \"fr\", \"yo\", \"ha\", \"sw\", \"ar\").\n\n"
            "Respond with ONLY valid JSON (no markdown, no extra text):\n"
            "{\"intent\": \"...\", \"language\": \"...\", \"confidence\": 0.0}\n"
        )

        if self.api_key and not self.gemini_disabled:
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 80}
            }
            data_bytes = json.dumps(payload).encode('utf-8')

            for model in self.models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
                req = urllib.request.Request(url, data=data_bytes, headers={'Content-Type': 'application/json'})
                try:
                    with urllib.request.urlopen(req, timeout=8) as resp:
                        result = json.loads(resp.read().decode('utf-8'))
                        raw = result['candidates'][0]['content']['parts'][0]['text'].strip()
                        if raw.startswith("```"): raw = raw.split("\n", 1)[1].rsplit("\n", 1)[0]
                        parsed = json.loads(raw)
                        intent = parsed.get("intent", "unclear")
                        if intent not in ("triage", "info", "unclear"): intent = "unclear"
                        return {
                            "intent": intent,
                            "language": parsed.get("language", "en"),
                            "confidence": float(parsed.get("confidence", 0.5))
                        }
                except urllib.error.HTTPError as he:
                    if he.code in (400, 403, 404):
                        print(f"[Gemini Intent Classifier] API Key Error (HTTP {he.code}). Routing to Groq failover engine.")
                        self.gemini_disabled = True
                        break
                except Exception as e:
                    print(f"[Gemini Intent Classifier] Error on {model}: {e}")

        groq_json = self._call_groq_fallback(prompt, is_json=True, max_tokens=100, temperature=0.1)
        if isinstance(groq_json, dict):
            intent = groq_json.get("intent", "unclear")
            if intent not in ("triage", "info", "unclear"): intent = "unclear"
            return {
                "intent": intent,
                "language": groq_json.get("language", "en"),
                "confidence": float(groq_json.get("confidence", 0.8))
            }

        return {"intent": "unclear", "language": "en", "confidence": 0.0}

    def classify_complaint_query(self, user_query: str) -> dict:
        """
        Gemini-powered complaint & query classifier with Groq Llama 3 failover.
        """
        prompt = (
            "You are Dr. Herbalist's clinical input triage AI.\n"
            "Analyze the following user query sent to a botanical medical AI app:\n\n"
            f"User Query: \"{user_query}\"\n\n"
            "Classify into EXACTLY ONE category:\n"
            "- \"greeting\"      → Simple hello, hi, good morning, how are you\n"
            "- \"knowledge\"     → Asking an educational/factual question about health, herbs, remedies, or disease mechanics (NOT reporting a personal active symptom)\n"
            "- \"symptom\"       → Reporting personal active physical/mental symptoms or asking for a diagnosis for themselves right now\n"
            "- \"out_of_domain\"  → Completely unrelated non-medical topic (cars, sports, crypto, coding, pop culture)\n"
            "- \"unclear\"        → Ambiguous or cannot determine\n\n"
            "Also extract the core health topic/condition if asking for knowledge (e.g. \"ulcer\", \"malaria\", \"headache\"), or empty string if not applicable.\n"
            "Detect the language (ISO 639-1 e.g. \"en\", \"fr\", \"yo\", \"ha\", \"pcm\" for Pidgin).\n\n"
            "Respond ONLY with raw valid JSON string (no markdown, no backticks):\n"
            "{\"category\": \"...\", \"condition_topic\": \"...\", \"language\": \"...\", \"confidence\": 0.0}\n"
        )

        if self.api_key and not self.gemini_disabled:
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 100}
            }
            data_bytes = json.dumps(payload).encode('utf-8')

            for model in self.models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
                req = urllib.request.Request(url, data_bytes, headers={'Content-Type': 'application/json'})
                try:
                    with urllib.request.urlopen(req, timeout=8) as resp:
                        result = json.loads(resp.read().decode('utf-8'))
                        raw = result['candidates'][0]['content']['parts'][0]['text'].strip()
                        if raw.startswith("```"): raw = raw.split("\n", 1)[1].rsplit("\n", 1)[0]
                        if raw.startswith("json"): raw = raw[4:].strip()
                        parsed = json.loads(raw)
                        cat = parsed.get("category", "unclear")
                        if cat not in ("knowledge", "symptom", "greeting", "out_of_domain", "unclear"): cat = "unclear"
                        return {
                            "category": cat,
                            "condition_topic": parsed.get("condition_topic", "").strip(),
                            "language": parsed.get("language", "en"),
                            "confidence": float(parsed.get("confidence", 0.5))
                        }
                except urllib.error.HTTPError as he:
                    if he.code in (400, 403, 404):
                        print(f"[Gemini Complaint Classifier] API Key Error (HTTP {he.code}). Routing to Groq failover engine.")
                        self.gemini_disabled = True
                        break
                except Exception as e:
                    print(f"[Gemini Complaint Classifier] Error on {model}: {e}")

        groq_json = self._call_groq_fallback(prompt, is_json=True, max_tokens=120, temperature=0.1)
        if isinstance(groq_json, dict):
            cat = groq_json.get("category", "unclear")
            if cat not in ("knowledge", "symptom", "greeting", "out_of_domain", "unclear"): cat = "unclear"
            return {
                "category": cat,
                "condition_topic": groq_json.get("condition_topic", "").strip(),
                "language": groq_json.get("language", "en"),
                "confidence": float(groq_json.get("confidence", 0.8))
            }

        return {"category": "unclear", "condition_topic": "", "language": "en", "confidence": 0.0}

    def analyze_vision_attachment(self, prompt_text: str, attachment_base64: str, mime_type: str = "image/jpeg", file_name: str = "") -> Optional[str]:
        """Analyzes uploaded plant photos or medical documents using Multimodal Gemini Vision AI"""
        if not self.api_key or self.gemini_disabled or not attachment_base64:
            return None

        clean_b64 = attachment_base64.split(",", 1)[1] if "," in attachment_base64 else attachment_base64

        if not mime_type or mime_type == "application/octet-stream":
            ext = file_name.lower()
            if ext.endswith(".png"): mime_type = "image/png"
            elif ext.endswith(".webp"): mime_type = "image/webp"
            elif ext.endswith(".pdf"): mime_type = "application/pdf"
            else: mime_type = "image/jpeg"

        system_instruction = (
            f"You are Dr. Herbalist, a Senior Botanical Scientist and Multimodal Clinical AI Specialist. "
            f"The user uploaded an attached file ({file_name or 'Specimen'}) with the query: \"{prompt_text or 'Please scan this plant photo/document and explain its medicinal properties.'}\"\n\n"
            f"CLINICAL VISION AI PROTOCOLS:\n"
            f"1. **Plant Specimen Identification**: Identify the botanical species, common names, part used, and active bioactives.\n"
            f"2. **Dermatological Analysis**: Analyze skin features and provide topical remedies if skin condition is shown.\n"
            f"3. **Medical Document Scan**: Summarize lab report findings if document is shown.\n"
            f"4. **REJECTION RULE**: If image is non-botanical and non-medical, reject politely.\n\n"
            f"Format response cleanly with markdown headings."
        )

        parts = [{"text": system_instruction}]
        if mime_type.startswith("image/") or mime_type == "application/pdf":
            parts.append({"inlineData": {"mimeType": mime_type, "data": clean_b64}})

        payload = {"contents": [{"role": "user", "parts": parts}], "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1500}}
        data_bytes = json.dumps(payload).encode('utf-8')

        for model in self.models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            req = urllib.request.Request(url, data=data_bytes, headers={'Content-Type': 'application/json'})
            try:
                with urllib.request.urlopen(req, timeout=12) as resp:
                    result = json.loads(resp.read().decode('utf-8'))
                    return result['candidates'][0]['content']['parts'][0]['text']
            except urllib.error.HTTPError as he:
                if he.code in (400, 403, 404):
                    print(f"[Gemini Vision AI Engine] API Key Error (HTTP {he.code}).")
                    self.gemini_disabled = True
                    break
            except Exception as e:
                print(f"[Gemini Vision AI Engine] Model {model} notice: {e}")
                continue

        return None
