"""HC-SR04 Ultrasonic Distance Sensor Driver for MicroPython"""
import machine
import time

class HCSR04:
    """
    HC-SR04 Ultrasonic Distance Sensor Driver
    
    The HC-SR04 uses a trigger/echo pin interface:
    - Send 10us pulse to TRIGGER pin
    - Measure pulse width on ECHO pin
    - Distance = (pulse_width * speed_of_sound) / 2
    """
    
    # Speed of sound in cm/us at 20°C
    SPEED_OF_SOUND = 0.0343  # cm/us
    
    # Timeout for echo (38ms = ~6.5m max range)
    TIMEOUT_US = 38000
    
    def __init__(self, trigger_pin: int, echo_pin: int):
        """
        Initialize HC-SR04 sensor
        
        Args:
            trigger_pin: GPIO pin number for trigger
            echo_pin: GPIO pin number for echo
        """
        self.trigger = machine.Pin(trigger_pin, machine.Pin.OUT)
        self.echo = machine.Pin(echo_pin, machine.Pin.IN)
        
        # Ensure trigger is low
        self.trigger.value(0)
        time.sleep_ms(100)
    
    def _send_trigger_pulse(self):
        """Send 10us trigger pulse"""
        self.trigger.value(0)
        time.sleep_us(2)
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)
    
    def _measure_echo_pulse(self) -> int:
        """
        Measure echo pulse width in microseconds
        
        Returns:
            Pulse width in microseconds, or -1 on timeout
        """
        # Wait for echo to go high
        timeout_start = time.ticks_us()
        while self.echo.value() == 0:
            if time.ticks_diff(time.ticks_us(), timeout_start) > self.TIMEOUT_US:
                return -1
        
        # Measure pulse width
        pulse_start = time.ticks_us()
        while self.echo.value() == 1:
            if time.ticks_diff(time.ticks_us(), pulse_start) > self.TIMEOUT_US:
                return -1
        
        pulse_end = time.ticks_us()
        return time.ticks_diff(pulse_end, pulse_start)
    
    def read_distance_cm(self) -> float:
        """
        Read distance in centimeters
        
        Returns:
            Distance in cm, or -1 on error/timeout
        """
        self._send_trigger_pulse()
        pulse_width = self._measure_echo_pulse()
        
        if pulse_width < 0:
            return -1
        
        # Calculate distance: (pulse_width * speed_of_sound) / 2
        distance = (pulse_width * self.SPEED_OF_SOUND) / 2
        
        return round(distance, 2)
    
    def read_distance_mm(self) -> float:
        """
        Read distance in millimeters
        
        Returns:
            Distance in mm, or -1 on error/timeout
        """
        distance_cm = self.read_distance_cm()
        if distance_cm < 0:
            return -1
        return round(distance_cm * 10, 1)
    
    def read_distance_inches(self) -> float:
        """
        Read distance in inches
        
        Returns:
            Distance in inches, or -1 on error/timeout
        """
        distance_cm = self.read_distance_cm()
        if distance_cm < 0:
            return -1
        return round(distance_cm / 2.54, 2)
    
    def read_multiple(self, samples: int = 5) -> dict:
        """
        Take multiple readings and return statistics
        
        Args:
            samples: Number of samples to take
            
        Returns:
            Dictionary with min, max, avg, median distances in cm
        """
        readings = []
        
        for _ in range(samples):
            distance = self.read_distance_cm()
            if distance > 0:
                readings.append(distance)
            time.sleep_ms(60)  # Wait between readings (HC-SR04 needs ~60ms)
        
        if not readings:
            return {
                'min': -1,
                'max': -1,
                'avg': -1,
                'median': -1,
                'count': 0
            }
        
        readings.sort()
        return {
            'min': readings[0],
            'max': readings[-1],
            'avg': round(sum(readings) / len(readings), 2),
            'median': readings[len(readings) // 2],
            'count': len(readings)
        }
    
    def is_object_detected(self, threshold_cm: float = 50) -> bool:
        """
        Check if an object is detected within threshold distance
        
        Args:
            threshold_cm: Distance threshold in cm
            
        Returns:
            True if object detected within threshold
        """
        distance = self.read_distance_cm()
        return 0 < distance <= threshold_cm
