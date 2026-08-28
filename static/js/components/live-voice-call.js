/**
 * ═══════════════════════════════════════════════════════════════════
 * HERBALIST AI — HANDS-FREE CONTINUOUS LIVE VOICE CALL COMPONENT
 * ChatGPT Advanced Voice / Gemini Live Standard with VAD & Waveforms
 * ═══════════════════════════════════════════════════════════════════
 */

(function(window) {
    'use strict';

    const VOICE_ACCENTS = {
        'en_ng': { name: 'Dr. Aisha', title: 'Nigerian English (Phytotherapy Specialist)', lang: 'en-NG', flag: '🇳🇬' },
        'ha': { name: 'Dr. Amina', title: 'Hausa (Ethnobotanical Physician)', lang: 'ha-NG', flag: '🇳🇬' },
        'yo': { name: 'Dr. Adebayo', title: 'Yoruba (Integrative Pharmacognosist)', lang: 'yo-NG', flag: '🇳🇬' },
        'ig': { name: 'Dr. Chioma', title: 'Igbo (Botanical Medicine Lead)', lang: 'ig-NG', flag: '🇳🇬' },
        'en_gb': { name: 'Dr. Oliver', title: 'UK English (Clinical Pharmacologist)', lang: 'en-GB', flag: '🇬🇧' },
        'en_us': { name: 'Dr. Sarah', title: 'US English (Integrative Health Lead)', lang: 'en-US', flag: '🇺🇸' }
    };

    const LiveVoiceCall = {
        modalEl: null,
        canvasEl: null,
        canvasCtx: null,
        animFrameId: null,
        recognition: null,
        isCalling: false,
        isMuted: false,
        activeLang: 'en_ng',
        vadTimeout: null,
        speechBuffer: '',
        callState: 'idle', // 'idle' | 'listening' | 'speaking' | 'processing'

        init: function() {
            this.createModalDOM();
        },

        createModalDOM: function() {
            let el = document.getElementById('live-call-modal');
            if (el) {
                this.modalEl = el;
                this.canvasEl = document.getElementById('call-waveform-canvas');
                if (this.canvasEl && typeof this.canvasEl.getContext === 'function') {
                    this.canvasCtx = this.canvasEl.getContext('2d');
                }
                return;
            }

            this.modalEl = document.createElement('div');
            this.modalEl.id = 'live-call-modal';
            this.modalEl.innerHTML = `
                <!-- Top Navigation & Doctor Info -->
                <div style="width:100%;max-width:600px;display:flex;align-items:center;justify-content:space-between;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <div style="width:40px;height:40px;border-radius:12px;background:rgba(46,204,113,0.15);border:1px solid rgba(46,204,113,0.3);display:flex;align-items:center;justify-content:center;font-size:20px;">🌿</div>
                        <div>
                            <div style="font-size:15px;font-weight:700;color:#fff;display:flex;align-items:center;gap:6px;">
                                <span id="call-doctor-name">Dr. Aisha</span>
                                <span id="call-live-pill" style="font-size:10px;background:rgba(46,204,113,0.2);color:#2ecc71;padding:2px 7px;border-radius:8px;font-weight:700;border:1px solid rgba(46,204,113,0.35);">LIVE CALL</span>
                            </div>
                            <div id="call-doctor-title" style="font-size:11px;color:rgba(255,255,255,0.65);margin-top:1px;">Nigerian English (Phytotherapy Specialist)</div>
                        </div>
                    </div>

                    <!-- Language Switcher Pill -->
                    <select id="call-lang-select" onchange="LiveVoiceCall.switchLanguage(this.value)" style="background:#101a14;color:#2ecc71;border:1px solid rgba(46,204,113,0.3);padding:6px 12px;border-radius:20px;font-size:12px;font-weight:600;outline:none;cursor:pointer;">
                        <option value="en_ng">🇳🇬 Nigerian English</option>
                        <option value="ha">🇳🇬 Hausa (Dr. Amina)</option>
                        <option value="yo">🇳🇬 Yoruba (Dr. Adebayo)</option>
                        <option value="ig">🇳🇬 Igbo (Dr. Chioma)</option>
                        <option value="en_gb">🇬🇧 UK English</option>
                        <option value="en_us">🇺🇸 US English</option>
                    </select>
                </div>

                <!-- Center Audio Waveform & Glowing Live Sphere -->
                <div class="live-call-sphere-container">
                    <div class="live-call-sphere" id="live-call-sphere">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line></svg>
                    </div>
                    <canvas class="waveform-canvas" id="call-waveform-canvas"></canvas>
                    <div id="call-transcript-subtitles" style="margin-top:16px;max-width:480px;text-align:center;font-size:13.5px;color:rgba(255,255,255,0.85);min-height:40px;line-height:1.5;">
                        Listening... Speak naturally in your selected language.
                    </div>
                </div>

                <!-- Bottom Call Control Bar -->
                <div class="call-control-pill">
                    <button class="call-btn-round call-btn-mic" id="call-mic-btn" onclick="LiveVoiceCall.toggleMute()" title="Mute / Unmute Microphone">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line></svg>
                    </button>

                    <button class="call-btn-round call-btn-end" onclick="LiveVoiceCall.end()" title="End Live Voice Call">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.68 13.31a16 16 0 0 0 3.41 2.6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7 2 2 0 0 1 1.72 2v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.42 19.42 0 0 1-6-6 19.8 19.8 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91"></path><line x1="23" y1="1" x2="1" y2="23"></line></svg>
                    </button>
                </div>
            `;

            document.body.appendChild(this.modalEl);
            this.canvasEl = document.getElementById('call-waveform-canvas');
            if (this.canvasEl) this.canvasCtx = this.canvasEl.getContext('2d');
        },

        start: function(langCode = 'en_ng') {
            if (!this.modalEl) this.createModalDOM();
            this.isCalling = true;
            this.isMuted = false;
            this.activeLang = langCode;
            this.modalEl.style.display = 'flex';

            this.updateDoctorProfileUI();
            this.startWaveformAnimation();
            this.initVADRecognition();

            if (typeof window.showToast === 'function') {
                window.showToast('Connected to Dr. Herbalist Live Call', 'success', 2000);
            }

            // Speak greeting
            const prof = VOICE_ACCENTS[this.activeLang] || VOICE_ACCENTS['en_ng'];
            this.doctorSpeak(`Hello! This is ${prof.name}. I am listening to your health symptoms.`);
        },

        end: function() {
            this.isCalling = false;
            if (this.recognition) {
                try { this.recognition.stop(); } catch(e){}
            }
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
            if (this.animFrameId) {
                if (typeof window.cancelAnimationFrame === 'function') {
                    window.cancelAnimationFrame(this.animFrameId);
                } else {
                    clearTimeout(this.animFrameId);
                }
                this.animFrameId = null;
            }
            if (this.modalEl) {
                this.modalEl.style.display = 'none';
            }
            if (typeof window.showToast === 'function') {
                window.showToast('Live consultation call ended', 'info', 1800);
            }
        },

        toggleMute: function() {
            this.isMuted = !this.isMuted;
            const btn = document.getElementById('call-mic-btn');
            if (btn) {
                btn.className = this.isMuted ? 'call-btn-round call-btn-mic muted' : 'call-btn-round call-btn-mic';
            }
            if (typeof window.showToast === 'function') {
                window.showToast(this.isMuted ? 'Microphone muted' : 'Microphone unmuted', 'info', 1500);
            }
        },

        switchLanguage: function(langCode) {
            this.activeLang = langCode;
            this.updateDoctorProfileUI();
            if (this.recognition) {
                const prof = VOICE_ACCENTS[langCode] || VOICE_ACCENTS['en_ng'];
                this.recognition.lang = prof.lang;
            }
            const prof = VOICE_ACCENTS[langCode];
            this.doctorSpeak(`Language switched to ${prof.title}. How can I assist your health?`);
        },

        updateDoctorProfileUI: function() {
            const prof = VOICE_ACCENTS[this.activeLang] || VOICE_ACCENTS['en_ng'];
            const nameEl = document.getElementById('call-doctor-name');
            const titleEl = document.getElementById('call-doctor-title');
            const selectEl = document.getElementById('call-lang-select');

            if (nameEl) nameEl.innerText = `${prof.flag} ${prof.name}`;
            if (titleEl) titleEl.innerText = prof.title;
            if (selectEl) selectEl.value = this.activeLang;
        },

        /**
         * Initialize Continuous Voice Activity Detection (VAD)
         */
        initVADRecognition: function() {
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRec) {
                this.updateSubtitle("Speech recognition not supported on this browser.");
                return;
            }

            this.recognition = new SpeechRec();
            const prof = VOICE_ACCENTS[this.activeLang] || VOICE_ACCENTS['en_ng'];
            this.recognition.lang = prof.lang;
            this.recognition.continuous = true;
            this.recognition.interimResults = true;

            this.recognition.onstart = () => {
                this.setState('listening');
            };

            this.recognition.onresult = (event) => {
                if (this.isMuted) return;

                // Natural Interruption: User spoke while doctor was speaking
                if (this.callState === 'speaking' && window.speechSynthesis) {
                    window.speechSynthesis.cancel();
                    this.setState('listening');
                }

                let interim = '';
                let finalStr = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalStr += event.results[i][0].transcript;
                    } else {
                        interim += event.results[i][0].transcript;
                    }
                }

                const currentSpoken = finalStr || interim;
                if (currentSpoken.trim()) {
                    this.updateSubtitle(`"${currentSpoken}"`);
                    this.speechBuffer = currentSpoken;

                    // Reset VAD pause timer
                    clearTimeout(this.vadTimeout);
                    this.vadTimeout = setTimeout(() => {
                        if (this.speechBuffer.trim().length > 2) {
                            this.submitSpokenTurn(this.speechBuffer.trim());
                            this.speechBuffer = '';
                        }
                    }, 1200); // 1.2s pause triggers consultation query
                }
            };

            this.recognition.onerror = (e) => {
                console.log("[Live Call VAD Notice]", e.error);
            };

            this.recognition.onend = () => {
                if (this.isCalling && !this.isMuted) {
                    try { this.recognition.start(); } catch(e){}
                }
            };

            try { this.recognition.start(); } catch(e){}
        },

        submitSpokenTurn: function(text) {
            this.setState('processing');
            this.updateSubtitle(`Dr. Herbalist is analyzing: "${text}"...`);

            // Also post into main chat input so feed stays synchronized
            const input = document.getElementById('user-input');
            if (input) input.value = text;

            // Submit query to doctor endpoint
            fetch('/api/diagnose', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ complaint: text, weight_kg: 70, age: 30, severity: 5 })
            }).then(r => r.json()).then(data => {
                const responseMsg = data.conversational_message || data.diagnosis || 'I recommend a soothing herbal infusion.';
                this.doctorSpeak(responseMsg);
            }).catch(() => {
                this.doctorSpeak("I heard your symptoms. Let us formulate an integrative herbal decoction.");
            });
        },

        doctorSpeak: function(text) {
            if (!window.speechSynthesis) return;
            window.speechSynthesis.cancel();

            this.setState('speaking');
            this.updateSubtitle(text);

            const cleanText = text.replace(/<[^>]*>?/gm, '').replace(/[*_#`]/g, '');
            const utter = new SpeechSynthesisUtterance(cleanText);
            const prof = VOICE_ACCENTS[this.activeLang] || VOICE_ACCENTS['en_ng'];
            utter.lang = prof.lang;
            utter.rate = 0.96;
            utter.pitch = 1.02;

            utter.onend = () => {
                if (this.isCalling) {
                    this.setState('listening');
                    this.updateSubtitle("Listening... Speak whenever you are ready.");
                }
            };

            utter.onerror = () => {
                if (this.isCalling) this.setState('listening');
            };

            window.speechSynthesis.speak(utter);
        },

        setState: function(state) {
            this.callState = state;
            const sphere = document.getElementById('live-call-sphere');
            if (sphere) {
                sphere.className = `live-call-sphere ${state}`;
            }
        },

        updateSubtitle: function(text) {
            const sub = document.getElementById('call-transcript-subtitles');
            if (sub) sub.innerText = text;
        },

        /**
         * Animated sine waveform on canvas
         */
        startWaveformAnimation: function() {
            let phase = 0;
            const draw = () => {
                if (!this.isCalling) return;
                if (this.canvasCtx && this.canvasEl) {
                    const ctx = this.canvasCtx;
                    const w = this.canvasEl.width = this.canvasEl.offsetWidth;
                    const h = this.canvasEl.height = this.canvasEl.offsetHeight;

                    ctx.clearRect(0, 0, w, h);
                    ctx.beginPath();
                    ctx.strokeStyle = this.callState === 'speaking' ? '#2ecc71' : (this.callState === 'listening' ? '#1abc9c' : 'rgba(255,255,255,0.2)');
                    ctx.lineWidth = 2.5;

                    const amp = this.callState === 'speaking' ? 18 : (this.callState === 'listening' ? 10 : 3);
                    const freq = 0.04;

                    for (let x = 0; x < w; x++) {
                        const y = (h / 2) + Math.sin(x * freq + phase) * amp * Math.sin(x / w * Math.PI);
                        if (x === 0) ctx.moveTo(x, y);
                        else ctx.lineTo(x, y);
                    }
                    ctx.stroke();
                    phase += 0.08;
                }
                if (typeof window.requestAnimationFrame === 'function') {
                    this.animFrameId = window.requestAnimationFrame(draw);
                } else {
                    this.animFrameId = setTimeout(draw, 33);
                }
            };
            draw();
        }
    };

    window.LiveVoiceCall = LiveVoiceCall;
})(window);
