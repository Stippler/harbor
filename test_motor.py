#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Test script for the Harbor motor control module."""

import argparse
import asyncio
import logging
import time
import sys
from pathlib import Path

# Add harbor module to path
sys.path.insert(0, str(Path(__file__).parent))

from harbor.motor import MotorController, create_motor_controller, MOTOR_CONFIGS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def test_basic_motor_control():
    """Test basic motor control functionality."""
    print("🔧 Testing Basic Motor Control")
    print("=" * 50)
    
    controller = MotorController()
    
    # Setup motors with default pins
    print("\n1. Setting up motors...")
    left_result = controller.setup_motor("left", 18, 19, 12)
    right_result = controller.setup_motor("right", 20, 21, 13)
    
    print(f"Left motor setup: {left_result}")
    print(f"Right motor setup: {right_result}")
    
    # Test individual motor control
    print("\n2. Testing individual motor control...")
    
    test_cases = [
        ("left", 0.5, "forward"),
        ("left", 0.8, "backward"), 
        ("left", 0.0, "stop"),
        ("right", 0.6, "forward"),
        ("right", 0.3, "backward"),
        ("right", 0.0, "stop")
    ]
    
    for motor_id, speed, direction in test_cases:
        result = controller.set_motor_speed(motor_id, speed, direction)
        print(f"Motor {motor_id} {direction} at {speed}: {result['message']}")
        time.sleep(1)
    
    # Test motor status
    print("\n3. Motor status check...")
    status = controller.get_motor_status()
    print(f"All motors status: {status}")
    
    # Cleanup
    controller.cleanup()
    print("\n✅ Basic motor control test completed")


def test_dual_motor_control():
    """Test dual motor control and movement patterns."""
    print("\n🚗 Testing Dual Motor Control")
    print("=" * 50)
    
    controller = create_motor_controller("l298n_default")
    
    # Test movement patterns
    movements = [
        ("Forward", lambda: controller.move_forward(0.7)),
        ("Backward", lambda: controller.move_backward(0.6)), 
        ("Turn Left", lambda: controller.turn_left(0.5)),
        ("Turn Right", lambda: controller.turn_right(0.5)),
        ("Spin Left", lambda: controller.spin_left(0.4)),
        ("Spin Right", lambda: controller.spin_right(0.4)),
        ("Stop", lambda: controller.stop_all_motors())
    ]
    
    print("\n1. Testing movement patterns...")
    for name, movement_func in movements:
        print(f"\n{name}:")
        result = movement_func()
        print(f"  Result: {result.get('message', 'OK')}")
        if 'results' in result:
            for motor, motor_result in result['results'].items():
                print(f"  {motor}: {motor_result.get('message', 'OK')}")
        time.sleep(2)
    
    # Cleanup
    controller.cleanup()
    print("\n✅ Dual motor control test completed")


def test_custom_motor_setup():
    """Test custom motor pin configuration."""
    print("\n⚙️  Testing Custom Motor Setup")
    print("=" * 50)
    
    controller = MotorController()
    
    # Setup with custom pins
    print("\n1. Custom pin configuration...")
    custom_config = [
        ("motor_a", 22, 23, 18),
        ("motor_b", 24, 25, 19)
    ]
    
    for motor_id, in1, in2, enable in custom_config:
        result = controller.setup_motor(motor_id, in1, in2, enable)
        print(f"{motor_id}: {result}")
    
    # Test custom motor control
    print("\n2. Testing custom motors...")
    for motor_id, _, _, _ in custom_config:
        result = controller.set_motor_speed(motor_id, 0.5, "forward")
        print(f"{motor_id} forward: {result['message']}")
        time.sleep(1)
        
        result = controller.stop_motor(motor_id)
        print(f"{motor_id} stop: {result['message']}")
    
    controller.cleanup()
    print("\n✅ Custom motor setup test completed")


