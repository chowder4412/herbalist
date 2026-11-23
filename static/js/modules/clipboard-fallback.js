/**
 * HERBALIST AI — CLIPBOARD FALLBACK
 * Copies supplied text only; prescription formatting and data remain inline.
 */

(function(window) {
    'use strict';

    function fallbackCopy(text, btnEl) {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        try {
            document.execCommand('copy');
            if (btnEl) {
                const origHTML = btnEl.innerHTML;
                btnEl.innerHTML = '<span style="color:#2ecc71;font-weight:800;">✓ Copied!</span>';
                setTimeout(() => { btnEl.innerHTML = origHTML; }, 2500);
            }
            window.showToast('📋 Full prescription copied to clipboard!', 'success');
        } catch (e) {
            window.showToast('Unable to copy automatically. Please select text manually.', 'warning');
        }
        document.body.removeChild(ta);
    }

    window.HerbalistClipboard = { fallbackCopy };
})(window);
