# ============================================================
# JARVIS LOCAL AI - FASTAPI SERVER
#
# Features:
# - JARVIS chat
# - Confirmation forwarding
# - Offline speech transcription
# - Static UI
# ============================================================

from pathlib import Path
import os
import tempfile
import traceback

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
)

from fastapi.responses import FileResponse

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from main import handle_user_input

from voice.stt import transcribe_audio_file


# ============================================================
# PATHS
# ============================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent.parent
)

# Your actual frontend from the project search:
WEB_DIR = (
    BASE_DIR
    / "web"
)

INDEX_FILE = (
    WEB_DIR
    / "index.html"
)

APP_JS_FILE = (
    WEB_DIR
    / "app.js"
)

STYLE_FILE = (
    WEB_DIR
    / "style.css"
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="JARVIS Local AI",
    version="2.0.0",
    description="JARVIS Local AI with Offline Whisper STT",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class Chat(BaseModel):

    message: str

    confirmed: bool = False


# ============================================================
# FRONTEND
# ============================================================

@app.get("/")
def index():

    if not INDEX_FILE.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "Frontend not found: "
                f"{INDEX_FILE}"
            ),
        )

    return FileResponse(
        str(INDEX_FILE)
    )


# ============================================================
# FRONTEND STATIC FILES
# ============================================================

@app.get("/app.js")
def app_js():

    if not APP_JS_FILE.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "app.js not found: "
                f"{APP_JS_FILE}"
            ),
        )

    return FileResponse(
        str(APP_JS_FILE),
        media_type="application/javascript",
    )


@app.get("/style.css")
def style_css():

    if not STYLE_FILE.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "style.css not found: "
                f"{STYLE_FILE}"
            ),
        )

    return FileResponse(
        str(STYLE_FILE),
        media_type="text/css",
    )


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health():

    return {
        "success": True,
        "status": "online",
        "service": "JARVIS Local AI",
        "offline_stt": True,
    }


# ============================================================
# STATUS
# ============================================================

@app.get("/api/status")
def status():

    model_path = (
        BASE_DIR
        / "models"
        / "faster-whisper-base"
    )

    return {
        "success": True,
        "online": True,
        "assistant": "JARVIS",
        "offline_stt": True,
        "whisper_model_exists":
            model_path.exists(),
        "whisper_model":
            str(model_path),
    }


# ============================================================
# CHAT
#
# Main frontend endpoint:
# /api/chat
# ============================================================

@app.post("/api/chat")
def api_chat(body: Chat):

    try:

        message = str(
            body.message or ""
        ).strip()

        if not message:

            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty.",
            )

        reply = handle_user_input(
            message,
            body.confirmed,
        )

        return {
            "success": True,
            "reply": str(
                reply or ""
            ),
        }

    except HTTPException:
        raise

    except Exception as e:

        traceback.print_exc()

        return {
            "success": False,
            "error": str(e),
            "reply":
                f"ERROR: {e}",
        }


# ============================================================
# LEGACY CHAT ENDPOINT
#
# Keeps the old /chat endpoint working.
# ============================================================

@app.post("/chat")
def chat(body: Chat):

    return api_chat(body)


# ============================================================
# OFFLINE TRANSCRIPTION
#
# Browser records audio.
# This endpoint sends it to local faster-whisper.
# ============================================================

@app.post("/api/transcribe")
async def transcribe_endpoint(
    file: UploadFile = File(...)
):

    temporary_path = None

    try:

        if not file.filename:

            raise HTTPException(
                status_code=400,
                detail="Audio file is missing.",
            )

        original_name = (
            file.filename
            or "voice.webm"
        )

        suffix = (
            Path(
                original_name
            ).suffix.lower()
        )

        allowed_audio = {
            ".webm",
            ".wav",
            ".ogg",
            ".m4a",
            ".mp3",
            ".mp4",
        }

        if suffix not in allowed_audio:

            suffix = ".webm"

        fd, temporary_path = (
            tempfile.mkstemp(
                prefix="jarvis_voice_",
                suffix=suffix,
            )
        )

        os.close(fd)

        with open(
            temporary_path,
            "wb"
        ) as output:

            while True:

                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                output.write(
                    chunk
                )

        if (
            not os.path.exists(
                temporary_path
            )
            or os.path.getsize(
                temporary_path
            ) == 0
        ):

            raise HTTPException(
                status_code=400,
                detail="Uploaded audio is empty.",
            )

        text = transcribe_audio_file(
            temporary_path,
            language="en",
        )

        text = str(
            text or ""
        ).strip()

        return {
            "success": True,
            "text": text,
        }

    except HTTPException:
        raise

    except Exception as e:

        traceback.print_exc()

        return {
            "success": False,
            "text": "",
            "error": str(e),
        }

    finally:

        if temporary_path:

            try:

                os.remove(
                    temporary_path
                )

            except Exception:

                pass


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    print()
    print(
        "=" * 60
    )
    print(
        "        JARVIS LOCAL AI SERVER"
    )
    print(
        "        OFFLINE WHISPER STT"
    )
    print(
        "=" * 60
    )
    print()

    print(
        f"Project: {BASE_DIR}"
    )

    print(
        f"Frontend: {INDEX_FILE}"
    )

    print(
        f"Frontend exists: "
        f"{INDEX_FILE.exists()}"
    )

    print()

    print(
        "JARVIS UI:"
    )

    print(
        "http://127.0.0.1:8000/"
    )

    print()

    print(
        "Chat API:"
    )

    print(
        "http://127.0.0.1:8000/api/chat"
    )

    print()

    print(
        "Offline STT:"
    )

    print(
        "http://127.0.0.1:8000/api/transcribe"
    )

    print()

    uvicorn.run(
        "ui.server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )