"""Static guardrails for the incremental frontend modularization.

These checks deliberately avoid importing the FastAPI application, so they are
fast and safe to run without seeding databases or contacting AI providers.
"""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def _asset_paths():
    page = INDEX.read_text(encoding="utf-8")
    return re.findall(r'(?:src|href)=["\'](/static/[^"\']+)["\']', page)


def test_production_page_keeps_all_referenced_static_assets():
    """A partial migration must never leave the production page with 404 assets."""
    assets = _asset_paths()
    assert assets, "index.html must retain its modular static assets"
    missing = [asset for asset in assets if not (ROOT / asset.lstrip("/")).is_file()]
    assert not missing, f"index.html references missing frontend assets: {missing}"


def test_production_page_retains_public_feature_hooks():
    """Protect the DOM hooks used by modules and inline event handlers."""
    page = INDEX.read_text(encoding="utf-8")
    required_ids = {
        "chat-feed",
        "user-input",
        "sidebar",
        "canvas-body",
        "toast-container",
        "emergency-modal",
    }
    missing = [element_id for element_id in required_ids if f'id="{element_id}"' not in page]
    assert not missing, f"migration removed required feature hooks: {missing}"


def test_component_owned_dynamic_ui_remains_loaded():
    """Some UI is created at runtime, so protect its component rather than markup."""
    page = INDEX.read_text(encoding="utf-8")
    assert "/static/js/components/recovery-tracker.js" in page


def test_public_inline_handlers_remain_available_during_transition():
    """Existing markup uses these handlers; they need compatibility shims first."""
    page = INDEX.read_text(encoding="utf-8")
    for handler in ("startNewChat", "toggleSidebar", "showToast"):
        assert handler in page, f"missing public frontend handler: {handler}"


def test_toast_api_has_one_active_modular_owner():
    """Prevent a later inline declaration from silently overriding the module."""
    page = INDEX.read_text(encoding="utf-8")
    toast_module = (ROOT / "static/js/modules/toast-dialog.js").read_text(encoding="utf-8")
    assert "function showToast(message, type = 'info', duration = 3600)" in toast_module
    assert "window.showToast = showToast" in toast_module
    assert "function showToast(message, type = 'info', duration = 3600)" not in page
    assert "legacyShowToast" not in page


def test_sidebar_controls_have_one_active_modular_owner():
    """Keep desktop and mobile navigation behavior out of the inline page."""
    page = INDEX.read_text(encoding="utf-8")
    chat_module = (ROOT / "static/js/modules/chat-consultation.js").read_text(encoding="utf-8")
    for handler in ("toggleSidebar", "toggleMobileSidebar", "closeMobileSidebar"):
        assert f"window.{handler} = {handler}" in chat_module
        assert f"function {handler}()" not in page
        assert f"legacy{handler[0].upper()}{handler[1:]}" not in page


def test_geolocation_and_modality_have_one_active_modular_owner():
    """Keep regional selection and its persisted preference behavior centralized."""
    page = INDEX.read_text(encoding="utf-8")
    geo_module = (ROOT / "static/js/modules/geolocation-modality.js").read_text(encoding="utf-8")
    for handler in (
        "changeClinicalModality",
        "detectUserLocationAndModality",
        "updateModalityDropdownLabels",
    ):
        assert f"window.{handler} = {handler}" in geo_module
        assert f"function {handler}" not in page
    assert "legacyChangeClinicalModality" not in page
    assert "legacyDetectUserLocationAndModality" not in page
    assert "legacyUpdateModalityDropdownLabels" not in page


def test_chat_history_storage_helpers_have_one_active_modular_owner():
    """Preserve account-scoped browser history while moving its helpers out."""
    page = INDEX.read_text(encoding="utf-8")
    core_module = (ROOT / "static/js/modules/core-state.js").read_text(encoding="utf-8")
    for handler in (
        "getActiveUserStorageKey",
        "getLocalChatSessions",
        "saveLocalChatSessions",
    ):
        assert f"window.{handler} = function" in core_module
        assert f"function {handler}" not in page
    assert "herbalist_chat_sessions_guest" in core_module
    assert "herbalist_chat_sessions_${cleanId}" in core_module


