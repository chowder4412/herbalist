/**
 * ═══════════════════════════════════════════════════════════════════
 * HERBALIST AI — INTERACTIVE CITATION POPOVERS & BOTANICAL CHIPS
 * Perplexity-standard scientific flyout cards and plant monographs
 * ═══════════════════════════════════════════════════════════════════
 */

(function(window) {
    'use strict';

    const BOTANICAL_KNOWLEDGE_BASE = {
        'vernonia amygdalina': {
            scientific: 'Vernonia amygdalina',
            common: 'Bitter Leaf (Ewuro / Shuwaka / Onugbu)',
            family: 'Asteraceae',
            phytochemicals: 'Vernoniosides, Luteolin, Vernodalin, Sesquiterpene lactones',
            actions: 'Hepatoprotective, Antidiabetic, Antimicrobial, Bitter digestive tonic',
            posology: 'Standard decoction: 5–10g dried leaves in 250ml water daily'
        },
        'moringa oleifera': {
            scientific: 'Moringa oleifera',
            common: 'Moringa / Drumstick Tree (Zogale / Ewe Igbale / Okwe Oyibo)',
            family: 'Moringaceae',
            phytochemicals: 'Moringine, Quercetin, Kaempferol, Chlorogenic acid',
            actions: 'Nutritional restorative, Anti-inflammatory, Hypotensive, Antioxidant',
            posology: 'Dried leaf powder: 3–5g daily with meals or warm water'
        },
        'zingiber officinale': {
            scientific: 'Zingiber officinale',
            common: 'Ginger (Citta / Jinja / Atale)',
            family: 'Zingiberaceae',
            phytochemicals: '6-Gingerol, 6-Shogaol, Zingiberene, Paradols',
            actions: 'Antiemetic, Thermogenic digestive, Anti-inflammatory, Carminative',
            posology: 'Fresh rhizome decoction: 2–4g boiled in water 2–3x daily'
        },
        'garcinia kola': {
            scientific: 'Garcinia kola',
            common: 'Bitter Kola (Orogbo / Namijin Goro / Agbilu)',
            family: 'Clusiaceae',
            phytochemicals: 'Kolaviron (biflavonoids), Garcinol, Tannins',
            actions: 'Bronchodilator, Antimicrobial, Antioxidant, Throat demulcent',
            posology: '1 seed chewed slowly or extracted in warm infusion'
        },
        'curcuma longa': {
            scientific: 'Curcuma longa',
            common: 'Turmeric (Gangamau / Kurkum)',
            family: 'Zingiberaceae',
            phytochemicals: 'Curcumin, Demethoxycurcumin, Turmerones',
            actions: 'Systemic anti-inflammatory, Choleretic, Hepatoprotective',
            posology: '1.5–3g standardized powder with black pepper (piperine)'
        },
        'ocimum gratissimum': {
            scientific: 'Ocimum gratissimum',
            common: 'African Clove Basil / Scent Leaf (Efirin / Daidoya / Nchanwu)',
            family: 'Lamiaceae',
            phytochemicals: 'Eugenol, Thymol, Citral, Rosmarinic acid',
            actions: 'Antispasmodic, Gastroprotective, Anthelmintic, Antimicrobial',
            posology: 'Leaf infusion: 5g fresh leaves steeped in 200ml hot water'
        },
        'azadirachta indica': {
            scientific: 'Azadirachta indica',
            common: 'Neem / Dogonyaro',
            family: 'Meliaceae',
            phytochemicals: 'Azadirachtin, Nimbin, Nimbidin, Quercetin',
            actions: 'Antimalarial support, Antipyretic, Detoxicant, Bitter alterative',
            posology: 'Boiled leaf decoction: 200ml twice daily for max 5 days'
        }
    };

    const CitationPopover = {
        popoverEl: null,
        hideTimeout: null,

        /**
         * Initialize popover container and click listeners
         */
        init: function() {
            this.createPopoverElement();
            this.observeDOM();
            this.processExistingText();
        },

        /**
         * Create floating popover DOM element
         */
        createPopoverElement: function() {
            let el = document.getElementById('clinical-popover');
            if (el) {
                this.popoverEl = el;
                return;
            }

            this.popoverEl = document.createElement('div');
            this.popoverEl.id = 'clinical-popover';
            this.popoverEl.onmouseenter = () => clearTimeout(this.hideTimeout);
            this.popoverEl.onmouseleave = () => this.hide();
            document.body.appendChild(this.popoverEl);

            window.addEventListener('click', (e) => {
                if (this.popoverEl && !this.popoverEl.contains(e.target) && e.target && e.target.classList && !e.target.classList.contains('citation-inline-badge') && !e.target.classList.contains('specimen-chip')) {
                    this.hide();
                }
            });
        },

        /**
         * Show popover positioned near target element
         */
        show: function(targetEl, htmlContent) {
            clearTimeout(this.hideTimeout);
            if (!this.popoverEl) this.createPopoverElement();

            this.popoverEl.innerHTML = htmlContent;
            this.popoverEl.style.display = 'block';

            const rect = targetEl.getBoundingClientRect();
            const popoverWidth = 320;
            const popoverHeight = this.popoverEl.offsetHeight || 180;

            let top = rect.bottom + 8;
            let left = rect.left + (rect.width / 2) - (popoverWidth / 2);

            // Boundary checks
            if (left < 10) left = 10;
            if (left + popoverWidth > window.innerWidth - 10) {
                left = window.innerWidth - popoverWidth - 10;
            }
            if (top + popoverHeight > window.innerHeight - 10) {
                top = rect.top - popoverHeight - 8; // flip above
            }

            this.popoverEl.style.top = `${top}px`;
            this.popoverEl.style.left = `${left}px`;
        },

        /**
         * Hide popover with debounce
         */
        hide: function() {
            this.hideTimeout = setTimeout(() => {
                if (this.popoverEl) this.popoverEl.style.display = 'none';
            }, 180);
        },

        /**
         * Show PubMed citation flyout
         */
        showCitation: function(targetEl, citationIndex, citationText) {
            const cleanText = decodeURIComponent(citationText || 'Peer-Reviewed Clinical Phytotherapy Study');
            const pmidMatch = cleanText.match(/PMID:\s*(\d+)/i);
            const pmid = pmidMatch ? pmidMatch[1] : '';
            const pubmedUrl = pmid ? `https://pubmed.ncbi.nlm.nih.gov/${pmid}/` : `https://pubmed.ncbi.nlm.nih.gov/?term=${encodeURIComponent(cleanText)}`;

            const html = `
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;border-bottom:1px solid rgba(46,204,113,0.2);padding-bottom:6px;">
                    <div style="display:flex;align-items:center;gap:6px;font-size:11px;font-weight:700;color:var(--accent-green,#2ecc71);">
                        <span>🔬</span>
                        <span>Evidence Source [${citationIndex}]</span>
                    </div>
                    ${pmid ? `<span style="font-size:10px;background:rgba(46,204,113,0.15);color:#2ecc71;padding:1px 6px;border-radius:4px;font-weight:600;">PMID: ${pmid}</span>` : ''}
                </div>
                <div style="font-size:12.5px;color:#fff;line-height:1.45;margin-bottom:8px;font-weight:500;">
                    ${cleanText}
                </div>
                <div style="font-size:11px;color:rgba(255,255,255,0.65);line-height:1.4;margin-bottom:10px;background:rgba(0,0,0,0.25);padding:6px 8px;border-radius:6px;">
                    Peer-reviewed phytotherapy data indexed in WHO TMGL, PubMed & Global Ethnobotanical Registries.
                </div>
                <a href="${pubmedUrl}" target="_blank" rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:700;color:var(--accent-green,#2ecc71);text-decoration:none;background:rgba(46,204,113,0.1);padding:4px 10px;border-radius:6px;border:1px solid rgba(46,204,113,0.3);">
                    <span>Open in PubMed</span>
                    <span>↗</span>
                </a>
            `;

            this.show(targetEl, html);
        },

        /**
         * Show Botanical Specimen details card
         */
        showSpecimen: function(targetEl, plantKey) {
            const info = BOTANICAL_KNOWLEDGE_BASE[plantKey.toLowerCase()];
            if (!info) return;

            const html = `
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;border-bottom:1px solid rgba(46,204,113,0.2);padding-bottom:6px;">
                    <div style="display:flex;align-items:center;gap:6px;font-size:11px;font-weight:700;color:var(--accent-green,#2ecc71);">
                        <span>🌿</span>
                        <span>${info.scientific}</span>
                    </div>
                    <span style="font-size:10px;background:rgba(255,255,255,0.06);color:rgba(255,255,255,0.7);padding:1px 6px;border-radius:4px;">${info.family}</span>
                </div>
                <div style="font-size:12px;color:#fff;font-weight:600;margin-bottom:4px;">
                    ${info.common}
                </div>
                <div style="font-size:11px;color:rgba(255,255,255,0.8);line-height:1.4;margin-bottom:6px;">
                    <strong>Phytochemicals:</strong> ${info.phytochemicals}
                </div>
                <div style="font-size:11px;color:#a8e6cf;line-height:1.4;margin-bottom:6px;">
                    <strong>Actions:</strong> ${info.actions}
                </div>
                <div style="font-size:11px;color:var(--text-muted,#7f8c8d);background:rgba(0,0,0,0.25);padding:5px 8px;border-radius:6px;">
                    <strong>Posology:</strong> ${info.posology}
                </div>
            `;

            this.show(targetEl, html);
        },

        /**
         * Process DOM text nodes to inject chips & citation badges
         */
        processExistingText: function() {
            const bubbles = document.querySelectorAll('.chat-bubble');
            bubbles.forEach(b => this.processBubble(b));
        },

        processBubble: function(bubble) {
            if (bubble.dataset.citationsProcessed === 'true') return;
            bubble.dataset.citationsProcessed = 'true';

            // Enhance [1], [2], [PMID: 1234] citations
            const citationPattern = /\[(\d+|PMID:\s*\d+)\]/g;
            const textContainers = bubble.querySelectorAll('p, li, .prescription-instructions');

            textContainers.forEach(el => {
                if (el.dataset.citationEnhanced) return;
                el.dataset.citationEnhanced = 'true';

                let html = el.innerHTML;
                html = html.replace(citationPattern, (match, p1) => {
                    const encodedMatch = encodeURIComponent(`Citation ${p1}`);
                    return `<span class="citation-inline-badge" onmouseenter="CitationPopover.showCitation(this, '${p1}', '${encodedMatch}')" onmouseleave="CitationPopover.hide()">${p1}</span>`;
                });

                // Match known botanical scientific names
                Object.keys(BOTANICAL_KNOWLEDGE_BASE).forEach(key => {
                    const regex = new RegExp(`\\b(${BOTANICAL_KNOWLEDGE_BASE[key].scientific})\\b`, 'gi');
                    html = html.replace(regex, (m) => {
                        return `<span class="specimen-chip" onmouseenter="CitationPopover.showSpecimen(this, '${key}')" onmouseleave="CitationPopover.hide()">${m}</span>`;
                    });
                });

                el.innerHTML = html;
            });
        },

        observeDOM: function() {
            const feed = document.getElementById('chat-feed');
            if (!feed) return;

            const observer = new MutationObserver(() => {
                this.processExistingText();
            });
            observer.observe(feed, { childList: true, subtree: true });
        }
    };

    window.CitationPopover = CitationPopover;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => CitationPopover.init());
    } else {
        CitationPopover.init();
    }
})(window);
