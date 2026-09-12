# ============================================================
# JARVIS LOCAL AI SERVER — BEASTMODE MULTIMODAL
#
# Flask UI + Chat API + File Uploads + Vision + Documents
# + Persistent Multimodal Memory + Coding Expert
# + OFFLINE SPEECH-TO-TEXT
# + GESTURE CONTROL (Tony Stark hologram commands)
#
# FILE:
# D:\personal-ai-full\api_server.py
# ============================================================

from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
)

from flask_cors import CORS

from pathlib import Path
from coding_engine.jarvis_swe_agent_v83 import run_swe_agent
from coding_engine.reasoning_engine_v82 import reason_about_change
from werkzeug.utils import secure_filename
from voice.tts import speak_async, stop as stop_tts
import csv
import json
import traceback
import uuid
import os
import tempfile
import time


# ============================================================
# JARVIS CORE
# ============================================================

from main import handle_user_input


# ============================================================
# MEMORY
# ============================================================

try:

    from memory.memory_manager import (
        remember,
        build_context,
    )

    MEMORY_AVAILABLE = True
    MEMORY_IMPORT_ERROR = ""

except Exception as memory_error:

    MEMORY_AVAILABLE = False
    MEMORY_IMPORT_ERROR = str(
        memory_error
    )

    def remember(*args, **kwargs):
        return None

    def build_context(*args, **kwargs):
        return ""


# ============================================================
# OFFLINE SPEECH-TO-TEXT
# ============================================================

try:

    from voice.stt import (
        transcribe_audio_file,
    )

    OFFLINE_STT_AVAILABLE = True
    OFFLINE_STT_IMPORT_ERROR = ""

except Exception as stt_error:

    OFFLINE_STT_AVAILABLE = False
    OFFLINE_STT_IMPORT_ERROR = str(
        stt_error
    )

    def transcribe_audio_file(
        file_path,
        language="en"
    ):

        raise RuntimeError(
            "Offline STT is unavailable: "
            + OFFLINE_STT_IMPORT_ERROR
        )


# ============================================================
# OPTIONAL DOCUMENT LIBRARIES
# ============================================================

try:

    import fitz

    PYMUPDF_AVAILABLE = True

except ImportError:

    fitz = None
    PYMUPDF_AVAILABLE = False


# ============================================================

try:

    from pypdf import PdfReader

    PYPDF_AVAILABLE = True

except ImportError:

    PdfReader = None
    PYPDF_AVAILABLE = False


# ============================================================

try:

    from docx import Document

    DOCX_AVAILABLE = True

except ImportError:

    Document = None
    DOCX_AVAILABLE = False


# ============================================================

try:

    from openpyxl import load_workbook

    XLSX_AVAILABLE = True

except ImportError:

    load_workbook = None
    XLSX_AVAILABLE = False


# ============================================================

try:

    from pptx import Presentation

    PPTX_AVAILABLE = True

except ImportError:

    Presentation = None
    PPTX_AVAILABLE = False


# ============================================================
# OPTIONAL VISION
# ============================================================

try:

    from vision.image_analyzer import (
        analyze_image,
        describe_image,
        read_image_text,
        explain_diagram,
        analyze_image_problem,
    )

    VISION_AVAILABLE = True
    VISION_IMPORT_ERROR = ""

except Exception as vision_error:

    VISION_AVAILABLE = False

    analyze_image = None
    describe_image = None
    read_image_text = None
    explain_diagram = None
    analyze_image_problem = None

    VISION_IMPORT_ERROR = str(
        vision_error
    )


# ============================================================
# OPTIONAL CODING EXPERT
# ============================================================

try:

    from coding_engine.coding_expert import (
        CodingExpert
    )

    CODING_EXPERT_AVAILABLE = True
    CODING_EXPERT_IMPORT_ERROR = ""

except Exception as coding_error:

    CodingExpert = None

    CODING_EXPERT_AVAILABLE = False

    CODING_EXPERT_IMPORT_ERROR = str(
        coding_error
    )


# ============================================================
# PATHS
# ============================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
)


# ============================================================
# WEB FRONTEND
# ============================================================

WEB_DIR = (
    BASE_DIR
    / "web"
)

