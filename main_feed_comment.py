"""
Script B: Main Feed Comment Automation
Scrolls through Instagram main feed and comments on posts using pixel matching
"""

import pyautogui
import time
import random
from pathlib import Path
import config
from utils import log_message, take_screenshot, setup_directories


def find_comment_button(confidence=0.8, region=None, grayscale=False):
    """
    Find the comment button using pixel matching
    
    Tries multiple reference images (light and dark theme)
    Finds the topmost button to avoid clicking Kiro icons
    
    Args:
        confidence: Matching confidence threshold (0.0 to 1.0)
        region: Optional search region (left, top, width, height)
        grayscale: Use grayscale matching for speed
        
    Returns:
        tuple: (x, y) coordinates if found, None otherwise
    """
    for image_name in config.PIXEL_MATCHING['comment_button_images']:
        image_path = Path('reference_images') / image_name
        
        if not image_path.exists():
            log_message(f"Reference image not found: {image_path}", level="WARNING")
            continue
        
        log_message(f"Trying to find comment button using: {image_name}")
            
        try:
            # Use locateOnScreen (finds first match, same as like button)
            location = pyautogui.locateOnScreen(
                str(image_path),
                confidence=confidence,
                region=region,
                grayscale=grayscale
            )
            
            if location:
                # Click on left-center of the matched region for better accuracy
                left, top, width, height = location
                click_x = left + int(width * 0.25)
                click_y = top + int(height * 0.5)
                click_point = (click_x, click_y)
                
                log_message(f"✓ Found comment button with {image_name} at region {location}", level="SUCCESS")
                log_message(f"Will click at adjusted position: {click_point}")
                return click_point
            else:
                log_message(f"  ✗ No match found with {image_name}", level="WARNING")
                
        except pyautogui.ImageNotFoundException:
            log_message(f"  ✗ Image not found: {image_name}", level="WARNING")
        except Exception as e:
            log_message(f"Error searching for {image_name}: {e}", level="WARNING")
            
    return None



def get_comment_text():
    """
    Get comment text from configuration
    
    Returns:
        str: Comment text to post
    """
    if config.COMMENTS['use_random'] and config.COMMENTS['comment_texts']:
        return random.choice(config.COMMENTS['comment_texts'])
    elif config.COMMENTS['comment_texts']:
        return config.COMMENTS['comment_texts'][0]
    else:
        return config.COMMENTS['default_comment']



def scroll_main_feed():
    """
    Scroll down the main feed to reveal new posts
    """
    log_message("Scrolling main feed...")
    
    # Get current mouse position (should be on Instagram after previous action)
    current_pos = pyautogui.position()
    log_message(f"Scrolling at current position: {current_pos}")
    
    # Perform scroll with randomization for more natural behavior
    scroll_amount = config.AUTOMATION['main_feed_scroll_amount']
    scroll_attempts = config.AUTOMATION['main_feed_scroll_attempts']
    
    for _ in range(scroll_attempts):
        # Add ±20% randomness to scroll amount
        random_scroll = int(scroll_amount * random.uniform(0.8, 1.2))
        pyautogui.scroll(random_scroll)
        time.sleep(random.uniform(0.1, 0.2))
    
    # Wait for content to load
    time.sleep(config.TIMING['wait_after_scroll'])


