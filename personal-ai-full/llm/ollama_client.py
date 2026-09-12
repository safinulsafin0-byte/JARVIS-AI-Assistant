import json
import time

import requests

from config import OLLAMA_HOST, OLLAMA_MODEL


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are JARVIS, a local AI assistant.

You have access to tools supplied by the application.

IMPORTANT TOOL-CALL RULES:

1. If a tool is required, output ONLY valid JSON.

2. The JSON MUST use exactly this structure:

{
  "tool": "tool.name",
  "args": {
    "argument": "value"
  }
}

3. For deleting a file, use exactly:

{
  "tool": "filesystem.delete_file",
  "args": {
    "path": "test.txt"
  }
}

4. For creating a file, use:

{
  "tool": "filesystem.create_file",
  "args": {
    "path": "test.txt",
    "content": ""
  }
}

5. For opening an application, use:

{
  "tool": "system.open_app",
  "args": {
    "command": "notepad"
  }
}

6. For opening a URL, opening a website, or performing a
   YouTube/web search, use exactly:

{
  "tool": "browser.open",
  "args": {
    "url": "https://www.youtube.com/results?search_query=Doctor+Strange+2+movie"
  }
}

   Never output the malformed shape below -- it will be
   rejected:

{
  "browser": {
    "open": "https://www.youtube.com/results?search_query=Doctor+Strange+2+movie"
  }
}

7. Never invent that a tool succeeded.

8. Destructive actions require confirmation if the application asks for confirmation.

9. If no tool is required, answer normally.

10. Do not output Markdown fences around tool JSON.

11. Do not output explanations together with tool JSON.

12. Always use the exact tool names supplied by the application.

13. Never use this malformed format:

{
  "filesystem.delete_file": "path": "test.txt"
}

14. Never use this malformed format either (nesting the tool
    name as a JSON key instead of using "tool"/"args"):

{
  "browser": {
    "open": "some value"
  }
}

15. Always use the "tool" and "args" fields.

