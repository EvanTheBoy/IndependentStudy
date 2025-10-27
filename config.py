"""
Configuration file for Instagram automation
Modify these coordinates regularly
"""

# iPhone Mirroring window coordinates
# Find them using find_coordinates.py
COORDINATES = {
    # Center of the Instagram feed
    'feed_center': (1033, 530),

    # Scroll positions (start and end points)
    'scroll_start': (1035, 643),
    'scroll_end': (1029, 163),

    # Like button (or use double-click on feed_center)
    'like_button': (1173, 475),

    # Comment button
    'comment_button': (1173, 531),
    
    # Back button (to close post view)
    'back_button': (881, 167),
}

# Timing settings (in seconds)
TIMING = {
    'pause_between_actions': 0.5,  # Pause between each action
    'scroll_duration': 0.5,  # How long the scroll takes
    'wait_after_scroll': 2,  # Wait for content to load
    'wait_after_like': 1.5,  # Wait after liking
    'wait_after_open_post': 1.5,  # Wait for post view to load
    'wait_after_close_post': 2.0,  # Wait for feed to reappear
    'wait_between_runs': 1,  # Wait between automation runs
}

# Automation settings
AUTOMATION = {
    'number_of_runs': 5,  # How many times to repeat
    'enable_screenshots': True,  # Save screenshots for verification
    'enable_failsafe': True,  # Move mouse to corner to stop
    'scroll_amount': -500,  # Scroll amount per attempt (negative = down, adjust as needed)
    'scroll_attempts': 5,  # Number of scroll attempts
}
