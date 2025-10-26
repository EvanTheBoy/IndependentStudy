"""
Generic App Automation Framework
Reusable class for automating different apps
"""
import pyautogui
import time
from datetime import datetime
from pathlib import Path


class AppAutomator:
    """
    Generic automation class for iOS apps via iPhone Mirroring
    """

    def __init__(self, app_name, coordinates, timing_config=None):
        """
        Initialize automator

        Args:
            app_name: Name of the app being automated
            coordinates: Dictionary of coordinate positions
            timing_config: Optional timing configuration
        """
        self.app_name = app_name
        self.coordinates = coordinates
        self.timing = timing_config or {
            'pause': 0.5,
            'scroll_duration': 0.5,
            'wait_after_action': 1.5
        }

        # Setup PyAutoGUI
        pyautogui.PAUSE = self.timing['pause']
        pyautogui.FAILSAFE = True

        # Create output directories
        self.screenshot_dir = Path(f"screenshots_{app_name}")
        self.screenshot_dir.mkdir(exist_ok=True)

        self.action_log = []

    def log(self, message, level="INFO"):
        """Log timestamped message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {"INFO": "ℹ", "SUCCESS": "✓", "ERROR": "✗", "WARNING": "⚠"}
        symbol = symbols.get(level, "•")

        log_entry = f"[{timestamp}] {symbol} {message}"
        print(log_entry)
        self.action_log.append(log_entry)

    def click(self, coord_name, clicks=1):
        """
        Click at named coordinate

        Args:
            coord_name: Name of coordinate from self.coordinates
            clicks: Number of clicks (1=single, 2=double)
        """
        if coord_name not in self.coordinates:
            self.log(f"Coordinate '{coord_name}' not found", level="ERROR")
            return False

        x, y = self.coordinates[coord_name]

        if clicks == 1:
            pyautogui.click(x, y)
            self.log(f"Clicked: {coord_name} at ({x}, {y})")
        elif clicks == 2:
            pyautogui.doubleClick(x, y)
            self.log(f"Double-clicked: {coord_name} at ({x}, {y})")

        time.sleep(self.timing['wait_after_action'])
        return True

    def scroll(self, start_coord, end_coord, duration=None):
        """
        Scroll from start to end coordinate

        Args:
            start_coord: Starting coordinate name
            end_coord: Ending coordinate name
            duration: Override scroll duration
        """
        if start_coord not in self.coordinates or end_coord not in self.coordinates:
            self.log("Scroll coordinates not found", level="ERROR")
            return False

        start_pos = self.coordinates[start_coord]
        end_pos = self.coordinates[end_coord]
        scroll_duration = duration or self.timing['scroll_duration']

        pyautogui.moveTo(start_pos)
        drag_distance = end_pos[1] - start_pos[1]
        pyautogui.drag(0, drag_distance, duration=scroll_duration)

        self.log(f"Scrolled from {start_coord} to {end_coord}")
        time.sleep(self.timing['wait_after_action'])
        return True

    def screenshot(self, name):
        """Take and save screenshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.screenshot_dir / f"{name}_{timestamp}.png"

        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        self.log(f"Screenshot: {filename}")

        return filename

    def type_text(self, text):
        """Type text"""
        pyautogui.typewrite(text, interval=0.1)
        self.log(f"Typed: {text}")
        time.sleep(self.timing['wait_after_action'])

    def press_key(self, key_name):
        """
        Press a keyboard key

        Args:
            key_name: Name of key to press (e.g., 'escape', 'enter')
        """
        pyautogui.press(key_name)
        self.log(f"Pressed key: {key_name}")
        time.sleep(self.timing['wait_after_action'])
        return True

    def run_sequence(self, actions, num_runs=10):
        """
        Run a sequence of actions multiple times

        Args:
            actions: List of action dictionaries
            num_runs: Number of times to repeat sequence

        Example actions:
            [
                {'action': 'click', 'coord': 'feed_center'},
                {'action': 'scroll', 'start': 'scroll_start', 'end': 'scroll_end'},
                {'action': 'screenshot', 'name': 'after_scroll'}
            ]
        """
        self.log(f"Starting {self.app_name} automation: {num_runs} runs")

        successful = 0
        failed = 0

        for run in range(1, num_runs + 1):
            try:
                self.log("=" * 50)
                self.log(f"Run {run}/{num_runs}")

                for action in actions:
                    action_type = action.get('action')

                    if action_type == 'click':
                        self.click(action['coord'], clicks=action.get('clicks', 1))

                    elif action_type == 'scroll':
                        self.scroll(action['start'], action['end'])

                    elif action_type == 'screenshot':
                        self.screenshot(action.get('name', f'run_{run}'))

                    elif action_type == 'wait':
                        wait_time = action.get('seconds', 1)
                        time.sleep(wait_time)
                        self.log(f"Waited {wait_time}s")

                    elif action_type == 'type':
                        self.type_text(action['text'])

                    elif action_type == 'press_key':
                        self.press_key(action['key'])

                successful += 1
                self.log(f"Run {run} completed", level="SUCCESS")

            except Exception as e:
                failed += 1
                self.log(f"Run {run} failed: {e}", level="ERROR")

        # Summary
        self.log("=" * 50)
        self.log(f"Completed: {successful}/{num_runs} successful", level="SUCCESS")
        if failed > 0:
            self.log(f"Failed: {failed}/{num_runs}", level="WARNING")

        return successful, failed

    def save_log(self):
        """Save action log to file"""
        log_file = Path(f"{self.app_name}_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(log_file, 'w') as f:
            f.write('\n'.join(self.action_log))
        self.log(f"Log saved: {log_file}")


# Example usage
if __name__ == "__main__":
    # Instagram example
    instagram_coords = {
        'feed_center': (1179, 431),
        'scroll_start': (1150, 600),
        'scroll_end': (1150, 600),
    }

    automator = AppAutomator('Instagram', instagram_coords)

    # Define action sequence
    actions = [
        {'action': 'click', 'coord': 'feed_center'},  # Activate window
        {'action': 'scroll', 'start': 'scroll_start', 'end': 'scroll_end'},
        {'action': 'wait', 'seconds': 1},
        {'action': 'click', 'coord': 'feed_center', 'clicks': 2},  # Double-click to like
        {'action': 'screenshot', 'name': 'after_like'},
    ]

    # Run automation
    automator.run_sequence(actions, num_runs=10)
    automator.save_log()
