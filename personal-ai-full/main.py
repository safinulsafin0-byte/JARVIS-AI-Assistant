import re

from vision.image_analyzer import (
    analyze_image,
    describe_image,
    read_image_text,
    explain_diagram,
    analyze_image_problem,
)

from image_generation.image_generator import generate_image
from llm.ollama_client import chat, is_tool_call
from voice.wake_word import WakeWordEngine
from tools.router import execute_tool_call, TOOL_DESCRIPTIONS

from memory.memory_manager import remember, build_context
from rag.retriever import search as rag_search
from automation.command_engine import handle_automation_command


# ============================================================
# TOOL RESULT INSTRUCTIONS
# ============================================================

TOOL_RESULT_INSTRUCTIONS = """
You are JARVIS, a local Windows AI assistant.

You have just received the result of a tool execution.

IMPORTANT RULES:

1. NEVER claim an action succeeded if the tool result says ERROR.
2. NEVER invent a successful result.
3. If the tool result starts with "SUCCESS:", briefly confirm it.
4. If the tool result starts with "ERROR:", explain the actual error.
5. Do not apologize unnecessarily.
6. Do not output raw JSON.
7. Do not output tool calls.
8. Keep responses concise and natural.
"""


# ============================================================
# WAKE-WORD PREFIX STRIPPING
#
# direct_command() below matches on things like
# text.startswith("search for ") or text in ("open youtube", ...).
# If the user's command still has a leading wake-word --
# "jarvis search for X", "hey jarvis open youtube" -- those
# checks silently miss (the string doesn't start with "search
# for ", it starts with "jarvis search for "), so the command
# falls all the way through to the LLM instead of being handled
# directly. The LLM then has to guess a tool-call shape from
# scratch, which is where the malformed JSON came from.
#
# Stripping any leading wake-word here, once, before pattern
# matching begins, fixes this for every pattern in
# direct_command() (and for handle_automation_command(), which
# receives the same stripped text) without having to touch each
# individual pattern.
# ============================================================

_WAKE_PREFIXES = (
    "hey jarvis,",
    "hey jarvis",
    "okay jarvis,",
    "okay jarvis",
    "ok jarvis,",
    "ok jarvis",
    "jarvis,",
    "jarvis",
)


def _strip_wake_prefix(text):
    """
    Remove a single leading wake-word phrase from user text, if
    present. Only strips from the very start of the message, and
    only once -- "jarvis jarvis open youtube" would still have one
    "jarvis" left, which is intentional (better to under-strip
    than to eat a real word the user meant as part of their
    command).
    """

    if not text:
        return text

    stripped = text.strip()
    lowered = stripped.lower()

    for prefix in _WAKE_PREFIXES:
        if lowered.startswith(prefix):
            rest = stripped[len(prefix):].strip()
            # Don't return an empty string just because the whole
            # message was the wake word itself -- let the caller
            # decide what to do with that.
            return rest if rest else stripped

    return stripped


# ============================================================
# INTERNAL PROMPT DETECTION
# ============================================================

def _is_internal_system_prompt(text):
    """
    Detect structured prompts generated internally by api_server.py.

    These prompts may contain:
    - Full PDF text
    - Full document content
    - OCR content
    - Image context
    - Multimodal attachment context

    They must NEVER pass through direct_command(),
    because words inside the document could accidentally trigger
    shutdown, browser actions, YouTube summary, etc.
    """

    if not text:
        return False

    text = str(text).strip()

    internal_markers = (
        "[SYSTEM: DOCUMENT QUESTION MODE]",
        "[SYSTEM: DOCUMENT ANALYSIS MODE]",
        "[SYSTEM: DOCUMENT MODE]",
        "[SYSTEM: IMAGE QUESTION MODE]",
        "[SYSTEM: IMAGE MODE]",
        "[SYSTEM: MULTIMODAL ATTACHMENT MODE]",
        "[SYSTEM: INTERNAL",
    )

    return any(
        text.startswith(marker)
        for marker in internal_markers
    )


# ============================================================
# SAFE LLM CHAT
# ============================================================

