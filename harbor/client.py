#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from aiohttp import web


# HTML client interface
CLIENT_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Harbor - WebRTC Camera Stream</title>
<style>
:root {
  --primary: #2563eb;
  --primary-hover: #1d4ed8;
  --success: #16a34a;
  --success-hover: #15803d;
  --danger: #dc2626;
  --danger-hover: #b91c1c;
  --warning: #d97706;
  --secondary: #6b7280;
  --background: #f8fafc;
  --surface: #ffffff;
  --surface-alt: #f1f5f9;
  --text: #1e293b;
  --text-secondary: #64748b;
  --border: #e2e8f0;
  --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --radius: 8px;
  --radius-lg: 12px;
}

* {
  box-sizing: border-box;
}

html {
  overflow-x: hidden;
}

html, body {
  max-width: 100%;
  overflow-x: hidden;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.6;
  color: var(--text);
  background: var(--background);
  margin: 0;
  padding: 16px;
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 32px;
}

.header h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: var(--text);
}

.header p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 1.1rem;
}

.main-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

@media (min-width: 768px) {
  .main-grid {
    grid-template-columns: 1fr 400px;
  }
}

.video-section {
  background: var(--surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  overflow: hidden;
}

.video-container {
  position: relative;
  background: #000;
  aspect-ratio: 16/9;
}

.video-container video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  color: white;
}

.video-placeholder.hidden {
  display: none;
}

.video-placeholder svg {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.7;
}

.video-controls {
  padding: 20px;
  border-top: 1px solid var(--border);
  background: var(--surface-alt);
}

.connect-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  font-weight: 500;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--secondary);
  transition: background-color 0.2s;
}

.status-dot.idle { background: var(--secondary); }
.status-dot.connecting { background: var(--warning); animation: pulse 2s infinite; }
.status-dot.connected { background: var(--success); }
.status-dot.error { background: var(--danger); }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.controls-section {
  background: var(--surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 24px;
}

.control-group {
  margin-bottom: 24px;
}

.control-group:last-child {
  margin-bottom: 0;
}

.control-group h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: var(--text);
}

.led-controls {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.pin-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pin-input label {
  font-weight: 500;
  color: var(--text);
  white-space: nowrap;
}

.button-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

button {
  padding: 10px 16px;
  border: none;
  border-radius: var(--radius);
  font-weight: 500;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 40px;
  flex: 1;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}

.btn-success {
  background: var(--success);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: var(--success-hover);
  transform: translateY(-1px);
}

.btn-danger {
  background: var(--danger);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: var(--danger-hover);
  transform: translateY(-1px);
}

.btn-secondary {
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--surface-alt);
  transform: translateY(-1px);
}

input[type="number"] {
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 0.9rem;
  background: var(--surface);
  color: var(--text);
  width: 80px;
  text-align: center;
}

input[type="number"]:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgb(37 99 235 / 0.1);
}

.log-container {
  background: #0f172a;
  border-radius: var(--radius);
  padding: 16px;
  height: 200px;
  overflow-y: auto;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
  font-size: 0.85rem;
  line-height: 1.4;
  color: #e2e8f0;
  border: 1px solid var(--border);
}

.log-container::-webkit-scrollbar {
  width: 6px;
}

.log-container::-webkit-scrollbar-track {
  background: transparent;
}

.log-container::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 3px;
}

.demo-mode {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border: 1px solid #f59e0b;
  border-radius: var(--radius);
  padding: 12px;
  margin-bottom: 16px;
  font-size: 0.9rem;
  color: #92400e;
}

.demo-mode strong {
  color: #78350f;
}

.motor-controls {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.speed-control label {
  font-weight: 500;
  color: var(--text);
  white-space: nowrap;
}

.speed-slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: var(--border);
  outline: none;
  -webkit-appearance: none;
}

.speed-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  border: 2px solid var(--surface);
  box-shadow: var(--shadow);
}

