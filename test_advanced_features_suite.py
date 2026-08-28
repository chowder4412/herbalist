"""
═══════════════════════════════════════════════════════════════════
HERBALIST AI — ADVANCED FEATURES QA & AUDIT SUITE
Automated testing of Live Voice Call (VAD), Recovery Tracker, and CYP450 Matrix.
═══════════════════════════════════════════════════════════════════
"""

import os
import subprocess
import unittest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class AdvancedFeaturesSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('index.html', 'r', encoding='utf-8') as f:
            cls.html = f.read()

    def test_01_component_files_exist(self):
        """Audit 1: Verify all 3 advanced component files exist on disk"""
        files = [
            'static/js/components/live-voice-call.js',
            'static/js/components/recovery-tracker.js',
            'static/js/components/cyp450-safety-matrix.js'
        ]
        for f in files:
            self.assertTrue(os.path.exists(f), f"Missing component file: {f}")
            self.assertGreater(os.path.getsize(f), 500, f"Component file {f} is too small")
        print("\n[ADVANCED QA 1 PASS] All 3 advanced component files exist and are populated.")

    def test_02_static_route_serving(self):
        """Audit 2: Verify FastAPI serves all 3 components with HTTP 200"""
        endpoints = [
            "/static/js/components/live-voice-call.js",
            "/static/js/components/recovery-tracker.js",
            "/static/js/components/cyp450-safety-matrix.js"
        ]
        for url in endpoints:
            res = client.get(url)
            self.assertEqual(res.status_code, 200, f"Failed fetching {url}")
            self.assertIn("javascript", res.headers.get("content-type", ""))
        print("[ADVANCED QA 2 PASS] FastAPI static route successfully serves all 3 components.")

    def test_03_js_syntax_and_ast(self):
        """Audit 3: Node.js AST parsing to verify syntax of all components"""
        files = [
            'static/js/components/live-voice-call.js',
            'static/js/components/recovery-tracker.js',
            'static/js/components/cyp450-safety-matrix.js'
        ]
        for path in files:
            res = subprocess.run(["node", "--check", path], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"JS Syntax error in {path}:\n{res.stderr}")
        print("[ADVANCED QA 3 PASS] 0 syntax errors across all 3 components.")

    def test_04_nodejs_dom_runtime_simulation(self):
        """Audit 4: Node.js DOM functional simulation of Live Voice, Tracker, and CYP450 Matrix"""
        simulation_script = """
        class MockElement {
            constructor(tag, id = '') {
                this.tagName = tag.toUpperCase();
                this.id = id;
                this.className = '';
                this.style = {};
                this.children = [];
                this._innerHTML = '';
                this.innerText = '';
                this.value = '';
                this.dataset = {};
                this.parentElement = null;
            }
            get innerHTML() { return this._innerHTML; }
            set innerHTML(val) {
                this._innerHTML = val;
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
            querySelector(selector) { return this.children[0] || null; }
            querySelectorAll(selector) { return this.children; }
            addEventListener(ev, fn) { this['on' + ev] = fn; }
            contains(el) { return true; }
            focus() {}
            getContext() { return { clearRect:()=>{}, beginPath:()=>{}, moveTo:()=>{}, lineTo:()=>{}, stroke:()=>{} }; }
        }

        const elementsMap = {};
        global.document = {
            body: new MockElement('body', 'body'),
            createElement: (tag) => new MockElement(tag),
            getElementById: (id) => {
                if (!elementsMap[id]) {
                    elementsMap[id] = new MockElement('div', id);
                    if (id.includes('select') || id.includes('input') || id.includes('vital')) elementsMap[id].value = '120/80';
                }
                return elementsMap[id];
            },
            querySelectorAll: () => [],
            addEventListener: () => {}
        };
        global.window = {
            innerWidth: 1200,
            innerHeight: 800,
            showToast: (m, t) => { global.lastToast = { m, t }; },
            speechSynthesis: { cancel: ()=>{}, speak: ()=>{} },
            SpeechRecognition: class { start(){} stop(){} },
            requestAnimationFrame: (cb) => 1,
            cancelAnimationFrame: () => {}
        };
        global.localStorage = {
            _data: {},
            getItem: (k) => global.localStorage._data[k] || null,
            setItem: (k, v) => { global.localStorage._data[k] = v; }
        };
        global.SpeechSynthesisUtterance = class {
            constructor(text) { this.text = text; }
        };

        const fs = require('fs');

        // Test Feature 1: Live Voice Call
        eval(fs.readFileSync('static/js/components/live-voice-call.js', 'utf8'));
        if (!window.LiveVoiceCall) throw new Error("LiveVoiceCall not exported");
        window.LiveVoiceCall.start('ha');
        window.LiveVoiceCall.toggleMute();
        window.LiveVoiceCall.switchLanguage('yo');
        window.LiveVoiceCall.end();

        // Test Feature 2: Recovery Tracker
        eval(fs.readFileSync('static/js/components/recovery-tracker.js', 'utf8'));
        if (!window.RecoveryTracker) throw new Error("RecoveryTracker not exported");
        window.RecoveryTracker.open();
        window.RecoveryTracker.submitCheckIn();
        window.RecoveryTracker.generateAIReview();
        window.RecoveryTracker.close();

        // Test Feature 3: CYP450 Safety Matrix
        eval(fs.readFileSync('static/js/components/cyp450-safety-matrix.js', 'utf8'));
        if (!window.CYP450SafetyMatrix) throw new Error("CYP450SafetyMatrix not exported");
        window.CYP450SafetyMatrix.open('Metformin', 'Vernonia amygdalina (Bitter Leaf)');
        window.CYP450SafetyMatrix.onSelectChange();
        window.CYP450SafetyMatrix.close();

        console.log("ADVANCED_FEATURES_SIMULATION_PASS");
        """

        res = subprocess.run(["node", "-e", simulation_script], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Node.js DOM Simulation failed:\n{res.stderr}")
        self.assertIn("ADVANCED_FEATURES_SIMULATION_PASS", res.stdout)
        print("[ADVANCED QA 4 PASS] Node.js DOM simulation passed 100% for Live Voice, Recovery Tracker, and CYP450 Matrix.")

if __name__ == '__main__':
    unittest.main()