def test_canvas_controls_have_one_active_modular_owner():
    """Keep the prescription canvas controls and active state in one module."""
    page = INDEX.read_text(encoding="utf-8")
    canvas_module = (ROOT / "static/js/modules/canvas-controller.js").read_text(encoding="utf-8")
    for handler in (
        "toggleArtifactsCanvas",
        "openArtifactsCanvas",
        "closeArtifactsCanvas",
        "toggleCanvasFullscreen",
        "setCanvasPotBatchLiters",
        "toggleHerbDispensaryCheck",
        "toggleChronoDose",
        "renderArtifactsCanvasContent",
    ):
        assert f"window.{handler} = {handler}" in canvas_module
        assert f"function {handler}" not in page
    assert "window.canvasActivePrescription" in canvas_module
    assert "window.activePrescriptionPayload" in canvas_module


def test_cook_mode_open_close_shell_has_one_active_modular_owner():
    """Keep Cook Mode entry and exit aligned with the Care Suite modal flow."""
    page = INDEX.read_text(encoding="utf-8")
    cook_module = (ROOT / "static/js/modules/cook-mode-controller.js").read_text(encoding="utf-8")
    for handler in ("openKitchenCookMode", "closeKitchenCookMode"):
        assert f"window.{handler} = {handler}" in cook_module
        assert f"function {handler}" not in page
    assert "window.openPatientCareToolkitModal?.('cook')" in cook_module
    assert "modal.classList.add('open')" in cook_module
    assert "modal.classList.add('active')" in cook_module
    assert "window.closePatientCareToolkitModal?.()" in cook_module
    assert "modal.classList.remove('open')" in cook_module
    assert "modal.classList.remove('active')" in cook_module


def test_cook_mode_engine_has_one_active_modular_owner():
    """Protect the recipe, narration, and kitchen-timer handlers in markup."""
    page = INDEX.read_text(encoding="utf-8")
    cook_module = (ROOT / "static/js/modules/cook-mode-controller.js").read_text(encoding="utf-8")
    for handler in (
        "initKitchenCookData",
        "renderCookStep",
        "jumpToCookStep",
        "nextCookStep",
        "prevCookStep",
        "changeCookAudioLanguage",
        "speakCookText",
        "readActiveCookStepAloud",
        "toggleCookVoiceNarration",
        "toggleKitchenTimer",
        "startKitchenTimer",
        "pauseKitchenTimer",
        "resetKitchenTimer",
    ):
        assert f"window.{handler} = {handler}" in cook_module
        assert f"function {handler}" not in page


def test_auth_read_helpers_have_one_active_modular_owner():
    """Keep token/user lookups centralized without changing account writes."""
    page = INDEX.read_text(encoding="utf-8")
    auth_module = (ROOT / "static/js/modules/auth-vault-controller.js").read_text(encoding="utf-8")
    for handler in ("getActiveAuthToken", "getStoredUser", "enforceAuthGuard"):
        assert f"window.{handler} = {handler}" in auth_module
        assert f"function {handler}" not in page
    assert "herbalist_jwt_token" in auth_module
    assert "herbalist_user_profile" in auth_module


def test_chat_markdown_formatter_has_one_active_modular_owner():
    """Keep streamed and saved-chat text formatting stable during extraction."""
    page = INDEX.read_text(encoding="utf-8")
    formatter = (ROOT / "static/js/modules/chat-formatting.js").read_text(encoding="utf-8")
    assert "/static/js/modules/chat-formatting.js" in page
    assert "function renderMarkdown(text)" in formatter
    assert "window.renderMarkdown = renderMarkdown" in formatter
    assert "function renderMarkdown(text)" not in page


def test_doctor_bubble_formatter_has_one_active_modular_owner():
    """Keep the streamed doctor-response wrapper visually stable."""
    page = INDEX.read_text(encoding="utf-8")
    formatter = (ROOT / "static/js/modules/chat-formatting.js").read_text(encoding="utf-8")
    assert "function formatDoctorBubbleHTML" in formatter
    assert "window.formatDoctorBubbleHTML = formatDoctorBubbleHTML" in formatter
    assert "function formatDoctorBubbleHTML" not in page


