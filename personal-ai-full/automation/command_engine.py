from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse


# ============================================================
# JARVIS AUTOMATION COMMAND ENGINE
# Drop-in natural-language automation layer.
#
# Supported examples:
#   open youtube and search for lofi music and play the 2nd video
#   search python tutorial on youtube and open the first video
#   search for lofi music on youtube                (search only, no auto-play)
#   play the 3rd video
#   search for latest AI news and tell me the results
#   open github
#   go back
#   scroll down
#   delete temporary files
# ============================================================


ORDINALS = {
    "first": 1,
    "1st": 1,
    "one": 1,
    "second": 2,
    "2nd": 2,
    "two": 2,
    "third": 3,
    "3rd": 3,
    "three": 3,
    "fourth": 4,
    "4th": 4,
    "four": 4,
    "fifth": 5,
    "5th": 5,
    "five": 5,
}


KNOWN_SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "facebook": "https://www.facebook.com",
    "gmail": "https://mail.google.com",
    "linkedin": "https://www.linkedin.com",
    "x": "https://x.com",
    "twitter": "https://x.com",
    "reddit": "https://www.reddit.com",
}


# Phrases that indicate the user actually wants a video opened/played,
# as opposed to just wanting the search performed.
PLAY_INTENT_PHRASES = (
    "play",
    "open the",
    "open first",
    "open second",
    "open third",
    "open fourth",
    "open fifth",
    "open 1st",
    "open 2nd",
    "open 3rd",
    "watch",
)


def _browser(action, **kwargs):
    try:
        from browser.browser_agent import browser_tool
        return str(browser_tool(action, **kwargs)).strip()
    except Exception as e:
        return f"ERROR: Browser automation failed: {e}"


def _success_or_error(result):
    return str(result).strip()


def _normalize(text):
    return re.sub(r"\s+", " ", str(text or "").lower()).strip()


def _extract_video_index(text, default=None):
    text = _normalize(text)

    for word, number in ORDINALS.items():
        if re.search(rf"\b{re.escape(word)}\b", text):
            return number

    match = re.search(r"\b(\d+)(?:st|nd|rd|th)?\s+video\b", text)
    if match:
        return max(1, int(match.group(1)))

    return default


def _wants_video_played(text):
    """
    True only when the user's wording actually asks for a video to be
    opened/played (e.g. "...and play the 2nd video", "open the first
    video"). A bare "search for X on youtube" does NOT count, even
    though an ordinal-less default used to be assumed here before.
    """
    text = _normalize(text)
    return any(phrase in text for phrase in PLAY_INTENT_PHRASES)


def _extract_youtube_query(original):
    text = str(original or "").strip()

    patterns = (
        r"(?:search for|search)\s+(.+?)\s+(?:on\s+)?youtube(?:\s|$)",
        r"(?:search for|search)\s+(.+?)\s+(?:and\s+)?(?:play|open)\s+(?:the\s+)?(?:first|second|third|fourth|fifth|\d+(?:st|nd|rd|th)?)\s+video",
        r"youtube\s+(?:and\s+)?(?:search for|search)\s+(.+?)(?:\s+(?:and\s+)?(?:play|open)\b|$)",
    )

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            query = match.group(1).strip(" ,.-")
            if query:
                return query

    return ""


def _looks_like_youtube_workflow(text):
    text = _normalize(text)
    return (
        "youtube" in text
        and any(word in text for word in ("search", "play", "open"))
    )


def _extract_search_query_for_results(original):
    text = str(original or "").strip()

    match = re.search(
        r"(?:search for|search)\s+(.+?)(?:\s+(?:and\s+)?(?:tell me|show me|give me|read me|what are)\s+(?:the\s+)?(?:results?|top results?))?$",
        text,
        flags=re.I,
    )
    if match:
        return match.group(1).strip(" ,.-")

    return ""


def _wants_results(text):
    text = _normalize(text)
    return any(
        phrase in text
        for phrase in (
            "tell me the result",
            "tell me the results",
            "show me the result",
            "show me the results",
            "what are the results",
            "read the results",
            "give me the results",
            "top results",
        )
    )


def _format_search_results(raw):
    raw = str(raw or "").strip()

    if raw.startswith("ERROR:"):
        return raw

    if not raw:
        return "ERROR: No search results were found."

    return raw


def _cleanup_directory(path: Path):
    deleted = 0
    failed = 0
    freed = 0

    if not path.exists() or not path.is_dir():
        return deleted, failed, freed

    try:
        entries = list(path.iterdir())
    except Exception:
        return deleted, failed, freed

    for item in entries:
        try:
            if item.is_symlink() or item.is_file():
                try:
                    freed += item.stat().st_size
                except Exception:
                    pass
                item.unlink(missing_ok=True)
                deleted += 1

            elif item.is_dir():
                try:
                    for child in item.rglob("*"):
                        if child.is_file():
                            try:
                                freed += child.stat().st_size
                            except Exception:
                                pass
                except Exception:
                    pass

                shutil.rmtree(item, ignore_errors=False)
                deleted += 1

        except Exception:
            failed += 1

    return deleted, failed, freed


