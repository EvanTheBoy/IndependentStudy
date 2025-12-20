#!/usr/bin/env python3
"""
X (Twitter) Like Automation
Enters posts, likes them, and returns to feed using pixel matching
"""

import pyautogui
import time
import random
from pathlib import Path
from core import config
from core.utils import log_message, take_screenshot, setup_directories, get_iphone_mirroring_region

# X-specific reference images (in reference_images/X/ folder)
X_LIKE_BUTTON_IMAGES = ['X/x_like_button.png', 'X/x_like_button_dark.png']
X_BACK_BUTTON_IMAGES = ['X/x_back_button.png']

# Max scroll attempts when looking for buttons
MAX_SCROLL_ATTEMPTS = 3


def get_post_click_position():
    """
    Get the position to click to enter a post (left side white area).
    Uses relative position within iPhone Mirroring window.

    Returns:
        tuple: (x, y) coordinates to click, or None if window not found
    """
    region = get_iphone_mirroring_region()
    if not region:
        log_message("iPhone Mirroring window not found", level="ERROR")
        return None

    left, top, width, height = region
    # Click on the left side of the window, roughly middle height
    # Based on the screenshot, the left white area is about 15% from left edge
    click_x = int(left + width * 0.15)
    click_y = int(top + height * 0.55)  # Slightly below center to hit post content

    return (click_x, click_y)


def find_button(image_list, confidence=0.8, max_scroll_attempts=MAX_SCROLL_ATTEMPTS, scroll_direction='down'):
    """
    Find a button on screen, scrolling if necessary.

    Args:
        image_list: List of image filenames to search for
        confidence: Matching confidence threshold
        max_scroll_attempts: Max times to scroll while searching
        scroll_direction: 'down' or 'up'

    Returns:
        tuple: (x, y) center coordinates of button, or None if not found
    """
    region = get_iphone_mirroring_region()

    for attempt in range(max_scroll_attempts + 1):
        # Try each image variant
        for img_name in image_list:
            img_path = Path('..') / img_name

            if not img_path.exists():
                continue

            try:
                location = pyautogui.locateOnScreen(
                    str(img_path),
                    confidence=confidence,
                    grayscale=True,
                    region=region
                )

                if location:
                    center = pyautogui.center(location)
                    log_message(f"Found button using {img_name} at {center}", level="SUCCESS")
                    return center

            except pyautogui.ImageNotFoundException:
                pass
            except Exception as e:
                log_message(f"Error searching for {img_name}: {e}", level="WARNING")

        # Button not found, try scrolling
        if attempt < max_scroll_attempts:
            log_message(f"Button not found, scrolling {scroll_direction} (attempt {attempt + 1}/{max_scroll_attempts})")
            scroll_in_window(direction=scroll_direction)
            time.sleep(0.5)

    return None


def scroll_in_window(direction='down', amount=300):
    """
    Scroll within the iPhone Mirroring window.

    Args:
        direction: 'down' or 'up'
        amount: Scroll amount in pixels
    """
    region = get_iphone_mirroring_region()
    if not region:
        return

    left, top, width, height = region
    center_x = int(left + width / 2)
    center_y = int(top + height / 2)

    # Move to center of window first
    pyautogui.moveTo(center_x, center_y)
    time.sleep(0.1)

    # Scroll (negative = down, positive = up)
    scroll_amount = -amount if direction == 'down' else amount
    pyautogui.scroll(scroll_amount)


def enter_post():
    """
    Click on a post to enter it.

    Returns:
        bool: True if click was performed, False otherwise
    """
    click_pos = get_post_click_position()
    if not click_pos:
        return False

    log_message(f"Clicking to enter post at {click_pos}")
    pyautogui.click(click_pos)
    time.sleep(1.5)  # Wait for post to load
    return True


def like_post():
    """
    Find and click the like button inside a post.
    Scrolls down if button is not visible.

    Returns:
        bool: True if liked successfully, False otherwise
    """
    log_message("Looking for like button...")

    like_button = find_button(
        X_LIKE_BUTTON_IMAGES,
        confidence=0.8,
        max_scroll_attempts=MAX_SCROLL_ATTEMPTS,
        scroll_direction='down'
    )

    if like_button:
        log_message(f"Clicking like button at {like_button}")
        pyautogui.click(like_button)
        time.sleep(0.5)
        return True
    else:
        log_message("Like button not found", level="WARNING")
        return False


