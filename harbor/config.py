#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from typing import Dict, Any


class Config:
    """Configuration management for Harbor system."""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize configuration.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default.
        
        Returns:
            dict: Configuration dictionary
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load config file {self.config_file}: {e}")
                print("Using default configuration")
        
        # Return default configuration
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for harbor server.
        
        Returns:
            dict: Default server configuration
        """
        return {
            "server": {
                "host": "0.0.0.0",
                "port": 8080,
                "public_domain": "localhost",
                "public_port": 8080,
                "ssl": {
                    "enabled": False,
                    "cert_file": "",
                    "key_file": ""
                }
            },
            "webrtc": {
                "ice_servers": [
                    # Add STUN/TURN servers here if needed for NAT traversal
                    # {"urls": "stun:stun.l.google.com:19302"}
                ]
            }
        }
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key_path: str, default=None):
        """Get configuration value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path (e.g., "server.host")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value):
        """Set configuration value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path (e.g., "server.host")
            value: Value to set
        """
        keys = key_path.split('.')
        config_ref = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        # Set the final key
        config_ref[keys[-1]] = value
    
    def get_server_url(self) -> str:
        """Get the public server URL for boat clients.
        
        Returns:
            str: Server URL (ws:// or wss://)
        """
        domain = self.get("server.public_domain", "localhost")
        port = self.get("server.public_port", 8080)
        ssl_enabled = self.get("server.ssl.enabled", False)
        
        protocol = "wss" if ssl_enabled else "ws"
        
        # Don't include port if it's the default for the protocol
        if (ssl_enabled and port == 443) or (not ssl_enabled and port == 80):
            return f"{protocol}://{domain}"
        else:
            return f"{protocol}://{domain}:{port}"
    
    def get_web_url(self) -> str:
        """Get the public web URL for browser clients.
        
        Returns:
            str: Web URL (http:// or https://)
        """
        domain = self.get("server.public_domain", "localhost")
        port = self.get("server.public_port", 8080)
        ssl_enabled = self.get("server.ssl.enabled", False)
        
        protocol = "https" if ssl_enabled else "http"
        
        # Don't include port if it's the default for the protocol
        if (ssl_enabled and port == 443) or (not ssl_enabled and port == 80):
            return f"{protocol}://{domain}"
        else:
            return f"{protocol}://{domain}:{port}"


def create_example_config():
    """Create an example configuration file."""
    config = Config("config.example.json")
    
    # Set example values
    config.set("server.public_domain", "your-server.com")
    config.set("server.public_port", 8080)
    config.set("boat.server_url", "ws://your-server.com:8080")
    config.set("boat.boat_id", "my-boat-1")
    
    # Add STUN server example
    config.set("webrtc.ice_servers", [
        {"urls": "stun:stun.l.google.com:19302"}
    ])
    
    config.save_config()
    print("Example configuration created: config.example.json")


if __name__ == "__main__":
    create_example_config()
