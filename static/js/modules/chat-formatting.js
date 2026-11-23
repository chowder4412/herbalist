/**
 * HERBALIST AI — CHAT FORMATTING
 * Lightweight, backwards-compatible formatting used by streamed and saved chat.
 */

(function(window) {
    'use strict';

    function renderMarkdown(text) {
        if (!text) return '';
        return text
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    function formatDoctorBubbleHTML(messageText, followUpChips = [], isTriage = false) {
        const renderedMsg = renderMarkdown(messageText || '');
        const chipsHtml = (followUpChips && followUpChips.length > 0) ? renderFollowUpChipsHTML(followUpChips) : '';
        const triageBadge = isTriage ? `<span style="font-size:11px;font-weight:700;color:var(--accent-green);background:rgba(46,204,113,0.15);padding:2px 8px;border-radius:10px;margin-left:6px;">Diagnostic Triage</span>` : '';

        return `
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2ecc71" stroke-width="2"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.4 19 2c1 2 2 4.1 2 9 0 4.9-4 9-9 9z"></path></svg>
                <span style="font-family:'Outfit',sans-serif;font-size:15px;font-weight:700;color:var(--accent-green);">Dr. Herbalist</span>
                ${triageBadge}
            </div>
            <div style="line-height:1.7;font-size:14.5px;color:#f4f9f5;">${renderedMsg}</div>
            ${chipsHtml}
        `;
    }

    window.renderMarkdown = renderMarkdown;
    window.formatDoctorBubbleHTML = formatDoctorBubbleHTML;
})(window);
