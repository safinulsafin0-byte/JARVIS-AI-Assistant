from urllib.parse import quote_plus
import threading
import queue
import traceback

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

from config import BROWSER_PROFILE


# ============================================================
# BROWSER WORKER
# ============================================================

_worker_thread = None
_worker_queue = None
_worker_ready = threading.Event()
_worker_stop = threading.Event()


# ============================================================
# WORKER STATE
#
# IMPORTANT:
# These objects MUST only be accessed inside the worker thread.
# ============================================================

_pw = None
_context = None
_page = None


# ============================================================
# CLOSED / DEAD CONNECTION DETECTION
# ============================================================

_CLOSED_ERROR_HINTS = (
    "has been closed",
    "target closed",
    "target page, context or browser has been closed",
    "browser has been closed",
    "connection closed",
    "context or browser has been closed",
)


def _is_closed_error(err):
    """Detect any error that means the browser/context/page died."""
    msg = str(err).lower()
    return any(hint in msg for hint in _CLOSED_ERROR_HINTS)


# ============================================================
# PAGE HELPERS
# ============================================================

def _page_alive(page):
    if page is None:
        return False

    try:
        return not page.is_closed()
    except Exception:
        return False


def _context_alive():
    global _context

    if _context is None:
        return False

    try:
        # Accessing .pages throws if the context itself is dead.
        _ = _context.pages

        # Also check the underlying browser connection, since a
        # crashed/closed browser process can leave a context object
        # that still superficially responds to .pages.
        browser = getattr(_context, "browser", None)
        if browser is not None:
            try:
                if not browser.is_connected():
                    return False
            except Exception:
                return False

        return True

    except Exception:
        return False


# ============================================================
# START BROWSER
# ============================================================

def _start_browser():
    global _pw
    global _context
    global _page

    # Already running
    if (
        _pw is not None
        and _context_alive()
    ):
        if _page_alive(_page):
            return _page

        try:
            pages = [
                p
                for p in _context.pages
                if _page_alive(p)
            ]

            if pages:
                _page = pages[-1]
                return _page

            # Context alive but no live pages left -> open a fresh one.
            _page = _context.new_page()
            return _page

        except Exception:
            pass

    # --------------------------------------------------------
    # Cleanup old objects
    # --------------------------------------------------------

    _stop_browser()

    # --------------------------------------------------------
    # Start Playwright
    # --------------------------------------------------------

    _pw = sync_playwright().start()

    # --------------------------------------------------------
    # Launch persistent browser
    # --------------------------------------------------------

    _context = _pw.chromium.launch_persistent_context(
        str(BROWSER_PROFILE),
        headless=False,
        viewport={
            "width": 1440,
            "height": 900,
        },
        args=[
            "--start-maximized",
        ],
    )

    # --------------------------------------------------------
    # Existing page
    # --------------------------------------------------------

    pages = [
        p
        for p in _context.pages
        if _page_alive(p)
    ]

    if pages:
        _page = pages[-1]
    else:
        _page = _context.new_page()

    return _page


# ============================================================
# STOP BROWSER
# ============================================================

def _stop_browser():

    global _pw
    global _context
    global _page

    try:
        if _context is not None:
            _context.close()
    except Exception:
        pass

    try:
        if _pw is not None:
            _pw.stop()
    except Exception:
        pass

    _page = None
    _context = None
    _pw = None


# ============================================================
# ENSURE PAGE
#
# Always returns a live page. If the cached context/page turns
# out to be dead (crashed browser, user closed the window, etc.)
# this forces a full clean restart instead of returning a
# half-dead reference.
# ============================================================

def _get_page(force_restart=False):

    global _page

    if not force_restart and _context_alive() and _page_alive(_page):
        return _page

    try:
        _stop_browser()
        return _start_browser()

    except Exception:

        _stop_browser()

        return _start_browser()


# ============================================================
# GENERIC "NAVIGATE WITH AUTO-RECONNECT" HELPER
#
# Every action that does page.goto() (open, search, youtube
# search, etc.) funnels through here so that a dead
# browser/context/page is transparently restarted and the
# navigation retried once, instead of surfacing a raw
# "Target page, context or browser has been closed" error.
# ============================================================

