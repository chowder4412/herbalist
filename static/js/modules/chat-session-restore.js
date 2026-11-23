/**
 * HERBALIST AI — CHAT SESSION RESTORE
 * Pure cleanup of persisted chat messages before the inline runtime replays them.
 */

(function(window) {
    'use strict';

    function sanitizeRestoredMessages(messages) {
        return (messages || []).filter((message) => {
            if (!message || !message.html) return false;
            const html = String(message.html);
            return !html.includes('typing-dots')
                && !html.includes('analyzing specimen & medical data')
                && !html.includes('id="typing-');
        }).map((message) => {
            if (message.role !== 'doctor' || !message.html) return message;
            const html = String(message.html)
                .replace(/<span id="streaming-badge-[^>]*>[\s\S]*?<\/span>/gi, '')
                .replace(/<span class="pulse-anim"[\s\S]*?<\/span>\s*LIVE STREAM/gi, '')
                .replace(/LIVE STREAM/gi, '');
            return { ...message, html };
        });
    }

    window.HerbalistChatSessionRestore = { sanitizeRestoredMessages };
})(window);
