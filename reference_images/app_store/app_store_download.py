#!/usr/bin/env python3
"""
App Store Download Automation
Searches for apps in the App Store and downloads them one by one.
Skips the first result (usually an ad) and clicks Get/Reinstall on the second result.
"""

import pyautogui
import time
import sys
from datetime import datetime
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.utils import log_message, get_iphone_mirroring_region

# ── App list ──────────────────────────────────────────────────────────────────
APPS_TO_DOWNLOAD = [
    "dealmoon",
    "Zillow",
    "starbucks",
    "class pass",
    "solid care",
    "Chelsea Piers",
    "toss",
    "Procare",
    "Ground News",
    "Home AI - AI Interior Design",
    "Canvas Student",
    "Scriptable",
    "SmartThings",
    "MyNBA 2K Companion App",
    "Xfinity",
    "UK ETA",
    "Nextdoor: Neighborhood",
    "United Airlines",
    "Upside: Earn Cash Back on Fuel",
    "Crumbl",
    "Love Island USA",
    "Libby, the library app",
    "Clime: NOAA Weather Radar Live",
    "hoopla Digital",
    "MeloShort",
]

# ── Reference images (relative to reference_images/) ─────────────────────────
IMAGES = {
    'input_box': [
        'app_store/app_store_input_box_1.png',
        'app_store/app_store_input_box_1_dark.png',
        'app_store/app_store_input_box_2.png',
        'app_store/app_store_input_box_2_dark.png',
    ],
    'get_button': [
        'app_store/get.png',
        'app_store/get_dark.png',
        'app_store/reinstall.png',
        'app_store/reinstall_dark.png',
    ],
    'install_button': [
        'app_store/first_time_install.png',
        'app_store/first_time_install_dark.png',
    ],
    'clear_button': [
        'app_store/clear_app_name_1.png',
        'app_store/clear_app_name_1_dark.png',
        'app_store/clear_app_name_2.png',
        'app_store/clear_app_name_2_dark.png',
    ],
}

# ── Timing (seconds) ──────────────────────────────────────────────────────────
WAIT_AFTER_CLICK        = 0.5
WAIT_AFTER_INPUT_CLICK  = 1.5   # extra wait for keyboard + focus to appear after tapping search box
WAIT_AFTER_SEARCH       = 2.5   # wait for search results to load
WAIT_FOR_INSTALL_POPUP  = 1.5   # wait after tapping Get before checking for Install popup
WAIT_AFTER_DOWNLOAD     = 5.0   # wait after tapping Get/Install for download to start
WAIT_AFTER_CLEAR        = 1.0

BASE_DIR = Path(__file__).resolve().parents[1]   # …/reference_images/


# ── Helpers ───────────────────────────────────────────────────────────────────

def img(name: str) -> str:
    """Return absolute path string for a reference image."""
    return str(BASE_DIR / name)


def find_button(image_names, confidence=0.75, grayscale=False):
    """
    Try each image in image_names and return the first (x, y) match, or None.
    Searches strictly within the iPhone Mirroring window region.
    """
    region = get_iphone_mirroring_region()
    if region is None:
        log_message("iPhone Mirroring window not found — cannot search outside it.", level="ERROR")
        return None
    log_message(f"Searching within iPhone Mirroring window: {region}")
    for name in image_names:
        path = img(name)
        if not Path(path).exists():
            log_message(f"Image missing: {path}", level="WARNING")
            continue
        try:
            loc = pyautogui.locateOnScreen(path, confidence=confidence,
                                           grayscale=grayscale, region=region)
            if loc:
                center = pyautogui.center(loc)
                log_message(f"Found '{name}' at {center}", level="SUCCESS")
                return center
        except pyautogui.ImageNotFoundException:
            pass
        except Exception as e:
            log_message(f"Error with '{name}': {e}", level="WARNING")
    return None


def find_all_buttons(image_names, confidence=0.75, grayscale=False):
    """
    Return all matches for any of the given images, sorted top-to-bottom (by y).
    Searches strictly within the iPhone Mirroring window region.
    """
    region = get_iphone_mirroring_region()
    if region is None:
        log_message("iPhone Mirroring window not found — cannot search outside it.", level="ERROR")
        return []
    log_message(f"Searching within iPhone Mirroring window: {region}")
    results = []
    for name in image_names:
        path = img(name)
        if not Path(path).exists():
            continue
        try:
            matches = list(pyautogui.locateAllOnScreen(
                path, confidence=confidence, grayscale=grayscale, region=region))
            for m in matches:
                results.append(pyautogui.center(m))
        except pyautogui.ImageNotFoundException:
            pass
        except Exception as e:
            log_message(f"Error scanning '{name}': {e}", level="WARNING")

    # deduplicate (within 20 px)
    unique = []
    for pt in results:
        if not any(abs(pt.x - u.x) < 20 and abs(pt.y - u.y) < 20 for u in unique):
            unique.append(pt)

    unique.sort(key=lambda p: p.y)
    return unique


# ── Core steps ────────────────────────────────────────────────────────────────

def click_input_box():
    """Find and click the App Store search input box."""
    log_message("Looking for search input box…")
    loc = find_button(IMAGES['input_box'])
    if loc is None:
        log_message("Search input box not found!", level="ERROR")
        return False
    pyautogui.click(loc)
    time.sleep(WAIT_AFTER_INPUT_CLICK)  # wait for keyboard + focus before typing
    return True


def type_app_name(app_name: str):
    """Type the app name into the search box and press Enter."""
    log_message(f"Typing: '{app_name}'")
    pyautogui.write(app_name, interval=0.05)
    time.sleep(1.0)  # wait for autocorrect/autocomplete to settle before pressing return
    pyautogui.press('return')
    log_message("Pressed Enter — waiting for results…")
    time.sleep(WAIT_AFTER_SEARCH)