def test_evidence_formatter_has_one_active_modular_owner():
    """Keep citation pills linked to the existing evidence drawer map."""
    page = INDEX.read_text(encoding="utf-8")
    formatter = (ROOT / "static/js/modules/evidence-formatting.js").read_text(encoding="utf-8")
    assert "/static/js/modules/evidence-formatting.js" in page
    assert "function formatTextWithCitations" in formatter
    assert "window.formatTextWithCitations = formatTextWithCitations" in formatter
    assert "function formatTextWithCitations" not in page
    assert "legacyFormatTextWithCitations" not in page
    assert "window.activeEvidenceCitationsMap" in formatter
    assert "window.activeEvidenceCitationsMap[citationId]" in page
    assert "window.closeEvidenceDrawer = closeEvidenceDrawer" in formatter
    assert "function closeEvidenceDrawer" not in page


def test_inline_session_and_modality_state_is_declared_once():
    """A duplicate `let` declaration prevents the entire inline app script loading."""
    page = INDEX.read_text(encoding="utf-8")
    for state_name in (
        "activeClinicalModality",
        "currentClinicalModality",
        "currentSessionId",
    ):
        assert page.count(f"let {state_name} =") == 1, state_name


def test_auth_modal_ui_has_one_modular_implementation():
    """Keep auth presentation controls modular without moving account writes."""
    page = INDEX.read_text(encoding="utf-8")
    auth_controls = (ROOT / "static/js/modules/auth-ui-controls.js").read_text(encoding="utf-8")
    for handler in (
        "openAuthModal",
        "closeAuthModal",
        "resetAuthModalFields",
        "switchAuthTab",
        "toggleAuthPasswordVisibility",
    ):
        assert f"function {handler}(" not in page
        assert f"window.{handler} = {handler}" in auth_controls
    assert "function openForgotPasswordStep(" not in page
    assert "window.currentAuthTab = tab" in auth_controls
    assert "auth-form-container" in auth_controls
    assert "firebase" not in auth_controls.lower()
    assert "const isRegister = window.currentAuthTab === 'register'" in page


def test_auth_ui_keeps_the_signed_out_sign_in_state_parseable():
    """The app page must render its signed-out state instead of a stray second else."""
    page = INDEX.read_text(encoding="utf-8")
    assert "navAuthBtn.innerHTML = 'Sign In';" in page
    assert "// If unauthenticated on /app, immediately redirect to /auth" not in page


def test_adherence_renderer_keeps_its_hoisted_inline_owner():
    """The modal controller must call the renderer, never replace it with a recursive bridge."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/adherence-modal-controls.js").read_text(encoding="utf-8")
    assert page.count("function updateAdherenceUI(") == 1
    assert "window.updateAdherenceUI = (...args)" not in page
    assert "if (typeof window.updateAdherenceUI === 'function')" in controls


def test_live_voice_controller_owns_its_profile_renderer():
    """Starting a live call must not invoke an undefined persona UI method."""
    controls = (ROOT / "static/js/components/live-voice-call.js").read_text(encoding="utf-8")
    assert "this.updateDoctorProfileUI();" in controls
    assert "updateDoctorProfileUI: function()" in controls
    assert "call-doctor-name" in controls
    assert "call-doctor-title" in controls
    for method in ("cleanMedicalText", "switchLanguage", "initWebAudioDSP", "initContinuousSpeechRecognition"):
        assert f"{method}: function(" in controls


def test_lab_upload_modal_controls_have_one_inline_implementation():
    """Keep the Lab Upload UI shell modular without moving OCR behavior."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/lab-upload-modal-controls.js").read_text(encoding="utf-8")
    for handler in ("openLabUploadModal", "closeLabUploadModal"):
        assert f"window.{handler} = {handler}" in controls
        assert f"function {handler}" not in page


def test_shared_modal_closer_has_one_active_modular_owner():
    """Keep shared modal closing behavior available to modal-control modules."""
    page = INDEX.read_text(encoding="utf-8")
    modal_core = (ROOT / "static/js/modules/modal-core.js").read_text(encoding="utf-8")
    assert "/static/js/modules/modal-core.js" in page
    assert "window.closeAllModals = closeAllModals" in modal_core
    assert "function closeAllModals" not in page
    assert "patient-care-toolkit-modal" in modal_core


def test_inline_chat_runtime_state_is_synchronized_for_modules():
    """Keep the active inline chat lifecycle visible to modular consumers."""
    page = INDEX.read_text(encoding="utf-8")
    assert "function syncChatRuntimeState()" in page
    assert "window.currentChatMessages = currentChatMessages" in page
    assert "syncChatRuntimeState();\n            if (!currentSessionId" in page