INDEX_FILE = (
    WEB_DIR
    / "index.html"
)


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = (
    BASE_DIR
    / "uploads"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LIMITS
# ============================================================

MAX_UPLOAD_BYTES = (
    25 * 1024 * 1024
)

MAX_EXTRACTED_CHARS = 60000


# ============================================================
# DOCUMENT EXTENSIONS
# ============================================================

ALLOWED_DOCUMENT_EXTENSIONS = {

    ".txt",
    ".md",
    ".csv",
    ".json",
    ".pdf",
    ".docx",
    ".xlsx",
    ".pptx",
}


# ============================================================
# IMAGE EXTENSIONS
# ============================================================

ALLOWED_IMAGE_EXTENSIONS = {

    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".gif",
}


# ============================================================
# AUDIO EXTENSIONS
# ============================================================

ALLOWED_AUDIO_EXTENSIONS = {

    ".webm",
    ".wav",
    ".ogg",
    ".m4a",
    ".mp3",
    ".mp4",
}


# ============================================================
# GESTURE CONTROL STATE
#
# MediaPipe Hands (frontend) detects a gesture name and POSTs
# it to /api/gesture. This backend only maps a gesture name to
# a JARVIS voice-style command and dispatches it through
# handle_user_input(). It NEVER handles raw hand movement,
# rotation, drag, or zoom — that stays in the browser's
# Three.js / hologram.js layer.
# ============================================================

GESTURE_ENABLED = True

# ============================================================
# JARVIS HOLOGRAM WORKSPACE CONTROL
# Particle + Line Drawing Mode
# ============================================================

HOLOGRAM_STATE = {
    "active": False,
    "mode": "none",
    "last_action": ""
}


def detect_hologram_command(text):

    text = str(text or "").lower()

    if (
        "start gesture" in text
        or "open hologram" in text
        or "hologram workspace" in text
    ):
        return {
            "action": "open",
            "mode": "none"
        }

    if "particle" in text or "particles" in text:
        return {
            "action": "open",
            "mode": "particles"
        }

    if (
        "line" in text
        or "lines" in text
        or "drawing" in text
        or "draw" in text
    ):
        return {
            "action": "open",
            "mode": "lines"
        }

    if "clear" in text:
        return {
            "action": "clear",
            "mode": HOLOGRAM_STATE["mode"]
        }

    return None


def update_hologram_state(action, mode="none"):

    HOLOGRAM_STATE["active"] = True
    HOLOGRAM_STATE["mode"] = mode
    HOLOGRAM_STATE["last_action"] = action

    return HOLOGRAM_STATE



LAST_GESTURE = {
    "name": "",
    "time": 0.0,
}


GESTURE_COOLDOWN = 1.5


# ============================================================
# GESTURE -> JARVIS COMMAND MAPPING
# ============================================================

GESTURE_COMMANDS = {

    "open_palm":
        "Open JARVIS holographic menu",

    "pinch":
        "Select hologram object",

    "fist":
        "Stop current operation",

    "thumb_up":
        "Confirm action",

    "thumb_down":
        "Reject action",

    "point":
        "Enable hologram pointer",

    "zoom":
        "Zoom hologram model",

    "clear":
        "Clear hologram workspace",

    "draw":
        "Enable hologram drawing",

}


# ============================================================
# FLASK
# ============================================================

app = Flask(
    __name__
)

# ============================================================
# OFFLINE TTS
# ============================================================

@app.route("/api/speak", methods=["POST"])
def speak_api():
    try:
        data = request.get_json(silent=True) or {}

        text = str(
            data.get("text", "")
        ).strip()

        if not text:
            return jsonify({
                "success": False,
                "error": "Text to speak is empty."
            }), 400

        result = speak_async(text)

        if not result.get("success", False):
            return jsonify(result), 500

        return jsonify(result)

    except Exception as error:
        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# STOP OFFLINE TTS
# ============================================================

@app.route("/api/speak/stop", methods=["POST"])
def stop_speak_api():
    try:
        stop_tts()

        return jsonify({
            "success": True
        })

    except Exception as error:
        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500
# ============================================================
# CORS
# ============================================================

CORS(
    app
)


# ============================================================
# FLASK CONFIG
# ============================================================

app.config[
    "MAX_CONTENT_LENGTH"
] = MAX_UPLOAD_BYTES


# ============================================================
# HELPERS
# ============================================================

def ext_of(filename):

    return (
        Path(
            filename or ""
        )
        .suffix
        .lower()
    )


# ============================================================

def safe_uploaded_name(filename):

    name = secure_filename(
        filename
        or "attachment"
    )

    return (
        name
        or (
            "attachment_"
            + uuid.uuid4().hex[:8]
        )
    )


# ============================================================
# MEMORY HELPER
# ============================================================

def remember_multimodal(
    user_message,
    assistant_result,
    attachment_name=None,
    attachment_type=None,
):
    """
    Persist multimodal interaction.

    The temporary uploaded file path itself is not stored.
    """

    try:

        if not MEMORY_AVAILABLE:
            return

        user_message = str(
            user_message
            or ""
        ).strip()

        assistant_result = str(
            assistant_result
            or ""
        ).strip()

        if not assistant_result:
            return

        if attachment_name:

            memory_user_message = (

                "[MULTIMODAL ATTACHMENT]\n"

                f"File: "
                f"{attachment_name}\n"

                f"Type: "
                f"{attachment_type or 'unknown'}\n"

                f"User request: "
                f"{user_message or 'Analyze this attachment.'}"
            )

        else:

            memory_user_message = (
                user_message
            )

        remember(
            memory_user_message,
            assistant_result
        )

    except Exception as error:

        print(
            "[MULTIMODAL MEMORY WARNING]",
            error
        )


# ============================================================
# TEXT FILE
# ============================================================

def read_text_file(path):

    encodings = (
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin-1",
    )
    for encoding in encodings:

        try:

            return path.read_text(
                encoding=encoding
            )

        except UnicodeDecodeError:

            continue

    raise ValueError(
        f"Could not decode text file: "
        f"{path.name}"
    )


# ============================================================
# CSV FILE
# ============================================================

def read_csv_file(path):

    encodings = (
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin-1",
    )

    for encoding in encodings:

        try:

            with path.open(
                "r",
                encoding=encoding,
                newline="",
            ) as file:

                rows = []

                for row in csv.reader(file):

                    rows.append(
                        " | ".join(
                            str(value)
                            for value in row
                        )
                    )

                return "\n".join(
                    rows
                )

        except UnicodeDecodeError:

            continue

    raise ValueError(
        f"Could not decode CSV file: "
        f"{path.name}"
    )


# ============================================================
# JSON FILE
# ============================================================

def read_json_file(path):

    raw = read_text_file(
        path
    )

    try:

        parsed = json.loads(
            raw
        )

        return json.dumps(
            parsed,
            ensure_ascii=False,
            indent=2,
        )

    except json.JSONDecodeError:

        return raw


# ============================================================
# PDF FILE
# ============================================================

def read_pdf_file(path):

    errors = []

    # --------------------------------------------------------
    # PyMuPDF
    # --------------------------------------------------------

    if PYMUPDF_AVAILABLE:

        try:

            document = fitz.open(
                str(path)
            )

            try:

                chunks = []

                for page_number, page in enumerate(
                    document,
                    1,
                ):

                    text = (
                        page.get_text(
                            "text"
                        )
                        or ""
                    ).strip()

                    if text:

                        chunks.append(
                            f"\n--- Page "
                            f"{page_number} ---\n"
                            f"{text}"
                        )

                result = "\n".join(
                    chunks
                )

                if result.strip():

                    return result

            finally:

                document.close()

        except Exception as error:

            errors.append(
                f"PyMuPDF: {error}"
            )

    # --------------------------------------------------------
    # pypdf fallback
    # --------------------------------------------------------

    if PYPDF_AVAILABLE:

        try:

            reader = PdfReader(
                str(path)
            )

            chunks = []

            for page_number, page in enumerate(
                reader.pages,
                1,
            ):

                try:

                    text = (
                        page.extract_text()
                        or ""
                    ).strip()

                except Exception as error:

                    text = (
                        f"[Page "
                        f"{page_number} "
                        f"read error: "
                        f"{error}]"
                    )

                if text:

                    chunks.append(
                        f"\n--- Page "
                        f"{page_number} ---\n"
                        f"{text}"
                    )

            result = "\n".join(
                chunks
            )

            if result.strip():

                return result

        except Exception as error:

            errors.append(
                f"pypdf: {error}"
            )

    if (
        not PYMUPDF_AVAILABLE
        and not PYPDF_AVAILABLE
    ):

        raise RuntimeError(
            "PDF support is unavailable. "
            "Install with:\n"
            "pip install pymupdf pypdf"
        )

    raise RuntimeError(
        "PDF text extraction failed. "
        + " | ".join(errors)
    )


# ============================================================
# DOCX
# ============================================================

def read_docx_file(path):

    if not DOCX_AVAILABLE:

        raise RuntimeError(
            "DOCX support is unavailable. "
            "Install with:\n"
            "pip install python-docx"
        )

    document = Document(
        str(path)
    )

    parts = []

    # --------------------------------------------------------
    # Paragraphs
    # --------------------------------------------------------

    for paragraph in document.paragraphs:

        text = (
            paragraph.text
            or ""
        ).strip()

        if text:

            parts.append(
                text
            )

    # --------------------------------------------------------
    # Tables
    # --------------------------------------------------------

    for table_number, table in enumerate(
        document.tables,
        1,
    ):

        parts.append(
            f"\n--- Table "
            f"{table_number} ---"
        )

        for row in table.rows:

            values = [
                cell.text.strip()
                for cell in row.cells
            ]

            parts.append(
                " | ".join(
                    values
                )
            )

    return "\n".join(
        parts
    )


# ============================================================
# XLSX
# ============================================================

def read_xlsx_file(path):

    if not XLSX_AVAILABLE:

        raise RuntimeError(
            "XLSX support is unavailable. "
            "Install with:\n"
            "pip install openpyxl"
        )

    workbook = load_workbook(
        str(path),
        read_only=True,
        data_only=True,
    )

    parts = []

    try:

        for worksheet in workbook.worksheets:

            parts.append(
                f"\n--- Sheet: "
                f"{worksheet.title} ---"
            )

            for row in worksheet.iter_rows(
                values_only=True
            ):

                values = [
                    ""
                    if value is None
                    else str(value)
                    for value in row
                ]

                if any(
                    value.strip()
                    for value in values
                ):

                    parts.append(
                        " | ".join(
                            values
                        )
                    )

    finally:

        workbook.close()

    return "\n".join(
        parts
    )


# ============================================================
# PPTX
# ============================================================

def read_pptx_file(path):

    if not PPTX_AVAILABLE:

        raise RuntimeError(
            "PPTX support is unavailable. "
            "Install with:\n"
            "pip install python-pptx"
        )

    presentation = Presentation(
        str(path)
    )

    parts = []

    for slide_number, slide in enumerate(
        presentation.slides,
        1,
    ):

        slide_parts = []

        for shape in slide.shapes:

            if hasattr(
                shape,
                "text"
            ):

                text = (
                    shape.text
                    or ""
                ).strip()

                if text:

                    slide_parts.append(
                        text
                    )

        if slide_parts:

            parts.append(
                f"\n--- Slide "
                f"{slide_number} ---\n"
                + "\n".join(
                    slide_parts
                )
            )

    return "\n".join(
        parts
    )


# ============================================================
# DOCUMENT ROUTER
# ============================================================

def extract_document(path):

    extension = ext_of(
        path.name
    )

    # --------------------------------------------------------
    # Text
    # --------------------------------------------------------

    if extension in {
        ".txt",
        ".md",
    }:

        return read_text_file(
            path
        )

    # --------------------------------------------------------
    # CSV
    # --------------------------------------------------------

    if extension == ".csv":

        return read_csv_file(
            path
        )

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    if extension == ".json":

        return read_json_file(
            path
        )

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    if extension == ".pdf":

        return read_pdf_file(
            path
        )

    # --------------------------------------------------------
    # DOCX
    # --------------------------------------------------------

    if extension == ".docx":

        return read_docx_file(
            path
        )

    # --------------------------------------------------------
    # XLSX
    # --------------------------------------------------------

    if extension == ".xlsx":

        return read_xlsx_file(
            path
        )

    # --------------------------------------------------------
    # PPTX
    # --------------------------------------------------------

    if extension == ".pptx":

        return read_pptx_file(
            path
        )

    raise ValueError(
        f"Unsupported document type: "
        f"{extension}"
    )


# ============================================================
# LIMIT DOCUMENT TEXT
# ============================================================

def limit_text(text):

    text = str(
        text or ""
    ).strip()

    if len(text) <= MAX_EXTRACTED_CHARS:

        return text

    return (
        text[
            :MAX_EXTRACTED_CHARS
        ]
        + "\n\n"
        "[SYSTEM NOTE: document "
        "truncated to context limit.]"
    )


# ============================================================
# CODING DETECTION
# ============================================================

def is_coding_problem(text):

    text = str(
        text or ""
    ).lower()

    explicit = (

        "solve in c++",

        "solve using c++",

        "give c++ code",

        "give me c++ code",

        "provide c++ code",

        "write c++ code",

        "cpp solution",

        "c++ solution",
    )

    if any(
        phrase in text
        for phrase in explicit
    ):

        return True

    strong = (

        "input:",

        "output:",

        "constraints:",

        "sample input",

        "sample output",

        "write a program",

        "write code",

        "solve this problem",

        "competitive programming",

        "stdin",

        "stdout",

        "time limit",

        "memory limit",
    )

    indicators = (

        "c++",

        "cpp",

        "array",

        "string",

        "integer",

        "vector",

        "graph",

        "tree",

        "sorting",

        "binary search",

        "dynamic programming",

        "dijkstra",

        "linked list",

        "stack",

        "queue",

        "heap",

        "recursion",

        "matrix",

        "substring",

        "subarray",
    )

    strong_hits = sum(
        phrase in text
        for phrase in strong
    )

    has_input_output = (
        "input" in text
        and "output" in text
    )

    has_indicator = any(
        phrase in text
        for phrase in indicators
    )

    return (
        strong_hits >= 2
        or (
            has_input_output
            and has_indicator
        )
    )


# ============================================================
# CODING EXPERT INSTANCE
# ============================================================

coding_expert = None

if CODING_EXPERT_AVAILABLE:

    try:

        coding_expert = CodingExpert(
            lambda prompt:
                handle_user_input(
                    prompt,
                    False,
                )
        )

    except Exception as error:

        CODING_EXPERT_AVAILABLE = False

        CODING_EXPERT_IMPORT_ERROR = str(
            error
        )


# ============================================================
# RUN CODING EXPERT
# ============================================================

def run_coding_expert(problem):

    if coding_expert is None:

        return {

            "success": False,

            "verified": False,

            "stage": "coding",

            "attempts": 0,

            "error":
                "Coding Expert is not available.",
        }

    try:

        return coding_expert.solve(
            problem
        )

    except Exception as error:

        traceback.print_exc()

        return {

            "success": False,

            "verified": False,

            "stage": "coding",

            "attempts": 0,

            "error": str(
                error
            ),
        }


# ============================================================
# FORMAT CODING RESULT
# ============================================================

def format_coding_result(result):

    result = result or {}

    success = bool(
        result.get(
            "success",
            False
        )
    )

    verified = bool(
        result.get(
            "verified",
            False
        )
    )

    code = str(
        result.get(
            "code",
            ""
        )
        or ""
    )

    attempts = result.get(
        "attempts",
        1
    )

    stage = result.get(
        "stage",
        "unknown"
    )

    if success and verified:

        tests = result.get(
            "tests",
            []
        )

        passed = sum(
            1
            for test in tests
            if test.get(
                "passed",
                False
            )
        )

        return (
            "## JARVIS Coding Expert\n\n"

            "### Verification: PASSED\n\n"

            f"All detected sample tests passed "
            f"({passed}/{len(tests)}).\n\n"

            f"Attempts: {attempts}\n\n"

            "### C++17 Solution\n\n"

            f"```cpp\n"
            f"{code}\n"
            f"```\n"
        )

    if success:

        return (
            "## JARVIS Coding Expert\n\n"

            "### Compilation: PASSED\n\n"

            "The solution compiled successfully, "
            "but sample verification was unavailable.\n\n"

            f"Attempts: {attempts}\n\n"

            f"```cpp\n"
            f"{code}\n"
            f"```\n"
        )

    error_message = str(
        result.get(
            "error",
            "Unknown error."
        )
    )

    return (
        "## JARVIS Coding Expert failed\n\n"

        f"Stage: `{stage}`\n\n"

        f"Attempts: {attempts}\n\n"

        f"```text\n"
        f"{error_message}\n"
        f"```\n"

        + (
            "\n### Generated Code\n\n"
            f"```cpp\n"
            f"{code}\n"
            f"```\n"
            if code
            else ""
        )
    )


# ============================================================
# VISION
# ============================================================

def run_vision(
    path,
    instruction,
):

    if not VISION_AVAILABLE:

        return (
            "ERROR: Vision module is unavailable.\n"
            f"Import error: "
            f"{VISION_IMPORT_ERROR}"
        )

    text = str(
        instruction or ""
    ).lower()

    try:

        # ----------------------------------------------------
        # OCR
        # ----------------------------------------------------

        if any(
            word in text
            for word in (
                "ocr",
                "read text",
                "extract text",
                "read image text",
            )
        ):

            return str(
                read_image_text(
                    str(path)
                )
            )

        # ----------------------------------------------------
        # Diagram
        # ----------------------------------------------------

        if any(
            word in text
            for word in (
                "diagram",
                "flowchart",
                "flow chart",
            )
        ):

            return str(
                explain_diagram(
                    str(path)
                )
            )

        # ----------------------------------------------------
        # Image problems
        # ----------------------------------------------------

        if any(
            word in text
            for word in (
                "find errors",
                "find problems",
                "image problems",
                "image errors",
                "check image",
            )
        ):

            return str(
                analyze_image_problem(
                    str(path)
                )
            )

        # ----------------------------------------------------
        # Analyze
        # ----------------------------------------------------

        if any(
            word in text
            for word in (
                "analyze",
                "analyse",
            )
        ):

            return str(
                analyze_image(
                    str(path)
                )
            )

        # ----------------------------------------------------
        # Default description
        # ----------------------------------------------------

        return str(
            describe_image(
                str(path)
            )
        )

    except Exception as error:

        traceback.print_exc()

        return (
            f"ERROR: Vision analysis failed: "
            f"{error}"
        )


# ============================================================
# GESTURE CONTROL
#
# Only discrete, symbolic hand-poses (open_palm, pinch, fist,
# thumb_up, thumb_down, point, zoom) come here. Continuous hand
# movement — rotate / drag / zoom-by-distance / 3D manipulation
# of a hologram — is handled entirely in the browser's
# Three.js / hologram.js layer and never touches this backend.
# ============================================================

def process_gesture_command(gesture):

    gesture = str(
        gesture or ""
    ).lower().strip()

    # ----------------------------------------------------
    # Master switch
    # ----------------------------------------------------

    if not GESTURE_ENABLED:

        return {

            "success": False,

            "error":
                "Gesture control is disabled.",
        }

    # ----------------------------------------------------
    # Unknown gesture
    # ----------------------------------------------------

    if gesture not in GESTURE_COMMANDS:

        return {

            "success": False,

            "error": "Unknown gesture",
        }

    # ----------------------------------------------------
    # Cooldown — same gesture spamming is ignored so a
    # held pose doesn't fire the same command 10x/sec
    # ----------------------------------------------------

    now = time.time()

    if (
        gesture == LAST_GESTURE["name"]
        and (
            now
            - LAST_GESTURE["time"]
        )
        < GESTURE_COOLDOWN
    ):

        return {

            "success": False,

            "gesture": gesture,

            "cooldown": True,

            "error":
                "Gesture ignored: cooldown active.",
        }

    LAST_GESTURE["name"] = gesture

    LAST_GESTURE["time"] = now

    # ----------------------------------------------------
    # Translate gesture -> JARVIS command -> response
    # ----------------------------------------------------

    command = GESTURE_COMMANDS[gesture]

    response = handle_user_input(
        command,
        True,
    )

    return {

        "success": True,

        "gesture": gesture,

        "command": command,

        "response": response,
    }


# ============================================================
# HOME
# ============================================================

@app.route(
    "/",
    methods=["GET"]
)
def home():

    if not INDEX_FILE.exists():

        return jsonify({

            "success": False,

            "online": True,

            "assistant": "JARVIS",

            "error":
                "index.html was not found.",

            "expected_path":
                str(INDEX_FILE),

        }), 404

    return send_from_directory(
        str(WEB_DIR),
        "index.html"
    )


# ============================================================
# FRONTEND CSS
# ============================================================

@app.route(
    "/style.css",
    methods=["GET"]
)
def serve_style():

    return send_from_directory(
        str(WEB_DIR),
        "style.css"
    )


# ============================================================
# FRONTEND JS
# ============================================================

@app.route(
    "/app.js",
    methods=["GET"]
)
def serve_app_js():

    return send_from_directory(
        str(WEB_DIR),
        "app.js"
    )


# ============================================================
# OTHER WEB FILES
# ============================================================

@app.route(
    "/web/<path:filename>",
    methods=["GET"]
)
def serve_web_file(filename):

    return send_from_directory(
        str(WEB_DIR),
        filename
    )


# ============================================================
# STATUS
# ============================================================

@app.route(
    "/api/status",
    methods=["GET"]
)
def status():

    return jsonify({

        "success":
            True,

        "online":
            True,

        "assistant":
            "JARVIS",

        "memory":
            MEMORY_AVAILABLE,

        "memory_error":
            (
                MEMORY_IMPORT_ERROR
                if not MEMORY_AVAILABLE
                else ""
            ),

        "vision":
            VISION_AVAILABLE,

        "pdf_reader":
            (
                PYMUPDF_AVAILABLE
                or PYPDF_AVAILABLE
            ),

        "docx_reader":
            DOCX_AVAILABLE,

        "xlsx_reader":
            XLSX_AVAILABLE,

        "pptx_reader":
            PPTX_AVAILABLE,

        "coding_expert":
            CODING_EXPERT_AVAILABLE,

        "offline_stt":
            OFFLINE_STT_AVAILABLE,

        "offline_stt_error":
            (
                OFFLINE_STT_IMPORT_ERROR
                if not OFFLINE_STT_AVAILABLE
                else ""
            ),

        "gesture_control":
            GESTURE_ENABLED,

    })


# ============================================================
# OFFLINE VOICE TRANSCRIPTION
#
# IMPORTANT:
#
# frontend:
#     POST /api/transcribe
#
# field:
#     file
#
# then:
#     local faster-whisper
#
# no online SpeechRecognition
# ============================================================

@app.route(
    "/api/transcribe",
    methods=["POST"]
)
def transcribe_api():

    temp_path = None

    try:

        audio_file = request.files.get("file")

        if not audio_file:

            return jsonify({
                "success": False,
                "text": "",
                "error": "Audio file is required."
            }), 400


        original_name = (
            audio_file.filename
            or
            "jarvis_voice.webm"
        )


        suffix = ext_of(
            original_name
        )


        if suffix not in ALLOWED_AUDIO_EXTENSIONS:

            suffix = ".webm"



        fd, temp_path = tempfile.mkstemp(
            prefix="jarvis_voice_",
            suffix=suffix
        )


        os.close(fd)


        audio_file.save(
            temp_path
        )


        file_size = os.path.getsize(
            temp_path
        )


        print()
        print(
            "[OFFLINE STT]"
        )

        print(
            f"Received: {original_name}"
        )

        print(
            f"Format: {suffix}"
        )

        print(
            f"Size: {file_size} bytes"
        )


        print(
            "[JARVIS STT] Transcribing locally..."
        )


        text = transcribe_audio_file(
            temp_path,
            language="en"
        )


        text = str(
            text or ""
        ).strip()


        print(
            f"[JARVIS STT] Recognized: {text}"
        )


        if not text:

            return jsonify({

                "success": False,

                "text": "",

                "error": "No speech detected"

            }), 200



        return jsonify({

            "success": True,

            "text": text,

            "offline": True

        })


    except Exception as error:

        traceback.print_exc()

        return jsonify({

            "success": False,

            "text": "",

            "offline": True,

            "error": str(error)

        }), 500


    finally:

        if temp_path:

            try:

                if os.path.exists(temp_path):

                    os.remove(
                        temp_path
                    )

            except Exception as cleanup_error:

                print(
                    "[STT CLEANUP WARNING]",
                    cleanup_error
                )


# ============================================================
# GESTURE API
#
# frontend:
#     POST /api/gesture
#     { "gesture": "pinch" }
#
# then:
#     GESTURE_COMMANDS lookup
#     -> handle_user_input()
#     -> JARVIS response
#
# Hand movement / rotate / drag / zoom stays in Three.js on
# the frontend — only discrete gesture NAMES land here.
# ============================================================

@app.route(
    "/api/gesture",
    methods=["POST"]
)
def gesture_api():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        gesture = data.get(
            "gesture"
        )

        if not gesture:

            return jsonify({

                "success": False,

                "error":
                    "Gesture name is required.",

            }), 400

        result = process_gesture_command(
            gesture
        )

        status_code = (
            200
            if result.get(
                "success",
                False
            )
            else 400
        )

        return jsonify(result), status_code

    except Exception as error:

        traceback.print_exc()

        return jsonify({

            "success": False,

            "error": str(error),

        }), 500



# ============================================================
# HOLOGRAM API
# ============================================================

@app.route(
    "/api/hologram",
    methods=["POST"]
)
def hologram_api():

    try:

        data = request.get_json(silent=True) or {}

        mode = str(
            data.get("mode", "")
        ).lower()


        if mode in ["particles", "lines"]:

            state = update_hologram_state(
                "open",
                mode
            )

            return jsonify({
                "success": True,
                "hologram": True,
                "state": state
            })


        if mode == "clear":

            HOLOGRAM_STATE["last_action"] = "clear"

            return jsonify({
                "success": True,
                "action": "clear"
            })


        return jsonify({
            "success": False,
            "error": "Invalid hologram mode"
        }),400


    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }),500


