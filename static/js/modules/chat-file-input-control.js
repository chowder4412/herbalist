/**
 * HERBALIST AI — CHAT FILE INPUT CONTROL
 * Opens the existing chooser only; attachment state and processing stay inline.
 */

(function(window) {
    'use strict';

    function triggerChatFileUpload() {
        document.getElementById('chat-file-upload')?.click();
    }

    window.triggerChatFileUpload = triggerChatFileUpload;
})(window);
