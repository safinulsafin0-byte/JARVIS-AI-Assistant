# Setup

1. Ensure Ollama is installed and the Qwen model works:

```powershell
ollama run qwen2.5:7b-instruct-q4_K_M
```

2. Create/activate venv:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Browser support:

```powershell
python -m playwright install chromium
```

5. Start:

```powershell
python main.py
```

For voice, run the voice loop from Python after confirming your microphone/audio devices work.
