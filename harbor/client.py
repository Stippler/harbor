#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from aiohttp import web


# HTML client interface
CLIENT_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
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

.video-settings {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: var(--surface);
  border-radius: var(--radius);
  border: 1px solid var(--border);
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.setting-group label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text);
}

.setting-select {
  padding: 6px 8px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--text);
  font-size: 0.85rem;
  cursor: pointer;
  touch-action: manipulation;
  min-height: 40px;
}

.setting-select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgb(37 99 235 / 0.1);
}

.connect-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.connect-section button {
  flex-shrink: 0;
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
  touch-action: manipulation;
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

.boats-container {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px;
  min-height: 100px;
  background: var(--surface-alt);
}

.boat-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
  margin-bottom: 8px;
  background: var(--surface);
  border-radius: var(--radius);
  border: 1px solid var(--border);
}

.boat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.boat-name {
  font-weight: 600;
  color: var(--text);
}

.boat-details {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.boat-status {
  color: var(--text-secondary);
  font-style: italic;
  text-align: center;
  padding: 20px;
}

.boat-connect-btn {
  padding: 6px 12px;
  font-size: 0.8rem;
  min-height: 32px;
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
  touch-action: manipulation;
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

/* Fix touch behavior on mobile */
button {
  -webkit-tap-highlight-color: rgba(37, 99, 235, 0.2);
  touch-action: manipulation;
  user-select: none;
  -webkit-user-select: none;
  transform: translateY(0);
  transition: all 0.15s ease;
}

button:focus {
  outline: none;
}

button:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

button:active {
  transform: translateY(1px);
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
  
  .video-settings {
    grid-template-columns: 1fr;
    gap: 8px;
    padding: 10px;
    margin-bottom: 12px;
  }
  
  .setting-select {
    padding: 8px;
    font-size: 0.9rem;
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
    min-height: 48px;
    min-width: 48px;
    font-size: 0.9rem;
    touch-action: manipulation;
    -webkit-tap-highlight-color: rgba(37, 99, 235, 0.2);
    cursor: pointer;
    pointer-events: auto;
    -webkit-user-select: none;
    user-select: none;
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
    -webkit-tap-highlight-color: rgba(37, 99, 235, 0.3);
    touch-action: manipulation;
    cursor: pointer;
  }
  
  .motor-btn:active, .motor-btn-small:active {
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2);
    background-color: var(--primary-hover);
  }
  
  .motor-btn.active, .motor-btn-small.active {
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2);
  }
  
  /* Ensure buttons are properly sized for touch */
  .motor-btn {
    min-height: 48px !important;
    min-width: 48px;
  }
  
  .motor-btn-small {
    min-height: 44px !important;
    min-width: 44px;
  }
  
  .demo-mode {
    padding: 10px;
    font-size: 0.85rem;
    margin-bottom: 12px;
  }
}