.speed-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  border: 2px solid var(--surface);
  box-shadow: var(--shadow);
}

#speed-value {
  font-weight: 600;
  color: var(--primary);
  min-width: 40px;
  text-align: center;
}

.movement-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
  align-items: center;
}

.motor-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
}

.motor-btn {
  min-height: 48px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  flex-direction: column;
}

.motor-btn svg {
  margin-bottom: 2px;
}

.motor-advanced {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.motor-btn-small {
  min-height: 36px;
  font-size: 0.8rem;
  padding: 6px 12px;
}

/* Button active/pressed states */
.motor-btn.active {
  background: var(--primary-hover);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
  transform: translateY(1px);
}

.motor-btn.active.btn-danger {
  background: var(--danger-hover);
}

.motor-btn-small.active {
  background: var(--secondary);
  color: var(--text);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
  transform: translateY(1px);
}

/* Prevent layout shift on button press */
button {
  transform: translateY(0);
  transition: all 0.15s ease;
}

button:active {
  transform: translateY(1px);
}

/* Fix touch behavior on mobile */
button:focus {
  outline: none;
}

button:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

@media (max-width: 767px) {
  body {
    padding: 8px;
    margin: 0;
    min-width: 320px;
  }
  
  .container {
    max-width: 100%;
    width: 100%;
    margin: 0;
    padding: 0;
  }
  
  .header {
    margin-bottom: 20px;
    padding: 0 8px;
  }
  
  .header h1 {
    font-size: 1.5rem;
    margin-bottom: 4px;
  }
  
  .header p {
    font-size: 1rem;
  }
  
  .main-grid {
    gap: 16px;
    grid-template-columns: 1fr;
    width: 100%;
    max-width: 100%;
  }
  
  .video-section {
    margin: 0;
    width: 100%;
    max-width: 100%;
    overflow: hidden;
  }
  
  .video-container {
    width: 100%;
    max-width: 100%;
  }
  
  .video-controls {
    padding: 16px;
  }
  
  .controls-section {
    padding: 16px;
    margin: 0;
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
  }
  
  .control-group {
    margin-bottom: 20px;
  }
  
  .control-group h3 {
    font-size: 1rem;
    margin-bottom: 10px;
  }
  
  .button-group {
    flex-direction: column;
    gap: 8px;
  }
  
  button {
    flex: none;
    width: 100%;
    min-height: 44px;
    font-size: 0.9rem;
  }
  
  .connect-section {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .pin-input {
    flex-direction: column;
    align-items: stretch;
    gap: 6px;
  }
  
  .pin-input label {
    text-align: left;
  }
  
  input[type="number"] {
    width: 100%;
    max-width: 100px;
    text-align: center;
  }
  
  /* Motor control mobile adjustments */
  .motor-controls {
    gap: 12px;
  }
  
  .speed-control {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
  
  .speed-control label {
    text-align: left;
  }
  
  .speed-slider {
    width: 100%;
  }
  
  #speed-value {
    text-align: center;
    font-size: 1.1rem;
  }
  
  .movement-grid {
    gap: 6px;
  }
  
  .motor-row {
    gap: 6px;
  }
  
  .motor-btn {
    min-height: 52px;
    font-size: 0.8rem;
    padding: 8px 4px;
  }
  
  .motor-btn svg {
    width: 18px;
    height: 18px;
  }
  
  .motor-advanced {
    gap: 6px;
  }
  
  .motor-btn-small {
    min-height: 44px;
    font-size: 0.75rem;
    padding: 8px 6px;
  }
  
  .motor-btn-small svg {
    width: 16px;
    height: 16px;
  }
  
  .log-container {
    height: 150px;
    font-size: 0.8rem;
    padding: 12px;
  }
  
  /* Fix any potential overflow issues */
  * {
    max-width: 100%;
  }
  
  /* Prevent button transforms from breaking layout on mobile */
  .motor-btn, .motor-btn-small {
    transform: none !important;
  }
  
  .motor-btn:active, .motor-btn-small:active {
    transform: none !important;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2);
  }
  
  .motor-btn.active, .motor-btn-small.active {
    transform: none !important;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2);
  }
  
  .demo-mode {
    padding: 10px;
    font-size: 0.85rem;
    margin-bottom: 12px;
  }
}

