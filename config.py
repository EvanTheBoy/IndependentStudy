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

# Pixel matching settings
PIXEL_MATCHING = {
    'confidence': 0.7,  # Matching confidence (0.0 to 1.0)
    'search_region': None,  # Search entire screen - simpler and more reliable
    'timeout': 3.0,  # Max seconds to search for element
    'grayscale': False,  # Use color matching for better accuracy
    'like_button_images': ['like_button.png', 'like_button_dark.png'],  # Try light theme first, then dark
    'comment_button_images': ['comment_button.png', 'comment_button_dark.png'],  # Try light theme first, then dark
}

# Comment settings for Script B
COMMENTS = {
    'comment_texts': [
        'Great post! 🔥',
        'Love this! ❤️',
        'Amazing! 👏',
        'Nice! 😊',
    ],
    'use_random': True,  # Randomly select from comment_texts
    'default_comment': 'Nice! 😊',
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
    'wait_after_comment_click': 1.0,  # Wait for comment dialog to open
    'wait_after_comment_submit': 1.5,  # Wait for comment to post
    'wait_after_dialog_close': 1.0,  # Wait for dialog to close
}

# Automation settings
AUTOMATION = {
    'number_of_runs': 3,  # How many times to repeat
    'enable_screenshots': True,  # Save screenshots for verification
    'enable_failsafe': True,  # Move mouse to corner to stop
    'scroll_amount': -500,  # Scroll amount per attempt (negative = down, adjust as needed)
    'scroll_attempts': 5,  # Number of scroll attempts
    'main_feed_scroll_amount': -600,  # Scroll amount for main feed (negative = down)
    'main_feed_scroll_attempts': 3,  # Number of scroll attempts for main feed
}