/* Small mobile devices (375px and below) */
@media (max-width: 375px) {
  body {
    padding: 2px;
    font-size: 14px;
  }
  
  .container {
    padding: 0;
    margin: 0;
  }
  
  .header {
    padding: 0 4px;
    margin-bottom: 12px;
  }
  
  .header h1 {
    font-size: 1.3rem;
    margin-bottom: 2px;
  }
  
  .header p {
    font-size: 0.9rem;
  }
  
  .main-grid {
    gap: 12px;
  }
  
  .video-controls {
    padding: 10px;
  }
  
  .video-settings {
    grid-template-columns: 1fr;
    gap: 6px;
    padding: 8px;
    margin-bottom: 10px;
  }
  
  .setting-select {
    padding: 6px;
    font-size: 0.8rem;
    min-height: 36px;
  }
  
  .connect-section {
    gap: 6px;
  }
  
  button {
    min-height: 44px;
    font-size: 0.8rem;
    padding: 8px 12px;
  }
  
  .controls-section {
    padding: 10px;
  }
  
  .control-group {
    margin-bottom: 14px;
  }
  
  .control-group h3 {
    font-size: 0.95rem;
    margin-bottom: 8px;
  }
  
  /* Motor controls for 375px */
  .speed-control {
    gap: 6px;
  }
  
  #speed-value {
    font-size: 1rem;
    min-width: 35px;
  }
  
  .movement-grid {
    gap: 4px;
  }
  
  .motor-row {
    gap: 4px;
  }
  
  .motor-btn {
    min-height: 44px !important;
    min-width: 44px;
    font-size: 0.7rem;
    padding: 4px 2px;
  }
  
  .motor-btn svg {
    width: 14px;
    height: 14px;
    margin-bottom: 1px;
  }
  
  .motor-advanced {
    gap: 4px;
  }
  
  .motor-btn-small {
    min-height: 38px !important;
    min-width: 38px;
    font-size: 0.65rem;
    padding: 4px 2px;
  }
  
  .motor-btn-small svg {
    width: 12px;
    height: 12px;
  }
  
  .log-container {
    height: 100px;
    font-size: 0.7rem;
    padding: 8px;
    line-height: 1.3;
  }
  
  /* LED controls */
  .pin-input input {
    max-width: 80px;
    padding: 6px 8px;
  }
  
  /* Status indicator */
  .status-indicator {
    font-size: 0.8rem;
  }
  
  .status-dot {
    width: 6px;
    height: 6px;
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
    <h1>Harbor Relay Server</h1>
    <p>WebRTC boat camera streaming relay</p>
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
        <div id="boat-selection" class="video-settings">
          <div class="setting-group">
            <label for="boat-select">Select Boat:</label>
            <select id="boat-select" class="setting-select">
              <option value="" disabled selected>Loading boats...</option>
            </select>
          </div>
          <div class="setting-group">
            <button id="refresh-boats" class="btn-secondary">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
              Refresh
            </button>
          </div>
        </div>
        <div class="connect-section">
          <button id="connect" class="btn-primary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L2 7v10c0 5.55 3.84 9.95 9 11 5.16-1.05 9-5.45 9-11V7l-10-5z"/>
            </svg>
            Connect
          </button>
          <button id="disconnect" class="btn-secondary" style="display: none;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 11H7v-2h10v2z"/>
            </svg>
            Disconnect
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
        <h3>Available Boats</h3>
        <div id="boats-list" class="boats-container">
          <div class="boat-status">Loading boats...</div>
        </div>
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
const disconnectBtn = document.getElementById('disconnect');
const videoEl = document.getElementById('v');
const videoPlaceholder = document.getElementById('video-placeholder');
const boatSelect = document.getElementById('boat-select');
const refreshBoatsBtn = document.getElementById('refresh-boats');
const boatsListEl = document.getElementById('boats-list');

// State
let pc = null;
let ws = null;
let isConnecting = false;
let availableBoats = [];
let selectedBoatId = null;

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
  const isConnected = pc && (pc.iceConnectionState === 'connected' || pc.connectionState === 'connected');
  
  // Update connect button
  connectBtn.disabled = connecting || isConnected || !selectedBoatId;
  connectBtn.innerHTML = connecting 
    ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>Connecting...'
    : '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L2 7v10c0 5.55 3.84 9.95 9 11 5.16-1.05 9-5.45 9-11V7l-10-5z"/></svg>Connect';
  
  // Show/hide disconnect button
  if (isConnected || connecting) {
    connectBtn.style.display = 'none';
    disconnectBtn.style.display = 'inline-flex';
  } else {
    connectBtn.style.display = 'inline-flex';
    disconnectBtn.style.display = 'none';
  }
  
  // Enable/disable boat selection
  boatSelect.disabled = connecting || isConnected;
  refreshBoatsBtn.disabled = connecting || isConnected;
}

// Boat management functions
async function loadBoats() {
  try {
    const response = await fetch('/boats');
    if (!response.ok) {
      throw new Error(`Failed to load boats: ${response.status}`);
    }
    
    const data = await response.json();
    availableBoats = data.boats || [];
    updateBoatsList();
    updateBoatSelect();
    log(`Loaded ${availableBoats.length} boats`);
    
  } catch (error) {
    log('Failed to load boats:', error.message);
    boatsListEl.innerHTML = '<div class="boat-status">Failed to load boats</div>';
  }
}

function updateBoatsList() {
  if (availableBoats.length === 0) {
    boatsListEl.innerHTML = '<div class="boat-status">No boats available</div>';
    return;
  }
  
  boatsListEl.innerHTML = availableBoats.map(boat => `
    <div class="boat-item">
      <div class="boat-info">
        <div class="boat-name">${boat.boat_id}</div>
        <div class="boat-details">
          ${boat.capabilities.width}x${boat.capabilities.height} @ ${boat.capabilities.fps}fps
          ${boat.connected ? '✓ Connected' : '✗ Offline'}
        </div>
      </div>
      <button class="btn-primary boat-connect-btn" 
              onclick="selectBoat('${boat.boat_id}')"
              ${!boat.connected ? 'disabled' : ''}>
        Select
      </button>
    </div>
  `).join('');
}

