/**
 * ═══════════════════════════════════════════════════════════════════
 * HERBALIST AI — TOAST & CUSTOM THEME DIALOG ENGINE
 * Modern glassmorphic alerts, confirms, and toast notifications.
 * ═══════════════════════════════════════════════════════════════════
 */

(function(window) {
    'use strict';

    function showToast(message, type = 'info', duration = 3600) {
        if (!message) return;
        // Kept byte-for-byte behaviorally aligned with the legacy inline toast
        // while index.html delegates to this module during the migration.
        let cleanMsg = String(message)
            .replace(/^[\s\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F1E0}-\u{1F1FF}💬🌿✨🔔🚨⚠️✅❌ℹ️📋📌✏️🗑️🩺\?]+\s*/u, '')
            .trim();
        if (!cleanMsg) cleanMsg = String(message).trim();

        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = 'position:fixed;top:22px;right:22px;z-index:999999;display:flex;flex-direction:column;gap:10px;pointer-events:none;max-width:390px;width:calc(100% - 44px);';
            document.body.appendChild(container);
        }

        const iconBadgeMap = {
            success: {
                svg: `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#2ecc71" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,
                bg: 'rgba(46, 204, 113, 0.15)',
                border: 'rgba(46, 204, 113, 0.35)',
                glow: 'rgba(46, 204, 113, 0.18)',
                cardBorder: 'rgba(46, 204, 113, 0.32)'
            },
            warning: {
                svg: `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#f1c40f" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
                bg: 'rgba(241, 196, 15, 0.16)',
                border: 'rgba(241, 196, 15, 0.38)',
                glow: 'rgba(241, 196, 15, 0.2)',
                cardBorder: 'rgba(241, 196, 15, 0.35)'
            },
            error: {
                svg: `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#ff6b6b" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`,
                bg: 'rgba(231, 76, 60, 0.16)',
                border: 'rgba(231, 76, 60, 0.38)',
                glow: 'rgba(231, 76, 60, 0.22)',
                cardBorder: 'rgba(231, 76, 60, 0.35)'
            },
            info: {
                svg: `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`,
                bg: 'rgba(52, 152, 219, 0.15)',
                border: 'rgba(52, 152, 219, 0.35)',
                glow: 'rgba(52, 152, 219, 0.2)',
                cardBorder: 'rgba(52, 152, 219, 0.32)'
            }
        };

        const cfg = iconBadgeMap[type] || iconBadgeMap.info;
        const toast = document.createElement('div');
        toast.className = `herbalist-modern-toast toast-${type}`;
        toast.style.cssText = `
            pointer-events: auto;
            background: linear-gradient(135deg, rgba(16, 26, 20, 0.94) 0%, rgba(10, 16, 12, 0.97) 100%);
            border: 1px solid ${cfg.cardBorder};
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.7), 0 0 24px ${cfg.glow};
            color: #f0f7f2;
            padding: 12px 14px;
            border-radius: 16px;
            font-family: 'Outfit', -apple-system, sans-serif;
            font-size: 13.5px;
            line-height: 1.45;
            display: flex;
            align-items: center;
            gap: 12px;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            transform: translateX(110px) scale(0.96);
            opacity: 0;
            transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s ease;
            cursor: pointer;
        `;

        toast.innerHTML = `
            <div style="width:34px;height:34px;border-radius:10px;background:${cfg.bg};border:1px solid ${cfg.border};display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 0 10px ${cfg.glow};">
                ${cfg.svg}
            </div>
            <div style="flex:1;word-break:break-word;font-weight:500;color:#e8f4ec;letter-spacing:-0.15px;">${cleanMsg}</div>
            <button type="button" aria-label="Close" style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);color:rgba(255,255,255,0.6);border-radius:8px;width:24px;height:24px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:12px;padding:0;flex-shrink:0;transition:all 0.2s;" onmouseover="this.style.color='#fff';this.style.background='rgba(255,255,255,0.15)'" onmouseout="this.style.color='rgba(255,255,255,0.6)';this.style.background='rgba(255,255,255,0.06)'" onclick="this.closest('.herbalist-modern-toast').remove()">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
        `;

        container.appendChild(toast);

        const triggerAnim = () => {
            toast.style.transform = 'translateX(0) scale(1)';
            toast.style.opacity = '1';
        };
        if (typeof requestAnimationFrame !== 'undefined') requestAnimationFrame(triggerAnim);
        else setTimeout(triggerAnim, 10);

        const safeRemove = () => {
            if (toast.remove) toast.remove();
            else if (toast.parentNode) toast.parentNode.removeChild(toast);
        };
        const timer = setTimeout(() => {
            toast.style.transform = 'translateX(90px) scale(0.95)';
            toast.style.opacity = '0';
            setTimeout(safeRemove, 320);
        }, duration);

        toast.onclick = (event) => {
            if (event.target.tagName !== 'BUTTON' && !event.target.closest('button')) {
                clearTimeout(timer);
                toast.style.transform = 'translateX(90px) scale(0.95)';
                toast.style.opacity = '0';
                setTimeout(safeRemove, 320);
            }
        };
    }

    function escapeDialogHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function showCustomConfirm(options = {}) {
        return new Promise((resolve) => {
            const title = options.title || 'Are you sure?';
            const message = options.message || 'Do you want to proceed with this action?';
            const confirmText = options.confirmText || 'Confirm';
            const cancelText = options.cancelText || 'Cancel';
            const isDestructive = options.isDestructive !== false;
            const icon = options.icon || (isDestructive ? '🗑️' : '🌿');

            let container = document.getElementById('custom-dialog-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'custom-dialog-container';
                document.body.appendChild(container);
            }

            container.innerHTML = `
                <div class="custom-dialog-overlay" id="active-custom-dialog">
                    <div class="custom-dialog-card ${isDestructive ? 'destructive' : ''}" role="dialog" aria-modal="true">
                        <div class="custom-dialog-header">
                            <div class="custom-dialog-icon-badge">${icon}</div>
                            <div style="flex: 1;">
                                <h4 class="custom-dialog-title">${escapeDialogHtml(title)}</h4>
                                <p class="custom-dialog-message">${escapeDialogHtml(message)}</p>
                            </div>
                        </div>
                        <div class="custom-dialog-actions">
                            <button type="button" class="custom-dialog-btn-cancel" id="custom-dialog-cancel-btn">${escapeDialogHtml(cancelText)}</button>
                            <button type="button" class="custom-dialog-btn-confirm ${isDestructive ? 'destructive' : ''}" id="custom-dialog-confirm-btn">${escapeDialogHtml(confirmText)}</button>
                        </div>
                    </div>
                </div>
            `;
            container.style.display = 'block';

            const confirmBtn = document.getElementById('custom-dialog-confirm-btn');
            const cancelBtn = document.getElementById('custom-dialog-cancel-btn');
            const overlay = document.getElementById('active-custom-dialog');

            function cleanup(result) {
                window.removeEventListener('keydown', handleKey);
                container.innerHTML = '';
                container.style.display = 'none';
                resolve(result);
            }

            function handleKey(e) {
                if (e.key === 'Escape') {
                    e.preventDefault();
                    cleanup(false);
                } else if (e.key === 'Enter') {
                    e.preventDefault();
                    cleanup(true);
                }
            }

            if (confirmBtn) confirmBtn.addEventListener('click', () => cleanup(true));
            if (cancelBtn) cancelBtn.addEventListener('click', () => cleanup(false));
            if (overlay) {
                overlay.addEventListener('click', (e) => {
                    if (e.target === overlay) cleanup(false);
                });
            }

            window.addEventListener('keydown', handleKey);
            if (confirmBtn) confirmBtn.focus();
        });
    }

    function showCustomPrompt(options = {}) {
        return new Promise((resolve) => {
            const title = typeof options === 'string' ? options : (options.title || 'Input Required');
            const message = typeof options === 'string' ? '' : (options.message || '');
            const placeholder = options.placeholder || 'Enter value...';
            const defaultValue = options.defaultValue || '';
            const confirmText = options.confirmText || 'Submit';
            const cancelText = options.cancelText || 'Cancel';
            const icon = options.icon || '✏️';

            let container = document.getElementById('custom-dialog-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'custom-dialog-container';
                document.body.appendChild(container);
            }

            container.innerHTML = `
                <div class="custom-dialog-overlay" id="active-custom-dialog">
                    <div class="custom-dialog-card" role="dialog" aria-modal="true">
                        <div class="custom-dialog-header">
                            <div class="custom-dialog-icon-badge">${icon}</div>
                            <div style="flex: 1;">
                                <h4 class="custom-dialog-title">${escapeDialogHtml(title)}</h4>
                                <p class="custom-dialog-message">${escapeDialogHtml(message)}</p>
                            </div>
                        </div>
                        <div class="custom-dialog-input-wrapper">
                            <input type="text" class="custom-dialog-input" id="custom-dialog-text-input" placeholder="${escapeDialogHtml(placeholder)}" value="${escapeDialogHtml(defaultValue)}" autocomplete="off" />
                        </div>
                        <div class="custom-dialog-actions">
                            <button type="button" class="custom-dialog-btn-cancel" id="custom-dialog-cancel-btn">${escapeDialogHtml(cancelText)}</button>
                            <button type="button" class="custom-dialog-btn-confirm" id="custom-dialog-confirm-btn">${escapeDialogHtml(confirmText)}</button>
                        </div>
                    </div>
                </div>
            `;
            container.style.display = 'block';

            const input = document.getElementById('custom-dialog-text-input');
            const confirmBtn = document.getElementById('custom-dialog-confirm-btn');
            const cancelBtn = document.getElementById('custom-dialog-cancel-btn');
            const overlay = document.getElementById('active-custom-dialog');

            function cleanup(result) {
                window.removeEventListener('keydown', handleKey);
                container.innerHTML = '';
                container.style.display = 'none';
                resolve(result);
            }

            function handleKey(e) {
                if (e.key === 'Escape') {
                    e.preventDefault();
                    cleanup(null);
                } else if (e.key === 'Enter') {
                    e.preventDefault();
                    const val = input ? input.value.trim() : '';
                    cleanup(val || null);
                }
            }

            if (confirmBtn) {
                confirmBtn.addEventListener('click', () => {
                    const val = input ? input.value.trim() : '';
                    cleanup(val || null);
                });
            }
            if (cancelBtn) cancelBtn.addEventListener('click', () => cleanup(null));
            if (overlay) {
                overlay.addEventListener('click', (e) => {
                    if (e.target === overlay) cleanup(null);
                });
            }

            window.addEventListener('keydown', handleKey);
            if (input) {
                input.focus();
                input.select();
            }
        });
    }

    function showCustomAlert(options = {}) {
        return new Promise((resolve) => {
            let title = 'Notice';
            let message = '';
            let buttonText = 'Got It';
            let icon = '🌿';

            if (typeof options === 'string') {
                message = options;
            } else if (options && typeof options === 'object') {
                title = options.title || 'Notice';
                message = options.message || '';
                buttonText = options.buttonText || 'Got It';
                icon = options.icon || '🌿';
            }

            let container = document.getElementById('custom-dialog-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'custom-dialog-container';
                document.body.appendChild(container);
            }

            container.innerHTML = `
                <div class="custom-dialog-overlay" id="active-custom-dialog">
                    <div class="custom-dialog-card" role="dialog" aria-modal="true">
                        <div class="custom-dialog-header">
                            <div class="custom-dialog-icon-badge">${icon}</div>
                            <div style="flex: 1;">
                                <h4 class="custom-dialog-title">${escapeDialogHtml(title)}</h4>
                                <p class="custom-dialog-message">${escapeDialogHtml(message)}</p>
                            </div>
                        </div>
                        <div class="custom-dialog-actions">
                            <button type="button" class="custom-dialog-btn-confirm" id="custom-dialog-alert-btn" style="width: 100%; justify-content: center;">${escapeDialogHtml(buttonText)}</button>
                        </div>
                    </div>
                </div>
            `;
            container.style.display = 'block';

            const btn = document.getElementById('custom-dialog-alert-btn');
            const overlay = document.getElementById('active-custom-dialog');

            function cleanup() {
                window.removeEventListener('keydown', handleKey);
                container.innerHTML = '';
                container.style.display = 'none';
                resolve(true);
            }

            function handleKey(e) {
                if (e.key === 'Escape' || e.key === 'Enter') {
                    e.preventDefault();
                    cleanup();
                }
            }

            if (btn) btn.addEventListener('click', cleanup);
            if (overlay) {
                overlay.addEventListener('click', (e) => {
                    if (e.target === overlay) cleanup();
                });
            }

            window.addEventListener('keydown', handleKey);
            if (btn) btn.focus();
        });
    }

    // Attach to window
    window.showToast = showToast;
    window.showCustomConfirm = showCustomConfirm;
    window.showCustomPrompt = showCustomPrompt;
    window.showCustomAlert = showCustomAlert;
    window.escapeDialogHtml = escapeDialogHtml;

})(window);
