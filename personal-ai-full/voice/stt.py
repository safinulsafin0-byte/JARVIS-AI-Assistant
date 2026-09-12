# ============================================================
# JARVIS OFFLINE SPEECH-TO-TEXT
# voice/stt.py
#
# Local microphone + faster-whisper
# No browser SpeechRecognition
# No online speech recognition
# ============================================================

from __future__ import annotations

import os
import tempfile
import wave
from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd

from faster_whisper import WhisperModel


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parent.parent

MODEL_DIR = (
    BASE_DIR
    / "models"
    / "faster-whisper-base"
)


# ============================================================
# CONFIG
# ============================================================

SAMPLE_RATE = 16000
CHANNELS = 1

DEFAULT_LANGUAGE = "en"

DEVICE = os.getenv(
    "JARVIS_WHISPER_DEVICE",
    "cpu"
)

COMPUTE_TYPE = os.getenv(
    "JARVIS_WHISPER_COMPUTE",
    "int8"
)

MODEL_DIR = MODEL_DIR.resolve()


# ============================================================
# GLOBAL MODEL
# ============================================================

_model: Optional[WhisperModel] = None


# ============================================================
# LOGGER
# ============================================================

def log(message: str):
    print(
        f"[JARVIS STT] {message}"
    )


# ============================================================
# MODEL LOADER
# ============================================================

def get_model() -> WhisperModel:

    global _model

    if _model is not None:
        return _model

    if not MODEL_DIR.exists():

        raise FileNotFoundError(
            "Local Whisper model was not found.\n"
            f"Expected model directory:\n"
            f"{MODEL_DIR}\n\n"
            "Download the model once with:\n"
            "python -c "
            "\"from huggingface_hub import snapshot_download; "
            "snapshot_download("
            "repo_id='Systran/faster-whisper-base', "
            f"local_dir=r'{MODEL_DIR}')\""
        )

    log(
        f"Loading local Whisper model: {MODEL_DIR}"
    )

    log(
        f"Device: {DEVICE}"
    )

    log(
        f"Compute type: {COMPUTE_TYPE}"
    )

    try:

        _model = WhisperModel(
            str(MODEL_DIR),
            device=DEVICE,
            compute_type=COMPUTE_TYPE,
        )

    except Exception as first_error:

        # ----------------------------------------------------
        # CUDA fallback
        # ----------------------------------------------------

        if DEVICE.lower() == "cuda":

            log(
                "CUDA Whisper startup failed."
            )

            log(
                "Falling back to CPU/int8."
            )

            try:

                _model = WhisperModel(
                    str(MODEL_DIR),
                    device="cpu",
                    compute_type="int8",
                )

            except Exception as fallback_error:

                raise RuntimeError(
                    "Could not load Whisper model.\n"
                    f"CUDA error: {first_error}\n"
                    f"CPU fallback error: {fallback_error}"
                )

        else:

            raise RuntimeError(
                f"Could not load local Whisper model: "
                f"{first_error}"
            )

    log(
        "Local Whisper model loaded successfully."
    )

    return _model


# ============================================================
# MICROPHONE DEVICES
# ============================================================

def list_input_devices():

    devices = sd.query_devices()

    result = []

    for index, device in enumerate(devices):

        try:

            input_channels = int(
                device.get(
                    "max_input_channels",
                    0
                )
            )

        except Exception:

            input_channels = 0

        if input_channels > 0:

            result.append(
                {
                    "index": index,
                    "name": device.get(
                        "name",
                        f"Input Device {index}"
                    ),
                    "sample_rate":
                        device.get(
                            "default_samplerate",
                            SAMPLE_RATE
                        ),
                }
            )

    return result


# ============================================================
# DEFAULT INPUT DEVICE
# ============================================================

def get_default_input_device():

    try:

        default_devices = (
            sd.default.device
        )

        if (
            isinstance(
                default_devices,
                (list, tuple)
            )
            and len(default_devices) >= 1
        ):

            input_index = (
                default_devices[0]
            )

            if input_index is not None:

                try:

                    input_index = int(
                        input_index
                    )

                    devices = (
                        list_input_devices()
                    )

                    for device in devices:

                        if device["index"] == input_index:

                            return input_index

                except Exception:

                    pass

    except Exception:

        pass

    devices = list_input_devices()

    if not devices:

        raise RuntimeError(
            "No microphone/input device was detected."
        )

    return devices[0]["index"]


# ============================================================
# MICROPHONE TEST
# ============================================================

def test_microphone():

    devices = list_input_devices()

    if not devices:

        raise RuntimeError(
            "No microphone was detected."
        )

    print()
    print(
        "=============================="
    )
    print(
        "JARVIS MICROPHONES"
    )
    print(
        "=============================="
    )

    for device in devices:

        print(
            f"[{device['index']}] "
            f"{device['name']}"
        )

    print()

    return True


# ============================================================
# RECORD MICROPHONE
# ============================================================

