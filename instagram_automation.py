"""
Instagram Automation Script
Automates scrolling and liking on Instagram through iPhone Mirroring
"""
import pyautogui
import time
from datetime import datetime
from pathlib import Path
import config

# Setup PyAutoGUI
pyautogui.PAUSE = config.TIMING['pause_between_actions']
pyautogui.FAILSAFE = config.AUTOMATION['enable_failsafe']

# Create screenshots directory
SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)


def log_message(message, level="INFO"):
    """
    Print timestamped log message

    Args:
        message: Message to log
        level: Log level (INFO, SUCCESS, ERROR, WARNING)
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    symbols = {
        "INFO": "ℹ",
        "SUCCESS": "✓",
        "ERROR": "✗",
        "WARNING": "⚠"
    }
    symbol = symbols.get(level, "•")
    print(f"[{timestamp}] {symbol} {message}")


def take_screenshot(name):
    """
    Capture and save screenshot

    Args:
        name: Base name for the screenshot file

    Returns:
        Path to saved screenshot
    """
    if not config.AUTOMATION['enable_screenshots']:
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = SCREENSHOT_DIR / f"{name}_{timestamp}.png"

    screenshot = pyautogui.screenshot()
    screenshot.save(filename)

    log_message(f"Screenshot saved: {filename}")
    return filename


def scroll_feed():
    """
    Scroll down the Instagram feed using randomized scroll amounts
    Handles variable post sizes (reels, ads, regular posts)
    """
    import random
    
    feed_center = config.COORDINATES['feed_center']

    log_message("Scrolling feed...")

    # Move mouse to feed center (but don't click to avoid opening post)
    pyautogui.moveTo(feed_center)
    time.sleep(0.3)

    # Use randomized scroll amounts to handle variable post sizes
    # This makes it less predictable and more human-like
    scroll_amount = config.AUTOMATION['scroll_amount']
    scroll_attempts = config.AUTOMATION['scroll_attempts']
    
    for _ in range(scroll_attempts):
        # Add ±20% randomness to scroll amount
        random_scroll = int(scroll_amount * random.uniform(0.8, 1.2))
        pyautogui.scroll(random_scroll)
        time.sleep(random.uniform(0.1, 0.2))

    # Wait for content to load
    time.sleep(config.TIMING['wait_after_scroll'])


def like_post():
    """
    Like the current post (double-click method)
    """
    feed_center = config.COORDINATES['feed_center']

    log_message("Liking post...")

    # Double-click to like (Instagram feature)
    pyautogui.doubleClick(feed_center)

    # Wait for animation
    time.sleep(config.TIMING['wait_after_like'])


def open_post():
    """
    Click on a post in the feed to open the detailed view

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read feed_center coordinates from config
        feed_center = config.COORDINATES['feed_center']

        log_message("Opening post...")

        # Click on feed center to open post
        pyautogui.click(feed_center)

        # Wait for post view to load
        time.sleep(config.TIMING['wait_after_open_post'])

        log_message("Post opened successfully", level="SUCCESS")
        return True

    except Exception as e:
        # Log error if post fails to open
        log_message(f"Failed to open post: {e}", level="ERROR")
        return False


def close_post():
    """
    Close the post view and return to feed by clicking back button

    Returns:
        bool: True if successful, False otherwise
    """
    max_retries = 2
    
    for attempt in range(1, max_retries + 1):
        try:
            log_message(f"Closing post view... (attempt {attempt}/{max_retries})")

            # Click the back button to close post view
            back_button = config.COORDINATES['back_button']
            pyautogui.click(back_button)

            # Wait for feed to reappear
            time.sleep(config.TIMING['wait_after_close_post'])

            log_message("Post closed successfully", level="SUCCESS")
            return True

        except Exception as e:
            # Log error if post fails to close
            log_message(f"Failed to close post (attempt {attempt}): {e}", level="ERROR")
            
            # If this was the last attempt, return False
            if attempt == max_retries:
                log_message("Post failed to close after all retries", level="ERROR")
                return False
            
            # Wait a bit before retrying
            time.sleep(0.5)
    
    return False


def activate_window():
    """
    Click on iPhone Mirroring window to ensure it's active
    """
    feed_center = config.COORDINATES['feed_center']
    pyautogui.click(feed_center)
    time.sleep(0.3)


def run_automation_cycle(run_number, total_runs):
    """
    Execute one complete scroll-and-like cycle
    
    Workflow:
    1. Click to open post
    2. Like the post
    3. Take screenshot
    4. Close post and return to feed
    5. Scroll feed down to next post

    Args:
        run_number: Current run number (1-indexed)
        total_runs: Total number of runs

    Returns:
        bool: True if successful, False if error occurred
    """
    try:
        log_message("=" * 50)
        log_message(f"Run {run_number}/{total_runs}", level="INFO")
        log_message("=" * 50)

        # 1. Open the post
        if not open_post():
            log_message("Failed to open post, continuing to next cycle", level="WARNING")
            return False

        # 2. Like the post
        like_post()

        # 3. Take screenshot for verification
        take_screenshot(f"run_{run_number}_liked")

        # 4. Close post and return to feed
        if not close_post():
            log_message("Failed to close post, continuing to next cycle", level="WARNING")
            return False

        # Extra wait to ensure we're back in feed view
        log_message("Waiting for feed view to stabilize...")
        time.sleep(1.0)

        # 5. Scroll feed down to next post (after closing)
        scroll_feed()

        # 6. Wait before next cycle
        time.sleep(config.TIMING['wait_between_runs'])

        log_message(f"Run {run_number} completed", level="SUCCESS")
        return True

    except Exception as e:
        log_message(f"Run {run_number} failed: {e}", level="ERROR")
        return False


def main():
    """
    Main automation function
    """
    num_runs = config.AUTOMATION['number_of_runs']

    print("\n" + "=" * 60)
    print(" " * 15 + "INSTAGRAM AUTOMATION")
    print("=" * 60)
    log_message(f"Starting automation with {num_runs} runs")
    log_message("Make sure iPhone Mirroring window is visible!")
    log_message("Starting in 5 seconds...")
    print()

    # Countdown
    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    print()

    # Run automation
    successful_runs = 0
    failed_runs = 0

    for run in range(1, num_runs + 1):
        success = run_automation_cycle(run, num_runs)

        if success:
            successful_runs += 1
        else:
            failed_runs += 1

    # Summary
    print("\n" + "=" * 60)
    log_message("AUTOMATION COMPLETED", level="SUCCESS")
    print("=" * 60)
    log_message(f"Successful runs: {successful_runs}/{num_runs}")
    log_message(f"Failed runs: {failed_runs}/{num_runs}")

    if config.AUTOMATION['enable_screenshots']:
        log_message(f"Screenshots saved in: {SCREENSHOT_DIR.absolute()}")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