def comment_on_post_in_feed():
    """
    Comment on a post in the main feed
    
    Workflow:
    1. Find and click comment button using pixel matching
    2. Wait for comment dialog
    3. Type comment text
    4. Submit comment
    5. Close dialog
    
    Returns:
        bool: True if successful, False otherwise
    """
    log_message("Commenting on post...")
    
    # 1. Find comment button using pixel matching
    button_location = find_comment_button(
        confidence=config.PIXEL_MATCHING['confidence'],
        region=config.PIXEL_MATCHING['search_region'],
        grayscale=config.PIXEL_MATCHING['grayscale']
    )
    
    if button_location:
        log_message(f"✓ Found comment button with pixel matching at {button_location}", level="SUCCESS")
    else:
        log_message("Pixel matching failed, using static coordinates", level="WARNING")
        button_location = config.COORDINATES['comment_button']
    
    # 2. Click comment button
    log_message(f"Clicking comment button at {button_location}")
    pyautogui.click(button_location)
    time.sleep(config.TIMING['wait_after_comment_click'])
    
    # 3. Find and click the comment input field (try both themes)
    log_message("Finding comment input field...")
    input_images = ['comment_input.png', 'comment_input_dark.png']
    input_found = False
    
    for img_name in input_images:
        input_img = Path('reference_images') / img_name
        if not input_img.exists():
            continue
            
        try:
            log_message(f"Trying {img_name}...")
            input_location = pyautogui.locateOnScreen(
                str(input_img),
                confidence=0.7,
                grayscale=False
            )
            
            if input_location:
                input_center = pyautogui.center(input_location)
                log_message(f"✓ Found input field with {img_name} at {input_center}")
                pyautogui.click(input_center)
                time.sleep(0.5)
                input_found = True
                break
        except Exception as e:
            log_message(f"Error with {img_name}: {e}", level="WARNING")
    
    if not input_found:
        log_message("Input field not found, trying Tab key", level="WARNING")
        pyautogui.press('tab')
        time.sleep(0.3)
    
    # 4. Type comment text
    comment_text = get_comment_text()
    log_message(f"Typing comment: '{comment_text}'")
    pyautogui.write(comment_text, interval=0.05)
    
    # 5. Find and click the submit button (arrow) - try both themes
    time.sleep(0.5)
    log_message("Finding submit button...")
    submit_images = ['comment_submit.png', 'comment_submit_dark.png']
    submit_found = False
    
    for img_name in submit_images:
        submit_img = Path('reference_images') / img_name
        if not submit_img.exists():
            continue
            
        try:
            log_message(f"Trying {img_name}...")
            submit_location = pyautogui.locateOnScreen(
                str(submit_img),
                confidence=0.7,
                grayscale=False
            )
            
            if submit_location:
                submit_center = pyautogui.center(submit_location)
                log_message(f"✓ Found submit button with {img_name} at {submit_center}")
                pyautogui.click(submit_center)
                time.sleep(config.TIMING['wait_after_comment_submit'])
                submit_found = True
                break
        except Exception as e:
            log_message(f"Error with {img_name}: {e}", level="WARNING")
    
    if not submit_found:
        log_message("Submit button not found, trying Enter key", level="WARNING")
        pyautogui.press('enter')
        time.sleep(config.TIMING['wait_after_comment_submit'])
    
    # 6. Close comment dialog by clicking outside (click above the dialog)
    log_message("Closing comment dialog...")
    close_x = button_location[0]
    close_y = button_location[1] - 200  # Click above the comment area to close
    pyautogui.click(close_x, close_y)
    time.sleep(config.TIMING['wait_after_dialog_close'])
    
    log_message("Comment posted successfully", level="SUCCESS")
    return True



def run_comment_cycle(run_number, total_runs):
    """
    Execute one complete scroll-and-comment cycle on main feed
    
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
        
        # 1. Scroll to reveal new post
        scroll_main_feed()
        
        # 2. Find and comment on the post
        success = comment_on_post_in_feed()
        
        # 3. Take screenshot if enabled
        if success and config.AUTOMATION['enable_screenshots']:
            take_screenshot(f"main_feed_comment_{run_number}")
        
        # 4. Wait before next cycle
        time.sleep(config.TIMING['wait_between_runs'])
        
        log_message(f"Run {run_number} completed", level="SUCCESS")
        return success
        
    except Exception as e:
        log_message(f"Run {run_number} failed: {e}", level="ERROR")
        return False



def main():
    """
    Main function for Script B: Main Feed Comment automation
    
    Initializes automation, runs comment cycles, and displays summary
    """
    # Setup
    setup_directories()
    
    # Enable PyAutoGUI failsafe if configured
    pyautogui.FAILSAFE = config.AUTOMATION['enable_failsafe']
    
    log_message("=" * 50)
    log_message("Script B: Main Feed Comment Automation", level="INFO")
    log_message("=" * 50)
    log_message(f"Number of runs: {config.AUTOMATION['number_of_runs']}")
    log_message(f"Screenshots enabled: {config.AUTOMATION['enable_screenshots']}")
    log_message(f"Failsafe enabled: {config.AUTOMATION['enable_failsafe']}")
    log_message(f"Random comments: {config.COMMENTS['use_random']}")
    
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
    
    try:
        # Run automation cycles
        for run_num in range(1, config.AUTOMATION['number_of_runs'] + 1):
            success = run_comment_cycle(run_num, config.AUTOMATION['number_of_runs'])
            
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
        
        log_message("=" * 50)
        log_message("Automation complete!", level="SUCCESS")


if __name__ == "__main__":
    main()
    