/**
 * ═══════════════════════════════════════════════════════════════════
 * HERBALIST AI — ARTIFACTS CANVAS CONTROLLER
 * Reactive prescription compounding workspace, pot volume slider,
 * dispensary checklist, and chrono-dosing tracker.
 * ═══════════════════════════════════════════════════════════════════
 */

(function(window) {
    'use strict';

    function toggleArtifactsCanvas() {
        const pane = document.getElementById('artifacts-canvas-pane');
        if (!pane) return;
        if (pane.classList.contains('collapsed')) {
            openArtifactsCanvas(window.canvasActivePrescription || window.activePrescriptionPayload);
        } else {
            closeArtifactsCanvas();
        }
    }

    function openArtifactsCanvas(data = null) {
        const pane = document.getElementById('artifacts-canvas-pane');
        const toggleBtn = document.getElementById('canvas-toggle-btn');
        if (!pane) return;

        if (data) {
            window.canvasActivePrescription = data;
        } else if (!window.canvasActivePrescription && window.activePrescriptionPayload) {
            window.canvasActivePrescription = window.activePrescriptionPayload;
        }

        pane.classList.remove('collapsed');
        if (toggleBtn) {
            toggleBtn.style.background = 'var(--accent-green)';
            toggleBtn.style.color = '#000';
            toggleBtn.style.borderColor = 'var(--accent-green)';
        }
        renderArtifactsCanvasContent();
    }

    function closeArtifactsCanvas() {
        const pane = document.getElementById('artifacts-canvas-pane');
        const toggleBtn = document.getElementById('canvas-toggle-btn');
        if (!pane) return;
        pane.classList.add('collapsed');
        pane.classList.remove('fullscreen');
        if (toggleBtn) {
            toggleBtn.style.background = 'rgba(52, 152, 219, 0.12)';
            toggleBtn.style.color = '#3498db';
            toggleBtn.style.borderColor = '#3498db';
        }
    }

    function toggleCanvasFullscreen() {
        const pane = document.getElementById('artifacts-canvas-pane');
        if (!pane) return;
        pane.classList.toggle('fullscreen');
        const btn = document.getElementById('canvas-fullscreen-btn');
        if (btn) {
            btn.style.color = pane.classList.contains('fullscreen') ? 'var(--accent-gold)' : '#fff';
        }
    }

    function setCanvasPotBatchLiters(liters) {
        window.currentCanvasBatchLiters = parseFloat(liters) || 2.0;
        renderArtifactsCanvasContent();
    }

    function toggleHerbDispensaryCheck(herbKey) {
        if (!window.checkedHerbDispensaryItems) window.checkedHerbDispensaryItems = new Set();
        if (window.checkedHerbDispensaryItems.has(herbKey)) {
            window.checkedHerbDispensaryItems.delete(herbKey);
        } else {
            window.checkedHerbDispensaryItems.add(herbKey);
        }
        renderArtifactsCanvasContent();
    }

    function toggleChronoDose(slot) {
        if (!window.chronoDoseChecklist) window.chronoDoseChecklist = { morning: false, midday: false, evening: false };
        window.chronoDoseChecklist[slot] = !window.chronoDoseChecklist[slot];
        renderArtifactsCanvasContent();
    }

    function renderArtifactsCanvasContent() {
        const body = document.getElementById('canvas-body');
        if (!body) return;

        const data = window.canvasActivePrescription || window.activePrescriptionPayload;
        if (!data) {
            body.innerHTML = `
                <div style="color:var(--text-muted);text-align:center;padding:60px 20px;">
                    <div style="width:48px;height:48px;border-radius:14px;background:rgba(46,204,113,0.12);border:1.5px solid rgba(46,204,113,0.3);display:flex;align-items:center;justify-content:center;margin:0 auto 12px auto;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2ecc71" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.4 19 2c1 2 2 4.1 2 9 0 4.9-4 9-9 9z"></path>
                            <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"></path>
                        </svg>
                    </div>
                    <h4 style="color:#fff;font-family:'Outfit',sans-serif;margin-bottom:6px;">No Active Prescription Loaded</h4>
                    <p style="font-size:12.5px;line-height:1.5;margin:0;">Consult Dr. Herbalist in the chat pane to generate an official botanical prescription.</p>
                </div>
            `;
            return;
        }

        const f = data.formulation || {};
        const ingredients = f.ingredients || [];
        const primaryDiag = data.primary_diagnosis || 'Health Maintenance';
        const formulationName = f.formulation_name || 'Botanical Synergy Complex';
        const matchScore = f.bioactive_match_score ? f.bioactive_match_score.toFixed(1) : '98.5';
        
        const currentBatchL = window.currentCanvasBatchLiters || 2.0;
        const multiplier = currentBatchL / 2.0;
        const totalBioactiveMg = Math.round((f.total_active_bioactives_mg || 2800) * multiplier);
        const totalCupsYield = Math.round((currentBatchL * 1000) / 150);
        const daysSupply = (totalCupsYield / 3).toFixed(1);
        const checkedItems = window.checkedHerbDispensaryItems || new Set();
        const chrono = window.chronoDoseChecklist || { morning: false, midday: false, evening: false };

        body.innerHTML = `
            <!-- 1. DIAGNOSIS & REMEDY SUMMARY BANNER -->
            <div style="background:linear-gradient(135deg, rgba(46,204,113,0.15), rgba(52,152,219,0.1));border:1px solid var(--accent-green);border-radius:16px;padding:16px;box-shadow:0 4px 20px rgba(0,0,0,0.3);">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                    <span style="font-size:10px;font-weight:800;color:var(--accent-green);text-transform:uppercase;letter-spacing:0.5px;background:rgba(46,204,113,0.15);padding:2px 8px;border-radius:6px;">ACTIVE CLINICAL FORMULATION</span>
                    <span style="font-size:11px;font-weight:700;color:var(--accent-gold);display:flex;align-items:center;gap:4px;">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                        <span>${matchScore}% Synergy Match</span>
                    </span>
                </div>
                <h4 style="font-family:'Outfit',sans-serif;font-size:16px;color:#fff;margin:0 0 4px 0;">${formulationName}</h4>
                <div style="font-size:12px;color:rgba(255,255,255,0.75);">Target: <strong>${primaryDiag}</strong></div>
            </div>

            <!-- 2. INTERACTIVE POT BATCH SLIDER -->
            <div style="background:rgba(0,0,0,0.35);border:1px solid var(--card-border);border-radius:16px;padding:16px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                    <div>
                        <span style="font-size:11px;font-weight:700;color:var(--accent-green);text-transform:uppercase;">Kitchen Pot Batch Volume</span>
                        <div style="font-size:11px;color:var(--text-muted);">Adjust pot volume to auto-scale raw dried herb masses</div>
                    </div>
                    <div style="font-family:'Outfit',sans-serif;font-size:20px;font-weight:800;color:#2ecc71;">
                        ${currentBatchL.toFixed(1)} L
                    </div>
                </div>
                <input type="range" min="0.5" max="5.0" step="0.5" value="${currentBatchL}" oninput="setCanvasPotBatchLiters(this.value)" style="width:100%;accent-color:var(--accent-green);cursor:pointer;margin-bottom:12px;">
                
                <!-- Quick Preset Liters Pills -->
                <div style="display:flex;gap:6px;margin-bottom:14px;">
                    ${[1.0, 2.0, 3.0, 4.0, 5.0].map(L => `
                        <button onclick="setCanvasPotBatchLiters(${L})" style="flex:1;padding:6px 0;background:${currentBatchL === L ? 'var(--accent-green)' : 'rgba(255,255,255,0.06)'};color:${currentBatchL === L ? '#000' : '#fff'};border:none;border-radius:8px;font-size:11px;font-weight:700;cursor:pointer;">
                            ${L}L
                        </button>
                    `).join('')}
                </div>

                <!-- Batch Yield Metrics Grid -->
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;text-align:center;font-size:11px;">
                    <div style="background:rgba(255,255,255,0.03);padding:8px;border-radius:10px;border:1px solid rgba(255,255,255,0.06);">
                        <span style="color:var(--text-muted);display:block;">Bioactive Mass</span>
                        <strong style="color:var(--accent-gold);font-size:13px;">${totalBioactiveMg} mg</strong>
                    </div>
                    <div style="background:rgba(255,255,255,0.03);padding:8px;border-radius:10px;border:1px solid rgba(255,255,255,0.06);">
                        <span style="color:var(--text-muted);display:block;">Teacup Servings</span>
                        <strong style="color:#2ecc71;font-size:13px;">${totalCupsYield} cups</strong>
                    </div>
                    <div style="background:rgba(255,255,255,0.03);padding:8px;border-radius:10px;border:1px solid rgba(255,255,255,0.06);">
                        <span style="color:var(--text-muted);display:block;">Days of Supply</span>
                        <strong style="color:#3498db;font-size:13px;">${daysSupply} days</strong>
                    </div>
                </div>
            </div>

            <!-- 3. INTERACTIVE DISPENSARY HERB CHECKLIST -->
            <div style="background:rgba(0,0,0,0.35);border:1px solid var(--card-border);border-radius:16px;padding:16px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                    <h4 style="font-family:'Outfit',sans-serif;font-size:14px;color:#fff;margin:0;display:flex;align-items:center;gap:8px;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2ecc71" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
                        <span>Dispensary & Compounding Checklist</span>
                    </h4>
                    <span style="font-size:10px;color:var(--text-muted);">Tap herb to check off</span>
                </div>

                <div style="display:flex;flex-direction:column;gap:8px;">
                    ${ingredients.map((ing, idx) => {
                        const key = `herb_${idx}_${ing.common_name}`;
                        const isChecked = checkedItems.has(key);
                        const scaledGrams = ((ing.weight_grams || 15.0) * multiplier).toFixed(1);
                        const scaledYield = Math.round((ing.yielded_bioactive_mg || 180) * multiplier);
                        const ap = ing.anatomy_profile;

                        return `
                            <div class="herb-check-item ${isChecked ? 'checked' : ''}" onclick="toggleHerbDispensaryCheck('${key}')">
                                <div style="width:20px;height:20px;border-radius:6px;border:1.5px solid ${isChecked ? 'var(--accent-green)' : 'rgba(255,255,255,0.3)'};background:${isChecked ? 'var(--accent-green)' : 'transparent'};display:flex;align-items:center;justify-content:center;color:#000;font-size:11px;font-weight:900;flex-shrink:0;">
                                    ${isChecked ? '✓' : ''}
                                </div>
                                <div style="flex:1;">
                                    <div class="herb-check-title" style="font-size:13px;font-weight:700;color:#fff;">
                                         ${ing.common_name}
                                    </div>
                                    <div style="font-size:11px;color:rgba(255,255,255,0.6);font-style:italic;">
                                        ${ing.botanical_name} (${ing.part_used})
                                    </div>
                                    ${ap ? `
                                        <div style="font-size:10px;color:#3498db;margin-top:2px;">
                                            🔬 ${ap.primary_tissue_type.split('&')[0]} • ${ap.recommended_extraction.split('(')[0]}
                                        </div>
                                    ` : ''}
                                </div>
                                <div style="text-align:right;flex-shrink:0;">
                                    <div style="font-size:14px;font-weight:800;color:var(--accent-green);">${scaledGrams}g</div>
                                    <div style="font-size:10px;color:var(--accent-gold);">${scaledYield}mg active</div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>

            <!-- 4. TODAY'S CHRONO-DOSING TRACKER -->
            <div style="background:rgba(0,0,0,0.35);border:1px solid var(--card-border);border-radius:16px;padding:16px;">
                <h4 style="font-family:'Outfit',sans-serif;font-size:14px;color:#fff;margin:0 0 10px 0;display:flex;align-items:center;gap:8px;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                    <span>Today's Chrono-Dosing Log (3x Daily)</span>
                </h4>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;">
                    <div onclick="toggleChronoDose('morning')" style="cursor:pointer;background:${chrono.morning ? 'rgba(46,204,113,0.15)' : 'rgba(255,255,255,0.03)'};border:1px solid ${chrono.morning ? 'var(--accent-green)' : 'rgba(255,255,255,0.1)'};border-radius:12px;padding:10px;text-align:center;">
                        <div style="display:flex;justify-content:center;margin-bottom:4px;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f39c12" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4M4.93 10.93l2.83-2.83M2 18h2M20 18h2M19.07 10.93l-2.83-2.83M22 22H2M8 18a4 4 0 0 1 8 0"/></svg>
                        </div>
                        <div style="font-size:11px;font-weight:700;color:#fff;margin-top:2px;">Morning</div>
                        <div style="font-size:10px;color:var(--text-muted);">8:00 AM (150mL)</div>
                        <div style="font-size:11px;font-weight:800;color:${chrono.morning ? 'var(--accent-green)' : 'rgba(255,255,255,0.3)'};margin-top:4px;">
                            ${chrono.morning ? '✓ TAKEN' : '○ PENDING'}
                        </div>
                    </div>
                    <div onclick="toggleChronoDose('midday')" style="cursor:pointer;background:${chrono.midday ? 'rgba(46,204,113,0.15)' : 'rgba(255,255,255,0.03)'};border:1px solid ${chrono.midday ? 'var(--accent-green)' : 'rgba(255,255,255,0.1)'};border-radius:12px;padding:10px;text-align:center;">
                        <div style="display:flex;justify-content:center;margin-bottom:4px;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f1c40f" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>
                        </div>
                        <div style="font-size:11px;font-weight:700;color:#fff;margin-top:2px;">Midday</div>
                        <div style="font-size:10px;color:var(--text-muted);">1:30 PM (150mL)</div>
                        <div style="font-size:11px;font-weight:800;color:${chrono.midday ? 'var(--accent-green)' : 'rgba(255,255,255,0.3)'};margin-top:4px;">
                            ${chrono.midday ? '✓ TAKEN' : '○ PENDING'}
                        </div>
                    </div>
                    <div onclick="toggleChronoDose('evening')" style="cursor:pointer;background:${chrono.evening ? 'rgba(46,204,113,0.15)' : 'rgba(255,255,255,0.03)'};border:1px solid ${chrono.evening ? 'var(--accent-green)' : 'rgba(255,255,255,0.1)'};border-radius:12px;padding:10px;text-align:center;">
                        <div style="display:flex;justify-content:center;margin-bottom:4px;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#9b59b6" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
                        </div>
                        <div style="font-size:11px;font-weight:700;color:#fff;margin-top:2px;">Bedtime</div>
                        <div style="font-size:10px;color:var(--text-muted);">9:00 PM (150mL)</div>
                        <div style="font-size:11px;font-weight:800;color:${chrono.evening ? 'var(--accent-green)' : 'rgba(255,255,255,0.3)'};margin-top:4px;">
                            ${chrono.evening ? '✓ TAKEN' : '○ PENDING'}
                        </div>
                    </div>
                </div>

                <!-- Canvas Quick Care Suite Action Buttons -->
                <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px;">
                    <button onclick="if(typeof saveCurrentPrescription==='function') saveCurrentPrescription(window.canvasActivePrescription || window.activePrescriptionPayload);" style="flex: 1; min-width: 140px; background: rgba(46,204,113,0.18); border: 1px solid var(--accent-green); color: var(--accent-green); padding: 10px 14px; border-radius: 12px; font-weight: 700; font-size: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px;">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
                        <span>Save to Library</span>
                    </button>
                    <button onclick="if(typeof openKitchenCookMode==='function') openKitchenCookMode(window.canvasActivePrescription || window.activePrescriptionPayload);" style="flex: 1; min-width: 150px; background: linear-gradient(135deg, rgba(243,156,18,0.22), rgba(230,126,34,0.12)); border: 1px solid var(--accent-gold); color: #fff; padding: 10px 14px; border-radius: 12px; font-weight: 700; font-size: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14h16c0 4.4-3.6 8-8 8s-8-3.6-8-8Z"></path><path d="M7 14V9a5 5 0 0 1 10 0v5"></path><path d="M12 4V2"></path><path d="M20 14l3-3"></path><path d="M9 2h6"></path></svg>
                        <span>Compound in Cook Mode</span>
                    </button>
                    <button onclick="if(typeof openVaultRecoveryModal==='function') openVaultRecoveryModal();" style="flex: 1; min-width: 140px; background: rgba(52,152,219,0.15); border: 1px solid #3498db; color: #3498db; padding: 10px 14px; border-radius: 12px; font-weight: 700; font-size: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px;">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                        <span>Track in Vault</span>
                    </button>
                </div>
            </div>
        `;
    }

    // Attach to window
    window.toggleArtifactsCanvas = toggleArtifactsCanvas;
    window.openArtifactsCanvas = openArtifactsCanvas;
    window.closeArtifactsCanvas = closeArtifactsCanvas;
    window.toggleCanvasFullscreen = toggleCanvasFullscreen;
    window.setCanvasPotBatchLiters = setCanvasPotBatchLiters;
    window.toggleHerbDispensaryCheck = toggleHerbDispensaryCheck;
    window.toggleChronoDose = toggleChronoDose;
    window.renderArtifactsCanvasContent = renderArtifactsCanvasContent;

})(window);
