#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging

from aiohttp import web, WSMsgType


async def websocket_handler(request: web.Request):
    """Handle WebSocket connections for command processing.
    
    Supports commands:
    - ping: Echo back with pong
    - led: Control LED state on specified pin
    
    Args:
        request: aiohttp web request for WebSocket upgrade
        
    Returns:
        web.WebSocketResponse: WebSocket response object
    """
    app = request.app
    ws = web.WebSocketResponse(heartbeat=30)
    await ws.prepare(request)
    app["sockets"].add(ws)
    
    # Send hello message with GPIO status
    await ws.send_json({"type": "hello", "gpio": app["led"].enabled})

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                except Exception:
                    await ws.send_json({"type": "error", "message": "invalid json"})
                    continue

                await _handle_command(ws, app, data)
                
            elif msg.type == WSMsgType.ERROR:
                logging.error("WebSocket error: %s", ws.exception())
                break
    finally:
        app["sockets"].discard(ws)

    return ws


async def _handle_command(ws, app, data):
    """Handle individual WebSocket commands.
    
    Args:
        ws: WebSocket response object
        app: aiohttp application instance
        data: Parsed JSON command data
    """
    cmd = data.get("cmd")
    
    if cmd == "ping":
        await ws.send_json({"type": "pong", "data": data.get("data")})
        
    elif cmd == "led":
        try:
            pin = data["pin"]
            state = data["state"]
            result = app["led"].set(pin, state)
            await ws.send_json({"type": "led", "result": result})
        except Exception as e:
            await ws.send_json({"type": "error", "message": str(e)})
            
    else:
        await ws.send_json({"type": "error", "message": "unknown cmd"})