/* Extra small mobile devices */
@media (max-width: 480px) {
  body {
    padding: 4px;
  }
  
  .header {
    padding: 0 4px;
  }
  
  .header h1 {
    font-size: 1.4rem;
  }
  
  .video-controls {
    padding: 12px;
  }
  
  .controls-section {
    padding: 12px;
  }
  
  .control-group {
    margin-bottom: 16px;
  }
  
  .motor-btn {
    min-height: 48px;
    font-size: 0.75rem;
    padding: 6px 2px;
  }
  
  .motor-btn svg {
    width: 16px;
    height: 16px;
  }
  
  .motor-btn-small {
    min-height: 40px;
    font-size: 0.7rem;
    padding: 6px 4px;
  }
  
  .motor-btn-small svg {
    width: 14px;
    height: 14px;
  }
  
  .log-container {
    height: 120px;
    font-size: 0.75rem;
    padding: 10px;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  :root {
    --background: #0f172a;
    --surface: #1e293b;
    --surface-alt: #334155;
    --text: #f1f5f9;
    --text-secondary: #94a3b8;
    --border: #475569;
  }
}
</style>
</head>
<body>
<div class="container">
  <header class="header">
    <h1>Harbor Camera Stream</h1>
    <p>WebRTC live streaming with GPIO control</p>
  </header>

  <div class="main-grid">
    <section class="video-section">
      <div class="video-container">
        <video id="v" autoplay playsinline muted></video>
        <div id="video-placeholder" class="video-placeholder">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M4 6.75A2.75 2.75 0 016.75 4h10.5A2.75 2.75 0 0120 6.75v10.5A2.75 2.75 0 0117.25 20H6.75A2.75 2.75 0 014 17.25V6.75zM6.75 5.5c-.69 0-1.25.56-1.25 1.25v10.5c0 .69.56 1.25 1.25 1.25h10.5c.69 0 1.25-.56 1.25-1.25V6.75c0-.69-.56-1.25-1.25-1.25H6.75z"/>
            <path d="M9.5 8.5a1 1 0 100 2 1 1 0 000-2zM8 8.5a2.5 2.5 0 115 0 2.5 2.5 0 01-5 0zM14 16l-2.5-3.125L9 16h5z"/>
          </svg>
          <div>Click Connect to start streaming</div>
        </div>
      </div>
      <div class="video-controls">
        <div id="demo-notice" class="demo-mode" style="display: none;">
          <strong>Demo Mode:</strong> Camera not available. Using placeholder video stream.
        </div>
        <div class="connect-section">
          <button id="connect" class="btn-primary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L2 7v10c0 5.55 3.84 9.95 9 11 5.16-1.05 9-5.45 9-11V7l-10-5z"/>
            </svg>
            Connect
          </button>
          <div class="status-indicator">
            <div id="status-dot" class="status-dot idle"></div>
            <span id="status-text">Idle</span>
          </div>
        </div>
      </div>
    </section>

    <aside class="controls-section">
      <div class="control-group">
        <h3>LED Control</h3>
        <div class="led-controls">
          <div class="pin-input">
            <label for="pin">GPIO Pin:</label>
            <input id="pin" type="number" value="17" min="1" max="40">
          </div>
          <div class="button-group">
            <button id="on" class="btn-success">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
              LED ON
            </button>
            <button id="off" class="btn-danger">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
              LED OFF
            </button>
          </div>
    </div>
  </div>

      <div class="control-group">
        <h3>Motor Control</h3>
        <div class="motor-controls">
          <div class="speed-control">
            <label for="motor-speed">Speed:</label>
            <input id="motor-speed" type="range" min="0" max="100" value="70" class="speed-slider">
            <span id="speed-value">70%</span>
          </div>
          <div class="movement-grid">
            <button id="motor-forward" class="btn-primary motor-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M7.41 15.41L12 10.83l4.59 4.58L18 14l-6-6-6 6z"/>
              </svg>
              Forward
            </button>
            <div class="motor-row">
              <button id="motor-left" class="btn-primary motor-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M15.41 16.09l-4.58-4.59 4.58-4.59L14 5.5l-6 6 6 6z"/>
                </svg>
                Left
              </button>
              <button id="motor-stop" class="btn-danger motor-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 6h12v12H6z"/>
                </svg>
                Stop
              </button>
              <button id="motor-right" class="btn-primary motor-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8.59 16.34l4.58-4.59-4.58-4.59L10 5.75l6 6-6 6z"/>
                </svg>
                Right
              </button>
            </div>
            <button id="motor-backward" class="btn-primary motor-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M7.41 8.84L12 13.42l4.59-4.58L18 10l-6 6-6-6z"/>
              </svg>
              Backward
            </button>
          </div>
          <div class="motor-advanced">
            <button id="motor-spin-left" class="btn-secondary motor-btn-small">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 6v3l4-4-4-4v3c-4.42 0-8 3.58-8 8 0 1.57.46 3.03 1.24 4.26L6.7 14.8c-.45-.83-.7-1.79-.7-2.8 0-3.31 2.69-6 6-6z"/>
              </svg>
              Spin Left
            </button>
            <button id="motor-spin-right" class="btn-secondary motor-btn-small">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8v-3l-4 4 4 4V6z"/>
              </svg>
              Spin Right
            </button>
          </div>
        </div>
      </div>

      <div class="control-group">
        <h3>Network Test</h3>
        <button id="ping" class="btn-secondary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          Ping Server
        </button>
    </div>

      <div class="control-group">
        <h3>Connection Log</h3>
        <div id="log" class="log-container"></div>
    </div>
    </aside>
  </div>
</div>
<script>
// DOM elements
const logEl = document.getElementById('log');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const connectBtn = document.getElementById('connect');
const videoEl = document.getElementById('v');
const videoPlaceholder = document.getElementById('video-placeholder');
const demoNotice = document.getElementById('demo-notice');
const pinInput = document.getElementById('pin');
const onBtn = document.getElementById('on');
const offBtn = document.getElementById('off');
const pingBtn = document.getElementById('ping');

// Motor control elements
const motorSpeedSlider = document.getElementById('motor-speed');
const speedValue = document.getElementById('speed-value');
const motorForward = document.getElementById('motor-forward');
const motorBackward = document.getElementById('motor-backward');
const motorLeft = document.getElementById('motor-left');
const motorRight = document.getElementById('motor-right');
const motorStop = document.getElementById('motor-stop');
const motorSpinLeft = document.getElementById('motor-spin-left');
const motorSpinRight = document.getElementById('motor-spin-right');

// State
let pc = null;
let ws = null;
let isConnecting = false;
let isDemoMode = false;
let currentMotorState = 'stop';  // Track current motor state
let motorTimeout = null;  // For auto-clearing active states

// Utility functions
function log(...args) {
  const timestamp = new Date().toLocaleTimeString();
  logEl.textContent += `[${timestamp}] ${args.join(' ')}\\n`;
  logEl.scrollTop = logEl.scrollHeight;
}

function updateStatus(status, text) {
  statusDot.className = `status-dot ${status}`;
  statusText.textContent = text;
}

function updateUI(connecting) {
  isConnecting = connecting;
  connectBtn.disabled = connecting;
  connectBtn.innerHTML = connecting 
    ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>Connecting...'
    : '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L2 7v10c0 5.55 3.84 9.95 9 11 5.16-1.05 9-5.45 9-11V7l-10-5z"/></svg>Connect';
  
  // Enable/disable controls based on connection
  const controlsDisabled = !ws || ws.readyState !== WebSocket.OPEN;
  onBtn.disabled = controlsDisabled;
  offBtn.disabled = controlsDisabled;
  pingBtn.disabled = controlsDisabled;
  
  // Enable/disable motor controls
  motorForward.disabled = controlsDisabled;
  motorBackward.disabled = controlsDisabled;
  motorLeft.disabled = controlsDisabled;
  motorRight.disabled = controlsDisabled;
  motorStop.disabled = controlsDisabled;
  motorSpinLeft.disabled = controlsDisabled;
  motorSpinRight.disabled = controlsDisabled;
  motorSpeedSlider.disabled = controlsDisabled;
}

// Demo mode fallback
function createDemoStream() {
  const canvas = document.createElement('canvas');
  canvas.width = 640;
  canvas.height = 480;
  const ctx = canvas.getContext('2d');
  
  // Create animated demo pattern
  let frame = 0;
  function drawFrame() {
    // Gradient background
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, '#1e293b');
    gradient.addColorStop(1, '#334155');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Animated circles
    ctx.fillStyle = 'rgba(59, 130, 246, 0.6)';
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 50 + Math.sin(frame * 0.05) * 20;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.fill();
    
    // Demo text
    ctx.fillStyle = '#e2e8f0';
    ctx.font = 'bold 24px system-ui';
    ctx.textAlign = 'center';
    ctx.fillText('DEMO MODE', centerX, centerY - 30);
    ctx.font = '16px system-ui';
    ctx.fillText('Camera simulation active', centerX, centerY + 10);
    
    frame++;
  }
  
  // Update at 30fps
  setInterval(drawFrame, 1000/30);
  drawFrame(); // Initial frame
  
  return canvas.captureStream(30);
}

