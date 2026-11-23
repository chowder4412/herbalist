/**
 * HERBALIST AI — BREW TIMER CHIME
 * Short audio cue only; timer state and scheduling remain in Cook Mode.
 */

(function(window) {
    'use strict';

    function playBrewTimerChime() {
        try {
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(523.25, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.4);
            gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.8);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.8);
        } catch (e) {
            console.log('[Audio Synth Chime Notice]', e);
        }
    }

    window.playBrewTimerChime = playBrewTimerChime;
})(window);
