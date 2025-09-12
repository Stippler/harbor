#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Harbor - WebRTC Live Camera Streaming for Raspberry Pi.

High-performance WebRTC video streaming server with WebSocket command 
interface, optimized for Raspberry Pi camera with GPIO LED control.
"""

import asyncio
import logging

from aiohttp import web

from .client import index_handler
from .led import LedController
from .motor import create_motor_controller
from .webrtc import offer_handler
from .websocket import websocket_handler


async def on_shutdown(app: web.Application):
    """Clean shutdown handler for the application.
    
    Closes all WebSocket connections, stops camera streams, 
    stops motors, and closes RTCPeerConnections gracefully.
    
    Args:
        app: aiohttp application instance
    """
    # Close WebSocket connections
    for ws in list(app["sockets"]):
        await ws.close()
    
    # Stop all camera tracks
    if "camera_tracks" in app:
        for camera_track in list(app["camera_tracks"]):
            camera_track.stop_camera()
    
    # Stop all motors and cleanup
    if "motor" in app:
        app["motor"].cleanup()
    
    # Close peer connections
    await asyncio.gather(
        *(pc.close() for pc in list(app["pcs"])), 
        return_exceptions=True
    )


def create_app(width=240, height=180, fps=10, enable_motors=True):
    """Create and configure the Harbor application for live camera streaming.
    
    Args:
        width: Video width in pixels (default: 240)
        height: Video height in pixels (default: 180)
        fps: Frames per second for camera stream (default: 10)
        enable_motors: Enable motor controller (default: True)
        
    Returns:
        web.Application: Configured aiohttp application
    """
    app = web.Application()
    
    # Initialize application state
    app["fps"] = fps
    app["width"] = width
    app["height"] = height
    app["led"] = LedController()
    app["pcs"] = set()  # RTCPeerConnection instances
    app["sockets"] = set()  # WebSocket connections
    app["camera_tracks"] = set()  # Active camera tracks
    
    # Initialize motor controller
    if enable_motors:
        try:
            app["motor"] = create_motor_controller("l298n_default")
            logging.info("Motor controller initialized")
        except Exception as e:
            logging.warning("Motor controller initialization failed: %s", e)
            app["motor"] = None
    else:
        app["motor"] = None
    
    logging.info("Harbor application created for live camera streaming (%dx%d @ %d fps)", 
                width, height, fps)
    
    # Configure routes
    app.router.add_get("/", index_handler)
    app.router.add_post("/offer", offer_handler)
    app.router.add_get("/ws", websocket_handler)
    
    # Add shutdown handler
    app.on_shutdown.append(on_shutdown)
    
    return app


# Expose main components for external use
__all__ = [
    "create_app",
    "LedController",
    "create_motor_controller",
    "index_handler",
    "offer_handler", 
    "websocket_handler"
]