// Main connection function
async function start() {
  if (pc || isConnecting) return;
  
  updateStatus('connecting', 'Connecting...');
  updateUI(true);
  log('Starting connection...');

  try {
  pc = new RTCPeerConnection({iceServers: []});
    
    pc.oniceconnectionstatechange = () => {
      log('WebRTC state:', pc.iceConnectionState);
      if (pc.iceConnectionState === 'connected') {
        updateStatus('connected', 'Connected');
        videoPlaceholder.classList.add('hidden');
      } else if (pc.iceConnectionState === 'failed' || pc.iceConnectionState === 'closed') {
        updateStatus('error', 'Connection failed');
        cleanup();
      }
    };
    
    pc.ontrack = (ev) => {
      log('Received video stream');
      videoEl.srcObject = ev.streams[0];
      videoPlaceholder.classList.add('hidden');
    };

    // Request video stream
  pc.addTransceiver('video', {direction: 'recvonly'});

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

    // Try to connect to server
    const response = await fetch('/offer', {
    method: 'POST',
      headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({sdp: offer.sdp, type: offer.type})
  });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Server error ${response.status}: ${errorText}`);
    }

    const answer = await response.json();
    
    // Check if response contains an error
    if (answer.error) {
      throw new Error(answer.error);
    }
    
  await pc.setRemoteDescription(answer);

    // Setup WebSocket
    await setupWebSocket();
    
  } catch (error) {
    log('Connection failed:', error.message);
    log('Falling back to demo mode...');
    
    // Enable demo mode
    isDemoMode = true;
    demoNotice.style.display = 'block';
    
    // Create demo video stream
    const demoStream = createDemoStream();
    videoEl.srcObject = demoStream;
    videoPlaceholder.classList.add('hidden');
    
    // Setup WebSocket anyway (might work even if camera doesn't)
    try {
      await setupWebSocket();
    } catch (wsError) {
      log('WebSocket also failed:', wsError.message);
      updateStatus('error', 'Demo mode (offline)');
      updateUI(false);
      return;
    }
    
    updateStatus('connected', 'Demo mode');
  }
  
  updateUI(false);
}

async function setupWebSocket() {
  return new Promise((resolve, reject) => {
  const wsProto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(wsProto + '://' + location.host + '/ws');
    
    const timeout = setTimeout(() => {
      reject(new Error('WebSocket connection timeout'));
    }, 5000);
    
    ws.onopen = () => {
      clearTimeout(timeout);
      log('WebSocket connected');
      updateUI(false);
      resolve();
    };
    
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if (data.type === 'hello') {
          log('Server hello - GPIO enabled:', data.gpio, 'Motor enabled:', data.motor);
        } else if (data.type === 'pong') {
          const latency = Date.now() - data.data;
          log(`Pong received (${latency}ms latency)`);
        } else if (data.type === 'led') {
          log('LED response:', JSON.stringify(data.result));
        } else if (data.type === 'motor') {
          if (data.result && data.result.status === 'error') {
            log('Motor error:', data.result.message);
          } else {
            log('Motor response:', JSON.stringify(data.result));
          }
        } else if (data.type === 'error') {
          log('Server error:', data.message);
        } else {
          log('Server message:', ev.data);
        }
      } catch (e) {
        log('Raw message:', ev.data);
      }
    };
    
    ws.onerror = (e) => {
      clearTimeout(timeout);
      log('WebSocket error:', e.message || 'Connection failed');
      reject(e);
    };
    
    ws.onclose = () => {
      log('WebSocket closed');
      updateStatus('error', 'Disconnected');
      updateUI(false);
      cleanup();
    };
  });
}

function cleanup() {
  if (pc) {
    pc.close();
    pc = null;
  }
  if (ws) {
    ws.close();
    ws = null;
  }
  isDemoMode = false;
  demoNotice.style.display = 'none';
  videoPlaceholder.classList.remove('hidden');
  videoEl.srcObject = null;
  updateUI(false);
}

// Event listeners
connectBtn.addEventListener('click', start);

pingBtn.addEventListener('click', () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    const timestamp = Date.now();
    ws.send(JSON.stringify({cmd: 'ping', data: timestamp}));
    log('Ping sent...');
  } else {
    log('WebSocket not connected');
  }
});

onBtn.addEventListener('click', () => {
  const pin = parseInt(pinInput.value);
  if (isNaN(pin) || pin < 1 || pin > 40) {
    log('Invalid pin number. Use 1-40.');
    return;
  }
  
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({cmd: 'led', pin, state: 'on'}));
    log(`LED ON command sent for pin ${pin}`);
  } else {
    log('WebSocket not connected');
  }
});

offBtn.addEventListener('click', () => {
  const pin = parseInt(pinInput.value);
  if (isNaN(pin) || pin < 1 || pin > 40) {
    log('Invalid pin number. Use 1-40.');
    return;
  }
  
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({cmd: 'led', pin, state: 'off'}));
    log(`LED OFF command sent for pin ${pin}`);
  } else {
    log('WebSocket not connected');
  }
});

// Pin input validation
pinInput.addEventListener('input', () => {
  const value = parseInt(pinInput.value);
  if (isNaN(value) || value < 1 || value > 40) {
    pinInput.style.borderColor = '#dc2626';
  } else {
    pinInput.style.borderColor = '';
  }
});

// Motor control functions
function sendMotorCommand(movement, speed = null) {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    log('WebSocket not connected - cannot send motor command');
    return;
  }
  
  try {
    const speedValue = speed !== null ? speed : parseInt(motorSpeedSlider.value) / 100;
    const command = {
      cmd: 'motor',
      action: 'move',
      movement: movement,
      speed: speedValue
    };
    
    ws.send(JSON.stringify(command));
    log(`Motor command: ${movement} at ${(speedValue * 100).toFixed(0)}%`);
    
    // Update button states
    updateMotorButtonStates(movement);
    
  } catch (error) {
    log(`Error sending motor command: ${error.message}`);
  }
}

// Update motor button active states
function updateMotorButtonStates(activeMovement) {
  // Clear all active states first
  const motorButtons = [motorForward, motorBackward, motorLeft, motorRight, motorStop, motorSpinLeft, motorSpinRight];
  motorButtons.forEach(btn => {
    if (btn) btn.classList.remove('active');
  });
  
  // Clear any existing timeout
  if (motorTimeout) {
    clearTimeout(motorTimeout);
    motorTimeout = null;
  }
  
  // Set active state for current movement
  currentMotorState = activeMovement;
  let activeButton = null;
  
  switch (activeMovement) {
    case 'forward':
      activeButton = motorForward;
      break;
    case 'backward':
      activeButton = motorBackward;
      break;
    case 'left':
      activeButton = motorLeft;
      break;
    case 'right':
      activeButton = motorRight;
      break;
    case 'stop':
      activeButton = motorStop;
      break;
    case 'spin_left':
      activeButton = motorSpinLeft;
      break;
    case 'spin_right':
      activeButton = motorSpinRight;
      break;
  }
  
  if (activeButton) {
    activeButton.classList.add('active');
    
    // Auto-clear active state after movement (except for stop)
    if (activeMovement !== 'stop') {
      motorTimeout = setTimeout(() => {
        activeButton.classList.remove('active');
        currentMotorState = 'stop';
        motorStop.classList.add('active');
      }, 2000); // Clear after 2 seconds
    }
  }
}

// Function to prevent button layout shift on mobile
function preventLayoutShift(event) {
  event.preventDefault();
  event.target.blur(); // Remove focus to prevent keyboard popup
  return false;
}

// Speed slider update
motorSpeedSlider.addEventListener('input', () => {
  const value = motorSpeedSlider.value;
  speedValue.textContent = value + '%';
});

// Motor control event listeners with layout shift prevention
motorForward.addEventListener('click', (e) => {
  preventLayoutShift(e);
  sendMotorCommand('forward');
});

motorBackward.addEventListener('click', (e) => {
  preventLayoutShift(e);
  sendMotorCommand('backward');
});

motorLeft.addEventListener('click', (e) => {
  preventLayoutShift(e);
  sendMotorCommand('left');
});

motorRight.addEventListener('click', (e) => {
  preventLayoutShift(e);
  sendMotorCommand('right');
});

motorStop.addEventListener('click', (e) => {
  preventLayoutShift(e);
  sendMotorCommand('stop', 0);
});

motorSpinLeft.addEventListener('click', (e) => {
  preventLayoutShift(e);
  sendMotorCommand('spin_left');
});

motorSpinRight.addEventListener('click', (e) => {
  preventLayoutShift(e);
  sendMotorCommand('spin_right');
});

// Add touch event listeners to prevent layout issues on mobile
const allMotorButtons = [motorForward, motorBackward, motorLeft, motorRight, motorStop, motorSpinLeft, motorSpinRight];
allMotorButtons.forEach(button => {
  if (button) {
    // Prevent default touch behavior that might cause layout shifts
    button.addEventListener('touchstart', (e) => {
      e.preventDefault();
    }, { passive: false });
    
    button.addEventListener('touchend', (e) => {
      e.preventDefault();
    }, { passive: false });
    
    // Prevent context menu on long press
    button.addEventListener('contextmenu', (e) => {
      e.preventDefault();
    });
  }
});

// Initialize UI
updateStatus('idle', 'Idle');
updateUI(false);
updateMotorButtonStates('stop'); // Initialize with stop state active
log('Harbor client initialized');
log('Click Connect to start streaming');

// Cleanup on page unload
window.addEventListener('beforeunload', cleanup);
</script>
"""


async def index_handler(_request: web.Request):
    """Serve the HTML client interface.
    
    Returns:
        web.Response: HTML response with embedded client
    """
    return web.Response(text=CLIENT_HTML, content_type="text/html")
