#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import asyncio
import logging

from boat import create_boat_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


async def main():
    parser = argparse.ArgumentParser(description="Boat WebRTC camera client for Raspberry Pi")
    parser.add_argument("--server", required=True, help="Harbor server URL (e.g., ws://harbor-server:8080)")
    parser.add_argument("--width", type=int, default=160, help="Camera width (default: 160)")
    parser.add_argument("--height", type=int, default=120, help="Camera height (default: 120)")
    parser.add_argument("--fps", type=int, default=30, help="Camera FPS (default: 30)")
    parser.add_argument("--boat-id", help="Unique boat identifier (auto-generated if not provided)")
    args = parser.parse_args()

    logging.info("Starting Boat client connecting to %s", args.server)
    
    try:
        # Create and start boat client
        client = await create_boat_client(
            server_url=args.server,
            width=args.width,
            height=args.height,
            fps=args.fps,
            boat_id=args.boat_id
        )
        
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
