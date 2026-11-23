/**
 * HERBALIST AI — KITCHEN COOK MODE HUD CONTROLLER
 * Owns the existing Care Suite flow, recipe steps, narration, and kitchen timer.
 */

(function(window) {
    'use strict';

    function openKitchenCookMode(data = null) {
        window.openPatientCareToolkitModal?.('cook');
        const modal = document.getElementById('patient-care-toolkit-modal');
        if (modal) {
            modal.classList.add('open');
            modal.classList.add('active');
        }
        initKitchenCookData(data);
    }

    function closeKitchenCookMode() {
        window.closePatientCareToolkitModal?.();
        const modal = document.getElementById('patient-care-toolkit-modal');
        if (modal) {
            modal.classList.remove('open');
            modal.classList.remove('active');
        }
    }

        let currentCookStepIndex = 0;
        let cookStepsList = [];
        let cookVoiceNarrationActive = true;
        let kitchenTimerInterval = null;
        let kitchenTimerRemainingSeconds = 20 * 60; // default 20 mins
        let kitchenTimerIsRunning = false;

        function parseHerbIngredient(ing, scaleRatio = 1.0) {
            let commonName = "Medicinal Herb";
            let botanicalName = "";
            let activeBioactives = "Active phytocompounds";
            let primaryRole = "Therapeutic active";
            let baseMass = 25.0;
            let icon = "🌿";

            if (typeof ing === 'string') {
                const str = ing;
                if (str.includes("HerbalRemedy(") || str.includes("common_name=")) {
                    const cnMatch = str.match(/common_name=['"]([^'"]+)['"]/);
                    if (cnMatch) commonName = cnMatch[1];

                    const bnMatch = str.match(/botanical_name=['"]([^'"]+)['"]/);
                    if (bnMatch) botanicalName = bnMatch[1];

                    const acMatch = str.match(/active_compounds=\[([^\]]+)\]/);
                    if (acMatch) {
                        activeBioactives = acMatch[1].replace(/['"]/g, '').split(',').slice(0, 2).map(s => s.trim()).join(', ');
                    }

                    const actMatch = str.match(/therapeutic_actions=\[([^\]]+)\]/);
                    if (actMatch) {
                        primaryRole = actMatch[1].replace(/['"]/g, '').split(',').slice(0, 2).map(s => s.trim()).join(', ');
                    }
                } else {
                    commonName = str.split('(')[0].trim();
                    if (str.includes('(')) {
                        botanicalName = str.substring(str.indexOf('(') + 1, str.indexOf(')')).trim();
                    }
                }
            } else if (typeof ing === 'object' && ing !== null) {
                let rawName = ing.name || ing.common_name || ing.herb || "";
                if (typeof rawName === 'string' && (rawName.includes("HerbalRemedy(") || rawName.includes("common_name="))) {
                    const parsed = parseHerbIngredient(rawName, scaleRatio);
                    commonName = parsed.commonName;
                    botanicalName = parsed.botanicalName || ing.botanical_name || "";
                    activeBioactives = parsed.activeBioactives;
                    primaryRole = parsed.primaryRole;
                } else {
                    commonName = rawName || "Medicinal Herb";
                    botanicalName = ing.botanical_name || ing.scientific_name || "";
                    
                    if (Array.isArray(ing.active_compounds) && ing.active_compounds.length > 0) {
                        activeBioactives = ing.active_compounds.slice(0, 2).join(', ');
                    } else if (Array.isArray(ing.active_bioactives) && ing.active_bioactives.length > 0) {
                        activeBioactives = ing.active_bioactives.slice(0, 2).join(', ');
                    } else if (ing.primary_bioactive) {
                        activeBioactives = ing.primary_bioactive;
                    }

                    if (Array.isArray(ing.therapeutic_actions) && ing.therapeutic_actions.length > 0) {
                        primaryRole = ing.therapeutic_actions.slice(0, 2).join(', ');
                    } else if (ing.role || ing.indication || ing.therapeutic_properties) {
                        primaryRole = ing.role || ing.indication || ing.therapeutic_properties;
                    }
                }

                const massRaw = ing.mass_g || ing.weight_grams || ing.amount || ing.dosage_g || '25';
                baseMass = parseFloat(massRaw.toString().replace(/[^\d.]/g, '')) || 25.0;
            }

            // Clean up commonName
            commonName = commonName.replace(/HerbalRemedy\(/g, '').replace(/common_name=/g, '').replace(/['"]/g, '').trim();
            if (commonName.includes(',')) commonName = commonName.split(',')[0].trim();

            // Select emoji icon based on botanical name or common name
            const lower = (commonName + " " + botanicalName).toLowerCase();
            if (lower.includes('root') || lower.includes('ginger') || lower.includes('rhizome') || lower.includes('ginseng') || lower.includes('turmeric')) {
                icon = '🫚';
            } else if (lower.includes('leaf') || lower.includes('neem') || lower.includes('bitter') || lower.includes('tea') || lower.includes('basil')) {
                icon = '🍃';
            } else if (lower.includes('bark') || lower.includes('kola') || lower.includes('cinnamon') || lower.includes('elm')) {
                icon = '🌰';
            } else if (lower.includes('berry') || lower.includes('citrus') || lower.includes('orange') || lower.includes('fruit') || lower.includes('papaya')) {
                icon = '🍋';
            } else if (lower.includes('flower') || lower.includes('hibiscus') || lower.includes('chamomile') || lower.includes('zobo')) {
                icon = '🌺';
            } else {
                icon = '🌿';
            }

            const scaledMass = (baseMass * scaleRatio).toFixed(1);

            return {
                commonName,
                botanicalName,
                activeBioactives,
                primaryRole,
                scaledMass: `${scaledMass}g`,
                icon
            };
        }

        function jumpToCookStep(index) {
            if (index >= 0 && index < cookStepsList.length) {
                currentCookStepIndex = index;
                renderCookStep();
                speakActiveCookStep();
            }
        }

        function initKitchenCookData(data = null) {
            let rxData = data;
            if (!rxData && typeof canvasActivePrescription !== 'undefined' && canvasActivePrescription) rxData = canvasActivePrescription;
            if (!rxData && typeof activePrescriptionPayload !== 'undefined' && activePrescriptionPayload) rxData = activePrescriptionPayload;
            if (!rxData) {
                try {
                    const saved = localStorage.getItem('herbalist_active_cook_rx');
                    if (saved) rxData = JSON.parse(saved);
                } catch(e) {}
            }

            const potBadge = document.getElementById('cook-hud-pot-badge');
            const timerWidget = document.getElementById('cook-timer-widget');
            const navControls = document.getElementById('cook-step-nav-controls');
            const tracker = document.getElementById('cook-step-tracker');
            const card = document.getElementById('cook-step-card');

            if (!rxData || (!rxData.formulation && !rxData.ingredients && !rxData.primary_diagnosis)) {
                cookStepsList = [];
                if (potBadge) potBadge.innerText = 'No Active Prescription Loaded';
                if (timerWidget) timerWidget.style.display = 'none';
                if (navControls) navControls.style.display = 'none';
                if (tracker) tracker.innerText = 'Prescription Needed';
                if (card) {
                    card.innerHTML = `
                        <div style="text-align:center;padding:36px 20px;color:var(--text-muted);">
                            <div style="font-size:44px;margin-bottom:12px;">🍲</div>
                            <h4 style="font-family:'Outfit',sans-serif;color:#fff;font-size:16px;font-weight:700;margin:0 0 6px 0;">No Active Prescription Loaded in Cook Mode</h4>
                            <p style="font-size:12.5px;line-height:1.6;max-width:440px;margin:0 auto 20px auto;color:#c0d5c8;">
                                Cook Mode automatically creates customized step-by-step pot compounding HUD steps, batch water ratios, and simmering timers directly from your Dr. Herbalist prescriptions.
                            </p>
                            <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
                                <button onclick="closePatientCareToolkitModal(); document.getElementById('user-input').focus();" style="background:linear-gradient(135deg, var(--accent-green), #27ae60);color:#000;border:none;padding:9px 18px;border-radius:10px;font-weight:800;font-size:12px;cursor:pointer;display:flex;align-items:center;gap:6px;">
                                    <span>🌿 Consult Dr. Herbalist</span>
                                </button>
                                <button onclick="closePatientCareToolkitModal(); openPrescriptionsModal();" style="background:rgba(255,255,255,0.08);border:1px solid var(--pill-border);color:#fff;padding:9px 18px;border-radius:10px;font-weight:700;font-size:12px;cursor:pointer;display:flex;align-items:center;gap:6px;">
                                    <span>📁 Load Saved Prescription</span>
                                </button>
                            </div>
                        </div>
                    `;
                }
                return;
            }

            if (timerWidget) timerWidget.style.display = 'flex';
            if (navControls) navControls.style.display = 'flex';

            const f = rxData.formulation || rxData;
            const potLiters = (typeof activeCanvasPotLiters !== 'undefined' && activeCanvasPotLiters) ? activeCanvasPotLiters : (f.total_volume_ml ? (f.total_volume_ml / 1000).toFixed(1) : '2.0');
            const totalVolMl = Math.round(parseFloat(potLiters) * 1000);
            const scaleRatio = parseFloat(potLiters) / 2.0;

            const rxTitle = f.formulation_name || rxData.primary_diagnosis || 'Prescribed Botanical Formulation';
            if (potBadge) potBadge.innerText = `${rxTitle} • ${potLiters} L Pot Batch (${totalVolMl} mL)`;

            const rawIngredients = f.ingredients || [];
            const scaledIngredients = rawIngredients.map(ing => parseHerbIngredient(ing, scaleRatio));

            const ingChecklistHTML = scaledIngredients.length > 0 ? `
                <div class="cook-herb-grid">
                    ${scaledIngredients.map(ing => `
                        <div class="cook-herb-infographic-card">
                            <div class="cook-herb-left">
                                <div class="cook-herb-icon-circle">${ing.icon}</div>
                                <div class="cook-herb-meta">
                                    <h4 class="cook-herb-common-name">${ing.commonName}</h4>
                                    ${ing.botanicalName ? `<span class="cook-herb-botanical-tag">${ing.botanicalName}</span>` : ''}
                                    <div class="cook-herb-badges-row">
                                        <span class="cook-chip active-bio">
                                            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/></svg>
                                            <strong>Active:</strong> ${ing.activeBioactives}
                                        </span>
                                        <span class="cook-chip action-role">
                                            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                                            <strong>Target:</strong> ${ing.primaryRole}
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div class="cook-herb-mass-pill">
                                <span class="mass-label">Batch Mass</span>
                                <span class="mass-val">${ing.scaledMass}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            ` : '<div style="font-size:12px;color:rgba(255,255,255,0.7);padding:10px;background:rgba(255,255,255,0.03);border-radius:10px;">Botanical mass scaled according to doctor prescription formula.</div>';

            const customSteps = f.household_kitchen_recipe || f.preparation_recipe_steps || [];
            const step3Desc = customSteps.length > 2 ? customSteps[2] : "Bring to a gentle boil, then turn heat to low and let it simmer covered for 25 to 30 minutes.";
            const step5Dose = f.household_dose_schedule || f.dosing_frequency || "Drink 1 teacup (150 mL) 2–3 times daily after meals.";

            if (Array.isArray(customSteps) && customSteps.length >= 4) {
                const stepIcons = ['⚖️', '💧', '🔥', '🍶', '🍵', '❄️'];
                cookStepsList = customSteps.map((stepStr, idx) => {
                    const isPotBoil = stepStr.toLowerCase().includes('boil') || stepStr.toLowerCase().includes('simmer') || stepStr.toLowerCase().includes('water');
                    const cleanTitle = stepStr.includes(':') ? stepStr.split(':')[0].replace(/STEP \d+ \(([^)]+)\)/i, '$1').replace(/^\d+\.\s*/, '').trim() : `Step ${idx + 1}`;
                    const cleanDesc = stepStr.includes(':') ? stepStr.split(':').slice(1).join(':').trim() : stepStr;
                    const timerMins = stepStr.toLowerCase().includes('simmer') || stepStr.toLowerCase().includes('boil') ? 25 : (idx === 0 ? 2 : (idx === 1 ? 5 : 0));
                    
                    let extra = '';
                    if (idx === 0 || stepStr.toLowerCase().includes('gather') || stepStr.toLowerCase().includes('prepare')) {
                        extra = `<div style="margin-top:8px;">${ingChecklistHTML}</div>`;
                    }
                    
                    return {
                        shortName: `${stepIcons[idx % stepIcons.length]} ${idx + 1}. ${cleanTitle.slice(0, 16)}`,
                        title: `${idx + 1}. ${cleanTitle}`,
                        desc: cleanDesc,
                        extraHTML: extra,
                        timerMinutes: timerMins
                    };
                });
            } else {
                cookStepsList = [
                    {
                        shortName: "⚖️ 1. Weigh & Rinse",
                        title: "1. Precise Herb Weighing & Cold Rinse",
                        desc: "Measure exact dry root/leaf mass. Gently rinse botanicals in clean cold water to remove dust particles.",
                        extraHTML: `<div style="margin-top:8px;">${ingChecklistHTML}</div>`,
                        timerMinutes: 2
                    },
                    {
                        shortName: "💧 2. Pot Water Prep",
                        title: "2. Cold Water Inoculation in Stainless / Glass Pot",
                        desc: `Place the measured botanicals into a clean stainless steel or borosilicate glass pot. Pour exactly <strong>${potLiters} Liters (${totalVolMl} mL)</strong> of clean drinking water. Let sit cold for 5 minutes for cellular hydration.`,
                        extraHTML: '',
                        timerMinutes: 5
                    },
                    {
                        shortName: "🔥 3. Covered Simmer",
                        title: "3. Rolling Boil & Slow Covered Simmer (Decoction Extraction)",
                        desc: step3Desc,
                        extraHTML: '',
                        timerMinutes: 25
                    },
                    {
                        shortName: "🍶 4. Filter & Bottle",
                        title: "4. Fine Mesh Straining & Airtight Bottling",
                        desc: "Turn off heat. Pour the hot decoction through a fine kitchen strainer into a clean glass pitcher or glass bottle.",
                        extraHTML: '',
                        timerMinutes: 3
                    },
                    {
                        shortName: "🍵 5. Dose & Store",
                        title: "5. Chrono-Dosing & Cold Storage Guidelines",
                        desc: `${step5Dose} Allow remaining brew to cool to room temperature, seal airtight, and store refrigerated (4°C) for up to 14 days. Drink warm.`,
                        extraHTML: '',
                        timerMinutes: 0
                    }
                ];
            }

            currentCookStepIndex = 0;
            renderCookStep();
            speakActiveCookStep();
        }

        function renderCookStep() {
            if (!cookStepsList || cookStepsList.length === 0) return;
            const step = cookStepsList[currentCookStepIndex];
            const card = document.getElementById('cook-step-card');
            const tracker = document.getElementById('cook-step-tracker');
            const prevBtn = document.getElementById('cook-prev-btn');
            const nextBtn = document.getElementById('cook-next-btn');

            if (tracker) tracker.innerText = `Step ${currentCookStepIndex + 1} of ${cookStepsList.length}`;

            // Build Stepper Ribbon HTML
            const stepperRibbonHTML = `
                <div class="cook-stepper-ribbon">
                    ${cookStepsList.map((s, idx) => {
                        let stateClass = '';
                        if (idx === currentCookStepIndex) stateClass = 'active';
                        else if (idx < currentCookStepIndex) stateClass = 'completed';
                        return `
                            <div class="cook-stepper-step ${stateClass}" onclick="jumpToCookStep(${idx})">
                                <span>${s.shortName || ('Step ' + (idx + 1))}</span>
                            </div>
                        `;
                    }).join('')}
                </div>
            `;

            if (card) {
                card.innerHTML = `
                    ${stepperRibbonHTML}
                    <div class="cook-step-num">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent-green)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 2v20"></path>
                            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                        </svg>
                        <span>STEP ${currentCookStepIndex + 1} OF ${cookStepsList.length} • CLINICAL HUD</span>
                    </div>
                    <div class="cook-step-title">${step.title}</div>
                    <div class="cook-step-desc">${step.desc}</div>
                    ${step.extraHTML || ''}
                `;
            }



            // Update navigation button states
            if (prevBtn) prevBtn.disabled = currentCookStepIndex === 0;
            if (nextBtn) {
                if (currentCookStepIndex === cookStepsList.length - 1) {
                    nextBtn.innerHTML = `
                        <span>Complete Cooking</span>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                        </svg>
                    `;
                } else {
                    nextBtn.innerHTML = `
                        <span>Next Step</span>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="9 18 15 12 9 6"></polyline>
                        </svg>
                    `;
                }
            }

            // Update timer to recommended step duration
            if (step.timerMinutes > 0) {
                resetKitchenTimer(step.timerMinutes * 60);
            }
        }

        function nextCookStep() {
            if (currentCookStepIndex < cookStepsList.length - 1) {
                currentCookStepIndex++;
                renderCookStep();
                speakActiveCookStep();
            } else {
                closeKitchenCookMode();
                appendBubble('doctor', `
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent-green)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                        </svg>
                        <h4 style="font-family:'Outfit',sans-serif;font-size:16px;color:var(--accent-green);margin:0;">Brewing Complete!</h4>
                    </div>
                    <p style="font-size:14px;line-height:1.6;">Your herbal decoction has been successfully brewed and scaled for your kitchen pot batch! Remember to adhere to your chrono-dosing schedule.</p>
                `);
            }
        }

        function prevCookStep() {
            if (currentCookStepIndex > 0) {
                currentCookStepIndex--;
                renderCookStep();
                speakActiveCookStep();
            }
        }

        let currentCookAudioLang = 'en';

        function changeCookAudioLanguage(lang) {
            currentCookAudioLang = lang || 'en';
            const select1 = document.getElementById('cook-audio-lang-toolkit');
            const select2 = document.getElementById('cook-audio-lang-fullscreen');
            if (select1) select1.value = currentCookAudioLang;
            if (select2) select2.value = currentCookAudioLang;
            
            const langNames = {
                'yo': 'Yorùbá (Dr. Adewale)',
                'ha': 'Hausa (Dr. Yusuf - Yusuf Lawal)',
                'ig': 'Igbo (Dr. Chioma)',
                'sw': 'Kiswahili (Dr. Juma)',
                'fr': 'Français (Dr. Monique)',
                'en': 'English'
            };
            showToast(`🌐 Audio language set to ${langNames[currentCookAudioLang] || 'English'}`, 'info', 2000);
            speakActiveCookStep();
        }

        async function speakTextWithLang(text, langCode = 'en') {
            if (!text || typeof window === 'undefined' || !('speechSynthesis' in window)) return;
            try {
                window.speechSynthesis.cancel();
                let clean = cleanClinicalTextForNaturalSpeech(text);
                
                if (langCode && langCode !== 'en') {
                    try {
                        const res = await fetch('/api/audio/speech-translate', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ text: clean, target_language: langCode })
                        });
                        if (res.ok) {
                            const data = await res.json();
                            if (data.translated_text) clean = cleanClinicalTextForNaturalSpeech(data.translated_text);
                        }
                    } catch(err) {
                        console.warn("Speech translation network note:", err);
                    }
                }
                
                const utterance = new SpeechSynthesisUtterance(clean);
                utterance.rate = 0.96;
                utterance.pitch = 1.0;
                
                const langMap = {
                    'yo': 'yo-NG',
                    'ha': 'ha-NG',
                    'ig': 'ig-NG',
                    'sw': 'sw-KE',
                    'fr': 'fr-FR',
                    'en': 'en-GB'
                };
                const ttsCode = langMap[langCode] || 'en-GB';
                utterance.lang = ttsCode;

                const naturalVoice = getBestNaturalVoice(ttsCode, 'female');
                if (naturalVoice) utterance.voice = naturalVoice;
                
                window.speechSynthesis.speak(utterance);
            } catch (e) {
                console.log("Speech narration note:", e);
            }
        }

        function speakCookText(text) {
            speakTextWithLang(text, currentCookAudioLang || 'en');
        }

        async function speakActiveCookStep() {
            if (!cookVoiceNarrationActive) return;
            const step = cookStepsList[currentCookStepIndex];
            if (step) {
                const text = `${step.title}. ${step.desc.replace(/<[^>]*>?/gm, '')}`;
                await speakTextWithLang(text, currentCookAudioLang);
            }
        }

        function readActiveCookStepAloud() {
            speakActiveCookStep();
        }

        function toggleCookVoiceNarration() {
            cookVoiceNarrationActive = !cookVoiceNarrationActive;
            const iconSvg = document.getElementById('cook-voice-icon-svg');
            const label = document.getElementById('cook-voice-label');
            if (iconSvg) {
                if (cookVoiceNarrationActive) {
                    iconSvg.innerHTML = `
                        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                        <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                    `;
                } else {
                    iconSvg.innerHTML = `
                        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                        <line x1="23" y1="9" x2="17" y2="15"></line>
                        <line x1="17" y1="9" x2="23" y2="15"></line>
                    `;
                }
            }
            if (label) label.innerText = cookVoiceNarrationActive ? 'Voice Guidance ON' : 'Voice Muted';
            if (!cookVoiceNarrationActive && window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
        }

        /* ── KITCHEN SIMMER TIMER ENGINE ── */
        function toggleKitchenTimer() {
            if (kitchenTimerIsRunning) {
                pauseKitchenTimer();
            } else {
                startKitchenTimer();
            }
        }

        function startKitchenTimer() {
            if (kitchenTimerIsRunning) return;
            kitchenTimerIsRunning = true;
            const btn = document.getElementById('cook-timer-btn');
            if (btn) {
                btn.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="6" y="4" width="4" height="16"></rect>
                        <rect x="14" y="4" width="4" height="16"></rect>
                    </svg>
                    <span>Pause Timer</span>
                `;
                btn.style.background = '#e67e22';
            }

            kitchenTimerInterval = setInterval(() => {
                if (kitchenTimerRemainingSeconds > 0) {
                    kitchenTimerRemainingSeconds--;
                    updateTimerDisplay();
                } else {
                    pauseKitchenTimer();
                    playKitchenChime();
                    speakCookText("Kitchen Timer Complete! Your decoction simmer has finished. Turn off the heat and prepare for straining.");
                }
            }, 1000);
        }

        function pauseKitchenTimer() {
            kitchenTimerIsRunning = false;
            clearInterval(kitchenTimerInterval);
            const btn = document.getElementById('cook-timer-btn');
            if (btn) {
                btn.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                    <span>Start Timer</span>
                `;
                btn.style.background = '';
            }
        }

        function resetKitchenTimer(seconds = 20 * 60) {
            pauseKitchenTimer();
            kitchenTimerRemainingSeconds = seconds;
            updateTimerDisplay();
        }

        function updateTimerDisplay() {
            const display = document.getElementById('cook-timer-display');
            if (!display) return;
            const mins = Math.floor(kitchenTimerRemainingSeconds / 60);
            const secs = kitchenTimerRemainingSeconds % 60;
            display.innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }

        function playKitchenChime() {
            try {
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
                osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.3); // A5
                gain.gain.setValueAtTime(0.3, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.2);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start();
                osc.stop(ctx.currentTime + 1.2);
            } catch (e) {
                console.log("Audio chime notice:", e);
            }
        }

        /* ══════════════════════════════════════════════════════════════ */
    // Public compatibility API used by existing markup and integrations.
    window.openKitchenCookMode = openKitchenCookMode;
    window.closeKitchenCookMode = closeKitchenCookMode;
    window.initKitchenCookData = initKitchenCookData;
    window.renderCookStep = renderCookStep;
    window.jumpToCookStep = jumpToCookStep;
    window.nextCookStep = nextCookStep;
    window.prevCookStep = prevCookStep;
    window.changeCookAudioLanguage = changeCookAudioLanguage;
    window.speakCookText = speakCookText;
    window.readActiveCookStepAloud = readActiveCookStepAloud;
    window.toggleCookVoiceNarration = toggleCookVoiceNarration;
    window.toggleKitchenTimer = toggleKitchenTimer;
    window.startKitchenTimer = startKitchenTimer;
    window.pauseKitchenTimer = pauseKitchenTimer;
    window.resetKitchenTimer = resetKitchenTimer;
    window.updateTimerDisplay = updateTimerDisplay;
    window.playKitchenChime = playKitchenChime;
    // Preserve earlier controller aliases during the transition.
    window.startCookTimer = startKitchenTimer;
    window.pauseCookTimer = pauseKitchenTimer;
    window.resetCookTimer = resetKitchenTimer;

})(window);
