# ESP32 ST7789 MicroPython Driver & Clock Demo

This project provides a MicroPython driver for ST7789-based displays and includes a demo application featuring a digital clock and screensaver.

## Project Structure

```
├── clock/
│   ├── clock_ui.py        # Main demo application (Clock + Screensaver)
│   └── vga2_bold_16x32.py # Bitmap font file
├── driver/
│   └── st7789.py          # ST7789 Display Driver Library
├── max30100/
│   ├── sensor.py          # MAX30100 Driver & Demo
│   └── sensor_interface.py # Sensor Interfaces
├── hcsr04/
│   ├── driver.py          # HC-SR04 Ultrasonic Sensor Driver
│   ├── example.py         # Example with ST7789 display
│   ├── example_simple.py  # Simple console example
│   └── README.md          # HC-SR04 documentation
├── mpu6050/
│   ├── driver.py          # MPU6050 Driver (Bridge Pattern)
│   ├── example_menu.py    # Interactive menu example
│   ├── example_display.py # ST7789 display example
│   ├── i2c_scanner.py     # I2C diagnostic tool
│   ├── example.py         # Legacy example
│   └── README.md          # MPU6050 documentation
├── test/
│   ├── sp7789_test.py     # Simple hardware test script
│   └── hello_world.py     # Basic firmware verification
├── tools/
│   ├── flash_esp32.py     # Script to flash MicroPython firmware
│   ├── flash_firmware.py  # Legacy flash script
│   └── select_port.py     # Script to identify ESP32 serial port
└── Makefile               # Build and run automation
```

## Hardware Requirements

- **ESP32 Development Board**
- **ST7789 Display Module** (Demo configured for 240x240 resolution)
- **MAX30100 Pulse Oximeter Sensor** (I2C)
- **HC-SR04 Ultrasonic Distance Sensor** (GPIO)
- **MPU6050 Accelerometer/Gyroscope** (I2C)

## Wiring Configuration

The default pin configuration in the scripts is as follows:

| Display Pin | ESP32 Pin | Notes |
|-------------|-----------|-------|
| **SCK / SCL**   | GPIO 18   | SPI Clock |
| **SDA / MOSI**  | GPIO 23   | SPI MOSI |
| **DC**      | GPIO 2    | Data/Command |
| **RES / RST**   | GPIO 4    | Reset |
| **CS**      | N/C       | Chip Select (Set to `None` in code) |
| **VCC**     | 3.3V      | Power |
| **GND**     | GND       | Ground |

### MAX30100 Wiring

| Sensor Pin | ESP32 Pin | Notes |
|------------|-----------|-------|
| **VIN**    | 3.3V      | Power |
| **SCL**    | GPIO 22   | I2C Clock |
| **SDA**    | GPIO 21   | I2C Data |
| **INT**    | N/C       | Interrupt (Not used) |
| **GND**    | GND       | Ground |

### HC-SR04 Wiring

| Sensor Pin | ESP32 Pin | Notes |
|------------|-----------|-------|
| **VCC**    | 5V        | Power (can work with 3.3V at reduced range) |
| **TRIG**   | GPIO 12   | Trigger (configurable) |
| **ECHO**   | GPIO 14   | Echo (configurable, use voltage divider for 5V) |
| **GND**    | GND       | Ground |

### MPU6050 Wiring

| Sensor Pin | ESP32 Pin | Notes |
|------------|-----------|-------|
| **VCC**    | 3.3V      | Power |
| **SCL**    | GPIO 17   | I2C Clock |
| **SDA**    | GPIO 18   | I2C Data |
| **GND**    | GND       | Ground |
| **AD0**    | GND/3.3V  | Address select (GND=0x68, 3.3V=0x69) |

> **Note:** If your display module requires a Chip Select (CS) pin, update the pin definition in the code (currently set to `None`).
> 
> **HC-SR04 Warning:** The ECHO pin outputs 5V. Use a voltage divider (1kΩ + 2kΩ) to protect ESP32 GPIO pins. See `hcsr04/README.md` for details.

## Quick Start (Makefile)

This project includes a `Makefile` to automate environment setup, firmware flashing, and running the projects.

### 1. Initialize Environment
Run this command once to create a virtual environment and install dependencies (`mpremote`, `pyserial`, `esptool`).
```bash
make init
```

### 2. Flash MicroPython Firmware (Optional)
If your ESP32 needs a fresh MicroPython installation:
```bash
make flash_esp32
```
*   Downloads the latest **ESP32_GENERIC** firmware.
*   Asks for confirmation before erasing and flashing.
*   **Warning:** This only supports standard ESP32s. Do not use for S2/S3/C3 boards.

### 3. Run the Projects
To deploy and run the code on your ESP32:

**Run Test Script:**
```bash
make run_test
```
*   Copies `st7789.py` and `sp7789_test.py`.
*   Draws a red rectangle and cycles background colors.

**Run Clock Demo:**
```bash
make run_clock
```
*   Copies `st7789.py`, font files, and `clock_ui.py`.
*   Displays a digital clock with a progress bar and screensaver.

**Run Simple SPI Test:**
```bash
make run_simple
```
*   Copies `simple_spi.py`.
*   Demonstrates direct SPI initialization and drawing without the heavy driver.
*   Useful for understanding low-level control or debugging.

