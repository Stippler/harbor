#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from aiohttp import web


# HTML client interface with WebSocket-based WebRTC signaling
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
  margin: 0;
  padding: 0;
  background: var(--background);
  color: var(--text);
  line-height: 1.6;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: var(--surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}

.header h1 {
  margin: 0 0 10px 0;
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary);
}

.header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.main-grid {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 30px;
  align-items: start;
}

@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

.video-section {
  background: var(--surface);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow);
}

.video-container {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  background: #000;
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: 20px;
}

video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 1.1rem;
  text-align: center;
}

.video-placeholder.hidden {
  display: none;
}

.video-placeholder svg {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.8;
}

.video-controls {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.video-settings {
  display: flex;
  gap: 15px;
  align-items: end;
}

@media (max-width: 640px) {
  .video-settings {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
}

.setting-group {
  flex: 1;
}

.setting-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: var(--text);
}

.setting-select {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--text);
  font-size: 14px;
  transition: border-color 0.2s;
}

.setting-select:focus {
  outline: none;
  border-color: var(--primary);
}

.connect-section {
  display: flex;
  gap: 15px;
  align-items: center;
}

@media (max-width: 640px) {
  .connect-section {
    flex-direction: column;
    gap: 10px;
  }
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-secondary {
  background: var(--secondary);
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #4b5563;
}

.btn-success {
  background: var(--success);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: var(--success-hover);
}

.btn-danger {
  background: var(--danger);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: var(--danger-hover);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  transition: background-color 0.3s;
}

.status-dot.idle {
  background: var(--secondary);
}

.status-dot.connecting {
  background: var(--warning);
  animation: pulse 2s infinite;
}

.status-dot.connected {
  background: var(--success);
}

.status-dot.error {
  background: var(--danger);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.controls-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.control-group {
  background: var(--surface);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow);
}

.control-group h3 {
  margin: 0 0 15px 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text);
}

.boats-container {
  max-height: 300px;
  overflow-y: auto;
}

.boat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background: var(--surface-alt);
  border-radius: var(--radius);
  border: 1px solid var(--border);
}

.boat-item:last-child {
  margin-bottom: 0;
}

.boat-info {
  flex: 1;
}

.boat-name {
  font-weight: 600;
  color: var(--text);
  margin-bottom: 4px;
}

