/**
 * HERBALIST AI — CARE SUITE CONTROLS
 * Public entry points for existing Synergy Lab and Recovery/Vault Care Suite tabs.
 */

(function(window) {
    'use strict';

    function openSynergyLabModal(condition = null) {
        window.openPatientCareToolkitModal?.('synergy');
        const modal = document.getElementById('patient-care-toolkit-modal');
        if (modal) {
            modal.classList.add('open');
            modal.classList.add('active');
        }
        if (condition) window.loadSynergyComparison?.(condition);
    }

    function closeSynergyLabModal() {
        window.closePatientCareToolkitModal?.();
        const modal = document.getElementById('patient-care-toolkit-modal');
        if (modal) {
            modal.classList.remove('open');
            modal.classList.remove('active');
        }
    }

    function openVaultRecoveryModal() {
        window.openPatientCareToolkitModal?.('recovery');
        const modal = document.getElementById('patient-care-toolkit-modal');
        if (modal) {
            modal.classList.add('open');
            modal.classList.add('active');
        }
    }

    function closeVaultRecoveryModal() {
        window.closePatientCareToolkitModal?.();
        const modal = document.getElementById('patient-care-toolkit-modal');
        if (modal) {
            modal.classList.remove('open');
            modal.classList.remove('active');
        }
    }

    window.openSynergyLabModal = openSynergyLabModal;
    window.closeSynergyLabModal = closeSynergyLabModal;
    window.openVaultRecoveryModal = openVaultRecoveryModal;
    window.closeVaultRecoveryModal = closeVaultRecoveryModal;
})(window);
