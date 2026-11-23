/**
 * HERBALIST AI — SAFETY CHECKER MODAL CONTROLS
 * Presentation controls only; safety-search requests remain in index.html.
 */

(function(window) {
    'use strict';

    function openSafetyCheckerModal(defaultTab = 'hdi') {
        switchSafetyTab(defaultTab);
        const modal = document.getElementById('safety-checker-modal');
        if (modal) modal.classList.add('active');
    }

    function closeSafetyCheckerModal() {
        const modal = document.getElementById('safety-checker-modal');
        if (modal) modal.classList.remove('active');
    }

    function switchSafetyTab(tab) {
        const tabHdi = document.getElementById('safety-tab-hdi');
        const tabSub = document.getElementById('safety-tab-sub');
        const panelHdi = document.getElementById('safety-panel-hdi');
        const panelSub = document.getElementById('safety-panel-sub');

        if (tab === 'hdi') {
            tabHdi.style.background = 'var(--accent-green)';
            tabHdi.style.color = '#000';
            tabSub.style.background = 'transparent';
            tabSub.style.color = 'var(--text-muted)';
            panelHdi.style.display = 'flex';
            panelSub.style.display = 'none';
        } else {
            tabSub.style.background = 'var(--accent-green)';
            tabSub.style.color = '#000';
            tabHdi.style.background = 'transparent';
            tabHdi.style.color = 'var(--text-muted)';
            panelSub.style.display = 'flex';
            panelHdi.style.display = 'none';
        }
    }

    window.openSafetyCheckerModal = openSafetyCheckerModal;
    window.closeSafetyCheckerModal = closeSafetyCheckerModal;
    window.switchSafetyTab = switchSafetyTab;
})(window);
