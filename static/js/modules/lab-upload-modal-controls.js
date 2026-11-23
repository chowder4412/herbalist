/**
 * HERBALIST AI — LAB UPLOAD MODAL CONTROLS
 * Opens and closes the existing Lab Upload interface without moving OCR logic.
 */

(function(window) {
    'use strict';

    function openLabUploadModal() {
        document.getElementById('lab-upload-modal')?.classList.add('active');
    }

    function closeLabUploadModal() {
        document.getElementById('lab-upload-modal')?.classList.remove('active');
    }

    window.openLabUploadModal = openLabUploadModal;
    window.closeLabUploadModal = closeLabUploadModal;
})(window);
