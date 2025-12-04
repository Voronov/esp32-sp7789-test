import machine
import time
import struct


# Pin Configuration
SCK_PIN  = 18
MOSI_PIN = 23
DC_PIN   = 2
RESET_PIN = 4

# Color Constants (RGB565)
BLACK = 0x0000
BLUE  = 0x001F
RED   = 0xF800
GREEN = 0x07E0
WHITE = 0xFFFF

class SimpleST7789:
  
    # ST7789 Command Register Addresses
    CMD_SWRESET = b"\x01" # Software Reset
    CMD_SLPOUT  = b"\x11" # Sleep Out
    CMD_COLMOD  = b"\x3a" # Interface Pixel Format
    CMD_MADCTL  = b"\x36" # Memory Data Access Control
    CMD_INVON   = b"\x21" # Display Inversion On
    CMD_DISPON  = b"\x29" # Display On
    CMD_CASET   = b"\x2a" # Column Address Set
    CMD_RASET   = b"\x2b" # Row Address Set
    CMD_RAMWR   = b"\x2c" # Memory Write

    def __init__(self, width=240, height=240):
        self.width = width
        self.height = height
        
        # Initialize Hardware
        self.dc = machine.Pin(DC_PIN, machine.Pin.OUT)
        self.reset = machine.Pin(RESET_PIN, machine.Pin.OUT)
        self.spi = machine.SPI(2, baudrate=40000000, polarity=1, phase=1, 
                               sck=machine.Pin(SCK_PIN), mosi=machine.Pin(MOSI_PIN))
        
        self._init_display()

    def _write_cmd(self, cmd):
        self.dc.off()
        self.spi.write(cmd)

    def _write_data(self, data):
        self.dc.on()
        self.spi.write(data)

    def _init_display(self):
        """Initialize the display with a standard startup sequence."""
        # Hardware Reset
        self.reset.on()
        time.sleep_ms(50)
        self.reset.off()
        time.sleep_ms(50)
        self.reset.on()
        time.sleep_ms(150)

        # Initialization Sequence
        commands = [
            (self.CMD_SWRESET, None, 150),                # 1. Software Reset
            (self.CMD_SLPOUT,  None, 255),                # 2. Sleep Out
            (self.CMD_COLMOD,  b"\x55", 10),              # 3. 16-bit Color
            (self.CMD_MADCTL,  b"\x00", 0),               # 4. RGB Order
            (self.CMD_INVON,   None, 0),                  # 5. Inversion On
            (self.CMD_DISPON,  None, 255),                # 6. Display On
        ]

        for cmd, data, delay in commands:
            self._write_cmd(cmd)
            if data:
                self._write_data(data)
            if delay:
                time.sleep_ms(delay)

    def set_window(self, x, y, w, h):
        """Set the drawing window on the display."""
        # Column Address Set
        self._write_cmd(self.CMD_CASET)
        self._write_data(struct.pack(">HH", x, x + w - 1))
        
        # Row Address Set
        self._write_cmd(self.CMD_RASET)
        self._write_data(struct.pack(">HH", y, y + h - 1))
        
        # Prepare to write to RAM
        self._write_cmd(self.CMD_RAMWR)

    def fill_rect(self, x, y, w, h, color):
        """Fill a rectangle with a single color."""
        # Clip to screen boundaries
        if x >= self.width or y >= self.height: return
        w = min(w, self.width - x)
        h = min(h, self.height - y)
        
        self.set_window(x, y, w, h)
        
        # Create a chunk of data (one full row of color)
        color_bytes = struct.pack(">H", color)
        chunk = color_bytes * w
        
        self.dc.on()
        for _ in range(h):
            self.spi.write(chunk)

    def fill(self, color):
        """Fill the entire screen."""
        self.fill_rect(0, 0, self.width, self.height, color)

def run():
    print("Starting Simple SPI Test...")
    display = SimpleST7789()
    
    colors = [RED, GREEN, BLUE, BLACK]
    
    print("Cycle Colors...")
    for color in colors:
        display.fill(color)
        time.sleep(0.5)
        
    print("Drawing Patterns...")
    # Draw a simple pattern
    rect_size = 20
    for i in range(10):
        x = 20 + i * 15
        y = 20 + i * 15
        display.fill_rect(x, y, rect_size, rect_size, WHITE)
        
    print("Test Complete.")

if __name__ == "__main__":
    run()