def _chat_internal(messages):
    """
    Safe chat function for internal document/image prompts.

    Internal prompts must NOT use tools.
    Different ollama_client.py implementations may accept
    different tool arguments, so this function safely tries
    the supported call styles.
    """

    errors = []

    try:
        return chat(messages, None)
    except Exception as e:
        errors.append(str(e))

    try:
        return chat(messages)
    except Exception as e:
        errors.append(str(e))

    raise RuntimeError(
        "Internal LLM request failed: " + " | ".join(errors)
    )


def _chat_normal(messages):
    """
    Normal JARVIS chat with tools enabled.
    """

    return chat(messages, TOOL_DESCRIPTIONS)


# ============================================================
# BROWSER HELPERS
# ============================================================

def _browser_tool(action, **args):

    try:
        from browser.browser_agent import browser_tool
        return browser_tool(action, **args)
    except Exception as e:
        return f"ERROR: Browser operation failed: {e}"


def _direct_browser_open(url):
    return _browser_tool("open", url=url)


def _direct_browser_search(query):
    return _browser_tool("search", query=query)


def _open_first_youtube_video():
    return _browser_tool("open_first_video")


def _get_current_browser_url():

    result = _browser_tool("current_url")

    if not result:
        return ""

    result = str(result).strip()

    if result.startswith("ERROR:"):
        return ""

    return result


def _is_youtube_video_url(url):

    if not url:
        return False

    url = str(url).lower().strip()

    return (
        "youtube.com/watch" in url
        or "youtube.com/shorts/" in url
        or "youtube.com/live/" in url
        or "youtu.be/" in url
    )


# ============================================================
# SYSTEM HELPERS
# ============================================================

def _direct_chrome_open():

    try:
        from tools import system_ops
        result = system_ops.open_app(command="chrome")
        return str(result)
    except Exception as e:
        return f"ERROR: Could not open Chrome: {e}"


def _direct_shutdown():

    try:
        from tools import system_ops
        return system_ops.shutdown(delay_seconds=10)
    except Exception as e:
        return f"ERROR: Could not schedule shutdown: {e}"


def _direct_cancel_shutdown():

    try:
        from tools import system_ops
        return system_ops.cancel_shutdown()
    except Exception as e:
        return f"ERROR: Could not cancel shutdown: {e}"


# ============================================================
# VIDEO SUMMARY
# ============================================================

def _summarize_current_video(language="English"):

    try:

        current_url = _get_current_browser_url()

        if not current_url:
            return "ERROR: I could not detect the current browser page."

        # ----------------------------------------------------
        # Already on a YouTube video
        # ----------------------------------------------------

        if _is_youtube_video_url(current_url):
            video_url = current_url

        # ----------------------------------------------------
        # On YouTube search/results page
        # ----------------------------------------------------

        elif "youtube.com" in current_url.lower():

            print("\nJARVIS: You are on YouTube.")
            print("JARVIS: Opening the first video...")

            open_result = _open_first_youtube_video()

            if str(open_result).startswith("ERROR:"):
                return str(open_result)

            video_url = _get_current_browser_url()

            if not _is_youtube_video_url(video_url):
                return (
                    "ERROR: I could not open a YouTube "
                    "video from the current page."
                )

        # ----------------------------------------------------
        # Not YouTube
        # ----------------------------------------------------

        else:
            return "ERROR: The current browser page is not a YouTube video."

        print("\nJARVIS: Getting the YouTube transcript...")

        try:
            from video_summarizer import summarize_youtube
        except ImportError as e:
            return f"ERROR: video_summarizer.py could not be imported: {e}"

        result = summarize_youtube(video_url, language=language)

        return str(result)

    except Exception as e:
        return f"ERROR: Could not summarize the video: {e}"


# ============================================================
# EXTRACT YOUTUBE URL
# ============================================================

def _extract_youtube_url(text):

    if not text:
        return None

    words = str(text).split()

    for word in words:

        cleaned = word.strip().strip("\"'").rstrip(".,!?;:)]}")
        lower = cleaned.lower()

        if "youtube.com/" in lower or "youtu.be/" in lower:

            if not lower.startswith("http"):
                cleaned = "https://" + cleaned

            return cleaned

    return None


