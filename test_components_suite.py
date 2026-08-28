import os
import re
import unittest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class ComponentsSuite(unittest.TestCase):
    def test_01_component_files_exist(self):
        """Verify all 5 modular component files and CSS design system exist on disk"""
        files = [
            "static/css/components.css",
            "static/js/components/agent-transparency.js",
            "static/js/components/message-actions.js",
            "static/js/components/citation-popover.js",
            "static/js/components/prescription-pdf.js",
            "static/js/components/command-palette.js"
        ]
        for f in files:
            self.assertTrue(os.path.exists(f), f"Missing modular component file: {f}")
        print("\n[COMPONENT AUDIT 1 PASS] All 5 component files and CSS design system exist.")

    def test_02_static_route_serving(self):
        """Verify FastAPI serves all static assets over HTTP 200"""
        endpoints = [
            "/static/css/components.css",
            "/static/js/components/agent-transparency.js",
            "/static/js/components/message-actions.js",
            "/static/js/components/citation-popover.js",
            "/static/js/components/prescription-pdf.js",
            "/static/js/components/command-palette.js"
        ]
        for ep in endpoints:
            response = client.get(ep)
            self.assertEqual(response.status_code, 200, f"Failed to serve {ep} over HTTP: {response.status_code}")
        print("[COMPONENT AUDIT 2 PASS] FastAPI static router successfully serves all component assets with HTTP 200.")

    def test_03_index_html_integration(self):
        """Verify index.html cleanly imports stylesheet and 5 component scripts"""
        with open('index.html', 'r', encoding='utf-8') as f:
            html = f.read()

        self.assertIn('<link rel="stylesheet" href="/static/css/components.css">', html)
        self.assertIn('<script src="/static/js/components/agent-transparency.js"></script>', html)
        self.assertIn('<script src="/static/js/components/message-actions.js"></script>', html)
        self.assertIn('<script src="/static/js/components/citation-popover.js"></script>', html)
        self.assertIn('<script src="/static/js/components/prescription-pdf.js"></script>', html)
        self.assertIn('<script src="/static/js/components/command-palette.js"></script>', html)
        print("[COMPONENT AUDIT 3 PASS] index.html cleanly imports modular component scripts.")

    def test_04_agent_transparency_api(self):
        """Verify AgentTransparency component exports required methods"""
        with open('static/js/components/agent-transparency.js', 'r', encoding='utf-8') as f:
            code = f.read()

        self.assertIn('AgentTransparency', code)
        self.assertIn('renderHUD', code)
        self.assertIn('startTool', code)
        self.assertIn('completeTool', code)
        self.assertIn('finishAll', code)
        print("[COMPONENT AUDIT 4 PASS] Feature 1: Agent Transparency API verified.")

    def test_05_message_actions_api(self):
        """Verify MessageActions component implements Copy, Regenerate, Edit, and Feedback"""
        with open('static/js/components/message-actions.js', 'r', encoding='utf-8') as f:
            code = f.read()

        self.assertIn('MessageActions', code)
        self.assertIn('copyMessageText', code)
        self.assertIn('editPatientPrompt', code)
        self.assertIn('regenerateLastResponse', code)
        self.assertIn('rateResponse', code)
        print("[COMPONENT AUDIT 5 PASS] Feature 2: Message-Level Actions API verified.")

    def test_06_citation_popover_api(self):
        """Verify CitationPopover component implements PubMed cards and Botanical specimen chips"""
        with open('static/js/components/citation-popover.js', 'r', encoding='utf-8') as f:
            code = f.read()

        self.assertIn('CitationPopover', code)
        self.assertIn('showCitation', code)
        self.assertIn('showSpecimen', code)
        self.assertIn('BOTANICAL_KNOWLEDGE_BASE', code)
        print("[COMPONENT AUDIT 6 PASS] Feature 3: Interactive Citation & Botanical Chips API verified.")

    def test_07_prescription_pdf_api(self):
        """Verify PrescriptionPDF component implements printable clinical Rx generation"""
        with open('static/js/components/prescription-pdf.js', 'r', encoding='utf-8') as f:
            code = f.read()

        self.assertIn('PrescriptionPDF', code)
        self.assertIn('exportActiveRx', code)
        self.assertIn('generatePrescriptionHTML', code)
        self.assertIn('renderPrintableSheet', code)
        print("[COMPONENT AUDIT 7 PASS] Feature 4: 1-Click Clinical PDF Prescription Export API verified.")

    def test_08_command_palette_api(self):
        """Verify CommandPalette component implements Ctrl+K spotlight and slash commands"""
        with open('static/js/components/command-palette.js', 'r', encoding='utf-8') as f:
            code = f.read()

        self.assertIn('CommandPalette', code)
        self.assertIn('SLASH_COMMANDS', code)
        self.assertIn('COMMANDS', code)
        self.assertIn('bindGlobalShortcuts', code)
        self.assertIn('bindSlashAutocomplete', code)
        print("[COMPONENT AUDIT 8 PASS] Feature 5: Command Palette (Ctrl+K) & Slash Commands API verified.")

if __name__ == '__main__':
    unittest.main()
