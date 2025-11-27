import machine
import st7789
import time
import random
import math
import vga2_bold_16x32 as font

# ================= SETUP =================
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

display.fill(st7789.BLACK)

# Setup Internal Clock (RTC)
rtc = machine.RTC()
rtc.datetime((2025, 11, 27, 3, 20, 30, 0, 0))

# ================= CONSTANTS =================
CENTER_X = 120
CENTER_Y = 100
CLOCK_RADIUS = 85

# Day names
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Color palette for animations
COLORS = [
    st7789.color565(255, 0, 128),    # Hot pink
    st7789.color565(0, 255, 128),    # Spring green
    st7789.color565(128, 0, 255),    # Purple
    st7789.color565(255, 128, 0),    # Orange
    st7789.color565(0, 128, 255),    # Sky blue
    st7789.color565(255, 255, 0),    # Yellow
]

# ================= HELPER FUNCTIONS =================

def center_text(text, y, color, bg=st7789.BLACK):
    text_width = len(text) * 16 
    x = (240 - text_width) // 2
    display.text(font, text, x, y, color, bg)

def draw_circle(cx, cy, r, color):
    """Draw circle outline using Bresenham's algorithm"""
    x = 0
    y = r
    d = 3 - 2 * r
    while x <= y:
        # Draw 8 octants
        display.pixel(cx + x, cy + y, color)
        display.pixel(cx - x, cy + y, color)
        display.pixel(cx + x, cy - y, color)
        display.pixel(cx - x, cy - y, color)
        display.pixel(cx + y, cy + x, color)
        display.pixel(cx - y, cy + x, color)
        display.pixel(cx + y, cy - x, color)
        display.pixel(cx - y, cy - x, color)
        if d < 0:
            d = d + 4 * x + 6
        else:
            d = d + 4 * (x - y) + 10
            y -= 1
        x += 1

def draw_thick_line(x0, y0, x1, y1, color, thickness=2):
    """Draw a thicker line by drawing multiple parallel lines"""
    display.line(x0, y0, x1, y1, color)
    if thickness > 1:
        # Draw parallel lines for thickness
        dx = x1 - x0
        dy = y1 - y0
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            # Perpendicular direction
            px = -dy / length
            py = dx / length
            for i in range(1, thickness):
                offset = (i + 1) // 2
                if i % 2 == 0:
                    offset = -offset
                ox = int(px * offset)
                oy = int(py * offset)
                display.line(x0 + ox, y0 + oy, x1 + ox, y1 + oy, color)

def draw_hand(angle, length, color, thickness=2):
    """Draw clock hand from center at given angle"""
    # Angle: 0 = 12 o'clock, increases clockwise
    rad = math.radians(angle - 90)
    x = int(CENTER_X + length * math.cos(rad))
    y = int(CENTER_Y + length * math.sin(rad))
    draw_thick_line(CENTER_X, CENTER_Y, x, y, color, thickness)

def erase_hand(angle, length, thickness=2):
    """Erase clock hand"""
    draw_hand(angle, length, st7789.BLACK, thickness)

def hsv_to_rgb565(h, s, v):
    """Convert HSV to RGB565 color"""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    r = int((r + m) * 255)
    g = int((g + m) * 255)
    b = int((b + m) * 255)
    return st7789.color565(r, g, b)

# ================= PARTICLE SYSTEM =================

class Particle:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x = random.randint(0, 239)
        self.y = random.randint(0, 239)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.life = random.randint(50, 150)
        self.max_life = self.life
        self.color_hue = random.randint(0, 360)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        
        if self.life <= 0 or self.x < 0 or self.x > 239 or self.y < 0 or self.y > 239:
            self.reset()
    
    def draw(self, erase=False):
        if erase:
            display.pixel(int(self.x), int(self.y), st7789.BLACK)
        else:
            # Fade based on life
            brightness = self.life / self.max_life
            color = hsv_to_rgb565(self.color_hue, 0.8, brightness)
            display.pixel(int(self.x), int(self.y), color)

# Create particles
particles = [Particle() for _ in range(15)]

# ================= CLOCK FACE =================

def draw_clock_face():
    """Draw the static clock face elements"""
    # Outer ring
    for r in range(CLOCK_RADIUS - 2, CLOCK_RADIUS + 1):
        draw_circle(CENTER_X, CENTER_Y, r, st7789.color565(40, 40, 60))
    
    # Hour markers
    for i in range(12):
        angle = i * 30 - 90
        rad = math.radians(angle)
        
        # Outer point
        x1 = int(CENTER_X + (CLOCK_RADIUS - 5) * math.cos(rad))
        y1 = int(CENTER_Y + (CLOCK_RADIUS - 5) * math.sin(rad))
        
        # Inner point
        inner_len = CLOCK_RADIUS - 15 if i % 3 == 0 else CLOCK_RADIUS - 10
        x2 = int(CENTER_X + inner_len * math.cos(rad))
        y2 = int(CENTER_Y + inner_len * math.sin(rad))
        
        # Color: brighter for 12, 3, 6, 9
        color = st7789.WHITE if i % 3 == 0 else st7789.color565(100, 100, 120)
        display.line(x1, y1, x2, y2, color)
    
    # Center dot
    display.fill_rect(CENTER_X - 3, CENTER_Y - 3, 6, 6, st7789.WHITE)

