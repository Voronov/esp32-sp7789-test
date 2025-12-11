# Makefile for ESP32 ST7789 Project

# Configuration
ifneq ($(VIRTUAL_ENV),)
	VENV_DIR := $(VIRTUAL_ENV)
else
	VENV_DIR := .venv
endif

PYTHON ?= python3
VENV_PYTHON ?= $(VENV_DIR)/bin/python
PIP ?= $(VENV_DIR)/bin/pip
MPREMOTE ?= $(VENV_DIR)/bin/mpremote
PORT_FILE ?= .port

# Default target
.PHONY: help
help:
	@echo "ESP32 ST7789 Project Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make init             - Create virtual environment and install dependencies"
	@echo "  make flash_esp32      - Erase and flash ESP32 with MicroPython firmware"
	@echo "  make hello            - Run simple hello world test (verify firmware)"
	@echo "  make run_test         - Deploy and run the Test project"
	@echo "  make run_clock        - Deploy and run the Clock project"
	@echo "  make run_sensor       - Deploy and run MAX30100 sensor"
	@echo "  make run_hcsr04       - Deploy and run HC-SR04 with display"
	@echo "  make run_hcsr04_simple- Deploy and run HC-SR04 console only"
	@echo "  make run_mpu6050      - Deploy and run MPU6050 sensor (legacy)"
	@echo "  make run_mpu6050_menu - Deploy and run MPU6050 with menu interface"
	@echo "  make run_mpu6050_display - Deploy and run MPU6050 with ST7789 display"
	@echo "  make scan_i2c         - Scan I2C bus for connected devices"
	@echo "  make clean            - Remove virtual environment and temporary files"
	@echo "  make reset_port       - Clear the saved port to select a new one"
	@echo ""

# Initialize Environment
.PHONY: init
init:
	@echo "Initializing environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install mpremote pyserial esptool
	@echo "Environment ready."

# Port Selection Logic
.PHONY: check_port
check_port:
	@if [ ! -f $(PORT_FILE) ]; then \
		$(VENV_PYTHON) tools/select_port.py; \
	else \
		$(VENV_PYTHON) tools/select_port.py; \
	fi

.PHONY: reset_port
reset_port:
	rm -f $(PORT_FILE)
	@echo "Port selection reset."

# Flash ESP32 with MicroPython Firmware
.PHONY: flash_esp32
flash_esp32: check_port
	$(VENV_PYTHON) tools/flash_esp32.py

# Flash Firmware (legacy)
.PHONY: flash
flash: check_port
	$(VENV_PYTHON) tools/flash_firmware.py

# Run Hello World Test
.PHONY: hello
hello: check_port
	@echo "---------------------------------------------------"
	@echo "Running Hello World Test on $$(cat $(PORT_FILE))..."
	@echo "---------------------------------------------------"
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) run test/hello_world.py

# Run Test Project
.PHONY: run_test
run_test: check_port
	@echo "---------------------------------------------------"
	@echo "Deploying Test Project to $$(cat $(PORT_FILE))..."
	@# Copy Driver
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp driver/st7789.py :st7789.py
	@# Copy Test Script
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp test/sp7789_test.py :sp7789_test.py
	@echo "Files copied. Running test..."
	@# Run the test script
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) run test/sp7789_test.py

# Run Clock Project
.PHONY: run_clock
run_clock: check_port
	@echo "---------------------------------------------------"
	@echo "Deploying Clock Project to $$(cat $(PORT_FILE))..."
	@# Copy Driver
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp driver/st7789.py :st7789.py
	@# Copy Font
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp clock/vga2_bold_16x32.py :vga2_bold_16x32.py
	@# Copy Clock UI
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp clock/clock_ui.py :clock_ui.py
	@echo "Files copied. Running clock..."
	@# Run the clock script
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) run clock/clock_ui.py

# Run Simple SPI Project
.PHONY: run_simple
run_simple: check_port
	@echo "---------------------------------------------------"
	@echo "Deploying Simple SPI Project to $$(cat $(PORT_FILE))..."
	@# Copy Simple SPI Script
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp simple_spi/simple_spi.py :simple_spi.py
	@echo "File copied. Running simple SPI test..."
	@# Run the script
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) run simple_spi/simple_spi.py

# Run MAX30100 Sensor Project
.PHONY: run_sensor
run_sensor: check_port
	@echo "---------------------------------------------------"
	@echo "Deploying MAX30100 Sensor Project to $$(cat $(PORT_FILE))..."
	@# Create max30100 directory on device
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs mkdir :max30100 || true
	@# Copy Driver and Font to root
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp driver/st7789.py :st7789.py
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp clock/vga2_bold_16x32.py :vga2_bold_16x32.py
	@# Copy Sensor Files
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp max30100/sensor_interface.py :max30100/sensor_interface.py
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp max30100/constants.py :max30100/constants.py
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp max30100/comm.py :max30100/comm.py
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp max30100/device.py :max30100/device.py
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp max30100/example.py :max30100/example.py
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp max30100/__init__.py :max30100/__init__.py
	@echo "Files copied. Running sensor demo..."
	@# Run the sensor script
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) run max30100/example.py