def _goto_with_retry(url, wait_until="domcontentloaded", timeout=60000):

    global _page

    last_error = None

    for attempt in range(2):

        try:

            page = _get_page(force_restart=(attempt > 0))

            page.goto(
                url,
                wait_until=wait_until,
                timeout=timeout,
            )

            _page = page

            return page, None

        except PlaywrightTimeoutError as e:

            last_error = e
            # Timeouts aren't a dead-browser problem; don't force restart.
            if attempt == 0:
                continue
            return None, f"ERROR: Page took too long to load: {url}"

        except Exception as e:

            last_error = e

            print(
                f"[BROWSER NAV ERROR attempt={attempt + 1}] {e}"
            )

            if attempt == 0:
                # Force a clean restart and try exactly once more.
                try:
                    _stop_browser()
                    _start_browser()
                except Exception as restart_error:
                    return None, (
                        "ERROR: Browser restart failed: "
                        f"{restart_error}"
                    )
                continue

            return None, f"ERROR: Could not open {url}: {e}"

    return None, f"ERROR: Could not open {url}: {last_error}"


# ============================================================
# OPEN URL
# ============================================================

def _open_url(url):

    if not url:
        return "ERROR: No URL was provided."

    url = str(url).strip()

    # Remove accidental markdown URL formatting
    if url.startswith("[") and "](" in url and url.endswith(")"):
        try:
            url = url.split("](", 1)[1][:-1]
        except Exception:
            pass

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    page, error = _goto_with_retry(url)

    if error:
        return error

    return f"SUCCESS: Opened {page.url}"


# ============================================================
# CURRENT URL
# ============================================================

def _current_url():

    global _page

    try:

        page = _get_page()

        _page = page

        return page.url

    except Exception as e:

        return (
            f"ERROR: Could not get current URL: {e}"
        )


# ============================================================
# GET ALL PAGES
# ============================================================

def _get_all_pages():

    try:

        page = _get_page()

        if _context is None:
            return [page]

        pages = [
            p
            for p in _context.pages
            if _page_alive(p)
        ]

        return pages

    except Exception:
        return []


# ============================================================
# FIND YOUTUBE VIDEO PAGE
# ============================================================

def _find_youtube_video_page():

    pages = _get_all_pages()

    for page in reversed(pages):

        try:

            url = page.url.lower().strip()

            if (
                "youtube.com/watch" in url
                or "youtube.com/shorts/" in url
                or "youtube.com/live/" in url
                or "youtu.be/" in url
            ):
                return page

        except Exception:
            continue

    return None


# ============================================================
# SEARCH
# ============================================================

def _search(query):

    global _page

    query = str(query).strip()

    if not query:
        return "ERROR: No search query was provided."

    encoded = quote_plus(query)

    try:
        current_url = _get_page().url.lower()
    except Exception:
        current_url = ""

    # ----------------------------------------------------
    # YouTube
    # ----------------------------------------------------

    if (
        "youtube.com" in current_url
        or "youtu.be" in current_url
    ):

        search_url = (
            "https://www.youtube.com/results"
            f"?search_query={encoded}"
        )

        page, error = _goto_with_retry(search_url)

        if error:
            return f"ERROR: Search failed: {error}"

        try:
            page.wait_for_selector(
                "ytd-video-renderer",
                timeout=15000,
            )
        except Exception:
            pass

        return (
            f"SUCCESS: Searched YouTube for "
            f"'{query}'. Current page: {page.url}"
        )

    # ----------------------------------------------------
    # Google
    # ----------------------------------------------------

    search_url = (
        "https://www.google.com/search?q="
        + encoded
    )

    page, error = _goto_with_retry(search_url)

    if error:
        return f"ERROR: Search failed: {error}"

    return (
        f"SUCCESS: Searched Google for "
        f"'{query}'. Current page: {page.url}"
    )


# ============================================================
# ADVANCED YOUTUBE / PAGE HELPERS
# ============================================================

def _youtube_search(query):
    query = str(query or "").strip()
    if not query:
        return "ERROR: No YouTube search query was provided."

    encoded = quote_plus(query)
    search_url = "https://www.youtube.com/results?search_query=" + encoded

    page, error = _goto_with_retry(search_url)

    if error:
        return f"ERROR: YouTube search failed: {error}"

    try:
        page.wait_for_selector("ytd-video-renderer", timeout=15000)
    except Exception:
        pass

    return f"SUCCESS: Searched YouTube for '{query}'."