.boat-details {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.boat-status {
  padding: 20px;
  text-align: center;
  color: var(--text-secondary);
  font-style: italic;
}

.log-container {
  background: #1a1a1a;
  color: #e5e5e5;
  padding: 15px;
  border-radius: var(--radius);
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.4;
  height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.log-container::-webkit-scrollbar {
  width: 8px;
}

.log-container::-webkit-scrollbar-track {
  background: #2a2a2a;
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb {
  background: #4a4a4a;
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb:hover {
  background: #5a5a5a;
}

/* Control buttons */
.control-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
  margin-top: 15px;
}

.control-buttons .btn {
  justify-content: center;
  padding: 8px 12px;
  font-size: 13px;
}
</style>
</head>
<body>
<div class="container">
  <header class="header">
    <h1>Harbor Relay Server</h1>
    <p>WebRTC boat camera streaming relay with WebSocket control</p>
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
          <div>Select a boat and click Connect</div>
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
            <button id="refresh-boats" class="btn btn-secondary">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M4 12a8 8 0 018-8V2.5L14.5 5 12 7.5V6a6 6 0 100 12 6 6 0 006-6h2a8 8 0 01-16 0z"/>
              </svg>
              Refresh
            </button>
          </div>
        </div>
        <div class="connect-section">
          <button id="connect" class="btn btn-primary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L2 7v10c0 5.55 3.84 9.95 9 11 5.16-1.05 9-5.45 9-11V7l-10-5z"/>
            </svg>
            Connect
          </button>
          <button id="disconnect" class="btn btn-danger" style="display: none;">
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
        <h3>Boat Controls</h3>
        <div class="control-buttons">
          <button class="btn btn-success" onclick="sendLEDControl('on')">LED On</button>
          <button class="btn btn-secondary" onclick="sendLEDControl('off')">LED Off</button>
          <button class="btn btn-warning" onclick="sendLEDControl('blink')">LED Blink</button>
          <button class="btn btn-primary" onclick="sendMotorControl('forward', 0.5, 2)">Forward</button>
          <button class="btn btn-primary" onclick="sendMotorControl('backward', 0.5, 2)">Backward</button>
          <button class="btn btn-primary" onclick="sendMotorControl('left', 0.5, 1)">Left</button>
          <button class="btn btn-primary" onclick="sendMotorControl('right', 0.5, 1)">Right</button>
          <button class="btn btn-danger" onclick="sendMotorControl('stop')">Stop</button>
          <button class="btn btn-secondary" onclick="sendBoatCommand('status')">Status</button>
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
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
let reconnectDelay = 2000;

// Utility functions
function log(...args) {
  const timestamp = new Date().toLocaleTimeString();
  logEl.textContent += `[${timestamp}] ${args.join(' ')}\n`;
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
  connectBtn.disabled = connecting || isConnected || !selectedBoatId || !ws || ws.readyState !== WebSocket.OPEN;
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

// WebSocket connection management
function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;
  
  log('🔌 Connecting to WebSocket:', wsUrl);
  ws = new WebSocket(wsUrl);
  
  ws.onopen = () => {
    log('✅ WebSocket connected to Harbor server');
    reconnectAttempts = 0;
    reconnectDelay = 2000;
    updateStatus('idle', 'WebSocket Connected');
    updateUI(false);
  };
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    } catch (error) {
      log('❌ Failed to parse WebSocket message:', error.message);
    }
  };
  
  ws.onclose = () => {
    log('❌ WebSocket disconnected');
    updateStatus('error', 'WebSocket Disconnected');
    scheduleReconnect();
  };
  
  ws.onerror = (error) => {
    log('❌ WebSocket error:', error);
  };
}

function scheduleReconnect() {
  if (reconnectAttempts < maxReconnectAttempts) {
    reconnectAttempts++;
    log(`🔄 Reconnecting WebSocket in ${reconnectDelay}ms (attempt ${reconnectAttempts})`);
    setTimeout(() => connectWebSocket(), reconnectDelay);
    reconnectDelay *= 1.5; // Exponential backoff
  } else {
    log('❌ Max reconnection attempts reached');
    updateStatus('error', 'Connection Failed');
  }
}

function sendWebSocketMessage(data) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(data));
    return true;
  } else {
    log('❌ WebSocket not connected, cannot send message');
    return false;
  }
}

// WebSocket message handling
function handleWebSocketMessage(data) {
  const msgType = data.type;
  
  if (msgType === 'boats_available') {
    availableBoats = data.boats || [];
    updateBoatsList();
    updateBoatSelect();
    log(`📋 Loaded ${availableBoats.length} boats`);
  } else if (msgType === 'webrtc_offer') {
    handleWebRTCOffer(data);
  } else if (msgType === 'stream_response') {
    handleStreamResponse(data);
  } else if (msgType === 'command_response') {
    handleCommandResponse(data);
  } else {
    log('❓ Unknown WebSocket message type:', msgType);
  }
}

async function handleWebRTCOffer(data) {
  if (!pc) {
    log('❌ Received WebRTC offer but no peer connection exists');
    return;
  }
  
  try {
    log('📨 Received WebRTC offer from boat', data.boat_id);
    
    const offer = new RTCSessionDescription({
      sdp: data.sdp,
      type: data.offer_type || 'offer'
    });
    
    await pc.setRemoteDescription(offer);
    log('✅ Set remote description from boat offer');
    log('🌐 BROWSER SIGNALING: Signaling state after offer:', pc.signalingState);
    log('🌐 BROWSER ICE: ICE connection state after offer:', pc.iceConnectionState);
    
    // Create answer
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    log('🌐 BROWSER ANSWER: Created answer - SDP length:', answer.sdp.length);
    log('🌐 BROWSER SIGNALING: Signaling state after answer:', pc.signalingState);
    log('🌐 BROWSER ICE: ICE gathering state after answer:', pc.iceGatheringState);
    
    // Send answer back to boat via server
    sendWebSocketMessage({
      type: 'webrtc_answer',
      boat_id: data.boat_id,
      sdp: answer.sdp,
      answer_type: answer.type
    });
    
    log('📤 Sent WebRTC answer to boat');
    
  } catch (error) {
    log('❌ Failed to handle WebRTC offer:', error.message);
    updateStatus('error', 'WebRTC Setup Failed');
    cleanup();
  }
}