def record_microphone(
    duration_sec: float = 5.0,
    sample_rate: int = SAMPLE_RATE,
):

    if duration_sec <= 0:

        raise ValueError(
            "duration_sec must be greater than 0."
        )

    device_index = (
        get_default_input_device()
    )

    log(
        f"Using microphone device: {device_index}"
    )

    log(
        f"Recording for {duration_sec:.1f} seconds..."
    )

    try:

        audio = sd.rec(
            int(
                duration_sec
                * sample_rate
            ),
            samplerate=sample_rate,
            channels=CHANNELS,
            dtype="float32",
            device=device_index,
        )

        sd.wait()

    except Exception as e:

        raise RuntimeError(
            "Microphone recording failed.\n"
            f"{e}"
        )

    if audio is None:

        raise RuntimeError(
            "Microphone returned no audio."
        )

    audio = np.asarray(
        audio,
        dtype=np.float32
    )

    if audio.ndim > 1:

        audio = audio[:, 0]

    if audio.size == 0:

        raise RuntimeError(
            "Recorded audio is empty."
        )

    # --------------------------------------------------------
    # Audio level diagnostic
    # --------------------------------------------------------

    try:

        rms = float(
            np.sqrt(
                np.mean(
                    audio ** 2
                )
            )
        )

    except Exception:

        rms = 0.0

    log(
        f"Audio level: {rms:.6f}"
    )

    if rms < 0.001:

        log(
            "WARNING: Microphone signal is extremely low."
        )

    return audio


# ============================================================
# SAVE WAV
# ============================================================

def save_wav(
    audio,
    sample_rate: int
) -> str:

    fd, path = tempfile.mkstemp(
        prefix="jarvis_stt_",
        suffix=".wav"
    )

    os.close(fd)

    pcm = np.clip(
        audio,
        -1.0,
        1.0
    )

    pcm = (
        pcm * 32767.0
    ).astype(
        np.int16
    )

    try:

        with wave.open(
            path,
            "wb"
        ) as wav:

            wav.setnchannels(
                1
            )

            wav.setsampwidth(
                2
            )

            wav.setframerate(
                sample_rate
            )

            wav.writeframes(
                pcm.tobytes()
            )

    except Exception:

        try:
            os.remove(path)
        except Exception:
            pass

        raise

    return path


# ============================================================
# TRANSCRIBE FILE
# ============================================================

def transcribe_file(
    audio_path,
    language: str = DEFAULT_LANGUAGE
):

    model = get_model()

    log(
        "Transcribing locally..."
    )

    try:

        segments, info = model.transcribe(
            str(audio_path),

            language=language,

            task="transcribe",

            beam_size=5,

            best_of=5,

            temperature=0.0,

            condition_on_previous_text=False,

            vad_filter=True,

            vad_parameters={
                "min_silence_duration_ms": 500,
            },
        )

        parts = []

        for segment in segments:

            text = str(
                segment.text or ""
            ).strip()

            if text:

                parts.append(
                    text
                )

        result = " ".join(
            parts
        ).strip()

        log(
            f"Recognized: {result}"
        )

        return result

    except Exception as e:

        raise RuntimeError(
            f"Whisper transcription failed: {e}"
        )


# ============================================================
# PUBLIC FILE API
# ============================================================

def transcribe_audio_file(
    file_path,
    language: str = DEFAULT_LANGUAGE
):

    return transcribe_file(
        file_path,
        language=language
    )


# ============================================================
# PUBLIC MICROPHONE API
# ============================================================

def listen_once(
    duration_sec: float = 5.0,
    sample_rate: int = SAMPLE_RATE,
    language: str = DEFAULT_LANGUAGE,
):

    temporary_wav = None

    try:

        audio = record_microphone(
            duration_sec=duration_sec,
            sample_rate=sample_rate
        )

        temporary_wav = save_wav(
            audio,
            sample_rate
        )

        return transcribe_file(
            temporary_wav,
            language=language
        )

    except KeyboardInterrupt:

        log(
            "Voice recording interrupted."
        )

        return ""

    except Exception as e:

        print(
            f"[JARVIS STT ERROR] {e}"
        )

        return ""

    finally:

        if temporary_wav:

            try:

                os.remove(
                    temporary_wav
                )

            except Exception:

                pass


# ============================================================
# STANDALONE TEST
# ============================================================

def main():

    print()
    print(
        "============================================"
    )
    print(
        "       JARVIS OFFLINE STT TEST"
    )
    print(
        "============================================"
    )
    print()

    try:

        test_microphone()

        print(
            f"Model: {MODEL_DIR}"
        )

        print(
            "Starting microphone test..."
        )

        print()

        text = listen_once(
            duration_sec=5,
            sample_rate=16000,
            language="en"
        )

        print()

        print(
            "--------------------------------------------"
        )

        print(
            "TRANSCRIPTION:"
        )

        print(
            text or "(nothing detected)"
        )

        print(
            "--------------------------------------------"
        )

    except Exception as e:

        print()
        print(
            "STT TEST FAILED:"
        )
        print(
            e
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()