def _open_nth_youtube_video(index=1):
    try:
        index = int(index)
    except Exception:
        return "ERROR: Video index must be a number."

    if index < 1:
        return "ERROR: Video index must be 1 or greater."

    global _page

    for attempt in range(2):

        try:
            page = _get_page(force_restart=(attempt > 0))

            if "youtube.com/results" not in page.url.lower():
                return "ERROR: Open a YouTube search results page first."

            try:
                page.wait_for_selector("ytd-video-renderer a#video-title", timeout=15000)
            except Exception:
                pass

            videos = page.locator("ytd-video-renderer a#video-title")
            count = videos.count()
            if count == 0:
                return "ERROR: No YouTube videos were found on the current page."
            if index > count:
                return f"ERROR: Only {count} YouTube video result(s) are currently available."

            video = videos.nth(index - 1)
            title = (video.get_attribute("title") or "").strip()
            href = (video.get_attribute("href") or "").strip()
            video.click(timeout=15000)
            try:
                page.wait_for_url("**/watch?**", timeout=20000)
            except Exception:
                pass
            _page = page
            label = title or href or f"video #{index}"
            return f"SUCCESS: Opened YouTube result #{index}: {label}. Current page: {page.url}"

        except Exception as e:

            if _is_closed_error(e) and attempt == 0:
                # Browser/page died mid-click - restart and retry once.
                try:
                    _stop_browser()
                    _start_browser()
                except Exception:
                    pass
                continue

            return f"ERROR: Could not open YouTube result #{index}: {e}"

    return f"ERROR: Could not open YouTube result #{index}."


def _search_results(limit=5):
    try:
        limit = max(1, int(limit))
    except Exception:
        limit = 5

    try:
        page = _get_page()
        url = page.url.lower()
        results = []

        if "youtube.com/results" in url:
            items = page.locator("ytd-video-renderer a#video-title")
            count = min(items.count(), limit)
            for i in range(count):
                item = items.nth(i)
                title = (item.get_attribute("title") or item.inner_text() or "").strip()
                href = (item.get_attribute("href") or "").strip()
                if href.startswith("/"):
                    href = "https://www.youtube.com" + href
                if title:
                    results.append(f"{i+1}. {title}\n   {href}")
            if not results:
                return "ERROR: No YouTube search results were found."
            return "SEARCH RESULTS:\n" + "\n".join(results)

        items = page.locator("a h3")
        count = min(items.count(), limit)
        for i in range(count):
            item = items.nth(i)
            title = (item.inner_text() or "").strip()
            if title:
                results.append(f"{i+1}. {title}")
        if not results:
            return "ERROR: No readable search results were found."
        return "SEARCH RESULTS:\n" + "\n".join(results)
    except Exception as e:
        return f"ERROR: Could not read search results: {e}"


def _page_title():
    try:
        return _get_page().title()
    except Exception as e:
        return f"ERROR: Could not get page title: {e}"


def _toggle_play_pause():
    try:
        page = _get_page()
        video = page.locator("video").first
        count = video.count()
        if count == 0:
            return "ERROR: No playable media was found on the current page."
        state = video.evaluate("v => { if (v.paused) { v.play(); return 'playing'; } v.pause(); return 'paused'; }")
        return f"SUCCESS: Media is now {state}."
    except Exception as e:
        return f"ERROR: Could not toggle play/pause: {e}"


# ============================================================
# EXPLICIT MEDIA CONTROLS
# ============================================================

def _play_video():

    try:

        page = _get_page()

        video = page.locator(
            "video"
        ).first

        if video.count() == 0:

            return (
                "ERROR: No playable video was found "
                "on the current page."
            )

        video.evaluate(
            """
            async (v) => {
                if (v.paused) {
                    await v.play();
                }
            }
            """
        )

        return (
            "SUCCESS: Video is now playing."
        )

    except Exception as e:

        return (
            f"ERROR: Could not play video: {e}"
        )


def _pause_video():

    try:

        page = _get_page()

        video = page.locator(
            "video"
        ).first

        if video.count() == 0:

            return (
                "ERROR: No playable video was found "
                "on the current page."
            )

        video.evaluate(
            """
            (v) => {
                if (!v.paused) {
                    v.pause();
                }
            }
            """
        )

        return (
            "SUCCESS: Video is now paused."
        )

    except Exception as e:

        return (
            f"ERROR: Could not pause video: {e}"
        )


# ============================================================
# OPEN FIRST YOUTUBE VIDEO
# ============================================================

def _open_first_youtube_video():

    return _open_nth_youtube_video(
        index=1
    )


# ============================================================
# BACK
# ============================================================

