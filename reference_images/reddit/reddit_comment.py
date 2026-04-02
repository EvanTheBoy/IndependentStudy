#!/usr/bin/env python3
"""
Reddit Comment Automation
Scrolls through Reddit feed and leaves comments on posts using pixel matching
"""

import pyautogui
import time
import random
from datetime import datetime
from pathlib import Path
from core import config
from core.utils import log_message, take_screenshot, setup_directories, get_iphone_mirroring_center, get_iphone_mirroring_region


# Reddit-specific reference images (in reddit subdirectory)
REDDIT_IMAGES = {
    'comment_button': ['reddit/reddit_comment_button.png'],
    'input_field': ['reddit/reddit_comment_input_field.png'],
    'reply_button': ['reddit/reddit_comment_reply.png'],
    'back_button': ['reddit/reddit_comment_back.png'],  # Note: typo in filename
}

# Reddit-specific comments
REDDIT_COMMENTS = [
    'Great post!',
    'Thanks for sharing!',
    'Interesting perspective',
    'Well said!',
    'This is helpful',
]


def find_buttons_on_screen(image_names, confidence=0.7, grayscale=False, find_all=False, use_region=True):
    """
    Find button(s) on screen using pixel matching

    Args:
        image_names: List of image filenames to try
        confidence: Matching confidence threshold
        grayscale: Use grayscale matching
        find_all: If True, find all matches; if False, find first match
        use_region: If True, limit search to iPhone Mirroring window

    Returns:
        list of (x, y) if find_all=True, or single (x, y) tuple, or None if not found
    """
    all_buttons = []

    # Get search region to limit to iPhone Mirroring window
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

        log_message(f"Searching for: {img_name}")

        try:
            if find_all:
                matches = list(pyautogui.locateAllOnScreen(
                    str(img_path),
                    confidence=confidence,
                    grayscale=grayscale,
                    region=region
                ))
                if matches:
                    log_message(f"  Found {len(matches)} match(es)", level="SUCCESS")
                    for match in matches:
                        center = pyautogui.center(match)
                        all_buttons.append(center)
            else:
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
            log_message(f"  Not found: {img_name}", level="WARNING")
        except Exception as e:
            log_message(f"  Error: {e}", level="WARNING")

    if find_all:
        # Remove duplicates
        unique_buttons = []
        for btn in all_buttons:
            is_dup = False
            for existing in unique_buttons:
                if abs(btn[0] - existing[0]) < 20 and abs(btn[1] - existing[1]) < 20:
                    is_dup = True
                    break
            if not is_dup:
                unique_buttons.append(btn)
        return unique_buttons if unique_buttons else None

    return None


def get_reddit_comment():
    """
    Get a random comment for Reddit

    Returns:
        str: Comment text
    """
    # Try config comments first, fall back to Reddit-specific ones
    if config.COMMENTS.get('comment_texts'):
        return random.choice(config.COMMENTS['comment_texts'])
    return random.choice(REDDIT_COMMENTS)


def click_comment_button():
    """
    Find and click a comment button on Reddit feed

    Returns:
        bool: True if successful
    """
    log_message("Looking for comment buttons on Reddit...")

    # Find all comment buttons
    buttons = find_buttons_on_screen(
        REDDIT_IMAGES['comment_button'],
        confidence=config.PIXEL_MATCHING['confidence'],
        grayscale=config.PIXEL_MATCHING['grayscale'],
        find_all=True
    )

    if not buttons:
        log_message("No comment buttons found", level="WARNING")
        return False

    # Pick a random one
    selected = random.choice(buttons)
    log_message(f"Selected comment button at {selected} (from {len(buttons)} found)")

    pyautogui.click(selected)
    time.sleep(config.TIMING.get('wait_after_comment_click', 1.0))

    return True