def test_new_chat_keeps_state_lifecycle_inline_and_view_reset_modular():
    """Keep session persistence canonical while sharing the view reset safely."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/chat-consultation.js").read_text(encoding="utf-8")
    assert page.count("function startNewChat(") == 1
    assert "persistActiveChatSession();" in page
    assert "window.HerbalistChatSessionUI.resetNewChatView();" in page
    assert "window.HerbalistChatSessionUI = { resetNewChatView, clearAttachmentPreview }" in controls
    assert "function startNewChat" not in controls
    assert "window.startNewChat = startNewChat;" in page
    assert "herbalist_active_session_id" in page
    assert "pendingAttachment = null;" in page
    assert "window.HerbalistChatSessionUI.clearAttachmentPreview();" in page


def test_recents_guest_prompt_delegates_to_its_modular_owner():
    """Keep guest recents presentation separate from stored-session handling."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/recents-guest-prompt-ui.js").read_text(encoding="utf-8")
    assert "/static/js/modules/recents-guest-prompt-ui.js" in page
    assert "window.HerbalistRecentsGuestPromptUI = { renderGuestPrompt, renderEmptyState, renderItems }" in controls
    assert "window.HerbalistRecentsGuestPromptUI.renderGuestPrompt(container);" in page
    assert "window.HerbalistRecentsGuestPromptUI.renderEmptyState(container);" in page
    assert "window.HerbalistRecentsGuestPromptUI.renderItems(items, currentSessionId);" in page
    assert "onmouseover=\"this.style.background='var(--accent-green)'" in controls
    assert "getLocalChatSessions()" in page
    assert "saveLocalChatSessions(localSessions)" in page


def test_chat_session_title_derivation_has_one_modular_owner():
    """Keep title derivation pure while session persistence remains inline."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/chat-session-title.js").read_text(encoding="utf-8")
    assert "/static/js/modules/chat-session-title.js" in page
    assert "window.HerbalistChatSessionTitle = { deriveSessionTitle }" in controls
    assert "window.HerbalistChatSessionTitle.deriveSessionTitle(" in page
    assert "saveLocalChatSessions(sessions);" in page
    assert "syncSessionToFirestore(currentSessionId, sessions[currentSessionId]);" in page


def test_chat_session_restore_cleanup_has_one_modular_owner():
    """Keep temporary-message cleanup pure while restoring and saving stays inline."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/chat-session-restore.js").read_text(encoding="utf-8")
    assert "/static/js/modules/chat-session-restore.js" in page
    assert "window.HerbalistChatSessionRestore = { sanitizeRestoredMessages }" in controls
    assert "window.HerbalistChatSessionRestore.sanitizeRestoredMessages(session.messages);" in page
    assert "saveLocalChatSessions(sessions);" in page
    assert "appendBubble(msg.role, msg.html, true);" in page


def test_chat_context_menu_has_one_active_global_handler():
    """Keep the selected-session context menu from being silently overridden."""
    page = INDEX.read_text(encoding="utf-8")
    assert page.count("function openContextMenu(") == 1
    assert page.count("function legacyOpenRecentContextMenu(") == 1
    assert "currentSelectedChatId = sessionId;" in page
    assert "const menu = document.getElementById('context-menu');" in page
    assert page.count("function shareConversation(") == 1
    assert page.count("function legacyShareConversation(") == 1


def test_inline_consumers_read_module_owned_clinical_modality():
    """Avoid saving or sending a stale modality after the selector changes."""
    page = INDEX.read_text(encoding="utf-8")
    assert "clinical_modality: window.currentClinicalModality || 'auto'" in page
    assert "modality: window.currentClinicalModality || 'auto'" in page
    assert "String(window.activeClinicalModality || '').toLowerCase()" in page


def test_inline_user_state_is_synchronized_for_modules():
    """Expose the live authenticated/guest user without changing auth writes."""
    page = INDEX.read_text(encoding="utf-8")
    assert "function syncUserRuntimeState()" in page
    assert "window.currentUserState = currentUserState" in page
    assert page.count("syncUserRuntimeState();") >= 2


