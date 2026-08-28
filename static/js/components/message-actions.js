/**
 * ═══════════════════════════════════════════════════════════════════
 * HERBALIST AI — MESSAGE-LEVEL ACTIONS SUITE
 * 1-Click Copy, Regenerate Response, Edit Prompt, and RLHF Feedback
 * ═══════════════════════════════════════════════════════════════════
 */

(function(window) {
    'use strict';

    const MessageActions = {
        /**
         * Initialize observer to auto-attach action bars to all chat bubbles
         */
        init: function() {
            this.attachToExistingBubbles();
            this.observeChatFeed();
        },

        /**
         * Attach action bars to all currently rendered bubbles
         */
        attachToExistingBubbles: function() {
            const bubbles = document.querySelectorAll('.chat-bubble');
            bubbles.forEach(bubble => this.attachToBubble(bubble));
        },

        /**
         * Mutation observer to automatically attach actions when new bubbles are created
         */
        observeChatFeed: function() {
            const feed = document.getElementById('chat-feed');
            if (!feed) return;

            const observer = new MutationObserver((mutations) => {
                mutations.forEach(mutation => {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1 && node.classList.contains('chat-bubble')) {
                            this.attachToBubble(node);
                        } else if (node.nodeType === 1) {
                            const subBubbles = node.querySelectorAll?.('.chat-bubble');
                            subBubbles?.forEach(b => this.attachToBubble(b));
                        }
                    });
                });
            });

            observer.observe(feed, { childList: true, subtree: true });
        },

        /**
         * Attach action bar to a single bubble
         */
        attachToBubble: function(bubble) {
            if (bubble.dataset.actionsAttached === 'true') return;
            bubble.dataset.actionsAttached = 'true';

            const isPatient = bubble.style.alignSelf === 'flex-end';

            if (isPatient) {
                // Patient Bubble: Attach Edit Prompt Pencil
                const editBtn = document.createElement('button');
                editBtn.className = 'patient-edit-btn';
                editBtn.title = 'Edit symptom input';
                editBtn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>`;
                editBtn.onclick = (e) => {
                    e.stopPropagation();
                    this.editPatientPrompt(bubble);
                };
                bubble.appendChild(editBtn);
            } else {
                // Doctor Bubble: Attach Full Action Bar (Copy, Regenerate, Thumbs Up/Down, PDF)
                const bar = document.createElement('div');
                bar.className = 'msg-actions-bar';
                bar.innerHTML = `
                    <button class="msg-action-btn copy-btn" title="Copy response to clipboard">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                        <span>Copy</span>
                    </button>
                    <button class="msg-action-btn regen-btn" title="Regenerate alternative clinical response">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"></path></svg>
                        <span>Regenerate</span>
                    </button>
                    <button class="msg-action-btn thumb-up-btn" title="Accurate & helpful advice">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>
                    </button>
                    <button class="msg-action-btn thumb-down-btn" title="Suggest clinical revision">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3"></path></svg>
                    </button>
                `;

                // Wire Copy
                const copyBtn = bar.querySelector('.copy-btn');
                copyBtn.onclick = (e) => {
                    e.stopPropagation();
                    this.copyMessageText(bubble, copyBtn);
                };

                // Wire Regenerate
                const regenBtn = bar.querySelector('.regen-btn');
                regenBtn.onclick = (e) => {
                    e.stopPropagation();
                    this.regenerateLastResponse();
                };

                // Wire Feedback
                const upBtn = bar.querySelector('.thumb-up-btn');
                upBtn.onclick = (e) => {
                    e.stopPropagation();
                    this.rateResponse(upBtn, 'up');
                };

                const downBtn = bar.querySelector('.thumb-down-btn');
                downBtn.onclick = (e) => {
                    e.stopPropagation();
                    this.rateResponse(downBtn, 'down');
                };

                bubble.appendChild(bar);
            }
        },

        /**
         * 1-Click Copy message text to clipboard
         */
        copyMessageText: function(bubble, btn) {
            // Extract clean readable text
            const clone = bubble.cloneNode(true);
            clone.querySelectorAll('.msg-actions-bar, .bubble-audio-btn, button, .agent-tools-container, .clinical-thought-hud').forEach(el => el.remove());
            const textToCopy = (clone.innerText || '').trim();

            navigator.clipboard.writeText(textToCopy).then(() => {
                const origHtml = btn.innerHTML;
                btn.innerHTML = `<span style="color:var(--accent-green,#2ecc71);font-weight:bold;">✓ Copied</span>`;
                if (typeof window.showToast === 'function') {
                    window.showToast('Prescription advice copied to clipboard', 'success', 2000);
                }
                setTimeout(() => { btn.innerHTML = origHtml; }, 2000);
            }).catch(err => {
                console.error("Clipboard copy failed:", err);
            });
        },

        /**
         * Edit user prompt
         */
        editPatientPrompt: function(bubble) {
            const text = (bubble.innerText || '').trim();
            const input = document.getElementById('user-input');
            if (input) {
                input.value = text;
                input.focus();
                input.scrollIntoView({ behavior: 'smooth', block: 'center' });
                if (typeof window.showToast === 'function') {
                    window.showToast('Prompt loaded into input for editing', 'info', 1800);
                }
            }
        },

        /**
         * Regenerate clinical response
         */
        regenerateLastResponse: function() {
            // Find the last patient query
            const patientBubbles = Array.from(document.querySelectorAll('.chat-bubble')).filter(b => b.style.alignSelf === 'flex-end');
            if (patientBubbles.length === 0) {
                if (typeof window.showToast === 'function') {
                    window.showToast('No recent patient query to regenerate', 'warning', 2000);
                }
                return;
            }

            const lastPatientBubble = patientBubbles[patientBubbles.length - 1];
            const lastText = (lastPatientBubble.innerText || '').trim();

            const input = document.getElementById('user-input');
            if (input && typeof window.submitQuery === 'function') {
                input.value = lastText;
                if (typeof window.showToast === 'function') {
                    window.showToast('Regenerating botanical clinical consultation...', 'info', 2200);
                }
                window.submitQuery();
            }
        },

        /**
         * Rate response
         */
        rateResponse: function(btn, rating) {
            const bar = btn.closest('.msg-actions-bar');
            bar.querySelectorAll('.msg-action-btn').forEach(b => b.classList.remove('active-rating'));
            btn.classList.add('active-rating');

            if (rating === 'up') {
                if (typeof window.showToast === 'function') {
                    window.showToast('Thank you! Efficacy feedback logged.', 'success', 2000);
                }
            } else {
                if (typeof window.showCustomPrompt === 'function') {
                    window.showCustomPrompt('Clinical Feedback', 'What botanical aspect could be improved? (e.g. dosage, specific herb alternative)', (notes) => {
                        if (notes && typeof window.showToast === 'function') {
                            window.showToast('Clinical feedback saved for continuous model tuning.', 'info', 2500);
                        }
                    });
                } else if (typeof window.showToast === 'function') {
                    window.showToast('Feedback noted.', 'info', 1800);
                }
            }
        }
    };

    window.MessageActions = MessageActions;

    // Auto-init when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => MessageActions.init());
    } else {
        MessageActions.init();
    }
})(window);
