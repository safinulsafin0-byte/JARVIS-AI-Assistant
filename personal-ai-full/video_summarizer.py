import re
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url):
    """
    Supports:
    https://www.youtube.com/watch?v=VIDEO_ID
    https://youtu.be/VIDEO_ID
    https://www.youtube.com/shorts/VIDEO_ID
    """

    if not url:
        return None

    url = url.strip()

    # youtube.com/watch?v=
    try:
        parsed = urlparse(url)

        if parsed.hostname:
            hostname = parsed.hostname.lower()

            if "youtube.com" in hostname:

                query = parse_qs(
                    parsed.query
                )

                if "v" in query:
                    return query["v"][0]

                parts = [
                    p for p in parsed.path.split("/")
                    if p
                ]

                if len(parts) >= 2:
                    if parts[0] in (
                        "shorts",
                        "embed",
                        "live",
                    ):
                        return parts[1]

            # youtu.be/VIDEO_ID
            if "youtu.be" in hostname:

                parts = [
                    p for p in parsed.path.split("/")
                    if p
                ]

                if parts:
                    return parts[0]

    except Exception:
        pass

    # Fallback
    match = re.search(
        r"(?:v=|youtu\.be/|shorts/|embed/|live/)"
        r"([A-Za-z0-9_-]{11})",
        url
    )

    if match:
        return match.group(1)

    return None


def get_transcript(url):
    """
    Get YouTube transcript.

    Tries:
    English
    Bangla
    Hindi
    Other available transcript
    """

    video_id = extract_video_id(url)

    if not video_id:
        return {
            "success": False,
            "error": "Could not extract YouTube video ID."
        }

    try:

        api = YouTubeTranscriptApi()

        # Try common languages first.
        try:

            transcript = api.fetch(
                video_id,
                languages=[
                    "en",
                    "bn",
                    "hi",
                ]
            )

        except Exception:

            # Try whatever transcript is available.
            transcript_list = api.list(
                video_id
            )

            transcript = None

            for item in transcript_list:

                try:
                    transcript = item.fetch()
                    break

                except Exception:
                    continue

            if transcript is None:
                raise Exception(
                    "No usable transcript found."
                )

        # Current API returns FetchedTranscript
        # with snippets containing text.
        lines = []

        for snippet in transcript:

            text = getattr(
                snippet,
                "text",
                ""
            )

            if text:
                lines.append(
                    text.strip()
                )

        full_text = " ".join(
            lines
        ).strip()

        if not full_text:

            return {
                "success": False,
                "error": (
                    "Transcript was found "
                    "but contained no text."
                )
            }

        return {
            "success": True,
            "video_id": video_id,
            "text": full_text,
        }

    except Exception as e:

        return {
            "success": False,
            "video_id": video_id,
            "error": str(e),
        }


def split_text(text, max_chars=7000):

    chunks = []

    text = text.strip()

    while len(text) > max_chars:

        cut = text.rfind(
            ". ",
            0,
            max_chars
        )

        if cut < max_chars // 2:
            cut = max_chars

        chunks.append(
            text[:cut].strip()
        )

        text = text[cut:].strip()

    if text:
        chunks.append(text)

    return chunks


def summarize_youtube(url, language="English"):

    transcript_result = get_transcript(
        url
    )

    if not transcript_result["success"]:

        return (
            "ERROR: Could not get the video transcript.\n"
            + transcript_result["error"]
        )

    transcript = transcript_result["text"]

    try:

        from llm.ollama_client import chat

        chunks = split_text(
            transcript,
            max_chars=7000
        )

        partial_summaries = []

        # ====================================================
        # SUMMARIZE EACH CHUNK
        # ====================================================

        for index, chunk in enumerate(
            chunks,
            start=1
        ):

            prompt = [
                {
                    "role": "system",
                    "content": (
                        "You are JARVIS, a local AI assistant. "
                        "Summarize the provided YouTube transcript "
                        "accurately. Do not invent information."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Summarize transcript section "
                        f"{index}/{len(chunks)}.\n\n"
                        f"Transcript:\n{chunk}\n\n"
                        "Give the important ideas, facts, "
                        "examples and conclusions."
                    ),
                },
            ]

            summary = chat(
                prompt,
                ""
            )

            partial_summaries.append(
                summary
            )

        # ====================================================
        # FINAL SUMMARY
        # ====================================================

        combined = "\n\n".join(
            partial_summaries
        )

        final_prompt = [
            {
                "role": "system",
                "content": (
                    "You are JARVIS. Create a clear and "
                    "accurate final summary of a YouTube video. "
                    "Use only the supplied summaries. "
                    "Do not invent information."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Create the final video summary "
                    f"in {language}.\n\n"
                    "Include:\n"
                    "1. What the video is about\n"
                    "2. Main points\n"
                    "3. Important details\n"
                    "4. Examples if present\n"
                    "5. Final conclusion\n\n"
                    "Transcript summaries:\n"
                    + combined
                ),
            },
        ]

        final_summary = chat(
            final_prompt,
            ""
        )

        return (
            "SUCCESS: Video summarized.\n\n"
            + final_summary
        )

    except Exception as e:

        return (
            "ERROR: Video summarization failed: "
            + str(e)
        )