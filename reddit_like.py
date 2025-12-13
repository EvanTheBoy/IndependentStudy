#!/usr/bin/env python3
"""
Reddit Upvote Automation
Scrolls through Reddit and upvotes posts using pixel matching
"""

import pyautogui
import time
import random
from pathlib import Path
import config
from utils import log_message, take_screenshot, setup_directories, get_iphone_mirroring_center


# Reddit-specific reference images
REDDIT_UPVOTE_BUTTON_IMAGES = ['reddit_upvote_button.png', 'reddit_upvote_button_dark.png']


def find_reddit_upvote_buttons(confidence=0.7, grayscale=True):
    """
    Find all Reddit upvote buttons on screen using pixel matching

    Args:
        confidence: Matching confidence threshold (0.0 to 1.0)
        grayscale: Use grayscale matching for speed

    Returns:
        list: List of (x, y) coordinates for all found upvote buttons
    """
    upvote_buttons = []

    for img_name in REDDIT_UPVOTE_BUTTON_IMAGES:
        img_path = Path('reference_images') / img_name

        if not img_path.exists():
            log_message(f"Reference image not found: {img_path}", level="WARNING")
            continue

        log_message(f"Searching for Reddit upvote buttons using: {img_name}")
        log_message(f"  Confidence: {confidence}, Grayscale: {grayscale}")

        try:
            matches = list(pyautogui.locateAllOnScreen(
                str(img_path),
                confidence=confidence,
                grayscale=grayscale
            ))

            if matches:
                log_message(f"  Found {len(matches)} match(es) with {img_name}", level="SUCCESS")
                for match in matches:
                    center = pyautogui.center(match)
                    upvote_buttons.append(center)
                    log_message(f"    Button at: {center}")
            else:
                log_message(f"  No matches found with {img_name}", level="WARNING")

        except pyautogui.ImageNotFoundException:
            log_message(f"  Image not found on screen: {img_name}", level="WARNING")
        except Exception as e:
            log_message(f"  Error searching for {img_name}: {e}", level="WARNING")

    # Remove duplicates (buttons within 20 pixels)
    unique_buttons = []
    for btn in upvote_buttons:
        is_duplicate = False
        for existing in unique_buttons:
            if abs(btn[0] - existing[0]) < 20 and abs(btn[1] - existing[1]) < 20:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_buttons.append(btn)

    if len(unique_buttons) != len(upvote_buttons):
        log_message(f"Removed {len(upvote_buttons) - len(unique_buttons)} duplicate(s)")

    return unique_buttons


def upvote_post_on_reddit():
    """
    Find all upvote buttons on Reddit and click a random one

    Returns:
        bool: True if successful, False otherwise
    """
    log_message("Looking for posts to upvote on Reddit...")

    upvote_buttons = find_reddit_upvote_buttons(
        confidence=config.PIXEL_MATCHING['confidence'],
        grayscale=config.PIXEL_MATCHING['grayscale']
    )

    if not upvote_buttons:
        log_message("No upvote buttons found on Reddit", level="WARNING")
        return False

    selected_button = random.choice(upvote_buttons)
    log_message(f"Randomly selected button at {selected_button} (from {len(upvote_buttons)} found)")

    log_message(f"Clicking upvote button at {selected_button}")
    pyautogui.click(selected_button)
    time.sleep(config.TIMING['wait_after_like'])

    log_message("Post upvoted successfully", level="SUCCESS")
    return True


def scroll_reddit_feed():
    """
    Scroll down the Reddit feed to reveal new posts
    """
    log_message("Scrolling Reddit feed...")

    # Dynamically get iPhone Mirroring window center
    feed_center = get_iphone_mirroring_center()
    if feed_center:
        pyautogui.moveTo(feed_center[0], feed_center[1])
        log_message(f"Moved to feed center: {feed_center}")
    else:
        log_message("Could not find window center, scrolling at current position", level="WARNING")

    scroll_amount = config.AUTOMATION.get('main_feed_scroll_amount', -600)
    scroll_attempts = config.AUTOMATION.get('main_feed_scroll_attempts', 3)

    for _ in range(scroll_attempts):
        random_scroll = int(scroll_amount * random.uniform(0.8, 1.2))
        pyautogui.scroll(random_scroll)
        time.sleep(random.uniform(0.1, 0.2))

    time.sleep(config.TIMING['wait_after_scroll'])


def run_reddit_cycle(run_number, total_runs):
    """
    Execute one complete cycle on Reddit:
    1. Try to upvote a post first
    2. Then scroll to reveal new posts for next cycle

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

        # 1. Find and upvote a post first
        success = upvote_post_on_reddit()

        # 2. Take screenshot if enabled
        if success and config.AUTOMATION['enable_screenshots']:
            take_screenshot(f"reddit_upvote_{run_number}")

        # 3. Scroll to reveal new posts for next cycle
        scroll_reddit_feed()

        # 4. Wait before next cycle
        time.sleep(config.TIMING['wait_between_runs'])

        log_message(f"Run {run_number} completed", level="SUCCESS")
        return success

    except Exception as e:
        log_message(f"Run {run_number} failed: {e}", level="ERROR")
        return False


def main():
    """
    Main function for Reddit Upvote automation
    """
    setup_directories()
    pyautogui.FAILSAFE = config.AUTOMATION['enable_failsafe']

    log_message("=" * 50)
    log_message("Reddit Upvote Automation", level="INFO")
    log_message("=" * 50)
    log_message(f"Number of runs: {config.AUTOMATION['number_of_runs']}")
    log_message(f"Screenshots enabled: {config.AUTOMATION['enable_screenshots']}")
    log_message(f"Failsafe enabled: {config.AUTOMATION['enable_failsafe']}")
    log_message(f"Reference images: {REDDIT_UPVOTE_BUTTON_IMAGES}")

    if config.AUTOMATION['enable_failsafe']:
        log_message("Move mouse to corner to stop automation", level="WARNING")

    log_message("\nStarting in 3 seconds...")
    for i in range(3, 0, -1):
        log_message(f"{i}...")
        time.sleep(1)

    log_message("Starting automation!\n")

    successful_cycles = 0
    failed_cycles = 0

    try:
        for run_num in range(1, config.AUTOMATION['number_of_runs'] + 1):
            success = run_reddit_cycle(run_num, config.AUTOMATION['number_of_runs'])
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
