/**
 * ═══════════════════════════════════════════════════════════════════
 * HERBALIST AI — COMMAND PALETTE & SLASH COMMANDS SUITE
 * Raycast-standard spotlight overlay (Ctrl+K) & in-chat slash actions
 * ═══════════════════════════════════════════════════════════════════
 */

(function(window) {
    'use strict';

    const COMMANDS = [
        { id: 'new_chat', title: 'Start New Consultation', badge: 'Action', icon: '✨', action: () => window.startNewChat?.() },
        { id: 'export_pdf', title: 'Export Active Prescription to PDF', badge: 'Export', icon: '📄', action: () => window.PrescriptionPDF?.exportActiveRx() },
        { id: 'telehealth', title: 'Start Telehealth Live Voice Call', badge: 'Voice', icon: '📞', action: () => window.startTelehealthCall?.() },
        { id: 'search_herb', title: 'Lookup Herb Monograph in Pharmacopeia', badge: 'Database', icon: '🌿', action: () => triggerSlashInput('/herb ') },
        { id: 'safety_check', title: 'Check Drug-Herb Interaction Matrix', badge: 'Safety', icon: '🛡️', action: () => triggerSlashInput('/safety ') },
        { id: 'calc_posology', title: 'Calculate Weight-Adjusted Posology', badge: 'Clinical', icon: '⚖️', action: () => triggerSlashInput('/dosage ') },
        { id: 'lang_hausa', title: 'Switch Voice to Hausa (Dr. Amina)', badge: 'Language', icon: '🇳🇬', action: () => setVoiceLang('ha') },
        { id: 'lang_yoruba', title: 'Switch Voice to Yoruba (Dr. Adebayo)', badge: 'Language', icon: '🇳🇬', action: () => setVoiceLang('yo') },
        { id: 'lang_igbo', title: 'Switch Voice to Igbo (Dr. Chioma)', badge: 'Language', icon: '🇳🇬', action: () => setVoiceLang('ig') },
        { id: 'lang_ng_en', title: 'Switch Voice to Nigerian English (Dr. Aisha)', badge: 'Language', icon: '🇳🇬', action: () => setVoiceLang('en_ng') }
    ];

    const SLASH_COMMANDS = [
        { cmd: '/herb', desc: 'Lookup plant phytochemicals and dosage (e.g. /herb bitter leaf)', example: '/herb ' },
        { cmd: '/safety', desc: 'Check herb-drug safety matrix (e.g. /safety metformin bitter leaf)', example: '/safety ' },
        { cmd: '/dosage', desc: 'Calculate weight-adjusted decoction posology', example: '/dosage ' },
        { cmd: '/pdf', desc: 'Generate printable clinical prescription PDF', example: '/pdf' },
        { cmd: '/clear', desc: 'Start a clean new consultation session', example: '/clear' },
        { cmd: '/call', desc: 'Launch live telehealth voice consultation', example: '/call' }
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
            input.focus();
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
            if (document.getElementById('command-palette-overlay')) return;

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

            this.inputEl.addEventListener('input', (e) => this.onSearch(e.target.value));
            this.inputEl.addEventListener('keydown', (e) => this.onKeyDown(e));
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
            setTimeout(() => this.inputEl.focus(), 50);
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
                chatInput.focus();
            }
            if (dropdown) dropdown.style.display = 'none';

            // If it's an immediate action like /clear or /pdf or /call, execute it directly
            if (exampleText === '/clear') {
                chatInput.value = '';
                window.startNewChat?.();
            } else if (exampleText === '/pdf') {
                chatInput.value = '';
                window.PrescriptionPDF?.exportActiveRx();
            } else if (exampleText === '/call') {
                chatInput.value = '';
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
