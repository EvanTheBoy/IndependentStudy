"""
Script A: Main Feed Like Automation
Scrolls through Instagram main feed and likes posts using pixel matching
"""

import pyautogui
import time
from pathlib import Path
import config
from utils import log_message, take_screenshot, setup_directories


def find_like_button(confidence=0.8, region=None, grayscale=True):
    """
    Find the like button using pixel matching

    Uses PyAutoGUI best practices:
    - Searches within region for speed (per official docs)
    - Uses grayscale for 30% speedup (per official docs)
    - Requires OpenCV for confidence parameter

    Tries multiple reference images (light and dark theme)
    Finds the topmost like button (first post in view)

    Args:
        confidence: Matching confidence threshold (0.0 to 1.0)
        region: Optional search region (left, top, width, height)
        grayscale: Use grayscale matching for speed (default: True, per PyAutoGUI docs)

    Returns:
        tuple: (x, y) coordinates if found, None otherwise
    """
    for image_name in config.PIXEL_MATCHING['like_button_images']:
        image_path = Path('reference_images') / image_name

        if not image_path.exists():
            log_message(f"Reference image not found: {image_path}", level="WARNING")
            continue

        log_message(f"Trying to find like button using: {image_name}")
        log_message(f"  Confidence: {confidence}, Grayscale: {grayscale}, Region: {region}")

        try:
            # Use locateOnScreen first (faster than locateAllOnScreen)
            # Only use locateAllOnScreen if we need to find multiple matches
            location = pyautogui.locateOnScreen(
                str(image_path),
                confidence=confidence,
                region=region,
                grayscale=grayscale  # 30% speedup per PyAutoGUI docs
            )

            if location:
                # Instead of using center, click on the left-center of the matched region
                # This ensures we click on the heart icon, not the empty space
                # location is (left, top, width, height)
                left, top, width, height = location
                # Click 25% from the left edge and vertically centered
                click_x = left + int(width * 0.25)
                click_y = top + int(height * 0.5)
                click_point = (click_x, click_y)

                log_message(f"✓ Found like button with {image_name} at region {location}", level="SUCCESS")
                log_message(f"Will click at adjusted position: {click_point} (left-center of match)")
                return click_point
            else:
                log_message(f"  ✗ No match found with {image_name}", level="WARNING")

        except pyautogui.ImageNotFoundException:
            # Image not found, try next reference image
            log_message(f"  ✗ Image not found on screen: {image_name}", level="WARNING")
            continue
        except Exception as e:
            log_message(f"  ✗ Error searching for {image_name}: {e}", level="WARNING")

    return None


def like_post_in_feed():
    """
    Like a post in the main feed by clicking the like button
    
    Uses pixel matching with fallback to coordinates

    Returns:
        bool: True if successful, False otherwise
    """
    log_message("Liking post...")

    # Try pixel matching first
    button_location = find_like_button(
        confidence=config.PIXEL_MATCHING['confidence'],
        region=config.PIXEL_MATCHING['search_region'],
        grayscale=config.PIXEL_MATCHING['grayscale']
    )
    
    if button_location:
        log_message(f"✓ Found like button with pixel matching at {button_location}", level="SUCCESS")
    else:
        log_message("Pixel matching failed, using static coordinates", level="WARNING")
        button_location = config.COORDINATES['like_button']
    
    # Click the button
    log_message(f"Clicking like button at {button_location}")
    pyautogui.click(button_location)

    # Wait for animation
    time.sleep(config.TIMING['wait_after_like'])

    log_message("Post liked successfully", level="SUCCESS")
    return True


