#!/usr/bin/env python3
from picamera2 import Picamera2
from pathlib import Path
import time

OUT = Path("fast_captures")
OUT.mkdir(exist_ok=True)

picam2 = Picamera2()
cfg = picam2.create_still_configuration(main={"size": (320, 240), "format": "RGB888"})
picam2.configure(cfg)
picam2.start()

frame_count = 0
t_start = time.time()

try:
    while True:
        ts = int(time.time() * 1000)
        path = OUT / f"img_{ts}.jpg"
        picam2.capture_file(str(path))   # direct write to disk

        frame_count += 1
        now = time.time()
        if now - t_start >= 1.0:
            fps = frame_count / (now - t_start)
            print(f"{fps:.2f} FPS")
            frame_count = 0
            t_start = now
except KeyboardInterrupt:
    pass
finally:
    picam2.stop()
