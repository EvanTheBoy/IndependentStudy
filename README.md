# Social Media Automation Scripts

This project contains automation scripts for interacting with various social media platforms using Python and PyAutoGUI. The scripts automate actions like liking posts and leaving comments across YouTube, Instagram, TikTok, X (Twitter), and Reddit.

## Table of Contents

- [Requirements](#requirements)
- [Setup](#setup)
- [Project Structure](#project-structure)
- [Scripts Overview](#scripts-overview)
  - [YouTube](#youtube)
  - [Instagram](#instagram)
  - [TikTok](#tiktok)
  - [X (Twitter)](#x-twitter)
  - [Reddit](#reddit)
- [Configuration](#configuration)
- [Core Utilities](#core-utilities)
- [How It Works](#how-it-works)
- [Safety Features](#safety-features)

---

## Requirements

- Python 3.x
- macOS with iPhone Mirroring enabled
- Required Python packages:
  ```
  pip install pyautogui pygetwindow
  ```

---

## Setup

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install pyautogui pygetwindow
   ```
3. Open iPhone Mirroring on your Mac
4. Navigate to the desired social media app on your mirrored iPhone
5. Run the desired script from the terminal

---

## Project Structure

```
IndependentStudy/
├── core/
│   ├── config.py          # Central configuration settings
│   └── utils.py           # Shared utility functions
├── reference_images/
│   ├── youtube/
│   │   ├── youtube_like.py
│   │   ├── youtube_comment.py
│   │   └── *.png          # Reference images for button detection
│   ├── instagram/
│   │   ├── instagram_like.py
│   │   ├── instagram_comment.py
│   │   └── *.png
│   ├── tiktok/
│   │   ├── tiktok_like.py
│   │   ├── tiktok_comment.py
│   │   └── *.png
│   ├── X/
│   │   ├── x_like.py
│   │   ├── x_comment.py
│   │   └── *.png
│   └── reddit/
│       ├── reddit_like.py
│       ├── reddit_comment.py
│       └── *.png
```

---

## Scripts Overview

### YouTube

#### Like Script (`reference_images/youtube/youtube_like.py`)

Automatically likes videos on YouTube.

**Usage:**
```bash
python reference_images/youtube/youtube_like.py
```

**Features:**
- Supports both light and dark theme detection
- Automatically detects the iPhone Mirroring window region
- Removes duplicate like button detections
- Implements swipe gesture to return from video to feed
- Retry logic for failed video entries (max 3 retries)

**Workflow:**
1. Finds like button on screen
2. Clicks the like button
3. Scrolls to next video
4. Repeats for configured number of runs

---

#### Comment Script (`reference_images/youtube/youtube_comment.py`)

Automatically leaves comments on YouTube videos.

**Usage:**
```bash
python reference_images/youtube/youtube_comment.py
```

**Features:**
- Handles both dark and light theme variants
- Supports multiple input field placeholder variants (8 total)
- Dynamically finds and clicks the submit button
- Includes comment section close logic with swipe fallback

**Workflow:**
1. Enters a video
2. Opens comment section
3. Finds and clicks input field
4. Types a random comment from the configured list
5. Submits the comment
6. Closes comment section and returns to feed

---

### Instagram

#### Like Script (`reference_images/instagram/instagram_like.py`)

Automatically likes posts in the Instagram feed.

**Usage:**
```bash
python reference_images/instagram/instagram_like.py
```

**Features:**
- Searches within iPhone Mirroring window bounds
- Handles light and dark theme variants
- Duplicate detection with 20-pixel threshold
- Scroll-based feed navigation

**Workflow:**
1. Detects like button (heart icon) on screen
2. Clicks to like the post
3. Scrolls down to next post
4. Repeats for configured number of runs

---

#### Comment Script (`reference_images/instagram/instagram_comment.py`)

Automatically posts comments on Instagram posts.

**Usage:**
```bash
python reference_images/instagram/instagram_comment.py
```

**Features:**
- Smart comment button detection with auto-scroll (up to 5 attempts)
- Drag-to-close functionality for comment section
- Multiple input field placeholder variants (6 total)
- Fallback swipe gesture if drag fails

**Workflow:**
1. Finds and clicks comment button (scrolls if needed)
2. Opens comment section
3. Finds input field and types comment
4. Submits comment
5. Closes comment section using drag gesture

---

### TikTok

#### Like Script (`reference_images/tiktok/tiktok_like.py`)

Automatically likes videos on TikTok.

**Usage:**
```bash
python reference_images/tiktok/tiktok_like.py
```

**Features:**
- Simple and efficient implementation
- Uses single reference image for detection
- Larger scroll amounts for TikTok's full-screen video format

**Workflow:**
1. Detects like button (heart icon)
2. Clicks to like the video
3. Scrolls to next video
4. Repeats for configured number of runs

---

#### Comment Script (`reference_images/tiktok/tiktok_comment.py`)

Automatically posts comments on TikTok videos and photo posts.

**Usage:**
```bash
python reference_images/tiktok/tiktok_comment.py
```

**Features:**
- Handles dual-column Explore layout (left/right columns)
- Distinguishes between video pages and photo posts automatically
- Uses relative coordinates for video pages (handles dynamic backgrounds)
- Uses pixel matching for photo posts (static backgrounds)
- Includes comment browsing function at end of run

**Relative Button Positions:**
- Back button: 8% from left, 12.5% from top
- Comment button: 92% from left, 62% from top

**Workflow:**
1. Enters a video/post from Explore page
2. Opens comment section using relative coordinates or pixel matching
3. Types and submits comment
4. Returns to Explore page
5. Scrolls to next content

---

### X (Twitter)

#### Like Script (`reference_images/X/x_like.py`)

Automatically likes posts on X (Twitter).

**Usage:**
```bash
python reference_images/X/x_like.py
```

**Features:**
- Enter post -> Like -> Back -> Scroll pattern
- Click position calculated as 15% from left, 55% from top
- Configurable scroll direction (up/down)
- Verification that back button disappears after exit

**Workflow:**
1. Enters a post by clicking
2. Finds and clicks like button
3. Returns to feed
4. Scrolls to next post
5. Repeats for configured number of runs

---

#### Comment Script (`reference_images/X/x_comment.py`)

Automatically posts replies/comments on X (Twitter).

**Usage:**
```bash
python reference_images/X/x_comment.py
```

**Features:**
- Complete workflow with popup wait handling
- Waits 6 seconds for "reply sent" popup to disappear
- Uses character-by-character typing for reliability
- Color matching for submit button (distinguishes blue Reply from black Subscribe)

**Workflow:**
1. Enters a post
2. Finds and clicks input field
3. Types comment character by character
4. Clicks submit button
5. Waits for reply confirmation popup
6. Returns to feed

---

### Reddit

#### Upvote Script (`reference_images/reddit/reddit_like.py`)

Automatically upvotes posts on Reddit.

**Usage:**
```bash
python reference_images/reddit/reddit_like.py
```

**Features:**
- Light and dark theme variants
- Random selection from found upvote buttons
- Feed-based navigation

**Workflow:**
1. Detects upvote button (arrow icon)
2. Clicks to upvote
3. Scrolls to next post
4. Repeats for configured number of runs

---

#### Comment Script (`reference_images/reddit/reddit_comment.py`)

Automatically posts comments on Reddit posts.

**Usage:**
```bash
python reference_images/reddit/reddit_comment.py
```

**Features:**
- Multi-variant button matching
- Input field detection with fallback tap in center of screen
- Reply button detection with Enter key fallback
- Swipe gesture fallback for closing

**Workflow:**
1. Enters a post
2. Finds comment button and opens comment section
3. Locates input field and types comment
4. Submits using Reply button or Enter key
5. Returns to feed

---

## Configuration

All scripts share a central configuration in `core/config.py`:

### Key Configuration Options

```python
# Pixel Matching Settings
PIXEL_MATCHING = {
    'confidence': 0.7,      # Match confidence threshold (0.0 - 1.0)
    'grayscale': True,      # Use grayscale matching for better performance
    'timeout': 10           # Timeout for locating elements
}

# Timing Settings
TIMING = {
    'wait_after_like': 1.0,     # Delay after liking
    'wait_after_scroll': 1.5,   # Delay after scrolling
    'wait_after_click': 0.5     # Delay after clicking
}

# Automation Settings
AUTOMATION = {
    'number_of_runs': 10,           # Number of iterations
    'main_feed_scroll_amount': -600 # Pixels to scroll (negative = down)
}

# Default Comments (per platform)
COMMENTS = {
    'youtube': ['Great video!', 'Thanks for sharing!', ...],
    'instagram': ['Great post!', 'Love this!', ...],
    'tiktok': ['Great content!', 'Love this!', ...],
    'twitter': ['Great post!', 'Amazing!', ...],
    'reddit': ['Great post!', 'Thanks for sharing!', ...]
}
```

---

## Core Utilities

The `core/utils.py` module provides shared utility functions:

| Function | Description |
|----------|-------------|
| `get_iphone_mirroring_region()` | Detects and returns the iPhone Mirroring window bounds |
| `get_iphone_mirroring_center()` | Calculates the center point of the iPhone Mirroring window |
| `log_message(message, level)` | Prints timestamped log messages with level indicators |
| `take_screenshot(name)` | Captures and saves screenshots for debugging |
| `setup_directories()` | Creates required directories for screenshots/logs |

---

## How It Works

1. **Window Detection**: Scripts first detect the iPhone Mirroring window on your Mac to limit the search region for UI elements.

2. **Pixel Matching**: Uses PyAutoGUI's `locateOnScreen()` function to find UI elements by comparing against reference images stored in each platform's folder.

3. **Theme Handling**: Most scripts include reference images for both light and dark themes to work regardless of the user's theme preference.

4. **Human-like Interaction**: Scripts include random delays and natural scrolling patterns to simulate human behavior.

5. **Fallback Mechanisms**: When primary detection methods fail, scripts employ fallback strategies like swipe gestures or keyboard shortcuts.

---

## Safety Features

- **PyAutoGUI Failsafe**: Move your mouse to any corner of the screen to immediately stop script execution
- **Retry Logic**: Failed actions are retried a limited number of times before moving on
- **Logging**: All actions are logged with timestamps for debugging
- **Screenshot Capture**: Optional screenshot capture for troubleshooting

---

## Notes

- Ensure your iPhone is properly mirrored to your Mac before running scripts
- Scripts are designed for educational and research purposes
- Reference images may need to be updated if app UIs change
- Adjust timing values in `config.py` if scripts run too fast/slow for your system
