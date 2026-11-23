/**
 * HERBALIST AI — DRUG SCANNER MODAL CONTROLS
 * Modal visibility only; OCR, API analysis, and prescription handoff stay inline.
 */

(function(window) {
    'use strict';

    function openDrugScannerModal() {
        const modal = document.getElementById('drug-scanner-modal');
        if (modal) modal.classList.add('active');
    }

    function closeDrugScannerModal() {
        const modal = document.getElementById('drug-scanner-modal');
        if (modal) modal.classList.remove('active');
    }

    window.openDrugScannerModal = openDrugScannerModal;
    window.closeDrugScannerModal = closeDrugScannerModal;
})(window);
