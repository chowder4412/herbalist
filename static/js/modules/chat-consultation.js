/**
 * ═══════════════════════════════════════════════════════════════════
 * HERBALIST AI — CHAT & CONSULTATION STREAM CONTROLLER
 * Diagnostic query submission, SSE streaming ingestion, bubble rendering,
 * and speech synthesis orchestration.
 * ═══════════════════════════════════════════════════════════════════
 */

(function(window) {
    'use strict';

    function resetNewChatView() {
        const chatFeed = document.getElementById('chat-feed');
        if (chatFeed) {
            chatFeed.innerHTML = '';
            chatFeed.style.display = 'none';
        }

        const scrollArea = document.getElementById('view-scroll-area');
        if (scrollArea) scrollArea.classList.add('hero-mode');

        const hero = document.getElementById('hero-welcome');
        if (hero) hero.style.display = 'flex';

        if (typeof window.renderArtifactsCanvasContent === 'function') {
            window.renderArtifactsCanvasContent();
        }

        const input = document.getElementById('user-input');
        if (input) {
            input.value = '';
            input.focus();
        }
    }

    function clearAttachmentPreview() {
        const previewBar = document.getElementById('attachment-preview-bar');
        if (previewBar) previewBar.style.display = 'none';
        const fileInput = document.getElementById('chat-file-upload');
        if (fileInput) fileInput.value = '';
    }

    function toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) sidebar.classList.toggle('collapsed');
    }

    function toggleMobileSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobile-overlay');
        if (sidebar) {
            sidebar.classList.toggle('mobile-open');
            sidebar.classList.remove('collapsed');
        }
        if (overlay) overlay.classList.toggle('active');
    }

    function closeMobileSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobile-overlay');
        if (sidebar) sidebar.classList.remove('mobile-open');
        if (overlay) overlay.classList.remove('active');
    }

    let currentChatAudio = null;

    function cleanClinicalTextForChatAudio(rawText) {
        if (!rawText) return '';
        return rawText
            .replace(/<[^>]*>?/gm, ' ')
            .replace(/https?:\/\/\S+/g, '')
            .replace(/[*_#`~>\[\]]/g, ' ')
            .replace(/🔊\s*Listen\s*\([^\)]*\)/gi, '')
            .replace(/PATIENT_GUEST/g, 'patient')
            .replace(/\bDr\.\s*Aisha\b/gi, 'Doctor Aisha')
            .replace(/\bDr\.\s*Herbalist\b/gi, 'Doctor Herbalist')
            .replace(/\bDr\.\s*([A-Za-z]+)\b/g, 'Doctor $1')
            .replace(/\bDr\.\b/g, 'Doctor')
            .replace(/(\d+(?:\.\d+)?)\s*mg\b/gi, '$1 milligrams')
            .replace(/(\d+(?:\.\d+)?)\s*ml\b/gi, '$1 milliliters')
            .replace(/(\d+(?:\.\d+)?)\s*kg\b/gi, '$1 kilograms')
            .replace(/(\d+(?:\.\d+)?)\s*g\b(?=[\s,\.\)]|$)/gi, '$1 grams')
            .replace(/(\d+(?:\.\d+)?)\s*L\b(?=[\s,\.\)]|$)/gi, '$1 liters')
            .replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '')
            .replace(/\s+/g, ' ')
            .trim();
    }

    function speakDoctorMessageInSelectedLanguage(text, langKey = null) {
        if (currentChatAudio) {
            try {
                currentChatAudio.pause();
                currentChatAudio.currentTime = 0;
            } catch(e){}
            currentChatAudio = null;
        }
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }

        const clean = cleanClinicalTextForChatAudio(text);
        if (!clean) return;

        const voiceLang = langKey || window.currentChatVoiceLang || 'en';
        const voiceMap = {
            'en': 'en_ng',
            'yo': 'yo',
            'ha': 'ha',
            'ig': 'ig',
            'sw': 'sw',
            'fr': 'fr',
            'es': 'es',
            'ar': 'ar',
            'zh': 'zh'
        };
        const voiceCode = voiceMap[voiceLang] || 'en_ng';

        if (typeof window.showToast === 'function') {
            const langNames = {
                'en': 'Dr. Aisha (Nigerian English)',
                'yo': 'Dr. Adewale (Yorùbá)',
                'ha': 'Dr. Yusuf (Hausa)',
                'ig': 'Dr. Chioma (Igbo)',
                'sw': 'Dr. Juma (Swahili)',
                'fr': 'Dr. Monique (Français)',
                'es': 'Dra. Elena (Español)',
                'ar': 'Dr. Tariq (العربية)',
                'zh': 'Dr. Chen (中文)'
            };
            window.showToast(`🔊 Playing voice with ${langNames[voiceLang] || 'Dr. Aisha'}...`, 'info', 2000);
        }

        // Stream Studio HD Audio from /api/tts/stream
        const streamUrl = `/api/tts/stream?text=${encodeURIComponent(clean.slice(0, 1500))}&voice=${encodeURIComponent(voiceCode)}`;
        const audio = new Audio(streamUrl);
        currentChatAudio = audio;

        audio.onended = () => { currentChatAudio = null; };
        audio.onerror = () => {
            currentChatAudio = null;
            if (window.speechSynthesis) {
                const utter = new SpeechSynthesisUtterance(clean);
                utter.lang = voiceLang === 'en' ? 'en-NG' : voiceLang;
                window.speechSynthesis.speak(utter);
            }
        };

        const playPromise = audio.play();
        if (playPromise !== undefined) {
            playPromise.catch(() => {
                if (window.speechSynthesis) {
                    const utter = new SpeechSynthesisUtterance(clean);
                    window.speechSynthesis.speak(utter);
                }
            });
        }
    }

    function speakText(html) {
        if (window.isVoiceAutoPlayActive) {
            speakDoctorMessageInSelectedLanguage(html);
        }
    }

    // Attach to window
    window.HerbalistChatSessionUI = { resetNewChatView, clearAttachmentPreview };
    window.toggleSidebar = toggleSidebar;
    window.toggleMobileSidebar = toggleMobileSidebar;
    window.closeMobileSidebar = closeMobileSidebar;
    window.speakDoctorMessageInSelectedLanguage = speakDoctorMessageInSelectedLanguage;
    window.speakText = speakText;

})(window);
