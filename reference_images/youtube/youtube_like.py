#!/usr/bin/env python3
"""
YouTube Like Automation
Scrolls through YouTube and likes videos using pixel matching
"""

import pyautogui
import time
import random
from datetime import datetime
from pathlib import Path
from core import config
from core.utils import log_message, take_screenshot, setup_directories, get_iphone_mirroring_center, get_iphone_mirroring_region


# YouTube-specific reference images
YOUTUBE_LIKE_BUTTON_IMAGES = ['youtube/youtube_like_button.png', 'youtube/youtube_like_button_dark.png']


def find_youtube_like_buttons(confidence=0.7, grayscale=True):
    """
    Find all YouTube like buttons on screen using pixel matching

    Args:
        confidence: Matching confidence threshold (0.0 to 1.0)
        grayscale: Use grayscale matching for speed

    Returns:
        list: List of (x, y) coordinates for all found like buttons
    """
    like_buttons = []

    # Limit search to iPhone Mirroring window
    region = get_iphone_mirroring_region()
    if region:
        log_message(f"Searching within iPhone Mirroring window: {region}")

    for img_name in YOUTUBE_LIKE_BUTTON_IMAGES:
        img_path = Path('..') / img_name

        if not img_path.exists():
            log_message(f"Reference image not found: {img_path}", level="WARNING")
            continue

        log_message(f"Searching for YouTube like buttons using: {img_name}")
        log_message(f"  Confidence: {confidence}, Grayscale: {grayscale}")

        try:
            matches = list(pyautogui.locateAllOnScreen(
                str(img_path),
                confidence=confidence,
                grayscale=grayscale,
                region=region
            ))

            if matches:
                log_message(f"  Found {len(matches)} match(es) with {img_name}", level="SUCCESS")
                for match in matches:
                    center = pyautogui.center(match)
                    like_buttons.append(center)
                    log_message(f"    Button at: {center}")
            else:
                log_message(f"  No matches found with {img_name}", level="WARNING")

        except pyautogui.ImageNotFoundException:
            log_message(f"  Image not found on screen: {img_name}", level="WARNING")
        except Exception as e:
            log_message(f"  Error searching for {img_name}: {e}", level="WARNING")

    # Remove duplicates (buttons within 20 pixels)
    unique_buttons = []
    for btn in like_buttons:
        is_duplicate = False
        for existing in unique_buttons:
            if abs(btn[0] - existing[0]) < 20 and abs(btn[1] - existing[1]) < 20:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_buttons.append(btn)

    if len(unique_buttons) != len(like_buttons):
        log_message(f"Removed {len(like_buttons) - len(unique_buttons)} duplicate(s)")

    return unique_buttons


def like_video_on_youtube():
    """
    Find all like buttons on YouTube and click a random one

    Returns:
        bool: True if successful, False otherwise
    """
    log_message("Looking for videos to like on YouTube...")

    like_buttons = find_youtube_like_buttons(
        confidence=config.PIXEL_MATCHING['confidence'],
        grayscale=config.PIXEL_MATCHING['grayscale']
    )

    if not like_buttons:
        log_message("No like buttons found on YouTube", level="WARNING")
        return False

    selected_button = random.choice(like_buttons)
    log_message(f"Randomly selected button at {selected_button} (from {len(like_buttons)} found)")

    log_message(f"Clicking like button at {selected_button}")
    pyautogui.click(selected_button)
    time.sleep(config.TIMING['wait_after_like'])

    log_message("Video liked successfully", level="SUCCESS")
    return True


def scroll_youtube_feed():
    """
    Scroll down the YouTube feed to reveal new videos
    For YouTube, scroll below center (video player is at top)
    """
    log_message("Scrolling YouTube feed...")

    # Get window region and scroll below center (avoid video player area)
    region = get_iphone_mirroring_region()
    if region:
        left, top, width, height = region
        scroll_x = left + width // 2
        scroll_y = top + int(height * 0.75)  # 75% down from top (below video player)
        pyautogui.moveTo(scroll_x, scroll_y)
        log_message(f"Moved to scroll position: ({scroll_x}, {scroll_y})")
    else:
        log_message("Could not find window, scrolling at current position", level="WARNING")

    scroll_amount = config.AUTOMATION.get('main_feed_scroll_amount', -600)
    scroll_attempts = config.AUTOMATION.get('main_feed_scroll_attempts', 3)

    for _ in range(scroll_attempts):
        random_scroll = int(scroll_amount * random.uniform(0.8, 1.2))
        pyautogui.scroll(random_scroll)
        time.sleep(random.uniform(0.1, 0.2))

    time.sleep(config.TIMING['wait_after_scroll'])


