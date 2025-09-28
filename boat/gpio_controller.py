#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GPIO Controller for Raspberry Pi boat hardware.
Handles LED and motor control via GPIO pins.
"""

import logging
import asyncio
from typing import Optional

try:
    from gpiozero import LED, Motor, PWMOutputDevice
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("gpiozero not available - GPIO control disabled")


class LEDController:
    """Controls LEDs on the boat."""
    
    def __init__(self):
        """Initialize LED controller."""
        self.leds = {}
        
        if GPIO_AVAILABLE:
            # Define LED pins (adjust these based on your wiring)
            self.led_pins = {
                "status": 18,    # Status LED
                "power": 19,     # Power indicator LED
                "warning": 20,   # Warning/error LED
            }
            
            # Initialize LEDs
            for led_id, pin in self.led_pins.items():
                try:
                    self.leds[led_id] = LED(pin)
                    logging.info("Initialized LED %s on pin %d", led_id, pin)
                except Exception as e:
                    logging.error("Failed to initialize LED %s on pin %d: %s", led_id, pin, e)
        else:
            logging.warning("GPIO not available - LED controller disabled")
    
    def turn_on(self, led_id: str):
        """Turn on an LED.
        
        Args:
            led_id: ID of the LED to turn on
        """
        if not GPIO_AVAILABLE:
            logging.info("MOCK: Turn on LED %s", led_id)
            return
            
        if led_id in self.leds:
            self.leds[led_id].on()
            logging.info("Turned on LED %s", led_id)
        else:
            logging.warning("Unknown LED ID: %s", led_id)
    
    def turn_off(self, led_id: str):
        """Turn off an LED.
        
        Args:
            led_id: ID of the LED to turn off
        """
        if not GPIO_AVAILABLE:
            logging.info("MOCK: Turn off LED %s", led_id)
            return
            
        if led_id in self.leds:
            self.leds[led_id].off()
            logging.info("Turned off LED %s", led_id)
        else:
            logging.warning("Unknown LED ID: %s", led_id)
    
    def blink(self, led_id: str, duration: float = 1.0):
        """Blink an LED for a specified duration.
        
        Args:
            led_id: ID of the LED to blink
            duration: Duration to blink in seconds
        """
        if not GPIO_AVAILABLE:
            logging.info("MOCK: Blink LED %s for %.1f seconds", led_id, duration)
            return
            
        if led_id in self.leds:
            # Start blinking (0.5 second on, 0.5 second off)
            self.leds[led_id].blink(on_time=0.5, off_time=0.5)
            logging.info("Blinking LED %s for %.1f seconds", led_id, duration)
            
            # Stop blinking after duration
            def stop_blink():
                self.leds[led_id].off()
                logging.info("Stopped blinking LED %s", led_id)
            
            # Schedule stop
            import threading
            timer = threading.Timer(duration, stop_blink)
            timer.start()
        else:
            logging.warning("Unknown LED ID: %s", led_id)
    
    def cleanup(self):
        """Clean up LED resources."""
        if GPIO_AVAILABLE:
            for led_id, led in self.leds.items():
                try:
                    led.close()
                    logging.info("Cleaned up LED %s", led_id)
                except Exception as e:
                    logging.error("Failed to cleanup LED %s: %s", led_id, e)


class MotorController:
    """Controls motors on the boat."""
    
    def __init__(self):
        """Initialize motor controller."""
        self.left_motor = None
        self.right_motor = None
        
        if GPIO_AVAILABLE:
            try:
                # Define motor pins (adjust these based on your wiring)
                # Using L298N motor driver pins
                self.left_motor = Motor(forward=2, backward=3, enable=4)
                self.right_motor = Motor(forward=17, backward=27, enable=22)
                
                logging.info("Initialized motor controller")
            except Exception as e:
                logging.error("Failed to initialize motors: %s", e)
                self.left_motor = None
                self.right_motor = None
        else:
            logging.warning("GPIO not available - Motor controller disabled")
    
    def move_forward(self, speed: float = 0.5, duration: float = 0):
        """Move boat forward.
        
        Args:
            speed: Speed from 0.0 to 1.0
            duration: Duration in seconds (0 = continuous)
        """
        if not GPIO_AVAILABLE:
            logging.info("MOCK: Move forward at speed %.2f for %s seconds", 
                        speed, duration if duration > 0 else "continuous")
            return
            
        if self.left_motor and self.right_motor:
            self.left_motor.forward(speed)
            self.right_motor.forward(speed)
            logging.info("Moving forward at speed %.2f", speed)
            
            if duration > 0:
                # Stop after duration
                def stop_motors():
                    self.stop()
                    logging.info("Stopped motors after %.1f seconds", duration)
                
                import threading
                timer = threading.Timer(duration, stop_motors)
                timer.start()
        else:
            logging.warning("Motors not available")
    
    def move_backward(self, speed: float = 0.5, duration: float = 0):
        """Move boat backward.
        
        Args:
            speed: Speed from 0.0 to 1.0
            duration: Duration in seconds (0 = continuous)
        """
        if not GPIO_AVAILABLE:
            logging.info("MOCK: Move backward at speed %.2f for %s seconds", 
                        speed, duration if duration > 0 else "continuous")
            return
            
        if self.left_motor and self.right_motor:
            self.left_motor.backward(speed)
            self.right_motor.backward(speed)
            logging.info("Moving backward at speed %.2f", speed)
            
            if duration > 0:
                # Stop after duration
                def stop_motors():
                    self.stop()
                    logging.info("Stopped motors after %.1f seconds", duration)
                
                import threading
                timer = threading.Timer(duration, stop_motors)
                timer.start()
        else:
            logging.warning("Motors not available")
    
    def turn_left(self, speed: float = 0.5, duration: float = 0):
        """Turn boat left.
        
        Args:
            speed: Speed from 0.0 to 1.0
            duration: Duration in seconds (0 = continuous)
        """
        if not GPIO_AVAILABLE:
            logging.info("MOCK: Turn left at speed %.2f for %s seconds", 
                        speed, duration if duration > 0 else "continuous")
            return
            
        if self.left_motor and self.right_motor:
            self.left_motor.backward(speed)  # Left motor backward
            self.right_motor.forward(speed)  # Right motor forward
            logging.info("Turning left at speed %.2f", speed)
            
            if duration > 0:
                # Stop after duration
                def stop_motors():
                    self.stop()
                    logging.info("Stopped turning after %.1f seconds", duration)
                
                import threading
                timer = threading.Timer(duration, stop_motors)
                timer.start()
        else:
            logging.warning("Motors not available")
    
    def turn_right(self, speed: float = 0.5, duration: float = 0):
        """Turn boat right.
        
        Args:
            speed: Speed from 0.0 to 1.0
            duration: Duration in seconds (0 = continuous)
        """
        if not GPIO_AVAILABLE:
            logging.info("MOCK: Turn right at speed %.2f for %s seconds", 
                        speed, duration if duration > 0 else "continuous")
            return
            
        if self.left_motor and self.right_motor:
            self.left_motor.forward(speed)   # Left motor forward
            self.right_motor.backward(speed) # Right motor backward
            logging.info("Turning right at speed %.2f", speed)
            
            if duration > 0:
                # Stop after duration
                def stop_motors():
                    self.stop()
                    logging.info("Stopped turning after %.1f seconds", duration)
                
                import threading
                timer = threading.Timer(duration, stop_motors)
                timer.start()
        else:
            logging.warning("Motors not available")
    
    def stop(self):
        """Stop all motors."""
        if not GPIO_AVAILABLE:
            logging.info("MOCK: Stop all motors")
            return
            
        if self.left_motor and self.right_motor:
            self.left_motor.stop()
            self.right_motor.stop()
            logging.info("Stopped all motors")
        else:
            logging.warning("Motors not available")
    
    def cleanup(self):
        """Clean up motor resources."""
        if GPIO_AVAILABLE:
            try:
                if self.left_motor:
                    self.left_motor.close()
                if self.right_motor:
                    self.right_motor.close()
                logging.info("Cleaned up motor controller")
            except Exception as e:
                logging.error("Failed to cleanup motors: %s", e)


# Global instances (created on first use)
_led_controller = None
_motor_controller = None


def get_led_controller() -> LEDController:
    """Get the global LED controller instance."""
    global _led_controller
    if _led_controller is None:
        _led_controller = LEDController()
    return _led_controller


def get_motor_controller() -> MotorController:
    """Get the global motor controller instance."""
    global _motor_controller
    if _motor_controller is None:
        _motor_controller = MotorController()
    return _motor_controller


def cleanup_gpio():
    """Clean up all GPIO resources."""
    global _led_controller, _motor_controller
    
    if _led_controller:
        _led_controller.cleanup()
        _led_controller = None
    
    if _motor_controller:
        _motor_controller.cleanup()
        _motor_controller = None
    
    logging.info("GPIO cleanup completed")
