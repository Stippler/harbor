#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription

from .server import harbor_server


async def webrtc_offer_handler(request: web.Request):
    """Handle WebRTC offers from browser clients for boat streams.
    
    Creates a relay connection between a boat and browser client.
    
    Args:
        request: aiohttp web request containing SDP offer
        
    Returns:
        web.Response: JSON response with SDP answer or error
    """
    try:
        params = await request.json()
        boat_id = params.get("boat_id")
        
        if not boat_id:
            return web.json_response({
                "error": "boat_id is required"
            }, status=400)
        
        # Check if boat is available
        if boat_id not in harbor_server.boats:
            return web.json_response({
                "error": f"Boat {boat_id} not found"
            }, status=404)
        
        boat = harbor_server.boats[boat_id]
        if not boat.is_connected():
            return web.json_response({
                "error": f"Boat {boat_id} is not connected"
            }, status=503)
        
        # Create peer connection for browser
        browser_pc = RTCPeerConnection()
        
        # Create peer connection for boat relay
        boat_pc = RTCPeerConnection()
        
        # Setup track forwarding from boat to browser
        @boat_pc.on("track")
        def on_boat_track(track):
            logging.info("Received track from boat %s, forwarding to browser", boat_id)
            browser_pc.addTrack(track)
        
        # Handle browser offer
        browser_offer = RTCSessionDescription(
            sdp=params["sdp"], 
            type=params["type"]
        )
        
        await browser_pc.setRemoteDescription(browser_offer)
        
        # Create offer for boat
        boat_offer = await boat_pc.createOffer()
        await boat_pc.setLocalDescription(boat_offer)
        
        # Send offer to boat
        await boat.send_message({
            "type": "webrtc_offer",
            "sdp": boat_offer.sdp,
            "type": boat_offer.type
        })
        
        # Create answer for browser
        browser_answer = await browser_pc.createAnswer()
        await browser_pc.setLocalDescription(browser_answer)
        
        # Store connections for cleanup
        app = request.app
        app["pcs"].add(browser_pc)
        app["pcs"].add(boat_pc)
        
        @browser_pc.on("iceconnectionstatechange")
        def on_browser_ice_state():
            logging.info("Browser ICE state for boat %s: %s", boat_id, browser_pc.iceConnectionState)
            if browser_pc.iceConnectionState in ("failed", "closed"):
                app["pcs"].discard(browser_pc)
        
        @boat_pc.on("iceconnectionstatechange")
        def on_boat_ice_state():
            logging.info("Boat relay ICE state for %s: %s", boat_id, boat_pc.iceConnectionState)
            if boat_pc.iceConnectionState in ("failed", "closed"):
                app["pcs"].discard(boat_pc)
        
        return web.json_response({
            "sdp": browser_pc.localDescription.sdp,
            "type": browser_pc.localDescription.type
        })
        
    except Exception as e:
        logging.error("WebRTC relay offer failed: %s", e)
        return web.json_response({
            "error": f"WebRTC relay failed: {e}"
        }, status=500)


async def list_boats_handler(request: web.Request):
    """Handle requests for available boats list.
    
    Args:
        request: aiohttp web request
        
    Returns:
        web.Response: JSON response with available boats
    """
    try:
        boats = harbor_server.get_available_boats()
        return web.json_response({
            "boats": boats
        })
    
    except Exception as e:
        logging.error("Failed to list boats: %s", e)
        return web.json_response({
            "error": f"Failed to list boats: {e}"
        }, status=500)
