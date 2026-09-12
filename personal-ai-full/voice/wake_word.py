# ============================================================
# JARVIS WAKE WORD ENGINE
# "HEY JARVIS" / "JARVIS"
# ============================================================

import time


# ============================================================
# WAKE WORDS
# ============================================================

WAKE_WORDS = (
    "hey jarvis",
    "hey jarvis",
    "jarvis",
    "হে জার্ভিস",
    "জার্ভিস",
)


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    return (
        str(text)
        .lower()
        .strip()
        .replace(",", " ")
        .replace(".", " ")
        .replace("!", " ")
        .replace("?", " ")
    )


# ============================================================
# CHECK WAKE WORD
# ============================================================

def contains_wake_word(text):

    normalized = normalize_text(text)

    if not normalized:
        return False

    for wake_word in WAKE_WORDS:

        if wake_word in normalized:
            return True

    return False


# ============================================================
# REMOVE WAKE WORD
# ============================================================

def remove_wake_word(text):

    if not text:
        return ""

    result = str(text).strip()

    lower_result = result.lower()

    for wake_word in WAKE_WORDS:

        index = lower_result.find(
            wake_word
        )

        if index != -1:

            result = (
                result[:index]
                + result[
                    index + len(wake_word):
                ]
            )

            break

    return result.strip()


# ============================================================
# EXTRACT COMMAND
# ============================================================

def extract_command(text):

    if not contains_wake_word(text):

        return None

    command = remove_wake_word(
        text
    )

    return command.strip()


# ============================================================
# WAKE WORD STATE
# ============================================================

class WakeWordEngine:

    def __init__(
        self,
        timeout_seconds=8
    ):

        self.timeout_seconds = (
            timeout_seconds
        )

        self.active = False
        self.activated_at = None

    # --------------------------------------------------------
    # ACTIVATE
    # --------------------------------------------------------

    def activate(self):

        self.active = True

        self.activated_at = time.time()

    # --------------------------------------------------------
    # DEACTIVATE
    # --------------------------------------------------------

    def deactivate(self):

        self.active = False

        self.activated_at = None

    # --------------------------------------------------------
    # CHECK TIMEOUT
    # --------------------------------------------------------

    def timed_out(self):

        if not self.active:
            return False

        if self.activated_at is None:
            return False

        elapsed = (
            time.time()
            - self.activated_at
        )

        return (
            elapsed >= self.timeout_seconds
        )

    # --------------------------------------------------------
    # PROCESS TEXT
    # --------------------------------------------------------

    def process(self, text):

        if not text:
            return None

        # ----------------------------------------------------
        # Already active
        # ----------------------------------------------------

        if self.active:

            if self.timed_out():

                self.deactivate()

                return None

            return str(
                text
            ).strip()

        # ----------------------------------------------------
        # Waiting for wake word
        # ----------------------------------------------------

        command = extract_command(
            text
        )

        if command is None:

            return None

        # ----------------------------------------------------
        # Wake word detected
        # ----------------------------------------------------

        self.activate()

        # ----------------------------------------------------
        # Wake word only
        # ----------------------------------------------------

        if not command:

            return ""

        return command


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    engine = WakeWordEngine()

    tests = (
        "hello jarvis",
        "Hey JARVIS",
        "Hey JARVIS open YouTube",
        "Jarvis what is AI",
        "random sentence",
    )

    for test in tests:

        result = engine.process(
            test
        )

        print(
            f"{test!r} -> {result!r}"
        )