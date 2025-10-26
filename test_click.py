"""
Click Test Tool
Test if clicking at specific coordinates works correctly
"""
import pyautogui
import time

# Configuration
TEST_COORDINATES = (1179, 431)  # Replace with your coordinates
DELAY_SECONDS = 3


def test_single_click(x, y, delay=3):
    """
    Perform a single click at specified coordinates after a delay

    Args:
        x: X coordinate
        y: Y coordinate
        delay: Seconds to wait before clicking
    """
    print("=" * 50)
    print("CLICK TEST TOOL")
    print("=" * 50)
    print(f"\nTarget coordinates: ({x}, {y})")
    print(f"Clicking in {delay} seconds...")
    print("Make sure iPhone Mirroring window is visible!\n")

    for i in range(delay, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    pyautogui.click(x, y)
    print(f"\n✓ Clicked at ({x}, {y})")
    print("Check if the click worked correctly!")
    print("=" * 50)


if __name__ == "__main__":
    test_single_click(TEST_COORDINATES[0], TEST_COORDINATES[1], DELAY_SECONDS)
