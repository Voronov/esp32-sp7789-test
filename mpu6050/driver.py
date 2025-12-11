"""
MPU6050 Driver with Bridge Pattern
- Device Layer: Low-level I2C communication
- Sensor Layer: High-level data processing and conversion
"""

from machine import I2C
import time


class MPU6050Device:
    """
    Low-level MPU6050 device implementation.
    Handles direct I2C communication with sensor registers.
    """
    
    PWR_MGMT_1 = 0x6B
    TEMP_OUT_H = 0x41
    ACCEL_XOUT_H = 0x3B
    GYRO_XOUT_H = 0x43
    GYRO_CONFIG = 0x1B
    ACCEL_CONFIG = 0x1C
    WHO_AM_I = 0x75
    
    def __init__(self, i2c: I2C, addr: int = 0x68, strict: bool = True):
        """
        Initialize MPU6050 device.
        
        Args:
            i2c: I2C bus object
            addr: I2C address (default 0x68, alternative 0x69)
            strict: If True, raise exception on connection failure.
                   If False, print warning and continue.
        """
        self.i2c = i2c
        self.addr = addr
        self.is_awake = False
        self.connected = False
        self.strict = strict
        self._verify_connection()
    
    def _verify_connection(self):
        """Verify sensor is present on I2C bus"""
        try:
            devices = self.i2c.scan()
            
            if self.addr not in devices:
                error_msg = self._generate_error_message(devices)
                
                if self.strict:
                    raise RuntimeError(error_msg)
                else:
                    print(f"WARNING: {error_msg}")
                    print("Continuing in non-strict mode...")
                    return
            
            who_am_i = self.i2c.readfrom_mem(self.addr, self.WHO_AM_I, 1)[0]
            if who_am_i not in [0x68, 0x69]:
                error_msg = f"Invalid WHO_AM_I: 0x{who_am_i:02X} (expected 0x68 or 0x69)"
                if self.strict:
                    raise RuntimeError(error_msg)
                else:
                    print(f"WARNING: {error_msg}")
                    return
            
            self.connected = True
            print(f"OK: MPU6050 found at 0x{self.addr:02X} (WHO_AM_I: 0x{who_am_i:02X})")
            
        except OSError as e:
            error_msg = f"I2C communication error: {e}"
            if self.strict:
                raise RuntimeError(error_msg)
            else:
                print(f"WARNING: {error_msg}")
    
    def _generate_error_message(self, devices: list) -> str:
        """Generate helpful error message with diagnostics"""
        msg = f"MPU6050 not found at 0x{self.addr:02X}\n"
        
        if not devices:
            msg += "No I2C devices detected on bus!\n"
            msg += "Troubleshooting:\n"
            msg += "  - Check wiring (SCL, SDA, VCC, GND)\n"
            msg += "  - Verify 3.3V power supply\n"
            msg += "  - Check if pins are correct\n"
            msg += "  - Try pull-up resistors (4.7kΩ)"
        else:
            msg += f"Found {len(devices)} device(s): "
            msg += ", ".join([f"0x{d:02X}" for d in devices]) + "\n"
            
            if 0x69 in devices and self.addr == 0x68:
                msg += "TIP: MPU6050 detected at 0x69. Try: MPU6050Device(i2c, addr=0x69)"
            elif 0x68 in devices and self.addr == 0x69:
                msg += "TIP: MPU6050 detected at 0x68. Try: MPU6050Device(i2c, addr=0x68)"
            else:
                msg += "TIP: MPU6050 not detected. Check address (0x68 or 0x69)"
        
        return msg
    
    def wake_up(self):
        """Wake up sensor from sleep mode"""
        if not self.connected:
            print("WARNING: Sensor not connected, skipping wake_up")
            return False
        
        try:
            self.i2c.writeto_mem(self.addr, self.PWR_MGMT_1, b'\x00')
            time.sleep_ms(100)
            self.is_awake = True
            print("OK: MPU6050 activated")
            return True
        except OSError as e:
            print(f"ERROR: Failed to wake sensor: {e}")
            return False
    
    def sleep(self):
        """Put sensor into sleep mode"""
        if not self.connected:
            print("WARNING: Sensor not connected, skipping sleep")
            return False
        
        try:
            self.i2c.writeto_mem(self.addr, self.PWR_MGMT_1, b'\x40')
            self.is_awake = False
            print("OK: MPU6050 sleep mode")
            return True
        except OSError as e:
            print(f"ERROR: Failed to sleep sensor: {e}")
            return False
    
    def read_temperature(self) -> tuple:
        """
        Read raw temperature data.
        
        Returns:
            Tuple of (high_byte, low_byte) or (0, 0) on error
        """
        if not self.connected:
            return (0, 0)
        
        try:
            data = self.i2c.readfrom_mem(self.addr, self.TEMP_OUT_H, 2)
            return data[0], data[1]
        except OSError as e:
            print(f"ERROR: Failed to read temperature: {e}")
            return (0, 0)
    
    def read_accelerometer(self) -> tuple:
        """
        Read raw accelerometer data for all axes.
        
        Returns:
            Tuple of 6 bytes (X_H, X_L, Y_H, Y_L, Z_H, Z_L) or zeros on error
        """
        if not self.connected:
            return (0, 0, 0, 0, 0, 0)
        
        try:
            return tuple(self.i2c.readfrom_mem(self.addr, self.ACCEL_XOUT_H, 6))
        except OSError as e:
            print(f"ERROR: Failed to read accelerometer: {e}")
            return (0, 0, 0, 0, 0, 0)
    
    def read_gyroscope(self) -> tuple:
        """
        Read raw gyroscope data for all axes.
        
        Returns:
            Tuple of 6 bytes (X_H, X_L, Y_H, Y_L, Z_H, Z_L) or zeros on error
        """
        if not self.connected:
            return (0, 0, 0, 0, 0, 0)
        
        try:
            return tuple(self.i2c.readfrom_mem(self.addr, self.GYRO_XOUT_H, 6))
        except OSError as e:
            print(f"ERROR: Failed to read gyroscope: {e}")
            return (0, 0, 0, 0, 0, 0)


