# JARVIS — Fully Local Personal AI

This project is designed around a local Ollama model. The AI response path does not require OpenAI/Gemini APIs.

## Main features

- Local Qwen model through Ollama
- Text chat
- Tool calling
- File/folder create/read/write/move/copy/rename/search
- Confirmation for destructive actions
- Windows app/path opening
- Keyboard/mouse/screenshot/clipboard controls
- Browser automation with persistent local browser profile
- Local conversation memory (SQLite)
- Local document RAG (Chroma + sentence-transformers)
- Local speech-to-text with faster-whisper
- Optional Piper TTS
- Optional FastAPI web UI

## Important safety

Only paths listed in `config.py` are accessible. Do not add Windows/system folders.
Review every tool before granting more permissions.
Keep confirmation enabled for deletion, messaging, posting, purchases, shutdown, etc.

## Start

```powershell
.\venv\Scripts\Activate.ps1
python main.py
```

## Browser

Install browser binaries once:

```powershell
python -m playwright install chromium
```

The browser uses a persistent profile under `browser/profile`. Log in manually first; do not give the AI your passwords.

## Web UI

```powershell
uvicorn ui.server:app --host 127.0.0.1 --port 8000
```

Then open http://127.0.0.1:8000 in your browser.

## RAG

Place documents under `rag/data` and call `ingest_folder` from a Python shell, for example:

```powershell
python -c "from rag.ingest import ingest_folder; print(ingest_folder('rag/data'))"
```

The first embedding-model download may come from Hugging Face. Afterward it is cached locally.

## Voice

STT uses a local faster-whisper model. The first run downloads the selected Whisper model unless already cached.
Piper TTS requires a Piper voice model and executable configured locally.
