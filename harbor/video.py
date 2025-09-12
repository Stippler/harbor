#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import threading
import time
from queue import Queue, Empty

import av
import numpy as np
from aiortc.mediastreams import VideoStreamTrack


class CameraStreamTrack(VideoStreamTrack):
    """High-performance video stream track for Raspberry Pi camera."""
    
    kind = "video"

    def __init__(self, fps=30, size=(640, 480)):
        """Initialize the camera stream track.
        
        Args:
            fps: Frames per second (optimized for high performance)
            size: Camera resolution as (width, height) tuple
        """
        super().__init__()
        self.fps = max(5, int(fps))  # Minimum 5 fps for stability
        self.size = size
        self.frame_queue = Queue(maxsize=3)  # Small buffer for low latency
        self.camera_thread = None
        self.running = False
        self.last_frame = None
        self.demo_mode = False  # Initialize demo_mode attribute
        
        # Initialize camera
        try:
            from picamera2 import Picamera2
            self.picam2 = Picamera2()
            
            # Configure for maximum performance
            config = self.picam2.create_video_configuration(
                main={"size": size, "format": "RGB888"},
                buffer_count=4  # Optimize buffer count
            )
            self.picam2.configure(config)
            
            logging.info("Camera initialized: %dx%d @ %d fps", size[0], size[1], fps)
            self.camera_available = True
            self.demo_mode = False  # Real camera mode
            
        except Exception as e:
            logging.warning("Camera initialization failed, enabling demo mode: %s", e)
            self.camera_available = False
            self.demo_mode = True
            self.picam2 = None
    
    def start_camera(self):
        """Start the camera capture thread or demo mode."""
        if not self.camera_available and not self.demo_mode:
            logging.error("Neither camera nor demo mode is available")
            return
            
        self.running = True
        
        if self.camera_available and self.picam2:
            try:
                self.picam2.start()
                self.camera_thread = threading.Thread(target=self._capture_loop, daemon=True)
                self.camera_thread.start()
                logging.info("Camera capture started")
            except Exception as e:
                logging.error("Failed to start camera, falling back to demo mode: %s", e)
                # Fall back to demo mode
                self.camera_available = False
                self.demo_mode = True
                if self.picam2:
                    try:
                        self.picam2.stop()
                    except:
                        pass
                self.camera_thread = threading.Thread(target=self._demo_loop, daemon=True)
                self.camera_thread.start()
                logging.info("Demo mode started (camera fallback)")
        else:
            # Start demo mode
            self.camera_thread = threading.Thread(target=self._demo_loop, daemon=True)
            self.camera_thread.start()
            logging.info("Demo mode started")
    
    def stop_camera(self):
        """Stop the camera capture thread or demo mode."""
        self.running = False
        if self.camera_thread and self.camera_thread.is_alive():
            self.camera_thread.join(timeout=2.0)
        if hasattr(self, 'picam2') and self.picam2:
            try:
                self.picam2.stop()
                logging.info("Camera capture stopped")
            except Exception as e:
                logging.warning("Error stopping camera: %s", e)
        else:
            logging.info("Demo mode stopped")
    
    def _capture_loop(self):
        """High-performance camera capture loop."""
        target_interval = 1.0 / self.fps
        
        while self.running:
            try:
                start_time = time.time()
                
                # Capture frame directly as numpy array with timeout handling
                try:
                    frame_array = self.picam2.capture_array()
                except Exception as capture_error:
                    logging.warning("Camera capture failed: %s", capture_error)
                    # Generate a black frame as fallback
                    h, w = self.size[1], self.size[0]
                    frame_array = np.zeros((h, w, 3), dtype=np.uint8)
                    # Add error text overlay
                    frame_array[:, :, 0] = 64  # Red tint to indicate error
                
                # Store latest frame (non-blocking)
                self.last_frame = frame_array
                
                # Also put in queue for immediate consumption
                try:
                    # Clear old frames and add new one
                    while not self.frame_queue.empty():
                        try:
                            self.frame_queue.get_nowait()
                        except Empty:
                            break
                    self.frame_queue.put_nowait(frame_array)
                except:
                    pass  # Queue operations are non-critical
                
                # Maintain target frame rate
                elapsed = time.time() - start_time
                sleep_time = target_interval - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                logging.error("Camera capture loop error: %s", e)
                time.sleep(0.5)  # Longer pause on loop error
    
    def _demo_loop(self):
        """Demo mode loop that generates synthetic video frames."""
        target_interval = 1.0 / self.fps
        frame_count = 0
        
        while self.running:
            try:
                start_time = time.time()
                
                # Generate demo frame
                h, w = self.size[1], self.size[0]
                frame_array = self._generate_demo_frame(w, h, frame_count)
                
                # Store latest frame
                self.last_frame = frame_array
                
                # Also put in queue for immediate consumption
                try:
                    # Clear old frames and add new one
                    while not self.frame_queue.empty():
                        try:
                            self.frame_queue.get_nowait()
                        except:
                            break
                    self.frame_queue.put_nowait(frame_array)
                except:
                    pass  # Queue operations are non-critical
                
                frame_count += 1
                
                # Maintain target frame rate
                elapsed = time.time() - start_time
                sleep_time = target_interval - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                logging.error("Demo mode error: %s", e)
                time.sleep(0.1)
    
    def _generate_demo_frame(self, width, height, frame_num):
        """Generate a synthetic demo frame.
        
        Args:
            width: Frame width in pixels
            height: Frame height in pixels  
            frame_num: Current frame number for animation
            
        Returns:
            numpy.ndarray: RGB frame array
        """
        # Create base frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Animated gradient background
        for y in range(height):
            for x in range(width):
                # Create moving gradient pattern
                wave = np.sin((x + frame_num * 2) * 0.02) * 0.3 + 0.7
                r = int(30 * wave)
                g = int(40 * wave) 
                b = int(85 * wave)
                frame[y, x] = [r, g, b]
        
        # Add animated circle
        center_x, center_y = width // 2, height // 2
        radius = 50 + int(20 * np.sin(frame_num * 0.1))
        
        # Draw circle
        y, x = np.ogrid[:height, :width]
        mask = (x - center_x) ** 2 + (y - center_y) ** 2 <= radius ** 2
        frame[mask] = [59, 130, 246]  # Blue circle
        
        # Add text overlay (simple)
        text_y = center_y + radius + 30
        if text_y < height - 20:
            # Simple "DEMO" text using rectangles
            demo_positions = [
                # D
                (center_x - 60, text_y, 8, 20), (center_x - 52, text_y, 12, 4),
                (center_x - 52, text_y + 8, 8, 4), (center_x - 52, text_y + 16, 12, 4),
                # E  
                (center_x - 30, text_y, 4, 20), (center_x - 26, text_y, 12, 4),
                (center_x - 26, text_y + 8, 8, 4), (center_x - 26, text_y + 16, 12, 4),
                # M
                (center_x - 4, text_y, 4, 20), (center_x + 8, text_y, 4, 20),
                (center_x, text_y, 8, 4), (center_x + 2, text_y + 4, 4, 4),
                # O
                (center_x + 20, text_y, 4, 20), (center_x + 32, text_y, 4, 20),
                (center_x + 24, text_y, 8, 4), (center_x + 24, text_y + 16, 8, 4)
            ]
            
            for x, y, w, h in demo_positions:
                if 0 <= x < width and 0 <= y < height:
                    x_end = min(x + w, width)
                    y_end = min(y + h, height)
                    frame[y:y_end, x:x_end] = [226, 232, 240]  # Light text
        
        return frame

    async def recv(self):
        """Receive the next video frame with minimal latency.
        
        Returns:
            av.VideoFrame: The next frame with proper timestamp
        """
        if not self.running:
            raise RuntimeError("Camera/demo mode not started")
        
        # Get the most recent frame
        try:
            # Try to get fresh frame from queue first
            img = self.frame_queue.get_nowait()
        except Empty:
            # Fall back to last known frame
            if self.last_frame is not None:
                img = self.last_frame
            else:
                # Create emergency placeholder
                h, w = self.size[1], self.size[0]
                if self.demo_mode:
                    # Generate a basic demo frame if none available
                    img = self._generate_demo_frame(w, h, 0)
                else:
                    img = np.zeros((h, w, 3), dtype=np.uint8)
                    img[:, :, 1] = 128  # Green tint to indicate no data
        
        # Convert to video frame
        frame = av.VideoFrame.from_ndarray(img, format="rgb24")
        
        # Set timestamp for A/V sync
        pts, time_base = await self.next_timestamp()
        frame.pts = pts
        frame.time_base = time_base
        
        return frame
    
    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.stop_camera()
        except Exception:
            pass  # Ignore errors during cleanup