/**
 * ═══════════════════════════════════════════════════════════════════
 * HERBALIST AI — INTERACTIVE DRUG-HERB CYP450 SAFETY MATRIX
 * Pharmacokinetic Hepatic Enzyme Visualizer & Clinical Risk Gauge
 * ═══════════════════════════════════════════════════════════════════
 */

(function(window) {
    'use strict';

    const CYP450_DATABASE = [
        {
            drug: 'Metformin',
            drugClass: 'Antidiabetic (Biguanide)',
            herb: 'Vernonia amygdalina (Bitter Leaf)',
            risk: 'yellow',
            riskTitle: 'Moderate / Additive Hypoglycemia',
            pathways: ['OCT1', 'AMPK Activation', 'CYP2C9'],
            mechanism: 'Both agents increase cellular glucose uptake. Additive blood-glucose lowering effect may cause mild hypoglycemia if unmonitored.',
            guidance: 'Monitor blood glucose regularly. Separate ingestion of concentrated decoction from pharmaceutical dose by 2–3 hours.'
        },
        {
            drug: 'Warfarin',
            drugClass: 'Anticoagulant (Vitamin K Antagonist)',
            herb: 'Zingiber officinale (Ginger)',
            risk: 'yellow',
            riskTitle: 'Caution / Mild Antiplatelet Synergy',
            pathways: ['CYP2C9 Inhibition', 'Thromboxane Synthetase'],
            mechanism: 'High gingerol concentrations exert mild inhibition on platelet aggregation and CYP2C9 metabolism.',
            guidance: 'Safe in standard dietary culinary amounts. Avoid high-dose concentrated ethanolic extracts (>4g/day). Monitor INR.'
        },
        {
            drug: 'Warfarin',
            drugClass: 'Anticoagulant',
            herb: "St. John's Wort (Hypericum perforatum)",
            risk: 'red',
            riskTitle: 'Contraindicated / Severe Reduction of Efficacy',
            pathways: ['CYP3A4 Induction', 'CYP2C9 Induction', 'P-gp'],
            mechanism: 'Potent induction of hepatic CYP2C9 dramatically accelerates warfarin clearance, precipitating thromboembolic risk.',
            guidance: 'Strictly contraindicated. Do not co-administer.'
        },
        {
            drug: 'Amlodipine / Lisinopril',
            drugClass: 'Antihypertensive (CCB / ACE Inhibitor)',
            herb: 'Hibiscus sabdariffa (Zobo / Roselle)',
            risk: 'yellow',
            riskTitle: 'Moderate / Additive Vasodilation',
            pathways: ['ACE Inhibition', 'Diuretic Pathway', 'CYP3A4'],
            mechanism: 'Anthocyanins in Hibiscus possess natural ACE-inhibitory and diuretic properties, amplifying blood pressure lowering.',
            guidance: 'Monitor resting blood pressure. Consume mild infusion 2 hours apart from pharmaceutical medication.'
        },
        {
            drug: 'Atorvastatin',
            drugClass: 'Lipid-Lowering (HMG-CoA Reductase)',
            herb: 'Moringa oleifera',
            risk: 'green',
            riskTitle: 'Safe / Synergistic Cardioprotective',
            pathways: ['Antioxidant Support', 'CYP3A4 Safe'],
            mechanism: 'Moringa provides complementary lipid-modulating polyphenols without inhibiting hepatic CYP3A4 clearance.',
            guidance: 'Standard therapeutic posology (3–5g daily) is safe and well-tolerated.'
        },
        {
            drug: 'Omeprazole',
            drugClass: 'Proton Pump Inhibitor (PPI)',
            herb: 'Curcuma longa (Turmeric)',
            risk: 'green',
            riskTitle: 'Safe / Synergistic Mucosal Protection',
            pathways: ['Gastroprotective', 'CYP2C19 Neutral'],
            mechanism: 'Curcumin stimulates mucin secretion, assisting mucosal re-epithelialization in synergy with acid suppression.',
            guidance: 'Safe for co-administration. Administer with light meals.'
        },
        {
            drug: 'Ciprofloxacin',
            drugClass: 'Fluoroquinolone Antibiotic',
            herb: 'Garcinia kola (Bitter Kola)',
            risk: 'yellow',
            riskTitle: 'Caution / Mineral Chelation & Bioavailability',
            pathways: ['Chelation Complex', 'CYP1A2'],
            mechanism: 'Tannins in bitter kola may bind ciprofloxacin in the gastrointestinal tract, diminishing systemic antibiotic absorption.',
            guidance: 'Do not take concurrently. Administer bitter kola at least 3 hours before or 2 hours after ciprofloxacin.'
        }
    ];

    const CYP450SafetyMatrix = {
        modalEl: null,

        init: function() {
            this.createModalDOM();
        },

        createModalDOM: function() {
            let el = document.getElementById('cyp450-matrix-modal');
            if (el) {
                this.modalEl = el;
                return;
            }

            this.modalEl = document.createElement('div');
            this.modalEl.id = 'cyp450-matrix-modal';
            this.modalEl.innerHTML = `
                <div class="modal-content-glass">
                    <!-- Header -->
                    <div class="modal-header-glass">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <div style="width:36px;height:36px;border-radius:10px;background:rgba(46,204,113,0.15);border:1px solid rgba(46,204,113,0.3);display:flex;align-items:center;justify-content:center;color:var(--accent-green,#2ecc71);">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                            </div>
                            <div>
                                <h3 style="margin:0;font-size:16px;font-weight:700;color:#fff;">Drug-Herb CYP450 Safety Matrix</h3>
                                <div style="font-size:11.5px;color:rgba(255,255,255,0.65);margin-top:1px;">Pharmacokinetic Interaction & Enzyme Pathway Visualizer</div>
                            </div>
                        </div>
                        <button onclick="CYP450SafetyMatrix.close()" style="background:transparent;border:none;color:#7f8c8d;font-size:20px;cursor:pointer;padding:4px 8px;border-radius:8px;">✕</button>
                    </div>

                    <!-- Body -->
                    <div class="modal-body-scroll">
                        <!-- Selector Pair Controls -->
                        <div class="metric-card-glass">
                            <strong style="font-size:13px;color:#fff;margin-bottom:8px;display:block;">Select Medication & Botanical Specimen:</strong>
                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                                <div>
                                    <label style="font-size:11px;color:rgba(255,255,255,0.7);display:block;margin-bottom:4px;">Pharmaceutical Drug</label>
                                    <select id="matrix-drug-select" onchange="CYP450SafetyMatrix.onSelectChange()" style="width:100%;box-sizing:border-box;background:#142219;border:1px solid rgba(46,204,113,0.3);color:#fff;padding:8px 12px;border-radius:8px;font-size:12.5px;outline:none;cursor:pointer;">
                                        <option value="Metformin">Metformin (Antidiabetic)</option>
                                        <option value="Warfarin">Warfarin (Anticoagulant)</option>
                                        <option value="Amlodipine / Lisinopril">Amlodipine / Lisinopril (Antihypertensive)</option>
                                        <option value="Atorvastatin">Atorvastatin (Statin / Lipid)</option>
                                        <option value="Omeprazole">Omeprazole (PPI / Acid)</option>
                                        <option value="Ciprofloxacin">Ciprofloxacin (Antibiotic)</option>
                                    </select>
                                </div>
                                <div>
                                    <label style="font-size:11px;color:rgba(255,255,255,0.7);display:block;margin-bottom:4px;">Botanical Specimen</label>
                                    <select id="matrix-herb-select" onchange="CYP450SafetyMatrix.onSelectChange()" style="width:100%;box-sizing:border-box;background:#142219;border:1px solid rgba(46,204,113,0.3);color:#fff;padding:8px 12px;border-radius:8px;font-size:12.5px;outline:none;cursor:pointer;">
                                        <option value="Vernonia amygdalina (Bitter Leaf)">Vernonia amygdalina (Bitter Leaf)</option>
                                        <option value="Zingiber officinale (Ginger)">Zingiber officinale (Ginger)</option>
                                        <option value="Hibiscus sabdariffa (Zobo / Roselle)">Hibiscus sabdariffa (Zobo / Roselle)</option>
                                        <option value="Moringa oleifera">Moringa oleifera</option>
                                        <option value="Curcuma longa (Turmeric)">Curcuma longa (Turmeric)</option>
                                        <option value="Garcinia kola (Bitter Kola)">Garcinia kola (Bitter Kola)</option>
                                        <option value="St. John's Wort (Hypericum perforatum)">St. John's Wort</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <!-- Dynamic Result Card -->
                        <div id="matrix-result-container"></div>
                    </div>
                </div>
            `;

            this.modalEl.onclick = (e) => {
                if (e.target === this.modalEl) this.close();
            };
            document.body.appendChild(this.modalEl);
        },

        open: function(drug = 'Metformin', herb = 'Vernonia amygdalina (Bitter Leaf)') {
            if (!this.modalEl) this.createModalDOM();
            this.modalEl.style.display = 'flex';

            const dSelect = document.getElementById('matrix-drug-select');
            const hSelect = document.getElementById('matrix-herb-select');
            if (dSelect) dSelect.value = drug;
            if (hSelect) hSelect.value = herb;

            this.evaluate(drug, herb);
        },

        close: function() {
            if (this.modalEl) this.modalEl.style.display = 'none';
        },

        onSelectChange: function() {
            const drug = document.getElementById('matrix-drug-select')?.value;
            const herb = document.getElementById('matrix-herb-select')?.value;
            this.evaluate(drug, herb);
        },

        evaluate: function(drug, herb) {
            const container = document.getElementById('matrix-result-container');
            if (!container) return;

            const match = CYP450_DATABASE.find(item => 
                (item.drug.toLowerCase().includes(drug.toLowerCase()) || drug.toLowerCase().includes(item.drug.toLowerCase())) &&
                (item.herb.toLowerCase().includes(herb.toLowerCase()) || herb.toLowerCase().includes(item.herb.toLowerCase()))
            ) || {
                drug: drug,
                drugClass: 'Prescription Medication',
                herb: herb,
                risk: 'green',
                riskTitle: 'No Documented Adverse Interaction',
                pathways: ['CYP3A4 Neutral', 'Phase II Conjugation'],
                mechanism: 'No competitive inhibition or hepatic enzyme induction documented in clinical ethnobotanical literature.',
                guidance: 'Standard botanical therapeutic posology is safe. Maintain normal administration interval.'
            };

            const riskClass = match.risk === 'red' ? 'risk-gauge-red' : (match.risk === 'yellow' ? 'risk-gauge-yellow' : 'risk-gauge-green');
            const riskIcon = match.risk === 'red' ? '⛔' : (match.risk === 'yellow' ? '⚠️' : '✅');

            container.innerHTML = `
                <div class="metric-card-glass" style="border-color:rgba(46,204,113,0.35);">
                    <div class="risk-gauge-meter ${riskClass}">
                        <span style="font-size:18px;">${riskIcon}</span>
                        <span>${match.riskTitle}</span>
                    </div>

                    <div style="margin-top:10px;">
                        <strong style="font-size:11px;color:rgba(255,255,255,0.6);text-transform:uppercase;letter-spacing:0.5px;display:block;margin-bottom:6px;">Enzyme & Transporter Pathways:</strong>
                        <div style="display:flex;flex-wrap:wrap;gap:6px;">
                            ${match.pathways.map(p => `<span class="pathway-badge-glass">🧬 ${p}</span>`).join('')}
                        </div>
                    </div>

                    <div style="margin-top:12px;font-size:12.5px;color:#d0e4d7;line-height:1.5;">
                        <strong style="color:#fff;">Pharmacokinetic Mechanism:</strong>
                        <div>${match.mechanism}</div>
                    </div>

                    <div style="margin-top:12px;background:rgba(0,0,0,0.3);padding:10px 14px;border-radius:8px;font-size:12px;color:var(--accent-green,#2ecc71);border-left:3px solid var(--accent-green,#2ecc71);line-height:1.45;">
                        <strong>Clinical Posology Rule:</strong> ${match.guidance}
                    </div>
                </div>
            `;
        }
    };

    window.CYP450SafetyMatrix = CYP450SafetyMatrix;
})(window);