Available tools are described by the application and injected into the prompt.
"""


# ============================================================
# CONNECTION RETRY SETTINGS
#
# Ollama sometimes hasn't finished starting its background
# service yet when JARVIS makes its very first request (e.g.
# right after boot/login). These settings let a request retry
# a few times with a short backoff instead of failing outright
# on a single refused connection.
# ============================================================

OLLAMA_MAX_RETRIES = 4
OLLAMA_RETRY_DELAY_SECONDS = 2
OLLAMA_RETRY_BACKOFF = 1.5


# ============================================================
# KNOWN TOOL NAMESPACES
#
# Used both by the dotted-string repair (existing behaviour)
# and by the nested-object repair added below.
# ============================================================

KNOWN_NAMESPACES = (
    "filesystem",
    "system",
    "browser",
)

known_prefixes = tuple(
    f"{namespace}." for namespace in KNOWN_NAMESPACES
)

# For nested single-value tool calls like:
#     {"browser": {"open": "https://..."}}
# we need to know which argument name the bare value should be
# assigned to, since the model only gave us a value, not a key.
SINGLE_ARG_KEY_MAP = {
    "open": "url",
    "open_app": "command",
    "delete_file": "path",
    "search": "query",
}


# ============================================================
# RESPONSE CLEANER
# ============================================================

def _clean_response(text):
    """
    Clean common Qwen formatting mistakes.
    """

    if not text:
        return ""

    text = str(text).strip()

    # --------------------------------------------------------
    # Remove markdown code fences
    # --------------------------------------------------------

    if text.startswith("```"):

        lines = text.splitlines()

        cleaned_lines = []

        for line in lines:

            stripped = line.strip()

            if stripped.startswith("```"):
                continue

            cleaned_lines.append(line)

        text = "\n".join(cleaned_lines).strip()

    return text


# ============================================================
# VALID TOOL CALL CHECK
# ============================================================

def _is_valid_tool_call(obj):
    """
    Check whether an object is a valid JARVIS tool call.
    """

    if not isinstance(obj, dict):
        return False

    tool = obj.get("tool")
    args = obj.get("args")

    return (
        isinstance(tool, str)
        and bool(tool.strip())
        and isinstance(args, dict)
    )


# ============================================================
# REPAIR NESTED-NAMESPACE TOOL JSON
#
# Handles the shape the model actually produced in practice:
#
#     {"browser": {"open": "https://..."}}
#
# instead of the correct:
#
#     {"tool": "browser.open", "args": {"url": "https://..."}}
#
# This is a different failure mode from the dotted-string
# malformed JSON handled by _repair_common_tool_json below --
# here the *entire text* is already valid JSON, it's just using
# the wrong schema (nested namespace/action objects instead of
# "tool"/"args"). json.loads() succeeds on it, so the old code
# never even reached the string-repair path for this case.
# ============================================================

def _repair_nested_namespace_tool_json(obj):
    """
    Try to convert {"<namespace>": {"<action>": <value>}} into
    a proper {"tool": "<namespace>.<action>", "args": {...}}
    tool call. Returns None if `obj` doesn't match that shape.
    """

    if not isinstance(obj, dict) or len(obj) != 1:
        return None

    (namespace, inner), = obj.items()

    if namespace not in KNOWN_NAMESPACES:
        return None

    if not isinstance(inner, dict) or len(inner) != 1:
        return None

    (action, value), = inner.items()

    if not isinstance(action, str) or not action.strip():
        return None

    tool_name = f"{namespace}.{action}"

    if isinstance(value, dict):
        args = value
    else:
        arg_key = SINGLE_ARG_KEY_MAP.get(action, "value")
        args = {arg_key: value}

    return {
        "tool": tool_name,
        "args": args,
    }


# ============================================================
# REPAIR MALFORMED TOOL JSON
# ============================================================

def _repair_common_tool_json(text):
    """
    Repair common malformed tool JSON generated by Qwen.

    Examples:

        {"filesystem.delete_file":"path":"test.txt"}

    becomes:

        {
            "tool": "filesystem.delete_file",
            "args": {
                "path": "test.txt"
            }
        }

    Also supports multiple arguments such as:

        {"filesystem.create_file":"path":"test.txt","content":""}
    """

    if not text:
        return None

    text = _clean_response(text).strip()

    # --------------------------------------------------------
    # First: try valid JSON
    # --------------------------------------------------------

    try:

        obj = json.loads(text)

        if _is_valid_tool_call(obj):
            return obj

        # The text is valid JSON but not in {"tool","args"}
        # shape -- check for the nested-namespace mistake
        # (e.g. {"browser": {"open": "url"}}) before giving up.
        nested_repair = _repair_nested_namespace_tool_json(obj)

        if nested_repair:
            return nested_repair

    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    # --------------------------------------------------------
    # Only attempt repair on object-looking text
    # --------------------------------------------------------

    if not (
        text.startswith("{")
        and text.endswith("}")
    ):
        return None

    # --------------------------------------------------------
    # Known tool prefixes (dotted-string malformed JSON, e.g.
    # {"filesystem.delete_file":"path":"test.txt"})
    # --------------------------------------------------------

    tool_name = None

    for prefix in known_prefixes:

        marker = '"' + prefix

        start = text.find(marker)

        if start == -1:
            continue

        end = text.find('"', start + 1)

        if end == -1:
            continue

        candidate = text[
            start + 1:end
        ]

        if candidate.startswith(prefix):

            tool_name = candidate
            break

    if not tool_name:
        return None

    # --------------------------------------------------------
    # Get content after tool name
    # --------------------------------------------------------

    tool_pos = text.find(
        '"' + tool_name + '"'
    )

    if tool_pos == -1:
        return None

    remainder = text[
        tool_pos + len(tool_name) + 2:
    ].strip()

    # Usually starts with :
    if remainder.startswith(":"):
        remainder = remainder[1:].strip()

    # --------------------------------------------------------
    # Parse malformed arguments
    #
    # "path":"test.txt"
    # "path":"test.txt","content":"hello"
    # --------------------------------------------------------

    args = {}

    while remainder:

        remainder = remainder.strip()

        # Remove separators
        while remainder.startswith(","):
            remainder = remainder[1:].strip()

        # Remove final }
        if remainder == "}":
            break

        if remainder.endswith("}"):
            remainder = remainder[:-1].strip()

        if not remainder:
            break

        # ----------------------------------------------------
        # Argument name
        # ----------------------------------------------------

        if not remainder.startswith('"'):
            break

        remainder = remainder[1:]

        name_end = remainder.find('"')

        if name_end == -1:
            break

        arg_name = remainder[:name_end]

        remainder = remainder[
            name_end + 1:
        ].strip()

        # ----------------------------------------------------
        # Colon
        # ----------------------------------------------------

        if not remainder.startswith(":"):
            break

        remainder = remainder[1:].strip()

        # ----------------------------------------------------
        # String value
        # ----------------------------------------------------

        if remainder.startswith('"'):

            remainder = remainder[1:]

            value_end = None
            escaped = False

            for i, char in enumerate(remainder):

                if char == '"' and not escaped:
                    value_end = i
                    break

                if char == "\\" and not escaped:
                    escaped = True
                else:
                    escaped = False

            if value_end is None:
                break

            arg_value = remainder[:value_end]

            # Unescape JSON-style strings
            try:
                arg_value = json.loads(
                    '"' + arg_value + '"'
                )
            except Exception:
                pass

            args[arg_name] = arg_value

            remainder = remainder[
                value_end + 1:
            ].strip()

        # ----------------------------------------------------
        # Non-string JSON value
        # ----------------------------------------------------

        else:

            value_end = len(remainder)

            comma_pos = remainder.find(",")

            brace_pos = remainder.find("}")

            positions = [
                p for p in (
                    comma_pos,
                    brace_pos
                )
                if p != -1
            ]

            if positions:
                value_end = min(positions)

            raw_value = remainder[
                :value_end
            ].strip()

            try:
                arg_value = json.loads(raw_value)
            except Exception:
                arg_value = raw_value.strip('"')

            args[arg_name] = arg_value

            remainder = remainder[
                value_end:
            ].strip()

        # ----------------------------------------------------
        # Continue if comma exists
        # ----------------------------------------------------

        if remainder.startswith(","):
            remainder = remainder[1:].strip()
            continue

        if remainder.startswith("}"):
            break

        if not remainder:
            break

        # Unexpected remainder
        break

    # --------------------------------------------------------
    # Return repaired tool call
    # --------------------------------------------------------

    if tool_name and isinstance(args, dict):

        return {
            "tool": tool_name,
            "args": args,
        }

    return None


# ============================================================
# EXTRACT JSON OBJECT FROM SURROUNDING TEXT
# ============================================================

def _extract_json_object(text):
    """
    Extract the first balanced JSON object from text.

    Example:

        Sure, I will delete it.
        {"tool":"filesystem.delete_file","args":{"path":"test.txt"}}

    Returns the JSON object portion.
    """

    if not text:
        return None

    start = text.find("{")

    if start == -1:
        return None

    depth = 0
    in_string = False
    escaped = False

    for i in range(start, len(text)):

        char = text[i]

        # Handle escaped characters inside strings
        if in_string:

            if escaped:
                escaped = False
                continue

            if char == "\\":
                escaped = True
                continue

            if char == '"':
                in_string = False

            continue

        # Start string
        if char == '"':
            in_string = True
            continue

        # Object depth
        if char == "{":

            depth += 1

        elif char == "}":

            depth -= 1

            if depth == 0:
                return text[
                    start:i + 1
                ]

    return None


# ============================================================
# POST TO OLLAMA WITH RETRY/BACKOFF
# ============================================================

def _post_chat_with_retry(payload):
    """
    POST to the Ollama /api/chat endpoint, retrying a few times
    with backoff if the connection is refused or times out.

    This covers the common case where Ollama's background
    service hasn't finished starting yet (e.g. right after
    Windows boot/login) when JARVIS makes its first request.

    Real HTTP errors (bad model, bad request, etc.) are NOT
    retried -- raise_for_status() will raise immediately for
    those on the first attempt that gets a response.
    """

    last_error = None

    delay = OLLAMA_RETRY_DELAY_SECONDS

    for attempt in range(1, OLLAMA_MAX_RETRIES + 1):

        try:

            response = requests.post(
                f"{OLLAMA_HOST}/api/chat",
                json=payload,
                timeout=180,
            )

            response.raise_for_status()

            return response

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as e:

            last_error = e

            if attempt < OLLAMA_MAX_RETRIES:

                print(
                    f"[OLLAMA] Connection attempt {attempt} "
                    f"failed ({e}). Retrying in {delay:.1f}s..."
                )

                time.sleep(delay)

                delay *= OLLAMA_RETRY_BACKOFF

                continue

            raise

    if last_error:
        raise last_error

    raise RuntimeError(
        "Failed to reach Ollama for an unknown reason."
    )


# ============================================================
# CHAT
# ============================================================

def chat(messages, tools_text=""):
    """
    Send a conversation to local Ollama/Qwen.
    """

    msgs = [
        {
            "role": "system",
            "content": (
                SYSTEM_PROMPT
                + "\n\nTOOLS:\n"
                + tools_text
            ),
        }
    ]

    msgs.extend(messages)

    response = _post_chat_with_retry(
        {
            "model": OLLAMA_MODEL,
            "messages": msgs,
            "stream": False,
        }
    )

    data = response.json()

    content = (
        data
        .get("message", {})
        .get("content", "")
    )

    return _clean_response(content)


# ============================================================
# TOOL CALL DETECTOR
# ============================================================

def is_tool_call(text):
    """
    Detect and parse a JARVIS tool call.

    Returns:

        dict -> valid tool call

        None -> normal assistant response
    """

    if not text:
        return None

    text = _clean_response(text)

    if not text:
        return None

    # --------------------------------------------------------
    # 1. Entire response is valid JSON
    # --------------------------------------------------------

    try:

        obj = json.loads(text)

        if _is_valid_tool_call(obj):
            return obj

        # Whole text parsed as JSON, but in the wrong schema --
        # try the nested-namespace repair (e.g. what a model
        # produces for {"browser": {"open": "url"}}).
        nested_repair = _repair_nested_namespace_tool_json(obj)

        if nested_repair and _is_valid_tool_call(nested_repair):
            return nested_repair

    except (
        json.JSONDecodeError,
        TypeError,
        ValueError,
    ):
        pass

    # --------------------------------------------------------
    # 2. JSON surrounded by normal text
    # --------------------------------------------------------

    candidate = _extract_json_object(text)

    if candidate:

        try:

            obj = json.loads(candidate)

            if _is_valid_tool_call(obj):
                return obj

            nested_repair = _repair_nested_namespace_tool_json(obj)

            if nested_repair and _is_valid_tool_call(nested_repair):
                return nested_repair

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ):
            pass

        # Try repairing extracted JSON
        repaired = _repair_common_tool_json(
            candidate
        )

        if repaired and _is_valid_tool_call(
            repaired
        ):
            return repaired

    # --------------------------------------------------------
    # 3. Repair malformed Qwen JSON
    # --------------------------------------------------------

    repaired = _repair_common_tool_json(text)

    if repaired and _is_valid_tool_call(
        repaired
    ):
        return repaired

    return None