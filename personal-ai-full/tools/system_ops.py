import os
import subprocess
import shutil
import time
from pathlib import Path
from datetime import datetime

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import pyperclip
except ImportError:
    pyperclip = None


# ============================================================
# HELPERS
# ============================================================

def _require_pyautogui():
    if pyautogui is None:
        return (
            "ERROR: pyautogui is not installed. "
            "Install it with: pip install pyautogui"
        )
    return None


# ============================================================
# OPEN APPLICATION
# ============================================================

def open_app(command):
    """
    Open a Windows application.

    Supports:
    - executable names available in PATH
    - full .exe paths
    - Chrome
    - VS Code
    - Windows shell commands
    """

    if not command:
        return "ERROR: No application command was provided."

    command = str(command).strip().strip('"').strip("'")

    if not command:
        return "ERROR: No application command was provided."

    # --------------------------------------------------------
    # 1. Direct executable available in PATH
    # --------------------------------------------------------

    executable = command.split()[0].strip('"').strip("'")

    found = shutil.which(executable)

    if found:
        try:
            subprocess.Popen(
                command,
                shell=True
            )

            return f"SUCCESS: Application opened: {command}"

        except Exception as e:
            return f"ERROR: Failed to open {command}: {e}"

    # --------------------------------------------------------
    # 2. Direct path to executable
    # --------------------------------------------------------

    if os.path.isfile(command):

        try:
            os.startfile(command)

            return (
                f"SUCCESS: Application opened: {command}"
            )

        except Exception as e:

            return (
                f"ERROR: Failed to open {command}: {e}"
            )

    # --------------------------------------------------------
    # 3. Google Chrome
    # --------------------------------------------------------

    chrome_paths = [

        os.path.expandvars(
            r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"
        ),

        os.path.expandvars(
            r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
        ),

        os.path.expandvars(
            r"%LocalAppData%\Google\Chrome\Application\chrome.exe"
        ),

    ]

    if executable.lower() in (
        "chrome",
        "chrome.exe",
        "google-chrome",
        "google-chrome.exe",
    ):

        for path in chrome_paths:

            if os.path.isfile(path):

                try:

                    subprocess.Popen(
                        [path],
                        shell=False
                    )

                    return (
                        "SUCCESS: Google Chrome opened."
                    )

                except Exception as e:

                    return (
                        f"ERROR: Chrome was found at "
                        f"{path}, but could not be opened: {e}"
                    )

        return (
            "ERROR: Google Chrome was not found on this computer."
        )

    # --------------------------------------------------------
    # 4. Visual Studio Code
    # --------------------------------------------------------

    vscode_paths = [

        os.path.expandvars(
            r"%LocalAppData%\Programs\Microsoft VS Code\Code.exe"
        ),

        os.path.expandvars(
            r"%ProgramFiles%\Microsoft VS Code\Code.exe"
        ),

    ]

    if executable.lower() in (
        "code",
        "code.exe",
        "vscode",
        "visual studio code",
    ):

        for path in vscode_paths:

            if os.path.isfile(path):

                try:

                    subprocess.Popen(
                        [path],
                        shell=False
                    )

                    return (
                        "SUCCESS: Visual Studio Code opened."
                    )

                except Exception as e:

                    return (
                        f"ERROR: VS Code was found at "
                        f"{path}, but could not be opened: {e}"
                    )

        return (
            "ERROR: Visual Studio Code was not found "
            "on this computer."
        )

    # --------------------------------------------------------
    # 5. Windows shell fallback
    # --------------------------------------------------------

    try:

        result = subprocess.run(
            ["cmd", "/c", "start", "", command],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:

            return (
                f"SUCCESS: Application opened: {command}"
            )

        error = result.stderr.strip()

        return (
            f"ERROR: Windows could not open "
            f"'{command}'. {error}"
        )

    except Exception as e:

        return (
            f"ERROR: Application '{command}' "
            f"could not be opened: {e}"
        )


# ============================================================
# OPEN PATH
# ============================================================

def open_path(path):
    """
    Open a file or folder using the default Windows application.
    """

    if not path:
        return "ERROR: No path was provided."

    try:

        path = Path(
            os.path.expandvars(
                os.path.expanduser(
                    str(path)
                )
            )
        )

        if not path.exists():

            return (
                f"ERROR: Path does not exist: {path}"
            )

        os.startfile(str(path))

        return (
            f"SUCCESS: Opened path: {path.resolve()}"
        )

    except Exception as e:

        return (
            f"ERROR: Could not open path: {e}"
        )


# ============================================================
# TYPE TEXT
# ============================================================

def type_text(text):

    error = _require_pyautogui()

    if error:
        return error

    if text is None:
        return "ERROR: No text was provided."

    try:

        pyautogui.write(
            str(text),
            interval=0.01
        )

        return "SUCCESS: Text typed."

    except Exception as e:

        return (
            f"ERROR: Could not type text: {e}"
        )


# ============================================================
# PRESS KEY
# ============================================================

def press(key):

    error = _require_pyautogui()

    if error:
        return error

    if not key:
        return "ERROR: No key was provided."

    try:

        pyautogui.press(
            str(key)
        )

        return (
            f"SUCCESS: Key pressed: {key}"
        )

    except Exception as e:

        return (
            f"ERROR: Could not press key: {e}"
        )


# ============================================================
# HOTKEY
# ============================================================

def hotkey(keys):

    error = _require_pyautogui()

    if error:
        return error

    if not keys:
        return "ERROR: No hotkey was provided."

    try:

        if isinstance(keys, str):

            key_list = [
                key.strip()
                for key in keys.split("+")
                if key.strip()
            ]

        elif isinstance(keys, (list, tuple)):

            key_list = [
                str(key).strip()
                for key in keys
                if str(key).strip()
            ]

        else:

            return (
                "ERROR: Hotkey must be a string "
                "or a list of keys."
            )

        if not key_list:

            return "ERROR: No valid keys were provided."

        pyautogui.hotkey(
            *key_list
        )

        return (
            f"SUCCESS: Hotkey pressed: {' + '.join(key_list)}"
        )

    except Exception as e:

        return (
            f"ERROR: Could not press hotkey: {e}"
        )


# ============================================================
# CLICK
# ============================================================

def click(x, y, button="left"):

    error = _require_pyautogui()

    if error:
        return error

    try:

        pyautogui.click(
            x=int(x),
            y=int(y),
            button=str(button)
        )

        return (
            f"SUCCESS: Clicked at ({x}, {y}) "
            f"with {button} button."
        )

    except Exception as e:

        return (
            f"ERROR: Could not click: {e}"
        )


# ============================================================
# SCROLL
# ============================================================

def scroll(amount):

    error = _require_pyautogui()

    if error:
        return error

    try:

        pyautogui.scroll(
            int(amount)
        )

        return (
            f"SUCCESS: Scrolled {amount}."
        )

    except Exception as e:

        return (
            f"ERROR: Could not scroll: {e}"
        )


# ============================================================
# SCREENSHOT
# ============================================================

def screenshot(path=None):
    """
    Take a screenshot of the entire primary display.
    """

    if ImageGrab is None:

        return (
            "ERROR: Screenshot requires Pillow. "
            "Install it with: pip install pillow"
        )

    try:

        # Default screenshot location
        if not path:

            screenshot_dir = (
                Path.cwd() / "screenshots"
            )

            screenshot_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            path = (
                screenshot_dir
                / f"screenshot_{timestamp}.png"
            )

        else:

            path = Path(
                os.path.expandvars(
                    os.path.expanduser(
                        str(path)
                    )
                )
            )

            if str(path.parent) == ".":

                screenshot_dir = (
                    Path.cwd() / "screenshots"
                )

                screenshot_dir.mkdir(
                    parents=True,
                    exist_ok=True
                )

                path = (
                    screenshot_dir / path.name
                )

            else:

                path.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )

        # Capture
        image = ImageGrab.grab()

        # Save
        image.save(
            str(path),
            "PNG"
        )

        # Verify
        if not path.is_file():

            return (
                "ERROR: Screenshot capture appeared "
                "to complete, but the file was not created."
            )

        return (
            f"SUCCESS: Screenshot saved to: "
            f"{path.resolve()}"
        )

    except Exception as e:

        return (
            f"ERROR: Could not take screenshot: {e}"
        )