def _back():

    global _page

    for attempt in range(2):

        try:

            page = _get_page(force_restart=(attempt > 0))

            page.go_back(
                wait_until="domcontentloaded",
                timeout=30000,
            )

            _page = page

            return (
                f"SUCCESS: Went back. "
                f"Current page: {page.url}"
            )

        except Exception as e:

            if _is_closed_error(e) and attempt == 0:
                try:
                    _stop_browser()
                    _start_browser()
                except Exception:
                    pass
                continue

            return (
                f"ERROR: Could not go back: {e}"
            )

    return "ERROR: Could not go back."


# ============================================================
# FORWARD
# ============================================================

def _forward():

    global _page

    for attempt in range(2):

        try:

            page = _get_page(force_restart=(attempt > 0))

            page.go_forward(
                wait_until="domcontentloaded",
                timeout=30000,
            )

            _page = page

            return (
                f"SUCCESS: Went forward. "
                f"Current page: {page.url}"
            )

        except Exception as e:

            if _is_closed_error(e) and attempt == 0:
                try:
                    _stop_browser()
                    _start_browser()
                except Exception:
                    pass
                continue

            return (
                f"ERROR: Could not go forward: {e}"
            )

    return "ERROR: Could not go forward."


# ============================================================
# SCROLL
# ============================================================

def _scroll(amount=700):

    try:

        page = _get_page()

        amount = int(amount)

        page.mouse.wheel(
            0,
            amount,
        )

        return (
            f"SUCCESS: Scrolled {amount}px."
        )

    except Exception as e:

        return (
            f"ERROR: Could not scroll: {e}"
        )


# ============================================================
# CLICK TEXT
# ============================================================

def _click_text(text):

    if not text:
        return "ERROR: No text was provided."

    try:

        page = _get_page()

        locator = page.get_by_text(
            text,
            exact=False,
        ).first

        locator.click(
            timeout=10000,
        )

        return (
            f"SUCCESS: Clicked '{text}'."
        )

    except PlaywrightTimeoutError:

        return (
            f"ERROR: Could not find "
            f"clickable text '{text}'."
        )

    except Exception as e:

        return (
            f"ERROR: Could not click "
            f"'{text}': {e}"
        )


# ============================================================
# TYPE
# ============================================================

def _type(selector, text):

    if not selector:
        return "ERROR: No selector was provided."

    try:

        page = _get_page()

        page.locator(
            selector
        ).fill(
            str(text)
        )

        return (
            f"SUCCESS: Typed text into "
            f"{selector}."
        )

    except Exception as e:

        return (
            f"ERROR: Could not type into "
            f"{selector}: {e}"
        )


# ============================================================
# PAGE TEXT
# ============================================================

def _page_text():

    try:

        page = _get_page()

        text = page.locator(
            "body"
        ).inner_text()

        return text[:12000]

    except Exception as e:

        return (
            f"ERROR: Could not read page text: {e}"
        )


# ============================================================
# EXECUTE ACTION
# ============================================================

def _execute(action, args):

    action = str(action).strip().lower()

    # --------------------------------------------------------
    # OPEN
    # --------------------------------------------------------

    if action == "open":

        return _open_url(
            args.get("url", "")
        )

    # --------------------------------------------------------
    # CURRENT URL
    # --------------------------------------------------------

    if action == "current_url":

        yt_page = _find_youtube_video_page()

        if yt_page is not None:

            global _page

            _page = yt_page

            return yt_page.url

        return _current_url()

    # --------------------------------------------------------
    # FIRST YOUTUBE VIDEO
    # --------------------------------------------------------

    if action == "open_first_video":

        return _open_first_youtube_video()

    # --------------------------------------------------------
    # YOUTUBE SEARCH
    # --------------------------------------------------------

    if action == "youtube_search":

        return _youtube_search(
            args.get("query", "")
        )

    # --------------------------------------------------------
    # OPEN NTH YOUTUBE VIDEO
    # --------------------------------------------------------

    if action == "open_nth_video":

        return _open_nth_youtube_video(
            args.get(
                "index",
                1,
            )
        )

    # --------------------------------------------------------
    # SEARCH RESULTS
    # --------------------------------------------------------

    if action == "search_results":

        return _search_results(
            args.get(
                "limit",
                5,
            )
        )

    # --------------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------------

    if action == "page_title":

        return _page_title()

    # --------------------------------------------------------
    # PLAY / PAUSE MEDIA
    # --------------------------------------------------------

    if action == "toggle_play_pause":

        return _toggle_play_pause()

    # --------------------------------------------------------
    # PLAY VIDEO
    # --------------------------------------------------------

    if action in (
        "play_video",
        "play",
    ):

        return _play_video()

    # --------------------------------------------------------
    # PAUSE VIDEO
    # --------------------------------------------------------

    if action in (
        "pause_video",
        "pause",
    ):

        return _pause_video()

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if action == "search":

        return _search(
            args.get("query", "")
        )

    # --------------------------------------------------------
    # BACK
    # --------------------------------------------------------

    if action == "back":

        return _back()

    # --------------------------------------------------------
    # FORWARD
    # --------------------------------------------------------

    if action == "forward":

        return _forward()

    # --------------------------------------------------------
    # SCROLL
    # --------------------------------------------------------

    if action == "scroll":

        return _scroll(
            args.get(
                "amount",
                700,
            )
        )

    # --------------------------------------------------------
    # CLICK TEXT
    # --------------------------------------------------------

    if action == "click_text":

        return _click_text(
            str(
                args.get(
                    "text",
                    "",
                )
            ).strip()
        )

    # --------------------------------------------------------
    # TYPE
    # --------------------------------------------------------

    if action == "type":

        return _type(
            str(
                args.get(
                    "selector",
                    "",
                )
            ).strip(),
            str(
                args.get(
                    "text",
                    "",
                )
            ),
        )

    # --------------------------------------------------------
    # PAGE TEXT
    # --------------------------------------------------------

    if action == "page_text":

        return _page_text()

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    return (
        f"ERROR: Unknown browser action: "
        f"{action}"
    )


