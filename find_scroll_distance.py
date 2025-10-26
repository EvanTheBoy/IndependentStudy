"""
Interactive tool to find the optimal scroll distance
"""
import pyautogui
import time


def test_scroll_distance():
    """
    Interactively test different scroll distances
    """
    print("=" * 60)
    print("SCROLL DISTANCE FINDER")
    print("=" * 60)
    print("\nThis tool helps you find the right scroll amount.")
    print("You'll test scrolling and see if buttons are visible.\n")

    # Get scroll starting position
    print("Step 1: Find your scroll starting position")
    print("Move mouse to where you want to START scrolling (usually middle of screen)")
    input("Press ENTER when mouse is in position...")
    scroll_start = pyautogui.position()
    print(f"✓ Scroll start position: {scroll_start}\n")

    # Test different distances
    print("Step 2: Test different scroll distances")
    print("We'll try scrolling different amounts.\n")

    test_distances = [100, 150, 200, 250, 300, 350, 400]

    for distance in test_distances:
        print(f"\n--- Testing scroll distance: {distance} pixels ---")
        print(f"This will scroll DOWN (drag UP) by {distance} pixels")
        print("Starting in 3 seconds...")
        time.sleep(3)

        # Perform scroll
        pyautogui.moveTo(scroll_start)
        pyautogui.drag(0, -distance, duration=0.5, button='left')  # Negative = scroll down

        print(f"✓ Scrolled {distance} pixels")
        print("\nCheck your iPhone Mirroring window:")
        print("  - Can you see the like button?")
        print("  - Can you see the comment button?")
        print("  - Is the post still mostly visible?")

        response = input("\nIs this scroll amount good? (y/n/q to quit): ").lower()

        if response == 'y':
            print(f"\n✓✓✓ Perfect! Use scroll distance: {distance}")
            print(f"\nIn your config.py, set:")
            print(f"  'scroll_start': {scroll_start}")
            print(f"  'scroll_end': ({scroll_start[0]}, {scroll_start[1] - distance})")
            print("\nOr use the drag command:")
            print(f"  pyautogui.drag(0, -{distance}, duration=0.5)")
            break
        elif response == 'q':
            print("Exiting...")
            break
        else:
            print("Trying next distance...")
            # Scroll back up a bit to reset
            time.sleep(1)
            pyautogui.moveTo(scroll_start)
            pyautogui.drag(0, distance, duration=0.3, button='left')  # Scroll back up
            time.sleep(1)

    print("\n" + "=" * 60)


def test_custom_distance():
    """
    Test a specific scroll distance you want to try
    """
    print("=" * 60)
    print("CUSTOM SCROLL DISTANCE TEST")
    print("=" * 60)

    distance = int(input("\nEnter scroll distance to test (pixels): "))

    print("\nMove mouse to scroll starting position...")
    input("Press ENTER when ready...")
    scroll_start = pyautogui.position()

    print(f"\nScrolling {distance} pixels in 3 seconds...")
    time.sleep(3)

    pyautogui.moveTo(scroll_start)
    pyautogui.drag(0, -distance, duration=0.5, button='left')

    print(f"✓ Scrolled {distance} pixels")
    print("Check if buttons are visible!")


if __name__ == "__main__":
    print("\nChoose mode:")
    print("1. Auto-test multiple distances (recommended)")
    print("2. Test specific distance")

    choice = input("\nEnter choice (1/2): ")

    if choice == "1":
        test_scroll_distance()
    else:
        test_custom_distance()
