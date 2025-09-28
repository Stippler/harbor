#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Harbor - WebRTC Relay Server for Boat Camera Streaming.

A WebRTC relay server that connects boat clients (running on Pi Zero)
to browser clients, enabling remote camera streaming and control.
"""

import asyncio
import logging

from aiohttp import web

from .client import index_handler
from .relay import webrtc_offer_handler, list_boats_handler
from .server import boat_websocket_handler, browser_websocket_handler


async def on_shutdown(app: web.Application):
    """Clean shutdown handler for the application.
    
    Closes all WebSocket connections and RTCPeerConnections gracefully.
    
    Args:
        app: aiohttp application instance
    """
    # Close WebSocket connections
    for ws in list(app["sockets"]):
        await ws.close()
    
    # Close peer connections
    await asyncio.gather(
        *(pc.close() for pc in list(app["pcs"])), 
        return_exceptions=True
    )


def create_app():
    """Create and configure the Harbor relay server application.
    
    Returns:
        web.Application: Configured aiohttp application
    """
    app = web.Application()
    
    # Initialize application state
    app["pcs"] = set()  # RTCPeerConnection instances
    app["sockets"] = set()  # WebSocket connections
    
    logging.info("Harbor relay server application created")
    
    # Configure routes
    app.router.add_get("/", index_handler)  # Web interface
    app.router.add_post("/offer", webrtc_offer_handler)  # WebRTC offers from browsers
    app.router.add_get("/boats", list_boats_handler)  # List available boats
    app.router.add_get("/ws", browser_websocket_handler)  # Browser WebSocket
    app.router.add_get("/boat", boat_websocket_handler)  # Boat WebSocket
    
    # Add shutdown handler
    app.on_shutdown.append(on_shutdown)
    
    return app


# Expose main components for external use
__all__ = [
    "create_app",
    "index_handler",
    "webrtc_offer_handler",
    "list_boats_handler",
    "boat_websocket_handler",
    "browser_websocket_handler"
]