/**
 * ═══════════════════════════════════════════════════════════════════
 * HERBALIST AI — AGENT TOOL-EXECUTION TRANSPARENCY COMPONENT
 * Real-time telemetry displaying active agent tool execution pills,
 * live timers, and completion badges during clinical reasoning.
 * ═══════════════════════════════════════════════════════════════════
 */

(function(window) {
    'use strict';

    const AgentTransparency = {
        activeTools: {},
        timers: {},

        // Default predefined clinical agent tools
        DEFAULT_TOOLS: [
            { id: 'vector_search', icon: '🔍', label: 'Querying Qdrant Botanical Vector Index' },
            { id: 'phytochem', icon: '🧬', label: 'Analyzing Phytochemicals & Synergies' },
            { id: 'drug_safety', icon: '🛡️', label: 'Cross-Referencing CYP450 Drug-Herb Matrix' },
            { id: 'posology', icon: '⚖️', label: 'Calculating Weight & Age Adjusted Posology' },
            { id: 'compounding', icon: '📄', label: 'Compounding Structured Phytotherapy Prescription' }
        ],

        /**
         * Render transparency HUD container inside a streaming bubble
         */
        renderHUD: function(containerId, initialPhase = 'Diagnostic Intake') {
            const container = document.getElementById(containerId);
            if (!container) return;

            container.innerHTML = `
                <div class="agent-tools-container" id="agent-tools-${containerId}">
                    <div class="agent-tools-header" onclick="AgentTransparency.toggleCollapse('${containerId}')">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span class="tool-pulse-dot"></span>
                            <span>Agent Clinical Sub-Systems:</span>
                            <span id="agent-hud-status-${containerId}" style="color:#fff;font-weight:600;">${initialPhase}</span>
                        </div>
                        <span id="agent-hud-arrow-${containerId}" style="font-size:10px;opacity:0.7;">▼</span>
                    </div>
                    <div class="agent-tools-list" id="agent-tools-list-${containerId}"></div>
                </div>
            `;
        },

        /**
         * Start an agent tool execution pill
         */
        startTool: function(containerId, toolId, customLabel, icon = '⚙️') {
            const listEl = document.getElementById(`agent-tools-list-${containerId}`);
            if (!listEl) return;

            const existing = document.getElementById(`tool-pill-${containerId}-${toolId}`);
            if (existing) {
                existing.className = 'agent-tool-pill running';
                return;
            }

            const startTime = Date.now();
            this.activeTools[`${containerId}_${toolId}`] = startTime;

            const pill = document.createElement('div');
            pill.id = `tool-pill-${containerId}-${toolId}`;
            pill.className = 'agent-tool-pill running';
            pill.innerHTML = `
                <div style="display:flex;align-items:center;gap:8px;">
                    <span>${icon}</span>
                    <span style="font-weight:500;">${customLabel}</span>
                </div>
                <div style="display:flex;align-items:center;gap:6px;">
                    <span class="tool-pulse-dot"></span>
                    <span class="tool-duration-badge" id="timer-${containerId}-${toolId}">0.1s</span>
                </div>
            `;
            listEl.appendChild(pill);

            // Start live timer
            this.timers[`${containerId}_${toolId}`] = setInterval(() => {
                const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
                const timerEl = document.getElementById(`timer-${containerId}-${toolId}`);
                if (timerEl) timerEl.innerText = `${elapsed}s`;
            }, 100);
        },

        /**
         * Complete an agent tool execution
         */
        completeTool: function(containerId, toolId) {
            const key = `${containerId}_${toolId}`;
            if (this.timers[key]) {
                clearInterval(this.timers[key]);
                delete this.timers[key];
            }

            const pill = document.getElementById(`tool-pill-${containerId}-${toolId}`);
            if (pill) {
                pill.className = 'agent-tool-pill completed';
                const pulseDot = pill.querySelector('.tool-pulse-dot');
                if (pulseDot) {
                    pulseDot.outerHTML = '<span style="color:var(--accent-green,#2ecc71);font-size:11px;font-weight:bold;">✓</span>';
                }
            }
        },

        /**
         * Toggle HUD collapse
         */
        toggleCollapse: function(containerId) {
            const listEl = document.getElementById(`agent-tools-list-${containerId}`);
            const arrowEl = document.getElementById(`agent-hud-arrow-${containerId}`);
            if (!listEl) return;

            if (listEl.style.display === 'none') {
                listEl.style.display = 'flex';
                if (arrowEl) arrowEl.innerText = '▼';
            } else {
                listEl.style.display = 'none';
                if (arrowEl) arrowEl.innerText = '▲';
            }
        },

        /**
         * Finish all running tools when stream ends
         */
        finishAll: function(containerId) {
            const listEl = document.getElementById(`agent-tools-list-${containerId}`);
            if (!listEl) return;

            const runningPills = listEl.querySelectorAll('.agent-tool-pill.running');
            runningPills.forEach(pill => {
                pill.className = 'agent-tool-pill completed';
                const pulseDot = pill.querySelector('.tool-pulse-dot');
                if (pulseDot) pulseDot.outerHTML = '<span style="color:var(--accent-green,#2ecc71);font-size:11px;font-weight:bold;">✓</span>';
            });

            // Clear all timers for this container
            Object.keys(this.timers).forEach(k => {
                if (k.startsWith(containerId)) {
                    clearInterval(this.timers[k]);
                    delete this.timers[k];
                }
            });

            const statusEl = document.getElementById(`agent-hud-status-${containerId}`);
            if (statusEl) statusEl.innerText = 'Prescription Compounded';
        }
    };

    window.AgentTransparency = AgentTransparency;
})(window);
