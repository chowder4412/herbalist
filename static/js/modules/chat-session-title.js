/**
 * HERBALIST AI — CHAT SESSION TITLE
 * Pure title derivation; session persistence and remote syncing remain inline.
 */

(function(window) {
    'use strict';

    function shortenTitle(value) {
        return value.length > 32 ? `${value.substring(0, 32)}...` : value;
    }

    function deriveSessionTitle(messages, prescription) {
        let title = 'Botanical Consultation';
        const firstUser = (messages || []).find((message) => message.role === 'patient');
        if (firstUser) {
            const cleanText = String(firstUser.html || '')
                .replace(/<[^>]*>?/gm, '')
                .replace(/🎙️|📄/g, '')
                .trim();
            if (cleanText) title = shortenTitle(cleanText);
        }
        if (prescription?.primary_diagnosis) title = shortenTitle(prescription.primary_diagnosis);
        return title;
    }

    window.HerbalistChatSessionTitle = { deriveSessionTitle };
})(window);
