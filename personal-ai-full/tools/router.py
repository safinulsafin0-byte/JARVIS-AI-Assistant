from config import REQUIRE_CONFIRMATION_FOR
from tools import file_ops, system_ops


# ============================================================
# TOOL DESCRIPTIONS
# ============================================================

TOOL_DESCRIPTIONS = """
You are controlling a Windows computer.

AVAILABLE TOOLS:

FILESYSTEM:
filesystem.list_dir(path)
filesystem.read_file(path)
filesystem.create_file(path, content)
filesystem.create_folder(path)
filesystem.write_file(path, content)
filesystem.rename(path, new_name)
filesystem.move(path, destination)
filesystem.copy(path, destination)
filesystem.delete_file(path)
filesystem.delete_folder(path)
filesystem.search_files(root, pattern)

SYSTEM:
system.open_app(command)
system.open_path(path)
system.type_text(text)
system.press(key)
system.hotkey(keys)
system.click(x, y, button)
system.scroll(amount)
system.screenshot(path)
system.clipboard_set(text)
system.system_status()
system.shutdown()
system.cancel_shutdown()

BROWSER:
browser.open(url)
browser.back()
browser.forward()
browser.scroll(amount)
browser.click_text(text)
browser.type(selector, text)
browser.search(query)
browser.page_text()

BROWSER VIDEO CONTROL:
browser.play_video()
browser.pause_video()
browser.toggle_play_pause()
browser.mute_video()
browser.unmute_video()


IMPORTANT BROWSER RULES:

- If the user says "open YouTube", use:
  browser.open(url="https://www.youtube.com")

- If the user says "open Google", use:
  browser.open(url="https://www.google.com")

- If the user says "open Facebook", use:
  browser.open(url="https://www.facebook.com")

- If the user says "open Gmail", use:
  browser.open(url="https://mail.google.com")

- If the user says "open Chrome", use:
  system.open_app(command="chrome")

- Website requests should use browser.open, NOT system.open_app.

VIDEO CONTROL RULES:

- If the user says "pause the video", use:
  browser.pause_video()

- If the user says "pause video", use:
  browser.pause_video()

- If the user says "play the video", use:
  browser.play_video()

- If the user says "resume the video", use:
  browser.play_video()

- If the user says "continue the video", use:
  browser.play_video()

- If the user says "toggle video", use:
  browser.toggle_play_pause()

- If the user says "play or pause the video", use:
  browser.toggle_play_pause()

- If the user says "mute the video", use:
  browser.mute_video()

- If the user says "unmute the video", use:
  browser.unmute_video()

- NEVER use browser.open() with a javascript: URL.

- NEVER use browser.open() with:
  javascript:
  data:
  file:

- NEVER generate JavaScript URLs such as:
  javascript:void(document.getElementsByTagName('video')[0].pause())

- Video actions must use the dedicated browser video tools.

- After a tool executes, trust the actual tool result.
- NEVER claim an action succeeded if the tool returned ERROR.
- NEVER invent a successful result.
"""


# ============================================================
# WEBSITE ALIASES
# ============================================================

WEBSITE_ALIASES = {
    "youtube": "https://www.youtube.com",
    "youtube.com": "https://www.youtube.com",

    "google": "https://www.google.com",
    "google.com": "https://www.google.com",

    "facebook": "https://www.facebook.com",
    "facebook.com": "https://www.facebook.com",

    "gmail": "https://mail.google.com",
    "gmail.com": "https://mail.google.com",

    "github": "https://github.com",
    "github.com": "https://github.com",

    "reddit": "https://www.reddit.com",
    "reddit.com": "https://www.reddit.com",

    "instagram": "https://www.instagram.com",
    "instagram.com": "https://www.instagram.com",

    "twitter": "https://twitter.com",
    "twitter.com": "https://twitter.com",

    "x": "https://x.com",
    "x.com": "https://x.com",
}


# ============================================================
# TOOL NAME ALIASES
# ============================================================

TOOL_ALIASES = {

    # -------------------------
    # SYSTEM
    # -------------------------

    "screenshot": "system.screenshot",
    "open_app": "system.open_app",
    "open_path": "system.open_path",
    "type_text": "system.type_text",
    "press": "system.press",
    "hotkey": "system.hotkey",
    "click": "system.click",
    "scroll": "system.scroll",
    "clipboard_set": "system.clipboard_set",
    "system_status": "system.system_status",
    "shutdown": "system.shutdown",
    "cancel_shutdown": "system.cancel_shutdown",

    # -------------------------
    # BROWSER VIDEO
    # -------------------------

    "play_video": "browser.play_video",
    "pause_video": "browser.pause_video",
    "toggle_play_pause": "browser.toggle_play_pause",
    "mute_video": "browser.mute_video",
    "unmute_video": "browser.unmute_video",

    # Common variations from LLM
    "browser.play": "browser.play_video",
    "browser.pause": "browser.pause_video",
    "browser.resume_video": "browser.play_video",
    "browser.resume": "browser.play_video",
    "browser.continue_video": "browser.play_video",
    "browser.toggle_video": "browser.toggle_play_pause",
}


