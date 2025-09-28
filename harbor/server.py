#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import logging
from typing import Dict, Set
import weakref

from aiohttp import web, WSMsgType
from aiortc import RTCPeerConnection, RTCSessionDescription


class HarborServer:
    """Harbor WebRTC relay server that connects boats to browser clients."""
    
    def __init__(self):
        """Initialize the Harbor server."""
        self.boats: Dict[str, 'BoatConnection'] = {}
        self.browser_clients: Set['BrowserClient'] = set()
        self.active_streams: Dict[str, RTCPeerConnection] = {}
        
        logging.info("Harbor server initialized")
    
    def register_boat(self, boat_id: str, websocket, capabilities: dict):
        """Register a new boat connection.
        
        Args:
            boat_id: Unique identifier for the boat
            websocket: WebSocket connection to the boat
            capabilities: Boat capabilities (video resolution, etc.)
        """
        if boat_id in self.boats:
            logging.warning("Boat %s already registered, replacing", boat_id)
        
        self.boats[boat_id] = BoatConnection(boat_id, websocket, capabilities)
        logging.info("Registered boat %s with capabilities: %s", boat_id, capabilities)
    
    def unregister_boat(self, boat_id: str):
        """Unregister a boat connection.
        
        Args:
            boat_id: Unique identifier for the boat
        """
        if boat_id in self.boats:
            del self.boats[boat_id]
            logging.info("Unregistered boat %s", boat_id)
    
    def register_browser_client(self, client: 'BrowserClient'):
        """Register a new browser client.
        
        Args:
            client: Browser client instance
        """
        self.browser_clients.add(client)
        logging.info("Registered browser client")
    
    def unregister_browser_client(self, client: 'BrowserClient'):
        """Unregister a browser client.
        
        Args:
            client: Browser client instance
        """
        self.browser_clients.discard(client)
        logging.info("Unregistered browser client")
    
    def get_available_boats(self):
        """Get list of available boats.
        
        Returns:
            list: List of boat information dictionaries
        """
        return [
            {
                "boat_id": boat_id,
                "capabilities": boat.capabilities,
                "connected": boat.is_connected()
            }
            for boat_id, boat in self.boats.items()
        ]
    
    async def setup_server_relay_stream(self, boat_id: str, browser_client: 'BrowserClient'):
        """Set up server-relayed video stream (no P2P WebRTC).
        
        This eliminates the need for STUN servers by routing video through the Harbor server.
        """
        if boat_id not in self.boats:
            logging.error("🟠 SERVER RELAY: Boat %s not found", boat_id)
            return False
        
        boat = self.boats[boat_id]
        if not boat.is_connected():
            logging.error("🟠 SERVER RELAY: Boat %s not connected", boat_id)
            return False
        
        try:
            # Create server-side peer connections
            boat_pc = RTCPeerConnection()
            browser_pc = RTCPeerConnection()
            
            # Set up track forwarding: boat -> server -> browser
            @boat_pc.on("track")
            def on_boat_track(track):
                logging.info("🟠 SERVER RELAY: Received track from boat %s, forwarding to browser", boat_id)
                browser_pc.addTrack(track)
            
            # Store connections
            browser_client.current_boat_id = boat_id
            browser_client.boat_pc = boat_pc
            browser_client.browser_pc = browser_pc
            
            # Create offer for boat (server acts as browser)
            boat_offer = await boat_pc.createOffer()
            await boat_pc.setLocalDescription(boat_offer)
            
            # Send offer to boat
            await boat.send_message({
                "type": "webrtc_offer",
                "sdp": boat_offer.sdp,
                "offer_type": boat_offer.type
            })
            
            # Wait for boat answer and set up browser connection
            @boat_pc.on("connectionstatechange")
            def on_boat_connection():
                logging.info("🟠 SERVER RELAY: Boat connection state: %s", boat_pc.connectionState)
                if boat_pc.connectionState == "connected":
                    # Create offer for browser when boat is connected
                    asyncio.create_task(self._setup_browser_connection(browser_client, browser_pc))
            
            logging.info("🟠 SERVER RELAY: Set up server relay for boat %s", boat_id)
            return True
            
        except Exception as e:
            logging.error("🟠 SERVER RELAY: Failed to set up server relay for boat %s: %s", boat_id, e)
            return False
    
    async def _setup_browser_connection(self, browser_client, browser_pc):
        """Set up browser connection after boat is connected."""
        try:
            # Create offer for browser
            browser_offer = await browser_pc.createOffer()
            await browser_pc.setLocalDescription(browser_offer)
            
            # Send offer to browser
            await browser_client.send_message({
                "type": "webrtc_offer",
                "boat_id": browser_client.current_boat_id,
                "sdp": browser_offer.sdp,
                "offer_type": browser_offer.type
            })
            
            logging.info("🟠 SERVER RELAY: Sent offer to browser for boat %s", browser_client.current_boat_id)
            
        except Exception as e:
            logging.error("🟠 SERVER RELAY: Failed to setup browser connection: %s", e)
            
        except Exception as e:
            logging.error("🟠 SERVER RELAY: Failed to set up relay for %s: %s", boat_id, e)
            return False
    
    async def relay_boat_offer_to_browser(self, boat_id: str, browser_client: 'BrowserClient'):
        """Relay boat's WebRTC offer to browser client.
        
        Args:
            boat_id: ID of the boat to stream from
            browser_client: Browser client to stream to
            
        Returns:
            bool: True if offer was relayed successfully
        """
        if boat_id not in self.boats:
            logging.error("Boat %s not found", boat_id)
            return False
        
        boat = self.boats[boat_id]
        if not boat.is_connected():
            logging.error("Boat %s not connected", boat_id)
            return False
        
        if not boat.current_offer:
            logging.error("🟠 RELAY OFFER: No WebRTC offer available from boat %s", boat_id)
            return False
        
        try:
            # Store the connection for answer relay
            browser_client.current_boat_id = boat_id
            logging.info("🟠 RELAY OFFER: Stored boat_id %s in browser client", boat_id)
            
            # Send the boat's offer to the browser
            offer_message = {
                "type": "webrtc_offer",
                "boat_id": boat_id,
                "sdp": boat.current_offer["sdp"],
                "offer_type": boat.current_offer["type"]
            }
            logging.info("🟠 RELAY OFFER: Sending offer to browser - SDP length: %d", len(offer_message["sdp"]))
            await browser_client.send_message(offer_message)
            
            logging.info("🟠 RELAY OFFER: Successfully relayed WebRTC offer from boat %s to browser", boat_id)
            return True
            
        except Exception as e:
            logging.error("Failed to relay offer from %s: %s", boat_id, e)
            return False
    
    async def relay_browser_answer_to_boat(self, boat_id: str, answer_data: dict):
        """Relay browser's WebRTC answer to boat.
        
        Args:
            boat_id: ID of the boat
            answer_data: WebRTC answer data from browser
            
        Returns:
            bool: True if answer was relayed successfully
        """
        if boat_id not in self.boats:
            logging.error("Boat %s not found", boat_id)
            return False
        
        boat = self.boats[boat_id]
        if not boat.is_connected():
            logging.error("Boat %s not connected", boat_id)
            return False
        
        try:
            # In server relay mode, handle browser answer for browser-server connection
            if hasattr(browser_client, 'browser_pc') and browser_client.browser_pc:
                # Set browser answer on server's browser peer connection
                answer = RTCSessionDescription(
                    sdp=answer_data.get("sdp"),
                    type=answer_data.get("answer_type", "answer")
                )
                await browser_client.browser_pc.setRemoteDescription(answer)
                logging.info("🟣 SERVER RELAY: Set browser answer on server connection")
                return True
            else:
                # Fallback to direct relay (P2P mode)
                answer_message = {
                    "type": "webrtc_answer",
                    "sdp": answer_data.get("sdp"),
                    "answer_type": answer_data.get("answer_type", "answer")
                }
                logging.info("🟣 RELAY ANSWER: Sending answer to boat %s - SDP length: %d", boat_id, len(answer_message["sdp"]))
                await boat.send_message(answer_message)
                
                logging.info("🟣 RELAY ANSWER: Successfully relayed WebRTC answer from browser to boat %s", boat_id)
                return True
            
        except Exception as e:
            logging.error("Failed to relay answer to %s: %s", boat_id, e)
            return False
    
    async def relay_control_command(self, boat_id: str, command: dict):
        """Relay control command from browser to boat.
        
        Args:
            boat_id: ID of the boat
            command: Control command data
            
        Returns:
            bool: True if command was relayed successfully
        """
        if boat_id not in self.boats:
            logging.error("Boat %s not found", boat_id)
            return False
        
        boat = self.boats[boat_id]
        if not boat.is_connected():
            logging.error("Boat %s not connected", boat_id)
            return False
        
        try:
            # Add boat_id to command and relay to boat
            command["boat_id"] = boat_id
            await boat.send_message(command)
            
            logging.info("Relayed control command to boat %s: %s", boat_id, command.get("type"))
            return True
            
        except Exception as e:
            logging.error("Failed to relay command to %s: %s", boat_id, e)
            return False


