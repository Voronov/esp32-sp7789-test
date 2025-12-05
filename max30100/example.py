"""Example usage of the interface-based sensor implementation with Display"""
import machine
import time
import st7789
import vga2_bold_16x32 as font

try:
    from max30100.comm import MAX30100Communication
    from max30100.device import MAX30100
except ImportError as e:
    print(f"Import Error (max30100 package): {e}")
    try:
        from .comm import MAX30100Communication
        from .device import MAX30100
    except ImportError:
        try:
            from comm import MAX30100Communication
            from device import MAX30100
        except ImportError:
            # Final attempt: maybe we are in max30100 folder?
            # But mpremote run executes in root usually.
            raise

def init_display():
    """Initialize the ST7789 Display"""
    print("Initializing display...")
    # SPI Setup matching sp7789_test.py
    spi = machine.SPI(2, baudrate=20000000, polarity=1, phase=1, 
                      sck=machine.Pin(5), mosi=machine.Pin(4))
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
    """Example usage of the interface-based sensor implementation"""
    
    # Initialize Display
    display = init_display()
    display.text(font, "MAX30100 Demo", 10, 10, st7789.YELLOW)
    display.text(font, "Initializing...", 10, 50, st7789.WHITE)
    
    # Initialize I2C bus
    i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21), freq=400000)
    
    print('Scanning I2C bus...')
    devices = i2c.scan()
    print(f'Found devices: {[hex(d) for d in devices]}')
    
    # Create communication layer
    comm = MAX30100Communication(i2c)
    
    # Create sensor instance
    sensor = MAX30100(comm)
    
    # Check device info
    if comm.check_connection():
        print('\n=== Device Information ===')
        info = sensor.get_device_info()
        for key, value in info.items():
            print(f'{key}: {value}')
        
        # Initialize sensor
        print('\n=== Initializing Sensor ===')
        if sensor.initialize():
            print('Sensor initialized successfully!')
            display.fill(st7789.BLACK)
            display.text(font, "Sensor Ready", 10, 10, st7789.GREEN)
            time.sleep(1)
            display.fill(st7789.BLACK)
            
            # Custom configuration
            sensor.configure(
                mode='spo2',
                sample_rate=100,
                led_current='high'
            )
            
            # Read data continuously
            print('\n=== Reading Data ===')
            print('Collecting samples... (place finger on sensor)')
            
            display.text(font, "Place Finger", 10, 100, st7789.CYAN)
            
            last_update = 0
            
            while True:
                if sensor.is_ready():
                    data = sensor.read_processed_data()
                    
                    # Print to console occasionally
                    print(f"IR={data['ir_raw']:5d}, Red={data['red_raw']:5d}, "
                          f"HR={data['heart_rate']:3d}, SpO2={data['spo2']:5.1f}%")
                    
                    # Update display every 200ms to avoid flicker
                    now = time.ticks_ms()
                    if time.ticks_diff(now, last_update) > 200:
                        # Clear previous values (simple block clear)
                        display.fill_rect(0, 0, 240, 240, st7789.BLACK)
                        
                        display.text(font, "MAX30100", 40, 10, st7789.YELLOW)
                        
                        # HR
                        hr = data['heart_rate']
                        color = st7789.GREEN if hr > 0 else st7789.RED
                        display.text(font, f"HR: {hr} BPM", 10, 60, color)
                        
                        # SpO2
                        spo2 = data['spo2']
                        display.text(font, f"SpO2: {spo2}%", 10, 100, st7789.WHITE)
                        
                        # Raw
                        display.text(font, f"IR: {data['ir_raw']}", 10, 150, st7789.BLUE)
                        
                        # Temp
                        temp = sensor.read_temperature()
                        if temp:
                            display.text(font, f"Temp: {temp}C", 10, 190, st7789.MAGENTA)
                        
                        last_update = now
                
                time.sleep_ms(10)
        
        else:
            print('Failed to initialize sensor!')
            display.text(font, "Init Failed!", 10, 100, st7789.RED)
    else:
        print('MAX30100 not found!')
        display.text(font, "Sensor Missing!", 10, 100, st7789.RED)


if __name__ == '__main__':
    main()
