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

> **Important (Mac Users):** If you are using a Mac with a Retina display, you must connect an external monitor and set it as the **main display**. PyAutoGUI's pixel matching does not work correctly with Retina/HiDPI displays, which will cause all scripts to fail. To set the external monitor as main: System Settings > Displays > Arrange > drag the menu bar to the external monitor.

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install pyautogui pygetwindow
   ```
3. Connect an external (non-Retina) monitor and set it as the main display
4. Open iPhone Mirroring on your Mac (on the external monitor)
5. Navigate to the desired social media app on your mirrored iPhone
6. Run the desired script from the terminal

---

## Quick Start

Follow these steps to run any script:

1. **Connect external monitor** and set it as the main display (required for Retina Macs)

2. **Open iPhone Mirroring** on your Mac
   - Make sure the window is on the main display (external monitor)
   - Keep the window visible and unobstructed

3. **Navigate to the app** on your mirrored iPhone
   - For TikTok: go to the **Explore** tab
   - For others: go to the main feed

4. **Position cursor** (for some scripts)
   - YouTube Comment: place cursor over a video thumbnail before running

5. **Run the script** from the project root directory:
   ```bash
   python reference_images/<platform>/<script>.py
   ```
   Examples:
   ```bash
   python reference_images/youtube/youtube_like.py
   python reference_images/instagram/instagram_comment.py
   python reference_images/X/x_comment.py
   ```

6. **During execution:**
   - **Don't leave the script unattended** - these are not "set and forget" automations
   - Ads may pop up on any platform and require manual dismissal
   - Don't move the mouse (the script controls it)
   - Don't switch windows or cover iPhone Mirroring

7. **To stop the script:**
   - Move mouse to any corner of the screen (PyAutoGUI failsafe), or
   - Press `Ctrl+C` in the terminal

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

**Detailed Workflow:**
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Click at window center to enter video                    │
│    ├─ If like button found → video entered successfully     │
│    └─ If not found → scroll feed and retry (max 3 retries)  │
├─────────────────────────────────────────────────────────────┤
│ 2. Find like button using pixel matching                    │
│    └─ Tries both light and dark theme reference images      │
├─────────────────────────────────────────────────────────────┤
│ 3. Click like button                                        │
├─────────────────────────────────────────────────────────────┤
│ 4. Scroll down to next video (75% down from top)            │
├─────────────────────────────────────────────────────────────┤
│ 5. Repeat from step 1                                       │
└─────────────────────────────────────────────────────────────┘
```

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

> **Pre-requisite:** Position your mouse cursor over a video thumbnail before running the script. The script will click at the current cursor position to enter the first video.

**Detailed Workflow:**
```
┌─────────────────────────────────────────────────────────────┐
│ INITIAL: Click at current cursor position to enter video   │
│    ├─ If comment button found → video entered successfully │
│    └─ If not found → scroll slightly and retry (max 3x)    │
├─────────────────────────────────────────────────────────────┤
│ 1. Find and click comment button                           │
├─────────────────────────────────────────────────────────────┤
│ 2. Find input field (tries 8 placeholder variants)         │
│    └─ 4 dark theme + 4 light theme variants                │
├─────────────────────────────────────────────────────────────┤
│ 3. Type random comment                                      │
├─────────────────────────────────────────────────────────────┤
│ 4. Find and click submit button                            │
│    ├─ Picks rightmost match (submit is on right side)      │
│    └─ Fallback: press Enter key                            │
├─────────────────────────────────────────────────────────────┤
│ 5. Close comment section                                    │
│    ├─ Try: click X/back button                             │
│    └─ Fallback: swipe down gesture                         │
├─────────────────────────────────────────────────────────────┤
│ 6. Scroll feed to reveal next video                        │
├─────────────────────────────────────────────────────────────┤
│ 7. Click to enter next video (with retry logic)            │
├─────────────────────────────────────────────────────────────┤
│ 8. Repeat from step 1                                       │
└─────────────────────────────────────────────────────────────┘
```

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

