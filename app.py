#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import ssl

from aiohttp import web

from harbor import create_app
from harbor.config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main():
    parser = argparse.ArgumentParser(description="Harbor WebRTC relay server for boat camera streaming")
    parser.add_argument("--config", default="config.json", help="Configuration file path")
    parser.add_argument("--host", help="Host to bind to (overrides config)")
    parser.add_argument("--port", type=int, help="Port to bind to (overrides config)")
    parser.add_argument("--domain", help="Public domain (overrides config)")
    parser.add_argument("--cert", help="Path to TLS cert (overrides config)")
    parser.add_argument("--key", help="Path to TLS key (overrides config)")
    args = parser.parse_args()

    # Load configuration
    config = Config(args.config)
    
    # Override config with command line arguments
    if args.host:
        config.set("server.host", args.host)
    if args.port:
        config.set("server.port", args.port)
        config.set("server.public_port", args.port)  # Assume same port for public
    if args.domain:
        config.set("server.public_domain", args.domain)
    if args.cert:
        config.set("server.ssl.cert_file", args.cert)
        config.set("server.ssl.enabled", True)
    if args.key:
        config.set("server.ssl.key_file", args.key)

    # Create Harbor relay server application with config
    app = create_app(config)

    # Get server settings
    host = config.get("server.host", "0.0.0.0")
    port = config.get("server.port", 8080)
    ssl_enabled = config.get("server.ssl.enabled", False)
    cert_file = config.get("server.ssl.cert_file")
    key_file = config.get("server.ssl.key_file")

    # Setup SSL if enabled
    ssl_context = None
    if ssl_enabled and cert_file and key_file:
        try:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(cert_file, key_file)
            logging.info("HTTPS enabled with cert: %s", cert_file)
        except Exception as e:
            logging.error("Failed to setup SSL: %s", e)
            logging.info("Falling back to HTTP")
            ssl_enabled = False

    # Display connection information
    web_url = config.get_web_url()
    server_url = config.get_server_url()
    
    logging.info("Starting Harbor relay server on %s:%d", host, port)
    logging.info("Web interface: %s", web_url)
    logging.info("Boat client URL: %s", server_url)
    
    # Start the server
    web.run_app(app, host=host, port=port, ssl_context=ssl_context)


if __name__ == "__main__":
    main()