def test_care_suite_entry_points_have_one_active_modular_owner():
    """Keep Synergy and Recovery/Vault opening on the unified Care Suite."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/care-suite-controls.js").read_text(encoding="utf-8")
    for handler in (
        "openSynergyLabModal",
        "closeSynergyLabModal",
        "openVaultRecoveryModal",
        "closeVaultRecoveryModal",
    ):
        assert f"window.{handler} = {handler}" in controls
        assert f"function {handler}" not in page
    assert "legacyOpenSynergyLabModal" not in page
    assert "legacyOpenVaultRecoveryModal" not in page
    assert "window.openPatientCareToolkitModal?.('synergy')" in controls
    assert "window.openPatientCareToolkitModal?.('recovery')" in controls
    assert controls.count("modal.classList.add('open')") == 2
    assert controls.count("modal.classList.remove('open')") == 2


def test_saved_prescriptions_modal_has_one_active_modular_owner():
    """Keep the library modal controls separate from prescription data operations."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/prescriptions-modal-controls.js").read_text(encoding="utf-8")
    for handler in ("openPrescriptionsModal", "closePrescriptionsModal"):
        assert f"window.{handler} = {handler}" in controls
        assert f"function {handler}" not in page
    assert "window.loadSavedPrescriptions?.()" in controls
    assert "legacyOpenPrescriptionsModal" not in page


def test_saved_prescription_filter_uses_the_canonical_record_list():
    """Search must filter records, not only currently-rendered DOM cards."""
    page = INDEX.read_text(encoding="utf-8")
    assert page.count("function filterSavedPrescriptions(") == 1
    assert "cachedAllSavedPrescriptions.filter(item =>" in page
    assert "document.querySelectorAll('#prescriptions-list-container > div')" not in page


def test_research_modal_close_controls_have_one_active_modular_owner():
    """Keep close buttons modular without changing research tool behavior."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/research-modal-controls.js").read_text(encoding="utf-8")
    for handler in ("closePharmacopeiaModal", "closeScannerModal", "closeRagModal"):
        assert f"window.{handler} = {handler}" in controls
        assert f"function {handler}" not in page
    assert "legacyCloseRagModal" not in page


def test_safety_checker_modal_controls_have_one_active_modular_owner():
    """Keep Safety Checker presentation separate from request behavior."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/safety-checker-modal-controls.js").read_text(encoding="utf-8")
    for handler in ("openSafetyCheckerModal", "closeSafetyCheckerModal", "switchSafetyTab"):
        assert f"window.{handler} = {handler}" in controls
        assert f"function {handler}" not in page
    assert "/api/herb-drug-check" in page
    assert "/api/synthetic-substitute" in page


def test_utility_modal_controls_have_one_active_modular_owner():
    """Keep Clinical Profile and Help Guide presentation controls modular."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/utility-modal-controls.js").read_text(encoding="utf-8")
    for handler in (
        "openClinicalModal",
        "closeClinicalModal",
        "openHelpGuideModal",
        "closeHelpGuideModal",
    ):
        assert f"window.{handler} = {handler}" in controls
        assert f"function {handler}" not in page
    assert page.count("function saveClinicalProfile(") == 1


def test_adherence_modal_controls_have_one_active_modular_owner():
    """Keep modal presentation separate from adherence records and reminders."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/adherence-modal-controls.js").read_text(encoding="utf-8")
    for handler in ("openAdherenceModal", "closeAdherenceModal"):
        assert f"window.{handler} = {handler}" in controls
        assert f"function {handler}" not in page
    assert "window.updateAdherenceUI();" in controls
    assert page.count("function updateAdherenceUI(") == 1
    assert "window.updateAdherenceUI = (...args)" not in page
    assert page.count("function logDoseTaken(") == 1
    assert "localStorage.setItem('herbalist_adherence'" in page


