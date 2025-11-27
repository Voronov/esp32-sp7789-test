import machine
import st7789
import time
import random
import vga2_bold_16x32 as font  # Import the font we just downloaded

# ================= SETUP =================
# Using your CONFIRMED working settings
spi = machine.SPI(2, baudrate=20000000, polarity=1, phase=1, sck=machine.Pin(18), mosi=machine.Pin(23))
reset_pin = machine.Pin(4, machine.Pin.OUT)
dc_pin = machine.Pin(2, machine.Pin.OUT)

display = st7789.ST7789(
    spi, 240, 240,
    reset=reset_pin,
    cs=None,
    dc=dc_pin,
    rotation=0
)

# Initialize
display.fill(st7789.BLACK)

# Setup Internal Clock (RTC)
rtc = machine.RTC()
# Set a fake start time: (Year, Month, Day, Weekday, Hour, Minute, Second, Subsecond)
rtc.datetime((2025, 11, 27, 3, 20, 30, 0, 0))

# ================= HELPER FUNCTIONS =================

def center_text(text, y, color, bg=st7789.BLACK):
    """Calculates X position to center text and draws it"""
    # Width of this specific font is 16 pixels per char
    text_width = len(text) * 16 
    x = (240 - text_width) // 2
    display.text(font, text, x, y, color, bg)

def draw_progress_bar(percent, color):
    """Draws a loading bar at the bottom"""
    bar_width = int((240 * percent) / 100)
    display.fill_rect(0, 230, bar_width, 10, color)
    display.fill_rect(bar_width, 230, 240-bar_width, 10, st7789.BLACK)

# ================= SCREENS =================

def screen_clock():
    """Screen 1: Big Clock"""
    current_time = rtc.datetime()
    # Format: HH:MM:SS
    time_str = "{:02d}:{:02d}:{:02d}".format(current_time[4], current_time[5], current_time[6])
    date_str = "{:04d}-{:02d}-{:02d}".format(current_time[0], current_time[1], current_time[2])
    
    # Draw Time (Big and centered)
    # We redraw background color to "erase" old numbers without clearing whole screen
    center_text(time_str, 90, st7789.CYAN, st7789.BLACK)
    
    # Draw Date (Smaller, just use same font for now)
    center_text(date_str, 130, st7789.YELLOW, st7789.BLACK)
    
    # Simple Animation: A "seconds" bar at the bottom
    seconds = current_time[6]
    pct = (seconds / 60) * 100
    draw_progress_bar(pct, st7789.BLUE)

def screen_bouncing_box(state):
    """Screen 2: Bouncing Box Animation"""
    # Clear screen only once when entering this mode
    if state['first_run']:
        display.fill(st7789.BLACK)
        state['first_run'] = False
        center_text("SCREENSAVER", 100, st7789.WHITE)

    # Erase old box
    display.fill_rect(state['x'], state['y'], 20, 20, st7789.BLACK)
    
    # Update position
    state['x'] += state['dx']
    state['y'] += state['dy']
    
    # Bounce off walls
    if state['x'] <= 0 or state['x'] >= 220: state['dx'] *= -1
    if state['y'] <= 0 or state['y'] >= 220: state['dy'] *= -1
    
    # Draw new box
    display.fill_rect(state['x'], state['y'], 20, 20, state['color'])

# ================= MAIN LOOP =================

last_switch = time.time()
current_screen = 0 

# State for the bouncing box animation
box_state = {
    'x': 10, 'y': 10, 
    'dx': 5, 'dy': 5, 
    'color': st7789.MAGENTA,
    'first_run': True
}

print("Starting UI Demo...")

while True:
    now = time.time()
    
    # Switch screens every 10 seconds
    if now - last_switch > 10:
        current_screen = (current_screen + 1) % 2
        last_switch = now
        display.fill(st7789.BLACK) # Clear screen on switch
        box_state['first_run'] = True # Reset animation state

    if current_screen == 0:
        # Update Clock
        screen_clock()
        # Sleep slightly to save power, but not too much or animation lags
        time.sleep(0.1) 
        
    elif current_screen == 1:
        # Update Animation
        screen_bouncing_box(box_state)
        # Faster refresh for smooth animation
        time.sleep(0.01)