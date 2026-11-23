/**
 * HERBALIST AI — TRIAGE PROGRESS UI
 * Renders supplied progress only; streamed triage decisions remain inline.
 */

(function(window) {
    'use strict';

    const phases = ['onset', 'duration', 'character', 'severity', 'medications', 'ready'];
    const labels = ['Onset', 'Pattern', 'Character', 'Severity', 'Medications', 'Diagnosis'];

    function showTriageProgress(currentPhase) {
        let bar = document.getElementById('triage-progress');
        if (!bar) {
            const feed = document.getElementById('chat-feed');
            if (!feed || !feed.parentNode) return;
            bar = document.createElement('div');
            bar.id = 'triage-progress';
            bar.style.cssText = 'display:flex;gap:4px;padding:8px 16px;align-items:center;justify-content:center;margin-bottom:8px;';
            feed.parentNode.insertBefore(bar, feed);
        }
        const idx = phases.indexOf(currentPhase);
        bar.innerHTML = labels.map((label, i) => {
            let bg, color, border;
            if (i < idx) {
                bg = 'rgba(46,204,113,0.25)'; color = '#2ecc71'; border = '1px solid rgba(46,204,113,0.5)';
            } else if (i === idx) {
                bg = 'rgba(46,204,113,0.12)'; color = '#fff'; border = '1px solid #2ecc71';
            } else {
                bg = 'rgba(255,255,255,0.04)'; color = 'rgba(255,255,255,0.35)'; border = '1px solid rgba(255,255,255,0.08)';
            }
            return `<span style="font-size:11px;font-weight:600;padding:4px 10px;border-radius:20px;background:${bg};color:${color};border:${border};white-space:nowrap;">${i < idx ? '✓ ' : ''}${label}</span>`;
        }).join('<span style="color:rgba(255,255,255,0.15);font-size:10px;">→</span>');
    }

    window.HerbalistTriageProgressUI = { showTriageProgress };
})(window);
