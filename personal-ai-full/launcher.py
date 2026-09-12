# ======================================
# JARVIS MASTER LAUNCHER v2
# ======================================

import subprocess
import sys
import time
import os


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PYTHON = sys.executable


SERVICES = [

    {
        "name": "JARVIS API SERVER",
        "command": [
            PYTHON,
            "api_server.py"
        ],
        "delay": 5
    },

    {
        "name": "EVENT RECEIVER",
        "command": [
            PYTHON,
            "-m",
            "agent.jarvis_event_receiver"
        ],
        "delay": 3
    },

    {
        "name": "BROWSER MONITOR",
        "command": [
            PYTHON,
            "-m",
            "agent.browser_monitor"
        ],
        "delay": 3
    },

    {
        "name": "ACTIVITY WATCHER",
        "command": [
            PYTHON,
            "-m",
            "agent.activity_watcher"
        ],
        "delay": 1
    },

    {
        "name": "ACTIVE WINDOW MONITOR",
        "command": [
            PYTHON,
            "-m",
            "agent.active_window_monitor"
        ],
        "delay": 1
    },

    {
        "name": "SYSTEM MONITOR",
        "command": [
            PYTHON,
            "-m",
            "agent.system_monitor"
        ],
        "delay": 1
    },

    {
        "name": "PROCESS MONITOR",
        "command": [
            PYTHON,
            "-m",
            "agent.process_monitor"
        ],
        "delay": 1
    }

]


processes = []


def start_service(service):

    print(
        f"🚀 STARTING: {service['name']}"
    )

    try:

        process = subprocess.Popen(
            service["command"],
            cwd=BASE_DIR
        )

        processes.append(
            (
                service["name"],
                process
            )
        )

        time.sleep(
            service["delay"]
        )

        if process.poll() is not None:

            print(
                f"❌ {service['name']} FAILED "
                f"(exit code {process.returncode})"
            )

            return False

        print(
            f"✅ {service['name']} STARTED"
        )

        return True


    except Exception as e:

        print(
            f"❌ FAILED TO START "
            f"{service['name']}: {e}"
        )

        return False


def stop_all():

    print(
        "\n🛑 STOPPING JARVIS..."
    )

    for name, process in reversed(processes):

        try:

            if process.poll() is None:

                print(
                    f"Stopping {name}..."
                )

                process.terminate()

        except Exception as e:

            print(
                f"❌ Could not stop {name}: {e}"
            )


    print(
        "🛑 JARVIS OFFLINE"
    )


def main():

    print()
    print("=" * 50)
    print("🔥 STARTING JARVIS SYSTEM")
    print("=" * 50)

    print(
        "🐍 Python:",
        PYTHON
    )

    print(
        "📁 Project:",
        BASE_DIR
    )

    print()


    failed = []


    for service in SERVICES:

        success = start_service(
            service
        )

        if not success:

            failed.append(
                service["name"]
            )


    print()
    print("=" * 50)


    if failed:

        print(
            "⚠️ JARVIS STARTED WITH ERRORS"
        )

        print(
            "Failed services:",
            ", ".join(failed)
        )

    else:

        print(
            "🔥 ALL JARVIS SERVICES ONLINE"
        )


    print("=" * 50)
    print()
    print(
        "Press CTRL+C to stop JARVIS."
    )


    try:

        while True:

            # Detect services that die later

            for name, process in processes:

                if process.poll() is not None:

                    print(
                        f"⚠️ {name} STOPPED "
                        f"(exit code {process.returncode})"
                    )

            time.sleep(10)


    except KeyboardInterrupt:

        stop_all()


if __name__ == "__main__":

    main()