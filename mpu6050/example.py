"""MPU6050 6-axis accelerometer and gyroscope sensor driver for MicroPython"""
import machine
import time


class MPU6050Config:
    """MPU6050 register addresses and configuration constants"""
    
    # I2C Address
    MPU6050_ADDR = 0x68  # Default address when AD0 is low
    MPU6050_ADDR_ALT = 0x69  # Alternative address when AD0 is high
    
    # Register Map
    REG_SELF_TEST_X = 0x0D
    REG_SELF_TEST_Y = 0x0E
    REG_SELF_TEST_Z = 0x0F
    REG_SELF_TEST_A = 0x10
    
    REG_SMPLRT_DIV = 0x19
    REG_CONFIG = 0x1A
    REG_GYRO_CONFIG = 0x1B
    REG_ACCEL_CONFIG = 0x1C
    
    REG_INT_PIN_CFG = 0x37
    REG_INT_ENABLE = 0x38
    REG_INT_STATUS = 0x3A
    
    # Accelerometer measurements
    REG_ACCEL_XOUT_H = 0x3B
    REG_ACCEL_XOUT_L = 0x3C
    REG_ACCEL_YOUT_H = 0x3D
    REG_ACCEL_YOUT_L = 0x3E
    REG_ACCEL_ZOUT_H = 0x3F
    REG_ACCEL_ZOUT_L = 0x40
    
    # Temperature measurement
    REG_TEMP_OUT_H = 0x41
    REG_TEMP_OUT_L = 0x42
    
    # Gyroscope measurements
    REG_GYRO_XOUT_H = 0x43
    REG_GYRO_XOUT_L = 0x44
    REG_GYRO_YOUT_H = 0x45
    REG_GYRO_YOUT_L = 0x46
    REG_GYRO_ZOUT_H = 0x47
    REG_GYRO_ZOUT_L = 0x48
    
    REG_SIGNAL_PATH_RESET = 0x68
    REG_USER_CTRL = 0x6A
    REG_PWR_MGMT_1 = 0x6B
    REG_PWR_MGMT_2 = 0x6C
    REG_FIFO_COUNT_H = 0x72
    REG_FIFO_COUNT_L = 0x73
    REG_FIFO_R_W = 0x74
    REG_WHO_AM_I = 0x75
    
    # Power Management
    PWR_RESET = 0x80
    PWR_SLEEP = 0x40
    PWR_CYCLE = 0x20
    PWR_TEMP_DIS = 0x08
    PWR_CLKSEL_INTERNAL = 0x00
    PWR_CLKSEL_PLL_X = 0x01
    
    # Gyroscope Full Scale Range
    GYRO_FS_250 = 0x00   # +/-250 deg/s
    GYRO_FS_500 = 0x08   # +/-500 deg/s
    GYRO_FS_1000 = 0x10  # +/-1000 deg/s
    GYRO_FS_2000 = 0x18  # +/-2000 deg/s
    
    # Accelerometer Full Scale Range
    ACCEL_FS_2G = 0x00   # +/-2g
    ACCEL_FS_4G = 0x08   # +/-4g
    ACCEL_FS_8G = 0x10   # +/-8g
    ACCEL_FS_16G = 0x18  # +/-16g
    
    # Scale factors for converting raw values
    GYRO_SCALE = {
        0x00: 131.0,   # +/-250 deg/s
        0x08: 65.5,    # +/-500 deg/s
        0x10: 32.8,    # +/-1000 deg/s
        0x18: 16.4     # +/-2000 deg/s
    }
    
    ACCEL_SCALE = {
        0x00: 16384.0,  # +/-2g
        0x08: 8192.0,   # +/-4g
        0x10: 4096.0,   # +/-8g
        0x18: 2048.0    # +/-16g
    }


class Device:
    """Parent class for all devices. Should act as an abstract class."""
    pass


class Controller:
    """Parent class for abstraction act as an abstract class."""
    pass


