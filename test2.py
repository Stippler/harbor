from picamera2 import Picamera2
from time import sleep

picam2 = Picamera2()
cfg = picam2.create_still_configuration(main={"size": (1280, 720)})
picam2.configure(cfg)
picam2.start()
sleep(0.5)                      # brief warm-up
picam2.capture_file("photo.jpg")
picam2.stop()
