/**
 * HERBALIST AI — VOICE EQUALIZER CONTROL
 * Visualizer visibility only; audio and speech behavior remain inline.
 */

(function(window) {
    'use strict';

    function showVoiceEqualizer(active = true) {
        const visualizer = document.getElementById('voice-wave-visualizer');
        if (visualizer) visualizer.style.display = active ? 'flex' : 'none';
    }

    window.showVoiceEqualizer = showVoiceEqualizer;
})(window);
