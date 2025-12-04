"""I2C Communication implementation for MAX30100"""
import machine
try:
    from . import sensor_interface as si
except ImportError:
    import sensor_interface as si

class MAX30100Communication(si.ISensorCommunication):
    """I2C Communication implementation for MAX30100"""
    
    MAX30100_ADDR = 0x57
    REG_PART_ID = 0xFF
    REG_REV_ID = 0xFE
    
    def __init__(self, i2c: machine.I2C, address: int = MAX30100_ADDR):
        self.i2c = i2c
        self.address = address
    
    def read_register(self, reg: int) -> int:
        """Read a single byte from register"""
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]
    
    def write_register(self, reg: int, value: int) -> None:
        """Write a single byte to register"""
        self.i2c.writeto_mem(self.address, reg, bytes([value]))
    
    def read_registers(self, reg: int, length: int) -> bytes:
        """Read multiple bytes from register"""
        return self.i2c.readfrom_mem(self.address, reg, length)
    
    def check_connection(self) -> bool:
        """Check if MAX30100 is connected"""
        try:
            part_id = self.read_register(self.REG_PART_ID)
            return part_id == 0x11  # MAX30100 Part ID
        except Exception:
            return False