# ============================================================
# CHAT API
# ============================================================

@app.route(
    "/api/chat",
    methods=["POST"]
)
def chat_api():

    temp_paths = []

    try:

        content_type = (
            request.content_type
            or ""
        )

        is_json = (
            "application/json"
            in content_type
        )

        # ====================================================
        # JSON
        # ====================================================
        if is_json:

            data = (
                request.get_json(
                    silent=True
                )
                or {}
            )

            user_text = str(
                data.get(
                    "message",
                    ""
                )
            ).strip()

            confirmed = (
                str(
                    data.get(
                        "confirmed",
                        "false"
                    )
                ).lower()
                == "true"
            )

            uploaded = []

        # ====================================================
        # MULTIPART
        # ====================================================

        else:

            user_text = str(
                request.form.get(
                    "message",
                    ""
                )
            ).strip()

            confirmed = (
                str(
                    request.form.get(
                        "confirmed",
                        "false"
                    )
                ).lower()
                == "true"
            )

            uploaded = [
                file
                for file
                in request.files.getlist(
                    "attachments"
                )
                if (
                    file
                    and file.filename
                )
            ]

        
        # ====================================================
        # HOLOGRAM COMMAND CHECK
        # ====================================================

        hologram_command = detect_hologram_command(
            user_text
        )

        if hologram_command:

            state = update_hologram_state(
                hologram_command["action"],
                hologram_command["mode"]
            )

            return jsonify({
                "success": True,
                "hologram": True,
                "mode": hologram_command["mode"],
                "action": hologram_command["action"],
                "state": state
            })


