"""MAX30100 Sensor Device Driver"""
import time

# Handle typing imports for MicroPython compatibility
try:
    from typing import Tuple, Dict, Optional
except ImportError:
    # MicroPython doesn't have typing module
    pass

try:
    from . import sensor_interface as si
    from .constants import MAX30100Config
except ImportError:
    try:
        import max30100.sensor_interface as si
        from max30100.constants import MAX30100Config
    except ImportError:
        import sensor_interface as si
        from constants import MAX30100Config

class MAX30100(si.ISensorInitializable, si.ISensorData, si.ISensorStatus, si.IHealthSensor):
    """
    Complete MAX30100 sensor implementation with all interfaces
    """
    
    def __init__(self, communication: si.ISensorCommunication):
        self.comm = communication
        self.config = MAX30100Config()
        self._initialized = False
        self._sample_rate = 100  # Hz
        
        # Data buffers
        self.ir_buffer = []
        self.red_buffer = []
        self.max_buffer_size = 100
    
    # ========================================================================
    # ISensorInitializable Implementation
    # ========================================================================
    
    def initialize(self) -> bool:
        """Initialize the sensor with default settings"""
        if not self.comm.check_connection():
            return False
        
        # Reset sensor
        self.reset()
        time.sleep_ms(100)
        
        # Default configuration
        self.configure(
            mode='spo2',
            sample_rate=100,
            pulse_width=1600,
            led_current='medium'
        )
        
        self._initialized = True
        return True
    
    def reset(self) -> None:
        """Reset the sensor to default state"""
        self.comm.write_register(
            self.config.REG_MODE_CONFIG, 
            self.config.MODE_RESET
        )
        
        # Clear buffers
        self.ir_buffer.clear()
        self.red_buffer.clear()
        
        # Clear FIFO
        self.comm.write_register(self.config.REG_FIFO_WR_PTR, 0x00)
        self.comm.write_register(self.config.REG_FIFO_RD_PTR, 0x00)
        self.comm.write_register(self.config.REG_OVRFLOW_CTR, 0x00)
    
    def configure(self, **kwargs) -> None:
        """
        Configure sensor with custom parameters
        
        Parameters:
        - mode: 'hr' or 'spo2' (default: 'spo2')
        - sample_rate: 50, 100, 167, 200, 400, 600, 800, 1000 Hz
        - pulse_width: 200, 400, 800, 1600 us
        - led_current: 'low', 'medium', 'high', 'max'
        """
        # Set mode
        mode = kwargs.get('mode', 'spo2')
        if mode == 'spo2':
            self.comm.write_register(
                self.config.REG_MODE_CONFIG, 
                self.config.MODE_SPO2_EN
            )
        elif mode == 'hr':
            self.comm.write_register(
                self.config.REG_MODE_CONFIG, 
                self.config.MODE_HR_ONLY
            )
        
        # Set SpO2 configuration
        spo2_config = self.config.SPO2_HI_RES_EN | self.config.SPO2_SR_1600
        
        sample_rate = kwargs.get('sample_rate', 100)
        if sample_rate == 50:
            spo2_config |= 0x00
        elif sample_rate == 100:
            spo2_config |= 0x04
        elif sample_rate >= 167:
            spo2_config |= 0x07
        
        self._sample_rate = sample_rate
        self.comm.write_register(self.config.REG_SPO2_CONFIG, spo2_config)
        
        # Set LED current
        led_current = kwargs.get('led_current', 'medium')
        led_value = {
            'low': self.config.LED_PW_LOW,
            'medium': self.config.LED_PW_MED,
            'high': 0xCC,
            'max': self.config.LED_PW_MAX
        }.get(led_current, self.config.LED_PW_MED)
        
        self.comm.write_register(self.config.REG_LED_CONFIG, led_value)
    
    # ========================================================================
    # ISensorData Implementation
    # ========================================================================
    
    def read_raw_data(self) -> Tuple[int, int]:
        """Read raw IR and Red LED values from FIFO"""
        data = self.comm.read_registers(self.config.REG_FIFO_DATA, 4)
        
        ir = (data[0] << 8) | data[1]
        red = (data[2] << 8) | data[3]
        
        # Update buffers
        self.ir_buffer.append(ir)
        self.red_buffer.append(red)
        
        if len(self.ir_buffer) > self.max_buffer_size:
            self.ir_buffer.pop(0)
            self.red_buffer.pop(0)
        
        return ir, red
    
    def read_processed_data(self) -> Dict[str, float]:
        """Read and return processed data"""
        ir, red = self.read_raw_data()
        
        return {
            'ir_raw': ir,
            'red_raw': red,
            'heart_rate': self.read_heart_rate() or 0,
            'spo2': self.read_spo2() or 0,
            'temperature': self.read_temperature() or 0
        }
    
    def get_sample_rate(self) -> int:
        """Get current sampling rate in Hz"""
        return self._sample_rate
    
    # ========================================================================
    # ISensorStatus Implementation
    # ========================================================================
    
    def get_status(self) -> Dict[str, any]:
        """Get current sensor status"""
        int_status = self.comm.read_register(self.config.REG_INT_STATUS)
        
        wr_ptr = self.comm.read_register(self.config.REG_FIFO_WR_PTR)
        rd_ptr = self.comm.read_register(self.config.REG_FIFO_RD_PTR)
        overflow = self.comm.read_register(self.config.REG_OVRFLOW_CTR)
        
        return {
            'initialized': self._initialized,
            'ready': self.is_ready(),
            'interrupt_status': int_status,
            'fifo_write_ptr': wr_ptr,
            'fifo_read_ptr': rd_ptr,
            'fifo_overflow': overflow,
            'samples_available': (wr_ptr - rd_ptr) % 16
        }
    
    def is_ready(self) -> bool:
        """Check if sensor is ready for reading"""
        if not self._initialized:
            return False
        
        # Check if FIFO has data
        wr_ptr = self.comm.read_register(self.config.REG_FIFO_WR_PTR)
        rd_ptr = self.comm.read_register(self.config.REG_FIFO_RD_PTR)
        
        return wr_ptr != rd_ptr
    
    def get_device_info(self) -> Dict[str, str]:
        """Get device identification information"""
        part_id = self.comm.read_register(0xFF)
        rev_id = self.comm.read_register(0xFE)
        
        return {
            'device': 'MAX30100',
            'part_id': f'0x{part_id:02X}',
            'revision_id': f'0x{rev_id:02X}',
            'manufacturer': 'Maxim Integrated'
        }
    
    # ========================================================================
    # IHealthSensor Implementation
    # ========================================================================
    
    def read_heart_rate(self) -> Optional[int]:
        """Calculate heart rate from IR signal using peak detection"""
        if len(self.ir_buffer) < 50:
            return None
        
        # Simple peak detection algorithm
        peaks = 0
        threshold = sum(self.ir_buffer[-50:]) / 50
        
        for i in range(1, len(self.ir_buffer[-50:]) - 1):
            current = self.ir_buffer[-50:][i]
            prev = self.ir_buffer[-50:][i-1]
            next_val = self.ir_buffer[-50:][i+1]
            
            if current > threshold and current > prev and current > next_val:
                peaks += 1
        
        # Convert to BPM (50 samples at 100Hz = 0.5 seconds)
        bpm = int(peaks * 120)
        
        # Clamp to reasonable range
        return min(max(bpm, 40), 200) if 40 <= bpm <= 200 else None
    
    def read_spo2(self) -> Optional[float]:
        """Calculate SpO2 from Red/IR ratio"""
        if len(self.ir_buffer) < 10 or len(self.red_buffer) < 10:
            return None
        
        # Calculate AC and DC components
        ir_ac = max(self.ir_buffer[-10:]) - min(self.ir_buffer[-10:])
        ir_dc = sum(self.ir_buffer[-10:]) / 10
        
        red_ac = max(self.red_buffer[-10:]) - min(self.red_buffer[-10:])
        red_dc = sum(self.red_buffer[-10:]) / 10
        
        if ir_dc == 0 or red_dc == 0:
            return None
        
        # R = (Red AC/DC) / (IR AC/DC)
        r = (red_ac / red_dc) / (ir_ac / ir_dc) if ir_ac > 0 else 0
        
        # Empirical formula (needs calibration)
        spo2 = 110 - 25 * r
        
        return round(spo2, 1) if 70 <= spo2 <= 100 else None
    
    def read_temperature(self) -> Optional[float]:
        """Read internal temperature sensor"""
        try:
            # Enable temperature reading
            mode = self.comm.read_register(self.config.REG_MODE_CONFIG)
            self.comm.write_register(
                self.config.REG_MODE_CONFIG, 
                mode | self.config.MODE_TEMP_EN
            )
            
            time.sleep_ms(100)
            
            # Read temperature
            temp_int = self.comm.read_register(self.config.REG_TEMP_INT)
            temp_frac = self.comm.read_register(self.config.REG_TEMP_FRAC)
            
            temperature = temp_int + (temp_frac * 0.0625)
            
            return round(temperature, 2)
        except Exception:
            return None
