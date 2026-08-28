/**
 * ═══════════════════════════════════════════════════════════════════
 * HERBALIST AI — COMMAND PALETTE & SLASH COMMANDS SUITE
 * Raycast-standard spotlight overlay (Ctrl+K) & in-chat slash actions
 * ═══════════════════════════════════════════════════════════════════
 */

(function(window) {
    'use strict';

    const COMMANDS = [
        { id: 'new_chat', title: 'Start New Consultation', badge: 'Action', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2ecc71" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>', action: () => window.startNewChat?.() },
        { id: 'live_voice', title: 'Start Hands-Free Live Voice Call (VAD)', badge: 'Voice', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2ecc71" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>', action: () => window.LiveVoiceCall?.start() },
        { id: 'recovery_tracker', title: 'Open Biomarker Recovery Tracker (7/30-Day)', badge: 'Health', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>', action: () => window.RecoveryTracker?.open() },
        { id: 'cyp450_matrix', title: 'Open Drug-Herb CYP450 Safety Matrix', badge: 'Safety', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f1c40f" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>', action: () => window.CYP450SafetyMatrix?.open() },
        { id: 'export_pdf', title: 'Export Active Prescription to PDF', badge: 'Export', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#e74c3c" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 1-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>', action: () => window.PrescriptionPDF?.exportActiveRx() },
        { id: 'search_herb', title: 'Lookup Herb Monograph in Pharmacopeia', badge: 'Database', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2ecc71" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path></svg>', action: () => triggerSlashInput('/herb ') },
        { id: 'calc_posology', title: 'Calculate Weight-Adjusted Posology', badge: 'Clinical', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f39c12" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18"></path><path d="M6 7l6-4 6 4"></path><path d="M4 14l2-7 2 7a3 3 0 0 0 6 0l2-7 2 7a3 3 0 0 0 6 0"></path></svg>', action: () => triggerSlashInput('/dosage ') },
        { id: 'lang_hausa', title: 'Switch Voice to Hausa (Dr. Amina)', badge: 'Language', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>', action: () => setVoiceLang('ha') },
        { id: 'lang_yoruba', title: 'Switch Voice to Yoruba (Dr. Adebayo)', badge: 'Language', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>', action: () => setVoiceLang('yo') },
        { id: 'lang_igbo', title: 'Switch Voice to Igbo (Dr. Chioma)', badge: 'Language', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1 4-10z"></path></svg>', action: () => setVoiceLang('ig') },
        { id: 'lang_ng_en', title: 'Switch Voice to Nigerian English (Dr. Aisha)', badge: 'Language', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>', action: () => setVoiceLang('en_ng') }
    ];

    const SLASH_COMMANDS = [
        { cmd: '/herb', desc: 'Lookup plant phytochemicals and dosage (e.g. /herb bitter leaf)', example: '/herb ' },
        { cmd: '/safety', desc: 'Check herb-drug safety matrix (e.g. /safety metformin bitter leaf)', example: '/safety ' },
        { cmd: '/dosage', desc: 'Calculate weight-adjusted decoction posology', example: '/dosage ' },
        { cmd: '/live', desc: 'Launch hands-free live voice call with VAD', example: '/live' },
        { cmd: '/tracker', desc: 'Open 7/30-day health diary & recovery charts', example: '/tracker' },
        { cmd: '/matrix', desc: 'Open interactive CYP450 drug-herb safety matrix', example: '/matrix' },
        { cmd: '/pdf', desc: 'Generate printable clinical prescription PDF', example: '/pdf' },
        { cmd: '/clear', desc: 'Start a clean new consultation session', example: '/clear' }
    ];

    function setVoiceLang(code) {
        if (typeof window.switchChatVoiceLanguage === 'function') {
            window.switchChatVoiceLanguage(code);
        } else if (typeof window.showToast === 'function') {
            window.showToast(`Voice set to: ${code.toUpperCase()}`, 'info', 2000);
        }
    }

    function triggerSlashInput(text) {
        const input = document.getElementById('user-input');
        if (input) {
            input.value = text;
            if (typeof input.focus === 'function') input.focus();
        }
    }

    const CommandPalette = {
        overlayEl: null,
        inputEl: null,
        resultsEl: null,
        selectedIndex: 0,
        filteredCommands: [...COMMANDS],

        init: function() {
            this.createPaletteDOM();
            this.bindGlobalShortcuts();
            this.bindSlashAutocomplete();
        },

        createPaletteDOM: function() {
            let el = document.getElementById('command-palette-overlay');
            if (el) {
                this.overlayEl = el;
                this.inputEl = document.getElementById('palette-search-input');
                this.resultsEl = document.getElementById('palette-results-list');
                return;
            }

            this.overlayEl = document.createElement('div');
            this.overlayEl.id = 'command-palette-overlay';
            this.overlayEl.innerHTML = `
                <div class="command-palette-modal" onclick="event.stopPropagation()">
                    <div class="command-palette-input-wrapper">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2ecc71" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                        <input type="text" class="command-palette-input" id="palette-search-input" placeholder="Type a command or search action (or use / for slash commands)..." autocomplete="off" />
                        <span style="font-size:11px;color:#7f8c8d;border:1px solid rgba(255,255,255,0.15);padding:2px 6px;border-radius:4px;font-family:monospace;">ESC</span>
                    </div>
                    <div class="command-palette-results" id="palette-results-list"></div>
                </div>
            `;

            this.overlayEl.onclick = () => this.close();
            document.body.appendChild(this.overlayEl);

            this.inputEl = document.getElementById('palette-search-input');
            this.resultsEl = document.getElementById('palette-results-list');

            if (this.inputEl) {
                this.inputEl.addEventListener('input', (e) => this.onSearch(e.target.value));
                this.inputEl.addEventListener('keydown', (e) => this.onKeyDown(e));
            }
        },

        bindGlobalShortcuts: function() {
            window.addEventListener('keydown', (e) => {
                // Ctrl + K or Cmd + K
                if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
                    e.preventDefault();
                    this.toggle();
                } else if (e.key === 'Escape' && this.isOpen()) {
                    this.close();
                }
            });
        },

        isOpen: function() {
            return this.overlayEl && this.overlayEl.style.display === 'flex';
        },

        open: function() {
            if (!this.overlayEl) this.createPaletteDOM();
            this.overlayEl.style.display = 'flex';
            this.inputEl.value = '';
            this.filteredCommands = [...COMMANDS];
            this.selectedIndex = 0;
            this.renderResults();
            setTimeout(() => {
                if (this.inputEl && typeof this.inputEl.focus === 'function') this.inputEl.focus();
            }, 50);
        },

        close: function() {
            if (this.overlayEl) this.overlayEl.style.display = 'none';
        },

        toggle: function() {
            if (this.isOpen()) this.close();
            else this.open();
        },

        onSearch: function(query) {
            const q = (query || '').toLowerCase().trim();
            if (!q) {
                this.filteredCommands = [...COMMANDS];
            } else {
                this.filteredCommands = COMMANDS.filter(cmd => 
                    cmd.title.toLowerCase().includes(q) || 
                    cmd.badge.toLowerCase().includes(q) ||
                    cmd.id.includes(q)
                );
            }
            this.selectedIndex = 0;
            this.renderResults();
        },

        renderResults: function() {
            if (this.filteredCommands.length === 0) {
                this.resultsEl.innerHTML = '<div style="color:var(--text-muted,#7f8c8d);font-size:12px;padding:16px;text-align:center;">No matching clinical commands found.</div>';
                return;
            }

            this.resultsEl.innerHTML = this.filteredCommands.map((cmd, idx) => `
                <div class="command-item ${idx === this.selectedIndex ? 'selected' : ''}" onclick="CommandPalette.executeIndex(${idx})">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span style="font-size:16px;">${cmd.icon}</span>
                        <span>${cmd.title}</span>
                    </div>
                    <span class="command-item-badge">${cmd.badge}</span>
                </div>
            `).join('');
        },

        onKeyDown: function(e) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.selectedIndex = (this.selectedIndex + 1) % this.filteredCommands.length;
                this.renderResults();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.selectedIndex = (this.selectedIndex - 1 + this.filteredCommands.length) % this.filteredCommands.length;
                this.renderResults();
            } else if (e.key === 'Enter') {
                e.preventDefault();
                this.executeIndex(this.selectedIndex);
            }
        },

        executeIndex: function(idx) {
            const cmd = this.filteredCommands[idx];
            if (cmd) {
                this.close();
                cmd.action();
            }
        },

        /**
         * In-chat Slash Commands autocomplete dropdown
         */
        bindSlashAutocomplete: function() {
            const chatInput = document.getElementById('user-input');
            if (!chatInput) return;

            let dropdown = document.getElementById('slash-autocomplete-dropdown');
            if (!dropdown) {
                dropdown = document.createElement('div');
                dropdown.id = 'slash-autocomplete-dropdown';
                const parent = chatInput.closest('.input-wrapper') || chatInput.parentElement;
                if (parent) {
                    parent.style.position = 'relative';
                    parent.appendChild(dropdown);
                }
            }

            chatInput.addEventListener('input', (e) => {
                const val = e.target.value;
                if (val.startsWith('/')) {
                    const query = val.toLowerCase().trim();
                    const matches = SLASH_COMMANDS.filter(s => s.cmd.startsWith(query) || s.desc.toLowerCase().includes(query.replace('/', '')));

                    if (matches.length > 0) {
                        dropdown.innerHTML = matches.map(s => `
                            <div style="display:flex;align-items:center;justify-content:space-between;padding:7px 10px;border-radius:8px;cursor:pointer;color:#fff;font-size:12px;" onmouseover="this.style.background='rgba(46,204,113,0.15)'" onmouseout="this.style.background='transparent'" onclick="CommandPalette.selectSlash('${s.example}')">
                                <strong style="color:var(--accent-green,#2ecc71);font-family:monospace;">${s.cmd}</strong>
                                <span style="color:rgba(255,255,255,0.7);font-size:11px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:200px;">${s.desc}</span>
                            </div>
                        `).join('');
                        dropdown.style.display = 'flex';
                    } else {
                        dropdown.style.display = 'none';
                    }
                } else {
                    dropdown.style.display = 'none';
                }
            });

            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    dropdown.style.display = 'none';
                }
            });
        },

        selectSlash: function(exampleText) {
            const chatInput = document.getElementById('user-input');
            const dropdown = document.getElementById('slash-autocomplete-dropdown');
            if (chatInput) {
                chatInput.value = exampleText;
                if (typeof chatInput.focus === 'function') chatInput.focus();
            }
            if (dropdown) dropdown.style.display = 'none';

            // If it's an immediate action like /clear or /pdf or /call, execute it directly
            if (exampleText === '/clear') {
                if (chatInput) chatInput.value = '';
                window.startNewChat?.();
            } else if (exampleText === '/pdf') {
                if (chatInput) chatInput.value = '';
                window.PrescriptionPDF?.exportActiveRx();
            } else if (exampleText === '/call') {
                if (chatInput) chatInput.value = '';
                window.startTelehealthCall?.();
            }
        }
    };

    window.CommandPalette = CommandPalette;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => CommandPalette.init());
    } else {
        CommandPalette.init();
    }
})(window);