# ====================================================
# EMPTY REQUEST
# ====================================================

        if (
            not user_text
            and not uploaded
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "Message or attachment is required.",

            }), 400

        # ====================================================
        # CLASSIFY ATTACHMENTS
        # ====================================================

        image_files = []

        document_files = []

        for file in uploaded:

            original_name = (
                file.filename
            )

            extension = ext_of(
                original_name
            )

            if (
                extension
                in ALLOWED_IMAGE_EXTENSIONS
            ):

                image_files.append(
                    file
                )

            elif (
                extension
                in ALLOWED_DOCUMENT_EXTENSIONS
            ):

                document_files.append(
                    file
                )

            else:

                return jsonify({

                    "success":
                        False,

                    "error":
                        (
                            "Unsupported file type: "
                            f"{original_name}"
                        ),

                }), 400

        # ====================================================
        # IMAGE PROCESSING
        # ====================================================

        vision_replies = []

        for file in image_files:

            safe_name = safe_uploaded_name(
                    file.filename
                )

            path = (
                UPLOAD_DIR
                / (
                    uuid.uuid4().hex
                    + "_"
                    + safe_name
                )
            )

            file.save(
                str(path)
            )

            temp_paths.append(
                path
            )

            instruction = (
                user_text
                or
                "Describe and analyze this image."
            )

            analysis = run_vision(
                path,
                instruction
            )

            analysis = str(
                analysis
            ).strip()

            vision_replies.append({

                "name":
                    file.filename,

                "reply":
                    analysis,

            })

            # ------------------------------------------------
            # Memory
            # ------------------------------------------------

            if not analysis.startswith(
                "ERROR:"
            ):

                remember_multimodal(

                    user_message=(
                        user_text
                        or
                        "Analyze this image."
                    ),

                    assistant_result=
                        analysis,

                    attachment_name=
                        file.filename,

                    attachment_type=
                        ext_of(
                            file.filename
                        ),
                )

        # ====================================================
        # DOCUMENT PROCESSING
        # ====================================================

        document_context_parts = []

        for file in document_files:

            safe_name = (
                safe_uploaded_name(
                    file.filename
                )
            )

            path = (
                UPLOAD_DIR
                / (
                    uuid.uuid4().hex
                    + "_"
                    + safe_name
                )
            )

            file.save(
                str(path)
            )

            temp_paths.append(
                path
            )

            try:

                content = limit_text(
                    extract_document(
                        path
                    )
                )

            except Exception as error:

                content = (
                    "[FILE READ ERROR: "
                    f"{error}]"
                )

            document_context_parts.append(

                "==================================================\n"

                f"ATTACHED FILE: "
                f"{file.filename}\n"

                f"TYPE: "
                f"{ext_of(file.filename)}\n"

                "==================================================\n"

                f"{content}\n"
            )

        document_context = (
            "\n".join(
                document_context_parts
            )
            .strip()
        )

        # ====================================================
        # IMAGE + DOCUMENT
        # ====================================================

        if (
            vision_replies
            and document_context
        ):

            final_prompt = (

                "[SYSTEM: MULTIMODAL ATTACHMENT MODE]\n\n"

                "The user attached image(s) "
                "and document(s).\n\n"

                "Use the image analysis and "
                "document content below.\n\n"

                "USER REQUEST:\n"

                f"{user_text or 'Analyze the attachments.'}\n\n"

                "IMAGE ANALYSIS:\n"

                +
                "\n\n".join(
                    f"{item['name']}:\n"
                    f"{item['reply']}"
                    for item
                    in vision_replies
                )

                +

                "\n\nDOCUMENT CONTENT:\n"

                +

                document_context
            )

            print("🔥 CHAT RECEIVED:", user_text)

            reply = "Hello, I am JARVIS. Chat API is working."

            print("🔥 CHAT RESPONSE SENT")

            remember_multimodal(

                user_message=(
                    user_text
                    or
                    "Analyze the attached "
                    "image and document."
                ),

                assistant_result=
                    reply,

                attachment_name=
                    "MULTIMODAL_SESSION",

                attachment_type=
                    "image+document",
            )

            return jsonify({

                "success":
                    True,

                "reply":
                    reply,

                "attachments":
                    [
                        file.filename
                        for file
                        in uploaded
                    ],

                "vision":
                    True,

                "multimodal_memory":
                    MEMORY_AVAILABLE,

                "coding_mode":
                    False,
            })

        # ====================================================
        # IMAGE ONLY
        # ====================================================

        if vision_replies:

            reply_parts = [

                f"### {item['name']}\n\n"
                f"{item['reply']}"

                for item
                in vision_replies
            ]

            combined_reply = (
                "\n\n".join(
                    reply_parts
                )
            )

            return jsonify({

                "success":
                    True,

                "reply":
                    combined_reply,

                "attachments":
                    [
                        file.filename
                        for file
                        in uploaded
                    ],

                "vision":
                    True,

                "multimodal_memory":
                    MEMORY_AVAILABLE,

                "coding_mode":
                    False,
            })

        # ====================================================
        # DOCUMENT ONLY
        # ====================================================

        if document_context:

            if user_text:

                final_prompt = (

                    "[SYSTEM: DOCUMENT QUESTION MODE]\n\n"

                    "Answer using the actual attached "
                    "document content.\n"

                    "Do not ask the user to upload it again.\n"

                    "If the answer is not in the document, "
                    "say so clearly.\n\n"

                    "USER QUESTION:\n"

                    f"{user_text}\n\n"

                    "DOCUMENT CONTENT:\n"

                    f"{document_context}"
                )

            else:

                final_prompt = (

                    "[SYSTEM: DOCUMENT ANALYSIS MODE]\n\n"

                    "Analyze the attached document. Give:\n\n"

                    "1. Purpose\n"
                    "2. Main points\n"
                    "3. Important facts\n"
                    "4. Methodology if present\n"
                    "5. Results if present\n"
                    "6. Conclusion\n\n"

                    "DOCUMENT CONTENT:\n"

                    f"{document_context}"
                )

            reply = str(
                handle_user_input(
                    final_prompt,
                    confirmed,
                )
            ).strip()

            remember_multimodal(

                user_message=(
                    user_text
                    or
                    "Analyze this document."
                ),

                assistant_result=
                    reply,

                attachment_name=(
                    ", ".join(
                        file.filename
                        for file
                        in document_files
                    )
                ),

                attachment_type=
                    "document",
            )

            return jsonify({

                "success":
                    True,

                "reply":
                    reply,

                "attachments":
                    [
                        file.filename
                        for file
                        in uploaded
                    ],

                "vision":
                    False,

                "multimodal_memory":
                    MEMORY_AVAILABLE,

                "coding_mode":
                    False,
            })

        # ====================================================
        # CODING MODE
        # ====================================================

        coding_mode = (

            not uploaded

            and is_coding_problem(
                user_text
            )

            and CODING_EXPERT_AVAILABLE
        )

        if coding_mode:

            result = run_coding_expert(
                user_text
            )

            reply = format_coding_result(
                result
            )

            return jsonify({

                "success":
                    True,

                "reply":
                    reply,

                "attachments":
                    [],

                "vision":
                    False,

                "coding_mode":
                    True,

                "coding_expert":
                    True,

                "coding_success":
                    bool(
                        result.get(
                            "success",
                            False
                        )
                    ),

                "coding_verified":
                    bool(
                        result.get(
                            "verified",
                            False
                        )
                    ),

                "coding_stage":
                    result.get(
                        "stage",
                        "unknown"
                    ),

                "coding_attempts":
                    result.get(
                        "attempts",
                        0
                    ),
            })

        # ====================================================
        # NORMAL CHAT
        # ====================================================

        reply = str(
            handle_user_input(
                user_text,
                confirmed,
            )
        ).strip()

        return jsonify({

            "success":
                True,

            "reply":
                reply,

            "attachments":
                [],

            "vision":
                False,

            "coding_mode":
                False,

            "coding_expert":
                CODING_EXPERT_AVAILABLE,

            "memory":
                MEMORY_AVAILABLE,
        })

    except Exception as error:

        traceback.print_exc()

        return jsonify({

            "success":
                False,

            "error":
                str(error),

        }), 500

    finally:

        # ----------------------------------------------------
        # Delete temporary uploaded files
        # ----------------------------------------------------

        for path in temp_paths:

            try:

                path.unlink(
                    missing_ok=True
                )

            except Exception:

                pass


