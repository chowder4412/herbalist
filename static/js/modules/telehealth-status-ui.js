/**
 * HERBALIST AI — TELEHEALTH STATUS UI
 * Visual status updates only; microphone, speech, and call state remain inline.
 */

(function(window) {
    'use strict';

    function setOrbState(state) {
        const orb = document.getElementById('orb-core-sphere');
        if (!orb) return;
        orb.classList.remove('doctor-speaking', 'patient-speaking');
        if (state === 'doctor-speaking') orb.classList.add('doctor-speaking');
        if (state === 'patient-speaking') orb.classList.add('patient-speaking');
    }

    function updateTelehealthStatus(msg, type) {
        const el = document.getElementById('telehealth-status-badge');
        if (!el) return;
        el.innerText = msg;
        if (type === 'listening') el.style.color = 'var(--accent-green)';
        else if (type === 'speaking') el.style.color = '#1abc9c';
        else if (type === 'thinking') el.style.color = 'var(--accent-gold)';
        else if (type === 'danger') el.style.color = '#e74c3c';
    }

    window.HerbalistTelehealthStatusUI = { setOrbState, updateTelehealthStatus };
})(window);