class BoatConnection:
    """Represents a connection to a boat client."""
    
    def __init__(self, boat_id: str, websocket, capabilities: dict):
        """Initialize boat connection.
        
        Args:
            boat_id: Unique identifier for the boat
            websocket: WebSocket connection
            capabilities: Boat capabilities
        """
        self.boat_id = boat_id
        self.websocket = websocket
        self.capabilities = capabilities
        self.pc = None
        self.current_offer = None  # Store the boat's WebRTC offer
    
    def is_connected(self):
        """Check if boat is still connected.
        
        Returns:
            bool: True if connected
        """
        return self.websocket and not self.websocket.closed
    
    async def send_message(self, data: dict):
        """Send message to boat.
        
        Args:
            data: Message data to send
        """
        if self.is_connected():
            await self.websocket.send_str(json.dumps(data))
    


class BrowserClient:
    """Represents a browser client connection."""
    
    def __init__(self, websocket):
        """Initialize browser client.
        
        Args:
            websocket: WebSocket connection to browser
        """
        self.websocket = websocket
        self.pc = None
        self.current_boat_id = None
    
    def is_connected(self):
        """Check if browser client is still connected.
        
        Returns:
            bool: True if connected
        """
        return self.websocket and not self.websocket.closed
    
    async def send_message(self, data: dict):
        """Send message to browser client.
        
        Args:
            data: Message data to send
        """
        if self.is_connected():
            await self.websocket.send_json(data)


