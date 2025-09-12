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
    
    # Send hello message with GPIO and motor status
    motor_available = app.get("motor") is not None
    await ws.send_json({
        "type": "hello", 
        "gpio": app["led"].enabled,
        "motor": motor_available
    })

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
    
    elif cmd == "motor":
        try:
            motor_controller = app.get("motor")
            if not motor_controller:
                await ws.send_json({"type": "error", "message": "Motor controller not available"})
                return
            
            action = data.get("action")
            motor_id = data.get("motor_id")
            speed = data.get("speed", 0.7)
            direction = data.get("direction", "forward")
            
            if action == "setup":
                # Setup individual motor
                in1_pin = data["in1_pin"]
                in2_pin = data["in2_pin"]
                enable_pin = data["enable_pin"]
                result = motor_controller.setup_motor(motor_id, in1_pin, in2_pin, enable_pin)
                
            elif action == "control":
                # Control individual motor
                result = motor_controller.set_motor_speed(motor_id, speed, direction)
                
            elif action == "stop":
                # Stop motor(s)
                if motor_id:
                    result = motor_controller.stop_motor(motor_id)
                else:
                    result = motor_controller.stop_all_motors()
                    
            elif action == "status":
                # Get motor status
                result = motor_controller.get_motor_status(motor_id)
                
            elif action == "move":
                # Dual motor movement commands
                movement = data.get("movement")
                if movement == "forward":
                    result = motor_controller.move_forward(speed)
                elif movement == "backward":
                    result = motor_controller.move_backward(speed)
                elif movement == "left":
                    result = motor_controller.turn_left(speed)
                elif movement == "right":
                    result = motor_controller.turn_right(speed)
                elif movement == "spin_left":
                    result = motor_controller.spin_left(speed)
                elif movement == "spin_right":
                    result = motor_controller.spin_right(speed)
                elif movement == "stop":
                    result = motor_controller.stop_all_motors()
                else:
                    result = {"status": "error", "message": f"Unknown movement: {movement}"}
            else:
                result = {"status": "error", "message": f"Unknown motor action: {action}"}
            
            await ws.send_json({"type": "motor", "result": result})
            
        except Exception as e:
            await ws.send_json({"type": "error", "message": str(e)})
            
    else:
        await ws.send_json({"type": "error", "message": "unknown cmd"})
