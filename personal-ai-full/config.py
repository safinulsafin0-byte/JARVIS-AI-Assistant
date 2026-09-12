from pathlib import Path
import os


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# OLLAMA
# ============================================================

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://127.0.0.1:11434"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:7b-instruct-q4_K_M"
)


# ============================================================
# ALLOWED FILESYSTEM ROOTS
# ============================================================

# JARVIS can access only these folders.
# Your current project is D:\personal-ai-full,
# so BASE_DIR automatically points to that folder.

ALLOWED_ROOT_DIRS = [
    BASE_DIR,
    Path(r"D:\personal-ai"),
    Path.home() / "Documents",
    Path.home() / "Downloads",
    Path.home() / "Desktop",
]


# ============================================================
# INTERNAL DIRECTORIES
# ============================================================

MEMORY_DB = (
    BASE_DIR
    / "memory"
    / "memory.db"
)

RAG_DIR = (
    BASE_DIR
    / "rag"
    / "data"
)

CHROMA_DIR = (
    BASE_DIR
    / "rag"
    / "chroma"
)

BROWSER_PROFILE = (
    BASE_DIR
    / "browser"
    / "profile"
)

SCREENSHOTS_DIR = (
    BASE_DIR
    / "screenshots"
)


# ============================================================
# VOICE
# ============================================================

WAKE_WORD = "jarvis"


# ============================================================
# CONFIRMATION
# ============================================================

REQUIRE_CONFIRMATION_FOR = {
    "delete_file",
    "delete_folder",
    "shutdown",
    "restart",
    "send_message",
    "post_content",
    "purchase",
}