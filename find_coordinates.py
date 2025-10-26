"""
Coordinate Finder Tool
Helps you find the x,y coordinates of UI elements on the iPhone Mirroring screen
"""
import pyautogui
import time


def find_coordinates(countdown_seconds=5):
    """
    Wait for countdown, then display current mouse position

    Args:
        countdown_seconds: Time to wait before capturing position
    """
    print("=" * 50)
    print("COORDINATE FINDER TOOL")
    print("=" * 50)
    print(f"\nMove your mouse to the target position...")
    print(f"Coordinates will be displayed in {countdown_seconds} seconds\n")

    for i in range(countdown_seconds, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    x, y = pyautogui.position()
    print(f"\n✓ Current Position: ({x}, {y})")
    print(f"\nSave this coordinate for your automation script!")
    print("=" * 50)

    return (x, y)


if __name__ == "__main__":
    find_coordinates()