**Detailed Workflow:**
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Scroll feed to reveal new posts                         │
├─────────────────────────────────────────────────────────────┤
│ 2. Find all like buttons on screen                         │
│    ├─ Search using both light and dark theme images        │
│    └─ Remove duplicates (within 20px threshold)            │
├─────────────────────────────────────────────────────────────┤
│ 3. Randomly select and click one like button               │
├─────────────────────────────────────────────────────────────┤
│ 4. Repeat from step 1                                       │
└─────────────────────────────────────────────────────────────┘
```

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

**Detailed Workflow:**
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Scroll feed to reveal posts                             │
├─────────────────────────────────────────────────────────────┤
│ 2. Find comment button                                      │
│    ├─ If found → click it                                  │
│    └─ If not found → scroll down slightly, retry (max 5x)  │
├─────────────────────────────────────────────────────────────┤
│ 3. Find input field (tries 6 placeholder variants)         │
│    └─ 3 dark theme + 3 light theme variants                │
├─────────────────────────────────────────────────────────────┤
│ 4. Type random comment                                      │
├─────────────────────────────────────────────────────────────┤
│ 5. Find and click submit button                            │
│    └─ Fallback: press Enter key                            │
├─────────────────────────────────────────────────────────────┤
│ 6. Close comment section                                    │
│    ├─ Find drag bar in top 200px of window                 │
│    ├─ Drag down 50% of window height (slow 1.5s drag)      │
│    ├─ Fallback: swipe down from near top                   │
│    └─ Click outside comment area to fully dismiss          │
├─────────────────────────────────────────────────────────────┤
│ 7. Repeat from step 1                                       │
└─────────────────────────────────────────────────────────────┘
```

---

### TikTok

> **Important:** Before running TikTok scripts, navigate to the **"Explore"** tab in the top navigation bar of the TikTok app.

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

**Detailed Workflow:**
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Scroll feed (larger scroll for full-screen videos)      │
├─────────────────────────────────────────────────────────────┤
│ 2. Find all like buttons using pixel matching              │
├─────────────────────────────────────────────────────────────┤
│ 3. Randomly select and click one like button               │
├─────────────────────────────────────────────────────────────┤
│ 4. Repeat from step 1                                       │
└─────────────────────────────────────────────────────────────┘
```

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

**Relative Button Positions (for videos):**
- Back button: 8% from left, 12.5% from top
- Comment button: 92% from left, 62% from top

**Detailed Workflow:**
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Click random content in Explore dual-column layout      │
│    ├─ Randomly choose left (25% width) or right (75%)      │
│    └─ Click at random Y position (25%-65% height)          │
├─────────────────────────────────────────────────────────────┤
│ 2. Detect content type                                      │
│    ├─ Try to find photo post input field (pixel matching)  │
│    ├─ If found → this is a PHOTO POST                      │
│    └─ If not found → assume this is a VIDEO                │
├─────────────────────────────────────────────────────────────┤
│ 3. Find comment input field                                 │
│    ├─ For VIDEO: use video_direct_comment_input_field.png  │
│    └─ For PHOTO: use comment_input_field.png               │
├─────────────────────────────────────────────────────────────┤
│ 4. Click input field and type comment                      │
├─────────────────────────────────────────────────────────────┤
│ 5. Submit with Enter key (TikTok uses Enter, not button)   │
├─────────────────────────────────────────────────────────────┤
│ 6. Go back to Explore                                       │
│    ├─ For VIDEO: use relative coords (8% left, 12.5% top)  │
│    ├─ For PHOTO: use pixel matching for back button        │
│    └─ Fallback: swipe right from left edge (iOS gesture)   │
├─────────────────────────────────────────────────────────────┤
│ 7. Scroll Explore feed                                      │
├─────────────────────────────────────────────────────────────┤
│ 8. Repeat from step 1                                       │
├─────────────────────────────────────────────────────────────┤
│ FINAL: Browse comments on one more post (scroll 3 seconds)  │
└─────────────────────────────────────────────────────────────┘
```

---

### X (Twitter)

#### Like Script (`reference_images/X/x_like.py`)

Automatically likes posts on X (Twitter).

**Usage:**
```bash
python reference_images/X/x_like.py
```

**Features:**
- Supports both light and dark theme detection
- Enter post -> Like -> Back -> Scroll pattern
- Click position calculated as 15% from left, 55% from top
- Configurable scroll direction (up/down)
- Verification that back button disappears after exit

