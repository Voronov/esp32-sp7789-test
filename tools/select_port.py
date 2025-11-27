import sys
import os

try:
    from serial.tools import list_ports
except ImportError:
    print("Error: pyserial is not installed. Please run 'make init' first.")
    sys.exit(1)

def select_port():
    print("Scanning for serial ports...")
    ports = list(list_ports.comports())
    
    # Filter out likely irrelevant ports (Bluetooth, etc) if desired, 
    # but often it's better to show them just in case.
    # We'll show everything but maybe highlight USB ones.
    
    usb_ports = [p for p in ports if 'usb' in p.device.lower() or 'slab' in p.device.lower()]
    other_ports = [p for p in ports if p not in usb_ports]
    
    sorted_ports = usb_ports + other_ports

    if not sorted_ports:
        print("No serial ports found! Please connect your ESP32.")
        return None

    print("\nAvailable Serial Ports:")
    for i, p in enumerate(sorted_ports):
        desc = p.description
        if p.device == desc:
            desc = ""
        else:
            desc = f" ({desc})"
        print(f"{i + 1}) {p.device}{desc}")

    while True:
        try:
            selection = input("\nSelect port number (or 'q' to quit): ")
            if selection.lower() == 'q':
                return None
            
            index = int(selection) - 1
            if 0 <= index < len(sorted_ports):
                return sorted_ports[index].device
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    port_file = ".port"
    
    # Check if port file already exists and verify it's still valid
    if os.path.exists(port_file):
        with open(port_file, 'r') as f:
            saved_port = f.read().strip()
        # Verify it still exists
        current_ports = [p.device for p in list_ports.comports()]
        if saved_port in current_ports:
            print(f"Using saved port: {saved_port}")
            sys.exit(0)
        else:
            print(f"Saved port {saved_port} not found.")
    
    selected = select_port()
    if selected:
        with open(port_file, "w") as f:
            f.write(selected)
        print(f"Selected port {selected} saved to {port_file}")
    else:
        print("No port selected.")
        sys.exit(1)
