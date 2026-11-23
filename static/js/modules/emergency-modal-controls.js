/**
 * HERBALIST AI — EMERGENCY MODAL CONTROLS
 * Keeps the existing emergency modal dismiss action independent from triage logic.
 */

(function(window) {
    'use strict';

    function closeEmergencyModal() {
        const modal = document.getElementById('emergency-modal');
        if (modal) modal.classList.remove('active');
    }

    function showEmergencyModal(message) {
        const modal = document.getElementById('emergency-modal');
        const body = document.getElementById('emergency-modal-body');
        if (body) body.innerHTML = window.renderMarkdown?.(message) || '';
        if (modal) modal.classList.add('active');
    }

    window.closeEmergencyModal = closeEmergencyModal;
    window.showEmergencyModal = showEmergencyModal;
})(window);