# ============================================================
# CLIPBOARD
# ============================================================

def clipboard_set(text):

    if pyperclip is None:

        return (
            "ERROR: Clipboard support requires pyperclip. "
            "Install it with: pip install pyperclip"
        )

    if text is None:

        return "ERROR: No text was provided."

    try:

        pyperclip.copy(
            str(text)
        )

        return (
            "SUCCESS: Text copied to clipboard."
        )

    except Exception as e:

        return (
            f"ERROR: Could not set clipboard: {e}"
        )


# ============================================================
# SYSTEM STATUS
# ============================================================

def system_status():

    try:

        return (
            "SUCCESS: JARVIS system is running. "
            f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    except Exception as e:

        return (
            f"ERROR: Could not get system status: {e}"
        )


# ============================================================
# SHUTDOWN
# ============================================================

def shutdown(delay_seconds=25):
    """
    Schedule a Windows shutdown.

    Default delay: 25 seconds.
    """

    try:

        delay_seconds = int(delay_seconds)

        if delay_seconds < 0:
            return (
                "ERROR: delay_seconds cannot be negative."
            )

        result = subprocess.run(
            [
                "shutdown",
                "/s",
                "/t",
                str(delay_seconds)
            ],
            capture_output=True,
            text=True,
            timeout=25
        )

        if result.returncode == 0:

            if delay_seconds == 0:

                return (
                    "SUCCESS: Windows shutdown has been initiated."
                )

            return (
                f"SUCCESS: Windows will shut down in "
                f"{delay_seconds} seconds. "
                f"Use cancel_shutdown to cancel it."
            )

        error = (
            result.stderr.strip()
            or result.stdout.strip()
        )

        return (
            f"ERROR: Could not schedule shutdown. {error}"
        )

    except Exception as e:

        return (
            f"ERROR: Could not shut down Windows: {e}"
        )


# ============================================================
# CANCEL SHUTDOWN
# ============================================================

def cancel_shutdown():
    """
    Cancel a scheduled Windows shutdown.
    """

    try:

        result = subprocess.run(
            [
                "shutdown",
                "/a"
            ],
            capture_output=True,
            text=True,
            timeout=25
        )

        if result.returncode == 0:

            return (
                "SUCCESS: Scheduled shutdown was cancelled."
            )

        error = (
            result.stderr.strip()
            or result.stdout.strip()
        )

        return (
            f"ERROR: No scheduled shutdown could be cancelled. "
            f"{error}"
        )

    except Exception as e:

        return (
            f"ERROR: Could not cancel shutdown: {e}")