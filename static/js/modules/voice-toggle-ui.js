/**
 * HERBALIST AI — VOICE TOGGLE UI
 * Renders the speaker control only; voice state and speech behavior stay inline.
 */

(function(window) {
    'use strict';

    function renderVoiceToggleUI(isVoiceEnabled) {
        const btn = document.getElementById('voice-toggle-btn');
        if (!btn) return;
        if (isVoiceEnabled) {
            btn.className = 'speaker-btn active-voice';
            btn.setAttribute('title', 'Voice Audio Readout: ON — Click to Mute');
            btn.innerHTML = `
                <svg id="voice-toggle-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                    <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                </svg>`;
        } else {
            btn.className = 'speaker-btn muted-voice';
            btn.setAttribute('title', 'Voice Audio Readout: MUTED — Click to Unmute');
            btn.innerHTML = `
                <svg id="voice-toggle-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                    <line x1="23" y1="9" x2="17" y2="15"></line>
                    <line x1="17" y1="9" x2="23" y2="15"></line>
                </svg>`;
        }
    }

    window.HerbalistVoiceToggleUI = { renderVoiceToggleUI };
})(window);