def cleanup_temporary_files():
    """
    Cleans only safe temporary locations:
      1. Current user's TEMP directory
      2. Project uploads directory

    It never touches Windows, Program Files, user Documents,
    Desktop, Downloads, or arbitrary drives.
    """

    total_deleted = 0
    total_failed = 0
    total_freed = 0

    temp_dir = Path(tempfile.gettempdir())

    d, f, b = _cleanup_directory(temp_dir)
    total_deleted += d
    total_failed += f
    total_freed += b

    try:
        project_root = Path(__file__).resolve().parents[1]
        uploads_dir = project_root / "uploads"

        d, f, b = _cleanup_directory(uploads_dir)
        total_deleted += d
        total_failed += f
        total_freed += b
    except Exception:
        pass

    freed_mb = total_freed / (1024 * 1024)

    if total_failed:
        return (
            "SUCCESS: Temporary cleanup completed. "
            f"Deleted {total_deleted} items and freed approximately "
            f"{freed_mb:.2f} MB. {total_failed} locked/protected items "
            "could not be removed."
        )

    return (
        "SUCCESS: Temporary cleanup completed. "
        f"Deleted {total_deleted} items and freed approximately "
        f"{freed_mb:.2f} MB."
    )


def handle_automation_command(user_text):
    """
    Returns:
        str  -> command was recognized and executed
        None -> not an automation command, let normal JARVIS continue
    """

    if not user_text:
        return None

    original = str(user_text).strip()
    text = _normalize(original)

    if not text:
        return None

    # ========================================================
    # SAFE TEMP CLEANUP
    # ========================================================

    cleanup_phrases = (
        "delete temporary files",
        "delete temp files",
        "clear temporary files",
        "clear temp files",
        "clean temporary files",
        "clean temp files",
        "clean up temporary files",
        "cleanup temporary files",
        "delete all temporary files",
        "delete all temp files",
    )

    if any(phrase in text for phrase in cleanup_phrases):
        return cleanup_temporary_files()

    # ========================================================
    # YOUTUBE: SEARCH (+ OPTIONAL PLAY OF NTH VIDEO)
    #
    # Search always runs. A specific video is only opened/played
    # when the user's phrasing actually asks for it (an ordinal
    # like "second"/"2nd" AND/OR a play/open/watch verb). A plain
    # "search for X on youtube" now stops after searching instead
    # of silently auto-playing the first result.
    # ========================================================

    if _looks_like_youtube_workflow(text):
        query = _extract_youtube_query(original)

        if query:
            search_result = _browser(
                "youtube_search",
                query=query,
            )

            if search_result.startswith("ERROR:"):
                return search_result

        if _wants_video_played(text):
            index = _extract_video_index(text, default=1)

            return _browser(
                "open_nth_video",
                index=index,
            )

        # Search only — wait for the user's follow-up command
        # ("play the second one") instead of guessing.
        if query:
            return search_result

        # No query and no play intent detected on a "youtube" line;
        # nothing safe to do here.
        return None

    # ========================================================
    # CURRENT YOUTUBE RESULT: PLAY/OPEN NTH VIDEO
    # (e.g. "play the second video" said after a search)
    # ========================================================

    if any(
        phrase in text
        for phrase in (
            "play the",
            "open the",
            "play ",
            "open ",
            "watch the",
            "watch ",
        )
    ) and "video" in text:
        index = _extract_video_index(text, default=1)

        return _browser(
            "open_nth_video",
            index=index,
        )

    # ========================================================
    # SEARCH + REPORT RESULTS
    # ========================================================

    if _wants_results(text):
        query = _extract_search_query_for_results(original)

        if query:
            search_result = _browser(
                "search",
                query=query,
            )

            if search_result.startswith("ERROR:"):
                return search_result

        results = _browser(
            "search_results",
            limit=5,
        )

        return _format_search_results(results)

    # ========================================================
    # ASK FOR CURRENT SEARCH RESULTS
    # ========================================================

    if any(
        phrase in text
        for phrase in (
            "what are the results",
            "show me the results",
            "tell me the results",
            "read the results",
            "give me the results",
        )
    ):
        return _format_search_results(
            _browser(
                "search_results",
                limit=5,
            )
        )

    # ========================================================
    # OPEN KNOWN SITES
    # ========================================================

    for site_name, url in KNOWN_SITES.items():
        if text in (
            f"open {site_name}",
            f"open {site_name}.com",
            f"go to {site_name}",
            f"launch {site_name}",
        ):
            return _browser("open", url=url)

    # ========================================================
    # BROWSER NAVIGATION
    # ========================================================

    if text in ("go back", "back", "browser back"):
        return _browser("back")

    if text in ("go forward", "forward", "browser forward"):
        return _browser("forward")

    if text in ("scroll down", "scroll"):
        return _browser("scroll", amount=800)

    if text in ("scroll up",):
        return _browser("scroll", amount=-800)

    return None