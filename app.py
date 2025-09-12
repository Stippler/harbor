#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging

from aiohttp import web

from harbor import create_app

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main():
    parser = argparse.ArgumentParser(description="High-performance WebRTC camera streaming for Raspberry Pi")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to (default: 8080)")
    parser.add_argument("--width", type=int, default=240, help="Camera width (default: 240)")
    parser.add_argument("--height", type=int, default=180, help="Camera height (default: 180)")
    parser.add_argument("--fps", type=int, default=10, help="Camera FPS (default: 10)")
    parser.add_argument("--cert", help="Path to TLS cert (PEM) for HTTPS")
    parser.add_argument("--key", help="Path to TLS key (PEM) for HTTPS")
    args = parser.parse_args()

    # Create application with live camera streaming
    app = create_app(
        width=args.width,
        height=args.height,
        fps=args.fps
    )

    # Setup SSL if certificates provided
    ssl_context = None
    if args.cert and args.key:
        import ssl
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(args.cert, args.key)
        logging.info("HTTPS enabled")

    # Start the server
    logging.info("Starting Harbor camera streaming server on %s:%d", args.host, args.port)
    web.run_app(app, host=args.host, port=args.port, ssl_context=ssl_context)


if __name__ == "__main__":
    main()