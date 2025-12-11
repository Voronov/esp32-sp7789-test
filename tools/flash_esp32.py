#!/usr/bin/env python3
"""
ESP32 Firmware Flasher
Supports ESP32 WROOM and ESP32-S3 with automatic firmware download
"""

import sys
import os
import urllib.request
import subprocess
from pathlib import Path

# Check for esptool
try:
    import esptool
except ImportError:
    print("Error: esptool is not installed. Please run 'make init' first.")
    sys.exit(1)

FIRMWARE_DIR = "firmware"
PORT_FILE = ".port"

# Firmware URLs for different ESP32 variants
FIRMWARE_URLS = {
    "ESP32_WROOM": "https://micropython.org/resources/firmware/ESP32_GENERIC-20251209-v1.27.0.bin",
    "ESP32_S3": "https://micropython.org/resources/firmware/ESP32_GENERIC_S3-20251209-v1.27.0.bin"
}

def get_port():
    """Get port from saved file or prompt user using select_port.py"""
    if os.path.exists(PORT_FILE):
        with open(PORT_FILE, 'r') as f:
            port = f.read().strip()
            if port:
                return port
    
    # Port not found, run select_port.py
    print("\nNo port configured. Running port selection...")
    try:
        result = subprocess.run(
            [sys.executable, "tools/select_port.py"],
            check=True,
            capture_output=False
        )
        
        # Read the port that was saved
        if os.path.exists(PORT_FILE):
            with open(PORT_FILE, 'r') as f:
                port = f.read().strip()
                if port:
                    return port
        
        print("Error: No port was selected.")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("Error: Port selection failed.")
        sys.exit(1)

def select_esp32_type():
    """Prompt user to select ESP32 type"""
    print("\n" + "="*60)
    print("ESP32 Board Type Selection")
    print("="*60)
    print("\nSelect your ESP32 board type:")
    print("  1) ESP32 WROOM (Standard ESP32)")
    print("  2) ESP32-S3")
    print("  3) Custom firmware URL")
    
    while True:
        choice = input("\nEnter choice [1-3]: ").strip()
        
        if choice == "1":
            return "ESP32_WROOM", FIRMWARE_URLS["ESP32_WROOM"]
        elif choice == "2":
            return "ESP32_S3", FIRMWARE_URLS["ESP32_S3"]
        elif choice == "3":
            custom_url = input("Enter custom firmware URL: ").strip()
            if not custom_url:
                print("Error: URL cannot be empty.")
                continue
            return "CUSTOM", custom_url
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def download_firmware(firmware_url, board_type):
    """Download firmware from URL"""
    # Create firmware directory if it doesn't exist
    Path(FIRMWARE_DIR).mkdir(exist_ok=True)
    
    # Extract filename from URL
    filename = os.path.basename(firmware_url)
    if not filename.endswith('.bin'):
        filename = f"{board_type.lower()}_firmware.bin"
    
    local_path = os.path.join(FIRMWARE_DIR, filename)
    
    # Check if firmware already exists
    if os.path.exists(local_path):
        print(f"\nFirmware already exists: {local_path}")
        use_existing = input("Use existing firmware? [Y/n]: ").strip().lower()
        if use_existing in ['', 'y', 'yes']:
            return local_path
        else:
            os.remove(local_path)
    
    # Download firmware
    print(f"\nDownloading firmware from:")
    print(f"  {firmware_url}")
    print(f"Saving to: {local_path}")
    
    try:
        print("\nDownloading... ", end='', flush=True)
        urllib.request.urlretrieve(firmware_url, local_path)
        print("✓ Complete")
        return local_path
    except Exception as e:
        print(f"\n✗ Error downloading firmware: {e}")
        sys.exit(1)

def erase_flash(port):
    """Erase ESP32 flash memory"""
    print("\n" + "="*60)
    print("Step 1/2: Erasing Flash Memory")
    print("="*60)
    
    try:
        subprocess.check_call(
            [sys.executable, "-m", "esptool", "--port", port, "erase_flash"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        print("✓ Flash erased successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during erase: {e}")
        print("\nTroubleshooting:")
        print("  1. Check USB cable connection")
        print("  2. Try holding the BOOT button while erasing")
        print("  3. Verify the correct port is selected")
        return False

def flash_firmware(firmware_path, port, board_type):
    """Flash firmware to ESP32"""
    print("\n" + "="*60)
    print("Step 2/2: Flashing Firmware")
    print("="*60)
    print(f"Board Type: {board_type}")
    print(f"Firmware:   {firmware_path}")
    print(f"Port:       {port}")
    
    # Determine flash address based on board type
    # ESP32 WROOM uses 0x1000, ESP32-S3 also uses 0x1000
    flash_address = "0x1000"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "esptool",
            "--port", port,
            "--baud", "460800",
            "write_flash",
            "-z",
            flash_address,
            firmware_path
        ])
        print("\n" + "="*60)
        print("✓ SUCCESS! Firmware flashed successfully")
        print("="*60)
        print("\nYour ESP32 is ready to use!")
        print("You can now run: make run_test")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error during flashing: {e}")
        print("\nTroubleshooting:")
        print("  1. Check USB cable connection")
        print("  2. Try a lower baud rate (--baud 115200)")
        print("  3. Verify the correct board type was selected")
        return False

def main():
    print("="*60)
    print("ESP32 MicroPython Firmware Flasher")
    print("="*60)
    print("\nThis tool will:")
    print("  1. Erase your ESP32 flash memory")
    print("  2. Download MicroPython firmware")
    print("  3. Flash the firmware to your ESP32")
    
    # Get port
    port = get_port()
    print(f"\nUsing port: {port}")
    
    # Select ESP32 type
    board_type, firmware_url = select_esp32_type()
    
    # Download firmware
    firmware_path = download_firmware(firmware_url, board_type)
    
    # Confirm before proceeding
    print("\n" + "="*60)
    print("⚠️  WARNING")
    print("="*60)
    print("This will ERASE ALL DATA on your ESP32!")
    print("All files and programs will be permanently deleted.")
    
    confirm = input("\nType 'yes' to continue: ").strip().lower()
    if confirm != 'yes':
        print("\nOperation cancelled.")
        sys.exit(0)
    
    # Erase flash
    if not erase_flash(port):
        sys.exit(1)
    
    # Flash firmware
    if not flash_firmware(firmware_path, port, board_type):
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
