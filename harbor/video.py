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
            
        except Exception as e:
            logging.error("Camera initialization failed: %s", e)
            raise RuntimeError(f"Camera not available: {e}")
    
    def start_camera(self):
        """Start the camera capture thread."""
        if not self.camera_available:
            raise RuntimeError("Camera not available")
            
        self.running = True
        self.picam2.start()
        self.camera_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.camera_thread.start()
        logging.info("Camera capture started")
    
    def stop_camera(self):
        """Stop the camera capture thread."""
        self.running = False
        if self.camera_thread and self.camera_thread.is_alive():
            self.camera_thread.join(timeout=2.0)
        if self.picam2:
            try:
                self.picam2.stop()
                logging.info("Camera capture stopped")
            except Exception as e:
                logging.warning("Error stopping camera: %s", e)
    
    def _capture_loop(self):
        """High-performance camera capture loop."""
        target_interval = 1.0 / self.fps
        
        while self.running:
            try:
                start_time = time.time()
                
                # Capture frame directly as numpy array
                frame_array = self.picam2.capture_array()
                
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
                logging.error("Camera capture error: %s", e)
                time.sleep(0.1)  # Brief pause on error

    async def recv(self):
        """Receive the next video frame with minimal latency.
        
        Returns:
            av.VideoFrame: The next frame with proper timestamp
        """
        if not self.running:
            raise RuntimeError("Camera not started")
        
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
        self.stop_camera()