# ============================================================
# FILE SIZE ERROR
# ============================================================

@app.errorhandler(
    413
)
def too_large(_):

    return jsonify({

        "success":
            False,

        "error":
            (
                "Attachment is too large. "
                "Maximum size is 25 MB."
            ),

    }), 413


# ============================================================
# SERVER START
# ============================================================
# ============================================================
# JARVIS VS CODE BRIDGE v1.1
# ============================================================
# ============================================================
# PROACTIVE VOICE BRIDGE
# ============================================================

@app.route(
    "/voice/get",
    methods=["GET"]
)
def voice_get():

    return jsonify({

        "success": True,

        "message": ""

    })
@app.route(
    "/jarvis/code",
    methods=["POST"]
)
@app.route(
    "/jarvis/code",
    methods=["POST"]
)
def jarvis_code():

    try:

        data = request.get_json(silent=True) or {}

        message = data.get(
            "message",
            ""
        )

        code = data.get(
            "code",
            ""
        )

        filename = data.get(
            "file",
            ""
        )


        print("\n🔥 VS CODE REQUEST")

        print(
            "FILE:",
            filename
        )

        print(
            "COMMAND:",
            message
        )


        request_data = {

            "message": message,

            "file": filename,

            "code": code

        }


        # SWE Agent
        result = run_swe_agent(
            request_data
        )


        return jsonify({

            "success": True,

            "answer": {
                "status": result.status,
                "history": result.history
        }

        })


    except Exception as error:


        traceback.print_exc()


        return jsonify({

            "success": False,

            "error": str(error)

        })
