"""
Instagram Automation Script with Static UI Element Recognition
Uses static UI elements (buttons, icons) instead of post content for image recognition
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


def find_element(image_name, confidence=0.8, description="element", region=None):
    """
    Find an image on screen and return its location

    Args:
        image_name: Name of the reference image file
        confidence: Matching confidence (0.0 to 1.0)
        description: Description for logging
        region: Optional (left, top, width, height) to search in specific area

    Returns:
        tuple: (x, y) coordinates if found, None otherwise
    """
    try:
        image_path = REFERENCE_DIR / image_name
        
        if not image_path.exists():
            log_message(f"Reference image not found: {image_path}", level="ERROR")
            return None

        log_message(f"Looking for {description}...")
        
        if region:
            location = pyautogui.locateCenterOnScreen(str(image_path), confidence=confidence, region=region)
        else:
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


def find_instagram_window():
    """
    Find the Instagram/iPhone Mirroring window by looking for static UI elements
    
    Returns:
        tuple: (x, y, width, height) of the window, or None
    """
    # Try to find Instagram logo or top bar
    logo = find_element('instagram_logo.png', confidence=0.8, description="Instagram logo")
    
    if logo:
        # Estimate window bounds based on logo position
        # Typical iPhone Mirroring window is ~400px wide, ~800px tall
        window_left = logo[0] - 200
        window_top = logo[1] - 50
        window_width = 400
        window_height = 800
        
        return (window_left, window_top, window_width, window_height)
    
    return None


def scroll_feed():
    """
    Scroll down the Instagram feed
    """
    # Find a static reference point (like bottom nav bar or feed background)
    feed_ref = find_element('feed_reference.png', confidence=0.7, description="feed reference")
    
    if not feed_ref:
        # Fallback to center of screen
        log_message("Using fallback scroll position", level="WARNING")
        feed_ref = (pyautogui.size()[0] // 2, pyautogui.size()[1] // 2)

    log_message("Scrolling feed...")

    # Move mouse to feed area
    pyautogui.moveTo(feed_ref)
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
    Like the current post by finding and clicking the heart icon
    """
    log_message("Looking for like button...")
    
    # Try to find the heart/like button icon
    like_button = find_element('like_button_icon.png', confidence=0.8, description="like button")
    
    if like_button:
        log_message("Clicking like button...")
        pyautogui.click(like_button)
    else:
        # Fallback: double-click in center of screen
        log_message("Using double-click fallback for liking", level="WARNING")
        center = (pyautogui.size()[0] // 2, pyautogui.size()[1] // 2)
        pyautogui.doubleClick(center)

    # Wait for animation
    time.sleep(config.TIMING['wait_after_like'])
    return True


def open_post():
    """
    Click on a post in the feed to open it
    Uses relative positioning from static UI elements
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        log_message("Opening post...")

        # Find a static reference point and click below it (where posts are)
        window = find_instagram_window()
        
        if window:
            # Click in the middle of the window, slightly below center
            click_x = window[0] + window[2] // 2
            click_y = window[1] + window[3] // 2 + 100
            
            pyautogui.click(click_x, click_y)
        else:
            # Fallback to screen center
            log_message("Using fallback position for opening post", level="WARNING")
            pyautogui.click(pyautogui.size()[0] // 2, pyautogui.size()[1] // 2)

        # Wait for post view to load
        time.sleep(config.TIMING['wait_after_open_post'])
        log_message("Post opened successfully", level="SUCCESS")
        return True

    except Exception as e:
        log_message(f"Failed to open post: {e}", level="ERROR")
        return False


def close_post():
    """
    Close the post view by finding and clicking the back button (←)

    Returns:
        bool: True if successful, False otherwise
    """
    max_retries = 2
    
    for attempt in range(1, max_retries + 1):
        try:
            log_message(f"Closing post view... (attempt {attempt}/{max_retries})")

            # Find the back button (← arrow) - this is always static
            # Try small version first
            back_button = find_element('back_arrow_small.png', confidence=0.7, description="back arrow (small)")
            
            if not back_button:
                # Try original size
                back_button = find_element('back_arrow.png', confidence=0.7, description="back arrow (original)")
            
            if back_button:
                pyautogui.click(back_button)
                time.sleep(config.TIMING['wait_after_close_post'])
                log_message("Post closed successfully", level="SUCCESS")
                return True
            else:
                log_message(f"Back button not found (attempt {attempt})", level="WARNING")
                
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
    Execute one complete scroll-and-like cycle using static UI recognition
    
    Workflow:
    1. Click to open post
    2. Like the post (find heart icon or double-click)
    3. Take screenshot
    4. Close post (find back arrow)
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

        # 5. Scroll feed down to next post
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
    print(" " * 8 + "INSTAGRAM AUTOMATION (Static UI Recognition)")
    print("=" * 60)
    log_message(f"Starting automation with {num_runs} runs")
    log_message("Make sure iPhone Mirroring window is visible!")
    log_message("This version uses static UI elements (buttons, icons)")
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
