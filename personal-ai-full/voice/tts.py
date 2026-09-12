# ============================================================
# JARVIS OFFLINE TEXT-TO-SPEECH
#
# File:
# D:\personal-ai-full\voice\tts.py
#
# Uses:
#   Piper TTS
#   en_US-lessac-medium.onnx
#
# Fully local / offline.
# ============================================================

from __future__ import annotations

import os
import subprocess
import tempfile
import threading
import wave
from pathlib import Path

import winsound


# ============================================================
# PATHS
# ============================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent.parent
)

PIPER_MODEL = (
    BASE_DIR
    / "models"
    / "en_US-lessac-medium.onnx"
)


# ============================================================
# STATE
# ============================================================

_tts_lock = threading.Lock()

_current_process = None


# ============================================================
# LOG
# ============================================================

def log(message: str):

    print(
        f"[JARVIS TTS] {message}"
    )


# ============================================================
# MODEL CHECK
# ============================================================

def model_exists() -> bool:

    return PIPER_MODEL.exists()


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text: str) -> str:

    text = str(
        text or ""
    ).strip()

    if not text:
        return ""

    # Remove fenced code blocks
    import re

    text = re.sub(
        r"```[\s\S]*?```",
        "Code block omitted.",
        text,
    )

    # Remove inline code
    text = re.sub(
        r"`([^`]+)`",
        r"\1",
        text,
    )

    # Remove markdown headings
    text = re.sub(
        r"^#{1,6}\s+",
        "",
        text,
        flags=re.MULTILINE,
    )

    # Remove bold / italic
    text = text.replace(
        "**",
        "",
    )

    text = text.replace(
        "__",
        "",
    )

    text = text.replace(
        "*",
        "",
    )

    # Replace URLs
    text = re.sub(
        r"https?://\S+",
        "website",
        text,
        flags=re.IGNORECASE,
    )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# STOP CURRENT TTS
# ============================================================

def stop():

    global _current_process

    process = _current_process

    if process is not None:

        try:

            if process.poll() is None:

                process.terminate()

        except Exception:
            pass

        _current_process = None

    try:

        winsound.PlaySound(
            None,
            winsound.SND_PURGE,
        )

    except Exception:
        pass


# ============================================================
# WAV DURATION
# ------------------------------------------------------------
# Reads the actual length of the generated clip so the caller
# (Flask route / frontend) can know exactly how long playback
# will take, instead of guessing from text length. Returns 0
# if it can't be determined for any reason - callers should
# fall back to an estimate in that case.
# ============================================================

def _get_wav_duration_ms(
    path: str
) -> int:

    try:

        with wave.open(
            path,
            "rb",
        ) as wf:

            frames = wf.getnframes()

            rate = wf.getframerate()

            if rate <= 0:

                return 0

            return int(
                round(
                    (
                        frames
                        / float(rate)
                    )
                    * 1000
                )
            )

    except Exception as error:

        log(
            f"Could not read WAV duration: {error}"
        )

        return 0


# ============================================================
# GENERATE WAV WITH PIPER
# ============================================================

def generate_wav(
    text: str,
    output_wav: str,
):

    global _current_process

    if not model_exists():

        raise FileNotFoundError(
            "Piper model not found:\n"
            f"{PIPER_MODEL}"
        )

    cleaned = clean_text(
        text
    )

    if not cleaned:

        raise ValueError(
            "Nothing to speak."
        )

    # --------------------------------------------------------
    # Find Piper executable
    # --------------------------------------------------------

    piper_executable = "piper"

    # If running inside the virtual environment,
    # explicitly prefer the executable there.
    venv_scripts = (
        BASE_DIR
        / "venv"
        / "Scripts"
        / "piper.exe"
    )

    if venv_scripts.exists():

        piper_executable = str(
            venv_scripts
        )

    command = [

        piper_executable,

        "--model",
        str(PIPER_MODEL),

        "--output_file",
        str(output_wav),
    ]

    log(
        f"Model: {PIPER_MODEL}"
    )

    process = subprocess.Popen(
        command,

        stdin=subprocess.PIPE,

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        text=True,

        encoding="utf-8",

        errors="replace",
    )

    _current_process = process

    try:

        stdout, stderr = process.communicate(
            input=cleaned
        )

    finally:

        if _current_process is process:

            _current_process = None

    if process.returncode != 0:

        raise RuntimeError(
            "Piper failed.\n"
            f"stdout:\n{stdout}\n"
            f"stderr:\n{stderr}"
        )

    if not os.path.exists(
        output_wav
    ):

        raise RuntimeError(
            "Piper completed but "
            "did not create the WAV file."
        )

    if os.path.getsize(
        output_wav
    ) <= 0:

        raise RuntimeError(
            "Piper created an empty WAV file."
        )

    return output_wav


# ============================================================
# SYNCHRONOUS SPEAK
# ============================================================

