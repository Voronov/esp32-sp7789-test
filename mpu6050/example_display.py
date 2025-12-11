"""
MPU6050 Continuous Display Example for ST7789
Continuously displays sensor data on ST7789 TFT display
"""

from machine import I2C, Pin, SPI
import time
import sys
sys.path.insert(0, '/')
from st7789 import ST7789, color565
from mpu6050.driver import MPU6050Device, MPU6050Sensor


class MPU6050Display:
    """
    Continuous display interface for MPU6050 sensor on ST7789.
    Shows real-time sensor data with color-coded sections.
    """
    
    COLOR_BG = color565(0, 0, 0)
    COLOR_TITLE = color565(255, 255, 255)
    COLOR_LABEL = color565(100, 200, 255)
    COLOR_VALUE = color565(255, 255, 0)
    COLOR_TEMP = color565(255, 100, 100)
    COLOR_ACCEL = color565(100, 255, 100)
    COLOR_GYRO = color565(150, 150, 255)
    
    def __init__(self, display: ST7789, sensor: MPU6050Sensor):
        """
        Initialize display interface.
        
        Args:
            display: ST7789 display instance
            sensor: MPU6050Sensor instance
        """
        self.display = display
        self.sensor = sensor
        self.width = display.width
        self.height = display.height
    
    def clear_screen(self):
        """Clear the display"""
        self.display.fill(self.COLOR_BG)
    
    def draw_header(self):
        """Draw the header section"""
        self.display.fill_rect(0, 0, self.width, 30, color565(20, 20, 60))
        
        title = "MPU6050 SENSOR"
        title_width = len(title) * 8
        x = (self.width - title_width) // 2
        self.display.text(None, title, x, 8, self.COLOR_TITLE, color565(20, 20, 60))
    
    def draw_temperature(self, y_pos: int, temp: float):
        """
        Draw temperature section.
        
        Args:
            y_pos: Y position to start drawing
            temp: Temperature value in °C
        """
        self.display.fill_rect(0, y_pos, self.width, 50, color565(40, 20, 20))
        
        self.display.text(None, "TEMPERATURE", 10, y_pos + 8, self.COLOR_TEMP, color565(40, 20, 20))
        
        temp_str = f"{temp:.2f} C"
        self.display.text(None, temp_str, 10, y_pos + 28, self.COLOR_VALUE, color565(40, 20, 20))
    
    def draw_acceleration(self, y_pos: int, accel: dict):
        """
        Draw acceleration section.
        
        Args:
            y_pos: Y position to start drawing
            accel: Acceleration dict with x, y, z keys
        """
        self.display.fill_rect(0, y_pos, self.width, 70, color565(20, 40, 20))
        
        self.display.text(None, "ACCELERATION (g)", 10, y_pos + 8, self.COLOR_ACCEL, color565(20, 40, 20))
        
        x_str = f"X: {accel['x']:7.3f}"
        y_str = f"Y: {accel['y']:7.3f}"
        z_str = f"Z: {accel['z']:7.3f}"
        
        self.display.text(None, x_str, 10, y_pos + 24, self.COLOR_VALUE, color565(20, 40, 20))
        self.display.text(None, y_str, 10, y_pos + 40, self.COLOR_VALUE, color565(20, 40, 20))
        self.display.text(None, z_str, 10, y_pos + 56, self.COLOR_VALUE, color565(20, 40, 20))
    
    def draw_gyroscope(self, y_pos: int, gyro: dict):
        """
        Draw gyroscope section.
        
        Args:
            y_pos: Y position to start drawing
            gyro: Gyroscope dict with x, y, z keys
        """
        self.display.fill_rect(0, y_pos, self.width, 70, color565(20, 20, 40))
        
        self.display.text(None, "GYROSCOPE (deg/s)", 10, y_pos + 8, self.COLOR_GYRO, color565(20, 20, 40))
        
        x_str = f"X: {gyro['x']:7.2f}"
        y_str = f"Y: {gyro['y']:7.2f}"
        z_str = f"Z: {gyro['z']:7.2f}"
        
        self.display.text(None, x_str, 10, y_pos + 24, self.COLOR_VALUE, color565(20, 20, 40))
        self.display.text(None, y_str, 10, y_pos + 40, self.COLOR_VALUE, color565(20, 20, 40))
        self.display.text(None, z_str, 10, y_pos + 56, self.COLOR_VALUE, color565(20, 20, 40))
    
    def draw_footer(self, y_pos: int, update_count: int):
        """
        Draw footer with update counter.
        
        Args:
            y_pos: Y position to start drawing
            update_count: Number of updates performed
        """
        self.display.fill_rect(0, y_pos, self.width, 20, color565(30, 30, 30))
        
        counter_str = f"Updates: {update_count}"
        self.display.text(None, counter_str, 10, y_pos + 6, self.COLOR_LABEL, color565(30, 30, 30))
    
    def update_display(self, data: dict, update_count: int):
        """
        Update the entire display with new sensor data.
        
        Args:
            data: Sensor data dict with temperature, acceleration, gyroscope
            update_count: Number of updates performed
        """
        y = 35
        
        self.draw_temperature(y, data['temperature'])
        y += 55
        
        self.draw_acceleration(y, data['acceleration'])
        y += 75
        
        self.draw_gyroscope(y, data['gyroscope'])
        y += 75
        
        self.draw_footer(y, update_count)
    
    def run(self, update_interval_ms: int = 500):
        """
        Run continuous display loop.
        
        Args:
            update_interval_ms: Update interval in milliseconds
        """
        print("Starting continuous display...")
        print("Press Ctrl+C to stop")
        
        self.clear_screen()
        self.draw_header()
        
        self.sensor.activate()
        
        update_count = 0
        
        try:
            while True:
                data = self.sensor.get_all_data()
                
                self.update_display(data, update_count)
                
                update_count += 1
                time.sleep_ms(update_interval_ms)
                
        except KeyboardInterrupt:
            print("\nStopping display...")
            self.sensor.deactivate()
            self.clear_screen()
            
            msg = "STOPPED"
            msg_width = len(msg) * 8
            x = (self.width - msg_width) // 2
            y = self.height // 2
            self.display.text(None, msg, x, y, self.COLOR_TITLE, self.COLOR_BG)
            
            print("Display stopped")


