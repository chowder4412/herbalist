/**
 * Local browser smoke checks for incremental frontend modularization.
 *
 * Usage (Windows):
 *   node tools\frontend-smoke.mjs
 *
 * The script discovers Playwright from the local npm cache automatically.
 * PLAYWRIGHT_ENTRY remains available as an explicit override.
 */

import { createServer } from 'node:http';
import { access, readFile, readdir } from 'node:fs/promises';
import { extname, join, normalize, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const root = resolve(process.cwd());
async function resolvePlaywrightEntry() {
  if (process.env.PLAYWRIGHT_ENTRY) return process.env.PLAYWRIGHT_ENTRY;

  const localAppData = process.env.LOCALAPPDATA;
  if (localAppData) {
    const npxCache = join(localAppData, 'npm-cache', '_npx');
    try {
      const cacheEntries = await readdir(npxCache, { withFileTypes: true });
      for (const entry of cacheEntries) {
        if (!entry.isDirectory()) continue;
        const candidate = join(npxCache, entry.name, 'node_modules', 'playwright', 'index.mjs');
        try {
          await access(candidate);
          return candidate;
        } catch {}
      }
    } catch {}
  }

  throw new Error(
    'Playwright was not found. Run tools\\install-playwright-trusted.ps1, or set PLAYWRIGHT_ENTRY to playwright/index.mjs.',
  );
}

const playwrightEntry = await resolvePlaywrightEntry();

const { chromium } = await import(pathToFileURL(playwrightEntry).href);
const contentTypes = {
  '.css': 'text/css',
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.json': 'application/json',
};

const server = createServer(async (request, response) => {
  const pathname = new URL(request.url, 'http://127.0.0.1').pathname;
  const relative = pathname === '/' ? 'index.html' : pathname.replace(/^\/+/, '');
  const target = normalize(join(root, relative));

  if (!target.startsWith(root)) {
    response.writeHead(403).end('Forbidden');
    return;
  }

  try {
    const body = await readFile(target);
    response.writeHead(200, { 'Content-Type': contentTypes[extname(target)] || 'application/octet-stream' });
    response.end(body);
  } catch {
    response.writeHead(404).end('Not found');
  }
});

await new Promise((resolveServer) => server.listen(0, '127.0.0.1', resolveServer));
const { port } = server.address();
const browser = await chromium.launch({ headless: true });

try {
  const page = await browser.newPage();
  const pageErrors = [];
  page.on('pageerror', (error) => pageErrors.push(error.stack || error.message));
  await page.route('**/*', async (route) => {
    const requestUrl = new URL(route.request().url());
    if (requestUrl.hostname === '127.0.0.1' || requestUrl.hostname === 'localhost') {
      await route.continue();
    } else {
      await route.abort();
    }
  });
  await page.addInitScript(() => {
    localStorage.setItem('herbalist_user', JSON.stringify({ email: 'smoke@example.test', full_name: 'Smoke Test' }));
  });
  // The current production document is intentionally large during migration.
  // Wait for the initial response, then wait for the specific modular APIs
  // under test instead of treating DOMContentLoaded as a 10-second requirement.
  await page.goto(`http://127.0.0.1:${port}/index.html`, { waitUntil: 'commit', timeout: 90000 });
  const requiredApis = [
    'showToast', 'toggleSidebar', 'changeClinicalModality', 'openAuthModal',
    'switchAuthTab', 'openSafetyCheckerModal', 'openHelpGuideModal',
    'openAdherenceModal', 'toggleAttachmentPopover',
    'openArtifactsCanvas', 'openKitchenCookMode',
    'showCustomConfirm', 'showCustomPrompt', 'showCustomAlert',
    'showVoiceEqualizer',
    'renderDynamicPromptChips',
    'playBrewTimerChime',
    'autoExpandTextarea',
    'dismissDisclaimer',
    'toggleAddProfileForm',
    'closeSignOutModal',
    'openDrugScannerModal', 'closeDrugScannerModal',
    // Defined by the large inline runtime, so include it in readiness instead
    // of racing the parse/execution of the transitional production document.
    'startNewChat',
  ];
  try {
    await page.waitForFunction(
      (apis) => apis.every((name) => typeof window[name] === 'function')
        && typeof window.HerbalistDialogs?.showConfirm === 'function',
      requiredApis,
      { timeout: 90000 },
    );
  } catch (error) {
    const readiness = await page.evaluate((apis) => ({
      missing: apis.filter((name) => typeof window[name] !== 'function'),
      dialogsReady: typeof window.HerbalistDialogs?.showConfirm === 'function',
      href: window.location.href,
      title: document.title,
      bodyText: document.body?.innerText?.slice(0, 160),
      storedUser: localStorage.getItem('herbalist_user'),
    }), requiredApis);
    readiness.pageErrors = pageErrors;
    throw new Error(`Frontend readiness failed: ${JSON.stringify(readiness)}`, { cause: error });
  }

  await page.evaluate(() => window.showToast('Modular toast smoke check', 'success', 5000));
  await page.waitForSelector('.herbalist-modern-toast');

  const sidebarCollapsedBefore = await page.locator('#sidebar').evaluate((node) => node.classList.contains('collapsed'));
  await page.evaluate(() => window.toggleSidebar());
  const sidebarCollapsedAfter = await page.locator('#sidebar').evaluate((node) => node.classList.contains('collapsed'));
  if (sidebarCollapsedBefore === sidebarCollapsedAfter) {
    throw new Error('Sidebar module did not toggle the collapsed state.');
  }

  await page.evaluate(() => window.changeClinicalModality('african', false));
  const modality = await page.evaluate(() => localStorage.getItem('herbalist_modality'));
  const selectorValue = await page.locator('#clinical-modality-selector').inputValue();
  if (modality !== 'african' || selectorValue !== 'african') {
    throw new Error('Modality module did not preserve the selected state.');
  }
  const moduleModality = await page.evaluate(() => ({
    active: window.activeClinicalModality,
    current: window.currentClinicalModality,
  }));
  if (moduleModality.active !== 'african' || moduleModality.current !== 'african') {
    throw new Error('Clinical modality consumers were not synchronized with the module state.');
  }

  const sessionStorage = await page.evaluate(() => {
    const key = window.getActiveUserStorageKey();
    window.saveLocalChatSessions({ smoke: { id: 'smoke', messages: [] } });
    return { key, sessions: window.getLocalChatSessions() };
  });
  if (sessionStorage.key !== 'herbalist_chat_sessions_smoke_example_test' || !sessionStorage.sessions.smoke) {
    throw new Error('Chat-history module did not preserve the account-scoped storage key.');
  }

  const authState = await page.evaluate(() => ({
    user: window.getStoredUser?.(),
    token: window.getActiveAuthToken?.(),
  }));
  if (authState.user?.email !== 'smoke@example.test' || authState.token !== null) {
    throw new Error(`Auth read helpers did not preserve the stored account state: ${JSON.stringify(authState)}`);
  }
  const newChatState = await page.evaluate(() => {
    window.startNewChat();
    return {
      sessionId: window.currentSessionId,
      messages: window.currentChatMessages,
      storedSessionId: localStorage.getItem('herbalist_active_session_id'),
    };
  });
  if (!newChatState.sessionId?.startsWith('chat_') || newChatState.storedSessionId !== newChatState.sessionId
    || !Array.isArray(newChatState.messages) || newChatState.messages.length !== 0) {
    throw new Error('New-chat state was not synchronized for modular consumers.');
  }

  const formattedMessage = await page.evaluate(() => window.renderMarkdown('**Bold**\n*italic*'));
  if (formattedMessage !== '<strong>Bold</strong><br><em>italic</em>') {
    throw new Error('Chat formatter did not preserve markdown-lite output.');
  }
  const doctorBubble = await page.evaluate(() => window.formatDoctorBubbleHTML('**Clinical update**', [], true));
  if (!doctorBubble.includes('<strong>Clinical update</strong>') || !doctorBubble.includes('Diagnostic Triage')) {
    throw new Error('Doctor bubble formatter did not preserve its rendered output.');
  }
  const citationMarkup = await page.evaluate(() => window.formatTextWithCitations('Evidence [1]', [{
    id: 'smoke-citation', title: 'Smoke study', journal: 'Smoke Journal', pmid: '12345',
  }]));
  if (!citationMarkup.includes("openEvidenceDrawer('smoke-citation')") || !citationMarkup.includes('🔬 [1]')) {
    throw new Error('Evidence formatter did not preserve citation-pill output.');
  }
  const evidenceDrawerState = await page.evaluate(() => {
    const drawer = document.getElementById('evidence-drawer');
    const overlay = document.getElementById('evidence-drawer-overlay');
    drawer.classList.add('open');
    overlay.classList.add('open');
    window.closeEvidenceDrawer();
    return !drawer.classList.contains('open') && !overlay.classList.contains('open');
  });
  if (!evidenceDrawerState) {
    throw new Error('Evidence drawer close control did not preserve its modal state.');
  }
  const careSuiteState = await page.evaluate(() => {
    const modal = document.getElementById('patient-care-toolkit-modal');
    window.openSynergyLabModal();
    const synergyOpened = modal.classList.contains('open') && modal.classList.contains('active');
    window.closeSynergyLabModal();
    const synergyClosed = !modal.classList.contains('open') && !modal.classList.contains('active');
    window.openVaultRecoveryModal();
    const vaultOpened = modal.classList.contains('open') && modal.classList.contains('active');
    window.closeVaultRecoveryModal();
    return { synergyOpened, synergyClosed, vaultOpened, vaultClosed: !modal.classList.contains('open') && !modal.classList.contains('active') };
  });
  if (!careSuiteState.synergyOpened || !careSuiteState.synergyClosed || !careSuiteState.vaultOpened || !careSuiteState.vaultClosed) {
    throw new Error('Care Suite entry points did not preserve the modal flow.');
  }
  const prescriptionsModalState = await page.evaluate(() => {
    const modal = document.getElementById('prescriptions-modal');
    window.openPrescriptionsModal();
    const opened = modal.classList.contains('active');
    window.closePrescriptionsModal();
    return { opened, closed: !modal.classList.contains('active') };
  });
  if (!prescriptionsModalState.opened || !prescriptionsModalState.closed) {
    throw new Error('Saved Prescriptions modal controls did not preserve the modal flow.');
  }
  const researchModalState = await page.evaluate(() => {
    const modalIds = ['pharmacopeia-modal', 'scanner-modal', 'rag-modal'];
    const handlers = [window.closePharmacopeiaModal, window.closeScannerModal, window.closeRagModal];
    return modalIds.every((id, index) => {
      const modal = document.getElementById(id);
      modal.classList.add('active');
      handlers[index]();
      return !modal.classList.contains('active');
    });
  });
  if (!researchModalState) {
    throw new Error('Research modal close controls did not preserve modal state.');
  }
  const emergencyModalState = await page.evaluate(() => {
    const modal = document.getElementById('emergency-modal');
    window.showEmergencyModal('**Emergency** guidance');
    const rendered = document.getElementById('emergency-modal-body').innerHTML;
    window.closeEmergencyModal();
    return !modal.classList.contains('active') && rendered.includes('<strong>Emergency</strong>');
  });
  if (!emergencyModalState) {
    throw new Error('Emergency modal close control did not preserve modal state.');
  }
  const sharedModalState = await page.evaluate(() => {
    const modalIds = ['pharmacopeia-modal', 'scanner-modal', 'prescriptions-modal', 'rag-modal', 'emergency-modal', 'clinical-modal', 'auth-modal'];
    const presentModalIds = modalIds.filter((id) => document.getElementById(id));
    presentModalIds.forEach((id) => document.getElementById(id).classList.add('active'));
    window.closeAllModals();
    return presentModalIds.every((id) => !document.getElementById(id).classList.contains('active'));
  });
  if (!sharedModalState) {
    throw new Error('Shared modal closer did not preserve modal state.');
  }
  const labUploadModalState = await page.evaluate(() => {
    const modal = document.getElementById('lab-upload-modal');
    if (!modal) return true;
    window.openLabUploadModal();
    const opened = modal.classList.contains('active');
    window.closeLabUploadModal();
    return opened && !modal.classList.contains('active');
  });
  if (!labUploadModalState) {
    throw new Error('Lab Upload modal controls did not preserve modal state.');
  }
  const passwordToggleState = await page.evaluate(() => {
    const input = document.getElementById('auth-password');
    const button = document.getElementById('btn-toggle-auth-pw');
    input.type = 'password';
    window.toggleAuthPasswordVisibility();
    const visible = input.type === 'text' && button.title === 'Hide password';
    window.toggleAuthPasswordVisibility();
    return visible && input.type === 'password' && button.title === 'Show password';
  });
  if (!passwordToggleState) {
    throw new Error('Auth password-visibility control did not preserve its state.');
  }
  const authTabState = await page.evaluate(() => {
    const modal = document.getElementById('auth-modal');
    const input = document.getElementById('auth-email');
    input.value = 'reset-me@example.test';
    window.openAuthModal('register');
    const opened = modal.classList.contains('active')
      && window.currentAuthTab === 'register'
      && document.getElementById('group-fullname').style.display === 'block'
      && input.value === '';
    window.switchAuthTab('register');
    const registered = window.currentAuthTab === 'register'
      && document.getElementById('group-fullname').style.display === 'block';
    window.switchAuthTab('login');
    window.closeAuthModal();
    return opened && registered && window.currentAuthTab === 'login'
      && !modal.classList.contains('active')
      && document.getElementById('group-fullname').style.display === 'none';
  });
  if (!authTabState) {
    throw new Error('Auth modal controls did not preserve their shared UI state.');
  }
  const safetyCheckerState = await page.evaluate(() => {
    const modal = document.getElementById('safety-checker-modal');
    const hdi = document.getElementById('safety-panel-hdi');
    const substitute = document.getElementById('safety-panel-sub');
    window.openSafetyCheckerModal('sub');
    const substituted = modal.classList.contains('active')
      && substitute.style.display === 'flex'
      && hdi.style.display === 'none';
    window.switchSafetyTab('hdi');
    const restored = hdi.style.display === 'flex' && substitute.style.display === 'none';
    window.closeSafetyCheckerModal();
    return substituted && restored && !modal.classList.contains('active');
  });
  if (!safetyCheckerState) {
    throw new Error('Safety Checker modal controls did not preserve tab state.');
  }
  const utilityModalState = await page.evaluate(() => {
    const help = document.getElementById('help-guide-modal');
    if (!help) return false;
    window.openHelpGuideModal();
    const helpOpened = help.classList.contains('active');
    window.closeHelpGuideModal();

    const clinical = document.getElementById('clinical-modal');
    if (!clinical) return helpOpened && !help.classList.contains('active');
    window.openClinicalModal();
    const clinicalOpened = clinical.classList.contains('active');
    window.closeClinicalModal();
    return helpOpened && !help.classList.contains('active')
      && clinicalOpened && !clinical.classList.contains('active');
  });
  if (!utilityModalState) {
    throw new Error('Utility modal controls did not preserve modal state.');
  }
  const adherenceModalState = await page.evaluate(() => {
    const modal = document.getElementById('adherence-modal');
    if (!modal) return false;
    window.openAdherenceModal();
    const opened = modal.style.display === 'flex';
    window.closeAdherenceModal();
    return opened && modal.style.display === 'none';
  });
  if (!adherenceModalState) {
    throw new Error('Adherence modal controls did not preserve modal state.');
  }
  const attachmentPopoverState = await page.evaluate(() => {
    const menu = document.getElementById('attachment-popover-menu');
    if (!menu) return false;
    window.toggleAttachmentPopover();
    const opened = menu.style.display === 'block';
    window.toggleAttachmentPopover(false);
    return opened && menu.style.display === 'none';
  });
  if (!attachmentPopoverState) {
    throw new Error('Attachment popover controls did not preserve menu state.');
  }
  const customDialogState = await page.evaluate(async () => {
    const container = document.getElementById('custom-dialog-container');
    const confirmedPromise = window.showCustomConfirm({ title: 'Smoke confirm', isDestructive: false });
    const confirmButton = document.getElementById('custom-dialog-confirm-btn');
    const confirmShown = container.style.display === 'block' && Boolean(confirmButton);
    confirmButton.click();
    const confirmed = await confirmedPromise;

    const promptPromise = window.showCustomPrompt({ defaultValue: '  smoke title  ' });
    const input = document.getElementById('custom-dialog-text-input');
    document.getElementById('custom-dialog-confirm-btn').click();
    const prompted = await promptPromise;

    const alertPromise = window.showCustomAlert('Smoke alert');
    const alertShown = container.style.display === 'block';
    document.getElementById('custom-dialog-confirm-btn').click();
    await alertPromise;
    return confirmShown && confirmed === true
      && input.value === '  smoke title  '
      && prompted === 'smoke title'
      && alertShown && container.style.display === 'none';
  });
  if (!customDialogState) {
    throw new Error('Custom dialog controls did not preserve confirm, prompt, and alert flows.');
  }
  const voiceEqualizerState = await page.evaluate(() => {
    const visualizer = document.getElementById('voice-wave-visualizer');
    if (!visualizer) return false;
    window.showVoiceEqualizer(true);
    const shown = visualizer.style.display === 'flex';
    window.showVoiceEqualizer(false);
    return shown && visualizer.style.display === 'none';
  });
  if (!voiceEqualizerState) {
    throw new Error('Voice equalizer control did not preserve visualizer state.');
  }
  const promptChipState = await page.evaluate(() => {
    const container = document.getElementById('dynamic-prompt-chips');
    if (!container) return false;
    window.renderDynamicPromptChips();
    return container.querySelectorAll('button').length === 4
      && container.textContent.includes('Ginger & Licorice Tea');
  });
  if (!promptChipState) {
    throw new Error('Dynamic prompt-chip renderer did not preserve suggestions.');
  }
  const textareaSizingState = await page.evaluate(() => {
    const input = document.getElementById('user-input');
    if (!input) return false;
    input.value = 'Smoke test input';
    window.autoExpandTextarea(input);
    return input.style.height === '120px' || input.style.height === 'auto' || input.style.height.endsWith('px');
  });
  if (!textareaSizingState) {
    throw new Error('Textarea auto-expand control did not preserve sizing behavior.');
  }
  const newChatViewState = await page.evaluate(() => {
    const feed = document.getElementById('chat-feed');
    const hero = document.getElementById('hero-welcome');
    const input = document.getElementById('user-input');
    if (!feed || !hero || !input || !window.HerbalistChatSessionUI) return false;
    feed.innerHTML = '<div>stale content</div>';
    feed.style.display = 'flex';
    hero.style.display = 'none';
    input.value = 'stale input';
    window.HerbalistChatSessionUI.resetNewChatView();
    return feed.innerHTML === '' && feed.style.display === 'none'
      && hero.style.display === 'flex' && input.value === '';
  });
  if (!newChatViewState) {
    throw new Error('New-chat view reset did not preserve the canonical shell state.');
  }
  const guestRecentsPromptState = await page.evaluate(() => {
    const container = document.createElement('div');
    window.HerbalistRecentsGuestPromptUI.renderGuestPrompt(container);
    return container.textContent.includes('Consultation History')
      && container.textContent.includes('Sign In / Register')
      && Boolean(container.querySelector('button'));
  });
  if (!guestRecentsPromptState) {
    throw new Error('Guest recents prompt did not preserve sign-in presentation.');
  }
  const emptyRecentsState = await page.evaluate(() => {
    const container = document.createElement('div');
    window.HerbalistRecentsGuestPromptUI.renderEmptyState(container);
    return container.textContent.includes('No past consultations yet');
  });
  if (!emptyRecentsState) {
    throw new Error('Empty recents state did not preserve its presentation.');
  }
  const recentsItemState = await page.evaluate(() => {
    const html = window.HerbalistRecentsGuestPromptUI.renderItems([
      { id: 'smoke-session', title: "Smoke's Consultation", isPinned: true },
    ], 'smoke-session');
    const wrapper = document.createElement('div');
    wrapper.innerHTML = html;
    return wrapper.querySelector('.recent-item.active') !== null
      && wrapper.textContent.includes("Smoke's Consultation")
      && wrapper.querySelector('.three-dots')?.getAttribute('onclick').includes('openContextMenu');
  });
  if (!recentsItemState) {
    throw new Error('Recents item UI did not preserve active, pinned, and menu presentation.');
  }
  const chatSessionTitleState = await page.evaluate(() => {
    const fromMessage = window.HerbalistChatSessionTitle.deriveSessionTitle([
      { role: 'patient', html: '<strong>Long clinical message for smoke title testing beyond thirty-two chars</strong>' },
    ], null);
    const fromPrescription = window.HerbalistChatSessionTitle.deriveSessionTitle([
      { role: 'patient', html: 'Patient message' },
    ], { primary_diagnosis: 'Prescription diagnosis title that is deliberately longer than thirty-two chars' });
    return fromMessage === 'Long clinical message for smoke ...'
      && fromPrescription === 'Prescription diagnosis title tha...';
  });
  if (!chatSessionTitleState) {
    throw new Error('Chat session title derivation did not preserve title precedence and truncation.');
  }
  const chatContextMenuState = await page.evaluate(() => {
    const menu = document.getElementById('context-menu');
    if (!menu || typeof window.openContextMenu !== 'function') return false;
    menu.classList.remove('active');
    window.openContextMenu({ stopPropagation() {}, clientX: 30, clientY: 40 }, 'smoke-session', 'Smoke Session');
    const opened = menu.classList.contains('active')
      && menu.style.top === '40px'
      && menu.style.left === '40px';
    document.dispatchEvent(new MouseEvent('click'));
    return opened && !menu.classList.contains('active');
  });
  if (!chatContextMenuState) {
    throw new Error('Chat context menu did not preserve selected-session UI behavior.');
  }
  const disclaimerState = await page.evaluate(() => {
    const banner = document.getElementById('disclaimer-banner');
    if (!banner) return false;
    banner.style.display = 'flex';
    localStorage.removeItem('herbalist_disclaimer_dismissed');
    window.dismissDisclaimer();
    return banner.style.display === 'none'
      && localStorage.getItem('herbalist_disclaimer_dismissed') === 'true';
  });
  if (!disclaimerState) {
    throw new Error('Disclaimer banner control did not preserve dismissal behavior.');
  }
  const profileFormState = await page.evaluate(() => {
    const form = document.createElement('div');
    form.id = 'add-profile-form-container';
    document.body.appendChild(form);
    window.toggleAddProfileForm();
    const opened = form.style.display === 'block';
    window.toggleAddProfileForm();
    const closed = form.style.display === 'none';
    form.remove();
    return opened && closed;
  });
  if (!profileFormState) {
    throw new Error('Profile form toggle did not preserve visibility behavior.');
  }
  const signoutModalState = await page.evaluate(() => {
    const modal = document.getElementById('signout-confirm-modal');
    if (!modal) return false;
    modal.classList.add('active');
    window.closeSignOutModal();
    return !modal.classList.contains('active');
  });
  if (!signoutModalState) {
    throw new Error('Sign-out modal close control did not preserve modal state.');
  }
  const voiceToggleUiState = await page.evaluate(() => {
    const button = document.getElementById('voice-toggle-btn');
    if (!button || !window.HerbalistVoiceToggleUI) return false;
    window.HerbalistVoiceToggleUI.renderVoiceToggleUI(false);
    const muted = button.className === 'speaker-btn muted-voice'
      && button.title.includes('MUTED');
    window.HerbalistVoiceToggleUI.renderVoiceToggleUI(true);
    return muted && button.className === 'speaker-btn active-voice'
      && button.title.includes('ON');
  });
  if (!voiceToggleUiState) {
    throw new Error('Voice toggle UI did not preserve speaker control state.');
  }
  const telehealthStatusUiState = await page.evaluate(() => {
    const orb = document.getElementById('orb-core-sphere');
    const badge = document.getElementById('telehealth-status-badge');
    if (!orb || !badge || !window.HerbalistTelehealthStatusUI) return false;
    window.HerbalistTelehealthStatusUI.setOrbState('doctor-speaking');
    const speaking = orb.classList.contains('doctor-speaking');
    window.HerbalistTelehealthStatusUI.setOrbState('patient-speaking');
    const listening = orb.classList.contains('patient-speaking')
      && !orb.classList.contains('doctor-speaking');
    window.HerbalistTelehealthStatusUI.updateTelehealthStatus('Smoke status', 'thinking');
    return speaking && listening && badge.innerText === 'Smoke status'
      && badge.style.color === 'var(--accent-gold)';
  });
  if (!telehealthStatusUiState) {
    throw new Error('Telehealth status UI did not preserve visual state.');
  }
  const telehealthTimerUiState = await page.evaluate(() => {
    const display = document.getElementById('telehealth-timer-display');
    if (!display || !window.HerbalistTelehealthTimerUI) return false;
    window.HerbalistTelehealthTimerUI.renderTelehealthTimer(125);
    return display.innerText === '⏱ 02:05';
  });
  if (!telehealthTimerUiState) {
    throw new Error('Telehealth timer UI did not preserve elapsed-time formatting.');
  }
  const drugScannerModalState = await page.evaluate(() => {
    const modal = document.getElementById('drug-scanner-modal');
    if (!modal) return false;
    window.openDrugScannerModal();
    const opened = modal.classList.contains('active');
    window.closeDrugScannerModal();
    return opened && !modal.classList.contains('active');
  });
  if (!drugScannerModalState) {
    throw new Error('Drug Scanner modal controls did not preserve modal state.');
  }
  const thoughtHudState = await page.evaluate(() => {
    const id = 'smoke';
    const steps = document.createElement('div');
    steps.id = `thought-steps-${id}`;
    steps.style.display = 'none';
    const arrow = document.createElement('span');
    arrow.id = `thought-hud-arrow-${id}`;
    document.body.append(steps, arrow);
    window.HerbalistThoughtHudControls.toggleThoughtHUD(id);
    const expanded = steps.style.display === 'flex' && arrow.innerText === '▲';
    window.HerbalistThoughtHudControls.toggleThoughtHUD(id);
    const collapsed = steps.style.display === 'none' && arrow.innerText === '▼';
    steps.remove();
    arrow.remove();
    return expanded && collapsed;
  });
  if (!thoughtHudState) {
    throw new Error('Thought HUD controls did not preserve expand/collapse state.');
  }
  const thoughtHudStepState = await page.evaluate(() => {
    const id = 'smoke-step';
    const hud = document.createElement('div');
    hud.id = `thought-hud-${id}`;
    const status = document.createElement('span');
    status.id = `thought-hud-status-${id}`;
    const steps = document.createElement('div');
    steps.id = `thought-steps-${id}`;
    hud.append(status, steps);
    document.body.appendChild(hud);
    window.HerbalistThoughtHudStepUI.updateThoughtHUDStep(id, {
      step: 2, progress: 100, title: 'Assessment', message: 'Smoke check',
    });
    const row = document.getElementById(`thought-step-${id}-2`);
    const rendered = hud.style.display === 'block' && status.innerText === 'Assessment'
      && row?.textContent.includes('Smoke check') && row.textContent.includes('✅');
    hud.remove();
    return rendered;
  });
  if (!thoughtHudStepState) {
    throw new Error('Thought HUD step UI did not preserve streamed-step presentation.');
  }
  const triageStepperState = await page.evaluate(() => {
    const oldStepper = document.getElementById('triage-stepper');
    oldStepper?.remove();
    window.HerbalistTriageStepperUI.updateTriageStepper('severity');
    const stepper = document.getElementById('triage-stepper');
    return Boolean(stepper)
      && document.getElementById('step-severity').classList.contains('active')
      && document.getElementById('step-onset').classList.contains('completed')
      && !document.getElementById('step-medications').classList.contains('completed');
  });
  if (!triageStepperState) {
    throw new Error('Triage stepper UI did not preserve phase presentation.');
  }
  const triageProgressState = await page.evaluate(() => {
    document.getElementById('triage-progress')?.remove();
    window.HerbalistTriageProgressUI.showTriageProgress('severity');
    const bar = document.getElementById('triage-progress');
    return Boolean(bar)
      && bar.textContent.includes('Onset')
      && bar.textContent.includes('Diagnosis')
      && bar.textContent.includes('✓');
  });
  if (!triageProgressState) {
    throw new Error('Triage progress UI did not preserve phase-bar rendering.');
  }
  const clipboardFallbackState = await page.evaluate(() => {
    if (!window.HerbalistClipboard?.fallbackCopy) return false;
    const originalExecCommand = document.execCommand;
    const button = document.createElement('button');
    button.innerHTML = 'Copy';
    document.body.appendChild(button);
    document.execCommand = () => true;
    window.HerbalistClipboard.fallbackCopy('Smoke copy', button);
    document.execCommand = originalExecCommand;
    const copied = button.textContent.includes('Copied');
    button.remove();
    return copied && !document.querySelector('textarea[style*="opacity"]');
  });
  if (!clipboardFallbackState) {
    throw new Error('Clipboard fallback did not preserve copy feedback and cleanup.');
  }
  const scannerFileInputState = await page.evaluate(() => {
    const input = document.getElementById('scanner-file-input');
    if (!input || typeof window.triggerFileInput !== 'function') return false;
    let clicked = false;
    const originalClick = input.click;
    input.click = () => { clicked = true; };
    window.triggerFileInput();
    input.click = originalClick;
    return clicked;
  });
  if (!scannerFileInputState) {
    throw new Error('Scanner file-input control did not open the chooser.');
  }
  const chatFileInputState = await page.evaluate(() => {
    const input = document.getElementById('chat-file-upload');
    if (!input || typeof window.triggerChatFileUpload !== 'function') return false;
    let clicked = false;
    const originalClick = input.click;
    input.click = () => { clicked = true; };
    window.triggerChatFileUpload();
    input.click = originalClick;
    return clicked;
  });
  if (!chatFileInputState) {
    throw new Error('Chat file-input control did not open the chooser.');
  }
  const attachmentPreviewState = await page.evaluate(() => {
    const preview = document.getElementById('attachment-preview-bar');
    const input = document.getElementById('chat-file-upload');
    if (!preview || !input || !window.HerbalistChatSessionUI) return false;
    preview.style.display = 'flex';
    window.HerbalistChatSessionUI.clearAttachmentPreview();
    return preview.style.display === 'none' && input.value === '';
  });
  if (!attachmentPreviewState) {
    throw new Error('Attachment preview UI did not preserve reset behavior.');
  }
  const forgotPasswordUiState = await page.evaluate(() => {
    const form = document.getElementById('auth-form-container');
    const forgot = document.getElementById('forgot-form-container');
    const authEmail = document.getElementById('auth-email');
    const forgotEmail = document.getElementById('forgot-email-input');
    if (!form || !forgot || !authEmail || !forgotEmail) return false;
    form.style.display = 'block';
    forgot.style.display = 'none';
    authEmail.value = 'reset@example.test';
    window.openForgotPasswordStep();
    const transitioned = form.style.display === 'none'
      && forgot.style.display === 'block'
      && forgotEmail.value === 'reset@example.test';
    window.switchAuthTab('login');
    return transitioned;
  });
  if (!forgotPasswordUiState) {
    throw new Error('Forgot-password UI did not preserve form transition behavior.');
  }
  const emailValidationState = await page.evaluate(() => (
    typeof window.isValidEmail === 'function'
      && window.isValidEmail('smoke@example.test')
      && !window.isValidEmail('not-an-email')
  ));
  if (!emailValidationState) {
    throw new Error('Email validation did not preserve expected validation behavior.');
  }
  const vaultTabUiState = await page.evaluate(() => {
    const ids = ['vault-tab-profiles', 'vault-tab-timeline', 'vault-panel-profiles', 'vault-panel-timeline'];
    const elements = ids.map((id) => {
      const element = document.createElement('div');
      element.id = id;
      document.body.appendChild(element);
      return element;
    });
    const [profilesTab, timelineTab, profilesPanel, timelinePanel] = elements;
    const timelineSelected = window.HerbalistVaultTabUI.renderVaultTab('timeline')
      && timelineTab.style.background === 'var(--accent-green)'
      && profilesPanel.style.display === 'none'
      && timelinePanel.style.display === 'flex';
    const profilesSelected = !window.HerbalistVaultTabUI.renderVaultTab('profiles')
      && profilesTab.style.background === 'var(--accent-green)'
      && profilesPanel.style.display === 'flex'
      && timelinePanel.style.display === 'none';
    elements.forEach((element) => element.remove());
    return timelineSelected && profilesSelected;
  });
  if (!vaultTabUiState) {
    throw new Error('Vault tab UI did not preserve tab and panel state.');
  }

  const canvasState = await page.evaluate(() => {
    const prescription = {
      primary_diagnosis: 'Smoke Test Diagnosis',
      formulation: {
        formulation_name: 'Smoke Test Formula',
        ingredients: [{ common_name: 'Ginger', botanical_name: 'Zingiber officinale', part_used: 'Root' }],
      },
    };
    window.activePrescriptionPayload = prescription;
    window.openArtifactsCanvas();
    window.setCanvasPotBatchLiters(3);
    window.toggleHerbDispensaryCheck('herb_0_Ginger');
    window.toggleChronoDose('morning');
    window.toggleCanvasFullscreen();
    const pane = document.getElementById('artifacts-canvas-pane');
    const beforeClose = {
      text: document.getElementById('canvas-body').textContent,
      liters: window.currentCanvasBatchLiters,
      herbChecked: window.checkedHerbDispensaryItems.has('herb_0_Ginger'),
      morningChecked: window.chronoDoseChecklist.morning,
      fullscreen: pane.classList.contains('fullscreen'),
    };
    window.closeArtifactsCanvas();
    return { ...beforeClose, collapsed: pane.classList.contains('collapsed'), fullscreenAfterClose: pane.classList.contains('fullscreen') };
  });
  if (!canvasState.text.includes('Smoke Test Formula') || canvasState.liters !== 3
    || !canvasState.herbChecked || !canvasState.morningChecked || !canvasState.fullscreen
    || !canvasState.collapsed || canvasState.fullscreenAfterClose) {
    throw new Error('Canvas module did not preserve the prescription workspace state.');
  }

  console.log('Running Cook Mode shell smoke check...');
  const cookModeState = await Promise.race([
    page.evaluate(() => {
      const modal = document.getElementById('patient-care-toolkit-modal');
      const before = modal ? [...modal.classList] : null;
      const api = {
        openCook: typeof window.openKitchenCookMode,
        closeCook: typeof window.closeKitchenCookMode,
        openToolkit: typeof window.openPatientCareToolkitModal,
        closeToolkit: typeof window.closePatientCareToolkitModal,
        initCook: typeof window.initKitchenCookData,
      };
      window.openKitchenCookMode(window.activePrescriptionPayload);
      const afterOpen = modal ? [...modal.classList] : null;
      const opened = Boolean(modal?.classList.contains('open') && modal.classList.contains('active'));
      window.closeKitchenCookMode();
      const afterClose = modal ? [...modal.classList] : null;
      return {
        before,
        afterOpen,
        afterClose,
        api,
        opened,
        closed: Boolean(modal && !modal.classList.contains('open') && !modal.classList.contains('active')),
      };
    }),
    new Promise((_, reject) => setTimeout(() => reject(new Error('Cook Mode shell interaction timed out.')), 10000)),
  ]);
  if (!cookModeState.opened || !cookModeState.closed) {
    throw new Error(`Cook Mode shell did not preserve the Care Suite modal flow: ${JSON.stringify(cookModeState)}`);
  }
  console.log('Cook Mode shell smoke check passed.');

  console.log('Frontend smoke checks passed: shared UI controls, storage, formatting, modal flows, canvas, and Cook Mode shell.');
} finally {
  // A page can keep an audio or speech handle alive briefly on Windows. Cleanup
  // must not turn already-passed assertions into a false smoke-test failure.
  server.closeAllConnections();
  let browserClosed = false;
  const closeBrowser = browser.close()
    .then(() => { browserClosed = true; })
    .catch((error) => console.warn(`Browser shutdown notice: ${error.message}`));
  await Promise.race([
    closeBrowser,
    new Promise((resolve) => setTimeout(resolve, 10000)),
  ]);
  if (!browserClosed) console.warn('Browser shutdown notice: timed out after 10 seconds; exiting after completed checks.');
  await Promise.race([
    new Promise((closeServer) => server.close(closeServer)),
    new Promise((resolve) => setTimeout(resolve, 2000)),
  ]);
}

process.exit(0);
