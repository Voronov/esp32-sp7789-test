# ESP32 ST7789 MicroPython Driver & Clock Demo

This project provides a MicroPython driver for ST7789-based displays and includes a demo application featuring a digital clock and screensaver.

## Project Structure

```
├── clock/
│   ├── clock_ui.py        # Main demo application (Clock + Screensaver)
│   └── vga2_bold_16x32.py # Bitmap font file
├── driver/
│   └── st7789.py          # ST7789 Display Driver Library
├── test/
│   └── sp7789_test.py     # Simple hardware test script
├── tools/
│   ├── flash_firmware.py  # Script to download and flash MicroPython
│   └── select_port.py     # Script to identify ESP32 serial port
└── Makefile               # Build and run automation
```

## Hardware Requirements

- **ESP32 Development Board**
- **ST7789 Display Module** (Demo configured for 240x240 resolution)

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

> **Note:** If your display module requires a Chip Select (CS) pin, update the pin definition in the code (currently set to `None`).

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
make flash
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