def test_error_handling():
    """Test error handling and edge cases."""
    print("\n⚠️  Testing Error Handling")
    print("=" * 50)
    
    controller = MotorController()
    
    # Test invalid motor ID
    print("\n1. Invalid motor ID...")
    result = controller.set_motor_speed("nonexistent", 0.5, "forward")
    print(f"Invalid motor: {result}")
    
    # Setup a motor for further tests
    controller.setup_motor("test", 18, 19, 12)
    
    # Test invalid direction
    print("\n2. Invalid direction...")
    result = controller.set_motor_speed("test", 0.5, "invalid_direction")
    print(f"Invalid direction: {result}")
    
    # Test speed clamping
    print("\n3. Speed value clamping...")
    test_speeds = [-0.5, 0.0, 0.5, 1.0, 1.5, 2.0]
    for speed in test_speeds:
        result = controller.set_motor_speed("test", speed, "forward")
        actual_speed = result.get('speed', 0)
        print(f"Input: {speed} -> Actual: {actual_speed}")
    
    controller.cleanup()
    print("\n✅ Error handling test completed")


async def test_async_motor_control():
    """Test asynchronous motor control patterns."""
    print("\n🔄 Testing Async Motor Control")
    print("=" * 50)
    
    controller = create_motor_controller("l298n_default")
    
    async def motor_sequence():
        """Run a sequence of motor movements."""
        sequences = [
            ("Forward", 0.6, 2.0),
            ("Left Turn", None, 1.0),  # Special case for turn
            ("Forward", 0.6, 2.0),
            ("Right Turn", None, 1.0),
            ("Backward", 0.4, 1.5),
            ("Stop", 0.0, 1.0)
        ]
        
        for name, speed, duration in sequences:
            print(f"\n{name} for {duration}s...")
            
            if name == "Forward":
                controller.move_forward(speed)
            elif name == "Backward":
                controller.move_backward(speed)
            elif name == "Left Turn":
                controller.turn_left(0.5)
            elif name == "Right Turn":
                controller.turn_right(0.5)
            elif name == "Stop":
                controller.stop_all_motors()
            
            await asyncio.sleep(duration)
    
    print("\n1. Running async motor sequence...")
    await motor_sequence()
    
    controller.cleanup()
    print("\n✅ Async motor control test completed")


def test_performance():
    """Test motor control performance and timing."""
    print("\n⚡ Testing Performance")
    print("=" * 50)
    
    controller = create_motor_controller("l298n_default")
    
    # Test command latency
    print("\n1. Command latency test...")
    num_commands = 100
    start_time = time.time()
    
    for i in range(num_commands):
        speed = (i % 10) / 10.0  # Vary speed from 0.0 to 0.9
        direction = "forward" if i % 2 == 0 else "backward"
        controller.set_motor_speed("left", speed, direction)
    
    end_time = time.time()
    avg_latency = (end_time - start_time) / num_commands * 1000  # ms
    
    print(f"Average command latency: {avg_latency:.2f}ms")
    print(f"Commands per second: {num_commands / (end_time - start_time):.1f}")
    
    # Test rapid direction changes
    print("\n2. Rapid direction change test...")
    start_time = time.time()
    
    for i in range(20):
        controller.move_forward(0.5)
        time.sleep(0.1)
        controller.move_backward(0.5)
        time.sleep(0.1)
        controller.stop_all_motors()
        time.sleep(0.1)
    
    end_time = time.time()
    print(f"Rapid change test completed in {end_time - start_time:.2f}s")
    
    controller.cleanup()
    print("\n✅ Performance test completed")


def main():
    """Main test function with command line options."""
    parser = argparse.ArgumentParser(description="Test Harbor motor control module")
    parser.add_argument("--test", choices=[
        "basic", "dual", "custom", "error", "async", "performance", "all"
    ], default="all", help="Test type to run")
    parser.add_argument("--config", choices=list(MOTOR_CONFIGS.keys()),
                       default="l298n_default", help="Motor configuration to use")
    
    args = parser.parse_args()
    
    print("🌊 Harbor Motor Control Test Suite")
    print("=" * 60)
    print(f"GPIO Available: {MotorController().enabled}")
    print(f"Test Mode: {args.test}")
    print(f"Configuration: {args.config}")
    
    try:
        if args.test in ["basic", "all"]:
            test_basic_motor_control()
            
        if args.test in ["dual", "all"]:
            test_dual_motor_control()
            
        if args.test in ["custom", "all"]:
            test_custom_motor_setup()
            
        if args.test in ["error", "all"]:
            test_error_handling()
            
        if args.test in ["async", "all"]:
            asyncio.run(test_async_motor_control())
            
        if args.test in ["performance", "all"]:
            test_performance()
        
        print("\n🎉 All tests completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