function handleStreamResponse(data) {
  if (data.success) {
    log(`✅ Stream request successful for boat ${data.boat_id}`);
  } else {
    log(`❌ Stream request failed for boat ${data.boat_id}`);
    updateStatus('error', 'Stream request failed');
    cleanup();
  }
}

function handleCommandResponse(data) {
  if (data.success) {
    log(`✅ Command ${data.command_type} successful for boat ${data.boat_id}`);
  } else {
    log(`❌ Command ${data.command_type} failed for boat ${data.boat_id}: ${data.error}`);
  }
}

// Boat management functions
function loadBoats() {
  if (ws && ws.readyState === WebSocket.OPEN) {
    sendWebSocketMessage({ type: 'list_boats' });
  } else {
    log('❌ Cannot load boats - WebSocket not connected');
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
          ${boat.connected ? '✅ Connected' : '❌ Offline'}
        </div>
      </div>
      <button class="btn btn-primary boat-connect-btn" 
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
  log(`🎯 Selected boat: ${boatId}`);
}

// Main connection function
async function start() {
  if (pc || isConnecting) {
    log('❌ Connection already exists or in progress');
    return;
  }
  
  if (!selectedBoatId) {
    log('❌ No boat selected');
    return;
  }
  
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    log('❌ WebSocket not connected');
    return;
  }
  
  updateStatus('connecting', 'Connecting...');
  updateUI(true);
  log(`🚀 Starting connection to boat ${selectedBoatId}...`);

  try {
    // Create WebRTC peer connection without STUN servers (direct connection mode)
    const iceConfig = {
      iceServers: [],                    // No STUN servers
      iceTransportPolicy: 'all',         // Allow all ICE candidates
      iceCandidatePoolSize: 10           // Generate more candidates
    };
    log('🌐 BROWSER ICE: Initializing WITHOUT STUN servers (direct connection mode)');
    pc = new RTCPeerConnection(iceConfig);
    
    // Setup comprehensive WebRTC event handlers
    pc.oniceconnectionstatechange = () => {
      log('🌐 BROWSER ICE: ICE connection state changed:', pc.iceConnectionState);
      if (pc.iceConnectionState === 'connected' || pc.iceConnectionState === 'completed') {
        updateStatus('connected', 'Connected');
        videoPlaceholder.classList.add('hidden');
        updateUI(false);
        log('🌐 BROWSER ICE: ICE connection established successfully!');
      } else if (pc.iceConnectionState === 'failed') {
        log('❌ BROWSER ICE: ICE connection failed - check STUN servers and firewall');
        updateStatus('error', 'ICE Connection Failed');
        cleanup();
      } else if (pc.iceConnectionState === 'closed') {
        log('🌐 BROWSER ICE: ICE connection closed');
        updateStatus('error', 'Connection closed');
        cleanup();
      } else if (pc.iceConnectionState === 'disconnected') {
        log('⚠️ BROWSER ICE: ICE connection disconnected');
        updateStatus('error', 'Disconnected');
        cleanup();
      } else if (pc.iceConnectionState === 'checking') {
        log('🔍 BROWSER ICE: ICE connection checking - waiting for connectivity');
        updateStatus('connecting', 'Checking connectivity...');
      }
    };
    
    pc.onconnectionstatechange = () => {
      log('🌐 BROWSER CONNECTION: Connection state changed:', pc.connectionState);
      if (pc.connectionState === 'connected') {
        updateStatus('connected', 'Connected');
        updateUI(false);
        log('🌐 BROWSER CONNECTION: WebRTC connection fully established!');
      } else if (pc.connectionState === 'failed') {
        log('❌ BROWSER CONNECTION: WebRTC connection failed');
        updateStatus('error', 'Connection failed');
        cleanup();
      } else if (pc.connectionState === 'closed') {
        log('🌐 BROWSER CONNECTION: WebRTC connection closed');
        updateStatus('error', 'Connection closed');
        cleanup();
      } else if (pc.connectionState === 'connecting') {
        log('🔍 BROWSER CONNECTION: WebRTC connecting...');
        updateStatus('connecting', 'Connecting...');
      }
    };
    
    pc.onicegatheringstatechange = () => {
      log('🌐 BROWSER ICE: ICE gathering state:', pc.iceGatheringState);
    };
    
    pc.onicecandidate = (event) => {
      if (event.candidate) {
        log('🌐 BROWSER ICE: Generated ICE candidate:', event.candidate.candidate);
      } else {
        log('🌐 BROWSER ICE: ICE candidate gathering complete');
      }
    };
    
    pc.onsignalingstatechange = () => {
      log('🌐 BROWSER SIGNALING: Signaling state:', pc.signalingState);
    };
    
    pc.ontrack = (ev) => {
      log('📹 Received video stream from boat');
      videoEl.srcObject = ev.streams[0];
      videoPlaceholder.classList.add('hidden');
    };

    // Request video stream
    pc.addTransceiver('video', {direction: 'recvonly'});

    // Request stream from boat via WebSocket
    sendWebSocketMessage({
      type: 'request_stream',
      boat_id: selectedBoatId
    });
    
    log('📤 Sent stream request to server');
    
  } catch (error) {
    log('❌ Connection failed:', error.message);
    updateStatus('error', 'Connection failed');
    cleanup();
  }
  
  updateUI(false);
}

