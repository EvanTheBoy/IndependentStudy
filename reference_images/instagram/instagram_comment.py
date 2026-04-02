#!/usr/bin/env python3
"""
Instagram Comment Automation
Scrolls through Instagram feed and leaves comments on posts using pixel matching
"""

import pyautogui
import time
import random
from datetime import datetime
from pathlib import Path
from core import config
from core.utils import log_message, take_screenshot, setup_directories, get_iphone_mirroring_center, get_iphone_mirroring_region


# Instagram-specific reference images (in instagram subdirectory)
# Includes both dark and light theme variants for each element
INSTAGRAM_IMAGES = {
    'comment_button': [
        'instagram/instagram_comment_button_dark.png',
        'instagram/instagram_comment_button.png',
    ],
    'input_field': [
        # Dark theme variants
        'instagram/instagram_comment_input_field_dark_1.png',
        'instagram/instagram_comment_input_field_dark_2.png',
        'instagram/instagram_comment_input_field_dark_3.png',
        # Light theme variants
        'instagram/instagram_comment_input_field_1.png',
        'instagram/instagram_comment_input_field_2.png',
        'instagram/instagram_comment_input_field_3.png',
    ],
    'submit_button': [
        'instagram/instagram_comment_submit_dark.png',
        'instagram/instagram_comment_submit.png',
    ],
    'drag_down': [
        'instagram/instagram_drag_down_dark.png',
        'instagram/instagram_drag_down.png',
    ],
}

# Instagram-specific comments
INSTAGRAM_COMMENTS = [
    'Great post!',
    'Love this!',
    'Amazing!',
    'So cool!',
    'Nice one!',
]


def find_button_on_screen(image_names, confidence=0.7, grayscale=False, use_region=True):
    """
    Find a button on screen by trying multiple reference images

    Args:
        image_names: List of image filenames to try
        confidence: Matching confidence threshold
        grayscale: Use grayscale matching
        use_region: If True, limit search to iPhone Mirroring window

    Returns:
        tuple: (x, y) coordinates if found, None otherwise
    """
    # Get search region if requested
    region = None
    if use_region:
        region = get_iphone_mirroring_region()
        if region:
            log_message(f"Searching within iPhone Mirroring window: {region}")

    for img_name in image_names:
        img_path = Path('..') / img_name

        if not img_path.exists():
            log_message(f"Reference image not found: {img_path}", level="WARNING")
            continue

        log_message(f"Trying: {img_name}")

        try:
            location = pyautogui.locateOnScreen(
                str(img_path),
                confidence=confidence,
                grayscale=grayscale,
                region=region
            )

            if location:
                center = pyautogui.center(location)
                log_message(f"  Found at {center}", level="SUCCESS")
                return center

        except pyautogui.ImageNotFoundException:
            log_message(f"  Not found", level="WARNING")
        except Exception as e:
            log_message(f"  Error: {e}", level="WARNING")

    return None


def get_instagram_comment():
    """
    Get a random comment for Instagram

    Returns:
        str: Comment text
    """
    if config.COMMENTS.get('comment_texts'):
        return random.choice(config.COMMENTS['comment_texts'])
    return random.choice(INSTAGRAM_COMMENTS)


def scroll_instagram_feed():
    """
    Scroll down the Instagram feed to reveal new posts
    Uses iPhone Mirroring window center as scroll position
    """
    log_message("Scrolling Instagram feed...")

    feed_center = get_iphone_mirroring_center()
    if feed_center:
        pyautogui.moveTo(feed_center[0], feed_center[1])
        log_message(f"Moved to feed center: {feed_center}")
    else:
        log_message("Could not find window center", level="WARNING")

    scroll_amount = config.AUTOMATION.get('main_feed_scroll_amount', -600)
    scroll_attempts = config.AUTOMATION.get('main_feed_scroll_attempts', 3)

    for _ in range(scroll_attempts):
        random_scroll = int(scroll_amount * random.uniform(0.8, 1.2))
        pyautogui.scroll(random_scroll)
        time.sleep(random.uniform(0.1, 0.2))

    time.sleep(config.TIMING['wait_after_scroll'])