def click_video_thumbnail():
    """
    Click on a video thumbnail to open the video player
    Clicks at the feed center position

    Returns:
        bool: True if successfully entered video, False otherwise
    """
    log_message("Clicking on video thumbnail to open video...")

    # Click at feed center
    region = get_iphone_mirroring_region()
    if region:
        left, top, width, height = region
        click_x = left + width // 2
        click_y = top + int(height * 0.5)  # Center of window
        pyautogui.click(click_x, click_y)
        log_message(f"Clicked at: ({click_x}, {click_y})")
    else:
        pyautogui.click()

    # Wait for video to load
    time.sleep(3)

    # Check if we successfully entered a video by looking for like button
    like_buttons = find_youtube_like_buttons(
        confidence=config.PIXEL_MATCHING['confidence'],
        grayscale=config.PIXEL_MATCHING['grayscale']
    )

    if like_buttons:
        log_message("Successfully entered video (like button found)", level="SUCCESS")
        return True
    else:
        log_message("May not have entered video (no like button found)", level="WARNING")
        return False


def go_back_from_video():
    """
    Go back from video player to feed
    Uses swipe gesture (swipe right from left edge) for iOS
    """
    log_message("Going back to feed...")

    # Get iPhone Mirroring window region dynamically
    region = get_iphone_mirroring_region()
    if region:
        left, top, width, height = region
        start_x = left + 10  # Near left edge of window
        end_x = left + width // 2  # Swipe to middle
        y = top + height // 2  # Middle height
    else:
        # Fallback to defaults
        start_x = 870
        end_x = 1100
        y = 400

    log_message(f"Swiping from ({start_x}, {y}) to ({end_x}, {y})")
    pyautogui.moveTo(start_x, y)
    time.sleep(0.1)
    pyautogui.drag(end_x - start_x, 0, duration=0.3)

    time.sleep(config.TIMING.get('wait_after_close_post', 1.0))
    log_message("Returned to feed")


def run_youtube_cycle(run_number, total_runs, max_retries=3):
    """
    Execute one complete cycle on YouTube:
    1. Click to enter video (retry if clicked between videos)
    2. Like the video
    3. Scroll down to next video

    Args:
        run_number: Current run number
        total_runs: Total number of runs
        max_retries: Max retries if failed to enter video

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        log_message("=" * 50)
        log_message(f"Run {run_number}/{total_runs}", level="INFO")
        log_message("=" * 50)

        # 1. Try to enter a video (with retry if clicked between videos)
        entered_video = False
        for attempt in range(1, max_retries + 1):
            entered_video = click_video_thumbnail()
            if entered_video:
                break
            else:
                log_message(f"Retry {attempt}/{max_retries}: Didn't enter video, scrolling and trying again...", level="WARNING")
                scroll_youtube_feed()

        if not entered_video:
            log_message("Failed to enter video after retries", level="ERROR")
            scroll_youtube_feed()
            return False

        # 2. Find and like the video
        success = like_video_on_youtube()

        # 3. Take screenshot if enabled
        if success and config.AUTOMATION['enable_screenshots']:
            take_screenshot(f"youtube_like_{run_number}")

        # 4. Scroll down to next video
        scroll_youtube_feed()

        # 5. Wait before next cycle
        time.sleep(config.TIMING['wait_between_runs'])

        log_message(f"Run {run_number} completed {'successfully' if success else 'with issues'}", level="SUCCESS" if success else "WARNING")
        return success

    except Exception as e:
        log_message(f"Run {run_number} failed: {e}", level="ERROR")
        return False


def main():
    """
    Main function for YouTube Like automation
    """
    setup_directories()
    pyautogui.FAILSAFE = config.AUTOMATION['enable_failsafe']

    log_message("=" * 50)
    log_message("YouTube Like Automation", level="INFO")
    log_message("=" * 50)
    log_message(f"Number of runs: {config.AUTOMATION['number_of_runs']}")
    log_message(f"Screenshots enabled: {config.AUTOMATION['enable_screenshots']}")
    log_message(f"Failsafe enabled: {config.AUTOMATION['enable_failsafe']}")
    log_message(f"Reference images: {YOUTUBE_LIKE_BUTTON_IMAGES}")

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

            success = run_youtube_cycle(run_num, config.AUTOMATION['number_of_runs'])
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