**Detailed Workflow:**
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Click to enter post (15% from left, 55% from top)       │
├─────────────────────────────────────────────────────────────┤
│ 2. Find like button                                         │
│    ├─ If found → click it                                  │
│    └─ If not found → scroll down, retry (max 3x)           │
├─────────────────────────────────────────────────────────────┤
│ 3. Find back button                                         │
│    ├─ If found → click it                                  │
│    └─ If not found → scroll up, retry (max 3x)             │
├─────────────────────────────────────────────────────────────┤
│ 4. Verify exit (check back button disappeared)              │
│    └─ If still visible → click again (max 3 attempts)      │
├─────────────────────────────────────────────────────────────┤
│ 5. Scroll feed to new posts (3x 600px scrolls)             │
├─────────────────────────────────────────────────────────────┤
│ 6. Repeat from step 1                                       │
└─────────────────────────────────────────────────────────────┘
```

---

#### Comment Script (`reference_images/X/x_comment.py`)

Automatically posts replies/comments on X (Twitter).

**Usage:**
```bash
python reference_images/X/x_comment.py
```

**Features:**
- Supports both light and dark theme detection
- Complete workflow with popup wait handling
- Waits 6 seconds for "reply sent" popup to disappear
- Uses character-by-character typing for reliability
- Color matching for submit button (distinguishes blue Reply from black Subscribe)

**Detailed Workflow:**
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Click to enter post (15% from left, 55% from top)       │
├─────────────────────────────────────────────────────────────┤
│ 2. Find input field                                         │
│    ├─ If found → click it                                  │
│    └─ If not found → scroll down, retry (max 2x)           │
├─────────────────────────────────────────────────────────────┤
│ 3. Type comment character by character (0.05s interval)    │
├─────────────────────────────────────────────────────────────┤
│ 4. Find and click submit button                            │
│    └─ Uses COLOR matching (not grayscale) to distinguish   │
│       blue "Reply" button from black "Subscribe" button    │
├─────────────────────────────────────────────────────────────┤
│ 5. Wait 6 seconds for "reply sent" popup to disappear      │
├─────────────────────────────────────────────────────────────┤
│ 6. Find back button                                         │
│    ├─ If found → click it                                  │
│    └─ If not found → scroll up aggressively (3x 500px)     │
│       then retry finding back button                        │
├─────────────────────────────────────────────────────────────┤
│ 7. Scroll feed to new posts (3x 600px scrolls)             │
├─────────────────────────────────────────────────────────────┤
│ 8. Repeat from step 1                                       │
└─────────────────────────────────────────────────────────────┘
```

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

**Detailed Workflow:**
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Find all upvote buttons on screen                       │
│    ├─ Search using light and dark theme images             │
│    └─ Remove duplicates (within 20px threshold)            │
├─────────────────────────────────────────────────────────────┤
│ 2. Randomly select and click one upvote button             │
├─────────────────────────────────────────────────────────────┤
│ 3. Scroll feed to reveal new posts                         │
├─────────────────────────────────────────────────────────────┤
│ 4. Repeat from step 1                                       │
└─────────────────────────────────────────────────────────────┘
```

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

**Detailed Workflow:**
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Find all comment buttons on screen                      │
│    └─ Randomly select one and click                        │
├─────────────────────────────────────────────────────────────┤
│ 2. Find input field                                         │
│    ├─ If found → click it                                  │
│    └─ Fallback: tap at center of screen + 200px down       │
├─────────────────────────────────────────────────────────────┤
│ 3. Type random comment                                      │
├─────────────────────────────────────────────────────────────┤
│ 4. Find and click Reply button                             │
│    └─ Fallback: press Enter key                            │
├─────────────────────────────────────────────────────────────┤
│ 5. Close comment section                                    │
│    ├─ Find and click back/X button                         │
│    └─ Fallback: swipe right gesture from left edge         │
├─────────────────────────────────────────────────────────────┤
│ 6. Scroll feed to reveal new posts                         │
├─────────────────────────────────────────────────────────────┤
│ 7. Repeat from step 1                                       │
└─────────────────────────────────────────────────────────────┘
```

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

## Core Implementation

This section shows the key code patterns used across all scripts.

### 1. Window Detection

Get the iPhone Mirroring window bounds to limit search region:

```python
import pygetwindow as gw

def get_iphone_mirroring_region():
    titles = gw.getAllTitles()
    for title in titles:
        if 'iPhone Mirroring' in title:
            left, top, width, height = gw.getWindowGeometry(title)
            return (int(left), int(top), int(width), int(height))
    return None
```

### 2. Pixel Matching (Find Single Element)

Find a UI element using reference images:

```python
import pyautogui
from pathlib import Path

def find_button(image_list, confidence=0.7, region=None):
    for img_name in image_list:
        img_path = Path('reference_images') / img_name
        try:
            location = pyautogui.locateOnScreen(
                str(img_path),
                confidence=confidence,
                grayscale=True,
                region=region  # Limit search to iPhone Mirroring window
            )
            if location:
                return pyautogui.center(location)
        except pyautogui.ImageNotFoundException:
            pass
    return None
```

### 3. Pixel Matching (Find All Elements)

Find all matching elements and remove duplicates:

