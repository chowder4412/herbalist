/**
 * HERBALIST AI — RESEARCH MODAL CONTROLS
 * Pure close controls for the existing research-tool interfaces.
 */

(function(window) {
    'use strict';

    function closePharmacopeiaModal() {
        document.getElementById('pharmacopeia-modal')?.classList.remove('active');
    }

    function closeScannerModal() {
        document.getElementById('scanner-modal')?.classList.remove('active');
    }

    function closeRagModal() {
        document.getElementById('rag-modal')?.classList.remove('active');
    }

    window.closePharmacopeiaModal = closePharmacopeiaModal;
    window.closeScannerModal = closeScannerModal;
    window.closeRagModal = closeRagModal;
})(window);
