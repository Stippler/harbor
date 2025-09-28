#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import asyncio
import logging
import sys
import os

from boat.config import Config
from boat import create_boat_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


async def main():
    parser = argparse.ArgumentParser(description="Boat WebRTC camera client for Raspberry Pi")
    parser.add_argument("--config", default="config.json", help="Configuration file path")
    parser.add_argument("--server", help="Harbor server URL (overrides config)")
    parser.add_argument("--width", type=int, help="Camera width (overrides config)")
    parser.add_argument("--height", type=int, help="Camera height (overrides config)")
    parser.add_argument("--fps", type=int, help="Camera FPS (overrides config)")
    parser.add_argument("--boat-id", help="Unique boat identifier (overrides config)")
    args = parser.parse_args()

    # Load configuration
    config = Config(args.config)
    
    # Override config with command line arguments
    if args.server:
        config.set("boat.server_url", args.server)
    if args.width:
        config.set("boat.camera.width", args.width)
    if args.height:
        config.set("boat.camera.height", args.height)
    if args.fps:
        config.set("boat.camera.fps", args.fps)
    if args.boat_id:
        config.set("boat.boat_id", args.boat_id)

    # Get settings from config
    server_url = config.get("boat.server_url")
    fallback_url = config.get("boat.fallback_server_url")
    width = config.get("boat.camera.width", 160)
    height = config.get("boat.camera.height", 120)
    fps = config.get("boat.camera.fps", 30)
    boat_id = config.get("boat.boat_id")

    if not server_url:
        logging.error("Server URL not specified in config or command line")
        logging.error("Use --server or set boat.server_url in config.json")
        return 1

    logging.info("Starting Boat client connecting to %s", server_url)
    if fallback_url:
        logging.info("Fallback URL: %s", fallback_url)
    logging.info("Boat ID: %s", boat_id or "auto-generated")
    logging.info("Camera: %dx%d @ %d fps", width, height, fps)
    
    try:
        # Create boat client
        from boat.client import BoatClient
        client = BoatClient(server_url, width, height, fps, boat_id)
        
        # Start with fallback support
        await client.start(fallback_url)
        
        # Run until interrupted
        try:
            while client.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logging.info("Received interrupt signal")
        
        # Cleanup
        await client.stop()
        
    except Exception as e:
        logging.error("Boat client failed: %s", e)
        return 1
    
    logging.info("Boat client stopped")
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
