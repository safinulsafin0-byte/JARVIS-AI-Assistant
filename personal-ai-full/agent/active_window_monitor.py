# ======================================
# JARVIS ACTIVE WINDOW MONITOR v1
# WINDOWS APPLICATION AWARENESS
# ======================================

import time
import json
import requests
import win32gui
import win32process
import psutil


EVENT_URL = "http://127.0.0.1:5002/event"

CHECK_INTERVAL = 3

last_window = ""


# ======================================
# GET ACTIVE WINDOW
# ======================================

def get_active_window():

    try:

        hwnd = win32gui.GetForegroundWindow()

        if not hwnd:
            return None

        title = win32gui.GetWindowText(hwnd)

        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        process_name = ""

        try:

            process_name = psutil.Process(pid).name()

        except:

            process_name = "unknown"

        return {

            "title": title,

            "process": process_name,

            "pid": pid

        }

    except Exception as e:

        print(
            "❌ ACTIVE WINDOW ERROR:",
            e
        )

        return None


# ======================================
# ANALYZE APPLICATION
# ======================================

def analyze_window(window):

    global last_window

    if not window:
        return None

    title = window["title"].lower()
    process = window["process"].lower()

    current_id = (
        process
        + "|"
        + title
    )

    if current_id == last_window:
        return None

    last_window = current_id

    context = "general"
    message = "User changed active application."

    # ==============================
    # DEVELOPMENT
    # ==============================

    if any(x in process for x in [
        "code.exe",
        "cursor.exe",
        "pycharm",
        "devenv.exe"
    ]):

        context = "coding"

        message = (
            "Coding environment detected."
        )

    # ==============================
    # BROWSER
    # ==============================

    elif any(x in process for x in [
        "chrome.exe",
        "msedge.exe",
        "firefox.exe",
        "brave.exe"
    ]):

        context = "browser"

        message = (
            "Browser activity detected."
        )

    # ==============================
    # MICROSOFT WORD
    # ==============================

    elif process == "winword.exe":

        context = "document"

        message = (
            "Microsoft Word is active."
        )

    # ==============================
    # POWERPOINT
    # ==============================

    elif process == "powerpnt.exe":

        context = "presentation"

        message = (
            "PowerPoint is active."
        )

    # ==============================
    # EXCEL
    # ==============================

    elif process == "excel.exe":

        context = "spreadsheet"

        message = (
            "Excel is active."
        )

    # ==============================
    # TERMINAL
    # ==============================

    elif any(x in process for x in [
        "powershell.exe",
        "windowsterminal.exe",
        "cmd.exe"
    ]):

        context = "terminal"

        message = (
            "Terminal activity detected."
        )

    # ==============================
    # PDF
    # ==============================

    elif (
        ".pdf" in title
        or
        "pdf" in process
    ):

        context = "reading"

        message = (
            "PDF reading activity detected."
        )

    return {

        "type": "active_window",

        "context": context,

        "message": message,

        "application": window["process"],

        "title": window["title"]

    }


# ======================================
# SEND EVENT
# ======================================

def send_event(event):

    try:

        response = requests.post(

            EVENT_URL,

            json=event,

            timeout=3

        )

        print(
            "🧠 ACTIVE WINDOW EVENT:",
            json.dumps(
                event,
                indent=2
            )
        )

        print(
            "🧠 EVENT RESPONSE:",
            response.json()
        )

    except Exception as e:

        print(
            "❌ EVENT BUS ERROR:",
            e
        )


# ======================================
# MAIN LOOP
# ======================================

def start_monitor():

    print(
        "🔥 JARVIS ACTIVE WINDOW MONITOR STARTED"
    )

    print(
        "Event Bus:",
        EVENT_URL
    )

    while True:

        window = get_active_window()

        event = analyze_window(
            window
        )

        if event:

            send_event(
                event
            )

        time.sleep(
            CHECK_INTERVAL
        )


# ======================================
# START
# ======================================

if __name__ == "__main__":

    start_monitor()