#!/usr/bin/env python3
"""
YouTube Comment Automation
Scrolls through YouTube and leaves comments on videos using pixel matching
"""

import pyautogui
import time
import random
from pathlib import Path
import config
from utils import log_message, take_screenshot, setup_directories, get_iphone_mirroring_center, get_iphone_mirroring_region


# YouTube-specific reference images
YOUTUBE_IMAGES = {
    'comment_button': [
        'youtube/youtube_comment_button_dark.png',
    ],
    'input_field': [
        'youtube/youtube_comment_input_field_dark_1.png',
        'youtube/youtube_comment_input_field_dark_2.png',
        'youtube/youtube_comment_input_field_dark_3.png',
        'youtube/youtube_comment_input_field_dark_4.png',
    ],
    'submit_button': [
        'youtube/youtube_comment_submit_dark.png',
    ],
    'back_button': [
        'youtube/youtube_comment_back.png',
    ],
}

# YouTube-specific comments
YOUTUBE_COMMENTS = [
    'Great video!',
    'Thanks for sharing!',
    'Very helpful content',
    'Love this!',
    'Well explained',
]


def find_button_on_screen(image_names, confidence=0.7, grayscale=False, use_region=False):
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
        img_path = Path('reference_images') / img_name

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


def find_all_buttons_on_screen(image_names, confidence=0.7, grayscale=False):
    """
    Find all matching buttons on screen

    Args:
        image_names: List of image filenames to try
        confidence: Matching confidence threshold
        grayscale: Use grayscale matching

    Returns:
        list: List of (x, y) coordinates
    """
    all_buttons = []

    for img_name in image_names:
        img_path = Path('reference_images') / img_name

        if not img_path.exists():
            continue

        log_message(f"Searching: {img_name}")

        try:
            matches = list(pyautogui.locateAllOnScreen(
                str(img_path),
                confidence=confidence,
                grayscale=grayscale
            ))

            if matches:
                log_message(f"  Found {len(matches)} match(es)", level="SUCCESS")
                for match in matches:
                    center = pyautogui.center(match)
                    all_buttons.append(center)

        except pyautogui.ImageNotFoundException:
            pass
        except Exception as e:
            log_message(f"  Error: {e}", level="WARNING")

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

    return unique_buttons


def get_youtube_comment():
    """
    Get a random comment for YouTube

    Returns:
        str: Comment text
    """
    if config.COMMENTS.get('comment_texts'):
        return random.choice(config.COMMENTS['comment_texts'])
    return random.choice(YOUTUBE_COMMENTS)


def click_comment_button():
    """
    Find and click a comment button on YouTube

    Returns:
        bool: True if successful
    """
    log_message("Looking for comment buttons on YouTube...")

    # Find all comment buttons and pick a random one
    buttons = find_all_buttons_on_screen(
        YOUTUBE_IMAGES['comment_button'],
        confidence=config.PIXEL_MATCHING['confidence'],
        grayscale=config.PIXEL_MATCHING['grayscale']
    )

    if not buttons:
        # Try single match
        location = find_button_on_screen(
            YOUTUBE_IMAGES['comment_button'],
            confidence=config.PIXEL_MATCHING['confidence'],
            grayscale=config.PIXEL_MATCHING['grayscale']
        )
        if location:
            buttons = [location]

    if not buttons:
        log_message("No comment buttons found", level="WARNING")
        return False

    selected = random.choice(buttons)
    log_message(f"Clicking comment button at {selected}")

    pyautogui.click(selected)
    time.sleep(config.TIMING.get('wait_after_comment_click', 1.5))

    return True


