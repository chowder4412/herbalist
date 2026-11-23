/**
 * HERBALIST AI — AUTH UI CONTROLS
 * Presentation-only controls for the existing authentication form.
 */

(function(window) {
    'use strict';

    const eyeOpen = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;
    const eyeOff = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"></path><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"></path><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"></path><line x1="2" y1="2" x2="22" y2="22"></line></svg>`;

    function toggleAuthPasswordVisibility() {
        const input = document.getElementById('auth-password');
        const button = document.getElementById('btn-toggle-auth-pw');
        if (!input || !button) return;
        if (input.type === 'password') {
            input.type = 'text';
            button.innerHTML = eyeOff;
            button.title = 'Hide password';
        } else {
            input.type = 'password';
            button.innerHTML = eyeOpen;
            button.title = 'Show password';
        }
    }

    function resetAuthModalFields() {
        ['auth-email', 'auth-password', 'auth-name', 'forgot-email-input'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        });
        const errEl = document.getElementById('auth-error-msg');
        if (errEl) { errEl.innerText = ''; errEl.style.display = 'none'; }
        const forgotErr = document.getElementById('forgot-error-msg');
        if (forgotErr) { forgotErr.innerText = ''; forgotErr.style.display = 'none'; }
        const forgotSuccess = document.getElementById('forgot-success-msg');
        if (forgotSuccess) { forgotSuccess.innerText = ''; forgotSuccess.style.display = 'none'; }
    }

    function switchAuthTab(tab) {
        window.currentAuthTab = tab;
        resetAuthModalFields();
        const tabLogin = document.getElementById('tab-login');
        const tabRegister = document.getElementById('tab-register');
        const nameGroup = document.getElementById('group-fullname');
        const forgotLink = document.getElementById('forgot-password-link');
        const titleEl = document.getElementById('auth-modal-title');
        const submitBtn = document.getElementById('auth-submit-btn');

        document.getElementById('auth-form-container').style.display = 'block';
        const forgotContainer = document.getElementById('forgot-form-container');
        if (forgotContainer) forgotContainer.style.display = 'none';
        const verifyContainer = document.getElementById('verify-email-container');
        if (verifyContainer) verifyContainer.style.display = 'none';

        if (tab === 'login') {
            tabLogin.style.background = 'var(--accent-green)';
            tabLogin.style.color = '#000';
            tabRegister.style.background = 'transparent';
            tabRegister.style.color = 'var(--text-muted)';
            if (nameGroup) nameGroup.style.display = 'none';
            if (forgotLink) forgotLink.style.display = 'inline-block';
            titleEl.innerHTML = 'Sign In to Herbalist AI';
            submitBtn.innerText = 'Sign In to Account';
        } else {
            tabRegister.style.background = 'var(--accent-green)';
            tabRegister.style.color = '#000';
            tabLogin.style.background = 'transparent';
            tabLogin.style.color = 'var(--text-muted)';
            if (nameGroup) nameGroup.style.display = 'block';
            if (forgotLink) forgotLink.style.display = 'none';
            titleEl.innerHTML = 'Create Account';
            submitBtn.innerText = 'Create Account';
        }
    }

    function openAuthModal(defaultTab = 'login') {
        resetAuthModalFields();
        switchAuthTab(defaultTab);
        const modal = document.getElementById('auth-modal');
        if (modal) modal.classList.add('active');
    }

    function closeAuthModal() {
        const modal = document.getElementById('auth-modal');
        if (modal) modal.classList.remove('active');
        resetAuthModalFields();
        document.getElementById('auth-form-container').style.display = 'block';
        const forgotContainer = document.getElementById('forgot-form-container');
        if (forgotContainer) forgotContainer.style.display = 'none';
        const verifyContainer = document.getElementById('verify-email-container');
        if (verifyContainer) verifyContainer.style.display = 'none';
    }

    window.toggleAuthPasswordVisibility = toggleAuthPasswordVisibility;
    window.resetAuthModalFields = resetAuthModalFields;
    window.switchAuthTab = switchAuthTab;
    window.openAuthModal = openAuthModal;
    window.closeAuthModal = closeAuthModal;
    window.currentAuthTab = window.currentAuthTab || 'login';
})(window);
