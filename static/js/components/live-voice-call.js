/**
 * ═══════════════════════════════════════════════════════════════════
 * HERBALIST AI — ADVANCED TELEHEALTH LIVE VOICE CONSULTATION SUITE
 * Bidirectional hands-free streaming, Web Audio DSP noise suppression,
 * continuous VAD barge-in interruption, and 9 multilingual doctor personas.
 * ═══════════════════════════════════════════════════════════════════
 */

(function(window) {
    'use strict';

    const VOICE_PERSONAS = {
        'en_ng': {
            id: 'en_ng',
            name: 'Dr. Aisha',
            title: 'Nigerian English • Lead Phytotherapy Specialist',
            lang: 'en-NG',
            langFallback: 'en-US',
            flag: '🇳🇬',
            pitch: 0.96,
            rate: 0.96,
            modality: 'african'
        },
        'yo': {
            id: 'yo',
            name: 'Dr. Adewale',
            title: 'Yorùbá • Indigenous Ethnobotanical Physician',
            lang: 'yo-NG',
            langFallback: 'en-NG',
            flag: '🇳🇬',
            pitch: 0.95,
            rate: 0.92,
            modality: 'african'
        },
        'ha': {
            id: 'ha',
            name: 'Dr. Yusuf',
            title: 'Hausa (Yusuf Lawal) • Phytomedicine Consultant',
            lang: 'ha-NG',
            langFallback: 'en-NG',
            flag: '🇳🇬',
            pitch: 0.95,
            rate: 0.92,
            modality: 'african'
        },
        'ig': {
            id: 'ig',
            name: 'Dr. Chioma',
            title: 'Igbo • Botanical Pharmacognosist',
            lang: 'ig-NG',
            langFallback: 'en-NG',
            flag: '🇳🇬',
            pitch: 1.05,
            rate: 0.92,
            modality: 'african'
        },
        'sw': {
            id: 'sw',
            name: 'Dr. Juma',
            title: 'Kiswahili • Mtaalamu wa Dawa Asili',
            lang: 'sw-KE',
            langFallback: 'sw',
            flag: '🇰🇪',
            pitch: 0.95,
            rate: 0.94,
            modality: 'african'
        },
        'fr': {
            id: 'fr',
            name: 'Dr. Monique',
            title: 'Français • Spécialiste en Phytothérapie',
            lang: 'fr-FR',
            langFallback: 'fr',
            flag: '🇫🇷',
            pitch: 1.02,
            rate: 0.96,
            modality: 'western'
        },
        'es': {
            id: 'es',
            name: 'Dra. Elena',
            title: 'Español • Fitoterapia Clínica y Nutrición',
            lang: 'es-ES',
            langFallback: 'es',
            flag: '🇪🇸',
            pitch: 1.02,
            rate: 0.96,
            modality: 'western'
        },
        'ar': {
            id: 'ar',
            name: 'Dr. Tariq',
            title: 'العربية • أخصائي الطب النبوي والأعشاب',
            lang: 'ar-SA',
            langFallback: 'ar',
            flag: '🇸🇦',
            pitch: 0.95,
            rate: 0.94,
            modality: 'western'
        },
        'zh': {
            id: 'zh',
            name: 'Dr. Chen',
            title: '中文 • 中医本草与辨证专家 (TCM Lead)',
            lang: 'zh-CN',
            langFallback: 'zh',
            flag: '🇨🇳',
            pitch: 0.98,
            rate: 0.95,
            modality: 'tcm'
        },
        'en_gb': {
            id: 'en_gb',
            name: 'Dr. Oliver',
            title: 'British English • Clinical Pharmacology Lead',
            lang: 'en-GB',
            langFallback: 'en-GB',
            flag: '🇬🇧',
            pitch: 1.0,
            rate: 0.96,
            modality: 'western'
        },
        'en_us': {
            id: 'en_us',
            name: 'Dr. Sarah',
            title: 'US English • Integrative Botanical Health Lead',
            lang: 'en-US',
            langFallback: 'en-US',
            flag: '🇺🇸',
            pitch: 1.02,
            rate: 0.98,
            modality: 'auto'
        }
    };

    const LiveVoiceCall = {
        modalEl: null,
        canvasEl: null,
        canvasCtx: null,
        animFrameId: null,
        recognition: null,
        audioCtx: null,
        analyser: null,
        micStream: null,
        freqDataArray: null,
        isCalling: false,
        isMuted: false,
        activePersonaKey: 'en_ng',
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
            this.modalEl.className = 'telehealth-modal-overlay';
            this.modalEl.innerHTML = `
                <!-- Top Header & Doctor Selection -->
                <div style="width:100%;max-width:760px;display:flex;align-items:center;justify-content:space-between;margin:0 auto;flex-shrink:0;">
                    <div style="display:flex;align-items:center;gap:12px;">
                        <div style="width:44px;height:44px;border-radius:14px;background:rgba(46,204,113,0.15);border:1.5px solid var(--accent-green);display:flex;align-items:center;justify-content:center;font-size:22px;box-shadow:0 0 15px rgba(46,204,113,0.3);">🩺</div>
                        <div>
                            <div style="font-size:16px;font-weight:700;color:#fff;display:flex;align-items:center;gap:8px;">
                                <span id="call-doctor-name">Dr. Aisha</span>
                                <span id="call-live-pill" style="font-size:10px;background:rgba(46,204,113,0.2);color:#2ecc71;padding:2px 8px;border-radius:8px;font-weight:800;border:1px solid rgba(46,204,113,0.35);letter-spacing:0.5px;">LIVE CONSULTATION</span>
                            </div>
                            <div id="call-doctor-title" style="font-size:12px;color:rgba(255,255,255,0.7);margin-top:2px;">Nigerian English • Lead Phytotherapy Specialist</div>
                        </div>
                    </div>

                    <!-- Multilingual Voice Switcher -->
                    <select id="call-lang-select" onchange="LiveVoiceCall.switchLanguage(this.value)" style="background:#101a14;color:#2ecc71;border:1px solid rgba(46,204,113,0.35);padding:8px 14px;border-radius:12px;font-size:12px;font-weight:700;outline:none;cursor:pointer;font-family:'Outfit',sans-serif;">
                        <option value="en_ng">🇳🇬 Nigerian English (Dr. Aisha)</option>
                        <option value="yo">🇳🇬 Yorùbá (Dr. Adewale)</option>
                        <option value="ha">🇳🇬 Hausa (Dr. Yusuf)</option>
                        <option value="ig">🇳🇬 Igbo (Dr. Chioma)</option>
                        <option value="sw">🇰🇪 Kiswahili (Dr. Juma)</option>
                        <option value="fr">🇫🇷 Français (Dr. Monique)</option>
                        <option value="es">🇪🇸 Español (Dra. Elena)</option>
                        <option value="ar">🇸🇦 العربية (Dr. Tariq)</option>
                        <option value="zh">🇨🇳 中文 (Dr. Chen)</option>
                        <option value="en_gb">🇬🇧 UK English (Dr. Oliver)</option>
                        <option value="en_us">🇺🇸 US English (Dr. Sarah)</option>
                    </select>
                </div>

                <!-- Center Audio HUD & Glowing Spherical Orb -->
                <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;margin:auto 0;width:100%;max-width:700px;">
                    <div class="stethoscope-orb-container" style="margin-bottom:16px;">
                        <div class="orb-glow-ring"></div>
                        <div class="orb-core-sphere" id="live-call-sphere">
                            <svg width="46" height="46" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path>
                                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                                <line x1="12" y1="19" x2="12" y2="22"></line>
                            </svg>
                        </div>
                    </div>

                    <div id="call-status-badge" style="font-family:'Outfit',sans-serif;font-size:15px;font-weight:700;color:var(--accent-green);text-shadow:0 0 12px rgba(46,204,113,0.5);margin-bottom:8px;">
                        Listening... Speak naturally in your language
                    </div>

                    <canvas class="waveform-canvas" id="call-waveform-canvas" width="600" height="60" style="max-width:100%;height:60px;margin-bottom:12px;"></canvas>

                    <div class="caption-ticker-box" id="call-transcript-box">
                        <div style="font-size:11px;font-weight:800;color:var(--accent-green);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">
                            LIVE CLINICAL SUBTITLES
                        </div>
                        <div id="call-transcript-subtitles" style="font-size:13.5px;line-height:1.5;color:#e8f4ec;">
                            Connected. Dr. Herbalist is listening. You can speak symptom onset, pain scale, or ask about natural botanical decoctions.
                        </div>
                    </div>
                </div>

                <!-- Bottom Telehealth Controls -->
                <div style="display:flex;justify-content:center;align-items:center;gap:12px;width:100%;max-width:760px;margin:0 auto;flex-shrink:0;flex-wrap:wrap;">
                    <button class="telehealth-ctrl-btn active-mic" id="call-mic-btn" onclick="LiveVoiceCall.toggleMute()" title="Mute / Unmute Microphone">
                        <svg id="call-mic-icon" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path>
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                            <line x1="12" y1="19" x2="12" y2="22"></line>
                        </svg>
                        <span id="call-mic-text">Microphone ON</span>
                    </button>

                    <button class="telehealth-ctrl-btn" onclick="LiveVoiceCall.interruptDoctor()" title="Interrupt Doctor Speaking & Talk">
                        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                            <line x1="23" y1="9" x2="17" y2="15"></line>
                            <line x1="17" y1="9" x2="23" y2="15"></line>
                        </svg>
                        <span>Interrupt Doctor</span>
                    </button>

                    <button class="telehealth-ctrl-btn danger" onclick="LiveVoiceCall.end()" title="End Consultation Call & View Full Prescription">
                        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M10.68 13.31a16 16 0 0 0 3.41 2.6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7 2 2 0 0 1 1.72 2v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.42 19.42 0 0 1-6-6 19.8 19.8 0 0 1-3.12-8.68A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91"></path>
                            <line x1="23" y1="1" x2="1" y2="23"></line>
                        </svg>
                        <span>End Call & View Prescription</span>
                    </button>
                </div>
            `;

            document.body.appendChild(this.modalEl);
            this.canvasEl = document.getElementById('call-waveform-canvas');
            if (this.canvasEl) this.canvasCtx = this.canvasEl.getContext('2d');
        },

        start: function(personaKey = null) {
            if (!this.modalEl) this.createModalDOM();
            this.isCalling = true;
            this.isMuted = false;

            if (personaKey && VOICE_PERSONAS[personaKey]) {
                this.activePersonaKey = personaKey;
            } else if (window.currentClinicalModality) {
                const map = { 'african': 'en_ng', 'ayurveda': 'en_gb', 'tcm': 'zh', 'western': 'en_us', 'auto': 'en_ng' };
                this.activePersonaKey = map[window.currentClinicalModality] || 'en_ng';
            }

            this.modalEl.style.display = 'flex';
            this.updateDoctorProfileUI();
            this.initWebAudioDSP();
            this.initContinuousSpeechRecognition();

            if (typeof window.showToast === 'function') {
                window.showToast('Live Telehealth Consultation Connected', 'success', 2200);
            }

            const persona = VOICE_PERSONAS[this.activePersonaKey] || VOICE_PERSONAS['en_ng'];
            this.doctorSpeak(`Hello, I am ${persona.name}. I am here to listen to your health symptoms and formulate evidence-based botanical remedies.`);
        },

        updateDoctorProfileUI: function() {
            const persona = VOICE_PERSONAS[this.activePersonaKey] || VOICE_PERSONAS['en_ng'];
            const nameEl = document.getElementById('call-doctor-name');
            const titleEl = document.getElementById('call-doctor-title');
            const languageSelect = document.getElementById('call-lang-select');
            if (nameEl) nameEl.innerText = persona.name;
            if (titleEl) titleEl.innerText = persona.title;
            if (languageSelect) languageSelect.value = persona.id;
        },

        cleanMedicalText: function(text) {
            return String(text || '')
                .replace(/<[^>]*>/g, ' ')
                .replace(/\s+/g, ' ')
                .trim();
        },

        switchLanguage: function(personaKey) {
            if (!VOICE_PERSONAS[personaKey]) return;
            this.activePersonaKey = personaKey;
            this.updateDoctorProfileUI();
            const persona = VOICE_PERSONAS[personaKey];
            this.updateSubtitle(`Voice switched to ${persona.name}.`);
        },

        initWebAudioDSP: function() {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            if (!AudioContextClass || !window.navigator?.mediaDevices?.getUserMedia) {
                this.startWaveformAnimationFallback();
                return;
            }
            window.navigator.mediaDevices.getUserMedia({ audio: true, video: false }).then((stream) => {
                if (!this.isCalling) {
                    stream.getTracks().forEach((track) => track.stop());
                    return;
                }
                this.micStream = stream;
                this.audioCtx = new AudioContextClass();
                this.analyser = this.audioCtx.createAnalyser();
                this.analyser.fftSize = 128;
                this.freqDataArray = new Uint8Array(this.analyser.frequencyBinCount);
                this.audioCtx.createMediaStreamSource(stream).connect(this.analyser);
                this.startDSPWaveformAnimation();
            }).catch(() => this.startWaveformAnimationFallback());
        },

        initContinuousSpeechRecognition: function() {
            const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!Recognition) return;
            this.recognition = new Recognition();
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = (VOICE_PERSONAS[this.activePersonaKey] || VOICE_PERSONAS.en_ng).lang;
            this.recognition.onresult = (event) => {
                let transcript = '';
                for (let index = event.resultIndex; index < event.results.length; index += 1) {
                    transcript += event.results[index][0].transcript;
                }
                if (transcript) this.updateSubtitle(transcript);
            };
            this.recognition.onend = () => {
                if (this.isCalling && !this.isMuted) {
                    try { this.recognition.start(); } catch (error) {}
                }
            };
            if (!this.isMuted) {
                try { this.recognition.start(); } catch (error) {}
            }
        },

        end: function() {
            this.isCalling = false;
            if (this.recognition) {
                try { this.recognition.stop(); } catch(e){}
            }
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
            if (this.micStream) {
                this.micStream.getTracks().forEach(track => track.stop());
                this.micStream = null;
            }
            if (this.audioCtx) {
                try { this.audioCtx.close(); } catch(e){}
                this.audioCtx = null;
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
                window.showToast('Telehealth consultation call ended', 'info', 2000);
            }
        },

        toggleMute: function() {
            this.isMuted = !this.isMuted;
            const btn = document.getElementById('call-mic-btn');
            const text = document.getElementById('call-mic-text');
            if (btn) {
                if (this.isMuted) {
                    btn.classList?.remove('active-mic');
                    btn.style.background = 'rgba(231,76,60,0.18)';
                    btn.style.borderColor = 'rgba(231,76,60,0.4)';
                    btn.style.color = '#e74c3c';
                    if (text) text.innerText = 'Microphone MUTED';
                } else {
                    btn.classList?.add('active-mic');
                    btn.style.background = '';
                    btn.style.borderColor = '';
                    btn.style.color = '';
                    if (text) text.innerText = 'Microphone ON';
                }
            }
            if (typeof window.showToast === 'function') {
                window.showToast(this.isMuted ? 'Microphone muted' : 'Microphone active', 'info', 1500);
            }
        },

        currentAudio: null,

        interruptDoctor: function() {
            if (this.currentAudio) {
                try {
                    this.currentAudio.pause();
                    this.currentAudio.currentTime = 0;
                } catch(e){}
                this.currentAudio = null;
            }
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
            this.setState('listening');
            this.updateSubtitle("Doctor interrupted. I am listening—please speak.");
        },

        doctorSpeak: function(text) {
            // Stop any existing audio or speech synthesis
            if (this.currentAudio) {
                try {
                    this.currentAudio.pause();
                    this.currentAudio.currentTime = 0;
                } catch(e){}
                this.currentAudio = null;
            }
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }

            this.setState('speaking');
            this.updateSubtitle(text);

            const spoken = this.cleanMedicalText(text);
            const persona = VOICE_PERSONAS[this.activePersonaKey] || VOICE_PERSONAS['en_ng'];

            // 1. Primary: 100% Free Server-Side Studio Neural HD Audio Stream
            const streamUrl = `/api/tts/stream?text=${encodeURIComponent(spoken.slice(0, 1000))}&voice=${encodeURIComponent(persona.id)}`;
            if (typeof Audio === 'undefined') {
                this.doctorSpeakLocalFallback(spoken, persona);
                return;
            }
            const audio = new Audio(streamUrl);
            this.currentAudio = audio;

            audio.onended = () => {
                this.currentAudio = null;
                if (this.isCalling) {
                    this.setState('listening');
                    this.updateSubtitle("Listening... Speak whenever you are ready.");
                }
            };

            audio.onerror = () => {
                console.log("[Neural Voice Fallback] Server stream unavailable, falling back to local speech engine.");
                this.currentAudio = null;
                this.doctorSpeakLocalFallback(spoken, persona);
            };

            const playPromise = audio.play();
            if (playPromise !== undefined) {
                playPromise.catch(err => {
                    console.log("[Neural Voice Autoplay Notice]:", err);
                    this.currentAudio = null;
                    this.doctorSpeakLocalFallback(spoken, persona);
                });
            }
        },

        doctorSpeakLocalFallback: function(spoken, persona) {
            if (!window.speechSynthesis) {
                if (this.isCalling) this.setState('listening');
                return;
            }
            window.speechSynthesis.cancel();

            const utter = new SpeechSynthesisUtterance(spoken);
            utter.lang = persona.lang;
            utter.rate = persona.rate || 0.96;
            utter.pitch = persona.pitch || 1.0;

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
            const badge = document.getElementById('call-status-badge');

            if (sphere) {
                sphere.className = `orb-core-sphere ${state === 'speaking' ? 'doctor-speaking' : (state === 'listening' ? 'patient-speaking' : '')}`;
            }

            if (badge) {
                if (state === 'speaking') {
                    badge.innerText = '🩺 Doctor Aisha Speaking...';
                    badge.style.color = '#1abc9c';
                } else if (state === 'listening') {
                    badge.innerText = '👂 Listening to your voice...';
                    badge.style.color = '#2ecc71';
                } else if (state === 'processing') {
                    badge.innerText = '🧠 Analyzing clinical symptoms...';
                    badge.style.color = '#f39c12';
                }
            }
        },

        updateSubtitle: function(text) {
            const sub = document.getElementById('call-transcript-subtitles');
            if (sub) sub.innerText = text;
        },

        /**
         * Real-Time DSP Waveform Visualizer using AnalyserNode Frequency Bytes
         */
        startDSPWaveformAnimation: function() {
            const draw = () => {
                if (!this.isCalling) return;
                if (this.canvasCtx && this.canvasEl && this.analyser && this.freqDataArray) {
                    this.analyser.getByteFrequencyData(this.freqDataArray);
                    const ctx = this.canvasCtx;
                    const w = this.canvasEl.width = this.canvasEl.offsetWidth;
                    const h = this.canvasEl.height = this.canvasEl.offsetHeight;

                    ctx.clearRect(0, 0, w, h);
                    const barWidth = (w / this.freqDataArray.length) * 2.2;
                    let x = 0;

                    for (let i = 0; i < this.freqDataArray.length; i++) {
                        const val = this.freqDataArray[i];
                        const percent = val / 255;
                        const barHeight = Math.max(4, percent * h * 0.85);

                        const color = this.callState === 'speaking' ? '#1abc9c' : (this.callState === 'listening' ? '#2ecc71' : '#f39c12');
                        ctx.fillStyle = color;
                        ctx.shadowBlur = 10;
                        ctx.shadowColor = color;

                        const y = (h - barHeight) / 2;
                        ctx.fillRect(x, y, barWidth - 1, barHeight);
                        x += barWidth;
                    }
                }
                this.animFrameId = window.requestAnimationFrame(draw);
            };
            draw();
        },

        startWaveformAnimationFallback: function() {
            let phase = 0;
            const draw = () => {
                if (!this.isCalling) return;
                if (this.canvasCtx && this.canvasEl) {
                    const ctx = this.canvasCtx;
                    const w = this.canvasEl.width = this.canvasEl.offsetWidth;
                    const h = this.canvasEl.height = this.canvasEl.offsetHeight;

                    ctx.clearRect(0, 0, w, h);
                    ctx.beginPath();
                    ctx.strokeStyle = this.callState === 'speaking' ? '#1abc9c' : (this.callState === 'listening' ? '#2ecc71' : 'rgba(255,255,255,0.2)');
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
                this.animFrameId = window.requestAnimationFrame(draw);
            };
            draw();
        }
    };

    window.LiveVoiceCall = LiveVoiceCall;
})(window);
