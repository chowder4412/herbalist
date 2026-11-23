/**
 * HERBALIST AI — VAULT TAB UI
 * Presentation only; patient-profile and recovery data loads remain inline.
 */

(function(window) {
    'use strict';

    function renderVaultTab(tab) {
        const tabProfiles = document.getElementById('vault-tab-profiles');
        const tabTimeline = document.getElementById('vault-tab-timeline');
        const panelProfiles = document.getElementById('vault-panel-profiles');
        const panelTimeline = document.getElementById('vault-panel-timeline');
        const profilesActive = tab === 'profiles';

        if (tabProfiles) {
            tabProfiles.style.background = profilesActive ? 'var(--accent-green)' : 'transparent';
            tabProfiles.style.color = profilesActive ? '#000' : 'var(--text-muted)';
        }
        if (tabTimeline) {
            tabTimeline.style.background = profilesActive ? 'transparent' : 'var(--accent-green)';
            tabTimeline.style.color = profilesActive ? 'var(--text-muted)' : '#000';
        }
        if (panelProfiles) panelProfiles.style.display = profilesActive ? 'flex' : 'none';
        if (panelTimeline) panelTimeline.style.display = profilesActive ? 'none' : 'flex';
        return !profilesActive;
    }

    window.HerbalistVaultTabUI = { renderVaultTab };
})(window);
