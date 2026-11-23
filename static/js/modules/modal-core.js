/**
 * HERBALIST AI — MODAL CORE
 * Shared close-all behavior used by existing modal entry points.
 */

(function(window) {
    'use strict';

    function closeAllModals() {
        [
            'pharmacopeia-modal',
            'scanner-modal',
            'prescriptions-modal',
            'rag-modal',
            'emergency-modal',
            'clinical-modal',
            'auth-modal',
            'patient-care-toolkit-modal',
            'synergy-lab-modal',
            'vault-recovery-modal',
        ].forEach((id) => {
            const element = document.getElementById(id);
            if (element) element.classList.remove('active');
        });
    }

    window.closeAllModals = closeAllModals;
})(window);
