/**
 * HERBALIST AI — PROFILE FORM CONTROLS
 * Presentation-only toggle; profile requests and saved records remain inline.
 */

(function(window) {
    'use strict';

    function toggleAddProfileForm() {
        const form = document.getElementById('add-profile-form-container');
        if (form) form.style.display = (form.style.display === 'none' || !form.style.display) ? 'block' : 'none';
    }

    window.toggleAddProfileForm = toggleAddProfileForm;
})(window);
