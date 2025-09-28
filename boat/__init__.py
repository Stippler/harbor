#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Boat - Pi Zero WebRTC Camera Client.

A WebRTC camera streaming client designed to run on Raspberry Pi Zero,
connecting to a Harbor server and streaming live video with GPIO control.
"""

import asyncio
import logging
from aiohttp import web

from .led import LedController
from .motor import create_motor_controller
from .websocket import websocket_handler
from .client import create_boat_client


async def on_shutdown(app: web.Application):
    """Clean shutdown handler for the boat client application.
    
    Closes WebSocket connections, stops camera streams, 
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


def create_boat_app(server_url, width=160, height=120, fps=30, enable_motors=True):
    """Create and configure the Boat client application.
    
    Args:
        server_url: URL of the Harbor server to connect to
        width: Video width in pixels (default: 160)
        height: Video height in pixels (default: 120)
        fps: Frames per second for camera stream (default: 30)
        enable_motors: Enable motor controller (default: True)
        
    Returns:
        web.Application: Configured aiohttp application
    """
    app = web.Application()
    
    # Initialize application state
    app["server_url"] = server_url
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
    
    logging.info("Boat client created for server %s (%dx%d @ %d fps)", 
                server_url, width, height, fps)
    
    # Configure routes for local control interface
    app.router.add_get("/ws", websocket_handler)
    
    # Add shutdown handler
    app.on_shutdown.append(on_shutdown)
    
    return app


# Expose main components for external use
__all__ = [
    "create_boat_app",
    "create_boat_client",
    "LedController",
    "create_motor_controller",
    "websocket_handler"
]