def test_attachment_popover_has_one_active_modular_owner():
    """Keep popover presentation separate from upload and scanner behavior."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/attachment-popover-controls.js").read_text(encoding="utf-8")
    assert "window.toggleAttachmentPopover = toggleAttachmentPopover" in controls
    assert "function toggleAttachmentPopover" not in page
    assert "attachment-popover-menu" in controls
    assert "triggerChatFileUpload();" in page
    assert "function triggerVisionAiScanner(" in page


def test_custom_dialog_engine_delegates_to_its_modular_owner():
    """Keep custom-dialog behavior modular while retaining legacy call names."""
    page = INDEX.read_text(encoding="utf-8")
    dialogs = (ROOT / "static/js/modules/custom-dialogs.js").read_text(encoding="utf-8")
    assert "/static/js/modules/custom-dialogs.js" in page
    for handler, module_handler in (
        ("escapeDialogHtml", "escapeHtml"),
        ("showCustomConfirm", "showConfirm"),
        ("showCustomPrompt", "showPrompt"),
        ("showCustomAlert", "showAlert"),
    ):
        assert f"function {handler}(" in page
        assert f"window.HerbalistDialogs.{module_handler}" in page
    assert "window.HerbalistDialogs = { escapeHtml, showConfirm, showPrompt, showAlert }" in dialogs
    assert "window.showCustomConfirm = showConfirm" in dialogs
    assert "window.showCustomPrompt = showPrompt" in dialogs
    assert "window.showCustomAlert = showAlert" in dialogs
    assert "custom-dialog-overlay" in dialogs


def test_voice_equalizer_control_has_one_active_modular_owner():
    """Keep visualizer visibility separate from audio and speech behavior."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/voice-equalizer-controls.js").read_text(encoding="utf-8")
    assert "/static/js/modules/voice-equalizer-controls.js" in page
    assert "window.showVoiceEqualizer = showVoiceEqualizer" in controls
    assert "function showVoiceEqualizer" not in page
    assert "voice-wave-visualizer" in controls
    assert "function speakText(" in page


def test_dynamic_prompt_chip_renderer_delegates_to_its_modular_owner():
    """Keep suggestion markup modular without moving chat submission."""
    page = INDEX.read_text(encoding="utf-8")
    chips = (ROOT / "static/js/modules/dynamic-prompt-chips.js").read_text(encoding="utf-8")
    assert "/static/js/modules/dynamic-prompt-chips.js" in page
    assert "window.renderDynamicPromptChips = renderDynamicPromptChips" in chips
    assert "window.HerbalistPromptChips.renderDynamicPromptChips" in page
    assert page.count("function selectDynamicPrompt(") == 1
    assert page.count("function submitQuery(") == 1


def test_brew_timer_chime_delegates_to_its_modular_owner():
    """Keep the audio cue modular without moving timer state or scheduling."""
    page = INDEX.read_text(encoding="utf-8")
    chime = (ROOT / "static/js/modules/brew-timer-chime.js").read_text(encoding="utf-8")
    assert "/static/js/modules/brew-timer-chime.js" in page
    assert "window.playBrewTimerChime = playBrewTimerChime" in chime
    assert "function playBrewTimerChime(" not in page
    assert "function legacyPlayBrewTimerChime(" in page
    assert "AudioContext" in chime


def test_textarea_autoexpand_delegates_to_its_modular_owner():
    """Keep textarea sizing modular without moving chat input behavior."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/textarea-autoexpand.js").read_text(encoding="utf-8")
    assert "/static/js/modules/textarea-autoexpand.js" in page
    assert "window.autoExpandTextarea = autoExpandTextarea" in controls
    assert "function autoExpandTextarea(" not in page
    assert "function legacyAutoExpandTextarea(" in page
    assert "Math.min(el.scrollHeight, 120)" in controls
    assert page.count("function handleKeyPress(") == 1


def test_disclaimer_banner_has_one_active_modular_owner():
    """Keep dismissal behavior modular without renaming its preference key."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/disclaimer-banner-controls.js").read_text(encoding="utf-8")
    assert "/static/js/modules/disclaimer-banner-controls.js" in page
    assert "window.dismissDisclaimer = dismissDisclaimer" in controls
    assert "function dismissDisclaimer" not in page
    assert "herbalist_disclaimer_dismissed" in controls


def test_profile_form_toggle_has_one_active_modular_owner():
    """Keep profile-form presentation separate from profile records and APIs."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/profile-form-controls.js").read_text(encoding="utf-8")
    assert "/static/js/modules/profile-form-controls.js" in page
    assert "window.toggleAddProfileForm = toggleAddProfileForm" in controls
    assert "function toggleAddProfileForm" not in page
    assert "/api/profiles" in page


def test_signout_modal_close_has_one_active_modular_owner():
    """Keep sign-out dismissal separate from account and token handling."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/signout-modal-controls.js").read_text(encoding="utf-8")
    assert "/static/js/modules/signout-modal-controls.js" in page
    assert "window.closeSignOutModal = closeSignOutModal" in controls
    assert "function closeSignOutModal" not in page
    assert page.count("function handleSignOut(") == 1
    assert page.count("function promptSignOutModal(") == 1


