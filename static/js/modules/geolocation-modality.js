/**
 * ═══════════════════════════════════════════════════════════════════
 * HERBALIST AI — GEOLOCATION & REGIONAL MODALITY ENGINE
 * IP & network-based tradition detection (African, Ayurveda, TCM, Western, WHO)
 * and topbar synchronization.
 * ═══════════════════════════════════════════════════════════════════
 */

(function(window) {
    'use strict';

    let userLocationData = {
        country: 'Global',
        country_code: 'GL',
        region: 'Global',
        timezone: '',
        detected_tradition: 'auto'
    };
    window.userLocationData = userLocationData;

    function changeClinicalModality(modalityKey, showNotification = true) {
        window.activeClinicalModality = modalityKey;
        window.currentClinicalModality = modalityKey;
        try { localStorage.setItem('herbalist_modality', modalityKey); } catch(e) {}

        const modalitySelector = document.getElementById('clinical-modality-selector');
        if (modalitySelector) modalitySelector.value = modalityKey;

        if (typeof window.syncRegionalEnglishVoiceProfile === 'function') {
            window.syncRegionalEnglishVoiceProfile();
        }

        const descriptions = {
            'auto': '🌐 Auto: Global WHO Synthesis active (TCM + Ayurveda + African + Western)',
            'tcm': '☯️ TCM: Traditional Chinese Medicine active (Yin/Yang, Qi & Meridians)',
            'ayurveda': '🕉️ Ayurveda: Tridosha (Vata/Pitta/Kapha) balancing active',
            'african': '🌍 African: Indigenous Ethnobotanical Phytotherapy active (Dr. Aisha)',
            'western': '🌿 Western: Clinical Pharmacology & Active Bioactives active'
        };

        if (showNotification && typeof window.showToast === 'function') {
            window.showToast(descriptions[modalityKey] || '🌐 Clinical Modality Updated', 'success');
        }
    }

    async function detectUserLocationAndModality() {
        try {
            let savedModality = null;
            try { savedModality = localStorage.getItem('herbalist_modality'); } catch(e) {}

            // Priority Layer 1: Native Server-Side Network Header Detection (/api/geo/detect)
            try {
                const geoRes = await fetch('/api/geo/detect');
                if (geoRes.ok) {
                    const geoData = await geoRes.json();
                    if (geoData && geoData.country_code && geoData.country_code !== 'GL') {
                        userLocationData.country = geoData.country_name;
                        userLocationData.country_code = geoData.country_code;
                        userLocationData.detected_tradition = geoData.suggested_modality;

                        if (!savedModality && geoData.suggested_modality !== 'auto') {
                            changeClinicalModality(geoData.suggested_modality, false);
                        }
                        updateModalityDropdownLabels(geoData.suggested_modality, geoData.country_name);
                        if (typeof window.syncRegionalEnglishVoiceProfile === 'function') {
                            window.syncRegionalEnglishVoiceProfile();
                        }
                        return;
                    }
                }
            } catch(netErr) {}

            // Priority Layer 2: Device / Browser Timezone Fallback
            const tz = (typeof Intl !== 'undefined' && Intl.DateTimeFormat && Intl.DateTimeFormat().resolvedOptions().timeZone) || '';
            userLocationData.timezone = tz;

            let detectedModality = 'auto';
            let countryName = 'Global';

            if (tz.includes('Kolkata') || tz.includes('Calcutta') || tz.includes('India') || tz.includes('Colombo') || tz.includes('Kathmandu') || tz.includes('Dhaka')) {
                detectedModality = 'ayurveda';
                countryName = 'India & South Asia';
                userLocationData.country_code = 'IN';
            } else if (tz.includes('Lagos') || tz.includes('Accra') || tz.includes('Johannesburg') || tz.includes('Nairobi') || tz.includes('Cairo') || tz.includes('Africa')) {
                detectedModality = 'african';
                countryName = 'African Region';
                userLocationData.country_code = 'AF';
            } else if (tz.includes('Shanghai') || tz.includes('Hong_Kong') || tz.includes('Taipei') || tz.includes('Tokyo') || tz.includes('Seoul') || tz.includes('Asia')) {
                detectedModality = 'tcm';
                countryName = 'East Asia';
                userLocationData.country_code = 'EA';
            } else if (tz.includes('New_York') || tz.includes('Chicago') || tz.includes('Los_Angeles') || tz.includes('Denver') || tz.includes('Phoenix') || tz.includes('Detroit') || tz.includes('America')) {
                detectedModality = 'western';
                countryName = 'United States';
                userLocationData.country_code = 'US';
            } else if (tz.includes('London') || tz.includes('Berlin') || tz.includes('Paris') || tz.includes('Toronto') || tz.includes('Sydney') || tz.includes('Europe')) {
                detectedModality = 'western';
                countryName = 'Western Clinical Region';
                userLocationData.country_code = 'WEST';
            }

            userLocationData.country = countryName;
            userLocationData.detected_tradition = detectedModality;

            if (!savedModality && detectedModality !== 'auto') {
                changeClinicalModality(detectedModality, false);
            }

            updateModalityDropdownLabels(detectedModality, countryName);
            if (typeof window.syncRegionalEnglishVoiceProfile === 'function') {
                window.syncRegionalEnglishVoiceProfile();
            }

        } catch (err) {
            console.log("[Geolocation Notice]:", err);
        }
    }

    function updateModalityDropdownLabels(detectedModality, countryName) {
        const modalitySelector = document.getElementById('clinical-modality-selector');
        if (modalitySelector) {
            if (detectedModality === 'ayurveda') {
                const opt = modalitySelector.querySelector('option[value="ayurveda"]');
                if (opt) opt.innerText = '🕉️ Ayurveda (India 🇮🇳 Active)';
            } else if (detectedModality === 'african') {
                const opt = modalitySelector.querySelector('option[value="african"]');
                if (opt) opt.innerText = '🌍 African Ethnomedicine (Africa 🌍 Active)';
            } else if (detectedModality === 'tcm') {
                const opt = modalitySelector.querySelector('option[value="tcm"]');
                if (opt) opt.innerText = '☯️ TCM (East Asia 🇨🇳 Active)';
            }
            modalitySelector.value = window.activeClinicalModality || 'auto';
        }
    }

    // Attach to window
    window.changeClinicalModality = changeClinicalModality;
    window.detectUserLocationAndModality = detectUserLocationAndModality;
    window.updateModalityDropdownLabels = updateModalityDropdownLabels;

})(window);
