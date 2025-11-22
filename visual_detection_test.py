#!/usr/bin/env python3
"""
Visual test - shows where like buttons are detected with red boxes
"""

import pyautogui
import time
from pathlib import Path
from PIL import Image, ImageDraw
import config

print("=" * 60)
print("VISUAL LIKE BUTTON DETECTION TEST")
print("=" * 60)

print("\nMake sure Instagram main feed is visible!")
print("Taking screenshot in 3 seconds...")
time.sleep(3)

# Take screenshot
search_region = config.PIXEL_MATCHING['search_region']
print(f"\nSearch region: {search_region}")

if search_region:
    print("Taking screenshot of search region...")
    screenshot = pyautogui.screenshot(region=search_region)
    # For drawing, we need to adjust coordinates
    offset_x, offset_y = search_region[0], search_region[1]
else:
    print("Taking full screenshot...")
    screenshot = pyautogui.screenshot()
    offset_x, offset_y = 0, 0

# Try to find like buttons
ref_images = config.PIXEL_MATCHING['like_button_images']
confidence = config.PIXEL_MATCHING['confidence']

print(f"\nSearching for like buttons...")
print(f"Reference images: {ref_images}")
print(f"Confidence: {confidence}")

found_any = False
draw = ImageDraw.Draw(screenshot)

for img_name in ref_images:
    img_path = Path('reference_images') / img_name
    
    if not img_path.exists():
        print(f"\n✗ {img_name} not found")
        continue
    
    print(f"\nTrying {img_name}...")
    
    # Try different confidence levels
    for conf in [0.9, 0.8, 0.7, 0.6, 0.5]:
        try:
            matches = list(pyautogui.locateAllOnScreen(
                str(img_path),
                confidence=conf,
                region=search_region,
                grayscale=False
            ))
            
            if matches:
                print(f"  ✓ Found {len(matches)} match(es) at confidence {conf}")
                
                for i, match in enumerate(matches):
                    # Adjust coordinates relative to screenshot
                    box_left = match.left - offset_x
                    box_top = match.top - offset_y
                    box_right = box_left + match.width
                    box_bottom = box_top + match.height
                    
                    # Draw red box
                    draw.rectangle(
                        [box_left, box_top, box_right, box_bottom],
                        outline='red',
                        width=3
                    )
                    
                    # Draw center point
                    center_x = box_left + match.width // 2
                    center_y = box_top + match.height // 2
                    draw.ellipse(
                        [center_x-5, center_y-5, center_x+5, center_y+5],
                        fill='red'
                    )
                    
                    print(f"    Match {i+1}: {match}")
                
                found_any = True
                break
                
        except Exception as e:
            if "Could not locate" not in str(e):
                print(f"  ✗ Error at confidence {conf}: {e}")
            continue

# Save result
output_dir = Path('screenshots')
output_dir.mkdir(exist_ok=True)
output_path = output_dir / 'detection_test.png'
screenshot.save(output_path)

print("\n" + "=" * 60)
if found_any:
    print("✓ LIKE BUTTONS DETECTED!")
    print("=" * 60)
    print(f"\nRed boxes show detected like buttons")
    print(f"Saved to: {output_path}")
    print("\nOpen the image to see where detection worked!")
else:
    print("✗ NO LIKE BUTTONS DETECTED")
    print("=" * 60)
    print(f"\nScreenshot saved to: {output_path}")
    print("\nThis shows what the script sees.")
    print("If you can see like buttons in the image but none were detected,")
    print("then the reference images don't match.")

print("\n" + "=" * 60)
