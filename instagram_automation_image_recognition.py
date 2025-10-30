"""
Instagram Automation Script with Image Recognition
Automates scrolling and liking on Instagram using image recognition instead of fixed coordinates
"""
import pyautogui
import time
from datetime import datetime
from pathlib import Path
import config

# Setup PyAutoGUI
pyautogui.PAUSE = config.TIMING['pause_between_actions']
pyautogui.FAILSAFE = config.AUTOMATION['enable_failsafe']

# Create directories
SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)

REFERENCE_DIR = Path("reference_images")
REFERENCE_DIR.mkdir(exist_ok=True)


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


def find_and_click(image_name, confidence=0.8, description="element"):
    """
    Find an image on screen and click it

    Args:
        image_name: Name of the reference image file
        confidence: Matching confidence (0.0 to 1.0)
        description: Description for logging

    Returns:
        bool: True if found and clicked, False otherwise
    """
    try:
        image_path = REFERENCE_DIR / image_name
        
        if not image_path.exists():
            log_message(f"Reference image not found: {image_path}", level="ERROR")
            return False

        log_message(f"Looking for {description}...")
        location = pyautogui.locateCenterOnScreen(str(image_path), confidence=confidence)
        
        if location:
            log_message(f"Found {description} at {location}")
            pyautogui.click(location)
            return True
        else:
            log_message(f"Could not find {description}", level="WARNING")
            return False
            
    except Exception as e:
        log_message(f"Error finding {description}: {e}", level="ERROR")
        return False


def find_element(image_name, confidence=0.8, description="element"):
    """
    Find an image on screen and return its location

    Args:
        image_name: Name of the reference image file
        confidence: Matching confidence (0.0 to 1.0)
        description: Description for logging

    Returns:
        tuple: (x, y) coordinates if found, None otherwise
    """
    try:
        image_path = REFERENCE_DIR / image_name
        
        if not image_path.exists():
            log_message(f"Reference image not found: {image_path}", level="ERROR")
            return None

        log_message(f"Looking for {description}...")
        location = pyautogui.locateCenterOnScreen(str(image_path), confidence=confidence)
        
        if location:
            log_message(f"Found {description} at {location}")
            return location
        else:
            log_message(f"Could not find {description}", level="WARNING")
            return None
            
    except Exception as e:
        log_message(f"Error finding {description}: {e}", level="ERROR")
        return None


def scroll_feed():
    """
    Scroll down the Instagram feed using mouse wheel emulation
    """
    # Find the feed area
    feed_location = find_element('feed_area.png', confidence=0.7, description="feed area")
    
    if not feed_location:
        # Fallback to center of screen if feed not found
        log_message("Using fallback scroll position", level="WARNING")
        feed_location = (pyautogui.size()[0] // 2, pyautogui.size()[1] // 2)

    log_message("Scrolling feed...")

    # Move mouse to feed area
    pyautogui.moveTo(feed_location)
    time.sleep(0.3)

    # Scroll down
    scroll_amount = config.AUTOMATION.get('scroll_amount', -500)
    scroll_attempts = config.AUTOMATION.get('scroll_attempts', 5)
    
    for _ in range(scroll_attempts):
        pyautogui.scroll(scroll_amount)
        time.sleep(0.1)

    # Wait for content to load
    time.sleep(config.TIMING['wait_after_scroll'])


def like_post():
    """
    Like the current post (double-click method)
    """
    # Try image recognition first
    post_center = find_element('post_center.png', confidence=0.7, description="post center")
    
    if not post_center:
        # Fallback to configured coordinates
        log_message("Using fallback coordinates for liking", level="WARNING")
        post_center = config.COORDINATES.get('feed_center', (pyautogui.size()[0] // 2, pyautogui.size()[1] // 2))

    log_message("Liking post...")

    # Double-click to like
    pyautogui.doubleClick(post_center)

    # Wait for animation
    time.sleep(config.TIMING['wait_after_like'])
    return True


def open_post():
    """
    Click on a post in the feed to open the detailed view

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        log_message("Opening post...")

        # Find and click on a post
        if find_and_click('post_thumbnail.png', confidence=0.7, description="post"):
            # Wait for post view to load
            time.sleep(config.TIMING['wait_after_open_post'])
            log_message("Post opened successfully", level="SUCCESS")
            return True
        else:
            log_message("Failed to find post to open", level="ERROR")
            return False

    except Exception as e:
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

            # Try image recognition first
            if find_and_click('back_button.png', confidence=0.8, description="back button"):
                # Wait for feed to reappear
                time.sleep(config.TIMING['wait_after_close_post'])
                log_message("Post closed successfully", level="SUCCESS")
                return True
            else:
                # Fallback to configured coordinates
                log_message(f"Using fallback coordinates for back button (attempt {attempt})", level="WARNING")
                back_button = config.COORDINATES.get('back_button')
                if back_button:
                    pyautogui.click(back_button)
                    time.sleep(config.TIMING['wait_after_close_post'])
                    log_message("Post closed successfully (fallback)", level="SUCCESS")
                    return True
                
                if attempt == max_retries:
                    return False
                
                time.sleep(0.5)

        except Exception as e:
            log_message(f"Failed to close post (attempt {attempt}): {e}", level="ERROR")
            
            if attempt == max_retries:
                return False
            
            time.sleep(0.5)
    
    return False


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
        if not like_post():
            log_message("Failed to like post", level="WARNING")

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
    print(" " * 10 + "INSTAGRAM AUTOMATION (Image Recognition)")
    print("=" * 60)
    log_message(f"Starting automation with {num_runs} runs")
    log_message("Make sure iPhone Mirroring window is visible!")
    log_message("Reference images should be in: reference_images/")
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
