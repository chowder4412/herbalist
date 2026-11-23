/**
 * HERBALIST AI — EVIDENCE FORMATTING
 * Formats inline evidence markers while preserving the existing drawer map.
 */

(function(window) {
    'use strict';

    function formatTextWithCitations(text, citationsList = []) {
        if (!text) return '';

        const citationMap = window.activeEvidenceCitationsMap || (window.activeEvidenceCitationsMap = {});
        if (citationsList && citationsList.length > 0) {
            citationsList.forEach((citation, index) => {
                const key = citation.id || `cit_${index + 1}`;
                citationMap[key] = citation;
            });
        }

        return text.replace(/\[(\d+)\]/g, (match, number) => {
            const index = parseInt(number, 10) - 1;
            const citation = (citationsList && citationsList[index]) ? citationsList[index] : null;
            const citationId = citation ? citation.id : `cit_${number}`;
            if (citation) citationMap[citationId] = citation;
            const title = citation ? `${citation.title} (${citation.journal})` : `PubMed Citation ${number}`;
            return `<button class="citation-pill" onclick="openEvidenceDrawer('${citationId}')" title="${title.replace(/"/g, '&quot;')}">🔬 [${number}]</button>`;
        });
    }

    function closeEvidenceDrawer() {
        const drawer = document.getElementById('evidence-drawer');
        const overlay = document.getElementById('evidence-drawer-overlay');
        if (drawer) drawer.classList.remove('open');
        if (overlay) overlay.classList.remove('open');
    }

    window.formatTextWithCitations = formatTextWithCitations;
    window.closeEvidenceDrawer = closeEvidenceDrawer;
})(window);