# ============================================================
# CHECK SUMMARY REQUEST
# ============================================================

def _is_summary_request(text):

    if not text:
        return False

    text = str(text).lower()

    summary_words = (
        "summarize", "summarise", "summary",
        "summerize", "summerise", "summeriz",
    )

    return any(word in text for word in summary_words)


# ============================================================
# CHECK VIDEO SUMMARY REQUEST
# ============================================================

def _is_video_summary_request(text):

    if not text:
        return False

    text = str(text).lower()

    if not _is_summary_request(text):
        return False

    video_phrases = (
        "youtube video", "youtube", "current video", "this video",
        "the video", "video summary", "summarize video", "summarise video",
    )

    return any(phrase in text for phrase in video_phrases)


# ============================================================
# DIRECT COMMAND HANDLER
# ============================================================

def direct_command(user_text):

    if not user_text:
        return None

    original = str(user_text).strip()

    # Strip a leading wake word ("jarvis", "hey jarvis", ...) before
    # any pattern matching happens below. See _strip_wake_prefix()
    # docstring for why this matters.
    original = _strip_wake_prefix(original)

    text = original.lower().strip()
    text = text.rstrip(" .!?,;:")

    if not text:
        return None

    # ========================================================
    # DIRECT YOUTUBE VIDEO SELECTION
    # Handles commands like:
    #   play the first video
    #   open the second video
    #   play 3rd video
    # This bypasses LLM tool-call generation completely.
    # ========================================================

    video_match = re.match(
        r"^(?:play|open)\s+(?:the\s+)?(first|second|third|fourth|fifth|\d+(?:st|nd|rd|th)?)\s+video$",
        text,
    )

    if video_match:

        position_text = video_match.group(1)

        position_map = {
            "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
        }

        if position_text in position_map:
            index = position_map[position_text]
        else:
            index = int(re.sub(r"(st|nd|rd|th)$", "", position_text))

        return _browser_tool("open_nth_video", index=index)

    # ========================================================
    # ADVANCED AUTOMATION ENGINE
    # ========================================================

    try:
        automation_result = handle_automation_command(original)

        if automation_result is not None:
            return automation_result

    except Exception as e:
        print("[AUTOMATION WARNING]", e)

    # ========================================================
    # IMAGE GENERATION
    # ========================================================

    image_generate_words = (
        "generate image", "generate an image", "generate a image",
        "create image", "create an image", "create a image",
        "make image", "make an image", "draw image", "draw an image",
        "draw a image", "create picture", "make picture",
        "generate picture", "generate photo", "create photo",
    )

    matched_image_command = None

    for command in image_generate_words:
        if text.startswith(command):
            matched_image_command = command
            break

    if matched_image_command:

        prompt = original[len(matched_image_command):].strip()
        prompt = prompt.lstrip(":,- ").strip()

        if not prompt:
            return "ERROR: Please provide a description for the image you want to generate."

        try:
            return str(generate_image(prompt))
        except Exception as e:
            return f"ERROR: Image generation failed: {e}"

    # ========================================================
    # IMAGE UNDERSTANDING
    # ========================================================

    if text.startswith("describe image "):

        image_path = original[len("describe image "):].strip().strip('"')

        if not image_path:
            return "ERROR: Please provide an image path."

        try:
            return str(describe_image(image_path))
        except Exception as e:
            return f"ERROR: Image description failed: {e}"

    if text.startswith("analyze image "):

        image_path = original[len("analyze image "):].strip().strip('"')

        if not image_path:
            return "ERROR: Please provide an image path."

        try:
            return str(analyze_image(image_path))
        except Exception as e:
            return f"ERROR: Image analysis failed: {e}"

    ocr_commands = (
        "read text from image ", "extract text from image ",
        "read image text ", "ocr image ",
    )

    for command in ocr_commands:

        if text.startswith(command):

            image_path = original[len(command):].strip().strip('"')

            if not image_path:
                return "ERROR: Please provide an image path."

            try:
                return str(read_image_text(image_path))
            except Exception as e:
                return f"ERROR: OCR failed: {e}"

    diagram_commands = (
        "explain diagram ", "analyze diagram ", "explain this diagram ",
    )

    for command in diagram_commands:

        if text.startswith(command):

            image_path = original[len(command):].strip().strip('"')

            if not image_path:
                return "ERROR: Please provide a diagram image path."

            try:
                return str(explain_diagram(image_path))
            except Exception as e:
                return f"ERROR: Diagram analysis failed: {e}"

    problem_commands = (
        "find problems in image ", "find errors in image ",
        "check image problems ", "analyze image problems ",
        "check image errors ",
    )

    for command in problem_commands:

        if text.startswith(command):

            image_path = original[len(command):].strip().strip('"')

            if not image_path:
                return "ERROR: Please provide an image path."

            try:
                return str(analyze_image_problem(image_path))
            except Exception as e:
                return f"ERROR: Image problem analysis failed: {e}"

    # ========================================================
    # CANCEL SHUTDOWN
    # ========================================================

    cancel_shutdown_words = (
        "cancel shutdown", "cancel the shutdown", "stop shutdown",
        "stop the shutdown", "abort shutdown", "abort the shutdown",
        "don't shut down", "do not shut down", "dont shut down",
    )

    if any(phrase in text for phrase in cancel_shutdown_words):
        return _direct_cancel_shutdown()

    # ========================================================
    # SHUTDOWN COMPUTER
    # ========================================================

    shutdown_words = (
        "shut down", "shutdown", "turn off the computer",
        "turn off computer", "power off",
    )

    if any(phrase in text for phrase in shutdown_words):
        return _direct_shutdown()

    # ========================================================
    # OPEN YOUTUBE
    # ========================================================

    if text in (
        "open youtube", "open youtube.com", "go to youtube",
        "go youtube", "launch youtube", "youtube open",
        "youtube kholo", "youtube khulo",
    ):
        return _direct_browser_open("https://www.youtube.com")

    # ========================================================
    # OPEN GOOGLE
    # ========================================================

    if text in (
        "open google", "open google.com", "go to google",
        "go google", "google open",
    ):
        return _direct_browser_open("https://www.google.com")

    # ========================================================
    # OPEN GITHUB
    # ========================================================

    if text in (
        "open github", "open github.com", "go to github", "github open",
    ):
        return _direct_browser_open("https://github.com")

    # ========================================================
    # OPEN FACEBOOK
    # ========================================================

    if text in (
        "open facebook", "open facebook.com", "go to facebook",
        "facebook open",
    ):
        return _direct_browser_open("https://www.facebook.com")

    # ========================================================
    # OPEN GMAIL
    # ========================================================

    if text in (
        "open gmail", "open gmail.com", "go to gmail", "gmail open",
    ):
        return _direct_browser_open("https://mail.google.com")

    # ========================================================
    # OPEN CHROME
    # ========================================================

    if text in (
        "open chrome", "launch chrome", "start chrome", "chrome open",
    ):
        return _direct_chrome_open()

    # ========================================================
    # SEARCH FOR
    # ========================================================

    if text.startswith("search for "):

        query = original[len("search for "):].strip()

        if query:
            return _direct_browser_search(query)

        return "ERROR: Search query is empty."

    # ========================================================
    # SEARCH
    # ========================================================

    if text.startswith("search "):

        query = original[len("search "):].strip()

        if query:
            return _direct_browser_search(query)

        return "ERROR: Search query is empty."

    # ========================================================
    # EXPLICIT YOUTUBE URL SUMMARY
    # ========================================================

    youtube_url = _extract_youtube_url(original)

    if youtube_url and _is_summary_request(text):

        language = "English"

        if "bangla" in text or "bengali" in text or "বাংলা" in original:
            language = "Bangla"

        try:
            from video_summarizer import summarize_youtube
            return str(summarize_youtube(youtube_url, language=language))
        except Exception as e:
            return f"ERROR: Could not summarize video: {e}"

    # ========================================================
    # CURRENT YOUTUBE VIDEO SUMMARY
    # ========================================================

    if _is_video_summary_request(text):

        is_bangla = "bangla" in text or "bengali" in text or "বাংলা" in original
        language = "Bangla" if is_bangla else "English"

        return _summarize_current_video(language=language)

    # ========================================================
    # NO DIRECT COMMAND
    # ========================================================

    return None