def click_input_field():
    """
    Find and click the comment input field

    Returns:
        bool: True if successful
    """
    log_message("Looking for comment input field...")

    location = find_buttons_on_screen(
        REDDIT_IMAGES['input_field'],
        confidence=0.7,
        grayscale=False
    )

    if location:
        pyautogui.click(location)
        time.sleep(0.5)
        return True

    log_message("Input field not found, trying tap", level="WARNING")
    # Fallback: tap in center of screen where input usually is
    feed_center = get_iphone_mirroring_center()
    if feed_center:
        pyautogui.click(feed_center[0], feed_center[1] + 200)
        time.sleep(0.5)
    return False


def type_and_submit_comment():
    """
    Type comment and click reply button

    Returns:
        bool: True if successful
    """
    # Type comment
    comment = get_reddit_comment()
    log_message(f"Typing comment: '{comment}'")
    pyautogui.write(comment, interval=0.03)
    time.sleep(0.5)

    # Find and click reply button
    log_message("Looking for reply button...")
    location = find_buttons_on_screen(
        REDDIT_IMAGES['reply_button'],
        confidence=0.7,
        grayscale=False
    )

    if location:
        pyautogui.click(location)
        time.sleep(config.TIMING.get('wait_after_comment_submit', 1.5))
        log_message("Comment submitted", level="SUCCESS")
        return True

    log_message("Reply button not found, trying Enter key", level="WARNING")
    pyautogui.press('enter')
    time.sleep(config.TIMING.get('wait_after_comment_submit', 1.5))
    return True


def close_comment_section():
    """
    Click the X button to close comment section and return to feed

    Returns:
        bool: True if successful
    """
    log_message("Closing comment section...")

    location = find_buttons_on_screen(
        REDDIT_IMAGES['back_button'],
        confidence=0.7,
        grayscale=False
    )

    if location:
        pyautogui.click(location)
        time.sleep(config.TIMING.get('wait_after_dialog_close', 1.0))
        log_message("Returned to feed", level="SUCCESS")
        return True

    log_message("Back button not found, trying swipe gesture", level="WARNING")
    # Fallback: swipe right from left edge
    feed_center = get_iphone_mirroring_center()
    if feed_center:
        start_x = feed_center[0] - 150
        pyautogui.moveTo(start_x, feed_center[1])
        time.sleep(0.1)
        pyautogui.drag(200, 0, duration=0.3)
        time.sleep(config.TIMING.get('wait_after_dialog_close', 1.0))

    return True


def scroll_reddit_feed():
    """
    Scroll down the Reddit feed to reveal new posts
    """
    log_message("Scrolling Reddit feed...")

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


def comment_on_reddit_post():
    """
    Complete workflow to comment on a Reddit post:
    1. Click comment button
    2. Click input field
    3. Type comment and submit
    4. Close comment section

    Returns:
        bool: True if successful
    """
    # 1. Click comment button
    if not click_comment_button():
        return False

    # 2. Click input field
    click_input_field()

    # 3. Type and submit comment
    type_and_submit_comment()

    # 4. Close comment section
    close_comment_section()

    log_message("Comment posted successfully", level="SUCCESS")
    return True


def run_reddit_comment_cycle(run_number, total_runs):
    """
    Execute one complete comment cycle on Reddit:
    1. Try to comment on a post first
    2. Then scroll to reveal new posts

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

        # 1. Comment on a post
        success = comment_on_reddit_post()

        # 2. Take screenshot if enabled
        if success and config.AUTOMATION['enable_screenshots']:
            take_screenshot(f"reddit_comment_{run_number}")

        # 3. Scroll to reveal new posts
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
    Main function for Reddit Comment automation
    """
    setup_directories()
    pyautogui.FAILSAFE = config.AUTOMATION['enable_failsafe']

    log_message("=" * 50)
    log_message("Reddit Comment Automation", level="INFO")
    log_message("=" * 50)
    log_message(f"Number of runs: {config.AUTOMATION['number_of_runs']}")
    log_message(f"Screenshots enabled: {config.AUTOMATION['enable_screenshots']}")
    log_message(f"Failsafe enabled: {config.AUTOMATION['enable_failsafe']}")

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

            success = run_reddit_comment_cycle(run_num, config.AUTOMATION['number_of_runs'])
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
