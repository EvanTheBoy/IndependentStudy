"""
Shared utility functions for Instagram automation scripts
"""

import pyautogui
from pathlib import Path
from datetime import datetime
from . import config

try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False


def get_iphone_mirroring_region(window_title='iPhone Mirroring'):
    """
    Get the region (left, top, width, height) of the iPhone Mirroring window.

    Args:
        window_title: Title of the window to find (default: 'iPhone Mirroring')

    Returns:
        tuple: (left, top, width, height) or None if not found
    """
    if not PYGETWINDOW_AVAILABLE:
        return None

    try:
        titles = gw.getAllTitles()
        for title in titles:
            if window_title in title:
                geom = gw.getWindowGeometry(title)
                left, top, width, height = geom
                return (int(left), int(top), int(width), int(height))
        return None
    except Exception as e:
        return None


def get_iphone_mirroring_center(window_title='iPhone Mirroring'):
    """
    Get the center coordinates of the iPhone Mirroring window.

    Args:
        window_title: Title of the window to find (default: 'iPhone Mirroring')

    Returns:
        tuple: (x, y) center coordinates, or fallback to config if not found
    """
    if not PYGETWINDOW_AVAILABLE:
        log_message("pygetwindow not installed. Using config coordinates.", level="WARNING")
        return config.COORDINATES.get('feed_center')

    try:
        # macOS: search through all window titles
        titles = gw.getAllTitles()
        for title in titles:
            if window_title in title:
                # getWindowGeometry returns (left, top, width, height)
                geom = gw.getWindowGeometry(title)
                left, top, width, height = geom
                center_x = int(left + width / 2)
                center_y = int(top + height / 2)
                log_message(f"Found '{title}' window at center: ({center_x}, {center_y})")
                return (center_x, center_y)

        log_message(f"Window containing '{window_title}' not found", level="WARNING")
        return config.COORDINATES.get('feed_center')
    except Exception as e:
        log_message(f"Error finding window: {e}", level="ERROR")
        return config.COORDINATES.get('feed_center')


def log_message(message, level="INFO"):
    """
    Print timestamped log message with level indicator
    
    Args:
        message: Message to log
        level: Log level (INFO, SUCCESS, ERROR, WARNING)
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    symbols = {"INFO": "ℹ", "SUCCESS": "✓", "ERROR": "✗", "WARNING": "⚠"}
    symbol = symbols.get(level, "•")
    print(f"[{timestamp}] {symbol} {message}")


def take_screenshot(name):
    """
    Capture and save screenshot
    
    Args:
        name: Base name for the screenshot file
        
    Returns:
        Path: Path to saved screenshot or None if screenshots disabled
    """
    if not config.AUTOMATION['enable_screenshots']:
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = Path("screenshots") / f"{name}_{timestamp}.png"
    
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    
    log_message(f"Screenshot saved: {filename}")
    return filename


def setup_directories():
    """Create necessary directories if they don't exist"""
    Path("screenshots").mkdir(exist_ok=True)
    Path("reference_images").mkdir(exist_ok=True)
