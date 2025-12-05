"""Example usage of HC-SR04 Ultrasonic Sensor with ST7789 Display"""
import machine
import time
import st7789
import vga2_bold_16x32 as font

try:
    from hcsr04.driver import HCSR04
except ImportError:
    try:
        from .driver import HCSR04
    except ImportError:
        from driver import HCSR04


def init_display():
    """Initialize the ST7789 Display"""
    print("Initializing display...")
    spi = machine.SPI(2, baudrate=20000000, polarity=1, phase=1,
                      sck=machine.Pin(18), mosi=machine.Pin(23))
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
    return display


def main():
    """Main example demonstrating HC-SR04 sensor readings"""
    
    # Initialize Display
    display = init_display()
    display.text(font, "HC-SR04 Demo", 10, 10, st7789.YELLOW)
    display.text(font, "Initializing...", 10, 50, st7789.WHITE)
    
    # Initialize HC-SR04
    # Using GPIO pins that don't conflict with display
    # Display uses: GPIO 18 (SCK), 23 (MOSI), 2 (DC), 4 (RST)
    # Available pins: 5, 12, 13, 14, 15, 16, 17, 19, 25, 26, 27, 32, 33
    TRIGGER_PIN = 12
    ECHO_PIN = 14
    
    print(f"Initializing HC-SR04 on Trigger={TRIGGER_PIN}, Echo={ECHO_PIN}")
    sensor = HCSR04(trigger_pin=TRIGGER_PIN, echo_pin=ECHO_PIN)
    
    time.sleep(1)
    display.fill(st7789.BLACK)
    display.text(font, "Sensor Ready", 10, 10, st7789.GREEN)
    time.sleep(1)
    
    print("\n=== Starting Distance Measurements ===")
    print("Format: Distance (cm) | Distance (mm) | Distance (in)")
    
    last_update = 0
    reading_count = 0
    
    while True:
        # Read distance
        distance_cm = sensor.read_distance_cm()
        
        if distance_cm > 0:
            distance_mm = sensor.read_distance_mm()
            distance_in = sensor.read_distance_inches()
            
            # Print to console
            print(f"{distance_cm:6.2f} cm | {distance_mm:7.1f} mm | {distance_in:6.2f} in")
            
            # Update display every 200ms
            now = time.ticks_ms()
            if time.ticks_diff(now, last_update) > 200:
                display.fill(st7789.BLACK)
                
                # Title
                display.text(font, "HC-SR04", 50, 10, st7789.YELLOW)
                
                # Distance in CM (main reading)
                color = st7789.GREEN if distance_cm < 50 else st7789.WHITE
                if distance_cm < 10:
                    color = st7789.RED
                
                display.text(font, f"{distance_cm:.1f} cm", 30, 60, color)
                
                # Distance in MM
                display.text(font, f"{distance_mm:.0f} mm", 30, 110, st7789.CYAN)
                
                # Distance in Inches
                display.text(font, f"{distance_in:.1f} in", 30, 160, st7789.MAGENTA)
                
                # Reading counter
                reading_count += 1
                display.text(font, f"#{reading_count}", 10, 210, st7789.BLUE)
                
                last_update = now
        else:
            print("Error: Timeout or out of range")
            display.fill_rect(0, 60, 240, 32, st7789.BLACK)
            display.text(font, "OUT OF RANGE", 10, 60, st7789.RED)
        
        # Wait between readings (HC-SR04 needs ~60ms between measurements)
        time.sleep_ms(100)


def example_statistics():
    """Example showing statistical analysis of multiple readings"""
    print("\n=== Statistical Analysis Example ===")
    
    TRIGGER_PIN = 5
    ECHO_PIN = 18
    sensor = HCSR04(trigger_pin=TRIGGER_PIN, echo_pin=ECHO_PIN)
    
    print("Taking 10 samples...")
    stats = sensor.read_multiple(samples=10)
    
    print(f"\nStatistics from {stats['count']} valid readings:")
    print(f"  Minimum:  {stats['min']:.2f} cm")
    print(f"  Maximum:  {stats['max']:.2f} cm")
    print(f"  Average:  {stats['avg']:.2f} cm")
    print(f"  Median:   {stats['median']:.2f} cm")


def example_object_detection():
    """Example showing object detection within threshold"""
    print("\n=== Object Detection Example ===")
    
    TRIGGER_PIN = 5
    ECHO_PIN = 18
    sensor = HCSR04(trigger_pin=TRIGGER_PIN, echo_pin=ECHO_PIN)
    
    THRESHOLD = 30  # cm
    print(f"Detecting objects within {THRESHOLD} cm...")
    
    while True:
        if sensor.is_object_detected(threshold_cm=THRESHOLD):
            distance = sensor.read_distance_cm()
            print(f"⚠️  OBJECT DETECTED at {distance:.2f} cm!")
        else:
            print("No object detected")
        
        time.sleep_ms(200)


if __name__ == '__main__':
    # Run main example with display
    main()
    
    # Uncomment to run other examples:
    # example_statistics()
    # example_object_detection()
