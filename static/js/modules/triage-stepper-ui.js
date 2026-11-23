/**
 * HERBALIST AI — TRIAGE STEPPER UI
 * Displays supplied SOCRATES progress only; triage logic remains inline.
 */

(function(window) {
    'use strict';

    function updateTriageStepper(currentPhase) {
        let stepperEl = document.getElementById('triage-stepper');
        const chatFeed = document.getElementById('chat-feed');
        if (!stepperEl && chatFeed) {
            stepperEl = document.createElement('div');
            stepperEl.id = 'triage-stepper';
            stepperEl.className = 'triage-stepper';
            stepperEl.innerHTML = `
                <div class="step-item" id="step-onset"><span class="step-num">1</span> Onset</div><div class="step-line"></div>
                <div class="step-item" id="step-duration"><span class="step-num">2</span> Pattern</div><div class="step-line"></div>
                <div class="step-item" id="step-character"><span class="step-num">3</span> Character</div><div class="step-line"></div>
                <div class="step-item" id="step-severity"><span class="step-num">4</span> Severity</div><div class="step-line"></div>
                <div class="step-item" id="step-medications"><span class="step-num">5</span> Meds</div><div class="step-line"></div>
                <div class="step-item" id="step-ready"><span class="step-num">6</span> Rx</div>`;
            chatFeed.parentNode.insertBefore(stepperEl, chatFeed);
        }

        const phasesOrder = ['onset', 'duration', 'character', 'severity', 'medications', 'ready'];
        const currentIdx = phasesOrder.indexOf(currentPhase);
        phasesOrder.forEach((phase, idx) => {
            const itemEl = document.getElementById(`step-${phase}`);
            if (!itemEl) return;
            itemEl.classList.remove('active', 'completed');
            if (idx === currentIdx) itemEl.classList.add('active');
            else if (idx < currentIdx) itemEl.classList.add('completed');
        });
    }

    window.HerbalistTriageStepperUI = { updateTriageStepper };
})(window);