# ================= ANIMATED CLOCK SCREEN =================

# State tracking for smooth animation
clock_state = {
    'last_sec': -1,
    'last_min': -1,
    'last_hour': -1,
    'hue': 0,
    'pulse': 0,
    'face_drawn': False
}

def screen_analog_clock():
    """Beautiful analog clock with smooth animations"""
    current_time = rtc.datetime()
    hour = current_time[4] % 12
    minute = current_time[5]
    second = current_time[6]
    
    # Draw clock face once
    if not clock_state['face_drawn']:
        display.fill(st7789.BLACK)
        draw_clock_face()
        clock_state['face_drawn'] = True
        clock_state['last_sec'] = -1
        clock_state['last_min'] = -1
        clock_state['last_hour'] = -1
    
    # Calculate angles
    sec_angle = second * 6
    min_angle = minute * 6 + second * 0.1
    hour_angle = hour * 30 + minute * 0.5
    
    # Erase old hands if changed
    if clock_state['last_sec'] != second:
        if clock_state['last_sec'] >= 0:
            old_sec_angle = clock_state['last_sec'] * 6
            erase_hand(old_sec_angle, CLOCK_RADIUS - 15, 1)
        clock_state['last_sec'] = second
    
    if clock_state['last_min'] != minute:
        if clock_state['last_min'] >= 0:
            old_min_angle = clock_state['last_min'] * 6 + clock_state['last_sec'] * 0.1
            erase_hand(old_min_angle, CLOCK_RADIUS - 25, 3)
        clock_state['last_min'] = minute
    
    if clock_state['last_hour'] != hour:
        if clock_state['last_hour'] >= 0:
            old_hour_angle = clock_state['last_hour'] * 30 + clock_state['last_min'] * 0.5
            erase_hand(old_hour_angle, CLOCK_RADIUS - 40, 4)
        clock_state['last_hour'] = hour
    
    # Draw hands (hour first, then minute, then second on top)
    draw_hand(hour_angle, CLOCK_RADIUS - 40, st7789.color565(200, 200, 255), 4)
    draw_hand(min_angle, CLOCK_RADIUS - 25, st7789.CYAN, 3)
    
    # Animated second hand color
    clock_state['hue'] = (clock_state['hue'] + 3) % 360
    sec_color = hsv_to_rgb565(clock_state['hue'], 1.0, 1.0)
    draw_hand(sec_angle, CLOCK_RADIUS - 15, sec_color, 1)
    
    # Redraw center dot
    display.fill_rect(CENTER_X - 3, CENTER_Y - 3, 6, 6, st7789.WHITE)
    
    # Digital time below analog clock with pulsing effect
    clock_state['pulse'] = (clock_state['pulse'] + 5) % 360
    pulse_brightness = 0.6 + 0.4 * math.sin(math.radians(clock_state['pulse']))
    time_color = hsv_to_rgb565(180, 0.5, pulse_brightness)
    
    time_str = "{:02d}:{:02d}".format(current_time[4], current_time[5])
    center_text(time_str, 195, time_color, st7789.BLACK)
    
    # Date at bottom
    day_name = DAYS[current_time[3]]
    month_name = MONTHS[current_time[1] - 1]
    date_str = "{} {} {}".format(day_name, current_time[2], month_name)
    # Truncate if too long
    if len(date_str) > 15:
        date_str = date_str[:15]
    center_text(date_str[:10], 225, st7789.color565(100, 100, 100), st7789.BLACK)

# ================= DIGITAL CLOCK WITH EFFECTS =================

digital_state = {
    'hue': 0,
    'particles_init': False,
    'last_sec': -1
}

