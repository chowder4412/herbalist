/**
 * HERBALIST AI — THOUGHT HUD STEP UI
 * Displays supplied stream metadata only; stream parsing remains inline.
 */

(function(window) {
    'use strict';

    function updateThoughtHUDStep(msgId, stepData) {
        const hud = document.getElementById(`thought-hud-${msgId}`);
        const stepsList = document.getElementById(`thought-steps-${msgId}`);
        const statusText = document.getElementById(`thought-hud-status-${msgId}`);
        if (hud) hud.style.display = 'block';
        if (statusText && stepData.title) statusText.innerText = stepData.title;
        if (!stepsList) return;

        let stepRow = document.getElementById(`thought-step-${msgId}-${stepData.step}`);
        if (!stepRow) {
            stepRow = document.createElement('div');
            stepRow.id = `thought-step-${msgId}-${stepData.step}`;
            stepRow.style.cssText = 'display:flex;align-items:flex-start;gap:8px;padding:4px 0;font-size:11.5px;color:rgba(255,255,255,0.85);';
            stepsList.appendChild(stepRow);
        }
        const isComplete = stepData.progress >= 100 || stepData.step < 4;
        const icon = isComplete ? '✅' : '🔍';
        stepRow.innerHTML = `
            <span style="font-size:12px;margin-top:1px;">${icon}</span>
            <div><strong style="color:var(--accent-green);">${stepData.title}:</strong><span style="color:#d0e4d7;">${stepData.message}</span></div>`;
    }

    window.HerbalistThoughtHudStepUI = { updateThoughtHUDStep };
})(window);