```python
def find_all_buttons(image_list, confidence=0.7, region=None):
    all_buttons = []
    for img_name in image_list:
        img_path = Path('reference_images') / img_name
        try:
            matches = list(pyautogui.locateAllOnScreen(
                str(img_path),
                confidence=confidence,
                region=region
            ))
            for match in matches:
                all_buttons.append(pyautogui.center(match))
        except pyautogui.ImageNotFoundException:
            pass

    # Remove duplicates (within 20px threshold)
    unique = []
    for btn in all_buttons:
        is_dup = any(abs(btn[0]-u[0]) < 20 and abs(btn[1]-u[1]) < 20 for u in unique)
        if not is_dup:
            unique.append(btn)
    return unique
```

### 4. Click, Type, and Scroll

Basic interaction functions:

```python
# Click at position
pyautogui.click(x, y)

# Type text
pyautogui.write('Hello!', interval=0.03)  # With delay between chars

# Scroll (negative = down, positive = up)
pyautogui.scroll(-500)

# Press key
pyautogui.press('enter')
```

### 5. Drag/Swipe Gestures

For iOS-style gestures (e.g., closing comment sections):

```python
# Drag gesture (e.g., drag down to close)
pyautogui.moveTo(start_x, start_y)
pyautogui.drag(0, 300, duration=0.5)  # Drag down 300px

# Swipe gesture (e.g., swipe right to go back)
pyautogui.moveTo(start_x, y)
pyautogui.drag(200, 0, duration=0.3)  # Swipe right 200px
```

### 6. Relative Coordinates

For dynamic backgrounds where pixel matching fails (e.g., TikTok videos):

```python
def get_button_position(region, x_ratio, y_ratio):
    left, top, width, height = region
    x = int(left + width * x_ratio)
    y = int(top + height * y_ratio)
    return (x, y)

# Example: TikTok comment button at 92% from left, 62% from top
region = get_iphone_mirroring_region()
comment_btn = get_button_position(region, 0.92, 0.62)
pyautogui.click(comment_btn)
```

---

## Safety Features

- **PyAutoGUI Failsafe**: Move your mouse to any corner of the screen to immediately stop script execution
- **Retry Logic**: Failed actions are retried a limited number of times before moving on
- **Logging**: All actions are logged with timestamps for debugging
- **Screenshot Capture**: Optional screenshot capture for troubleshooting

---

## Maintenance

### Comment Input Field Reference Images

The comment input field detection relies on reference images that capture placeholder text (e.g., "Add a comment...", "Write a comment..."). These placeholders vary across platforms and may change when apps are updated.

**Why updates are needed:**
- Each platform uses different placeholder text variants
- App updates may introduce new placeholder text or change existing ones
- The scripts may fail to detect the input field if the reference images no longer match

**Affected files by platform:**

| Platform | Reference Images |
|----------|-----------------|
| YouTube | `youtube_comment_input_field_1.png` through `_4.png` (light/dark variants) |
| Instagram | `instagram_comment_input_field_1.png` through `_3.png` (light/dark variants) |
| TikTok | `tiktok_comment_input_field.png`, `tiktok_video_direct_comment_input_field.png` |
| X (Twitter) | `x_comment_input_field.png`, `x_comment_input_field_dark.png` |
| Reddit | `reddit_comment_input_field.png` |

**How to update:**
1. Open the app in iPhone Mirroring
2. Navigate to a comment section
3. Take a screenshot of the input field placeholder
4. Crop the image to include only the placeholder text area
5. Save it to the appropriate `reference_images/<platform>/` folder
6. Add the new variant to the script's image search list if needed

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| All scripts suddenly stop working | Restart your Mac. This can resolve issues with PyAutoGUI's screen capture or window detection that accumulate over time. |
| Script can't find buttons | Update reference images for the affected platform (see Maintenance section above) |
| Some scripts stopped working after app update | Recapture the reference images for the affected buttons/input fields. App UI changes can break pixel matching. |
| Scripts run but miss clicks | Adjust timing values in `config.py` (increase delays) |
| "iPhone Mirroring window not found" | Make sure iPhone Mirroring is open, visible, and **on the main display** (the external monitor if you followed the Setup instructions) |
| Scripts work erratically on Retina display | Connect an external monitor and set it as main display (see Setup section) |

---

## Notes

- **Don't leave scripts unattended** - ads may pop up on any platform and require manual dismissal; stay at your computer while running
- Ensure your iPhone is properly mirrored to your Mac before running scripts
- Scripts are designed for educational and research purposes
- Reference images may need to be updated if app UIs change
- Adjust timing values in `config.py` if scripts run too fast/slow for your system