def screen_digital_clock():
    """Fancy digital clock with particle effects"""
    current_time = rtc.datetime()
    second = current_time[6]
    
    # Initialize particles once
    if not digital_state['particles_init']:
        display.fill(st7789.BLACK)
        digital_state['particles_init'] = True
    
    # Update and draw particles
    for p in particles:
        p.draw(erase=True)
        p.update()
        p.draw()
    
    # Animated color for time
    digital_state['hue'] = (digital_state['hue'] + 2) % 360
    time_color = hsv_to_rgb565(digital_state['hue'], 1.0, 1.0)
    
    # Big time display
    time_str = "{:02d}:{:02d}:{:02d}".format(current_time[4], current_time[5], second)
    center_text(time_str, 90, time_color, st7789.BLACK)
    
    # Seconds indicator - animated arc
    if digital_state['last_sec'] != second:
        # Clear old arc segment
        if digital_state['last_sec'] >= 0:
            old_angle = digital_state['last_sec'] * 6 - 90
            rad = math.radians(old_angle)
            x = int(120 + 100 * math.cos(rad))
            y = int(120 + 100 * math.sin(rad))
            display.fill_rect(x - 3, y - 3, 6, 6, st7789.BLACK)
        digital_state['last_sec'] = second
    
    # Draw current second marker
    angle = second * 6 - 90
    rad = math.radians(angle)
    x = int(120 + 100 * math.cos(rad))
    y = int(120 + 100 * math.sin(rad))
    marker_color = hsv_to_rgb565((digital_state['hue'] + 180) % 360, 1.0, 1.0)
    display.fill_rect(x - 3, y - 3, 6, 6, marker_color)
    
    # Date display
    day_name = DAYS[current_time[3]]
    date_str = "{:04d}-{:02d}-{:02d}".format(current_time[0], current_time[1], current_time[2])
    center_text(day_name, 130, st7789.YELLOW, st7789.BLACK)
    center_text(date_str, 160, st7789.color565(100, 150, 200), st7789.BLACK)
    
    # Animated progress bar for seconds
    bar_y = 200
    bar_height = 8
    bar_width = int((second / 60) * 200)
    
    # Rainbow gradient bar
    display.fill_rect(20, bar_y, 200, bar_height, st7789.color565(30, 30, 30))
    if bar_width > 0:
        for i in range(bar_width):
            bar_hue = (digital_state['hue'] + i * 2) % 360
            color = hsv_to_rgb565(bar_hue, 1.0, 1.0)
            display.vline(20 + i, bar_y, bar_height, color)

# ================= MATRIX RAIN CLOCK =================

matrix_state = {
    'drops': [],
    'init': False
}

def screen_matrix_clock():
    """Matrix-style rain with clock overlay"""
    current_time = rtc.datetime()
    
    if not matrix_state['init']:
        display.fill(st7789.BLACK)
        # Initialize rain drops
        matrix_state['drops'] = []
        for i in range(15):
            matrix_state['drops'].append({
                'x': random.randint(0, 14) * 16,
                'y': random.randint(-240, 0),
                'speed': random.randint(3, 8),
                'char': chr(random.randint(33, 126))
            })
        matrix_state['init'] = True
    
    # Update rain drops
    for drop in matrix_state['drops']:
        # Erase old position
        display.fill_rect(drop['x'], drop['y'], 16, 32, st7789.BLACK)
        
        # Update position
        drop['y'] += drop['speed']
        
        # Reset if off screen
        if drop['y'] > 240:
            drop['y'] = random.randint(-60, -10)
            drop['x'] = random.randint(0, 14) * 16
            drop['char'] = chr(random.randint(33, 126))
        
        # Draw character with fade effect
        brightness = max(0, min(255, 255 - abs(drop['y'] - 120)))
        color = st7789.color565(0, brightness, 0)
        display.text(font, drop['char'], drop['x'], drop['y'], color, st7789.BLACK)
    
    # Draw time in center with glow effect
    time_str = "{:02d}:{:02d}:{:02d}".format(current_time[4], current_time[5], current_time[6])
    
    # Dark background box for readability
    display.fill_rect(20, 85, 200, 40, st7789.color565(0, 20, 0))
    center_text(time_str, 90, st7789.color565(0, 255, 0), st7789.color565(0, 20, 0))
    
    # Date
    date_str = "{:02d}/{:02d}/{:04d}".format(current_time[1], current_time[2], current_time[0])
    display.fill_rect(40, 130, 160, 35, st7789.color565(0, 15, 0))
    center_text(date_str, 135, st7789.color565(0, 180, 0), st7789.color565(0, 15, 0))

# ================= MAIN LOOP =================

last_switch = time.time()
current_screen = 0
NUM_SCREENS = 3

print("Starting Amazing Clock UI...")
print("Screens: Analog Clock -> Digital Clock -> Matrix Clock")
print("Auto-switches every 15 seconds")

while True:
    now = time.time()
    
    # Switch screens every 15 seconds
    if now - last_switch > 15:
        current_screen = (current_screen + 1) % NUM_SCREENS
        last_switch = now
        # Reset states
        clock_state['face_drawn'] = False
        digital_state['particles_init'] = False
        matrix_state['init'] = False
        display.fill(st7789.BLACK)

    if current_screen == 0:
        screen_analog_clock()
        time.sleep(0.05)
    elif current_screen == 1:
        screen_digital_clock()
        time.sleep(0.03)
    else:
        screen_matrix_clock()
        time.sleep(0.05)