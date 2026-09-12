import base64
import requests
from pathlib import Path

from config import OLLAMA_HOST


# ============================================================
# VISION MODEL
# ============================================================

VISION_MODEL = "qwen2.5vl:3b"


# ============================================================
# VALIDATE IMAGE
# ============================================================

def _validate_image(image_path):

    path = Path(image_path)

    if not path.exists():

        return (
            None,
            f"ERROR: Image file does not exist: {path}"
        )

    if not path.is_file():

        return (
            None,
            f"ERROR: This is not a valid image file: {path}"
        )

    valid_extensions = (
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".bmp",
    )

    if path.suffix.lower() not in valid_extensions:

        return (
            None,
            "ERROR: Unsupported image format. "
            "Supported formats are PNG, JPG, JPEG, WEBP, and BMP."
        )

    return path, None


# ============================================================
# ENCODE IMAGE
# ============================================================

def _encode_image(image_path):

    try:

        with open(
            image_path,
            "rb"
        ) as file:

            encoded = base64.b64encode(
                file.read()
            )

            return encoded.decode(
                "utf-8"
            )

    except Exception as e:

        raise RuntimeError(
            f"Could not encode image: {e}"
        )


# ============================================================
# ANALYZE IMAGE
# ============================================================

def analyze_image(
    image_path,
    question="Describe this image in detail."
):
    """
    Analyze an image using Qwen Vision through Ollama.

    Parameters:
        image_path: Path to image
        question: What JARVIS should analyze

    Returns:
        SUCCESS: ...
        ERROR: ...
    """

    try:

        path, error = _validate_image(
            image_path
        )

        if error:

            return error

        if not question:

            question = (
                "Describe this image in detail."
            )

        image_base64 = _encode_image(
            path
        )

        print(
            "\n[VISION] Analyzing image..."
        )

        print(
            f"[VISION] Image: {path.name}"
        )

        payload = {

            "model": VISION_MODEL,

            "messages": [

                {

                    "role": "user",

                    "content": str(question),

                    "images": [

                        image_base64

                    ],

                }

            ],

            "stream": False,

        }

        response = requests.post(

            f"{OLLAMA_HOST}/api/chat",

            json=payload,

            timeout=300,

        )

        response.raise_for_status()

        data = response.json()

        answer = (

            data
            .get("message", {})
            .get("content", "")
            .strip()

        )

        if not answer:

            return (
                "ERROR: Vision model returned an empty response."
            )

        return (

            "SUCCESS: Image analyzed successfully.\n\n"
            + answer

        )

    except requests.exceptions.ConnectionError:

        return (
            "ERROR: Cannot connect to Ollama. "
            "Make sure Ollama is running."
        )

    except requests.exceptions.Timeout:

        return (
            "ERROR: Vision model took too long to respond."
        )

    except Exception as e:

        return (
            f"ERROR: Image analysis failed: {e}"
        )


# ============================================================
# DESCRIBE IMAGE
# ============================================================

def describe_image(image_path):

    return analyze_image(

        image_path,

        question=(
            "Describe this image clearly and in detail. "
            "Identify the important objects, people, text, "
            "scene, layout, and important visual details."
        ),

    )


# ============================================================
# OCR / TEXT EXTRACTION
# ============================================================

def read_image_text(image_path):

    return analyze_image(

        image_path,

        question=(
            "Read and extract all visible text from this image. "
            "Preserve the original text as accurately as possible. "
            "If text is unclear, say which part is unclear."
        ),

    )


# ============================================================
# DIAGRAM ANALYSIS
# ============================================================

def explain_diagram(image_path):

    return analyze_image(

        image_path,

        question=(
            "Analyze this diagram carefully. "
            "Explain each important component and describe "
            "how the components are connected. "
            "Explain the complete process shown in the diagram "
            "in simple language."
        ),

    )


# ============================================================
# IMAGE PROBLEM DETECTION
# ============================================================

def analyze_image_problem(image_path):

    return analyze_image(

        image_path,

        question=(
            "Analyze this image for possible errors, inconsistencies, "
            "problems, design issues, missing elements, "
            "or incorrect information. "
            "Explain the problems clearly."
        ),

    )


# ============================================================
# QUICK TEST
# ============================================================

if __name__ == "__main__":

    result = analyze_image(

        image_path="test.jpg",

        question=(
            "Describe this image in detail."
        ),

    )

    print(result)