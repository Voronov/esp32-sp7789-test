"""
I2C Scanner Utility
Scans I2C bus and helps diagnose connection issues
"""

from machine import I2C, Pin

def scan_i2c(scl=17, sda=18, freq=400000):
    """
    Scan I2C bus for connected devices.
    
    Args:
        scl: SCL pin number (default 17)
        sda: SDA pin number (default 18)
        freq: I2C frequency in Hz (default 400000)
    
    Returns:
        List of detected I2C addresses
    """
    print("=" * 50)
    print(f"I2C Scanner")
    print(f"SCL: GPIO{scl}, SDA: GPIO{sda}, Freq: {freq}Hz")
    print("=" * 50)
    
    try:
        i2c = I2C(0, scl=Pin(scl), sda=Pin(sda), freq=freq)
        print("I2C bus initialized")
        
        print("\nScanning...")
        devices = i2c.scan()
        
        if not devices:
            print("\nNo I2C devices found!")
            print("\nTroubleshooting:")
            print("  1. Check wiring connections")
            print("  2. Verify power supply (3.3V)")
            print("  3. Check if SCL and SDA are correct")
            print("  4. Try pull-up resistors (4.7kΩ)")
            return []
        
        print(f"\nFound {len(devices)} device(s):\n")
        for addr in devices:
            device_name = identify_device(addr)
            print(f"  0x{addr:02X} ({addr:3d}) - {device_name}")
        
        return devices
        
    except Exception as e:
        print(f"\nError: {e}")
        return []


def identify_device(addr):
    """Identify common I2C devices by address"""
    devices = {
        0x68: "MPU6050 (or DS1307 RTC)",
        0x69: "MPU6050 (alternate address)",
        0x76: "BMP280/BME280",
        0x77: "BMP180/BMP280/BME280",
        0x57: "MAX30100",
        0x3C: "OLED Display (128x64)",
        0x3D: "OLED Display (128x64)",
        0x48: "ADS1115",
        0x50: "EEPROM",
    }
    return devices.get(addr, "Unknown device")


if __name__ == '__main__':
    scan_i2c()
