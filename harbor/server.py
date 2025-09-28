#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
            logging.error("No WebRTC offer available from boat %s", boat_id)
            return False
        
        try:
            # Store the connection for answer relay
            browser_client.current_boat_id = boat_id
            
            # Send the boat's offer to the browser
            await browser_client.send_message({
                "type": "webrtc_offer",
                "boat_id": boat_id,
                "sdp": boat.current_offer["sdp"],
                "offer_type": boat.current_offer["type"]
            })
            
            logging.info("Relayed WebRTC offer from boat %s to browser", boat_id)
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
            # Send the browser's answer to the boat
            await boat.send_message({
                "type": "webrtc_answer",
                "sdp": answer_data.get("sdp"),
                "answer_type": answer_data.get("type", "answer")
            })
            
            logging.info("Relayed WebRTC answer from browser to boat %s", boat_id)
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
                        if boat_id in harbor_server.boats:
                            boat = harbor_server.boats[boat_id]
                            boat.current_offer = {
                                "sdp": data.get("sdp"),
                                "type": data.get("offer_type", "offer")
                            }
                            logging.info("Stored WebRTC offer from boat %s", boat_id)
                    
                    elif msg_type == "webrtc_answer":
                        # Handle WebRTC answer from boat
                        # Relay to appropriate browser client
                        logging.info("Received WebRTC answer from boat %s", data.get("boat_id"))
                    
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
                        if boat_id:
                            success = await harbor_server.relay_boat_offer_to_browser(boat_id, client)
                            await client.send_message({
                                "type": "stream_response",
                                "boat_id": boat_id,
                                "success": success
                            })
                    
                    elif msg_type == "webrtc_answer":
                        # Relay WebRTC answer from browser to boat
                        boat_id = data.get("boat_id") or client.current_boat_id
                        if boat_id:
                            success = await harbor_server.relay_browser_answer_to_boat(boat_id, data)
                            logging.info("WebRTC answer relayed to boat %s: %s", boat_id, success)
                    
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
