"""
Sensor Interface Module using Abstract Base Classes
This demonstrates proper OOP design with interfaces in Python
"""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Optional
import machine
import time


class ISensorCommunication(ABC):
    """Interface for low-level sensor communication"""
    
    @abstractmethod
    def read_register(self, reg: int) -> int:
        """Read a single byte from register"""
        pass
    
    @abstractmethod
    def write_register(self, reg: int, value: int) -> None:
        """Write a single byte to register"""
        pass
    
    @abstractmethod
    def read_registers(self, reg: int, length: int) -> bytes:
        """Read multiple bytes from register"""
        pass
    
    @abstractmethod
    def check_connection(self) -> bool:
        """Check if sensor is connected and responding"""
        pass


class ISensorInitializable(ABC):
    """Interface for sensor initialization"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the sensor with default or custom settings"""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset the sensor to default state"""
        pass
    
    @abstractmethod
    def configure(self, **kwargs) -> None:
        """Configure sensor with custom parameters"""
        pass


class ISensorData(ABC):
    """Interface for reading sensor data"""
    
    @abstractmethod
    def read_raw_data(self) -> Tuple[int, int]:
        """Read raw sensor values"""
        pass
    
    @abstractmethod
    def read_processed_data(self) -> Dict[str, float]:
        """Read processed/calculated sensor values"""
        pass
    
    @abstractmethod
    def get_sample_rate(self) -> int:
        """Get current sampling rate in Hz"""
        pass


class ISensorStatus(ABC):
    """Interface for sensor status and diagnostics"""
    
    @abstractmethod
    def get_status(self) -> Dict[str, any]:
        """Get current sensor status"""
        pass
    
    @abstractmethod
    def is_ready(self) -> bool:
        """Check if sensor is ready for reading"""
        pass
    
    @abstractmethod
    def get_device_info(self) -> Dict[str, str]:
        """Get device identification information"""
        pass


class IHealthSensor(ABC):
    """Interface specific to health monitoring sensors"""
    
    @abstractmethod
    def read_heart_rate(self) -> Optional[int]:
        """Read heart rate in BPM"""
        pass
    
    @abstractmethod
    def read_spo2(self) -> Optional[float]:
        """Read SpO2 percentage"""
        pass
    
    @abstractmethod
    def read_temperature(self) -> Optional[float]:
        """Read temperature in Celsius"""
        pass
