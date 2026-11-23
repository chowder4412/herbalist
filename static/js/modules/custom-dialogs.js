/**
 * HERBALIST AI — CUSTOM DIALOGS
 * Confirm, prompt, and alert presentation with the existing keyboard behavior.
 */

(function(window) {
    'use strict';

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function showConfirm(options = {}) {
        return new Promise((resolve) => {
            const title = options.title || 'Are you sure?';
            const message = options.message || 'Do you want to proceed with this action?';
            const confirmText = options.confirmText || 'Confirm';
            const cancelText = options.cancelText || 'Cancel';
            const isDestructive = options.isDestructive !== false;
            const icon = options.icon || (isDestructive ? '🗑️' : '🌿');
            const container = document.getElementById('custom-dialog-container');
            if (!container) return resolve(false);

            container.innerHTML = `
                <div class="custom-dialog-overlay" id="active-custom-dialog">
                    <div class="custom-dialog-card ${isDestructive ? 'destructive' : ''}" role="dialog" aria-modal="true">
                        <div class="custom-dialog-header"><div class="custom-dialog-icon-badge">${icon}</div><div style="flex: 1;"><h4 class="custom-dialog-title">${escapeHtml(title)}</h4><p class="custom-dialog-message">${escapeHtml(message)}</p></div></div>
                        <div class="custom-dialog-actions"><button type="button" class="custom-dialog-btn-cancel" id="custom-dialog-cancel-btn">${escapeHtml(cancelText)}</button><button type="button" class="custom-dialog-btn-confirm ${isDestructive ? 'destructive' : ''}" id="custom-dialog-confirm-btn">${escapeHtml(confirmText)}</button></div>
                    </div>
                </div>`;
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
                if (e.key === 'Escape') { e.preventDefault(); cleanup(false); }
                else if (e.key === 'Enter') { e.preventDefault(); cleanup(true); }
            }
            if (confirmBtn) confirmBtn.addEventListener('click', () => cleanup(true));
            if (cancelBtn) cancelBtn.addEventListener('click', () => cleanup(false));
            if (overlay) overlay.addEventListener('click', (e) => { if (e.target === overlay) cleanup(false); });
            window.addEventListener('keydown', handleKey);
            if (confirmBtn) confirmBtn.focus();
        });
    }

    function showPrompt(options = {}) {
        return new Promise((resolve) => {
            const title = options.title || 'Rename Consultation';
            const message = options.message || 'Enter a new title:';
            const placeholder = options.placeholder || 'e.g. Morning Digestion Herbal Tea';
            const defaultValue = options.defaultValue || '';
            const confirmText = options.confirmText || 'Save Title';
            const cancelText = options.cancelText || 'Cancel';
            const icon = options.icon || '✏️';
            const container = document.getElementById('custom-dialog-container');
            if (!container) return resolve(null);

            container.innerHTML = `
                <div class="custom-dialog-overlay" id="active-custom-dialog">
                    <div class="custom-dialog-card" role="dialog" aria-modal="true">
                        <div class="custom-dialog-header"><div class="custom-dialog-icon-badge">${icon}</div><div style="flex: 1;"><h4 class="custom-dialog-title">${escapeHtml(title)}</h4><p class="custom-dialog-message">${escapeHtml(message)}</p></div></div>
                        <div class="custom-dialog-input-wrapper"><input type="text" class="custom-dialog-input" id="custom-dialog-text-input" placeholder="${escapeHtml(placeholder)}" value="${escapeHtml(defaultValue)}" autocomplete="off" /></div>
                        <div class="custom-dialog-actions"><button type="button" class="custom-dialog-btn-cancel" id="custom-dialog-cancel-btn">${escapeHtml(cancelText)}</button><button type="button" class="custom-dialog-btn-confirm" id="custom-dialog-confirm-btn">${escapeHtml(confirmText)}</button></div>
                    </div>
                </div>`;
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
            function submittedValue() { return input ? input.value.trim() || null : null; }
            function handleKey(e) {
                if (e.key === 'Escape') { e.preventDefault(); cleanup(null); }
                else if (e.key === 'Enter') { e.preventDefault(); cleanup(submittedValue()); }
            }
            if (confirmBtn) confirmBtn.addEventListener('click', () => cleanup(submittedValue()));
            if (cancelBtn) cancelBtn.addEventListener('click', () => cleanup(null));
            if (overlay) overlay.addEventListener('click', (e) => { if (e.target === overlay) cleanup(null); });
            window.addEventListener('keydown', handleKey);
            if (input) { input.focus(); input.select(); }
        });
    }

    function showAlert(options = {}) {
        return new Promise((resolve) => {
            let title = 'Notice';
            let message = '';
            let buttonText = 'Got It';
            let icon = '🌿';
            if (typeof options === 'string') message = options;
            else if (options && typeof options === 'object') {
                title = options.title || 'Notice';
                message = options.message || '';
                buttonText = options.buttonText || 'Got It';
                icon = options.icon || '🌿';
            }
            const container = document.getElementById('custom-dialog-container');
            if (!container) return resolve();
            container.innerHTML = `
                <div class="custom-dialog-overlay" id="active-custom-dialog">
                    <div class="custom-dialog-card" role="dialog" aria-modal="true">
                        <div class="custom-dialog-header"><div class="custom-dialog-icon-badge">${icon}</div><div style="flex: 1;"><h4 class="custom-dialog-title">${escapeHtml(title)}</h4><p class="custom-dialog-message">${escapeHtml(message)}</p></div></div>
                        <div class="custom-dialog-actions"><button type="button" class="custom-dialog-btn-confirm" id="custom-dialog-confirm-btn">${escapeHtml(buttonText)}</button></div>
                    </div>
                </div>`;
            container.style.display = 'block';
            const confirmBtn = document.getElementById('custom-dialog-confirm-btn');
            const overlay = document.getElementById('active-custom-dialog');
            function cleanup() {
                window.removeEventListener('keydown', handleKey);
                container.innerHTML = '';
                container.style.display = 'none';
                resolve();
            }
            function handleKey(e) {
                if (e.key === 'Escape' || e.key === 'Enter') { e.preventDefault(); cleanup(); }
            }
            if (confirmBtn) confirmBtn.addEventListener('click', cleanup);
            if (overlay) overlay.addEventListener('click', (e) => { if (e.target === overlay) cleanup(); });
            window.addEventListener('keydown', handleKey);
            if (confirmBtn) confirmBtn.focus();
        });
    }

    window.HerbalistDialogs = { escapeHtml, showConfirm, showPrompt, showAlert };
    window.showCustomConfirm = showConfirm;
    window.showCustomPrompt = showPrompt;
    window.showCustomAlert = showAlert;
})(window);
