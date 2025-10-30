# Setup Guide: Image Recognition Automation

This guide helps you set up the image recognition version of the Instagram automation.

## What You Need

You need to capture 4 small reference images that the automation will use to find UI elements:

1. **back_button.png** - The back arrow (←) button when viewing a post
2. **post_thumbnail.png** - A post in the feed
3. **post_center.png** - Center of a post when opened
4. **feed_area.png** - General feed area

## How to Capture Reference Images

### Method 1: Using macOS Screenshot Tool (Recommended)

1. Open iPhone Mirroring and Instagram
2. Press `Cmd + Shift + 4` to activate screenshot selection
3. Click and drag to select the UI element
4. The screenshot will be saved to your Desktop
5. Move it to the `reference_images/` folder and rename it

### Method 2: Using Python Script

```bash
python3 -c "import pyautogui; pyautogui.screenshot('reference_images/back_button.png', region=pyautogui.locateOnScreen())"
```

## Step-by-Step Instructions

### 1. Capture Back Button
- Open a post in Instagram
- Use `Cmd + Shift + 4`
- Select just the back arrow button (←)
- Save as: `reference_images/back_button.png`

### 2. Capture Post Thumbnail
- Go back to the feed
- Use `Cmd + Shift + 4`
- Select the center area of any post
- Save as: `reference_images/post_thumbnail.png`

### 3. Capture Post Center
- Open a post
- Use `Cmd + Shift + 4`
- Select the middle of the post image
- Save as: `reference_images/post_center.png`

### 4. Capture Feed Area
- Go back to the feed
- Use `Cmd + Shift + 4`
- Select a neutral area in the feed (not on a post)
- Save as: `reference_images/feed_area.png`

## Tips for Good Reference Images

- **Small is better** - Capture just the essential part (20-50 pixels)
- **High contrast** - Choose distinctive elements
- **Avoid text** - Text can change, icons are more reliable
- **Test different sizes** - If recognition fails, try larger/smaller captures

## Running the Automation

Once you have all 4 reference images:

```bash
python3 instagram_automation_image_recognition.py
```

## Troubleshooting

**"Could not find element"**
- Try adjusting the confidence level (default 0.8)
- Recapture the reference image with more/less surrounding area
- Make sure the Instagram window is in the same position

**"Reference image not found"**
- Check that images are in `reference_images/` folder
- Check file names match exactly (case-sensitive)

## Advantages of Image Recognition

✅ No need to manually find coordinates
✅ Works even if window moves
✅ More robust to UI changes
✅ Easier to maintain

## Configuration

You can adjust confidence levels in the code:
- `confidence=0.8` - Default (80% match required)
- `confidence=0.7` - More lenient (finds more matches)
- `confidence=0.9` - Stricter (fewer false positives)
