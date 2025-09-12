from gpiozero import LED
from time import sleep

leds = [LED(21), LED(16), LED(20), LED(26), LED(19)]

while True:
    for led in leds:
        led.on()
        sleep(1)
        led.off()


