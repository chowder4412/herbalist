/**
 * HERBALIST AI — FORGOT PASSWORD UI
 * Form transition only; validation and reset-email requests remain inline.
 */

(function(window) {
    'use strict';

    function openForgotPasswordStep(e) {
        if (e) e.preventDefault();
        document.getElementById('auth-form-container').style.display = 'none';
        const forgotContainer = document.getElementById('forgot-form-container');
        if (forgotContainer) forgotContainer.style.display = 'block';
        const emailInput = document.getElementById('auth-email');
        const forgotInput = document.getElementById('forgot-email-input');
        if (emailInput && emailInput.value && forgotInput) forgotInput.value = emailInput.value;
    }

    window.openForgotPasswordStep = openForgotPasswordStep;
})(window);
