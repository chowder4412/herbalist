/**
 * HERBALIST AI — SAVED PRESCRIPTIONS MODAL CONTROLS
 * Opens the existing library UI while leaving its data operations unchanged.
 */

(function(window) {
    'use strict';

    function openPrescriptionsModal() {
        window.closeAllModals?.();
        const modal = document.getElementById('prescriptions-modal');
        if (modal) {
            modal.classList.add('active');
            window.loadSavedPrescriptions?.();
        }
    }

    function closePrescriptionsModal() {
        document.getElementById('prescriptions-modal')?.classList.remove('active');
    }

    window.openPrescriptionsModal = openPrescriptionsModal;
    window.closePrescriptionsModal = closePrescriptionsModal;
})(window);