def click_comment_button(max_scroll_attempts=5):
    """
    Find and click the comment button on Instagram feed
    If not found, scroll down slightly and retry until found

    Args:
        max_scroll_attempts: Maximum number of small scroll attempts

    Returns:
        bool: True if successful
    """
    log_message("Looking for comment button on Instagram...")

    location = find_button_on_screen(
        INSTAGRAM_IMAGES['comment_button'],
        confidence=config.PIXEL_MATCHING['confidence'],
        grayscale=config.PIXEL_MATCHING['grayscale'],
        use_region=True
    )

    # If not found, try small scrolls to reveal the comment button
    scroll_attempt = 0
    while not location and scroll_attempt < max_scroll_attempts:
        scroll_attempt += 1
        log_message(f"Comment button not visible, scrolling down slightly (attempt {scroll_attempt}/{max_scroll_attempts})...")

        # Get window center for scrolling
        feed_center = get_iphone_mirroring_center()
        if feed_center:
            pyautogui.moveTo(feed_center[0], feed_center[1])

        # Small scroll down (-150 to -250 pixels)
        small_scroll = random.randint(-250, -150)
        pyautogui.scroll(small_scroll)
        time.sleep(0.5)

        # Try to find the button again
        location = find_button_on_screen(
            INSTAGRAM_IMAGES['comment_button'],
            confidence=config.PIXEL_MATCHING['confidence'],
            grayscale=config.PIXEL_MATCHING['grayscale'],
            use_region=True
        )

    if not location:
        log_message(f"Comment button not found after {max_scroll_attempts} scroll attempts", level="WARNING")
        return False

    log_message(f"Clicking comment button at {location}")
    pyautogui.click(location)
    time.sleep(config.TIMING.get('wait_after_comment_click', 1.5))

    return True


def click_input_field():
    """
    Find and click the comment input field
    Tries multiple placeholder images since Instagram shows different placeholders

    Returns:
        bool: True if successful
    """
    log_message("Looking for comment input field (trying multiple placeholders)...")

    # Try each placeholder image
    for img_name in INSTAGRAM_IMAGES['input_field']:
        img_path = Path('..') / img_name

        if not img_path.exists():
            log_message(f"  Image not found: {img_path}", level="WARNING")
            continue

        log_message(f"Trying placeholder: {img_name}")

        try:
            location = pyautogui.locateOnScreen(
                str(img_path),
                confidence=0.7,
                grayscale=False
            )

            if location:
                center = pyautogui.center(location)
                log_message(f"  Found input field at {center}", level="SUCCESS")
                pyautogui.click(center)
                time.sleep(0.5)
                return True

        except pyautogui.ImageNotFoundException:
            log_message(f"  Not matched", level="WARNING")
        except Exception as e:
            log_message(f"  Error: {e}", level="WARNING")

    log_message("Input field not found with any placeholder", level="WARNING")
    return False


def type_and_submit_comment():
    """
    Type comment and click submit button

    Returns:
        bool: True if successful
    """
    # Type comment
    comment = get_instagram_comment()
    log_message(f"Typing comment: '{comment}'")
    pyautogui.write(comment, interval=0.03)

    # Wait for button to become active after typing
    log_message("Waiting for submit button to become active...")
    time.sleep(1.0)

    # Find and click submit button
    log_message("Looking for submit button...")

    location = find_button_on_screen(
        INSTAGRAM_IMAGES['submit_button'],
        confidence=0.7,
        grayscale=False,
        use_region=True
    )

    if location:
        pyautogui.click(location)
        time.sleep(config.TIMING.get('wait_after_comment_submit', 1.5))
        log_message("Comment submitted", level="SUCCESS")
        return True

    log_message("Submit button not found, trying Enter key", level="WARNING")
    pyautogui.press('enter')
    time.sleep(config.TIMING.get('wait_after_comment_submit', 1.5))
    return True


def close_comment_section():
    """
    Close the comment section by:
    1. Finding the drag_down bar and dragging it down to collapse the comment section
    2. Clicking outside the comment area to dismiss it

    Returns:
        bool: True if successful
    """
    log_message("Closing comment section...")

    feed_center = get_iphone_mirroring_center()
    region = get_iphone_mirroring_region()

    # Step 1: Find the drag_down bar using pixel matching in the top portion of the window
    log_message("Looking for drag down bar...")

    drag_location = None
    if region:
        # Search only in top 200px of the window where the drag bar should be
        search_region = (region[0], region[1], region[2], 200)

        for img_name in INSTAGRAM_IMAGES['drag_down']:
            img_path = Path('..') / img_name
            if not img_path.exists():
                continue

            # Try different confidence levels, starting high
            for conf in [0.8, 0.7, 0.6, 0.5]:
                try:
                    location = pyautogui.locateOnScreen(
                        str(img_path),
                        confidence=conf,
                        region=search_region
                    )
                    if location:
                        drag_location = pyautogui.center(location)
                        log_message(f"Found drag bar at {drag_location} (confidence={conf})")
                        break
                except Exception as e:
                    continue

            if drag_location:
                break

    if drag_location:
        log_message(f"Dragging down from {drag_location}...")
        drag_distance = 400
        if region:
            drag_distance = int(region[3] * 0.5)  # 50% of window height

        # Use slow drag - this works with iPhone Mirroring
        pyautogui.moveTo(drag_location.x, drag_location.y)
        time.sleep(0.3)
        pyautogui.drag(0, drag_distance, duration=1.5, button='left')
        time.sleep(0.8)
    else:
        log_message("Drag bar not found, trying swipe from top of screen", level="WARNING")
        # Fallback: swipe down from near the top of the comment section
        if region and feed_center:
            start_y = region[1] + 100  # About 100px from top of window
            drag_distance = int(region[3] * 0.5)  # 50% of window height

            pyautogui.moveTo(feed_center[0], start_y)
            time.sleep(0.3)
            pyautogui.drag(0, drag_distance, duration=1.5, button='left')
            time.sleep(0.8)

    # Step 2: Click outside the comment area to fully dismiss it
    log_message("Clicking outside comment area to dismiss...")
    if feed_center and region:
        # After dragging down, the post should be visible at the top
        # Click on the post area (upper portion of window)
        click_y = region[1] + 150  # 150 pixels from top of window
        pyautogui.click(feed_center[0], click_y)
        time.sleep(config.TIMING.get('wait_after_dialog_close', 1.0))

    log_message("Comment section closed", level="SUCCESS")
    return True


