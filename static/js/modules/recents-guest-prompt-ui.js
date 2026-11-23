/**
 * HERBALIST AI — RECENTS GUEST PROMPT UI
 * Guest-history presentation only; session storage and merging remain inline.
 */

(function(window) {
    'use strict';

    function renderGuestPrompt(container) {
        if (!container) return;
        container.innerHTML = `
            <div style="color:var(--text-muted);font-size:12px;padding:16px 12px;text-align:center;line-height:1.5;background:radial-gradient(circle at 50% 0%, rgba(46,204,113,0.08) 0%, rgba(255,255,255,0.02) 100%);border-radius:14px;border:1px dashed rgba(46,204,113,0.25);margin:4px;">
                <div style="width:34px;height:34px;border-radius:10px;background:rgba(46,204,113,0.12);border:1px solid rgba(46,204,113,0.3);display:flex;align-items:center;justify-content:center;margin:0 auto 8px auto;color:var(--accent-green);">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                </div>
                <span style="display:block;color:#e0ece3;font-weight:600;font-size:12px;margin-bottom:2px;">Consultation History</span>
                <span style="display:block;color:rgba(255,255,255,0.6);font-size:11px;line-height:1.4;">Sign in to save and revisit your herbal consultations.</span>
                <button onclick="openAuthModal('login')" style="margin-top:10px;background:linear-gradient(135deg, rgba(46,204,113,0.2) 0%, rgba(39,174,96,0.25) 100%);border:1px solid var(--accent-green);color:var(--accent-green);padding:6px 14px;border-radius:9px;font-size:11.5px;font-weight:700;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.background='var(--accent-green)';this.style.color='#000'" onmouseout="this.style.background='linear-gradient(135deg, rgba(46,204,113,0.2) 0%, rgba(39,174,96,0.25) 100%)';this.style.color='var(--accent-green)'">Sign In / Register</button>
            </div>`;
    }

    function renderEmptyState(container) {
        if (!container) return;
        container.innerHTML = '<div style="color:var(--text-muted);font-size:11px;padding:12px;text-align:center;font-style:italic;">No past consultations yet. Start a consultation above!</div>';
    }

    function renderItems(items, currentSessionId) {
        return items.map((item) => {
            const isActive = item.id === currentSessionId;
            const iconSvg = item.isPinned
                ? '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#f1c40f" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;"><line x1="12" y1="17" x2="12" y2="22"></line><path d="M5 17h14v-1.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V6h1a2 2 0 0 0 0-4H8a2 2 0 0 0 0 4h1v4.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24Z"></path></svg>'
                : '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.85;color:var(--accent-green);flex-shrink:0;"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>';
            const title = String(item.title || 'Botanical Consultation');
            const escapedTitle = title.replace(/'/g, "\\'");
            return `
                <div class="recent-item ${isActive ? 'active' : ''}" onclick="loadRecentConsultation('${item.id}')" style="cursor:pointer; display:flex; align-items:center; justify-content:space-between; padding:8px 12px; border-radius:10px; margin-bottom:2px; ${isActive ? 'background:rgba(46,204,113,0.15); border:1px solid rgba(46,204,113,0.35); color:#fff;' : ''}">
                    <div style="display:flex; align-items:center; gap:8px; min-width:0; flex:1;"><span style="display:flex; align-items:center; justify-content:center; flex-shrink:0;">${iconSvg}</span><span class="recent-item-title" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-size:12.5px;">${title}</span></div>
                    <span class="three-dots" onclick="openContextMenu(event, '${item.id}', '${escapedTitle}')" style="padding:2px 6px; border-radius:6px; opacity:0.75; flex-shrink:0;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.75'"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1.5"></circle><circle cx="12" cy="5" r="1.5"></circle><circle cx="12" cy="19" r="1.5"></circle></svg></span>
                </div>`;
        }).join('');
    }

    window.HerbalistRecentsGuestPromptUI = { renderGuestPrompt, renderEmptyState, renderItems };
})(window);