def test_voice_toggle_ui_delegates_to_its_modular_owner():
    """Keep speaker-button rendering separate from voice state and persistence."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/voice-toggle-ui.js").read_text(encoding="utf-8")
    assert "/static/js/modules/voice-toggle-ui.js" in page
    assert "window.HerbalistVoiceToggleUI = { renderVoiceToggleUI }" in controls
    assert "return window.HerbalistVoiceToggleUI.renderVoiceToggleUI(isVoiceEnabled);" in page
    assert "herbalist_voice_enabled" in page
    assert page.count("function toggleVoice(") == 1


def test_telehealth_status_ui_delegates_to_its_modular_owner():
    """Keep telehealth visuals separate from microphone and call behavior."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/telehealth-status-ui.js").read_text(encoding="utf-8")
    assert "/static/js/modules/telehealth-status-ui.js" in page
    assert "window.HerbalistTelehealthStatusUI = { setOrbState, updateTelehealthStatus }" in controls
    assert "return window.HerbalistTelehealthStatusUI.setOrbState(state);" in page
    assert "return window.HerbalistTelehealthStatusUI.updateTelehealthStatus(msg, type);" in page
    assert page.count("function toggleTelehealthMic(") == 2


def test_telehealth_timer_ui_delegates_to_its_modular_owner():
    """Keep timer formatting separate from telehealth timer lifecycle."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/telehealth-timer-ui.js").read_text(encoding="utf-8")
    assert "/static/js/modules/telehealth-timer-ui.js" in page
    assert "window.HerbalistTelehealthTimerUI = { renderTelehealthTimer }" in controls
    assert "return window.HerbalistTelehealthTimerUI.renderTelehealthTimer(telehealthSecondsElapsed);" in page
    assert "setInterval" in page
    assert "clearInterval" in page


def test_drug_scanner_modal_controls_have_one_active_modular_owner():
    """Keep scanner visibility separate from OCR and clinical handoff."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/drug-scanner-modal-controls.js").read_text(encoding="utf-8")
    assert "/static/js/modules/drug-scanner-modal-controls.js" in page
    for handler in ("openDrugScannerModal", "closeDrugScannerModal"):
        assert f"window.{handler} = {handler}" in controls
        assert f"function {handler}" not in page
    assert "/api/vision/scan-drug" in page
    assert page.count("function prescribeScannedDrugInteraction(") == 1


def test_thought_hud_toggle_delegates_to_its_modular_owner():
    """Keep Thought HUD presentation separate from streamed clinical steps."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/thought-hud-controls.js").read_text(encoding="utf-8")
    assert "/static/js/modules/thought-hud-controls.js" in page
    assert "window.HerbalistThoughtHudControls = { toggleThoughtHUD }" in controls
    assert "return window.HerbalistThoughtHudControls.toggleThoughtHUD(msgId);" in page
    assert page.count("function updateThoughtHUDStep(") == 1
    step_controls = (ROOT / "static/js/modules/thought-hud-step-ui.js").read_text(encoding="utf-8")
    assert "window.HerbalistThoughtHudStepUI = { updateThoughtHUDStep }" in step_controls
    assert "return window.HerbalistThoughtHudStepUI.updateThoughtHUDStep(msgId, stepData);" in page


def test_triage_stepper_ui_delegates_to_its_modular_owner():
    """Keep progress presentation separate from triage and diagnosis logic."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/triage-stepper-ui.js").read_text(encoding="utf-8")
    assert "/static/js/modules/triage-stepper-ui.js" in page
    assert "window.HerbalistTriageStepperUI = { updateTriageStepper }" in controls
    assert "return window.HerbalistTriageStepperUI.updateTriageStepper(currentPhase);" in page
    assert page.count("function showTriageProgress(") == 1
    assert page.count("function renderFullDiagnosis(") == 1