# Global server instance
harbor_server = HarborServer()


async def boat_websocket_handler(request: web.Request):
    """Handle WebSocket connections from boat clients.
    
    Args:
        request: aiohttp web request
        
    Returns:
        web.WebSocketResponse: WebSocket response
    """
    ws = web.WebSocketResponse(heartbeat=30)
    await ws.prepare(request)
    logging.info("🔗 BOAT WS: New boat WebSocket connection from %s", request.remote)
    
    boat_id = None
    
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    msg_type = data.get("type")
                    
                    if msg_type == "boat_register":
                        boat_id = data["boat_id"]
                        capabilities = data.get("capabilities", {})
                        harbor_server.register_boat(boat_id, ws, capabilities)
                        
                        await ws.send_str(json.dumps({
                            "type": "boat_registered",
                            "boat_id": boat_id
                        }))
                    
                    elif msg_type == "webrtc_offer":
                        # Handle WebRTC offer from boat - store for browser clients
                        boat_id = data.get("boat_id")
                        logging.info("🔵 BOAT OFFER: Received WebRTC offer from boat %s", boat_id)
                        logging.info("🔵 BOAT OFFER: SDP length: %d", len(data.get("sdp", "")))
                        logging.info("🔵 BOAT OFFER: Offer type: %s", data.get("offer_type", "offer"))
                        
                        if boat_id in harbor_server.boats:
                            boat = harbor_server.boats[boat_id]
                            boat.current_offer = {
                                "sdp": data.get("sdp"),
                                "type": data.get("offer_type", "offer")
                            }
                            logging.info("🔵 BOAT OFFER: Stored WebRTC offer from boat %s", boat_id)
                        else:
                            logging.error("🔴 BOAT OFFER: Boat %s not found in registered boats", boat_id)
                    
                    elif msg_type == "webrtc_answer":
                        # Handle WebRTC answer from boat in server relay mode
                        boat_id = data.get("boat_id")
                        logging.info("🔵 BOAT ANSWER: Received WebRTC answer from boat %s", boat_id)
                        
                        # Find browser client for this boat and set answer on boat peer connection
                        for client in harbor_server.browser_clients:
                            if hasattr(client, 'current_boat_id') and client.current_boat_id == boat_id:
                                if hasattr(client, 'boat_pc') and client.boat_pc:
                                    try:
                                        answer = RTCSessionDescription(
                                            sdp=data.get("sdp"),
                                            type=data.get("answer_type", "answer")
                                        )
                                        await client.boat_pc.setRemoteDescription(answer)
                                        logging.info("🔵 BOAT ANSWER: Set boat answer on server relay connection")
                                    except Exception as e:
                                        logging.error("🔵 BOAT ANSWER: Failed to set boat answer: %s", e)
                                break
                    
                    else:
                        logging.warning("Unknown message type from boat: %s", msg_type)
                
                except json.JSONDecodeError:
                    logging.warning("Invalid JSON from boat")
                except Exception as e:
                    logging.error("Error handling boat message: %s", e)
            
            elif msg.type == WSMsgType.ERROR:
                logging.error("WebSocket error from boat: %s", ws.exception())
                break
    
    finally:
        if boat_id:
            harbor_server.unregister_boat(boat_id)
    
    return ws


