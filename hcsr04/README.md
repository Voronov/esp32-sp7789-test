# HC-SR04 Ultrasonic Distance Sensor

This module provides a MicroPython driver for the HC-SR04 ultrasonic distance sensor with examples for ESP32.

## Hardware Overview

The HC-SR04 is an ultrasonic distance sensor that measures distance by:
1. Sending a 10μs pulse to the TRIGGER pin
2. Sensor emits 8 ultrasonic pulses at 40kHz
3. Measuring the pulse width on the ECHO pin
4. Calculating distance: `distance = (pulse_width × speed_of_sound) / 2`

### Specifications
- **Operating Voltage**: 5V DC
- **Operating Current**: 15mA
- **Measuring Range**: 2cm - 400cm
- **Accuracy**: ±3mm
- **Measuring Angle**: 15°
- **Trigger Input**: 10μs TTL pulse
- **Echo Output**: TTL pulse proportional to distance

## Wiring

### HC-SR04 Pinout
```
HC-SR04
┌─────────────┐
│  VCC  TRIG  │
│  ECHO GND   │
└─────────────┘
```

### ESP32 Connection
```
HC-SR04          ESP32
────────────────────────
VCC      →      5V (or 3.3V with level shifter)
TRIG     →      GPIO 12 (configurable)
ECHO     →      GPIO 14 (configurable)
GND      →      GND
```

**Note:** If using with ST7789 display, avoid these pins:
- GPIO 18 (SPI SCK)
- GPIO 23 (SPI MOSI)
- GPIO 2 (DC)
- GPIO 4 (RST)

**Important Notes:**
- HC-SR04 operates at 5V, but many work at 3.3V with reduced range
- ECHO pin outputs 5V - use a voltage divider or level shifter for ESP32 (3.3V tolerant)
- Simple voltage divider: 1kΩ and 2kΩ resistors can protect ESP32

### Voltage Divider for ECHO Pin (Recommended)
```
HC-SR04 ECHO ──┬── 1kΩ ──┬── ESP32 GPIO
               │         │
              2kΩ       GND
               │
              GND
```

## Installation

Copy the `hcsr04` folder to your ESP32:
```bash
# Using mpremote
mpremote cp -r hcsr04 :

# Or using ampy
ampy put hcsr04
```

## Usage

### Basic Example

```python
from hcsr04 import HCSR04
import time

# Initialize sensor
sensor = HCSR04(trigger_pin=12, echo_pin=14)

# Read distance
while True:
    distance = sensor.read_distance_cm()
    if distance > 0:
        print(f"Distance: {distance:.2f} cm")
    else:
        print("Out of range")
    time.sleep_ms(100)
```

### Available Methods

#### `read_distance_cm() -> float`
Returns distance in centimeters, or -1 on error/timeout.

```python
distance = sensor.read_distance_cm()
```

#### `read_distance_mm() -> float`
Returns distance in millimeters, or -1 on error/timeout.

```python
distance = sensor.read_distance_mm()
```

#### `read_distance_inches() -> float`
Returns distance in inches, or -1 on error/timeout.

```python
distance = sensor.read_distance_inches()
```

#### `read_multiple(samples=5) -> dict`
Takes multiple readings and returns statistics.

```python
stats = sensor.read_multiple(samples=10)
print(f"Average: {stats['avg']} cm")
print(f"Min: {stats['min']} cm")
print(f"Max: {stats['max']} cm")
print(f"Median: {stats['median']} cm")
```

#### `is_object_detected(threshold_cm=50) -> bool`
Checks if an object is within threshold distance.

```python
if sensor.is_object_detected(threshold_cm=30):
    print("Object detected!")
```

## Examples

### 1. Simple Console Example
```bash
mpremote run hcsr04/example_simple.py
```

Continuously reads and displays distance measurements.

### 2. Display Example
```bash
mpremote run hcsr04/example.py
```

Shows distance on ST7789 display with color-coded alerts.

### 3. Statistical Analysis
```python
from hcsr04 import HCSR04

sensor = HCSR04(trigger_pin=12, echo_pin=14)
stats = sensor.read_multiple(samples=10)

print(f"Average: {stats['avg']} cm")
print(f"Range: {stats['min']} - {stats['max']} cm")
```

### 4. Proximity Detection
```python
from hcsr04 import HCSR04
import time

sensor = HCSR04(trigger_pin=12, echo_pin=14)
THRESHOLD = 20  # cm

while True:
    if sensor.is_object_detected(threshold_cm=THRESHOLD):
        distance = sensor.read_distance_cm()
        print(f"⚠️ Object at {distance:.2f} cm!")
    time.sleep_ms(200)
```

## Timing Requirements

- **Minimum delay between readings**: 60ms (sensor cycle time)
- **Trigger pulse**: 10μs
- **Maximum echo timeout**: 38ms (~6.5m range)

## Troubleshooting

### No readings / Always timeout
- Check wiring connections
- Verify GPIO pin numbers in code
- Ensure sensor has stable 5V power supply
- Check if ECHO pin needs voltage divider

### Erratic readings
- Sensor needs 60ms between measurements
- Avoid measuring reflective or angled surfaces
- Keep sensor stable (vibrations affect readings)
- Check for electromagnetic interference

### Short range only
- Sensor may need 5V instead of 3.3V
- Check if ECHO signal is reaching ESP32
- Verify voltage divider isn't too resistive

### "Out of range" for close objects
- HC-SR04 minimum range is ~2cm
- Objects closer than 2cm won't be detected

## Technical Details

### How It Works

1. **Trigger Phase**: 10μs HIGH pulse on TRIGGER pin
2. **Ultrasonic Burst**: Sensor sends 8 pulses at 40kHz
3. **Echo Wait**: ECHO pin goes HIGH
4. **Echo Receive**: ECHO pin stays HIGH until echo received
5. **Calculate**: Distance = (echo_time × 343m/s) / 2

### Distance Calculation

```
distance (cm) = (pulse_width_μs × 0.0343) / 2

Where:
- 0.0343 = speed of sound (343 m/s = 0.0343 cm/μs)
- ÷ 2 = sound travels to object and back
```

### Measurement Range

- **Minimum**: 2 cm
- **Maximum**: 400 cm (4 meters)
- **Optimal**: 10 cm - 300 cm
- **Accuracy**: ±3 mm

## API Reference

### Class: `HCSR04`

```python
class HCSR04:
    def __init__(self, trigger_pin: int, echo_pin: int)
    def read_distance_cm(self) -> float
    def read_distance_mm(self) -> float
    def read_distance_inches(self) -> float
    def read_multiple(self, samples: int = 5) -> dict
    def is_object_detected(self, threshold_cm: float = 50) -> bool
```


## References

- [HC-SR04 Datasheet](https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf)
- [ESP32 GPIO Reference](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/gpio.html)