def click_get_button():
    """
    Find all Get / Reinstall buttons visible on screen, skip the first one
    (usually an ad), and click the second one.
    For first-time installs: after clicking Get, an Install popup appears — click it too.
    Returns True on success.
    """
    log_message("Scanning for Get / Reinstall buttons…")
    buttons = find_all_buttons(IMAGES['get_button'])

    if len(buttons) == 0:
        log_message("No Get/Reinstall button found on screen.", level="WARNING")
        return False

    if len(buttons) == 1:
        log_message("Only one button found — skipping (likely an ad).", level="WARNING")
        return False

    # buttons[0] = ad row, buttons[1] = first real result
    target = buttons[1]
    log_message(f"Clicking Get/Reinstall at {target} (second result)")
    pyautogui.click(target)

    # Wait for Install popup to appear before scanning — avoids false positives from search results
    log_message(f"Waiting {WAIT_FOR_INSTALL_POPUP}s for Install popup…")
    time.sleep(WAIT_FOR_INSTALL_POPUP)

    # For first-time installs, a second Install button may appear — click it if present
    install_loc = find_button(IMAGES['install_button'])
    if install_loc:
        log_message(f"Install popup detected — clicking Install at {install_loc}")
        pyautogui.click(install_loc)
    else:
        log_message("No Install popup — treating as Reinstall, download already started.")

    time.sleep(WAIT_AFTER_DOWNLOAD)
    return True


def clear_search_box():
    """
    Click the clear (×) button in the search bar to reset the input field.
    Returns True on success.
    """
    log_message("Looking for clear button…")
    loc = find_button(IMAGES['clear_button'])
    if loc is None:
        log_message("Clear button not found — trying select-all + delete.", level="WARNING")
        pyautogui.hotkey('command', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(WAIT_AFTER_CLEAR)
        return True

    pyautogui.click(loc)
    log_message("Search box cleared.", level="SUCCESS")
    time.sleep(WAIT_AFTER_CLEAR)
    return True


# ── Main loop ─────────────────────────────────────────────────────────────────

def download_app(app_name: str) -> bool:
    """
    Full download sequence for a single app:
      1. Find & click search box
      2. Type app name + Enter
      3. Click Get on the second result (skip ad)
      4. Clear the search box
    """
    log_message("─" * 50)
    log_message(f"Downloading: {app_name}")
    log_message("─" * 50)

    if not click_input_box():
        log_message("Skipping — will try to clear search box before next app.", level="WARNING")
        clear_search_box()
        return False

    type_app_name(app_name)

    success = click_get_button()
    if not success:
        log_message(f"Could not tap Get for '{app_name}'", level="WARNING")

    clear_search_box()
    return success


def main():
    pyautogui.FAILSAFE = True
    log_message("=" * 50)
    log_message("App Store Download Automation")
    log_message("=" * 50)
    log_message(f"Apps to download: {len(APPS_TO_DOWNLOAD)}")
    for i, name in enumerate(APPS_TO_DOWNLOAD, 1):
        log_message(f"  {i}. {name}")
    log_message("\nMove mouse to any screen corner to abort at any time.")
    log_message("\nStarting in 5 seconds…")
    for i in range(5, 0, -1):
        log_message(f"  {i}…")
        time.sleep(1)

    succeeded, failed = [], []
    timing_records = []   # list of dicts, one per app iteration

    try:
        for app in APPS_TO_DOWNLOAD:
            iter_start = datetime.now()
            log_message(f"[TIMER] '{app}' started at {iter_start.strftime('%Y-%m-%d %H:%M:%S.%f')}")

            ok = download_app(app)
            (succeeded if ok else failed).append(app)
            time.sleep(1.0)

            iter_end = datetime.now()
            duration = (iter_end - iter_start).total_seconds()
            log_message(f"[TIMER] '{app}' ended at  {iter_end.strftime('%Y-%m-%d %H:%M:%S.%f')} "
                        f"(took {duration:.2f}s)")

            timing_records.append({
                'app':      app,
                'start':    iter_start,
                'end':      iter_end,
                'duration': duration,
            })

    except pyautogui.FailSafeException:
        log_message("\nFailsafe triggered — automation stopped.", level="WARNING")
    except KeyboardInterrupt:
        log_message("\nCtrl-C — automation stopped.", level="WARNING")
    except Exception as e:
        log_message(f"\nUnexpected error: {e}", level="ERROR")
    finally:
        log_message("\n" + "=" * 50)
        log_message("SUMMARY")
        log_message("=" * 50)
        log_message(f"Succeeded ({len(succeeded)}): {', '.join(succeeded) or 'none'}", level="SUCCESS")
        log_message(f"Failed    ({len(failed)}): {', '.join(failed) or 'none'}",
                    level="ERROR" if failed else "INFO")

        if timing_records:
            log_message("\n" + "-" * 50)
            log_message("TIMING RECORDS")
            log_message("-" * 50)
            for idx, rec in enumerate(timing_records, 1):
                log_message(
                    f"  [{idx}] {rec['app']}"
                    f"\n        start    : {rec['start'].strftime('%Y-%m-%d %H:%M:%S.%f')}"
                    f"\n        end      : {rec['end'].strftime('%Y-%m-%d %H:%M:%S.%f')}"
                    f"\n        duration : {rec['duration']:.2f}s"
                )

        log_message("=" * 50)
        log_message("Done.", level="SUCCESS")


if __name__ == "__main__":
    main()