async def browser_websocket_handler(request: web.Request):
    """Handle WebSocket connections from browser clients.
    
    Args:
        request: aiohttp web request
        
    Returns:
        web.WebSocketResponse: WebSocket response
    """
    ws = web.WebSocketResponse(heartbeat=30)
    await ws.prepare(request)
    logging.info("🌐 BROWSER WS: New browser WebSocket connection from %s", request.remote)
    
    client = BrowserClient(ws)
    harbor_server.register_browser_client(client)
    
    # Send available boats
    await client.send_message({
        "type": "boats_available",
        "boats": harbor_server.get_available_boats()
    })
    
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    msg_type = data.get("type")
                    
                    if msg_type == "request_stream":
                        boat_id = data.get("boat_id")
                        logging.info("🟡 BROWSER REQUEST: Stream request for boat %s", boat_id)
                        if boat_id:
                            # Check if boat exists and has offer
                            if boat_id in harbor_server.boats:
                                boat = harbor_server.boats[boat_id]
                                logging.info("🟡 BROWSER REQUEST: Boat %s found, connected: %s", boat_id, boat.is_connected())
                                logging.info("🟡 BROWSER REQUEST: Boat has offer: %s", bool(boat.current_offer))
                                if boat.current_offer:
                                    logging.info("🟡 BROWSER REQUEST: Offer SDP length: %d", len(boat.current_offer.get("sdp", "")))
                            else:
                                logging.error("🟡 BROWSER REQUEST: Boat %s not found", boat_id)
                            
                            # Use server-relayed streaming instead of P2P
                            success = await harbor_server.setup_server_relay_stream(boat_id, client)
                            logging.info("🟡 BROWSER REQUEST: Server relay result: %s", success)
                            await client.send_message({
                                "type": "stream_response",
                                "boat_id": boat_id,
                                "success": success
                            })
                    
                    elif msg_type == "webrtc_answer":
                        # Relay WebRTC answer from browser to boat
                        boat_id = data.get("boat_id") or client.current_boat_id
                        logging.info("🟢 BROWSER ANSWER: Received WebRTC answer for boat %s", boat_id)
                        logging.info("🟢 BROWSER ANSWER: SDP length: %d", len(data.get("sdp", "")))
                        logging.info("🟢 BROWSER ANSWER: Answer type: %s", data.get("answer_type", "answer"))
                        if boat_id:
                            success = await harbor_server.relay_browser_answer_to_boat(boat_id, data)
                            logging.info("🟢 BROWSER ANSWER: Relay result: %s", success)
                    
                    elif msg_type in ["led_control", "motor_control", "boat_command"]:
                        # Relay control commands to boat
                        boat_id = data.get("boat_id") or client.current_boat_id
                        if boat_id:
                            success = await harbor_server.relay_control_command(boat_id, data)
                            await client.send_message({
                                "type": "command_response",
                                "boat_id": boat_id,
                                "command_type": msg_type,
                                "success": success
                            })
                    
                    elif msg_type == "list_boats":
                        await client.send_message({
                            "type": "boats_available",
                            "boats": harbor_server.get_available_boats()
                        })
                    
                    else:
                        logging.warning("Unknown message type from browser: %s", msg_type)
                
                except json.JSONDecodeError:
                    logging.warning("Invalid JSON from browser")
                except Exception as e:
                    logging.error("Error handling browser message: %s", e)
            
            elif msg.type == WSMsgType.ERROR:
                logging.error("WebSocket error from browser: %s", ws.exception())
                break
    
    finally:
        harbor_server.unregister_browser_client(client)
    
    return ws
