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
	@echo "  make init          - Create virtual environment and install dependencies"
	@echo "  make run_test      - Deploy and run the Test project"
	@echo "  make run_clock     - Deploy and run the Clock project"
	@echo "  make clean         - Remove virtual environment and temporary files"
	@echo "  make reset_port    - Clear the saved port to select a new one"
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

# Flash Firmware
.PHONY: flash
flash: check_port
	$(VENV_PYTHON) tools/flash_firmware.py

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

# Generic Run Target (Interactive)
.PHONY: run
run: check_port
	@echo "Select project to run:"
	@echo "1) Test (sp7789_test.py)"
	@echo "2) Clock (clock_ui.py)"
	@echo "3) Simple SPI (simple_spi.py)"
	@echo "4) MAX30100 Sensor (example.py)"
	@read -p "Enter choice [1/2/3/4]: " choice; \
	if [ "$$choice" = "1" ]; then \
		$(MAKE) run_test; \
	elif [ "$$choice" = "2" ]; then \
		$(MAKE) run_clock; \
	elif [ "$$choice" = "3" ]; then \
		$(MAKE) run_simple; \
	elif [ "$$choice" = "4" ]; then \
		$(MAKE) run_sensor; \
	else \
		echo "Invalid choice."; \
	fi

# Clean
.PHONY: clean
clean:
	rm -rf $(VENV_DIR)
	rm -f $(PORT_FILE)
	@echo "Cleaned up."