def comment_on_instagram_post():
    """
    Complete workflow to comment on an Instagram post:
    1. Click comment button
    2. Click input field (try multiple placeholders)
    3. Type comment and submit
    4. Close comment section (drag down + click outside)

    Returns:
        bool: True if successful
    """
    # 1. Click comment button
    if not click_comment_button():
        return False

    # 2. Click input field
    if not click_input_field():
        log_message("Could not find input field, aborting", level="ERROR")
        close_comment_section()
        return False

    # 3. Type and submit comment
    type_and_submit_comment()

    # 4. Close comment section
    close_comment_section()

    log_message("Comment posted successfully", level="SUCCESS")
    return True


def run_instagram_comment_cycle(run_number, total_runs):
    """
    Execute one complete comment cycle on Instagram:
    1. Scroll to reveal new post and find comment button
    2. Comment on post
    3. Continue scrolling

    Args:
        run_number: Current run number
        total_runs: Total number of runs

    Returns:
        bool: True if successful
    """
    try:
        log_message("=" * 50)
        log_message(f"Run {run_number}/{total_runs}", level="INFO")
        log_message("=" * 50)

        # 1. Scroll to reveal post with comment button
        scroll_instagram_feed()

        # 2. Comment on the post
        success = comment_on_instagram_post()

        # 3. Take screenshot if enabled
        if success and config.AUTOMATION['enable_screenshots']:
            take_screenshot(f"instagram_comment_{run_number}")

        # 4. Wait before next cycle
        time.sleep(config.TIMING['wait_between_runs'])

        log_message(f"Run {run_number} completed", level="SUCCESS")
        return success

    except Exception as e:
        log_message(f"Run {run_number} failed: {e}", level="ERROR")
        return False


def main():
    """
    Main function for Instagram Comment automation
    """
    setup_directories()
    pyautogui.FAILSAFE = config.AUTOMATION['enable_failsafe']

    log_message("=" * 50)
    log_message("Instagram Comment Automation", level="INFO")
    log_message("=" * 50)
    log_message(f"Number of runs: {config.AUTOMATION['number_of_runs']}")
    log_message(f"Screenshots enabled: {config.AUTOMATION['enable_screenshots']}")
    log_message(f"Failsafe enabled: {config.AUTOMATION['enable_failsafe']}")
    log_message(f"Input field placeholders: {len(INSTAGRAM_IMAGES['input_field'])} variants")

    if config.AUTOMATION['enable_failsafe']:
        log_message("Move mouse to corner to stop automation", level="WARNING")

    log_message("\nStarting in 3 seconds...")
    for i in range(3, 0, -1):
        log_message(f"{i}...")
        time.sleep(1)

    log_message("Starting automation!\n")

    successful_cycles = 0
    failed_cycles = 0
    timing_records = []

    try:
        for run_num in range(1, config.AUTOMATION['number_of_runs'] + 1):
            iter_start = datetime.now()
            log_message(f"[TIMER] Run {run_num} started at {iter_start.strftime('%Y-%m-%d %H:%M:%S.%f')}")

            success = run_instagram_comment_cycle(run_num, config.AUTOMATION['number_of_runs'])
            if success:
                successful_cycles += 1
            else:
                failed_cycles += 1

            iter_end = datetime.now()
            duration = (iter_end - iter_start).total_seconds()
            log_message(f"[TIMER] Run {run_num} ended at  {iter_end.strftime('%Y-%m-%d %H:%M:%S.%f')} (took {duration:.2f}s)")
            timing_records.append({'run': run_num, 'start': iter_start, 'end': iter_end, 'duration': duration})

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

        if timing_records:
            log_message("\n" + "-" * 50)
            log_message("TIMING RECORDS")
            log_message("-" * 50)
            for idx, rec in enumerate(timing_records, 1):
                log_message(
                    f"  [{idx}] Run {rec['run']}"
                    f"\n        start    : {rec['start'].strftime('%Y-%m-%d %H:%M:%S.%f')}"
                    f"\n        end      : {rec['end'].strftime('%Y-%m-%d %H:%M:%S.%f')}"
                    f"\n        duration : {rec['duration']:.2f}s"
                )

        log_message("=" * 50)
        log_message("Automation complete!", level="SUCCESS")


if __name__ == "__main__":
    main()
