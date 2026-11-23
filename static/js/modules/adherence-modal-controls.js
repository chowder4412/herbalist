/**
 * HERBALIST AI — ADHERENCE MODAL CONTROLS
 * Presentation only; adherence state, reminders, and storage remain inline.
 */

(function(window) {
    'use strict';

    function openAdherenceModal() {
        const modal = document.getElementById('adherence-modal');
        if (modal) modal.style.display = 'flex';
        if (typeof window.updateAdherenceUI === 'function') window.updateAdherenceUI();
    }

    function closeAdherenceModal() {
        const modal = document.getElementById('adherence-modal');
        if (modal) modal.style.display = 'none';
    }

    window.openAdherenceModal = openAdherenceModal;
    window.closeAdherenceModal = closeAdherenceModal;
})(window);