if __name__ == "__main__":

    print()

    print(
        "=" * 68
    )

    print(
        "             JARVIS LOCAL AI SERVER"
    )

    print(
        "             MULTIMODAL BEASTMODE"
    )

    print(
        "             OFFLINE VOICE ENABLED"
    )

    print(
        "             GESTURE CONTROL ENABLED"
    )

    print(
        "=" * 68
    )

    print()

    print(
        f"Project : {BASE_DIR}"
    )

    print(
        f"Web folder : {WEB_DIR}"
    )

    print(
        f"Frontend : {INDEX_FILE}"
    )

    print(
        f"Frontend found : "
        f"{INDEX_FILE.exists()}"
    )

    print()

    # --------------------------------------------------------
    # Memory
    # --------------------------------------------------------

    print(
        f"Memory : "
        f"{MEMORY_AVAILABLE}"
    )

    if not MEMORY_AVAILABLE:

        print(
            f"Memory error : "
            f"{MEMORY_IMPORT_ERROR}"
        )

    # --------------------------------------------------------
    # Vision
    # --------------------------------------------------------

    print(
        f"Vision : "
        f"{VISION_AVAILABLE}"
    )

    if not VISION_AVAILABLE:

        print(
            f"Vision error : "
            f"{VISION_IMPORT_ERROR}"
        )

    # --------------------------------------------------------
    # Documents
    # --------------------------------------------------------

    print(
        f"PDF : "
        f"{PYMUPDF_AVAILABLE or PYPDF_AVAILABLE}"
    )

    print(
        f"DOCX : "
        f"{DOCX_AVAILABLE}"
    )

    print(
        f"XLSX : "
        f"{XLSX_AVAILABLE}"
    )

    print(
        f"PPTX : "
        f"{PPTX_AVAILABLE}"
    )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()

    print("=" * 68)

    print(
        "             JARVIS SERVER RUNNING"
    )

    print(
        "             http://127.0.0.1:8000"
    )

    print()

    app.run(

        host="0.0.0.0",

        port=8000,

        debug=False,

        threaded=True

    )