# ============================================================
# HANDLE TOOL RESULT
# ============================================================

def _handle_tool_result(prompt_context, original_response, result_text):

    follow_messages = prompt_context + [
        {"role": "assistant", "content": str(original_response)},
        {
            "role": "user",
            "content": (
                TOOL_RESULT_INSTRUCTIONS
                + "\n\nTOOL RESULT:\n"
                + str(result_text)
            ),
        },
    ]

    try:
        follow = _chat_normal(follow_messages)
        follow = str(follow).strip()
    except Exception:
        follow = str(result_text).strip()

    # --------------------------------------------------------
    # Prevent false success
    # --------------------------------------------------------

    if str(result_text).startswith("ERROR:"):
        return "The requested action failed. " + str(result_text)

    # --------------------------------------------------------
    # Empty model response fallback
    # --------------------------------------------------------

    if not follow:
        return str(result_text).strip()

    return follow


# ============================================================
# MAIN REQUEST HANDLER
# ============================================================

def handle_user_input(user_text, user_confirmed=False):

    if not user_text:
        return "Please enter a message."

    user_text = str(user_text).strip()

    if not user_text:
        return "Please enter a message."

    # ========================================================
    # DETECT INTERNAL STRUCTURED PROMPT
    # ========================================================

    is_internal_prompt = _is_internal_system_prompt(user_text)

    # ========================================================
    # DIRECT COMMAND
    #
    # IMPORTANT:
    # Internal PDF/document prompts must NEVER go through
    # direct_command().
    # ========================================================

    if not is_internal_prompt:

        direct_result = direct_command(user_text)

        if direct_result is not None:

            result_text = str(direct_result).strip()

            try:
                remember(user_text, result_text)
            except Exception:
                pass

            return result_text

    # ========================================================
    # MEMORY
    # ========================================================

    try:
        context = build_context()
    except Exception as e:
        print("[MEMORY WARNING]", e)
        context = ""

    # ========================================================
    # RAG
    # ========================================================

    rag = ""

    rag_keywords = (
        "my document", "my pdf", "paper", "assignment", "document",
        "notes", "my files", "research paper", "local file",
    )

    # Internal document prompts already contain the actual document content.
    if (
        not is_internal_prompt
        and any(keyword in user_text.lower() for keyword in rag_keywords)
    ):

        try:
            rag = rag_search(user_text)
        except Exception as e:
            print("[RAG WARNING]", e)
            rag = ""

    # ========================================================
    # BUILD PROMPT
    # ========================================================

    prompt_context = []

    if context:
        prompt_context.append({"role": "system", "content": "MEMORY:\n" + str(context)})

    if rag:
        prompt_context.append(
            {"role": "system", "content": "LOCAL DOCUMENT CONTEXT:\n" + str(rag)}
        )

    prompt_context.append({"role": "user", "content": user_text})

    # ========================================================
    # QWEN RESPONSE
    #
    # Internal document/image prompts:
    # - No tools
    # - No tool call parsing
    # - No direct commands
    # ========================================================

    try:

        if is_internal_prompt:
            response = _chat_internal(prompt_context)
        else:
            response = _chat_normal(prompt_context)

    except Exception as e:

        error_message = f"ERROR: LLM request failed: {e}"
        print("[LLM ERROR]", error_message)

        try:
            remember(user_text, error_message)
        except Exception:
            pass

        return error_message

    response = str(response).strip()

    # ========================================================
    # INTERNAL PROMPT
    #
    # Return direct LLM response.
    # Never parse document/image analysis as a tool call.
    # ========================================================

    if is_internal_prompt:

        try:
            remember(user_text, response)
        except Exception:
            pass

        return response

    # ========================================================
    # DETECT TOOL CALL
    # ========================================================

    try:
        call = is_tool_call(response)
    except Exception as e:
        print("[TOOL PARSE WARNING]", e)
        call = None

    # ========================================================
    # TOOL CALL
    # ========================================================

    if call:

        try:
            result = execute_tool_call(call, user_confirmed=user_confirmed)
        except Exception as e:
            result = f"ERROR: Tool execution failed: {e}"

        result_text = str(result).strip()

        # ----------------------------------------------------
        # Confirmation needed
        # ----------------------------------------------------

        if result_text.startswith("CONFIRMATION_NEEDED:"):

            try:
                remember(user_text, result_text)
            except Exception:
                pass

            return result_text

        # ----------------------------------------------------
        # Process tool result
        # ----------------------------------------------------

        final_response = _handle_tool_result(
            prompt_context=prompt_context,
            original_response=response,
            result_text=result_text,
        )

        try:
            remember(user_text, final_response)
        except Exception:
            pass

        return final_response

    # ========================================================
    # NORMAL CHAT
    # ========================================================

    try:
        remember(user_text, response)
    except Exception:
        pass

    return response


