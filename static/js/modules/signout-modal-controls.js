/**
 * HERBALIST AI — SIGN-OUT MODAL CONTROLS
 * Dismissal only; account lookup and sign-out behavior remain inline.
 */

(function(window) {
    'use strict';

    function closeSignOutModal() {
        const modal = document.getElementById('signout-confirm-modal');
        if (modal) modal.classList.remove('active');
    }

    window.closeSignOutModal = closeSignOutModal;
})(window);
