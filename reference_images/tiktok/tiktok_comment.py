#!/usr/bin/env python3
"""
TikTok Comment Automation
Scrolls through TikTok Explore tab and leaves comments on videos and photo posts
using pixel matching for UI element detection.

TikTok Explore has a dual-column layout (similar to Xiaohongshu):
- Videos have a triangle icon in the top-right corner
- Photo posts have stacked squares icon in the top-right corner

For videos: use tiktok_video_direct_comment_input_field.png
For photo posts: use tiktok_comment_input_field.png
Both use Enter key to submit comments (no submit button)
"""

import pyautogui
import time
import random
from datetime import datetime
from pathlib import Path
from core import config
from core.utils import log_message, take_screenshot, setup_directories, get_iphone_mirroring_center, get_iphone_mirroring_region


# TikTok-specific reference images (for pixel matching)
TIKTOK_IMAGES = {
    # Video comment input (direct input field on video page)
    'video_comment_input': ['tiktok/tiktok_video_direct_comment_input_field.png'],
    # Photo post comment input
    'photo_comment_input': ['tiktok/tiktok_comment_input_field.png'],
    # Back button to return to explore feed (for photo posts)
    'back_button': ['tiktok/tiktok_comment_back.png'],
    # Video comment button (to open comment section)
    'video_comment_button': ['tiktok/tiktok_video_comment_button.png'],
    # Photo post comment button
    'photo_comment_button': ['tiktok/tiktok_comment_button.png'],
    # Close button for video comment section (X button)
    'comment_section_close': ['tiktok/tiktok_comment_section_close.png'],
}

# Relative positions for TikTok VIDEO page buttons (as percentage of window)
# Used instead of pixel matching because video backgrounds are dynamic
TIKTOK_VIDEO_BUTTONS = {
    'back_button': {
        'x_ratio': 0.08,   # 8% from left (on the < button)
        'y_ratio': 0.125,  # 12.5% from top
    },
    'comment_button': {
        'x_ratio': 0.92,   # 92% from left (right side)
        'y_ratio': 0.62,   # 62% from top (on the comment icon)
    },
}

# TikTok-specific comments
TIKTOK_COMMENTS = [
    'Great content!',
    'Love this!',
    'Amazing!',
    'Nice post!',
    'So cool!',
    'This is awesome!',
    'Wow!',
    'Thanks for sharing!',
]


def get_video_button_position(button_name):
    """
    Calculate the absolute position of a button on TikTok video page
    based on relative coordinates. Used for video pages where pixel matching
    fails due to dynamic backgrounds.

    Args:
        button_name: 'back_button' or 'comment_button'

    Returns:
        (x, y) tuple or None if window not found
    """
    region = get_iphone_mirroring_region()
    if not region:
        log_message("Could not find iPhone Mirroring window", level="ERROR")
        return None

    left, top, width, height = region
    button_config = TIKTOK_VIDEO_BUTTONS.get(button_name)

    if not button_config:
        log_message(f"Unknown button: {button_name}", level="ERROR")
        return None

    x = int(left + width * button_config['x_ratio'])
    y = int(top + height * button_config['y_ratio'])

    log_message(f"Calculated {button_name} position: ({x}, {y})")
    return (x, y)


def find_element_on_screen(image_names, confidence=0.7, grayscale=False, use_region=True):
    """
    Find an element on screen using pixel matching

    Args:
        image_names: List of image filenames to try
        confidence: Matching confidence threshold
        grayscale: Use grayscale matching
        use_region: If True, limit search to iPhone Mirroring window

    Returns:
        (x, y) tuple if found, None otherwise
    """
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

    return None


def get_tiktok_comment():
    """
    Get a random comment for TikTok

    Returns:
        str: Comment text
    """
    # Try config comments first, fall back to TikTok-specific ones
    if config.COMMENTS.get('comment_texts'):
        return random.choice(config.COMMENTS['comment_texts'])
    return random.choice(TIKTOK_COMMENTS)


def click_random_content_in_explore():
    """
    Click on a random content item in the TikTok Explore dual-column layout.
    The layout has left and right columns with content thumbnails.

    Returns:
        bool: True if clicked successfully
    """
    log_message("Clicking random content in Explore...")

    region = get_iphone_mirroring_region()
    if not region:
        log_message("Could not find iPhone Mirroring window", level="ERROR")
        return False

    left, top, width, height = region

    # Calculate positions for left and right columns
    # Explore layout: two columns side by side
    # Left column center: approximately 1/4 of the width
    # Right column center: approximately 3/4 of the width

    left_col_x = left + int(width * 0.25)
    right_col_x = left + int(width * 0.75)

    # Vertical position: somewhere in the middle area of the screen
    # Avoid top (navigation) and bottom (tab bar)
    min_y = top + int(height * 0.25)
    max_y = top + int(height * 0.65)

    # Randomly choose left or right column
    chosen_x = random.choice([left_col_x, right_col_x])
    chosen_y = random.randint(min_y, max_y)

    log_message(f"Clicking at ({chosen_x}, {chosen_y})")
    pyautogui.click(chosen_x, chosen_y)

    # Wait for content to load
    time.sleep(config.TIMING.get('wait_after_open_post', 1.5))
    return True


