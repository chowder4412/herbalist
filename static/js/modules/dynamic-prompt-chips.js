/**
 * HERBALIST AI — DYNAMIC PROMPT CHIPS
 * Renders suggestions only; chat submission remains in the inline lifecycle.
 */

(function(window) {
    'use strict';

    function renderDynamicPromptChips() {
        const container = document.getElementById('dynamic-prompt-chips');
        if (!container) return;

        const hour = new Date().getHours();
        const timeGreeting = hour < 12 ? 'Morning' : (hour < 18 ? 'Afternoon' : 'Evening');
        const promptPool = [
            { text: `🍵 ${timeGreeting} Decoction: Boil 2.0L Ginger & Licorice Tea`, query: `Prepare a 2.0-liter decoction recipe using Ginger and Licorice root with Clark's body weight dosing.` },
            { text: '🫀 Metoprolol & Hawthorn Herb-Drug Interaction', query: `Perform a full pharmacokinetic interaction analysis between Metoprolol and Hawthorn Berry (Crataegus).` },
            { text: '🌿 Curcumin 95% Curcuminoid Anti-Inflammatory Dose', query: `Calculate the optimal daily bioactive dosage of 95% standardized Curcuminoids for systemic joint inflammation.` },
            { text: '💤 Ashwagandha & Passionflower Sleep Protocol', query: `Formulate a clinical sleep phytotherapy regimen combining Ashwagandha (Withania somnifera) and Passionflower.` },
            { text: '🛡️ WHO Hepatic Safety & Pyrrolizidine Check', query: `Verify WHO safety protocols and contraindications for hepatic-sensitive patients.` },
        ];
        container.innerHTML = promptPool.slice(0, 4).map((prompt) => `
            <button onclick="selectDynamicPrompt('${prompt.query.replace(/'/g, "\\'")}')" style="background: rgba(255,255,255,0.04); border: 1px solid var(--pill-border); color: #e2efe6; padding: 8px 14px; border-radius: 20px; font-size: 12px; font-weight: 500; cursor: pointer; transition: all 0.2s ease; display: flex; align-items: center; gap: 6px;" onmouseover="this.style.background='rgba(46,204,113,0.12)'; this.style.borderColor='var(--accent-green)';" onmouseout="this.style.background='rgba(255,255,255,0.04)'; this.style.borderColor='var(--pill-border)';">
                <span>${prompt.text}</span>
            </button>
        `).join('');
    }

    window.HerbalistPromptChips = { renderDynamicPromptChips };
    window.renderDynamicPromptChips = renderDynamicPromptChips;
})(window);