def go_back():
    """
    Find and click the back button to return to feed.
    Scrolls up if button is not visible.
    Verifies that we actually exited the post by checking if back button disappears.

    Returns:
        bool: True if returned successfully, False otherwise
    """
    log_message("Looking for back button...")

    max_attempts = 3
    for attempt in range(max_attempts):
        back_button = find_button(
            X_BACK_BUTTON_IMAGES,
            confidence=0.8,  # Higher confidence to avoid false matches
            max_scroll_attempts=MAX_SCROLL_ATTEMPTS,
            scroll_direction='up'
        )

        if back_button:
            log_message(f"Clicking back button at {back_button}")
            pyautogui.click(back_button)
            time.sleep(1.0)  # Wait for transition

            # Verify we exited - back button should no longer be visible
            region = get_iphone_mirroring_region()
            still_visible = None
            for img_name in X_BACK_BUTTON_IMAGES:
                img_path = Path('..') / img_name
                if img_path.exists():
                    try:
                        still_visible = pyautogui.locateOnScreen(
                            str(img_path),
                            confidence=0.8,
                            grayscale=True,
                            region=region
                        )
                    except:
                        pass

            if still_visible:
                log_message(f"Back button still visible, click may have missed (attempt {attempt + 1}/{max_attempts})", level="WARNING")
                continue  # Try again
            else:
                log_message("Successfully exited post", level="SUCCESS")
                return True
        else:
            log_message("Back button not found", level="WARNING")
            return False

    log_message("Failed to exit post after multiple attempts", level="ERROR")
    return False


def scroll_feed():
    """
    Scroll down the feed significantly to reveal new posts.
    Multiple scrolls to ensure we move past the current post.
    """
    log_message("Scrolling feed to new posts...")

    # Scroll multiple times to ensure we move to a completely new post
    for i in range(3):
        scroll_in_window(direction='down', amount=600)
        time.sleep(0.3)

    time.sleep(1.0)  # Wait for content to load
    log_message("Feed scrolled to new content")


def run_x_cycle(run_number, total_runs):
    """
    Execute one complete enter-like-back cycle on X.

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

        # 1. Enter a post
        if not enter_post():
            log_message("Failed to enter post", level="ERROR")
            return False

        # 2. Like the post
        liked = like_post()

        # 3. Go back to feed
        if not go_back():
            log_message("Failed to go back, trying alternative method", level="WARNING")
            # Try scrolling up more aggressively
            for _ in range(3):
                scroll_in_window(direction='up', amount=500)
                time.sleep(0.3)
            if not go_back():
                log_message("Still can't find back button", level="ERROR")
                return False

        # 4. Scroll feed to see new posts
        scroll_feed()

        # 5. Take screenshot if enabled
        if liked and config.AUTOMATION['enable_screenshots']:
            take_screenshot(f"x_like_{run_number}")

        log_message(f"Run {run_number} completed", level="SUCCESS")
        return liked

    except Exception as e:
        log_message(f"Run {run_number} failed: {e}", level="ERROR")
        return False


def main():
    """
    Main function for X Like automation
    """
    # Setup
    setup_directories()

    # Enable PyAutoGUI failsafe
    pyautogui.FAILSAFE = config.AUTOMATION['enable_failsafe']

    log_message("=" * 50)
    log_message("X (Twitter) Like Automation", level="INFO")
    log_message("=" * 50)
    log_message(f"Number of runs: {config.AUTOMATION['number_of_runs']}")
    log_message(f"Screenshots enabled: {config.AUTOMATION['enable_screenshots']}")
    log_message(f"Failsafe enabled: {config.AUTOMATION['enable_failsafe']}")
    log_message(f"Like button images: {X_LIKE_BUTTON_IMAGES}")
    log_message(f"Back button images: {X_BACK_BUTTON_IMAGES}")

    log_message("\nNew flow: Enter post -> Like -> Back -> Scroll -> Repeat")

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
            success = run_x_cycle(run_num, config.AUTOMATION['number_of_runs'])

            if success:
                successful_cycles += 1
            else:
                failed_cycles += 1

            # Wait between runs
            if run_num < config.AUTOMATION['number_of_runs']:
                time.sleep(config.TIMING['wait_between_runs'])

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