def find_and_click_comment_input():
    """
    Try to find the comment input field.
    First try video input, then photo post input.

    Returns:
        tuple: (success: bool, is_video: bool)
            - success: True if found and clicked
            - is_video: True if this is a video page, False if photo post
    """
    log_message("Looking for comment input field...")

    # Try video comment input first
    location = find_element_on_screen(
        TIKTOK_IMAGES['video_comment_input'],
        confidence=config.PIXEL_MATCHING['confidence'],
        grayscale=config.PIXEL_MATCHING['grayscale']
    )

    if location:
        log_message("Found video comment input", level="SUCCESS")
        pyautogui.click(location)
        time.sleep(0.5)
        return (True, True)  # success=True, is_video=True

    # Try photo post comment input
    location = find_element_on_screen(
        TIKTOK_IMAGES['photo_comment_input'],
        confidence=config.PIXEL_MATCHING['confidence'],
        grayscale=config.PIXEL_MATCHING['grayscale']
    )

    if location:
        log_message("Found photo post comment input", level="SUCCESS")
        pyautogui.click(location)
        time.sleep(0.5)
        return (True, False)  # success=True, is_video=False

    log_message("No comment input field found", level="WARNING")
    return (False, False)


def type_and_submit_comment():
    """
    Type a comment and submit it using Enter key.
    TikTok uses Enter key to submit, not a button.

    Returns:
        bool: True if successful
    """
    # Type comment
    comment = get_tiktok_comment()
    log_message(f"Typing comment: '{comment}'")

    # Use pyautogui.write for ASCII characters
    pyautogui.write(comment, interval=0.03)
    time.sleep(0.5)

    # Submit with Enter key
    log_message("Submitting comment with Enter key...")
    pyautogui.press('enter')
    time.sleep(config.TIMING.get('wait_after_comment_submit', 1.5))

    log_message("Comment submitted", level="SUCCESS")
    return True


def go_back_to_explore(is_video=False):
    """
    Click the back button to return to the Explore feed.

    Args:
        is_video: If True, use relative coordinates (for video pages with dynamic backgrounds)
                  If False, use pixel matching (for photo posts)

    Returns:
        bool: True if successful
    """
    log_message("Going back to Explore feed...")

    if is_video:
        # For video pages: use relative coordinates because background is dynamic
        log_message("Using relative coordinates for video page back button")
        position = get_video_button_position('back_button')
        if position:
            pyautogui.click(position)
            time.sleep(config.TIMING.get('wait_after_dialog_close', 1.0))
            log_message("Returned to Explore feed", level="SUCCESS")
            return True
    else:
        # For photo posts: use pixel matching
        location = find_element_on_screen(
            TIKTOK_IMAGES['back_button'],
            confidence=config.PIXEL_MATCHING['confidence'],
            grayscale=config.PIXEL_MATCHING['grayscale']
        )

        if location:
            pyautogui.click(location)
            time.sleep(config.TIMING.get('wait_after_dialog_close', 1.0))
            log_message("Returned to Explore feed", level="SUCCESS")
            return True

    log_message("Back button not found, trying swipe gesture", level="WARNING")
    # Fallback: swipe right from left edge (iOS back gesture)
    region = get_iphone_mirroring_region()
    if region:
        left, top, width, height = region
        start_x = left + 10  # Near left edge
        center_y = top + height // 2
        end_x = start_x + width // 3
        # Simulate swipe gesture
        pyautogui.mouseDown(start_x, center_y, button='left')
        time.sleep(0.05)
        pyautogui.moveTo(end_x, center_y, duration=0.3)
        pyautogui.mouseUp(button='left')
        time.sleep(config.TIMING.get('wait_after_dialog_close', 1.0))

    return True


def scroll_in_area(duration=3.0):
    """
    Scroll within the current view for a specified duration.
    Used for browsing comments.

    Args:
        duration: How long to scroll (in seconds)
    """
    log_message(f"Scrolling for {duration} seconds...")

    feed_center = get_iphone_mirroring_center()
    if feed_center:
        pyautogui.moveTo(feed_center[0], feed_center[1])

    start_time = time.time()
    while time.time() - start_time < duration:
        scroll_amount = random.randint(-300, -500)
        pyautogui.scroll(scroll_amount)
        time.sleep(random.uniform(0.3, 0.6))

    log_message("Finished scrolling", level="SUCCESS")


