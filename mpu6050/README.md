# MPU6050 Sensor Driver

MPU6050 6-axis accelerometer and gyroscope sensor driver with bridge pattern architecture.

## Architecture

The driver uses the **Bridge Pattern** to separate concerns:

### Device Layer (Implementation)
- **`MPU6050Device`**: Low-level I2C communication
  - Direct register access
  - Wake/sleep control
  - Raw data reading

### Sensor Layer (Abstraction)
- **`MPU6050Sensor`**: High-level data processing
  - Temperature conversion (°C)
  - Acceleration conversion (g)
  - Gyroscope conversion (°/s)
  - Data aggregation

## Files

- **`driver.py`**: Core driver with bridge pattern implementation
- **`example_menu.py`**: Interactive menu-based example
- **`example_display.py`**: Continuous ST7789 display example
- **`example.py`**: Legacy example (deprecated)

## Hardware Setup

### I2C Connections
- **SCL**: GPIO 17
- **SDA**: GPIO 18
- **I2C Address**: 0x68 (default)

### ST7789 Display (for example_display.py)
- **SCK**: GPIO 14
- **MOSI**: GPIO 13
- **RESET**: GPIO 23
- **DC**: GPIO 16
- **CS**: GPIO 15
- **Backlight**: GPIO 4

## Usage

### Example 1: Menu-Based Interface

Interactive menu with wake/sleep cycles for each operation.

```python
from machine import I2C, Pin
from driver import MPU6050Device, MPU6050Sensor
from example_menu import MPU6050Menu

i2c = I2C(0, scl=Pin(17), sda=Pin(18), freq=400000)
device = MPU6050Device(i2c)
sensor = MPU6050Sensor(device)

menu = MPU6050Menu(sensor)
menu.run()
```

**Features:**
1. Get Temperature - Single temperature reading
2. Get All Data - Temperature, acceleration, and gyroscope
3. Get 100 Readings - Statistics from 100 temperature samples
4. Exit

Each operation wakes the sensor, reads data, and puts it back to sleep.

### Example 2: Continuous Display

Real-time sensor data display on ST7789 TFT screen.

```python
from machine import I2C, Pin
from driver import MPU6050Device, MPU6050Sensor
from example_display import MPU6050Display, init_display

i2c = I2C(0, scl=Pin(17), sda=Pin(18), freq=400000)
device = MPU6050Device(i2c)
sensor = MPU6050Sensor(device)

display = init_display()
mpu_display = MPU6050Display(display, sensor)
mpu_display.run(update_interval_ms=500)
```

**Features:**
- Color-coded sections for each data type
- Real-time updates (configurable interval)
- Update counter
- Clean visual layout

### Basic Usage

```python
from machine import I2C, Pin
from driver import MPU6050Device, MPU6050Sensor

# Initialize I2C
i2c = I2C(0, scl=Pin(17), sda=Pin(18), freq=400000)

# Create device and sensor
device = MPU6050Device(i2c)
sensor = MPU6050Sensor(device)

# Wake up sensor
sensor.activate()

# Read data
temp = sensor.get_temperature()
accel = sensor.get_acceleration()
gyro = sensor.get_gyro()
all_data = sensor.get_all_data()

# Sleep sensor
sensor.deactivate()
```

## API Reference

### MPU6050Device

Low-level device interface.

**Methods:**
- `wake_up()`: Wake sensor from sleep mode
- `sleep()`: Put sensor into sleep mode
- `read_temperature()`: Read raw temperature bytes
- `read_accelerometer()`: Read raw accelerometer bytes
- `read_gyroscope()`: Read raw gyroscope bytes

### MPU6050Sensor

High-level sensor interface.

**Methods:**
- `activate()`: Wake up the sensor
- `deactivate()`: Put sensor to sleep
- `is_active()`: Check if sensor is awake
- `get_temperature()`: Get temperature in °C
- `get_acceleration()`: Get acceleration dict (x, y, z in g)
- `get_gyro()`: Get gyroscope dict (x, y, z in °/s)
- `get_all_data()`: Get all sensor data in one dict

**Data Formats:**

```python
# Temperature
temp = 25.43  # float in °C

# Acceleration
accel = {
    'x': 0.012,  # g
    'y': -0.003,  # g
    'z': 0.998   # g
}

# Gyroscope
gyro = {
    'x': 1.23,   # °/s
    'y': -0.45,  # °/s
    'z': 0.12    # °/s
}

# All data
data = {
    'temperature': 25.43,
    'acceleration': {'x': 0.012, 'y': -0.003, 'z': 0.998},
    'gyroscope': {'x': 1.23, 'y': -0.45, 'z': 0.12}
}
```

## Sensor Specifications

- **Temperature Range**: -40°C to +85°C
- **Temperature Sensitivity**: 340 LSB/°C
- **Accelerometer Range**: ±2g (default)
- **Accelerometer Sensitivity**: 16384 LSB/g
- **Gyroscope Range**: ±250°/s (default)
- **Gyroscope Sensitivity**: 131 LSB/(°/s)

## Power Management

The driver implements proper power management:

- Sensor starts in sleep mode after initialization
- Use `activate()` before reading data
- Use `deactivate()` to save power when not in use
- Menu example demonstrates wake/sleep cycles
- Display example keeps sensor active during continuous operation

## License

MIT License
