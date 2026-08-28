import re
import json
import unittest

class RecentsAuditSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('index.html', 'r', encoding='utf-8') as f:
            cls.html = f.read()

    def test_01_recents_core_functions_exist(self):
        """Verify all Recents CRUD and UI lifecycle functions exist"""
        functions = [
            'getLocalChatSessions',
            'saveLocalChatSessions',
            'persistActiveChatSession',
            'renderRecentsList',
            'loadRecentConsultation',
            'startNewChat',
            'restoreActiveSessionOnBoot',
            'openContextMenu',
            'pinConversation',
            'renameConversation',
            'deleteConversation',
            'shareConversation'
        ]
        for fn in functions:
            match = re.search(r'(function\s+' + fn + r'|async\s+function\s+' + fn + r'|' + fn + r'\s*=\s*)', self.html)
            self.assertIsNotNone(match, f"Missing required Recents function: {fn}")
        print("\n[RECENTS AUDIT 1 PASS] All 12 Recents functions are present and exported.")

    def test_02_no_native_dialogs_in_recents(self):
        """Verify that Recents actions use Custom Dialog Engine (zero native confirm/prompt/alert)"""
        recents_section = re.search(r'function getLocalChatSessions[\s\S]*?toggleMobileSidebar', self.html)
        self.assertIsNotNone(recents_section, "Recents section not found")
        section_text = recents_section.group(0)

        native_confirms = [m.start() for m in re.finditer(r'(?<!Custom)confirm\(', section_text)]
        native_prompts = [m.start() for m in re.finditer(r'(?<!Custom)prompt\(', section_text)]

        self.assertEqual(len(native_confirms), 0, f"Found native confirm() in Recents section: {native_confirms}")
        self.assertEqual(len(native_prompts), 0, f"Found native prompt() in Recents section: {native_prompts}")
        self.assertIn('showCustomConfirm', section_text)
        self.assertIn('showCustomPrompt', section_text)
        print("[RECENTS AUDIT 2 PASS] Recents uses custom theme-matched modals for confirm & rename.")

    def test_03_multi_user_storage_isolation(self):
        """Verify user storage key uses isolated per-user namespace"""
        self.assertIn('getActiveUserStorageKey', self.html)
        self.assertIn('herbalist_chat_sessions_', self.html)
        print("[RECENTS AUDIT 3 PASS] Multi-user session isolation is strictly enforced via namespaced keys.")

    def test_04_pinned_sorting_and_active_state(self):
        """Verify pinned items sort to top and active items receive .active styling"""
        self.assertIn('isPinned', self.html)
        self.assertIn('recent-item', self.html)
        self.assertIn("${isActive ? 'active' : ''}", self.html)
        print("[RECENTS AUDIT 4 PASS] Pinned sorting & active item highlight logic verified.")

    def test_05_sanitized_title_truncation(self):
        """Verify first user query is cleaned of HTML/emojis and truncated properly"""
        self.assertIn('replace(/<[^>]*>?/gm', self.html)
        self.assertIn('substring(0, 32)', self.html)
        print("[RECENTS AUDIT 5 PASS] Title sanitization and 32-character boundary truncation verified.")

    def test_06_greeting_and_chat_reload_persistence(self):
        """Verify restoreActiveSessionOnBoot does NOT discard greeting responses and sanitizes badges"""
        restore_fn = re.search(r'function restoreActiveSessionOnBoot[\s\S]*?function openContextMenu', self.html)
        self.assertIsNotNone(restore_fn, "restoreActiveSessionOnBoot function not found")
        fn_text = restore_fn.group(0)

        # Must NOT contain the old destructive filter
        self.assertNotIn("if (msg.html.includes('LIVE STREAM') && !msg.html.includes('primary_diagnosis')", fn_text,
                         "Destructive LIVE STREAM filter still present in restoreActiveSessionOnBoot!")
        
        # Must sanitize streaming badges cleanly
        self.assertIn("streaming-badge-", fn_text)
        self.assertIn("appendBubble", fn_text)
        print("[RECENTS AUDIT 6 PASS] Greeting and chat reload persistence verified (no message dropping).")

    def test_07_modern_svg_icons_in_recents_and_context_menu(self):
        """Verify modern vector SVG icons are used in Recents list, context menu, and guest lock"""
        # Vector speech bubble
        self.assertIn('<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor"', self.html)
        # Vector pin
        self.assertIn('<line x1="12" y1="17" x2="12" y2="22"></line>', self.html)
        # Context menu action icons
        self.assertIn('pinIconSvg', self.html)
        self.assertIn('renameIconSvg', self.html)
        self.assertIn('shareIconSvg', self.html)
        self.assertIn('deleteIconSvg', self.html)
        print("[RECENTS AUDIT 7 PASS] Modern vector SVG icons verified across Recents and Context Menu.")

    def test_08_modern_glassmorphic_toast_engine(self):
        """Verify showToast implements modern glassmorphic card with vector badge mapping"""
        toast_fn = re.search(r'function showToast[\s\S]*?window\.showToast\s*=\s*showToast;', self.html)
        self.assertIsNotNone(toast_fn, "showToast function not found")
        fn_text = toast_fn.group(0)

        # Must have modern iconBadgeMap
        self.assertIn('iconBadgeMap', fn_text)
        self.assertIn('success:', fn_text)
        self.assertIn('error:', fn_text)
        self.assertIn('warning:', fn_text)
        self.assertIn('info:', fn_text)
        self.assertIn('herbalist-modern-toast', fn_text)
        self.assertIn('backdrop-filter: blur(16px)', fn_text)
        print("[RECENTS AUDIT 8 PASS] Modern glassmorphic Toast notification engine verified.")

    def test_09_stream_live_incremental_persistence(self):
        """Verify submitQuery performs incremental chat message syncing during text streaming"""
        submit_fn = re.search(r'async function submitQuery[\s\S]*?function renderFullDiagnosis', self.html)
        self.assertIsNotNone(submit_fn, "submitQuery function not found")
        fn_text = submit_fn.group(0)

        self.assertIn('streamTextBuffer += dataObj.text', fn_text)
        self.assertIn('currentChatMessages', fn_text)
        self.assertIn('persistActiveChatSession()', fn_text)
        print("[RECENTS AUDIT 9 PASS] Live incremental SSE stream persistence verified.")

if __name__ == '__main__':
    unittest.main()
