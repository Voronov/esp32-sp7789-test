"""MPU6050 temperature sensor driver for MicroPython"""
import machine
import time


class MPU6050Config:
    """MPU6050 register addresses and configuration constants"""
    
    # I2C Address
    MPU6050_ADDR = 0x68  # Default address when AD0
    
    # Register Map
    # Temperature measurement
    REG_TEMP_OUT_H = 0x41
    REG_PWR_MGMT_1 = 0x6B
    REG_FIFO_R_W = 0x74
    REG_WHO_AM_I = 0x75
    
    # Power Management
    PWR_CLKSEL_PLL_X = 0x01


class Device:
    """Abstract base class for I2C devices.
    
    Defines the interface that all device implementations must follow.
    Subclasses should implement I2C communication methods and device initialization.
    
    Attributes:
        i2c: I2C bus instance for communication
        address: I2C device address
        config: Device configuration object containing register addresses and constants
    """
    
    def __init__(self, i2c, address, config):
        """Initialize device with I2C bus, address, and configuration.
        
        Args:
            i2c: I2C bus instance
            address: I2C device address
            config: Configuration object for the device
        """
        self.i2c = i2c
        self.address = address
        self.config = config
    
    def initialize(self):
        """Initialize the device. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement initialize()")
    
    def read(self, reg, length=1):
        """Read data from device register. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement read()")
    
    def write(self, reg, data):
        """Write data to device register. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement write()")


class Controller:
    """Abstract base class for device controllers.
    
    Controllers provide high-level interfaces to interact with devices.
    They handle data conversion and provide user-friendly methods.
    Subclasses should implement methods to get processed sensor data.
    """
    
    def __init__(self, device):
        """Initialize controller with a device instance."""
        raise NotImplementedError("Subclasses must implement __init__()")
    
    def read_register(self, reg):
        """Read a single byte from register."""
        raise NotImplementedError("Subclasses must implement read_register()")
    
    def write_register(self, reg, value):
        """Write a single byte to register."""
        raise NotImplementedError("Subclasses must implement write_register()")


class MPU6050(Device):
    """Class representing the MPU6050 device with I2C communication."""
    
    def __init__(self, i2c, address=MPU6050Config.MPU6050_ADDR):
        """Initialize MPU6050 device
        
        Args:
            i2c: I2C bus instance
            address: I2C address (0x68 or 0x69)
        """
        # Call parent constructor with config
        super().__init__(i2c, address, MPU6050Config())
        
        # Initialize sensor
        self.initialize()
    
    def initialize(self):
        """Initialize the MPU6050 sensor"""
        try:
            # Check device ID
            who_am_i = self.read_register(self.config.REG_WHO_AM_I)
            if who_am_i not in [0x68, 0x69]:
                print(f"MPU6050 not found. WHO_AM_I: 0x{who_am_i:02X}")
                return False
            
            # Wake up the device (clear sleep bit)
            self.write_register(self.config.REG_PWR_MGMT_1, self.config.PWR_CLKSEL_PLL_X)
            time.sleep_ms(100)
            
            return True
        except Exception as e:
            print(f"MPU6050 initialization failed: {e}")
            return False
    
    def read_register(self, reg):
        """Read a single byte from register"""
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]
    
    def write_register(self, reg, value):
        """Write a single byte to register"""
        self.i2c.writeto_mem(self.address, reg, bytes([value]))
    
    def read_registers(self, reg, length):
        """Read multiple bytes from register"""
        return self.i2c.readfrom_mem(self.address, reg, length)
    
    def read(self, reg, length=1):
        """Reads data from the MPU6050 device.
        
        Args:
            reg: Register address to read from
            length: Number of bytes to read
            
        Returns:
            bytes: Data read from the device
        """
        return self.read_registers(reg, length)
    
    def write(self, reg, data):
        """Writes data to the MPU6050 device.
        
        Args:
            reg: Register address to write to
            data: Data bytes to write
        """
        if isinstance(data, int):
            self.write_register(reg, data)
        else:
            self.i2c.writeto_mem(self.address, reg, data)
    
    def read_raw_temp(self):
        """Read raw temperature data
        
        Returns:
            Raw temperature value (16-bit signed)
        """
        data = self.read_registers(self.config.REG_TEMP_OUT_H, 2)
        return self._bytes_to_int16(data[0], data[1])
    
    def _bytes_to_int16(self, high, low):
        """Convert two bytes to signed 16-bit integer"""
        value = (high << 8) | low
        # Convert to signed
        if value >= 0x8000:
            value = -((65535 - value) + 1)
        return value


class MPU6050Controller(Controller):
    """Controller for MPU6050 temperature sensor.
    
    Provides high-level methods to read temperature data from the MPU6050.
    """
    
    def __init__(self, device):
        """Initialize controller with MPU6050 device
        
        Args:
            device: MPU6050 device instance
        """
        self.device = device
    
    def get_temperature(self):
        """Gets the temperature from the MPU6050 device in Celsius.
        
        Returns:
            Temperature in degrees Celsius
        """
        raw_temp = self.device.read_raw_temp()
        # Temperature formula from datasheet: Temp = (TEMP_OUT / 340) + 36.53
        return (raw_temp / 340.0) + 36.53


# Example usage
if __name__ == '__main__':
    # Initialize I2C (adjust pins for your ESP32)
    # Using GPIO 26 (SCL) and GPIO 25 (SDA) - common alternative I2C pins
    # If these don't work, try: GPIO 22 (SCL) and GPIO 21 (SDA)
    i2c = machine.I2C(0, scl=machine.Pin(17), sda=machine.Pin(18), freq=400000)
    
    # Create MPU6050 device
    mpu = MPU6050(i2c)
    
    # Create controller
    controller = MPU6050Controller(mpu)
    
    # Read data
    print("MPU6050 Temperature Sensor Test")
    print("=" * 40)
    
    while True:
        try:
            # Get temperature
            temp = controller.get_temperature()
            
            print(f"Temperature: {temp:.2f}°C")
            print("-" * 40)
            
            time.sleep_ms(500)
            
        except KeyboardInterrupt:
            print("\nStopped by user")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)