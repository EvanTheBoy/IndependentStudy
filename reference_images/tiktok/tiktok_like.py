#!/usr/bin/env python3
"""
TikTok Like Automation
Finds and clicks like buttons on TikTok using pixel matching
"""

import pyautogui
import time
import random
from datetime import datetime
from pathlib import Path
from core import config
from core.utils import log_message, take_screenshot, setup_directories


def find_tiktok_like_buttons(confidence=0.7):
    """
    Find all TikTok like buttons on screen
    
    Returns:
        list: List of (x, y) coordinates for all found like buttons
    """
    like_buttons = []
    ref_image = Path('tiktok_like_button.png')
    
    if not ref_image.exists():
        log_message(f"Reference image not found: {ref_image}", level="WARNING")
        return like_buttons
    
    log_message("Searching for TikTok like buttons...")
    
    try:
        matches = list(pyautogui.locateAllOnScreen(
            str(ref_image),
            confidence=confidence,
            grayscale=False
        ))
        
        if matches:
            log_message(f"✓ Found {len(matches)} like button(s)")
            for match in matches:
                center = pyautogui.center(match)
                like_buttons.append(center)
                log_message(f"  Button at: {center}")
        else:
            log_message("No like buttons found", level="WARNING")
            
    except Exception as e:
        log_message(f"Error searching for like buttons: {e}", level="WARNING")
    
    return like_buttons


def like_random_video():
    """
    Find all like buttons and click a random one
    
    Returns:
        bool: True if successful, False otherwise
    """
    log_message("Looking for TikTok videos to like...")
    
    # Find all like buttons
    like_buttons = find_tiktok_like_buttons()
    
    if not like_buttons:
        log_message("No like buttons found", level="WARNING")
        return False
    
    # Randomly select one
    selected_button = random.choice(like_buttons)
    log_message(f"Randomly selected button at {selected_button}")
    
    # Click it
    log_message(f"Clicking like button at {selected_button}")
    pyautogui.click(selected_button)
    time.sleep(1.0)
    
    log_message("Video liked successfully", level="SUCCESS")
    return True


def scroll_tiktok_feed():
    """
    Scroll down the TikTok feed to reveal new videos
    """
    log_message("Scrolling TikTok feed...")
    
    # Get current mouse position
    current_pos = pyautogui.position()
    log_message(f"Scrolling at current position: {current_pos}")
    
    # TikTok usually needs bigger scrolls
    scroll_amount = -500
    scroll_attempts = 3
    
    for _ in range(scroll_attempts):
        random_scroll = int(scroll_amount * random.uniform(0.8, 1.2))
        pyautogui.scroll(random_scroll)
        time.sleep(random.uniform(0.1, 0.2))
    
    # Wait for content to load
    time.sleep(2)


def run_tiktok_cycle(run_number, total_runs):
    """
    Execute one complete scroll-and-like cycle on TikTok
    
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
        
        # 1. Scroll to reveal new videos
        scroll_tiktok_feed()
        
        # 2. Find and like a random video
        success = like_random_video()
        
        # 3. Take screenshot if enabled
        if success and config.AUTOMATION['enable_screenshots']:
            take_screenshot(f"tiktok_like_{run_number}")
        
        # 4. Wait before next cycle
        time.sleep(config.TIMING['wait_between_runs'])
        
        log_message(f"Run {run_number} completed", level="SUCCESS")
        return success
        
    except Exception as e:
        log_message(f"Run {run_number} failed: {e}", level="ERROR")
        return False


def main():
    """
    Main function for TikTok Like automation
    """
    # Setup
    setup_directories()
    
    # Enable PyAutoGUI failsafe
    pyautogui.FAILSAFE = config.AUTOMATION['enable_failsafe']
    
    log_message("=" * 50)
    log_message("TikTok Like Automation", level="INFO")
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
    timing_records = []

    try:
        # Run automation cycles
        for run_num in range(1, config.AUTOMATION['number_of_runs'] + 1):
            iter_start = datetime.now()
            log_message(f"[TIMER] Run {run_num} started at {iter_start.strftime('%Y-%m-%d %H:%M:%S.%f')}")

            success = run_tiktok_cycle(run_num, config.AUTOMATION['number_of_runs'])

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