class MPU6050Sensor:
    """
    High-level MPU6050 sensor interface.
    Converts raw bytes into meaningful physical quantities.
    """
    
    TEMP_SENSITIVITY = 340.0
    TEMP_OFFSET = 36.53
    ACCEL_SCALE = 16384.0
    GYRO_SCALE = 131.0
    
    def __init__(self, device: MPU6050Device):
        """
        Initialize sensor with device implementation.
        
        Args:
            device: MPU6050Device instance
        """
        self.device = device
    
    @staticmethod
    def bytes_to_number(high: int, low: int) -> int:
        """
        Convert two bytes to signed 16-bit integer.
        
        Uses bitwise operations:
        1. Shift high byte left by 8 positions
        2. OR with low byte to combine
        3. Check sign bit and adjust if negative
        
        Args:
            high: High byte (bits 15-8)
            low: Low byte (bits 7-0)
        
        Returns:
            Signed integer (-32768 to 32767)
        """
        value = (high << 8) | low
        if value & 0x8000:
            value -= 0x10000
        return value
    
    def get_temperature(self) -> float:
        """
        Get temperature in Celsius.
        
        Formula: Temperature = (raw_value / 340) + 36.53
        
        Returns:
            Temperature in °C
        """
        high, low = self.device.read_temperature()
        raw_temp = self.bytes_to_number(high, low)
        temperature = (raw_temp / self.TEMP_SENSITIVITY) + self.TEMP_OFFSET
        return round(temperature, 2)
    
    def get_acceleration(self) -> dict:
        """
        Get acceleration for all axes in g.
        
        Returns:
            Dict with keys 'x', 'y', 'z' in g units
        """
        data = self.device.read_accelerometer()
        
        x = self.bytes_to_number(data[0], data[1])
        y = self.bytes_to_number(data[2], data[3])
        z = self.bytes_to_number(data[4], data[5])
        
        return {
            'x': round(x / self.ACCEL_SCALE, 3),
            'y': round(y / self.ACCEL_SCALE, 3),
            'z': round(z / self.ACCEL_SCALE, 3)
        }
    
    def get_gyro(self) -> dict:
        """
        Get angular velocity for all axes in degrees/second.
        
        Returns:
            Dict with keys 'x', 'y', 'z' in °/s
        """
        data = self.device.read_gyroscope()
        
        x = self.bytes_to_number(data[0], data[1])
        y = self.bytes_to_number(data[2], data[3])
        z = self.bytes_to_number(data[4], data[5])
        
        return {
            'x': round(x / self.GYRO_SCALE, 2),
            'y': round(y / self.GYRO_SCALE, 2),
            'z': round(z / self.GYRO_SCALE, 2)
        }
    
    def get_all_data(self) -> dict:
        """
        Get all sensor data at once.
        
        Returns:
            Dict with temperature, acceleration, and gyroscope data
        """
        return {
            'temperature': self.get_temperature(),
            'acceleration': self.get_acceleration(),
            'gyroscope': self.get_gyro()
        }
    
    def is_active(self) -> bool:
        """Check if sensor is active"""
        return self.device.is_awake
    
    def activate(self):
        """Activate the sensor"""
        self.device.wake_up()
    
    def deactivate(self):
        """Deactivate the sensor"""
        self.device.sleep()
