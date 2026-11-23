/**
 * HERBALIST AI — UTILITY MODAL CONTROLS
 * Small presentation-only modals with no persistence or request behavior.
 */

(function(window) {
    'use strict';

    function openClinicalModal() {
        document.getElementById('clinical-modal').classList.add('active');
    }

    function closeClinicalModal() {
        document.getElementById('clinical-modal').classList.remove('active');
    }

    function openHelpGuideModal() {
        document.getElementById('help-guide-modal')?.classList.add('active');
    }

    function closeHelpGuideModal() {
        document.getElementById('help-guide-modal')?.classList.remove('active');
    }

    window.openClinicalModal = openClinicalModal;
    window.closeClinicalModal = closeClinicalModal;
    window.openHelpGuideModal = openHelpGuideModal;
    window.closeHelpGuideModal = closeHelpGuideModal;
})(window);
