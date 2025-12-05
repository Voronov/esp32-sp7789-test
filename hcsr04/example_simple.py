"""Simple HC-SR04 Example - Console Only (No Display)"""
import machine
import time

try:
    from hcsr04.driver import HCSR04
except ImportError:
    try:
        from .driver import HCSR04
    except ImportError:
        from driver import HCSR04


def main():
    """Simple example reading distance from HC-SR04"""
    
    # Configure your GPIO pins here
    TRIGGER_PIN = 12  # GPIO pin connected to HC-SR04 TRIGGER
    ECHO_PIN = 14     # GPIO pin connected to HC-SR04 ECHO
    
    print("=" * 50)
    print("HC-SR04 Ultrasonic Distance Sensor Example")
    print("=" * 50)
    print(f"Trigger Pin: GPIO {TRIGGER_PIN}")
    print(f"Echo Pin:    GPIO {ECHO_PIN}")
    print("=" * 50)
    
    # Initialize sensor
    sensor = HCSR04(trigger_pin=TRIGGER_PIN, echo_pin=ECHO_PIN)
    
    print("\nStarting measurements... (Press Ctrl+C to stop)\n")
    
    try:
        while True:
            # Read distance in centimeters
            distance = sensor.read_distance_cm()
            
            if distance > 0:
                # Valid reading
                print(f"Distance: {distance:6.2f} cm  ({distance * 10:7.1f} mm, {distance / 2.54:6.2f} in)")
            else:
                # Timeout or error
                print("Distance: OUT OF RANGE or ERROR")
            
            # Wait 100ms between readings
            time.sleep_ms(100)
            
    except KeyboardInterrupt:
        print("\n\nMeasurement stopped by user")


def example_with_statistics():
    """Example with statistical analysis"""
    
    TRIGGER_PIN = 12
    ECHO_PIN = 14
    
    print("=" * 50)
    print("HC-SR04 Statistical Analysis Example")
    print("=" * 50)
    
    sensor = HCSR04(trigger_pin=TRIGGER_PIN, echo_pin=ECHO_PIN)
    
    print("\nTaking 10 samples for statistical analysis...")
    stats = sensor.read_multiple(samples=10)
    
    print("\n" + "=" * 50)
    print(f"Statistics from {stats['count']} valid readings:")
    print("=" * 50)
    print(f"  Minimum:  {stats['min']:6.2f} cm")
    print(f"  Maximum:  {stats['max']:6.2f} cm")
    print(f"  Average:  {stats['avg']:6.2f} cm")
    print(f"  Median:   {stats['median']:6.2f} cm")
    print("=" * 50)


def example_proximity_alert():
    """Example with proximity alert"""
    
    TRIGGER_PIN = 12
    ECHO_PIN = 14
    ALERT_THRESHOLD = 20  # cm
    
    print("=" * 50)
    print("HC-SR04 Proximity Alert Example")
    print("=" * 50)
    print(f"Alert Threshold: {ALERT_THRESHOLD} cm")
    print("=" * 50)
    
    sensor = HCSR04(trigger_pin=TRIGGER_PIN, echo_pin=ECHO_PIN)
    
    print("\nMonitoring... (Press Ctrl+C to stop)\n")
    
    try:
        while True:
            distance = sensor.read_distance_cm()
            
            if distance > 0:
                if distance <= ALERT_THRESHOLD:
                    print(f"⚠️  ALERT! Object at {distance:.2f} cm (threshold: {ALERT_THRESHOLD} cm)")
                else:
                    print(f"✓  Safe: {distance:.2f} cm")
            else:
                print("No object detected (out of range)")
            
            time.sleep_ms(200)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")


if __name__ == '__main__':
    # Run the simple continuous measurement example
    main()
    
    # Uncomment to run other examples:
    # example_with_statistics()
    # example_proximity_alert()
