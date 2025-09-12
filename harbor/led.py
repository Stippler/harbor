#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging


class LedController:
    """GPIO LED controller with fallback to mock mode when GPIO is unavailable."""
    
    def __init__(self):
        self.enabled = False
        self._cache = {}
        try:
            from gpiozero import LED  # noqa: F401
            self._LED = LED
            self.enabled = True
            logging.info("GPIO enabled via gpiozero")
        except Exception as e:
            self.enabled = False
            self._LED = None
            logging.info("GPIO not available, using mock: %s", e)

    def set(self, pin, state):
        """Set LED state on specified pin.
        
        Args:
            pin: GPIO pin number
            state: LED state ('on'/'off', '1'/'0', 'true'/'false', 'high'/'low')
            
        Returns:
            dict: Status information with pin and state
            
        Raises:
            ValueError: If state is not a valid value
        """
        pin = int(pin)
        state_str = str(state).lower()
        
        if not self.enabled:
            logging.info("[MOCK] LED pin %d -> %s", pin, state_str)
            return {"status": "mock", "pin": pin, "state": state_str}

        led = self._cache.get(pin)
        if led is None:
            led = self._LED(pin)
            self._cache[pin] = led

        if state_str in ("on", "1", "true", "high"):
            led.on()
        elif state_str in ("off", "0", "false", "low"):
            led.off()
        else:
            raise ValueError("state must be 'on' or 'off'")
            
        return {"status": "ok", "pin": pin, "state": state_str}
