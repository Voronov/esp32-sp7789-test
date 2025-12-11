"""
MPU6050 Menu-Based Example
Interactive menu for reading sensor data with wake/sleep cycle
"""

from machine import I2C, Pin
import time
from mpu6050.driver import MPU6050Device, MPU6050Sensor


class MPU6050Menu:
    """
    Text menu interface for MPU6050 sensor.
    Manages wake/sleep cycles for each operation.
    """
    
    def __init__(self, sensor: MPU6050Sensor):
        """
        Initialize menu with sensor instance.
        
        Args:
            sensor: MPU6050Sensor instance
        """
        self.sensor = sensor
    
    def display_menu(self):
        """Display the main menu"""
        print("\n" + "=" * 40)
        print("MPU6050 SENSOR MENU")
        print("=" * 40)
        print("1) Get Temperature")
        print("2) Get All Data")
        print("3) Get 100 Readings")
        print("4) Exit")
        print("=" * 40)
    
    def get_temperature(self):
        """Read and display temperature with wake/sleep cycle"""
        print("\n--- Temperature Reading ---")
        self.sensor.activate()
        
        temp = self.sensor.get_temperature()
        print(f"Temperature: {temp}°C")
        
        self.sensor.deactivate()
        print("Sensor put to sleep\n")
    
    def get_all_data(self):
        """Read and display all sensor data with wake/sleep cycle"""
        print("\n--- All Sensor Data ---")
        self.sensor.activate()
        
        data = self.sensor.get_all_data()
        
        print(f"Temperature: {data['temperature']}°C")
        print(f"Acceleration (g):")
        print(f"  X: {data['acceleration']['x']:7.3f}")
        print(f"  Y: {data['acceleration']['y']:7.3f}")
        print(f"  Z: {data['acceleration']['z']:7.3f}")
        print(f"Gyroscope (°/s):")
        print(f"  X: {data['gyroscope']['x']:7.2f}")
        print(f"  Y: {data['gyroscope']['y']:7.2f}")
        print(f"  Z: {data['gyroscope']['z']:7.2f}")
        
        self.sensor.deactivate()
        print("Sensor put to sleep\n")
    
    def get_100_readings(self):
        """Read and display 100 temperature readings with wake/sleep cycle"""
        print("\n--- 100 Temperature Readings ---")
        self.sensor.activate()
        
        print("Reading...", end="")
        temps = []
        for i in range(100):
            temp = self.sensor.get_temperature()
            temps.append(temp)
            if (i + 1) % 20 == 0:
                print(f" {i + 1}", end="")
        
        print("\n")
        avg_temp = sum(temps) / len(temps)
        min_temp = min(temps)
        max_temp = max(temps)
        
        print(f"Statistics:")
        print(f"  Average: {avg_temp:.2f}°C")
        print(f"  Minimum: {min_temp:.2f}°C")
        print(f"  Maximum: {max_temp:.2f}°C")
        print(f"  Range:   {max_temp - min_temp:.2f}°C")
        
        self.sensor.deactivate()
        print("Sensor put to sleep\n")
    
    def run(self):
        """Run the interactive menu loop"""
        print("\nMPU6050 Interactive Menu")
        print("Sensor will wake up for each operation")
        
        while True:
            self.display_menu()
            
            try:
                choice = input("Select option (1-4): ").strip()
                
                if choice == '1':
                    self.get_temperature()
                elif choice == '2':
                    self.get_all_data()
                elif choice == '3':
                    self.get_100_readings()
                elif choice == '4':
                    print("\nExiting... Goodbye!")
                    break
                else:
                    print("\nInvalid option. Please select 1-4.")
                
            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Exiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")
                self.sensor.deactivate()


if __name__ == '__main__':
    print("Initializing MPU6050...")
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
            menu = MPU6050Menu(sensor)
            menu.run()
            
    except Exception as e:
        print(f"\nFatal error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check I2C wiring (SCL=GPIO17, SDA=GPIO18)")
        print("  2. Verify 3.3V power supply")
        print("  3. Run 'mpu6050/i2c_scanner.py' for diagnostics")
