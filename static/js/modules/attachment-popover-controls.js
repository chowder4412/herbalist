/**
 * HERBALIST AI — ATTACHMENT POPOVER CONTROLS
 * Menu presentation only; upload and scanner actions remain inline.
 */

(function(window) {
    'use strict';

    function toggleAttachmentPopover(show) {
        const menu = document.getElementById('attachment-popover-menu');
        if (!menu) return;

        if (show === false) {
            menu.style.display = 'none';
            return;
        }

        if (show && show.stopPropagation) show.stopPropagation();
        const isVisible = menu.style.display === 'block';
        menu.style.display = isVisible ? 'none' : 'block';
    }

    document.addEventListener('click', (e) => {
        const menu = document.getElementById('attachment-popover-menu');
        const btn = document.getElementById('add-clinical-btn-el');
        if (menu && menu.style.display === 'block') {
            if (!menu.contains(e.target) && (!btn || !btn.contains(e.target))) {
                menu.style.display = 'none';
            }
        }
    });

    window.toggleAttachmentPopover = toggleAttachmentPopover;
})(window);