def test_triage_progress_ui_delegates_to_its_modular_owner():
    """Keep phase-bar presentation separate from streamed triage decisions."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/triage-progress-ui.js").read_text(encoding="utf-8")
    assert "/static/js/modules/triage-progress-ui.js" in page
    assert "window.HerbalistTriageProgressUI = { showTriageProgress }" in controls
    assert "return window.HerbalistTriageProgressUI.showTriageProgress(currentPhase);" in page
    assert "showTriageProgress(dataObj.triage_phase);" in page
    assert "showTriageProgress(data.triage_phase);" in page


def test_chat_file_input_control_has_one_active_modular_owner():
    """Keep file-picker presentation separate from attachment state and uploads."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/chat-file-input-control.js").read_text(encoding="utf-8")
    assert "/static/js/modules/chat-file-input-control.js" in page
    assert "window.triggerChatFileUpload = triggerChatFileUpload" in controls
    assert "function triggerChatFileUpload" not in page
    assert page.count("function handleChatFileSelected(") == 1
    assert "let pendingAttachment = null;" in page


def test_clipboard_fallback_delegates_to_its_modular_owner():
    """Keep clipboard fallback separate from prescription-data formatting."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/clipboard-fallback.js").read_text(encoding="utf-8")
    assert "/static/js/modules/clipboard-fallback.js" in page
    assert "window.HerbalistClipboard = { fallbackCopy }" in controls
    assert "return window.HerbalistClipboard.fallbackCopy(text, btnEl);" in page
    assert page.count("function copyPrescriptionText(") == 1
    assert "activePrescriptionPayload" in page


def test_scanner_file_input_control_has_one_active_modular_owner():
    """Keep file-picker presentation separate from Vision AI scan processing."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/scanner-file-input-control.js").read_text(encoding="utf-8")
    assert "/static/js/modules/scanner-file-input-control.js" in page
    assert "window.triggerFileInput = triggerFileInput" in controls
    assert "function triggerFileInput" not in page
    assert page.count("function handleImageSelected(") == 1
    assert "/api/vision-scan" in page


def test_forgot_password_ui_has_one_active_modular_owner():
    """Keep the reset-form transition separate from Firebase reset requests."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/forgot-password-ui.js").read_text(encoding="utf-8")
    assert "/static/js/modules/forgot-password-ui.js" in page
    assert "window.openForgotPasswordStep = openForgotPasswordStep" in controls
    assert "function openForgotPasswordStep" not in page
    assert page.count("function handleSendPasswordResetEmail(") == 1
    assert page.count("function legacyHandleSendPasswordResetEmail(") == 1
    assert "sendPasswordResetEmail" in page


def test_email_validation_has_one_active_modular_owner():
    """Keep pure email validation separate from authentication requests."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/email-validation.js").read_text(encoding="utf-8")
    assert "/static/js/modules/email-validation.js" in page
    assert "window.isValidEmail = isValidEmail" in controls
    assert "function isValidEmail" not in page
    assert "sendPasswordResetEmail" in page
    assert "fetch('/api/auth/" in page


def test_vault_tab_ui_delegates_to_its_modular_owner():
    """Keep tab presentation separate from recovery and patient data loading."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/vault-tab-ui.js").read_text(encoding="utf-8")
    assert "/static/js/modules/vault-tab-ui.js" in page
    assert "window.HerbalistVaultTabUI = { renderVaultTab }" in controls
    assert "window.HerbalistVaultTabUI.renderVaultTab(tab)" in page
    assert "loadRecoveryTimelineFromBackend();" in page
    assert "/api/profiles" in page


def test_emergency_modal_close_control_has_one_active_modular_owner():
    """Keep emergency dismissal separate from the clinical triage flow."""
    page = INDEX.read_text(encoding="utf-8")
    controls = (ROOT / "static/js/modules/emergency-modal-controls.js").read_text(encoding="utf-8")
    assert "window.closeEmergencyModal = closeEmergencyModal" in controls
    assert "window.showEmergencyModal = showEmergencyModal" in controls
    assert "function closeEmergencyModal" not in page
    assert "function showEmergencyModal" not in page


def test_existing_client_data_keys_are_not_renamed_or_dropped():
    """Modularization must preserve users' browser-resident consultations and vault data."""
    page = INDEX.read_text(encoding="utf-8")
    required_keys = {
        "herbalist_active_session_id",
        "herbalist_active_cook_rx",
        "herbalist_adherence",
        "herbalist_chat_voice_lang",
        "herbalist_jwt_token",
        "herbalist_modality",
        "herbalist_saved_prescriptions",
        "herbalist_symptom_log",
        "herbalist_user",
        "herbalist_user_profile",
    }
    missing = [key for key in required_keys if key not in page]
    assert not missing, f"migration dropped existing client-data keys: {missing}"