**Run MAX30100 Sensor Demo:**
```bash
make run_sensor
```
*   Copies `sensor.py` and `sensor_interface.py`.
*   Initializes the MAX30100 sensor via I2C.
*   Displays Heart Rate (BPM), SpO2 (%), and Temperature in the console.

**Run HC-SR04 Distance Sensor:**
```bash
# Simple console example
make run_hcsr04_simple

# With ST7789 display
make run_hcsr04
```
*   Reads distance from HC-SR04 ultrasonic sensor.
*   Displays measurements in cm, mm, and inches.
*   See `hcsr04/README.md` for detailed documentation.

**Run MPU6050 Accelerometer/Gyroscope:**
```bash
# Interactive menu interface
make run_mpu6050_menu

# Continuous ST7789 display
make run_mpu6050_display

# Scan I2C bus for diagnostics
make scan_i2c
```
*   Reads acceleration (g), gyroscope (°/s), and temperature (°C).
*   Menu interface with wake/sleep cycles.
*   Real-time display with color-coded sections.
*   See `mpu6050/README.md` for detailed documentation.

**Interactive Menu:**
```bash
make run
```
*   Selects the project to run from a menu.

**Port Selection:**
The first time you run a command, you will be prompted to select your ESP32's serial port. This selection is saved to a `.port` file. To reset it:
```bash
make reset_port
```

## Driver Details (`st7789.py`)

The driver supports:
- 320x240, 240x240, 135x240, and 128x128 pixel displays.
- Display rotation (Portrait, Landscape, Inverted).
- RGB and BGR color modes.
- Text drawing with bitmap fonts.
- Basic shapes (lines, rectangles, polygons) and bitmaps.
- Fast SPI communication.

## MAX30100 Details (`sensor.py`)

The MAX30100 driver provides:
- I2C communication implementation.
- Heart Rate (BPM) and SpO2 calculation algorithms.
- Temperature reading.
- FIFO buffer management for raw IR and Red LED data.
- Configurable sample rates and LED pulse widths.

To use it in your own code:
```python
from max30100.sensor import MAX30100, MAX30100Communication
import machine

i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
comm = MAX30100Communication(i2c)
sensor = MAX30100(comm)

if sensor.initialize():
    sensor.configure(mode='spo2')
    while True:
        if sensor.is_ready():
            data = sensor.read_processed_data()
            print(f"HR: {data['heart_rate']}, SpO2: {data['spo2']}")
```

## HC-SR04 Details (`hcsr04/driver.py`)

The HC-SR04 ultrasonic distance sensor driver provides:
- Simple trigger/echo pin interface
- Distance measurements in cm, mm, and inches
- Statistical analysis (min, max, avg, median)
- Object detection within threshold
- Proper timing and timeout handling

**Key Features:**
- **Range**: 2cm - 400cm (±3mm accuracy)
- **Timing**: Automatic 10μs trigger pulse
- **Timeout**: 38ms for ~6.5m max range
- **Multiple Units**: cm, mm, inches

To use it in your own code:
```python
from hcsr04 import HCSR04
import time

# Initialize sensor (adjust pins as needed)
sensor = HCSR04(trigger_pin=12, echo_pin=14)

# Read distance
while True:
    distance = sensor.read_distance_cm()
    if distance > 0:
        print(f"Distance: {distance:.2f} cm")
    else:
        print("Out of range")
    time.sleep_ms(100)

# Statistical analysis
stats = sensor.read_multiple(samples=10)
print(f"Average: {stats['avg']} cm")

# Object detection
if sensor.is_object_detected(threshold_cm=30):
    print("Object detected!")
```

**Important:** HC-SR04 ECHO pin outputs 5V. Use a voltage divider to protect ESP32 GPIO pins. See `hcsr04/README.md` for complete wiring diagrams and safety information.

## MPU6050 Details (`mpu6050/driver.py`)

The MPU6050 driver uses the **Bridge Pattern** to separate device communication from data processing:

**Device Layer (`MPU6050Device`):**
- Low-level I2C communication
- Register access and power management
- Connection verification with diagnostics
- Error handling (strict/non-strict modes)

**Sensor Layer (`MPU6050Sensor`):**
- Temperature conversion (°C)
- Acceleration conversion (g)
- Gyroscope conversion (°/s)
- Data aggregation

**Key Features:**
- **Range**: ±2g (accel), ±250°/s (gyro), -40°C to +85°C
- **Error Handling**: Graceful degradation with diagnostics
- **Power Management**: Wake/sleep cycle support
- **I2C Scanner**: Built-in diagnostic tool

To use it in your own code:
```python
from mpu6050.driver import MPU6050Device, MPU6050Sensor
from machine import I2C, Pin

i2c = I2C(0, scl=Pin(17), sda=Pin(18), freq=400000)
device = MPU6050Device(i2c, strict=False)  # Non-strict mode

if device.connected:
    sensor = MPU6050Sensor(device)
    sensor.activate()
    
    data = sensor.get_all_data()
    print(f"Temp: {data['temperature']}°C")
    print(f"Accel: {data['acceleration']}")
    print(f"Gyro: {data['gyroscope']}")
    
    sensor.deactivate()
```

**Troubleshooting:**
If the sensor is not detected, run the I2C scanner:
```bash
make scan_i2c
```
This will show all connected I2C devices and help diagnose connection issues.