# ============================================================
# TEXT MODE
# ============================================================

def text_chat_loop():

    print("\n================================")
    print("       JARVIS TEXT MODE")
    print("================================")
    print("Type 'exit' to leave.\n")

    while True:

        try:
            user_text = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if not user_text:
            continue

        if user_text.lower() in ("exit", "quit"):
            break

        try:
            reply = handle_user_input(user_text)
            print("JARVIS:", reply)
        except Exception as e:
            print("JARVIS: An error occurred.")
            print("[ERROR]", e)

        print()


# ============================================================
# VOICE MODE
# ============================================================

def voice_loop():

    try:
        from voice.stt import listen_once
        from voice.tts import speak
    except ImportError as e:
        print("JARVIS: Voice mode is not available.")
        print("[IMPORT ERROR]", e)
        return

    print()
    print("================================")
    print("       JARVIS VOICE MODE")
    print("================================")
    print()
    print("Microphone is active.")
    print("Speak after 'Listening...'")
    print("Press Ctrl+C to stop.")
    print()

    wake_engine = WakeWordEngine(timeout_seconds=8)

    while True:

        try:

            print("\U0001f399\ufe0f Listening...")

            text = listen_once(duration_sec=5, sample_rate=16000)

            if not text:
                print("...no speech detected...\n")
                continue

            text = str(text).strip()

            if not text:
                continue

            print("You:", text)

            if text.lower() in (
                "exit", "quit", "stop jarvis", "goodbye jarvis", "stop",
            ):

                reply = "Voice mode stopped, Sir."
                print("JARVIS:", reply)

                try:
                    speak(str(reply))
                except Exception as tts_error:
                    print("[TTS ERROR]", tts_error)

                break

            processed_text = wake_engine.process(text)

            if processed_text is None:
                print("\U0001f4a4 Waiting for 'Hey JARVIS'...")
                continue

            if not processed_text:
                print("\u26a1 JARVIS activated.")

                try:
                    speak("Yes, Sir?")
                except Exception as tts_error:
                    print("[TTS ERROR]", tts_error)

                continue

            text = processed_text

            try:
                reply = handle_user_input(text)
            except Exception as input_error:
                print("[HANDLE INPUT ERROR]", input_error)
                reply = "ERROR: I could not process your request."

            print("JARVIS:", reply)

            try:
                speak(str(reply))
            except Exception as tts_error:
                print("[TTS ERROR]", tts_error)

        except KeyboardInterrupt:
            print()
            print("Voice mode stopped.")
            break

        except Exception as e:
            print("[VOICE ERROR]", e)
            print("Retrying...\n")


# ============================================================
# STARTUP MENU
# ============================================================

def main_menu():

    while True:

        print("\n")
        print("========================================")
        print("           JARVIS LOCAL AI")
        print("========================================")
        print()
        print("[1] Text Mode")
        print("[2] Voice Mode")
        print("[3] Exit")
        print()

        try:
            choice = input("Select mode: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if choice == "1":
            text_chat_loop()
        elif choice == "2":
            voice_loop()
        elif choice == "3":
            print("Goodbye, Sir.")
            break
        else:
            print("Invalid choice. Select 1, 2, or 3.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main_menu()