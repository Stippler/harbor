#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging

from aiohttp import web

from harbor import create_app

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main():
    parser = argparse.ArgumentParser(description="Harbor WebRTC relay server for boat camera streaming")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to (default: 8080)")
    parser.add_argument("--cert", help="Path to TLS cert (PEM) for HTTPS")
    parser.add_argument("--key", help="Path to TLS key (PEM) for HTTPS")
    args = parser.parse_args()

    # Create Harbor relay server application
    app = create_app()

    # Setup SSL if certificates provided
    ssl_context = None
    if args.cert and args.key:
        import ssl
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(args.cert, args.key)
        logging.info("HTTPS enabled")

    # Start the server
    logging.info("Starting Harbor relay server on %s:%d", args.host, args.port)
    web.run_app(app, host=args.host, port=args.port, ssl_context=ssl_context)


if __name__ == "__main__":
    main()