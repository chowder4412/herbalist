/**
 * HERBALIST AI — DISCLAIMER BANNER CONTROL
 * Preserves the existing dismissal preference key.
 */

(function(window) {
    'use strict';

    function dismissDisclaimer() {
        const banner = document.getElementById('disclaimer-banner');
        if (banner) banner.style.display = 'none';
        try { localStorage.setItem('herbalist_disclaimer_dismissed', 'true'); } catch (e) {}
    }

    window.dismissDisclaimer = dismissDisclaimer;
})(window);