def browse_comments_and_exit():
    """
    Browse comments on a random content item:
    1. Click on random content in Explore
    2. Click comment button to open comments
    3. Scroll through comments for ~3 seconds
    4. Exit:
       - For videos: close comment section first, then exit (using relative coordinates)
       - For photo posts: just click back button (using pixel matching)

    Returns:
        bool: True if successful
    """
    log_message("=" * 50)
    log_message("Browsing comments before exit...", level="INFO")
    log_message("=" * 50)

    # 1. Click on random content
    if not click_random_content_in_explore():
        return False

    # 2. Determine if this is a video or photo post and click comment button
    is_video = False

    # First, try to detect content type by looking for PHOTO POST comment input
    # (Photo post backgrounds are static, so pixel matching works reliably)
    # If not found, assume it's a video page
    photo_input = find_element_on_screen(
        TIKTOK_IMAGES['photo_comment_input'],
        confidence=config.PIXEL_MATCHING['confidence'],
        grayscale=config.PIXEL_MATCHING['grayscale']
    )

    if photo_input:
        # This is a photo post - use pixel matching for comment button
        is_video = False
        log_message("Detected photo post, using pixel matching for comment button")
        location = find_element_on_screen(
            TIKTOK_IMAGES['photo_comment_button'],
            confidence=config.PIXEL_MATCHING['confidence'],
            grayscale=config.PIXEL_MATCHING['grayscale']
        )

        if location:
            log_message("Found photo post comment button", level="SUCCESS")
            pyautogui.click(location)
            time.sleep(1.0)
        else:
            log_message("Photo comment button not found", level="WARNING")
            go_back_to_explore(is_video=False)
            return False
    else:
        # No photo input found - assume this is a video page
        # Use relative coordinates for comment button (video backgrounds are dynamic)
        is_video = True
        log_message("Detected video page, using relative coordinates for comment button")
        position = get_video_button_position('comment_button')
        if position:
            pyautogui.click(position)
            time.sleep(1.0)
        else:
            log_message("Could not calculate comment button position", level="WARNING")
            go_back_to_explore(is_video=True)
            return False

    # 3. Scroll through comments for about 3 seconds
    scroll_in_area(duration=3.0)

    # 4. Exit based on content type
    if is_video:
        # For videos: close comment section first
        log_message("Closing video comment section...")
        close_location = find_element_on_screen(
            TIKTOK_IMAGES['comment_section_close'],
            confidence=config.PIXEL_MATCHING['confidence'],
            grayscale=config.PIXEL_MATCHING['grayscale']
        )

        if close_location:
            pyautogui.click(close_location)
            time.sleep(0.5)
            log_message("Comment section closed", level="SUCCESS")

        # Then go back to explore using relative coordinates
        go_back_to_explore(is_video=True)
    else:
        # For photo posts: just click back button using pixel matching
        go_back_to_explore(is_video=False)

    log_message("Finished browsing comments", level="SUCCESS")
    return True


def scroll_explore_feed():
    """
    Scroll down the Explore feed to reveal new content.
    """
    log_message("Scrolling Explore feed...")

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


def comment_on_tiktok_content():
    """
    Complete workflow to comment on a TikTok video or photo post:
    1. Click on random content in Explore
    2. Find and click comment input field
    3. Type comment and submit with Enter
    4. Go back to Explore feed

    Returns:
        bool: True if successful
    """
    # 1. Click on random content
    if not click_random_content_in_explore():
        return False

    # 2. Find and click comment input field
    success, is_video = find_and_click_comment_input()
    if not success:
        # Still try to go back even if we couldn't find comment input
        # Try relative coordinates first (assume video), then fallback
        go_back_to_explore(is_video=True)
        return False

    # 3. Type and submit comment
    type_and_submit_comment()

    # 4. Go back to Explore feed (use appropriate method based on content type)
    go_back_to_explore(is_video=is_video)

    log_message("Comment posted successfully", level="SUCCESS")
    return True


def run_tiktok_comment_cycle(run_number, total_runs):
    """
    Execute one complete comment cycle on TikTok:
    1. Comment on a random content item
    2. Scroll to reveal new content

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

        # 1. Comment on content
        success = comment_on_tiktok_content()

        # 2. Take screenshot if enabled
        if success and config.AUTOMATION['enable_screenshots']:
            take_screenshot(f"tiktok_comment_{run_number}")

        # 3. Scroll to reveal new content
        scroll_explore_feed()

        # 4. Wait before next cycle
        time.sleep(config.TIMING['wait_between_runs'])

        log_message(f"Run {run_number} completed", level="SUCCESS")
        return success

    except Exception as e:
        log_message(f"Run {run_number} failed: {e}", level="ERROR")
        return False


def main():
    """
    Main function for TikTok Comment automation
    """
    setup_directories()
    pyautogui.FAILSAFE = config.AUTOMATION['enable_failsafe']

    log_message("=" * 50)
    log_message("TikTok Comment Automation", level="INFO")
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

            success = run_tiktok_comment_cycle(run_num, config.AUTOMATION['number_of_runs'])
            if success:
                successful_cycles += 1
            else:
                failed_cycles += 1

            iter_end = datetime.now()
            duration = (iter_end - iter_start).total_seconds()
            log_message(f"[TIMER] Run {run_num} ended at  {iter_end.strftime('%Y-%m-%d %H:%M:%S.%f')} (took {duration:.2f}s)")
            timing_records.append({'run': run_num, 'start': iter_start, 'end': iter_end, 'duration': duration})

        # After all comment cycles, browse comments on one more post before exiting
        log_message("\nAll comment cycles completed. Now browsing comments...")
        browse_comments_and_exit()

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
