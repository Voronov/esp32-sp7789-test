"""Example usage of the interface-based sensor implementation"""
import machine
import time

try:
    from .comm import MAX30100Communication
    from .device import MAX30100
except ImportError:
    from comm import MAX30100Communication
    from device import MAX30100

def main():
    """Example usage of the interface-based sensor implementation"""
    
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
            
            # Custom configuration
            sensor.configure(
                mode='spo2',
                sample_rate=100,
                led_current='high'
            )
            
            print(f'Sample rate: {sensor.get_sample_rate()} Hz')
            
            # Read status
            print('\n=== Sensor Status ===')
            status = sensor.get_status()
            for key, value in status.items():
                print(f'{key}: {value}')
            
            # Read data continuously
            print('\n=== Reading Data ===')
            print('Collecting samples... (place finger on sensor)')
            
            for i in range(50):
                if sensor.is_ready():
                    data = sensor.read_processed_data()
                    
                    print(f"Sample {i:3d}: "
                          f"IR={data['ir_raw']:5d}, "
                          f"Red={data['red_raw']:5d}, "
                          f"HR={data['heart_rate']:3d} BPM, "
                          f"SpO2={data['spo2']:5.1f}%")
                
                time.sleep_ms(50)
            
            # Read temperature
            print('\n=== Temperature ===')
            temp = sensor.read_temperature()
            if temp:
                print(f'Temperature: {temp}°C')
        
        else:
            print('Failed to initialize sensor!')
    else:
        print('MAX30100 not found!')


if __name__ == '__main__':
    main()