function updateBoatSelect() {
  const currentValue = boatSelect.value;
  boatSelect.innerHTML = '<option value="" disabled>Select a boat...</option>';
  
  availableBoats.forEach(boat => {
    if (boat.connected) {
      const option = document.createElement('option');
      option.value = boat.boat_id;
      option.textContent = `${boat.boat_id} (${boat.capabilities.width}x${boat.capabilities.height})`;
      boatSelect.appendChild(option);
    }
  });
  
  // Restore selection if still available
  if (currentValue && availableBoats.find(b => b.boat_id === currentValue && b.connected)) {
    boatSelect.value = currentValue;
    selectedBoatId = currentValue;
  } else {
    selectedBoatId = null;
  }
  
  updateUI(false);
}

function selectBoat(boatId) {
  selectedBoatId = boatId;
  boatSelect.value = boatId;
  updateUI(false);
  log(`Selected boat: ${boatId}`);
}

// Main connection function
async function start() {
  if (pc || isConnecting) {
    log('Connection already exists or in progress');
    return;
  }
  
  if (!selectedBoatId) {
    log('No boat selected');
    return;
  }
  
  updateStatus('connecting', 'Connecting...');
  updateUI(true);
  log(`Starting connection to boat ${selectedBoatId}...`);

  try {
    pc = new RTCPeerConnection({iceServers: []});
    
    pc.oniceconnectionstatechange = () => {
      log('WebRTC ICE state:', pc.iceConnectionState);
      if (pc.iceConnectionState === 'connected' || pc.iceConnectionState === 'completed') {
        updateStatus('connected', 'Connected');
        videoPlaceholder.classList.add('hidden');
        updateUI(false);
      } else if (pc.iceConnectionState === 'failed' || pc.iceConnectionState === 'closed') {
        updateStatus('error', 'Connection failed');
        cleanup();
      } else if (pc.iceConnectionState === 'disconnected') {
        updateStatus('error', 'Disconnected');
        cleanup();
      }
    };
    
    pc.onconnectionstatechange = () => {
      log('WebRTC connection state:', pc.connectionState);
      if (pc.connectionState === 'connected') {
        updateStatus('connected', 'Connected');
        updateUI(false);
      } else if (pc.connectionState === 'failed' || pc.connectionState === 'closed') {
        updateStatus('error', 'Connection failed');
        cleanup();
      }
    };
    
    pc.ontrack = (ev) => {
      log('Received video stream from boat');
      videoEl.srcObject = ev.streams[0];
      videoPlaceholder.classList.add('hidden');
    };

    // Request video stream
    pc.addTransceiver('video', {direction: 'recvonly'});

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    // Send offer to relay server with boat ID
    const response = await fetch('/offer', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        sdp: offer.sdp, 
        type: offer.type,
        boat_id: selectedBoatId
      })
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
    log(`Connected to boat ${selectedBoatId} via relay`);
    
  } catch (error) {
    log('Connection failed:', error.message);
    updateStatus('error', 'Connection failed');
    cleanup();
  }
  
  updateUI(false);
}

// Cleanup function
function cleanup() {
  // Close WebRTC peer connection
  if (pc) {
    // Stop all tracks
    if (pc.getSenders) {
      pc.getSenders().forEach(sender => {
        if (sender.track) {
          sender.track.stop();
        }
      });
    }
    if (pc.getReceivers) {
      pc.getReceivers().forEach(receiver => {
        if (receiver.track) {
          receiver.track.stop();
        }
      });
    }
    pc.close();
    pc = null;
  }
  
  // Stop video stream
  if (videoEl.srcObject) {
    const stream = videoEl.srcObject;
    if (stream.getTracks) {
      stream.getTracks().forEach(track => track.stop());
    }
    videoEl.srcObject = null;
  }
  
  // Reset state
  isConnecting = false;
  videoPlaceholder.classList.remove('hidden');
  updateUI(false);
}

// Disconnect function
function disconnect() {
  log('Disconnecting...');
  updateStatus('disconnecting', 'Disconnecting...');
  cleanup();
  updateStatus('idle', 'Idle');
  log('Disconnected');
}

// Event listeners
connectBtn.addEventListener('click', start);
disconnectBtn.addEventListener('click', disconnect);

refreshBoatsBtn.addEventListener('click', loadBoats);

boatSelect.addEventListener('change', (e) => {
  selectedBoatId = e.target.value;
  updateUI(false);
  log(`Selected boat: ${selectedBoatId}`);
});

// Initialize UI
updateStatus('idle', 'Idle');
updateUI(false);
log('Harbor relay client initialized');
log('Loading available boats...');

// Load boats on startup
loadBoats();

// Refresh boats every 30 seconds
setInterval(loadBoats, 30000);

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
