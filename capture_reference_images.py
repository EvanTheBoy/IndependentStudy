"""
Helper script to capture reference images for image recognition
"""
import pyautogui
import time
from pathlib import Path

REFERENCE_DIR = Path("reference_images")
REFERENCE_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("REFERENCE IMAGE CAPTURE TOOL")
print("=" * 60)
print("\nThis tool helps you capture reference images for automation.")
print("You'll capture small screenshots of UI elements.\n")

images_to_capture = [
    {
        "name": "back_button.png",
        "description": "Back button (← arrow) when viewing a post",
        "tip": "Select just the back arrow button"
    },
    {
        "name": "post_thumbnail.png",
        "description": "A post in the feed (any post)",
        "tip": "Select the center area of a post"
    },
    {
        "name": "post_center.png",
        "description": "Center of a post when opened (for liking)",
        "tip": "Select the middle of the post image"
    },
    {
        "name": "feed_area.png",
        "description": "General feed area (for scrolling)",
        "tip": "Select a neutral area in the feed"
    }
]

print("Instructions:")
print("1. Position your Instagram window where you want it")
print("2. For each image, you'll have 5 seconds to prepare")
print("3. Then click and drag to select the UI element")
print("4. The selected area will be saved as a reference image\n")

input("Press Enter to start...")

for i, img_info in enumerate(images_to_capture, 1):
    print(f"\n{'=' * 60}")
    print(f"Image {i}/{len(images_to_capture)}: {img_info['name']}")
    print(f"Description: {img_info['description']}")
    print(f"Tip: {img_info['tip']}")
    print(f"{'=' * 60}")
    
    print("\nPreparing in 5 seconds...")
    for countdown in range(5, 0, -1):
        print(f"  {countdown}...")
        time.sleep(1)
    
    print("\n✓ Now click and drag to select the area!")
    print("  (Move mouse to top-left, then drag to bottom-right)")
    
    try:
        # Let user select region
        region = pyautogui.screenshot()
        
        # Use PyAutoGUI's built-in region selector
        print("\n  Waiting for selection...")
        time.sleep(1)
        
        # Take screenshot of selected region
        # Note: User needs to manually select region using system screenshot tool
        print(f"\n  Please use your system screenshot tool (Cmd+Shift+4) to capture:")
        print(f"  {img_info['description']}")
        print(f"  Save it as: {REFERENCE_DIR / img_info['name']}")
        
        input(f"\n  Press Enter when you've saved {img_info['name']}...")
        
        # Check if file exists
        if (REFERENCE_DIR / img_info['name']).exists():
            print(f"  ✓ {img_info['name']} saved successfully!")
        else:
            print(f"  ⚠ Warning: {img_info['name']} not found in {REFERENCE_DIR}")
            retry = input("  Skip this image? (y/n): ")
            if retry.lower() != 'y':
                print("  Please save the image and press Enter...")
                input()
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        continue

print("\n" + "=" * 60)
print("REFERENCE IMAGE CAPTURE COMPLETE!")
print("=" * 60)
print(f"\nReference images saved in: {REFERENCE_DIR.absolute()}")
print("\nYou can now run: python3 instagram_automation_image_recognition.py")
print("=" * 60 + "\n")
