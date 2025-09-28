#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import logging
from urllib.parse import urlparse
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import BYE

from .video import CameraStreamTrack


class BoatClient:
    """WebRTC client that streams camera feed to Harbor server."""
    
    def __init__(self, server_url, width=160, height=120, fps=30, boat_id=None):
        """Initialize the boat client.
        
        Args:
            server_url: URL of the Harbor server (e.g., 'ws://harbor-server:8080')
            width: Video width in pixels
            height: Video height in pixels
            fps: Frames per second
            boat_id: Unique identifier for this boat (optional)
        """
        self.server_url = server_url
        self.width = width
        self.height = height
        self.fps = fps
        self.boat_id = boat_id or f"boat_{asyncio.get_event_loop().time():.0f}"
        
        self.pc = None
        self.ws = None
        self.camera_track = None
        self.running = False
        
        logging.info("Boat client initialized: %s -> %s", self.boat_id, server_url)
    
    async def start(self, fallback_url=None):
        """Start the boat client and connect to server."""
        if self.running:
            logging.warning("Boat client already running")
            return
        
        self.running = True
        logging.info("Starting boat client connection to %s", self.server_url)
        
        # Try primary server URL first, then fallback
        urls_to_try = [self.server_url]
        if fallback_url:
            urls_to_try.append(fallback_url)
        
        connected = False
        for url in urls_to_try:
            try:
                logging.info("Attempting connection to %s", url)
                
                # Parse server URL
                parsed = urlparse(url)
                ws_url = f"ws://{parsed.netloc}/boat"
                
                # Connect to server WebSocket
                self.ws = await websockets.connect(ws_url, timeout=10)
                logging.info("Connected to Harbor server WebSocket at %s", url)
                self.server_url = url  # Update to working URL
                connected = True
                break
                
            except Exception as e:
                logging.warning("Failed to connect to %s: %s", url, e)
                continue
        
        if not connected:
            raise ConnectionError("Failed to connect to any server URLs")
        
        try:
            
            # Initialize WebRTC peer connection
            self.pc = RTCPeerConnection()
            
            # Setup camera track
            self.camera_track = CameraStreamTrack(self.fps, (self.width, self.height))
            self.camera_track.start_camera()
            self.pc.addTrack(self.camera_track)
            logging.info("Camera track added to peer connection")
            
            # Setup peer connection event handlers
            @self.pc.on("iceconnectionstatechange")
            def on_ice_state_change():
                logging.info("ICE connection state: %s", self.pc.iceConnectionState)
            
            @self.pc.on("connectionstatechange")
            def on_connection_state_change():
                logging.info("Connection state: %s", self.pc.connectionState)
            
            # Send boat registration
            await self._send_message({
                "type": "boat_register",
                "boat_id": self.boat_id,
                "capabilities": {
                    "video": True,
                    "width": self.width,
                    "height": self.height,
                    "fps": self.fps
                }
            })
            
            # Start message handling loop
            await self._message_loop()
            
        except Exception as e:
            logging.error("Failed to start boat client: %s", e)
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the boat client and cleanup resources."""
        if not self.running:
            return
        
        self.running = False
        logging.info("Stopping boat client")
        
        # Stop camera
        if self.camera_track:
            self.camera_track.stop_camera()
            self.camera_track = None
        
        # Close peer connection
        if self.pc:
            await self.pc.close()
            self.pc = None
        
        # Close WebSocket
        if self.ws:
            await self.ws.close()
            self.ws = None
        
        logging.info("Boat client stopped")
    
    async def _message_loop(self):
        """Handle incoming messages from server."""
        try:
            async for message in self.ws:
                if not self.running:
                    break
                
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    logging.warning("Received invalid JSON: %s", message)
                except Exception as e:
                    logging.error("Error handling message: %s", e)
        
        except websockets.exceptions.ConnectionClosed:
            logging.info("Server connection closed")
        except Exception as e:
            logging.error("Message loop error: %s", e)
        
        await self.stop()
    
    async def _handle_message(self, data):
        """Handle individual messages from server.
        
        Args:
            data: Parsed JSON message data
        """
        msg_type = data.get("type")
        
        if msg_type == "webrtc_offer":
            await self._handle_webrtc_offer(data)
        elif msg_type == "webrtc_answer":
            await self._handle_webrtc_answer(data)
        elif msg_type == "ice_candidate":
            await self._handle_ice_candidate(data)
        elif msg_type == "boat_registered":
            logging.info("Successfully registered with server as %s", self.boat_id)
        elif msg_type == "error":
            logging.error("Server error: %s", data.get("message"))
        else:
            logging.warning("Unknown message type: %s", msg_type)
    
    async def _handle_webrtc_offer(self, data):
        """Handle WebRTC offer from server.
        
        Args:
            data: Message data containing SDP offer
        """
        try:
            offer = RTCSessionDescription(
                sdp=data["sdp"],
                type=data["type"]
            )
            
            # Set remote description
            await self.pc.setRemoteDescription(offer)
            
            # Create and send answer
            answer = await self.pc.createAnswer()
            await self.pc.setLocalDescription(answer)
            
            await self._send_message({
                "type": "webrtc_answer",
                "boat_id": self.boat_id,
                "sdp": answer.sdp,
                "answer_type": answer.type
            })
            
            logging.info("Sent WebRTC answer to server")
            
        except Exception as e:
            logging.error("Failed to handle WebRTC offer: %s", e)
    
    async def _handle_webrtc_answer(self, data):
        """Handle WebRTC answer from server.
        
        Args:
            data: Message data containing SDP answer
        """
        try:
            answer = RTCSessionDescription(
                sdp=data["sdp"],
                type=data["answer_type"]
            )
            
            await self.pc.setRemoteDescription(answer)
            logging.info("Set remote description from server answer")
            
        except Exception as e:
            logging.error("Failed to handle WebRTC answer: %s", e)
    
    async def _handle_ice_candidate(self, data):
        """Handle ICE candidate from server.
        
        Args:
            data: Message data containing ICE candidate
        """
        # ICE candidate handling would go here
        # For now, we're using a simple setup without explicit ICE handling
        pass
    
    async def _send_message(self, data):
        """Send message to server.
        
        Args:
            data: Dictionary to send as JSON
        """
        if self.ws and not self.ws.closed:
            await self.ws.send(json.dumps(data))


async def create_boat_client(server_url, width=160, height=120, fps=30, boat_id=None):
    """Create and start a boat client.
    
    Args:
        server_url: URL of the Harbor server
        width: Video width in pixels
        height: Video height in pixels
        fps: Frames per second
        boat_id: Unique identifier for this boat
        
    Returns:
        BoatClient: Started boat client instance
    """
    client = BoatClient(server_url, width, height, fps, boat_id)
    await client.start()
    return client
