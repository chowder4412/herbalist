/**
 * ═══════════════════════════════════════════════════════════════════
 * HERBALIST AI — AUTHENTICATION & HEALTH VAULT CONTROLLER
 * Strict Auth Guard, User Profile Rendering, Health Vault Storage,
 * and Zero-Guest Mode Enforcement.
 * ═══════════════════════════════════════════════════════════════════
 */

(function(window) {
    'use strict';

    function getActiveAuthToken() {
        try {
            return localStorage.getItem('herbalist_jwt_token') ||
                   localStorage.getItem('herbalist_token') ||
                   localStorage.getItem('herbalist_auth_token') || null;
        } catch(e) {
            return null;
        }
    }

    function getStoredUser() {
        try {
            const raw = localStorage.getItem('herbalist_user') ||
                        localStorage.getItem('herbalist_user_profile');
            return raw ? JSON.parse(raw) : null;
        } catch(e) {
            return null;
        }
    }

    /**
     * Strict Authentication Guard:
     * Immediately bounces unauthenticated visitors from /app to /auth
     */
    function enforceAuthGuard() {
        const isApp = window.location.pathname.includes('/app') ||
                      window.location.pathname.includes('/consult') ||
                      window.location.pathname.endsWith('index.html');

        if (!isApp) return true;

        const user = getStoredUser();
        const token = getActiveAuthToken();

        if (!user && !token) {
            console.warn('[Herbalist AI Auth Guard] Unauthenticated access to dashboard blocked. Redirecting to /auth...');
            const returnUrl = encodeURIComponent(window.location.pathname + window.location.search);
            window.location.replace('/auth?redirect=' + returnUrl);
            return false;
        }
        return true;
    }

    // Run auth check immediately
    enforceAuthGuard();

    function updateSidebarUserProfile() {
        const user = getStoredUser();
        const avatarEl = document.getElementById('user-avatar-initials');
        const nameEl = document.getElementById('user-display-name');
        const statusEl = document.getElementById('user-account-status');
        const actionBtn = document.getElementById('user-auth-action-btn');
        const heroTitle = document.getElementById('hero-title-text');

        if (user && (user.email || user.full_name || user.displayName)) {
            const name = user.full_name || user.displayName || user.email.split('@')[0];
            const initials = (name.replace(/[^a-zA-Z]/g, '').slice(0, 2) || 'PT').toUpperCase();

            if (avatarEl) {
                avatarEl.innerText = initials;
                avatarEl.style.background = 'var(--accent-green, #2ecc71)';
                avatarEl.style.color = '#000';
                avatarEl.style.fontWeight = '700';
            }
            if (nameEl) nameEl.innerText = name;
            if (statusEl) statusEl.innerText = user.email || 'Verified Patient';
            if (actionBtn) {
                actionBtn.title = 'Sign Out';
                actionBtn.onclick = (e) => {
                    e.stopPropagation();
                    promptSignOut();
                };
                actionBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#e74c3c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>`;
            }
            if (heroTitle) {
                heroTitle.innerText = `What can I help with, ${name}?`;
            }
        }
    }

    async function promptSignOut() {
        const user = getStoredUser();
        const email = user ? (user.email || 'your account') : 'your account';

        let confirmed = true;
        if (typeof window.showCustomConfirm === 'function') {
            confirmed = await window.showCustomConfirm({
                title: 'Sign Out of Herbalist AI?',
                message: `Are you sure you want to sign out (${email})? You will need to log back in to access your consultations and Health Vault.`,
                confirmText: 'Sign Out',
                cancelText: 'Cancel',
                isDestructive: true,
                icon: '🚪'
            });
        }

        if (confirmed) {
            try {
                localStorage.removeItem('herbalist_user');
                localStorage.removeItem('herbalist_user_profile');
                localStorage.removeItem('herbalist_jwt_token');
                localStorage.removeItem('herbalist_token');
                localStorage.removeItem('herbalist_auth_token');
                localStorage.removeItem('herbalist_active_session_id');

                if (typeof window.firebase !== 'undefined' && window.firebase.auth) {
                    await window.firebase.auth().signOut();
                }
            } catch(e){}

            if (typeof window.showToast === 'function') {
                window.showToast('Signed out successfully. Redirecting to welcome portal...', 'info', 1500);
            }
            setTimeout(() => {
                window.location.replace('/welcome');
            }, 500);
        }
    }

    function handleProfileClick() {
        promptSignOut();
    }

    function saveCurrentPrescription(rxData) {
        if (!rxData) {
            if (typeof window.showToast === 'function') {
                window.showToast('No active prescription to save.', 'warning');
            }
            return;
        }

        try {
            const saved = JSON.parse(localStorage.getItem('herbalist_saved_prescriptions') || '[]');
            const newEntry = {
                id: 'RX_' + Date.now(),
                timestamp: new Date().toISOString(),
                diagnosis: rxData.primary_diagnosis || 'Prescribed Botanical Formulation',
                formulation_name: rxData.formulation ? rxData.formulation.formulation_name : 'Herbal Remedy',
                payload: rxData
            };

            saved.unshift(newEntry);
            localStorage.setItem('herbalist_saved_prescriptions', JSON.stringify(saved.slice(0, 50)));

            if (typeof window.showToast === 'function') {
                window.showToast('Prescription saved to your Health Vault! 📁', 'success');
            }
        } catch(e) {
            console.error("Save prescription error:", e);
        }
    }

    function openVaultRecoveryModal() {
        const modal = document.getElementById('recovery-tracker-modal');
        if (modal) modal.classList.add('active');
    }

    function closeVaultRecoveryModal() {
        const modal = document.getElementById('recovery-tracker-modal');
        if (modal) modal.classList.remove('active');
    }

    // Attach to window
    window.getActiveAuthToken = getActiveAuthToken;
    window.getStoredUser = getStoredUser;
    window.enforceAuthGuard = enforceAuthGuard;
    window.updateSidebarUserProfile = updateSidebarUserProfile;
    window.promptSignOut = promptSignOut;
    window.saveCurrentPrescription = saveCurrentPrescription;
    window.handleProfileClick = handleProfileClick;
    window.openVaultRecoveryModal = openVaultRecoveryModal;
    window.closeVaultRecoveryModal = closeVaultRecoveryModal;

    // Run UI update on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', updateSidebarUserProfile);
    } else {
        updateSidebarUserProfile();
    }

})(window);
