#!/usr/bin/env python3
"""
Harbor Camera Presets
Predefined configurations for different performance levels and use cases.
"""

# Performance presets for different scenarios
CAMERA_PRESETS = {
    "ultra_low": {
        "width": 160,
        "height": 120,
        "fps": 10,
        "description": "Ultra low resolution for very slow connections or old hardware"
    },
    "low": {
        "width": 320,
        "height": 240,
        "fps": 15,
        "description": "Low resolution for Pi Zero and slow connections (default)"
    },
    "medium": {
        "width": 640,
        "height": 480,
        "fps": 20,
        "description": "Medium resolution for Pi 3/4 and good connections"
    },
    "high": {
        "width": 1280,
        "height": 720,
        "fps": 25,
        "description": "High resolution HD for Pi 4 and fast connections"
    },
    "ultra_high": {
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "description": "Ultra high resolution Full HD for Pi 4 and excellent connections"
    }
}

# Device-specific recommendations
DEVICE_PRESETS = {
    "pi_zero": "ultra_low",
    "pi_zero_2w": "low", 
    "pi_3": "medium",
    "pi_4": "high",
    "pi_5": "ultra_high"
}

def get_preset(preset_name):
    """Get camera configuration for a preset.
    
    Args:
        preset_name: Name of the preset
        
    Returns:
        dict: Camera configuration
        
    Raises:
        ValueError: If preset doesn't exist
    """
    if preset_name not in CAMERA_PRESETS:
        available = list(CAMERA_PRESETS.keys())
        raise ValueError(f"Unknown preset '{preset_name}'. Available: {available}")
    
    return CAMERA_PRESETS[preset_name].copy()

def list_presets():
    """List all available presets with descriptions."""
    print("📷 Available Camera Presets:")
    print("=" * 60)
    
    for name, config in CAMERA_PRESETS.items():
        print(f"{name:12} {config['width']:4}x{config['height']:<4} @ {config['fps']:2}fps - {config['description']}")
    
    print("\n🤖 Device Recommendations:")
    print("=" * 60)
    
    for device, preset in DEVICE_PRESETS.items():
        config = CAMERA_PRESETS[preset]
        print(f"{device:12} → {preset:10} ({config['width']}x{config['height']} @ {config['fps']}fps)")

def get_device_preset(device):
    """Get recommended preset for a device.
    
    Args:
        device: Device name (pi_zero, pi_zero_2w, pi_3, pi_4, pi_5)
        
    Returns:
        dict: Camera configuration
    """
    if device not in DEVICE_PRESETS:
        available = list(DEVICE_PRESETS.keys())
        raise ValueError(f"Unknown device '{device}'. Available: {available}")
    
    preset_name = DEVICE_PRESETS[device]
    return get_preset(preset_name)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_presets()
        elif command == "get":
            if len(sys.argv) < 3:
                print("Usage: python presets.py get <preset_name>")
                sys.exit(1)
            try:
                config = get_preset(sys.argv[2])
                print(f"Preset '{sys.argv[2]}':")
                print(f"  Width: {config['width']}")
                print(f"  Height: {config['height']}")
                print(f"  FPS: {config['fps']}")
                print(f"  Description: {config['description']}")
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
        elif command == "device":
            if len(sys.argv) < 3:
                print("Usage: python presets.py device <device_name>")
                sys.exit(1)
            try:
                config = get_device_preset(sys.argv[2])
                print(f"Recommended for {sys.argv[2]}:")
                print(f"  Width: {config['width']}")
                print(f"  Height: {config['height']}")
                print(f"  FPS: {config['fps']}")
                print(f"  Description: {config['description']}")
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
        else:
            print("Unknown command. Use: list, get <preset>, or device <device>")
            sys.exit(1)
    else:
        list_presets()
