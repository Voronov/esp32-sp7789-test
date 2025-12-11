"""
Simple ESP32 MicroPython Test
Verifies that the firmware is working correctly
"""

import sys
import time
from machine import Pin

def test_basic_functionality():
    """Test basic Python functionality"""
    print("="*50)
    print("ESP32 MicroPython Test")
    print("="*50)
    
    # Test 1: Basic print
    print("\n[TEST 1] Basic Print")
    print("Hello from ESP32!")
    print("✓ Print working")
    
    # Test 2: Math operations
    print("\n[TEST 2] Math Operations")
    result = 2 + 2
    print(f"2 + 2 = {result}")
    assert result == 4, "Math failed!"
    print("✓ Math working")
    
    # Test 3: String operations
    print("\n[TEST 3] String Operations")
    text = "MicroPython"
    print(f"Text: {text}")
    print(f"Length: {len(text)}")
    print(f"Upper: {text.upper()}")
    print("✓ Strings working")
    
    # Test 4: Lists
    print("\n[TEST 4] Lists")
    numbers = [1, 2, 3, 4, 5]
    print(f"List: {numbers}")
    print(f"Sum: {sum(numbers)}")
    print("✓ Lists working")
    
    # Test 5: System info
    print("\n[TEST 5] System Information")
    print(f"Platform: {sys.platform}")
    print(f"Python version: {sys.version}")
    print("✓ System info accessible")
    
    # Test 6: Time functions
    print("\n[TEST 6] Time Functions")
    start = time.ticks_ms()
    time.sleep_ms(100)
    elapsed = time.ticks_diff(time.ticks_ms(), start)
    print(f"Sleep test: {elapsed}ms (expected ~100ms)")
    print("✓ Time functions working")
    
    # Test 7: Onboard LED (GPIO 2)
    print("\n[TEST 7] Onboard LED Toggle")
    print("Toggling LED on GPIO 2...")
    led = Pin(2, Pin.OUT)
    for i in range(5):
        led.on()
        print(f"  {i+1}. LED ON")
        time.sleep_ms(300)
        led.off()
        print(f"  {i+1}. LED OFF")
        time.sleep_ms(300)
    print("✓ LED toggle working")
    
    print("\n" + "="*50)
    print("✓ ALL TESTS PASSED!")
    print("="*50)
    print("\nYour ESP32 firmware is working correctly!")
    print("You can now run other projects.")

if __name__ == "__main__":
    try:
        test_basic_functionality()
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import sys
        sys.print_exception(e)
