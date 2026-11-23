/**
 * HERBALIST AI — SCANNER FILE INPUT CONTROL
 * Opens the existing chooser only; scan processing remains inline.
 */

(function(window) {
    'use strict';

    function triggerFileInput() {
        document.getElementById('scanner-file-input')?.click();
    }

    window.triggerFileInput = triggerFileInput;
})(window);
