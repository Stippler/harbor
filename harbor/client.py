#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from aiohttp import web


# HTML client interface
CLIENT_HTML = """<!doctype html>
<meta charset="utf-8">
<title>Pi Zero 2 W — WebRTC + WebSocket test</title>
<style>
body { font-family: system-ui, sans-serif; max-width: 800px; margin: 24px auto; }
#row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-items: start; }
button { padding: 8px 12px; }
input { padding: 6px; width: 80px; }
pre { background: #111; color: #eee; padding: 8px; height: 180px; overflow:auto; }
video { width: 100%; background: #000; }
</style>
<h2>Pi WebRTC Stream + Command WebSocket</h2>
<div id="row">
  <div>
    <video id="v" autoplay playsinline></video>
    <div style="margin-top:8px;">
      <button id="connect">Connect</button>
      <span id="status">idle</span>
    </div>
  </div>
  <div>
    <div style="margin-bottom:8px;">
      <label>LED pin: <input id="pin" type="number" value="17"></label>
    </div>
    <div>
      <button id="on">LED ON</button>
      <button id="off">LED OFF</button>
      <button id="ping">Ping</button>
    </div>
    <pre id="log"></pre>
  </div>
</div>
<script>
const logEl = document.getElementById('log');
function log(...args){ logEl.textContent += args.join(' ') + "\\n"; logEl.scrollTop = logEl.scrollHeight; }

let pc = null;
let ws = null;

async function start(){
  if (pc) return;
  document.getElementById('status').textContent = 'connecting';

  pc = new RTCPeerConnection({iceServers: []});
  pc.oniceconnectionstatechange = () => log('pc state:', pc.iceConnectionState);
  pc.ontrack = (ev) => { document.getElementById('v').srcObject = ev.streams[0]; };

  // request a recv-only video stream
  pc.addTransceiver('video', {direction: 'recvonly'});

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

  const r = await fetch('/offer', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({sdp: offer.sdp, type: offer.type})
  });
  const answer = await r.json();
  await pc.setRemoteDescription(answer);

  // command WebSocket
  const wsProto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(wsProto + '://' + location.host + '/ws');
  ws.onopen = () => { log('ws: open'); document.getElementById('status').textContent = 'connected'; };
  ws.onmessage = (ev) => log('ws:', ev.data);
  ws.onerror = (e) => log('ws error:', e.message || e);
  ws.onclose = () => log('ws: closed');
}

document.getElementById('connect').onclick = start;

document.getElementById('ping').onclick = () => {
  if (ws) ws.send(JSON.stringify({cmd:'ping', data: Date.now()}));
};

document.getElementById('on').onclick = () => {
  const pin = parseInt(document.getElementById('pin').value);
  if (ws) ws.send(JSON.stringify({cmd:'led', pin, state:'on'}));
};

document.getElementById('off').onclick = () => {
  const pin = parseInt(document.getElementById('pin').value);
  if (ws) ws.send(JSON.stringify({cmd:'led', pin, state:'off'}));
};
</script>
"""


async def index_handler(_request: web.Request):
    """Serve the HTML client interface.
    
    Returns:
        web.Response: HTML response with embedded client
    """
    return web.Response(text=CLIENT_HTML, content_type="text/html")