def scroll_main_feed():
    """
    Scroll down the main feed to reveal new posts
    """
    import random
    
    log_message("Scrolling main feed...")
    
    # Get current mouse position (should be on Instagram after clicking like button)
    current_pos = pyautogui.position()
    log_message(f"Scrolling at current position: {current_pos}")
    
    # Perform scroll with randomization for more natural behavior
    scroll_amount = config.AUTOMATION['main_feed_scroll_amount']
    scroll_attempts = config.AUTOMATION['main_feed_scroll_attempts']
    
    for _ in range(scroll_attempts):
        # Add ±20% randomness to scroll amount
        random_scroll = int(scroll_amount * random.uniform(0.8, 1.2))
        pyautogui.scroll(random_scroll)
        time.sleep(random.uniform(0.1, 0.2))
    
    # Wait for content to load
    time.sleep(config.TIMING['wait_after_scroll'])


def run_like_cycle(run_number, total_runs):
    """
    Execute one complete scroll-and-like cycle on main feed
    
    Args:
        run_number: Current run number
        total_runs: Total number of runs
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        log_message("=" * 50)
        log_message(f"Run {run_number}/{total_runs}", level="INFO")
        log_message("=" * 50)
        
        # 1. Scroll to reveal new post
        scroll_main_feed()
        
        # 2. Find and like the post
        success = like_post_in_feed()
        
        # 3. Take screenshot if enabled
        if success and config.AUTOMATION['enable_screenshots']:
            take_screenshot(f"main_feed_like_{run_number}")
        
        # 4. Wait before next cycle
        time.sleep(config.TIMING['wait_between_runs'])
        
        log_message(f"Run {run_number} completed", level="SUCCESS")
        return success
        
    except Exception as e:
        log_message(f"Run {run_number} failed: {e}", level="ERROR")
        return False


def main():
    """
    Main function for Script A: Main Feed Like automation
    
    Initializes automation, runs like cycles, and displays summary
    """
    # Setup
    setup_directories()
    
    # Enable PyAutoGUI failsafe if configured
    pyautogui.FAILSAFE = config.AUTOMATION['enable_failsafe']
    
    log_message("=" * 50)
    log_message("Script A: Main Feed Like Automation", level="INFO")
    log_message("=" * 50)
    log_message(f"Number of runs: {config.AUTOMATION['number_of_runs']}")
    log_message(f"Screenshots enabled: {config.AUTOMATION['enable_screenshots']}")
    log_message(f"Failsafe enabled: {config.AUTOMATION['enable_failsafe']}")
    
    if config.AUTOMATION['enable_failsafe']:
        log_message("Move mouse to corner to stop automation", level="WARNING")
    
    # Countdown
    log_message("\nStarting in 3 seconds...")
    for i in range(3, 0, -1):
        log_message(f"{i}...")
        time.sleep(1)
    
    log_message("Starting automation!\n")
    
    # Track statistics
    successful_cycles = 0
    failed_cycles = 0
    
    try:
        # Run automation cycles
        for run_num in range(1, config.AUTOMATION['number_of_runs'] + 1):
            success = run_like_cycle(run_num, config.AUTOMATION['number_of_runs'])
            
            if success:
                successful_cycles += 1
            else:
                failed_cycles += 1
    
    except pyautogui.FailSafeException:
        log_message("\nFailsafe triggered! Mouse moved to corner.", level="WARNING")
        log_message("Automation stopped by user.", level="INFO")
    
    except KeyboardInterrupt:
        log_message("\nKeyboard interrupt detected!", level="WARNING")
        log_message("Automation stopped by user.", level="INFO")
    
    except Exception as e:
        log_message(f"\nUnexpected error: {e}", level="ERROR")
    
    finally:
        # Display summary
        log_message("\n" + "=" * 50)
        log_message("AUTOMATION SUMMARY", level="INFO")
        log_message("=" * 50)
        log_message(f"Total runs attempted: {successful_cycles + failed_cycles}")
        log_message(f"Successful: {successful_cycles}", level="SUCCESS")
        log_message(f"Failed: {failed_cycles}", level="ERROR")
        
        if successful_cycles + failed_cycles > 0:
            success_rate = (successful_cycles / (successful_cycles + failed_cycles)) * 100
            log_message(f"Success rate: {success_rate:.1f}%")
        
        log_message("=" * 50)
        log_message("Automation complete!", level="SUCCESS")


if __name__ == "__main__":
    main()
