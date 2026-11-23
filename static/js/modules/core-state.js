/**
 * ═══════════════════════════════════════════════════════════════════
 * HERBALIST AI — CORE APPLICATION & SESSION STATE MODULE
 * Global variables, localStorage synchronization, and reactive store.
 * ═══════════════════════════════════════════════════════════════════
 */

(function(window) {
    'use strict';

    // Global Session & Modality State
    let activeClinicalModality = localStorage.getItem('herbalist_modality') || 'auto';
    let currentClinicalModality = activeClinicalModality;
    let currentSessionId = localStorage.getItem('herbalist_active_session_id') || ('SESS_' + Date.now());

    // Chat History & Profile State
    let currentUserState = null;
    let currentChatMessages = [];
    let activePatientProfile = {
        name: "Patient Guest",
        age: 30,
        gender: "Male",
        weight_kg: 70.0,
        medical_history: "None reported",
        allergies: "None reported",
        chronic_conditions: "None"
    };

    // Active Clinical Prescription Payloads
    let activePrescriptionPayload = null;
    let canvasActivePrescription = null;
    let currentCanvasBatchLiters = 2.0;
    let checkedHerbDispensaryItems = new Set();
    let chronoDoseChecklist = { morning: false, midday: false, evening: false };

    // Attach to window for public facade backwards-compatibility
    window.activeClinicalModality = activeClinicalModality;
    window.currentClinicalModality = currentClinicalModality;
    window.currentSessionId = currentSessionId;
    window.currentUserState = currentUserState;
    window.currentChatMessages = currentChatMessages;
    window.activePatientProfile = activePatientProfile;
    window.activePrescriptionPayload = activePrescriptionPayload;
    window.canvasActivePrescription = canvasActivePrescription;
    window.currentCanvasBatchLiters = currentCanvasBatchLiters;
    window.checkedHerbDispensaryItems = checkedHerbDispensaryItems;
    window.chronoDoseChecklist = chronoDoseChecklist;

    // Helper functions
    window.getActiveUserStorageKey = function() {
        try {
            const storedUser = localStorage.getItem('herbalist_user');
            const storedProfile = localStorage.getItem('herbalist_user_profile');
            const user = JSON.parse(storedUser || storedProfile || 'null');
            if (user && (user.id || user.uid || user.email)) {
                const cleanId = String(user.id || user.uid || user.email).replace(/[^a-zA-Z0-9_]/g, '_');
                return `herbalist_chat_sessions_${cleanId}`;
            }
        } catch (e) {}
        return 'herbalist_chat_sessions_guest';
    };

    window.getLocalChatSessions = function() {
        const key = window.getActiveUserStorageKey();
        try {
            const raw = localStorage.getItem(key);
            return raw ? JSON.parse(raw) : {};
        } catch(e) {
            return {};
        }
    };

    window.saveLocalChatSessions = function(sessions) {
        const key = window.getActiveUserStorageKey();
        try {
            localStorage.setItem(key, JSON.stringify(sessions));
        } catch(e) {
            console.warn("[Local Sessions Save Notice]", e);
        }
    };

    window.persistActiveChatSession = function() {
        if (!window.currentSessionId) return;
        const sessions = window.getLocalChatSessions();
        sessions[window.currentSessionId] = {
            id: window.currentSessionId,
            messages: window.currentChatMessages || [],
            prescription: window.activePrescriptionPayload || null,
            modality: window.currentClinicalModality || 'auto',
            updatedAt: Date.now()
        };
        window.saveLocalChatSessions(sessions);
    };

})(window);
