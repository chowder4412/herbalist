/**
 * HERBALIST AI — TEXTAREA AUTO-EXPAND
 * Input presentation only; keyboard and submission behavior remain inline.
 */

(function(window) {
    'use strict';

    function autoExpandTextarea(el) {
        if (!el) return;
        el.style.height = 'auto';
        el.style.height = Math.min(el.scrollHeight, 120) + 'px';
    }

    window.autoExpandTextarea = autoExpandTextarea;
})(window);
