# Setup Guide: Static UI Element Recognition

This version uses **static UI elements** (buttons, icons, logos) instead of post content for more reliable image recognition.

## Required Reference Images

Capture these **static UI elements** that don't change:

### 1. back_arrow.png (MOST IMPORTANT)
- **What**: The ← back arrow button when viewing a post
- **Size**: 20-40 pixels
- **Why**: This never changes, always looks the same
- **How**: Open a post, use `Cmd + Shift + 4`, capture just the ← arrow

### 2. instagram_logo.png (Optional but helpful)
- **What**: The Instagram logo/text at the top
- **Size**: 80-120 pixels wide
- **Why**: Helps locate the window
- **How**: Capture the "Instagram" text or logo at the top

### 3. like_button_icon.png (Optional)
- **What**: The heart icon (outline, not filled)
- **Size**: 20-30 pixels
- **Why**: Static button that doesn't change
- **How**: Open a post, capture just the heart icon below the post

### 4. feed_reference.png (Optional)
- **What**: Any static part of the feed (like bottom navigation icons)
- **Size**: 40-60 pixels
- **Why**: Reference point for scrolling
- **How**: Capture one of the bottom navigation icons (home, search, etc.)

## What NOT to Capture

❌ **Post content** - Videos and images change
❌ **Usernames** - Different for each post
❌ **Like counts** - Numbers change
❌ **Comments** - Text varies

## Minimum Setup

You only need **ONE** reference image to start:
- `back_arrow.png` - The ← button

The script will use fallbacks for everything else.

## How to Capture

1. Open iPhone Mirroring and Instagram
2. Press `Cmd + Shift + 4`
3. Click and drag to select the UI element
4. Save to `reference_images/` folder with the correct name

## Tips for Best Results

✅ **Capture small** - Just the icon/button itself (20-50px)
✅ **High contrast** - Icons with clear edges work best
✅ **Consistent lighting** - Capture in the same lighting you'll use
✅ **Clean capture** - No overlapping elements

## Running the Script

```bash
python instagram_automation_static_ui.py
```

## Advantages

- ✅ Static UI elements never change (unlike video content)
- ✅ More reliable matching
- ✅ Works even if posts are different
- ✅ Back arrow is always in the same visual style

## Fallback Behavior

If an element isn't found, the script falls back to:
- Screen center for clicking
- Double-click for liking
- Coordinate-based positioning

This makes it robust even with minimal reference images!