# ============================================================
# WORKER LOOP
# ============================================================

def _browser_worker():

    global _worker_queue

    print(
        "[BROWSER] Browser worker starting..."
    )

    try:

        _start_browser()

        print(
            "[BROWSER] Playwright browser ready."
        )

    except Exception as e:

        print(
            "[BROWSER] Initial startup failed:",
            e,
        )

    _worker_ready.set()

    while not _worker_stop.is_set():

        try:

            job = _worker_queue.get(
                timeout=0.2
            )

        except queue.Empty:

            continue

        if job is None:
            break

        action, args, result_queue = job

        try:

            result = _execute(
                action,
                args,
            )

        except Exception as e:

            print(
                "[BROWSER WORKER ERROR]",
                traceback.format_exc(),
            )

            result = (
                "ERROR: Browser operation failed: "
                f"{e}"
            )

        try:

            result_queue.put(
                result
            )

        except Exception:
            pass

    print(
        "[BROWSER] Browser worker stopping..."
    )

    try:
        _stop_browser()
    except Exception:
        pass


# ============================================================
# START WORKER
# ============================================================

def _ensure_worker():

    global _worker_thread
    global _worker_queue

    if (
        _worker_thread is not None
        and _worker_thread.is_alive()
    ):
        return

    _worker_queue = queue.Queue()

    _worker_ready.clear()
    _worker_stop.clear()

    _worker_thread = threading.Thread(
        target=_browser_worker,
        name="JARVIS-Browser-Worker",
        daemon=True,
    )

    _worker_thread.start()

    # Wait for startup
    _worker_ready.wait(
        timeout=30
    )


# ============================================================
# PUBLIC BROWSER TOOL
#
# This function can safely be called from Flask,
# text mode, voice mode, etc.
#
# ALL PLAYWRIGHT WORK IS SENT TO ONE THREAD.
# ============================================================

def browser_tool(action, **args):

    _ensure_worker()

    if (
        _worker_thread is None
        or not _worker_thread.is_alive()
    ):

        return (
            "ERROR: Browser worker is not running."
        )

    result_queue = queue.Queue(
        maxsize=1
    )

    try:

        _worker_queue.put(
            (
                action,
                args,
                result_queue,
            )
        )

        result = result_queue.get(
            timeout=120
        )

        return str(result)

    except queue.Empty:

        return (
            "ERROR: Browser operation timed out."
        )

    except Exception as e:

        return (
            f"ERROR: Browser request failed: {e}"
        )


# ============================================================
# CLOSE BROWSER
# ============================================================

def close_browser():

    global _worker_thread
    global _worker_queue

    if _worker_queue is None:
        return

    try:

        _worker_stop.set()

        _worker_queue.put(
            None
        )

        if (
            _worker_thread is not None
            and _worker_thread.is_alive()
        ):

            _worker_thread.join(
                timeout=10
            )

    except Exception:
        pass

    _worker_thread = None
    _worker_queue = None