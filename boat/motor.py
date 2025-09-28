#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
from typing import Optional, Tuple, Dict, Any


class MotorController:
    """Dual motor controller for H-bridge motor drivers (L298N, etc.) with fallback to mock mode."""
    
    def __init__(self):
        """Initialize the motor controller with GPIO or mock mode."""
        self.enabled = False
        self.motors = {}
        self._pwm_objects = {}
        
        try:
            from gpiozero import OutputDevice, PWMOutputDevice
            self._OutputDevice = OutputDevice
            self._PWMOutputDevice = PWMOutputDevice
            self.enabled = True
            logging.info("GPIO enabled for motor control")
        except Exception as e:
            self.enabled = False
            self._OutputDevice = None
            self._PWMOutputDevice = None
            logging.info("GPIO not available for motors, using mock mode: %s", e)
    
    def setup_motor(self, motor_id: str, in1_pin: int, in2_pin: int, enable_pin: int) -> Dict[str, Any]:
        """Setup a motor with its control pins.
        
        Args:
            motor_id: Unique identifier for the motor ('left', 'right', 'motor1', etc.)
            in1_pin: GPIO pin for direction control 1
            in2_pin: GPIO pin for direction control 2  
            enable_pin: GPIO pin for PWM speed control (enable)
            
        Returns:
            dict: Status information about motor setup
        """
        if not self.enabled:
            logging.info("[MOCK] Motor %s setup: IN1=%d, IN2=%d, EN=%d", 
                        motor_id, in1_pin, in2_pin, enable_pin)
            self.motors[motor_id] = {
                'in1_pin': in1_pin,
                'in2_pin': in2_pin,
                'enable_pin': enable_pin,
                'speed': 0,
                'direction': 'stop',
                'mock': True
            }
            return {"status": "mock", "motor_id": motor_id, "message": "Motor configured in mock mode"}
        
        try:
            # Setup GPIO pins
            in1 = self._OutputDevice(in1_pin)
            in2 = self._OutputDevice(in2_pin)
            enable = self._PWMOutputDevice(enable_pin)
            
            # Store motor configuration
            self.motors[motor_id] = {
                'in1': in1,
                'in2': in2,
                'enable': enable,
                'in1_pin': in1_pin,
                'in2_pin': in2_pin,
                'enable_pin': enable_pin,
                'speed': 0,
                'direction': 'stop',
                'mock': False
            }
            
            # Initialize motor to stopped state
            in1.off()
            in2.off()
            enable.value = 0
            
            logging.info("Motor %s configured: IN1=%d, IN2=%d, EN=%d", 
                        motor_id, in1_pin, in2_pin, enable_pin)
            
            return {"status": "ok", "motor_id": motor_id, "message": "Motor configured successfully"}
            
        except Exception as e:
            logging.error("Failed to setup motor %s: %s", motor_id, e)
            return {"status": "error", "motor_id": motor_id, "message": str(e)}
    
    def set_motor_speed(self, motor_id: str, speed: float, direction: str = "forward") -> Dict[str, Any]:
        """Set motor speed and direction.
        
        Args:
            motor_id: Motor identifier
            speed: Speed value from 0.0 to 1.0 (0 = stop, 1 = full speed)
            direction: Direction ('forward', 'backward', 'stop')
            
        Returns:
            dict: Status information about the operation
        """
        if motor_id not in self.motors:
            return {"status": "error", "message": f"Motor {motor_id} not configured"}
        
        # Validate inputs
        speed = max(0.0, min(1.0, float(speed)))  # Clamp speed to 0-1
        direction = direction.lower()
        
        if direction not in ['forward', 'backward', 'stop']:
            return {"status": "error", "message": "Direction must be 'forward', 'backward', or 'stop'"}
        
        motor = self.motors[motor_id]
        
        if not self.enabled or motor.get('mock', False):
            # Mock mode
            motor['speed'] = speed
            motor['direction'] = direction
            logging.info("[MOCK] Motor %s: %s at %.1f%% speed", 
                        motor_id, direction, speed * 100)
            return {
                "status": "mock", 
                "motor_id": motor_id,
                "speed": speed,
                "direction": direction,
                "message": f"Motor {direction} at {speed*100:.1f}% (mock)"
            }
        
        try:
            # Set direction pins based on direction
            if direction == 'forward':
                motor['in1'].on()
                motor['in2'].off()
            elif direction == 'backward':
                motor['in1'].off()
                motor['in2'].on()
            else:  # stop
                motor['in1'].off()
                motor['in2'].off()
                speed = 0.0
            
            # Set PWM speed
            motor['enable'].value = speed
            
            # Update motor state
            motor['speed'] = speed
            motor['direction'] = direction
            
            logging.info("Motor %s: %s at %.1f%% speed", motor_id, direction, speed * 100)
            
            return {
                "status": "ok",
                "motor_id": motor_id, 
                "speed": speed,
                "direction": direction,
                "message": f"Motor {direction} at {speed*100:.1f}%"
            }
            
        except Exception as e:
            logging.error("Failed to control motor %s: %s", motor_id, e)
            return {"status": "error", "motor_id": motor_id, "message": str(e)}
    
    def stop_motor(self, motor_id: str) -> Dict[str, Any]:
        """Stop a specific motor.
        
        Args:
            motor_id: Motor identifier
            
        Returns:
            dict: Status information about the operation
        """
        return self.set_motor_speed(motor_id, 0.0, "stop")
    
    def stop_all_motors(self) -> Dict[str, Any]:
        """Stop all configured motors.
        
        Returns:
            dict: Status information about the operation
        """
        results = {}
        for motor_id in self.motors.keys():
            results[motor_id] = self.stop_motor(motor_id)
        
        logging.info("All motors stopped")
        return {"status": "ok", "message": "All motors stopped", "results": results}
    
    def get_motor_status(self, motor_id: Optional[str] = None) -> Dict[str, Any]:
        """Get status of one or all motors.
        
        Args:
            motor_id: Specific motor ID, or None for all motors
            
        Returns:
            dict: Motor status information
        """
        if motor_id:
            if motor_id not in self.motors:
                return {"status": "error", "message": f"Motor {motor_id} not configured"}
            
            motor = self.motors[motor_id]
            return {
                "motor_id": motor_id,
                "speed": motor['speed'],
                "direction": motor['direction'],
                "pins": {
                    "in1": motor['in1_pin'],
                    "in2": motor['in2_pin'], 
                    "enable": motor['enable_pin']
                },
                "mock": motor.get('mock', False)
            }
        else:
            # Return all motor statuses
            statuses = {}
            for mid in self.motors.keys():
                statuses[mid] = self.get_motor_status(mid)
            return {"motors": statuses, "enabled": self.enabled}
    
    def set_dual_motor_speed(self, left_speed: float, right_speed: float, 
                           left_direction: str = "forward", right_direction: str = "forward") -> Dict[str, Any]:
        """Control both motors simultaneously (common for robot movement).
        
        Args:
            left_speed: Speed for left motor (0.0 to 1.0)
            right_speed: Speed for right motor (0.0 to 1.0)
            left_direction: Direction for left motor
            right_direction: Direction for right motor
            
        Returns:
            dict: Status information about both motors
        """
        results = {}
        
        # Control left motor (assuming it's configured as 'left')
        if 'left' in self.motors:
            results['left'] = self.set_motor_speed('left', left_speed, left_direction)
        
        # Control right motor (assuming it's configured as 'right')
        if 'right' in self.motors:
            results['right'] = self.set_motor_speed('right', right_speed, right_direction)
        
        return {"status": "ok", "message": "Dual motor control", "results": results}
    
    def move_forward(self, speed: float = 0.7) -> Dict[str, Any]:
        """Move both motors forward at the same speed.
        
        Args:
            speed: Speed value from 0.0 to 1.0
            
        Returns:
            dict: Status information
        """
        return self.set_dual_motor_speed(speed, speed, "forward", "forward")
    
    def move_backward(self, speed: float = 0.7) -> Dict[str, Any]:
        """Move both motors backward at the same speed.
        
        Args:
            speed: Speed value from 0.0 to 1.0
            
        Returns:
            dict: Status information
        """
        return self.set_dual_motor_speed(speed, speed, "backward", "backward")
    
    def turn_left(self, speed: float = 0.7) -> Dict[str, Any]:
        """Turn left by moving right motor forward and left motor backward.
        
        Args:
            speed: Speed value from 0.0 to 1.0
            
        Returns:
            dict: Status information
        """
        return self.set_dual_motor_speed(speed, speed, "backward", "forward")
    
    def turn_right(self, speed: float = 0.7) -> Dict[str, Any]:
        """Turn right by moving left motor forward and right motor backward.
        
        Args:
            speed: Speed value from 0.0 to 1.0
            
        Returns:
            dict: Status information
        """
        return self.set_dual_motor_speed(speed, speed, "forward", "backward")
    
    def spin_left(self, speed: float = 0.5) -> Dict[str, Any]:
        """Spin left in place (left motor backward, right motor forward).
        
        Args:
            speed: Speed value from 0.0 to 1.0
            
        Returns:
            dict: Status information  
        """
        return self.set_dual_motor_speed(speed, speed, "backward", "forward")
    
    def spin_right(self, speed: float = 0.5) -> Dict[str, Any]:
        """Spin right in place (left motor forward, right motor backward).
        
        Args:
            speed: Speed value from 0.0 to 1.0
            
        Returns:
            dict: Status information
        """
        return self.set_dual_motor_speed(speed, speed, "forward", "backward")
    
    def cleanup(self):
        """Clean up GPIO resources and stop all motors."""
        try:
            self.stop_all_motors()
            
            if self.enabled:
                for motor_id, motor in self.motors.items():
                    if not motor.get('mock', False):
                        # Close GPIO objects
                        if 'in1' in motor:
                            motor['in1'].close()
                        if 'in2' in motor:
                            motor['in2'].close()  
                        if 'enable' in motor:
                            motor['enable'].close()
                        
                        logging.info("Motor %s GPIO cleaned up", motor_id)
            
            self.motors.clear()
            logging.info("Motor controller cleanup complete")
            
        except Exception as e:
            logging.error("Error during motor cleanup: %s", e)
    
    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup()


# Predefined motor configurations for common setups
MOTOR_CONFIGS = {
    "l298n_default": {
        "left": {"in1_pin": 18, "in2_pin": 19, "enable_pin": 12},
        "right": {"in1_pin": 20, "in2_pin": 21, "enable_pin": 13}
    },
    "l298n_alt": {
        "left": {"in1_pin": 22, "in2_pin": 23, "enable_pin": 18},
        "right": {"in1_pin": 24, "in2_pin": 25, "enable_pin": 19}
    }
}


def create_motor_controller(config_name: str = "l298n_default") -> MotorController:
    """Create and configure a motor controller with predefined pin setup.
    
    Args:
        config_name: Name of predefined configuration
        
    Returns:
        MotorController: Configured motor controller instance
    """
    if config_name not in MOTOR_CONFIGS:
        raise ValueError(f"Unknown config: {config_name}. Available: {list(MOTOR_CONFIGS.keys())}")
    
    controller = MotorController()
    config = MOTOR_CONFIGS[config_name]
    
    for motor_id, pins in config.items():
        result = controller.setup_motor(motor_id, **pins)
        logging.info("Motor setup result: %s", result)
    
    return controller
