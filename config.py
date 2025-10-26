"""
Configuration file for Instagram automation
Modify these coordinates based on your screen setup
"""

# iPhone Mirroring window coordinates
# You need to find these using find_coordinates.py
COORDINATES = {
    # Center of the Instagram feed
    'feed_center': (1044, 529),

    # Scroll positions (start and end points)
    'scroll_start': (1035, 755),
    'scroll_end': (1036, 342),

    # Like button (or use double-click on feed_center)
    'like_button': (1180, 489),

    # Comment button
    'comment_button': (1181, 545),
}

# Timing settings (in seconds)
TIMING = {
    'pause_between_actions': 0.5,  # Pause between each action
    'scroll_duration': 0.5,  # How long the scroll takes
    'wait_after_scroll': 2,  # Wait for content to load
    'wait_after_like': 1.5,  # Wait after liking
    'wait_after_open_post': 1.5,  # Wait for post view to load
    'wait_after_close_post': 1.0,  # Wait for feed to reappear
    'wait_between_runs': 1,  # Wait between automation runs
}

# Automation settings
AUTOMATION = {
    'number_of_runs': 10,  # How many times to repeat
    'enable_screenshots': True,  # Save screenshots for verification
    'enable_failsafe': True,  # Move mouse to corner to stop
}
