#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Test script to make connected LEDs blink using the harbor module."""

import argparse
import asyncio
import logging
import time

from harbor.led import LedController

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def blink_led_sync(led_controller, pin, duration=10, interval=0.5):
    """Blink an LED synchronously.
    
    Args:
        led_controller: LedController instance
        pin: GPIO pin number
        duration: Total duration to blink in seconds
        interval: Time between on/off states in seconds
    """
    print(f"Blinking LED on pin {pin} for {duration} seconds...")
    
    end_time = time.time() + duration
    state = True
    
    while time.time() < end_time:
        try:
            result = led_controller.set(pin, "on" if state else "off")
            print(f"LED {pin}: {result}")
            state = not state
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopping blink test...")
            break
        except Exception as e:
            print(f"Error controlling LED {pin}: {e}")
            break
    
    # Turn off LED when done
    try:
        led_controller.set(pin, "off")
        print(f"LED {pin} turned off")
    except Exception as e:
        print(f"Error turning off LED {pin}: {e}")


async def blink_led_async(led_controller, pin, duration=10, interval=0.5):
    """Blink an LED asynchronously.
    
    Args:
        led_controller: LedController instance
        pin: GPIO pin number
        duration: Total duration to blink in seconds
        interval: Time between on/off states in seconds
    """
    print(f"Async blinking LED on pin {pin} for {duration} seconds...")
    
    end_time = time.time() + duration
    state = True
    
    while time.time() < end_time:
        try:
            result = led_controller.set(pin, "on" if state else "off")
            print(f"LED {pin}: {result}")
            state = not state
            await asyncio.sleep(interval)
        except KeyboardInterrupt:
            print(f"\nStopping async blink test for pin {pin}...")
            break
        except Exception as e:
            print(f"Error controlling LED {pin}: {e}")
            break
    
    # Turn off LED when done
    try:
        led_controller.set(pin, "off")
        print(f"LED {pin} turned off")
    except Exception as e:
        print(f"Error turning off LED {pin}: {e}")


async def blink_multiple_leds(led_controller, pins, duration=10, interval=0.5):
    """Blink multiple LEDs concurrently.
    
    Args:
        led_controller: LedController instance
        pins: List of GPIO pin numbers
        duration: Total duration to blink in seconds
        interval: Time between on/off states in seconds
    """
    print(f"Blinking {len(pins)} LEDs concurrently: {pins}")
    
    # Create tasks for each LED
    tasks = [
        blink_led_async(led_controller, pin, duration, interval)
        for pin in pins
    ]
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\nStopping all blink tests...")
        # Turn off all LEDs
        for pin in pins:
            try:
                led_controller.set(pin, "off")
            except Exception as e:
                print(f"Error turning off LED {pin}: {e}")


def test_led_states(led_controller, pin):
    """Test different LED state formats.
    
    Args:
        led_controller: LedController instance
        pin: GPIO pin number
    """
    print(f"Testing different state formats for LED on pin {pin}...")
    
    test_states = [
        ("on", 1),
        ("off", 1),
        ("1", 1),
        ("0", 1),
        ("true", 1),
        ("false", 1),
        ("high", 1),
        ("low", 1),
    ]
    
    for state, delay in test_states:
        try:
            result = led_controller.set(pin, state)
            print(f"State '{state}': {result}")
            time.sleep(delay)
        except Exception as e:
            print(f"Error with state '{state}': {e}")
    
    # Turn off at the end
    led_controller.set(pin, "off")


def main():
    parser = argparse.ArgumentParser(description="Test LED blinking with harbor module")
    parser.add_argument("--pins", nargs="+", type=int, default=[17], 
                       help="GPIO pin numbers to test (default: 17)")
    parser.add_argument("--duration", type=float, default=10,
                       help="Duration to blink in seconds (default: 10)")
    parser.add_argument("--interval", type=float, default=0.5,
                       help="Interval between blinks in seconds (default: 0.5)")
    parser.add_argument("--mode", choices=["sync", "async", "multi", "states"], 
                       default="sync", help="Test mode (default: sync)")
    
    args = parser.parse_args()
    
    # Initialize LED controller
    led_controller = LedController()
    print(f"LED Controller initialized - GPIO enabled: {led_controller.enabled}")
    
    try:
        if args.mode == "sync":
            # Test single LED synchronously
            pin = args.pins[0]
            blink_led_sync(led_controller, pin, args.duration, args.interval)
            
        elif args.mode == "async":
            # Test single LED asynchronously
            pin = args.pins[0]
            asyncio.run(blink_led_async(led_controller, pin, args.duration, args.interval))
            
        elif args.mode == "multi":
            # Test multiple LEDs concurrently
            asyncio.run(blink_multiple_leds(led_controller, args.pins, args.duration, args.interval))
            
        elif args.mode == "states":
            # Test different state formats
            pin = args.pins[0]
            test_led_states(led_controller, pin)
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        # Ensure all LEDs are turned off
        print("Turning off all LEDs...")
        for pin in args.pins:
            try:
                led_controller.set(pin, "off")
            except Exception:
                pass
        print("Test completed")


if __name__ == "__main__":
    main()
