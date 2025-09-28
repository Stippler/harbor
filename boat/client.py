#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import logging
from urllib.parse import urlparse
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
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
                
                # Connect to server WebSocket with manual timeout
                try:
                    self.ws = await asyncio.wait_for(
                        websockets.connect(ws_url), 
                        timeout=10.0
                    )
                    logging.info("Connected to Harbor server WebSocket at %s", url)
                    self.server_url = url  # Update to working URL
                    connected = True
                    break
                except asyncio.TimeoutError:
                    logging.warning("Connection to %s timed out", url)
                    continue
                
            except Exception as e:
                logging.warning("Failed to connect to %s: %s", url, e)
                continue
        
        if not connected:
            raise ConnectionError("Failed to connect to any server URLs")
        
        try:
            
            # Initialize WebRTC peer connection without STUN servers (local network only)
            # This works if both devices are on the same network or have direct connectivity
            ice_config = RTCConfiguration(
                iceServers=[],  # No STUN servers - direct connection only
            )
            logging.info("🚤 BOAT ICE: Initializing peer connection WITHOUT STUN servers (direct connection mode)")
            self.pc = RTCPeerConnection(configuration=ice_config)
            
            # Setup camera track
            self.camera_track = CameraStreamTrack(self.fps, (self.width, self.height))
            self.camera_track.start_camera()
            self.pc.addTrack(self.camera_track)
            logging.info("🚤 BOAT CAMERA: Camera track added to peer connection")
            logging.info("🚤 BOAT CAMERA: Track kind: %s", self.camera_track.kind)
            logging.info("🚤 BOAT CAMERA: Track ready state: %s", self.camera_track.readyState)
            
            # Setup peer connection event handlers
            @self.pc.on("iceconnectionstatechange")
            def on_ice_state_change():
                logging.info("🚤 BOAT ICE: ICE connection state changed: %s", self.pc.iceConnectionState)
                if self.pc.iceConnectionState == "failed":
                    logging.error("🚤 BOAT ICE: ICE connection failed - check STUN servers and firewall")
                elif self.pc.iceConnectionState == "disconnected":
                    logging.warning("🚤 BOAT ICE: ICE connection disconnected")
                elif self.pc.iceConnectionState == "connected":
                    logging.info("🚤 BOAT ICE: ICE connection established successfully!")
            
            @self.pc.on("connectionstatechange")
            def on_connection_state_change():
                logging.info("🚤 BOAT CONNECTION: Connection state changed: %s", self.pc.connectionState)
                if self.pc.connectionState == "connected":
                    logging.info("🚤 BOAT CONNECTION: WebRTC connection fully established!")
                elif self.pc.connectionState == "failed":
                    logging.error("🚤 BOAT CONNECTION: WebRTC connection failed")
                elif self.pc.connectionState == "disconnected":
                    logging.warning("🚤 BOAT CONNECTION: WebRTC connection disconnected")
            
            @self.pc.on("icegatheringstatechange")
            def on_ice_gathering_state_change():
                logging.info("🚤 BOAT ICE: ICE gathering state: %s", self.pc.iceGatheringState)
            
            @self.pc.on("icecandidate")
            def on_ice_candidate(candidate):
                if candidate:
                    logging.info("🚤 BOAT ICE: Generated ICE candidate: %s", candidate.candidate)
                else:
                    logging.info("🚤 BOAT ICE: ICE candidate gathering complete")
            
            @self.pc.on("signalingstatechange")
            def on_signaling_state_change():
                logging.info("🚤 BOAT SIGNALING: Signaling state: %s", self.pc.signalingState)
            
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
            
            # Create initial offer for automatic streaming
            logging.info("🚤 BOAT OFFER: Creating initial WebRTC offer for streaming")
            offer = await self.pc.createOffer()
            await self.pc.setLocalDescription(offer)
            logging.info("🚤 BOAT OFFER: Created offer - SDP length: %d", len(offer.sdp))
            logging.info("🚤 BOAT OFFER: Offer type: %s", offer.type)
            logging.info("🚤 BOAT OFFER: ICE gathering state after offer: %s", self.pc.iceGatheringState)
            logging.info("🚤 BOAT OFFER: Signaling state after offer: %s", self.pc.signalingState)
            
            # Send offer to server
            offer_message = {
                "type": "webrtc_offer",
                "boat_id": self.boat_id,
                "sdp": offer.sdp,
                "offer_type": offer.type
            }
            await self._send_message(offer_message)
            logging.info("🚤 BOAT OFFER: Sent WebRTC offer to server")
            
            # Test network connectivity
            await self._test_network_connectivity()
            
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
        
        if msg_type == "webrtc_offer" or msg_type == "offer":
            await self._handle_webrtc_offer(data)
        elif msg_type == "webrtc_answer" or msg_type == "answer":
            await self._handle_webrtc_answer(data)
        elif msg_type == "ice_candidate":
            await self._handle_ice_candidate(data)
        elif msg_type == "boat_registered":
            logging.info("Successfully registered with server as %s", self.boat_id)
        elif msg_type == "led_control":
            await self._handle_led_control(data)
        elif msg_type == "motor_control":
            await self._handle_motor_control(data)
        elif msg_type == "boat_command":
            await self._handle_boat_command(data)
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
            logging.info("🚤 BOAT ANSWER: Received WebRTC answer from server")
            logging.info("🚤 BOAT ANSWER: SDP length: %d", len(data.get("sdp", "")))
            logging.info("🚤 BOAT ANSWER: Answer type: %s", data.get("answer_type", "answer"))
            
            answer = RTCSessionDescription(
                sdp=data["sdp"],
                type=data["answer_type"]
            )
            
            await self.pc.setRemoteDescription(answer)
            logging.info("🚤 BOAT ANSWER: Successfully set remote description from server answer")
            logging.info("🚤 BOAT ANSWER: ICE connection state after answer: %s", self.pc.iceConnectionState)
            logging.info("🚤 BOAT ANSWER: Connection state after answer: %s", self.pc.connectionState)
            logging.info("🚤 BOAT ANSWER: Signaling state after answer: %s", self.pc.signalingState)
            
            # Set up ICE connection timeout
            asyncio.create_task(self._monitor_ice_connection())
            
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
    
    async def _handle_led_control(self, data):
        """Handle LED control command from server.
        
        Args:
            data: Message data containing LED control info
        """
        try:
            action = data.get("action")  # "on", "off", "blink"
            led_id = data.get("led_id", "status")  # default to status LED
            
            logging.info("LED control: %s LED %s", action, led_id)
            
            # Import GPIO control here to avoid issues on non-Pi systems
            try:
                from boat.gpio_controller import get_led_controller
                led_controller = get_led_controller()
                
                if action == "on":
                    led_controller.turn_on(led_id)
                elif action == "off":
                    led_controller.turn_off(led_id)
                elif action == "blink":
                    duration = data.get("duration", 1.0)
                    led_controller.blink(led_id, duration)
                
                # Send confirmation back to server
                await self._send_message({
                    "type": "command_response",
                    "boat_id": self.boat_id,
                    "command_type": "led_control",
                    "success": True,
                    "action": action,
                    "led_id": led_id
                })
                
            except ImportError:
                logging.warning("GPIO not available - LED control disabled")
                await self._send_message({
                    "type": "command_response",
                    "boat_id": self.boat_id,
                    "command_type": "led_control",
                    "success": False,
                    "error": "GPIO not available"
                })
                
        except Exception as e:
            logging.error("Failed to handle LED control: %s", e)
            await self._send_message({
                "type": "command_response",
                "boat_id": self.boat_id,
                "command_type": "led_control",
                "success": False,
                "error": str(e)
            })
    
    async def _handle_motor_control(self, data):
        """Handle motor control command from server.
        
        Args:
            data: Message data containing motor control info
        """
        try:
            action = data.get("action")  # "forward", "backward", "left", "right", "stop"
            speed = data.get("speed", 0.5)  # 0.0 to 1.0
            duration = data.get("duration", 0)  # 0 = continuous
            
            logging.info("Motor control: %s at speed %.2f for %s seconds", 
                        action, speed, duration if duration > 0 else "continuous")
            
            # Import GPIO control here to avoid issues on non-Pi systems
            try:
                from boat.gpio_controller import get_motor_controller
                motor_controller = get_motor_controller()
                
                if action == "forward":
                    motor_controller.move_forward(speed, duration)
                elif action == "backward":
                    motor_controller.move_backward(speed, duration)
                elif action == "left":
                    motor_controller.turn_left(speed, duration)
                elif action == "right":
                    motor_controller.turn_right(speed, duration)
                elif action == "stop":
                    motor_controller.stop()
                
                # Send confirmation back to server
                await self._send_message({
                    "type": "command_response",
                    "boat_id": self.boat_id,
                    "command_type": "motor_control",
                    "success": True,
                    "action": action,
                    "speed": speed,
                    "duration": duration
                })
                
            except ImportError:
                logging.warning("GPIO not available - Motor control disabled")
                await self._send_message({
                    "type": "command_response",
                    "boat_id": self.boat_id,
                    "command_type": "motor_control",
                    "success": False,
                    "error": "GPIO not available"
                })
                
        except Exception as e:
            logging.error("Failed to handle motor control: %s", e)
            await self._send_message({
                "type": "command_response",
                "boat_id": self.boat_id,
                "command_type": "motor_control",
                "success": False,
                "error": str(e)
            })
    
    async def _handle_boat_command(self, data):
        """Handle general boat command from server.
        
        Args:
            data: Message data containing boat command
        """
        try:
            command = data.get("command")
            params = data.get("params", {})
            
            logging.info("Boat command: %s with params %s", command, params)
            
            # Handle different boat commands
            if command == "status":
                # Send boat status back to server
                await self._send_message({
                    "type": "boat_status",
                    "boat_id": self.boat_id,
                    "camera_active": self.camera is not None,
                    "webrtc_connected": self.pc.connectionState == "connected" if self.pc else False,
                    "websocket_connected": self.ws and not self.ws.closed if hasattr(self.ws, 'closed') else bool(self.ws)
                })
            elif command == "restart_camera":
                # Restart camera
                await self._restart_camera()
            else:
                logging.warning("Unknown boat command: %s", command)
                await self._send_message({
                    "type": "command_response",
                    "boat_id": self.boat_id,
                    "command_type": "boat_command",
                    "success": False,
                    "error": f"Unknown command: {command}"
                })
                
        except Exception as e:
            logging.error("Failed to handle boat command: %s", e)
            await self._send_message({
                "type": "command_response",
                "boat_id": self.boat_id,
                "command_type": "boat_command",
                "success": False,
                "error": str(e)
            })
    
    async def _test_network_connectivity(self):
        """Test network connectivity to STUN servers."""
        import socket
        import asyncio
        
        # Test local network connectivity instead of Google STUN servers
        logging.info("🌐 BOAT NETWORK: Testing local network connectivity...")
        
        # Test connection to Harbor server
        try:
            import socket
            server_host = self.server_url.split("://")[1].split(":")[0]
            server_port = int(self.server_url.split(":")[-1])
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((server_host, server_port))
            sock.close()
            
            if result == 0:
                logging.info("🌐 BOAT NETWORK: ✅ Can reach Harbor server %s:%d", server_host, server_port)
            else:
                logging.warning("🌐 BOAT NETWORK: ❌ Cannot reach Harbor server %s:%d", server_host, server_port)
                
        except Exception as e:
            logging.error("🌐 BOAT NETWORK: ❌ Error testing Harbor server: %s", e)
        
        # Test DNS resolution
        try:
            import socket
            server_host = self.server_url.split("://")[1].split(":")[0]
            ip = socket.gethostbyname(server_host)
            logging.info("🌐 BOAT NETWORK: ✅ DNS resolution: %s -> %s", server_host, ip)
        except Exception as e:
            logging.error("🌐 BOAT NETWORK: ❌ DNS resolution failed: %s", e)
    
    async def _restart_camera(self):
        """Restart the camera."""
        try:
            if self.camera:
                logging.info("Stopping camera for restart")
                self.camera.stop()
                await asyncio.sleep(1)
                
                logging.info("Starting camera after restart")
                self.camera.start()
                
                await self._send_message({
                    "type": "command_response",
                    "boat_id": self.boat_id,
                    "command_type": "restart_camera",
                    "success": True
                })
                
        except Exception as e:
            logging.error("Failed to restart camera: %s", e)
            await self._send_message({
                "type": "command_response",
                "boat_id": self.boat_id,
                "command_type": "restart_camera",
                "success": False,
                "error": str(e)
            })
    
    async def _monitor_ice_connection(self):
        """Monitor ICE connection and log timeout if stuck."""
        await asyncio.sleep(30)  # Wait 30 seconds
        
        if self.pc and self.pc.iceConnectionState == "checking":
            logging.error("🚤 BOAT ICE: ICE connection stuck in 'checking' state for 30+ seconds")
            logging.error("🚤 BOAT ICE: This usually indicates firewall/NAT issues or STUN server problems")
            logging.error("🚤 BOAT ICE: Current ICE gathering state: %s", self.pc.iceGatheringState)
            logging.error("🚤 BOAT ICE: Current connection state: %s", self.pc.connectionState)
    
    async def _send_message(self, data):
        """Send message to server.
        
        Args:
            data: Dictionary to send as JSON
        """
        if self.ws and hasattr(self.ws, 'closed') and not self.ws.closed:
            await self.ws.send(json.dumps(data))
        elif self.ws:
            # For websockets that don't have .closed attribute, try sending anyway
            try:
                await self.ws.send(json.dumps(data))
            except Exception as e:
                logging.warning("Failed to send message: %s", e)


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
