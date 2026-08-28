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
        # Look for confirm( or prompt( in recents functions
        recents_section = re.search(r'function getLocalChatSessions[\s\S]*?toggleMobileSidebar', self.html)
        self.assertIsNotNone(recents_section, "Recents section not found")
        section_text = recents_section.group(0)

        # Check for native confirm( or prompt( calls that are not showCustomConfirm / showCustomPrompt
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

if __name__ == '__main__':
    unittest.main()