# ============================================================
# EXECUTE TOOL
# ============================================================

def execute_tool_call(call, user_confirmed=False):

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not isinstance(call, dict):
        return "ERROR: Invalid tool call. Expected a dictionary."

    tool = call.get("tool", "")
    args = call.get("args", {}) or {}

    if not isinstance(args, dict):
        args = {}

    # --------------------------------------------------------
    # Normalize tool name
    # --------------------------------------------------------

    tool = str(tool).strip()

    if not tool:
        return "ERROR: Empty tool name."

    if tool in TOOL_ALIASES:
        tool = TOOL_ALIASES[tool]

    # ========================================================
    # WEBSITE FALLBACK
    # ========================================================

    if tool == "system.open_app":

        command = str(
            args.get("command", "")
        ).strip()

        normalized = (
            command
            .lower()
            .strip()
            .rstrip("/")
        )

        normalized = normalized.strip("\"'")

        if normalized in WEBSITE_ALIASES:

            url = WEBSITE_ALIASES[normalized]

            try:

                from browser.browser_agent import browser_tool

                return browser_tool(
                    "open",
                    url=url
                )

            except Exception as e:

                return (
                    f"ERROR: Could not open website "
                    f"{url}: {e}"
                )

    # ========================================================
    # CONFIRMATION
    # ========================================================

    action = tool.split(".")[-1]

    if (
        action in REQUIRE_CONFIRMATION_FOR
        and not user_confirmed
    ):

        return (
            f"CONFIRMATION_NEEDED: "
            f"{action} with args={args}"
        )

    # ========================================================
    # FILESYSTEM
    # ========================================================

    if tool == "filesystem.list_dir":
        return file_ops.list_dir(**args)

    if tool == "filesystem.read_file":
        return file_ops.read_file(**args)

    if tool == "filesystem.create_file":
        return file_ops.create_file(**args)

    if tool == "filesystem.create_folder":
        return file_ops.create_folder(**args)

    if tool == "filesystem.write_file":
        return file_ops.write_file(**args)

    if tool == "filesystem.rename":
        return file_ops.rename(**args)

    if tool == "filesystem.move":
        return file_ops.move(**args)

    if tool == "filesystem.copy":
        return file_ops.copy(**args)

    if tool == "filesystem.delete_file":
        return file_ops.delete_file(**args)

    if tool == "filesystem.delete_folder":
        return file_ops.delete_folder(**args)

    if tool == "filesystem.search_files":
        return file_ops.search_files(**args)

    # ========================================================
    # SYSTEM
    # ========================================================

    if tool == "system.open_app":

        return system_ops.open_app(
            **args
        )

    if tool == "system.open_path":

        return system_ops.open_path(
            **args
        )

    if tool == "system.type_text":

        return system_ops.type_text(
            **args
        )

    if tool == "system.press":

        return system_ops.press(
            **args
        )

    if tool == "system.hotkey":

        return system_ops.hotkey(
            **args
        )

    if tool == "system.click":

        return system_ops.click(
            **args
        )

    if tool == "system.scroll":

        return system_ops.scroll(
            **args
        )

    if tool == "system.screenshot":

        return system_ops.screenshot(
            **args
        )

    if tool == "system.clipboard_set":

        return system_ops.clipboard_set(
            **args
        )

    if tool == "system.system_status":

        return system_ops.system_status()

    if tool == "system.shutdown":

        return system_ops.shutdown()

    if tool == "system.cancel_shutdown":

        return system_ops.cancel_shutdown()

    # ========================================================
    # BROWSER
    # ========================================================

    if tool.startswith("browser."):

        from browser.browser_agent import browser_tool

        action = tool.split(
            ".",
            1
        )[1]

        try:

            return browser_tool(
                action,
                **args
            )

        except Exception as e:

            return (
                f"ERROR: Browser action "
                f"{action} failed: {e}"
            )

    # ========================================================
    # UNKNOWN TOOL
    # ========================================================

    return (
        f"ERROR: Unknown tool: {tool}"
    )