// Control functions
function sendLEDControl(action, ledId = 'status', duration = 1.0) {
  if (!selectedBoatId) {
    log('❌ No boat selected for LED control');
    return;
  }
  
  sendWebSocketMessage({
    type: 'led_control',
    boat_id: selectedBoatId,
    action: action,
    led_id: ledId,
    duration: duration
  });
  
  log(`💡 Sent LED control: ${action} ${ledId}`);
}

function sendMotorControl(action, speed = 0.5, duration = 0) {
  if (!selectedBoatId) {
    log('❌ No boat selected for motor control');
    return;
  }
  
  sendWebSocketMessage({
    type: 'motor_control',
    boat_id: selectedBoatId,
    action: action,
    speed: speed,
    duration: duration
  });
  
  log(`🚤 Sent motor control: ${action} at speed ${speed}`);
}

function sendBoatCommand(command, params = {}) {
  if (!selectedBoatId) {
    log('❌ No boat selected for command');
    return;
  }
  
  sendWebSocketMessage({
    type: 'boat_command',
    boat_id: selectedBoatId,
    command: command,
    params: params
  });
  
  log(`⚙️ Sent boat command: ${command}`);
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
  log('🔌 Disconnecting...');
  updateStatus('disconnecting', 'Disconnecting...');
  cleanup();
  updateStatus('idle', 'Idle');
  log('✅ Disconnected');
}

// Event listeners
connectBtn.addEventListener('click', start);
disconnectBtn.addEventListener('click', disconnect);

refreshBoatsBtn.addEventListener('click', loadBoats);

boatSelect.addEventListener('change', (e) => {
  selectedBoatId = e.target.value;
  updateUI(false);
  log(`🎯 Selected boat: ${selectedBoatId}`);
});

// Keyboard controls (for testing)
document.addEventListener('keydown', (e) => {
  if (!selectedBoatId) return;
  
  switch(e.key) {
    case 'l': sendLEDControl('on'); break;
    case 'L': sendLEDControl('off'); break;
    case 'b': sendLEDControl('blink'); break;
    case 'w': sendMotorControl('forward', 0.5, 2); break;
    case 's': sendMotorControl('backward', 0.5, 2); break;
    case 'a': sendMotorControl('left', 0.5, 1); break;
    case 'd': sendMotorControl('right', 0.5, 1); break;
    case ' ': sendMotorControl('stop'); break;
    case 'r': sendBoatCommand('status'); break;
  }
});

// Initialize
updateStatus('connecting', 'Connecting...');
updateUI(false);
log('🚢 Harbor relay client initialized');
log('🔌 Connecting to WebSocket...');

// Connect WebSocket on startup
connectWebSocket();

// Refresh boats every 30 seconds
setInterval(() => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    loadBoats();
  }
}, 30000);

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  cleanup();
  if (ws) {
    ws.close();
  }
});

// Add control info to log
log('🎮 Keyboard controls: L=LED on/off, B=blink, WASD=move, Space=stop, R=status');
</script>
</body>
</html>
"""


async def index_handler(_request: web.Request):
    """Serve the HTML client interface with WebSocket-based WebRTC signaling.
    
    Returns:
        web.Response: HTML response with embedded client
    """
    return web.Response(text=CLIENT_HTML, content_type='text/html')