class MPU6050(Device):
    """Class representing the MPU6050 device with I2C communication."""
    
    def __init__(self, i2c, address=MPU6050Config.MPU6050_ADDR):
        """Initialize MPU6050 device
        
        Args:
            i2c: I2C bus instance
            address: I2C address (0x68 or 0x69)
        """
        self.i2c = i2c
        self.address = address
        self.config = MPU6050Config()
        
        # Current scale settings
        self.gyro_scale = self.config.GYRO_FS_250
        self.accel_scale = self.config.ACCEL_FS_2G
        
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
            
            # Set default ranges
            self.set_gyro_range(self.config.GYRO_FS_250)
            self.set_accel_range(self.config.ACCEL_FS_2G)
            
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
    
    def set_gyro_range(self, range_value):
        """Set gyroscope full scale range
        
        Args:
            range_value: GYRO_FS_250, GYRO_FS_500, GYRO_FS_1000, or GYRO_FS_2000
        """
        self.write_register(self.config.REG_GYRO_CONFIG, range_value)
        self.gyro_scale = range_value
    
    def set_accel_range(self, range_value):
        """Set accelerometer full scale range
        
        Args:
            range_value: ACCEL_FS_2G, ACCEL_FS_4G, ACCEL_FS_8G, or ACCEL_FS_16G
        """
        self.write_register(self.config.REG_ACCEL_CONFIG, range_value)
        self.accel_scale = range_value
    
    def read_raw_accel(self):
        """Read raw accelerometer data
        
        Returns:
            Tuple of (x, y, z) raw values (16-bit signed)
        """
        data = self.read_registers(self.config.REG_ACCEL_XOUT_H, 6)
        
        # Combine high and low bytes (big-endian)
        x = self._bytes_to_int16(data[0], data[1])
        y = self._bytes_to_int16(data[2], data[3])
        z = self._bytes_to_int16(data[4], data[5])
        
        return x, y, z
    
    def read_raw_gyro(self):
        """Read raw gyroscope data
        
        Returns:
            Tuple of (x, y, z) raw values (16-bit signed)
        """
        data = self.read_registers(self.config.REG_GYRO_XOUT_H, 6)
        
        # Combine high and low bytes (big-endian)
        x = self._bytes_to_int16(data[0], data[1])
        y = self._bytes_to_int16(data[2], data[3])
        z = self._bytes_to_int16(data[4], data[5])
        
        return x, y, z
    
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
    """Class representing the controller for MPU6050 device."""
    
    def __init__(self, device):
        """Initialize controller with MPU6050 device
        
        Args:
            device: MPU6050 device instance
        """
        self.device = device
    
    def get_acceleration(self):
        """Gets the acceleration data from the MPU6050 device in g (gravity).
        
        Returns:
            Dictionary with 'x', 'y', 'z' acceleration values in g
        """
        raw_x, raw_y, raw_z = self.device.read_raw_accel()
        
        # Get scale factor based on current range
        scale = self.device.config.ACCEL_SCALE[self.device.accel_scale]
        
        return {
            'x': raw_x / scale,
            'y': raw_y / scale,
            'z': raw_z / scale
        }
    
    def get_gyroscope(self):
        """Gets the gyroscope data from the MPU6050 device in deg/s.
        
        Returns:
            Dictionary with 'x', 'y', 'z' angular velocity values in deg/s
        """
        raw_x, raw_y, raw_z = self.device.read_raw_gyro()
        
        # Get scale factor based on current range
        scale = self.device.config.GYRO_SCALE[self.device.gyro_scale]
        
        return {
            'x': raw_x / scale,
            'y': raw_y / scale,
            'z': raw_z / scale
        }
    
    def get_temperature(self):
        """Gets the temperature from the MPU6050 device in Celsius.
        
        Returns:
            Temperature in degrees Celsius
        """
        raw_temp = self.device.read_raw_temp()
        # Temperature formula from datasheet: Temp = (TEMP_OUT / 340) + 36.53
        return (raw_temp / 340.0) + 36.53
    
    def get_all_data(self):
        """Get all sensor data at once.
        
        Returns:
            Dictionary with acceleration, gyroscope, and temperature data
        """
        return {
            'acceleration': self.get_acceleration(),
            'gyroscope': self.get_gyroscope(),
            'temperature': self.get_temperature()
        }


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
    print("MPU6050 Sensor Test")
    print("=" * 40)
    
    while True:
        try:
            # Get all data
            temp = controller.get_temperature()
        
            print(f"Temp:  {temp:.2f}C")
            print("-" * 40)
            
            time.sleep_ms(500)
            
        except KeyboardInterrupt:
            print("\nStopped by user")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)