# Run HC-SR04 Distance Sensor with Display
.PHONY: run_hcsr04
run_hcsr04: check_port
	@echo "---------------------------------------------------"
	@echo "Deploying HC-SR04 Project to $$(cat $(PORT_FILE))..."
	@# Create hcsr04 directory on device
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs mkdir :hcsr04 || true
	@# Copy Driver and Font to root
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp driver/st7789.py :st7789.py
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp clock/vga2_bold_16x32.py :vga2_bold_16x32.py
	@# Copy HC-SR04 Files
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp hcsr04/driver.py :hcsr04/driver.py
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp hcsr04/__init__.py :hcsr04/__init__.py
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp hcsr04/example.py :hcsr04/example.py
	@echo "Files copied. Running HC-SR04 demo with display..."
	@# Run the script
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) run hcsr04/example.py

# Run HC-SR04 Simple Console Example
.PHONY: run_hcsr04_simple
run_hcsr04_simple: check_port
	@echo "---------------------------------------------------"
	@echo "Running HC-SR04 Simple Console Example on $$(cat $(PORT_FILE))..."
	@# Create hcsr04 directory on device
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs mkdir :hcsr04 || true
	@# Copy HC-SR04 Files
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp hcsr04/driver.py :hcsr04/driver.py
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp hcsr04/__init__.py :hcsr04/__init__.py
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp hcsr04/example_simple.py :hcsr04/example_simple.py
	@echo "Files copied. Running HC-SR04 simple demo..."
	@# Run the script
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) run hcsr04/example_simple.py

# Run MPU6050 Accelerometer/Gyroscope Sensor (Legacy)
.PHONY: run_mpu6050
run_mpu6050: check_port
	@echo "---------------------------------------------------"
	@echo "Deploying MPU6050 Project to $$(cat $(PORT_FILE))..."
	@# Create mpu6050 directory on device
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs mkdir :mpu6050 || true
	@# Copy MPU6050 Files
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp mpu6050/example.py :mpu6050/example.py
	@echo "Files copied. Running MPU6050 demo..."
	@# Run the script
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) run mpu6050/example.py

# Run MPU6050 with Menu Interface
.PHONY: run_mpu6050_menu
run_mpu6050_menu: check_port
	@echo "---------------------------------------------------"
	@echo "Deploying MPU6050 Menu Project to $$(cat $(PORT_FILE))..."
	@# Create mpu6050 directory on device
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs mkdir :mpu6050 || true
	@# Copy MPU6050 Files
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp mpu6050/driver.py :mpu6050/driver.py
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp mpu6050/example_menu.py :mpu6050/example_menu.py
	@echo "Files copied. Running MPU6050 menu demo..."
	@# Run the script
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) run mpu6050/example_menu.py

# Run MPU6050 with ST7789 Display
.PHONY: run_mpu6050_display
run_mpu6050_display: check_port
	@echo "---------------------------------------------------"
	@echo "Deploying MPU6050 Display Project to $$(cat $(PORT_FILE))..."
	@# Create mpu6050 directory on device
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs mkdir :mpu6050 || true
	@# Copy Driver to root
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp driver/st7789.py :st7789.py
	@# Copy MPU6050 Files
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp mpu6050/driver.py :mpu6050/driver.py
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp mpu6050/example_display.py :mpu6050/example_display.py
	@echo "Files copied. Running MPU6050 display demo..."
	@# Run the script
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) run mpu6050/example_display.py

# Scan I2C Bus
.PHONY: scan_i2c
scan_i2c: check_port
	@echo "---------------------------------------------------"
	@echo "Scanning I2C Bus on $$(cat $(PORT_FILE))..."
	@# Create mpu6050 directory on device
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs mkdir :mpu6050 || true
	@# Copy I2C scanner
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) fs cp mpu6050/i2c_scanner.py :mpu6050/i2c_scanner.py
	@echo "Running I2C scanner..."
	@# Run the scanner
	$(MPREMOTE) connect $$(cat $(PORT_FILE)) run mpu6050/i2c_scanner.py

# Generic Run Target (Interactive)
.PHONY: run
run: check_port
	@echo "Select project to run:"
	@echo "1) Test (sp7789_test.py)"
	@echo "2) Clock (clock_ui.py)"
	@echo "3) Simple SPI (simple_spi.py)"
	@echo "4) MAX30100 Sensor (example.py)"
	@echo "5) HC-SR04 Distance Sensor (with display)"
	@echo "6) HC-SR04 Simple (console only)"
	@echo "7) MPU6050 Accelerometer/Gyroscope"
	@read -p "Enter choice [1-7]: " choice; \
	if [ "$$choice" = "1" ]; then \
		$(MAKE) run_test; \
	elif [ "$$choice" = "2" ]; then \
		$(MAKE) run_clock; \
	elif [ "$$choice" = "3" ]; then \
		$(MAKE) run_simple; \
	elif [ "$$choice" = "4" ]; then \
		$(MAKE) run_sensor; \
	elif [ "$$choice" = "5" ]; then \
		$(MAKE) run_hcsr04; \
	elif [ "$$choice" = "6" ]; then \
		$(MAKE) run_hcsr04_simple; \
	elif [ "$$choice" = "7" ]; then \
		$(MAKE) run_mpu6050; \
	else \
		echo "Invalid choice."; \
	fi

# Clean
.PHONY: clean
clean:
	rm -rf $(VENV_DIR)
	rm -f $(PORT_FILE)
	@echo "Cleaned up."