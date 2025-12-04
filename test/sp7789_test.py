import machine
import driver.st7789 as st7789
import time

# 1. Define the pins (MATCHING YOUR WORKING ARDUINO SETUP)
# CS is set to None because your User_Setup.h says "TFT_CS -1"
spi = machine.SPI(2, baudrate=20000000, polarity=1, phase=1, sck=machine.Pin(18), mosi=machine.Pin(23))
reset_pin = machine.Pin(4, machine.Pin.OUT)
dc_pin = machine.Pin(2, machine.Pin.OUT)

# 2. Initialize the display
print("Initializing display...")
display = st7789.ST7789(
    spi,
    240, 240,
    reset=reset_pin,
    cs=None,          # <--- FIXED: Set to None (was pin 5)
    dc=dc_pin,
    rotation=0
)

# --- IMPORTANT: display.init() REMOVED ---
# The driver automatically initializes during the step above.
# Do not add display.init() here.

# 3. Clear screen to Black
print("Filling black...")
display.fill(st7789.BLACK)

# 4. Draw a Red Box
print("Drawing red box...")
display.fill_rect(50, 50, 100, 100, st7789.RED)

# 5. Loop colors
print("Looping colors...")
while True:
    display.fill(st7789.BLUE)
    time.sleep(1)
    display.fill(st7789.GREEN)
    time.sleep(1)