def init_display():
    """
    Initialize ST7789 display.
    Adjust pins according to your hardware setup.
    
    Returns:
        ST7789 display instance
    """
    spi = SPI(1, baudrate=40000000, polarity=1, phase=1, sck=Pin(14), mosi=Pin(13))
    
    display = ST7789(
        spi,
        width=240,
        height=240,
        reset=Pin(23, Pin.OUT),
        dc=Pin(16, Pin.OUT),
        cs=Pin(15, Pin.OUT),
        backlight=Pin(4, Pin.OUT),
        rotation=0
    )
    
    return display


if __name__ == '__main__':
    print("Initializing MPU6050 and ST7789...")
    print("Scanning I2C bus...\n")
    
    try:
        i2c = I2C(0, scl=Pin(17), sda=Pin(18), freq=400000)
        devices = i2c.scan()
        
        if devices:
            print(f"Found {len(devices)} I2C device(s): ", end="")
            print(", ".join([f"0x{d:02X}" for d in devices]))
            print()
        else:
            print("WARNING: No I2C devices found!")
            print("Please check your wiring and connections.\n")
        
        device = MPU6050Device(i2c, strict=False)
        
        if not device.connected:
            print("\nCannot proceed without sensor connection.")
            print("Run 'mpu6050/i2c_scanner.py' for detailed diagnostics.")
        else:
            sensor = MPU6050Sensor(device)
            display = init_display()
            
            mpu_display = MPU6050Display(display, sensor)
            mpu_display.run(update_interval_ms=500)
            
    except Exception as e:
        print(f"\nFatal error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check I2C wiring (SCL=GPIO17, SDA=GPIO18)")
        print("  2. Check SPI wiring for ST7789 display")
        print("  3. Verify 3.3V power supply")
        print("  4. Run 'mpu6050/i2c_scanner.py' for diagnostics")
