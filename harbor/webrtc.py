#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription

from .video import CameraStreamTrack


async def offer_handler(request: web.Request):
    """Handle WebRTC offer and return answer with live camera stream.
    
    Creates a new RTCPeerConnection, adds live camera track, and processes 
    the offer to generate an appropriate answer.
    
    Args:
        request: aiohttp web request containing SDP offer
        
    Returns:
        web.Response: JSON response with SDP answer
    """
    app = request.app
    params = await request.json()
    
    # Create new peer connection
    pc = RTCPeerConnection()
    app["pcs"].add(pc)

    @pc.on("iceconnectionstatechange")
    def on_ice_state_change():
        logging.info("ICE state: %s", pc.iceConnectionState)
        if pc.iceConnectionState in ("failed", "closed"):
            app["pcs"].discard(pc)
            # Clean up camera track
            for track in pc.getSenders():
                if hasattr(track.track, 'stop_camera'):
                    track.track.stop_camera()

    # Get video settings from request (if provided)
    video_width = params.get("width", app["width"])
    video_height = params.get("height", app["height"])
    video_fps = params.get("fps", app["fps"])
    
    # Create and start camera stream track with custom settings
    try:
        camera_track = CameraStreamTrack(video_fps, (video_width, video_height))
        camera_track.start_camera()
        pc.addTrack(camera_track)
        logging.info("Camera track added: %dx%d @ %d fps (demo mode: %s)", 
                    video_width, video_height, video_fps, camera_track.demo_mode)
    except Exception as e:
        logging.error("Failed to create camera track: %s", e)
        # Return error response
        return web.json_response({
            "error": f"Camera initialization failed: {e}"
        }, status=500)
    
    # Store camera track for cleanup
    if "camera_tracks" not in app:
        app["camera_tracks"] = set()
    app["camera_tracks"].add(camera_track)

    # Process offer and create answer
    await pc.setRemoteDescription(RTCSessionDescription(sdp=params["sdp"], type=params["type"]))
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response({
        "sdp": pc.localDescription.sdp, 
        "type": pc.localDescription.type
    })