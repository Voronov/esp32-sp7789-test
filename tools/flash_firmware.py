import sys
import os
import re
import urllib.request
import subprocess

# Check for esptool
try:
    import esptool
except ImportError:
    print("Error: esptool is not installed. Please run 'make init' first.")
    sys.exit(1)

FIRMWARE_DIR = "firmware"
BASE_URL = "https://micropython.org/download/ESP32_GENERIC/"
PORT_FILE = ".port"

def get_port():
    if os.path.exists(PORT_FILE):
        with open(PORT_FILE, 'r') as f:
            return f.read().strip()
    return None

def download_latest_firmware():
    print(f"Checking {BASE_URL} for latest firmware...")
    try:
        with urllib.request.urlopen(BASE_URL) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching MicroPython page: {e}")
        sys.exit(1)

    # Find .bin links.
    # The page usually lists releases. We want the first .bin link in the releases section.
    # Pattern example: /resources/firmware/ESP32_GENERIC-20240105-v1.22.1.bin
    
    # Find all hrefs pointing to a bin file
    matches = re.findall(r'href=\"(/resources/firmware/ESP32_GENERIC-[0-9]+-v[0-9\.]+\.bin)\"', html)
    
    if not matches:
         print("No release firmware found.")
         sys.exit(1)

    # Pick the first one, assuming it's the latest stable release
    firmware_path = matches[0]
    firmware_url = "https://micropython.org" + firmware_path
    filename = os.path.basename(firmware_path)
    local_path = os.path.join(FIRMWARE_DIR, filename)

    if not os.path.exists(FIRMWARE_DIR):
        os.makedirs(FIRMWARE_DIR)

    if os.path.exists(local_path):
        print(f"Firmware already exists: {local_path}")
        return local_path

    print(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(firmware_url, local_path)
        print("Download complete.")
    except Exception as e:
        print(f"Failed to download: {e}")
        sys.exit(1)
    
    return local_path

def flash_firmware(firmware_path, port):
    print("\n---------------------------------------------------")
    print(f"Target Port: {port}")
    print(f"Firmware:    {firmware_path}")
    print("---------------------------------------------------")
    print("Warning: This will ERASE all data on the ESP32 and flash new firmware.")
    confirm = input("Type 'yes' to continue: ")
    if confirm.strip().lower() != 'yes':
        print("Aborted.")
        sys.exit(0)

    # Erase
    print(f"\n[1/2] Erasing flash...")
    try:
        subprocess.check_call([sys.executable, "-m", "esptool", "--port", port, "erase_flash"])
    except subprocess.CalledProcessError:
        print("Error during erase. Please check connections and try holding the BOOT button.")
        sys.exit(1)
    
    # Flash
    # Address 0x1000 is typical for ESP32 generic
    print(f"\n[2/2] Flashing firmware...")
    try:
        subprocess.check_call([sys.executable, "-m", "esptool", "--port", port, "--baud", "460800", "write_flash", "-z", "0x1000", firmware_path])
        print("\nSuccess! Firmware updated.")
    except subprocess.CalledProcessError:
        print("Error during flashing.")
        sys.exit(1)

def main():
    print("MicroPython Firmware Flasher")
    print("----------------------------")
    print("This tool downloads the latest ESP32_GENERIC firmware and flashes it.")
    
    # Ask for chip type
    print("\n[CHECK] Confirm your ESP32 Board Type.")
    print("This firmware is for 'ESP32_GENERIC' (Standard ESP32-WROOM/WROVER).")
    print("It is NOT compatible with ESP32-S2, ESP32-S3, ESP32-C3, etc.")
    
    chip_type = input("Is your board a standard ESP32? [y/n]: ").strip().lower()
    if chip_type not in ['y', 'yes']:
        print("\n[STOPPING] Incompatible Board.")
        print("The automated download only supports ESP32_GENERIC.")
        print("If you have an S2, S3, or C3, please download the correct firmware")
        print("from https://micropython.org/download/ and flash it manually.")
        sys.exit(1)

    port = get_port()
    if not port:
        print("No port selected. Please run 'make check_port' or 'make run' first to select a port.")
        sys.exit(1)
    
    firmware_path = download_latest_firmware()
    flash_firmware(firmware_path, port)

if __name__ == "__main__":
    main()
