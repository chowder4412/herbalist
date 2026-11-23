/**
 * HERBALIST AI — TELEHEALTH TIMER UI
 * Formats and displays elapsed time only; timer lifecycle remains inline.
 */

(function(window) {
    'use strict';

    function renderTelehealthTimer(secondsElapsed) {
        const mins = Math.floor(secondsElapsed / 60);
        const secs = secondsElapsed % 60;
        const el = document.getElementById('telehealth-timer-display');
        if (el) el.innerText = `⏱ ${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }

    window.HerbalistTelehealthTimerUI = { renderTelehealthTimer };
})(window);
