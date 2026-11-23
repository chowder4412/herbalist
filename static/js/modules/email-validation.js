/**
 * HERBALIST AI — EMAIL VALIDATION
 * Pure input validation; authentication requests remain inline.
 */

(function(window) {
    'use strict';

    function isValidEmail(email) {
        return /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email);
    }

    window.isValidEmail = isValidEmail;
})(window);
