import os
import json
import time


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MEMORY_FILE = os.path.join(
    BASE_DIR,
    "memory",
    "activity_history.json"
)


DEFAULT_COOLDOWN = 60


memory = {
    "last_context": "",
    "last_application": "",
    "last_title": "",
    "context_start_time": 0,
    "last_spoken_time": 0,
    "total_events": 0
}


def load_memory():

    global memory

    try:

        os.makedirs(
            os.path.dirname(MEMORY_FILE),
            exist_ok=True
        )

        if not os.path.exists(MEMORY_FILE):

            save_memory()

            return

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        if isinstance(data, dict):

            memory.update(data)

    except Exception as e:

        print(
            "❌ CONTEXT MEMORY LOAD ERROR:",
            e
        )


def save_memory():

    try:

        os.makedirs(
            os.path.dirname(MEMORY_FILE),
            exist_ok=True
        )

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                memory,
                f,
                indent=4,
                ensure_ascii=False
            )

    except Exception as e:

        print(
            "❌ CONTEXT MEMORY SAVE ERROR:",
            e
        )


def update_context(
    context,
    application="",
    title=""
):

    now = time.time()

    context_changed = (
        context != memory.get(
            "last_context",
            ""
        )
    )

    if context_changed:

        memory["last_context"] = context

        memory["context_start_time"] = now

    memory["last_application"] = application

    memory["last_title"] = title

    memory["total_events"] = (
        memory.get(
            "total_events",
            0
        )
        + 1
    )

    save_memory()

    return context_changed


def get_context_duration():

    start_time = memory.get(
        "context_start_time",
        0
    )

    if not start_time:

        return 0

    duration = time.time() - start_time

    return int(duration)


def should_speak(
    context,
    cooldown=DEFAULT_COOLDOWN
):

    now = time.time()

    last_spoken = memory.get(
        "last_spoken_time",
        0
    )

    last_context = memory.get(
        "last_context",
        ""
    )

    if context != last_context:

        memory["last_spoken_time"] = now

        save_memory()

        return True

    if now - last_spoken >= cooldown:

        memory["last_spoken_time"] = now

        save_memory()

        return True

    return False


def mark_spoken():

    memory["last_spoken_time"] = time.time()

    save_memory()


def get_memory():

    return memory.copy()


load_memory()