"""
Shared utility functions for Instagram automation scripts
"""

import pyautogui
from pathlib import Path
from datetime import datetime
import config


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
