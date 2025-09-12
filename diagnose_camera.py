#!/usr/bin/env python3
"""
Camera Diagnostic Script for Harbor on Raspberry Pi
This script helps diagnose camera connection and configuration issues.
"""

import sys
import subprocess
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def run_command(cmd, description=""):
    """Run a shell command and return the result."""
    try:
        print(f"\n🔍 {description}")
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        if result.stderr:
            print(f"Error: {result.stderr.strip()}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⚠️ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return False

def check_camera_hardware():
    """Check if camera hardware is detected."""
    print("\n" + "="*60)
    print("🔧 CAMERA HARDWARE CHECK")
    print("="*60)
    
    # Check if camera is detected
    success = run_command("vcgencmd get_camera", "Check camera detection")
    
    # Check camera configuration
    run_command("raspi-config nonint get_camera", "Check camera configuration")
    
    # List video devices
    run_command("ls -la /dev/video*", "List video devices")
    
    # Check camera module in device tree
    run_command("dtparam -l | grep -i cam", "Check camera device tree parameters")
    
    return success

def check_camera_permissions():
    """Check camera permissions and groups."""
    print("\n" + "="*60)
    print("👤 PERMISSIONS CHECK")
    print("="*60)
    
    # Check user groups
    run_command("groups", "Check user groups")
    
    # Check video device permissions
    run_command("ls -la /dev/video0", "Check /dev/video0 permissions")
    
    # Check if user is in video group
    run_command("id -nG | grep -q video && echo 'User is in video group' || echo 'User NOT in video group'", 
                "Check video group membership")

def test_picamera2():
    """Test picamera2 functionality."""
    print("\n" + "="*60)
    print("📷 PICAMERA2 TEST")
    print("="*60)
    
    try:
        print("Importing picamera2...")
        from picamera2 import Picamera2
        print("✅ picamera2 imported successfully")
        
        print("Creating Picamera2 instance...")
        picam2 = Picamera2()
        print("✅ Picamera2 instance created")
        
        print("Getting camera info...")
        camera_info = picam2.camera_info
        print(f"📋 Camera info: {camera_info}")
        
        print("Configuring camera...")
        config = picam2.create_video_configuration(
            main={"size": (640, 480), "format": "RGB888"},
            buffer_count=2
        )
        picam2.configure(config)
        print("✅ Camera configured successfully")
        
        print("Starting camera...")
        picam2.start()
        print("✅ Camera started successfully")
        
        print("Capturing test frame...")
        frame = picam2.capture_array()
        print(f"✅ Frame captured: {frame.shape} {frame.dtype}")
        
        print("Stopping camera...")
        picam2.stop()
        print("✅ Camera stopped successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ picamera2 not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        try:
            if 'picam2' in locals():
                picam2.stop()
        except:
            pass
        return False

def test_harbor_camera():
    """Test Harbor camera module."""
    print("\n" + "="*60)
    print("🌊 HARBOR CAMERA TEST")
    print("="*60)
    
    try:
        print("Importing Harbor video module...")
        from harbor.video import CameraStreamTrack
        print("✅ Harbor video module imported")
        
        print("Creating camera track...")
        camera_track = CameraStreamTrack(fps=10, size=(320, 240))  # Lower settings for test
        print(f"✅ Camera track created (demo_mode: {camera_track.demo_mode})")
        
        print("Starting camera...")
        camera_track.start_camera()
        print("✅ Camera started")
        
        print("Testing frame capture...")
        import asyncio
        
        async def test_capture():
            frame = await camera_track.recv()
            return frame
        
        frame = asyncio.run(test_capture())
        print(f"✅ Frame received: {frame.width}x{frame.height}")
        
        print("Stopping camera...")
        camera_track.stop_camera()
        print("✅ Camera stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Harbor camera test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def provide_recommendations():
    """Provide troubleshooting recommendations."""
    print("\n" + "="*60)
    print("💡 TROUBLESHOOTING RECOMMENDATIONS")
    print("="*60)
    
    print("""
🔧 HARDWARE CHECKS:
1. Ensure camera ribbon cable is properly connected
2. Check camera cable is not damaged
3. Verify camera is enabled in raspi-config
4. Try a different camera module if available

⚙️ SOFTWARE FIXES:
1. Update system: sudo apt update && sudo apt upgrade
2. Enable camera: sudo raspi-config -> Interface Options -> Camera -> Enable
3. Add user to video group: sudo usermod -a -G video $USER
4. Reboot after changes: sudo reboot

🐍 PYTHON ENVIRONMENT:
1. Install picamera2: pip install picamera2
2. Install gpiozero: pip install gpiozero
3. Check Python version: python3 --version

📋 HARBOR SPECIFIC:
1. Run Harbor with verbose logging: python app.py --host 0.0.0.0 --port 8080
2. Check demo mode works: Harbor should fall back automatically
3. Test motor controls separately: python test_motor.py

🔍 DEBUGGING:
1. Check kernel messages: dmesg | grep -i camera
2. Check system logs: journalctl -u harbor (if using systemd)
3. Monitor camera usage: sudo fuser /dev/video0
    """)

def main():
    """Main diagnostic function."""
    print("🌊 Harbor Camera Diagnostic Tool")
    print("="*60)
    print("This tool will help diagnose camera issues on Raspberry Pi")
    
    # Run all diagnostic tests
    tests = [
        ("Hardware Detection", check_camera_hardware),
        ("Permissions Check", check_camera_permissions),
        ("Picamera2 Test", test_picamera2),
        ("Harbor Camera Test", test_harbor_camera),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print(f"\n⚠️ Test '{test_name}' interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed < total:
        provide_recommendations()
    else:
        print("\n🎉 All tests passed! Your camera should work with Harbor.")

if __name__ == "__main__":
    main()