def click_input_field():
    """
    Find and click the comment input field
    Tries multiple placeholder images since YouTube shows different placeholders

    Returns:
        bool: True if successful
    """
    log_message("Looking for comment input field (trying multiple placeholders)...")

    # Try each placeholder image
    for img_name in YOUTUBE_IMAGES['input_field']:
        img_path = Path('reference_images') / img_name

        if not img_path.exists():
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
    comment = get_youtube_comment()
    log_message(f"Typing comment: '{comment}'")
    pyautogui.write(comment, interval=0.03)

    # Wait for button to become active after typing
    log_message("Waiting for submit button to become active...")
    time.sleep(1.5)

    # Find and click submit button (search only within iPhone Mirroring window)
    # Submit button is always on the right side, so pick the rightmost match
    log_message("Looking for submit button...")

    region = get_iphone_mirroring_region()
    all_matches = []

    for img_name in YOUTUBE_IMAGES['submit_button']:
        img_path = Path('reference_images') / img_name
        if not img_path.exists():
            continue
        try:
            matches = list(pyautogui.locateAllOnScreen(
                str(img_path),
                confidence=0.6,
                region=region
            ))
            for match in matches:
                center = pyautogui.center(match)
                all_matches.append(center)
        except:
            pass

    if all_matches:
        # Pick the rightmost match (submit button is on the right)
        location = max(all_matches, key=lambda p: p.x)
        log_message(f"Found {len(all_matches)} matches, picking rightmost at {location}")

        # Move to button first, then click
        pyautogui.moveTo(location)
        time.sleep(0.2)
        pyautogui.click()
        time.sleep(0.5)
        # Click again to make sure
        pyautogui.click()
        time.sleep(config.TIMING.get('wait_after_comment_submit', 1.5))
        log_message("Comment submitted", level="SUCCESS")
        return True

    log_message("Submit button not found, trying Enter key", level="WARNING")
    pyautogui.press('enter')
    time.sleep(config.TIMING.get('wait_after_comment_submit', 1.5))
    return True


def close_comment_section():
    """
    Click the X button to close comment section

    Returns:
        bool: True if successful
    """
    log_message("Closing comment section...")

    location = find_button_on_screen(
        YOUTUBE_IMAGES['back_button'],
        confidence=0.7,
        grayscale=False
    )

    if location:
        pyautogui.click(location)
        time.sleep(config.TIMING.get('wait_after_dialog_close', 1.0))
        log_message("Returned to video", level="SUCCESS")
        return True

    log_message("Back button not found, trying swipe gesture", level="WARNING")
    # Fallback: swipe down to close
    feed_center = get_iphone_mirroring_center()
    if feed_center:
        pyautogui.moveTo(feed_center[0], feed_center[1] - 100)
        time.sleep(0.1)
        pyautogui.drag(0, 200, duration=0.3)
        time.sleep(config.TIMING.get('wait_after_dialog_close', 1.0))

    return True


def scroll_youtube_feed():
    """
    Scroll down the YouTube feed to reveal new videos
    """
    log_message("Scrolling YouTube feed...")

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


def click_video_and_wait():
    """
    Click on a video thumbnail and wait for it to load
    """
    log_message("Clicking on video thumbnail...")

    feed_center = get_iphone_mirroring_center()
    if feed_center:
        pyautogui.click(feed_center[0], feed_center[1])
        log_message(f"Clicked at {feed_center}")
    else:
        log_message("Could not find window center", level="WARNING")
        pyautogui.click()

    # Wait for YouTube to load the video
    log_message("Waiting for video to load...")
    time.sleep(3)  # YouTube needs time to load video


def comment_on_youtube_video():
    """
    Complete workflow to comment on a YouTube video:
    1. Click comment button
    2. Click input field (try multiple placeholders)
    3. Type comment and submit
    4. Close comment section

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


def run_youtube_comment_cycle(run_number, total_runs):
    """
    Execute one complete comment cycle on YouTube:
    1. Comment on current video
    2. Scroll to reveal new video
    3. Click on video and wait for it to load

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

        # 1. Comment on current video
        success = comment_on_youtube_video()

        # 2. Take screenshot if enabled
        if success and config.AUTOMATION['enable_screenshots']:
            take_screenshot(f"youtube_comment_{run_number}")

        # 3. Scroll to reveal new video
        scroll_youtube_feed()

        # 4. Click on new video and wait for it to load
        click_video_and_wait()

        # 5. Wait before next cycle
        time.sleep(config.TIMING['wait_between_runs'])

        log_message(f"Run {run_number} completed", level="SUCCESS")
        return success

    except Exception as e:
        log_message(f"Run {run_number} failed: {e}", level="ERROR")
        return False


def main():
    """
    Main function for YouTube Comment automation
    """
    setup_directories()
    pyautogui.FAILSAFE = config.AUTOMATION['enable_failsafe']

    log_message("=" * 50)
    log_message("YouTube Comment Automation", level="INFO")
    log_message("=" * 50)
    log_message(f"Number of runs: {config.AUTOMATION['number_of_runs']}")
    log_message(f"Screenshots enabled: {config.AUTOMATION['enable_screenshots']}")
    log_message(f"Failsafe enabled: {config.AUTOMATION['enable_failsafe']}")
    log_message(f"Input field placeholders: {len(YOUTUBE_IMAGES['input_field'])} variants")

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
            success = run_youtube_comment_cycle(run_num, config.AUTOMATION['number_of_runs'])
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