def speak(
    text: str
):

    cleaned = clean_text(
        text
    )

    if not cleaned:

        return {
            "success": False,
            "error": "Nothing to speak.",
        }

    if not model_exists():

        error = (
            "Piper model not found:\n"
            f"{PIPER_MODEL}"
        )

        print(
            "[TTS ERROR]",
            error
        )

        return {
            "success": False,
            "error": error,
        }

    with _tts_lock:

        temp_wav = None

        try:

            # ------------------------------------------------
            # Stop any previous audio
            # ------------------------------------------------

            stop()

            # ------------------------------------------------
            # Temporary WAV
            # ------------------------------------------------

            fd, temp_wav = tempfile.mkstemp(
                prefix="jarvis_tts_",
                suffix=".wav",
            )

            os.close(
                fd
            )

            # ------------------------------------------------
            # Piper
            # ------------------------------------------------

            generate_wav(
                cleaned,
                temp_wav,
            )

            duration_ms = _get_wav_duration_ms(
                temp_wav
            )

            log(
                "Playing response..."
            )

            # ------------------------------------------------
            # Native Windows playback
            # ------------------------------------------------

            winsound.PlaySound(
                temp_wav,
                winsound.SND_FILENAME,
            )

            log(
                "Playback completed."
            )

            return {
                "success": True,
                "text": cleaned,
                "offline": True,
                "duration_ms": duration_ms,
            }

        except Exception as error:

            print(
                "[TTS ERROR]",
                error
            )

            return {
                "success": False,
                "error": str(error),
            }

        finally:

            if temp_wav:

                try:

                    if os.path.exists(
                        temp_wav
                    ):

                        os.remove(
                            temp_wav
                        )

                except Exception:
                    pass


# ============================================================
# ASYNC SPEAK
#
# Flask won't have to wait until the sentence finishes
# PLAYING - but it DOES wait for the (fast) Piper generation
# step, because that's the only way to know the real clip
# duration before responding. Only playback itself happens in
# the background thread.
#
# The lock is held only around generation (protects the
# shared Piper subprocess handle), NOT across playback -
# holding it across playback would let one lingering speak()
# call block/deadlock a following stop()+speak() pair, since
# stop() can't interrupt audio it never gets to run against.
# Windows' PlaySound already stops any previous synchronous
# clip when a new one starts, so serializing generation alone
# is enough to keep behavior correct.
# ============================================================

def speak_async(
    text: str
):

    cleaned = clean_text(
        text
    )

    if not cleaned:

        return {
            "success": False,
            "error": "Nothing to speak.",
        }

    if not model_exists():

        error = (
            "Piper model not found:\n"
            f"{PIPER_MODEL}"
        )

        print(
            "[TTS ERROR]",
            error
        )

        return {
            "success": False,
            "error": error,
        }

    # ----------------------------------------------------------
    # Stop whatever might still be playing from a previous turn
    # BEFORE generating the new clip, so two responses can never
    # overlap on the speakers (and therefore never overlap into
    # the microphone either).
    # ----------------------------------------------------------

    stop()

    temp_wav = None

    duration_ms = 0

    with _tts_lock:

        try:

            fd, temp_wav = tempfile.mkstemp(
                prefix="jarvis_tts_",
                suffix=".wav",
            )

            os.close(
                fd
            )

            generate_wav(
                cleaned,
                temp_wav,
            )

            duration_ms = _get_wav_duration_ms(
                temp_wav
            )

        except Exception as error:

            if temp_wav:

                try:

                    if os.path.exists(
                        temp_wav
                    ):

                        os.remove(
                            temp_wav
                        )

                except Exception:
                    pass

            print(
                "[TTS ERROR]",
                error
            )

            return {
                "success": False,
                "error": str(error),
            }

    def worker():

        try:

            log(
                "Playing response..."
            )

            winsound.PlaySound(
                temp_wav,
                winsound.SND_FILENAME,
            )

            log(
                "Playback completed."
            )

        except Exception as error:

            print(
                "[ASYNC TTS ERROR]",
                error
            )

        finally:

            try:

                if os.path.exists(
                    temp_wav
                ):

                    os.remove(
                        temp_wav
                    )

            except Exception:
                pass

    thread = threading.Thread(
        target=worker,
        daemon=True,
    )

    thread.start()

    return {
        "success": True,
        "started": True,
        "offline": True,
        "text": cleaned,
        "duration_ms": duration_ms,
    }


# ============================================================
# TEST
# ============================================================

def test():

    print()
    print(
        "=" * 60
    )
    print(
        "        JARVIS OFFLINE TTS TEST"
    )
    print(
        "=" * 60
    )

    print()

    print(
        "Model:"
    )

    print(
        PIPER_MODEL
    )

    print()

    print(
        "Model exists:",
        model_exists()
    )

    print()

    result = speak(
        "Hello Sir. JARVIS offline voice output is working."
    )

    print()

    print(
        "Result:",
        result
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    test()