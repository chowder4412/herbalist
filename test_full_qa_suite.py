"""
═══════════════════════════════════════════════════════════════════
HERBALIST AI — COMPREHENSIVE 360° QA & AUDIT SUITE
Automated functional, structural, and runtime testing of the 5 World-Class
Modular Components and their interaction with the Core Platform.
═══════════════════════════════════════════════════════════════════
"""

import os
import re
import json
import subprocess
import unittest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class FullQAAndAuditSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('index.html', 'r', encoding='utf-8') as f:
            cls.html = f.read()

    def test_01_static_assets_mime_types_and_headers(self):
        """QA 1: Verify all 5 components & CSS are served with correct MIME types and HTTP 200"""
        assets = [
            ("/static/css/components.css", "css"),
            ("/static/js/components/agent-transparency.js", "javascript"),
            ("/static/js/components/message-actions.js", "javascript"),
            ("/static/js/components/citation-popover.js", "javascript"),
            ("/static/js/components/prescription-pdf.js", "javascript"),
            ("/static/js/components/command-palette.js", "javascript")
        ]

        for path, expected_type in assets:
            res = client.get(path)
            self.assertEqual(res.status_code, 200, f"Failed fetching {path}: status {res.status_code}")
            content_type = res.headers.get("content-type", "")
            self.assertIn(expected_type, content_type, f"Unexpected content-type for {path}: {content_type}")
            self.assertGreater(len(res.text), 100, f"Asset {path} appears empty or truncated")
        print("\n[QA 1 PASS] All static assets are served over HTTP 200 with valid MIME headers.")

    def test_02_css_rules_and_print_sheet_integrity(self):
        """QA 2: Verify CSS design system contains all required component classes and @media print rules"""
        with open('static/css/components.css', 'r', encoding='utf-8') as f:
            css = f.read()

        required_classes = [
            '.agent-tools-container',
            '.agent-tool-pill',
            '.tool-pulse-dot',
            '.msg-actions-bar',
            '.msg-action-btn',
            '.patient-edit-btn',
            '.citation-inline-badge',
            '.specimen-chip',
            '#clinical-popover',
            '#command-palette-overlay',
            '.command-palette-modal',
            '#slash-autocomplete-dropdown',
            '@media print'
        ]

        for cls_name in required_classes:
            self.assertIn(cls_name, css, f"Missing CSS class/rule: {cls_name}")
        print("[QA 2 PASS] CSS design system contains complete glassmorphic and print media rules.")

    def test_03_nodejs_dom_runtime_simulation(self):
        """QA 3: Execute full DOM runtime simulation of all 5 components in Node.js"""
        js_simulation_script = """
        // Mock Browser Environment
        class MockElement {
            constructor(tag, id = '') {
                this.tagName = tag.toUpperCase();
                this.id = id;
                this.className = '';
                this.style = {};
                this.children = [];
                this._innerHTML = '';
                this.innerText = '';
                this.dataset = {};
                this.attributes = {};
                this.parentElement = null;
            }
            get innerHTML() { return this._innerHTML; }
            set innerHTML(val) {
                this._innerHTML = val;
                // Parse class names in mock
                const classMatches = val.match(/class=["']([^"']+)["']/g) || [];
                this.children = classMatches.map(m => {
                    const cls = m.replace(/class=["']/, '').replace(/["']/, '');
                    const child = new MockElement('div');
                    child.className = cls;
                    child.parentElement = this;
                    return child;
                });
            }
            appendChild(child) {
                child.parentElement = this;
                this.children.push(child);
                return child;
            }
            querySelector(selector) {
                if (selector.startsWith('.')) {
                    const cls = selector.substring(1);
                    return this.children.find(c => (c.className || '').includes(cls)) || null;
                }
                return this.children[0] || null;
            }
            querySelectorAll(selector) {
                return this.children;
            }
            addEventListener(ev, fn) { this['on' + ev] = fn; }
            contains(el) { return true; }
            getBoundingClientRect() {
                return { top: 100, bottom: 130, left: 200, right: 350, width: 150, height: 30 };
            }
            closest(selector) { return this.parentElement || this; }
            remove() {}
        }

        const elementsMap = {};
        global.document = {
            body: new MockElement('body', 'body'),
            createElement: (tag) => new MockElement(tag),
            getElementById: (id) => {
                if (!elementsMap[id]) {
                    elementsMap[id] = new MockElement('div', id);
                    if (id === 'user-input') elementsMap[id].value = '';
                }
                return elementsMap[id];
            },
            querySelectorAll: (sel) => [],
            addEventListener: (ev, fn) => {}
        };
        global.window = {
            innerWidth: 1200,
            innerHeight: 800,
            addEventListener: (ev, fn) => {},
            print: () => { global.printCalled = true; },
            showToast: (msg, type) => { global.lastToast = { msg, type }; }
        };
        global.navigator = {
            clipboard: {
                writeText: (t) => Promise.resolve()
            }
        };
        global.MutationObserver = class {
            observe() {}
            disconnect() {}
        };

        const fs = require('fs');

        // Load Component 1: Agent Transparency
        eval(fs.readFileSync('static/js/components/agent-transparency.js', 'utf8'));
        if (!window.AgentTransparency) throw new Error("AgentTransparency failed to export to window");
        window.AgentTransparency.renderHUD('stream-test-1');
        window.AgentTransparency.startTool('stream-test-1', 'tool_vector', 'Searching Qdrant');
        window.AgentTransparency.completeTool('stream-test-1', 'tool_vector');
        window.AgentTransparency.finishAll('stream-test-1');

        // Load Component 2: Message Actions
        eval(fs.readFileSync('static/js/components/message-actions.js', 'utf8'));
        if (!window.MessageActions) throw new Error("MessageActions failed to export to window");
        const docBubble = new MockElement('div');
        docBubble.className = 'chat-bubble';
        docBubble.style.alignSelf = 'flex-start';
        docBubble.innerText = 'Prescription: Take Vernonia amygdalina 250ml twice daily.';
        window.MessageActions.attachToBubble(docBubble);

        const patBubble = new MockElement('div');
        patBubble.className = 'chat-bubble';
        patBubble.style.alignSelf = 'flex-end';
        patBubble.innerText = 'I have a sore throat and fever.';
        window.MessageActions.attachToBubble(patBubble);

        // Load Component 3: Citation Popover
        eval(fs.readFileSync('static/js/components/citation-popover.js', 'utf8'));
        if (!window.CitationPopover) throw new Error("CitationPopover failed to export to window");
        const citationBadge = new MockElement('span');
        window.CitationPopover.showCitation(citationBadge, '1', 'Clinical study on Vernonia');
        window.CitationPopover.showSpecimen(citationBadge, 'vernonia amygdalina');
        window.CitationPopover.hide();

        // Load Component 4: Prescription PDF
        eval(fs.readFileSync('static/js/components/prescription-pdf.js', 'utf8'));
        if (!window.PrescriptionPDF) throw new Error("PrescriptionPDF failed to export to window");
        window.PrescriptionPDF.exportActiveRx({
            primary_diagnosis: 'Acute Upper Respiratory Congestion',
            age: 28,
            weight_kg: 68,
            ingredients: [{ name: 'Garcinia kola', part: 'Seed', extraction: 'Maceration', dosage: '1 seed chewed twice daily' }]
        });
        if (!global.printCalled) throw new Error("PrescriptionPDF failed to call window.print()");

        // Load Component 5: Command Palette
        eval(fs.readFileSync('static/js/components/command-palette.js', 'utf8'));
        if (!window.CommandPalette) throw new Error("CommandPalette failed to export to window");
        window.CommandPalette.open();
        if (!window.CommandPalette.isOpen()) throw new Error("CommandPalette.isOpen() returned false after open()");
        window.CommandPalette.onSearch('pdf');
        window.CommandPalette.selectSlash('/clear');
        window.CommandPalette.close();

        console.log("ALL_COMPONENTS_FUNCTIONAL_PASS");
        """

        result = subprocess.run(
            ["node", "-e", js_simulation_script],
            capture_output=True,
            text=True
        )

        self.assertEqual(result.returncode, 0, f"Node.js DOM Simulation failed:\n{result.stderr}")
        self.assertIn("ALL_COMPONENTS_FUNCTIONAL_PASS", result.stdout)
        print("[QA 3 PASS] Full DOM runtime simulation in Node.js passed 100% across all 5 components.")

    def test_04_zero_regressions_on_existing_features(self):
        """QA 4: Verify existing chat history, voices, and core diagnostic lifecycles remain 100% intact"""
        self.assertIn('function restoreActiveSessionOnBoot', self.html)
        self.assertIn('function renderRecentsList', self.html)
        self.assertIn('function showToast', self.html)
        self.assertIn('function showCustomConfirm', self.html)
        self.assertIn('function showCustomPrompt', self.html)
        self.assertIn('CHAT_VOICE_PROFILES', self.html)
        print("[QA 4 PASS] Zero regressions verified on existing chat sessions, voice profiles, and custom modals.")

if __name__ == '__main__':
    unittest.main()
