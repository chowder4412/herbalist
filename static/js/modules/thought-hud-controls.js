/**
 * HERBALIST AI — THOUGHT HUD CONTROLS
 * Expand/collapse presentation only; streamed step content remains inline.
 */

(function(window) {
    'use strict';

    function toggleThoughtHUD(msgId) {
        const stepsList = document.getElementById(`thought-steps-${msgId}`);
        const arrow = document.getElementById(`thought-hud-arrow-${msgId}`);
        if (!stepsList) return;
        if (stepsList.style.display === 'none') {
            stepsList.style.display = 'flex';
            if (arrow) arrow.innerText = '▲';
        } else {
            stepsList.style.display = 'none';
            if (arrow) arrow.innerText = '▼';
        }
    }

    window.HerbalistThoughtHudControls = { toggleThoughtHUD };
})(window);
