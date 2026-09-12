import os
os.environ["HF_HOME"] = r"D:\huggingface_cache"
from pathlib import Path
from datetime import datetime

import torch
from diffusers import StableDiffusionPipeline


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "generated_images"

MODEL_ID = "runwayml/stable-diffusion-v1-5"


# ============================================================
# GLOBAL MODEL
# ============================================================

_pipe = None


# ============================================================
# LOAD MODEL
# ============================================================

def load_image_model():
    """
    Load Stable Diffusion model only once.
    """

    global _pipe

    if _pipe is not None:
        return _pipe

    print("\n[IMAGE] Loading image generation model...")
    print("[IMAGE] This may take time on the first run.")

    try:

        device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        dtype = (
            torch.float16
            if device == "cuda"
            else torch.float32
        )

        pipe = StableDiffusionPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=dtype,
        )

        pipe = pipe.to(device)

        # Memory optimization
        if device == "cuda":

            try:
                pipe.enable_attention_slicing()
            except Exception:
                pass

        _pipe = pipe

        print(
            f"[IMAGE] Model loaded successfully on {device.upper()}."
        )

        return _pipe

    except Exception as e:

        raise RuntimeError(
            f"Failed to load image generation model: {e}"
        )


# ============================================================
# BUILD OUTPUT PATH
# ============================================================

def _build_output_path():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    return (
        OUTPUT_DIR
        / f"jarvis_image_{timestamp}.png"
    )


# ============================================================
# GENERATE IMAGE
# ============================================================

def generate_image(
    prompt,
    width=512,
    height=512,
    steps=30,
    guidance_scale=7.5,
):
    """
    Generate an image using Stable Diffusion.

    Returns:
        SUCCESS: ...
        ERROR: ...
    """

    try:

        if not prompt:

            return (
                "ERROR: Image prompt is empty."
            )

        prompt = str(prompt).strip()

        if not prompt:

            return (
                "ERROR: Image prompt is empty."
            )

        print(
            "\n[IMAGE] Generating image..."
        )

        print(
            f"[IMAGE] Prompt: {prompt}"
        )

        pipe = load_image_model()

        # Generate image
        result = pipe(
            prompt=prompt,
            width=int(width),
            height=int(height),
            num_inference_steps=int(steps),
            guidance_scale=float(guidance_scale),
        )

        image = result.images[0]

        output_path = _build_output_path()

        image.save(
            output_path
        )

        if not output_path.exists():

            return (
                "ERROR: Image generation finished but "
                "the output file was not created."
            )

        return (
            "SUCCESS: Image generated successfully.\n"
            f"PATH: {output_path.resolve()}"
        )

    except Exception as e:

        return (
            f"ERROR: Image generation failed: {e}"
        )


# ============================================================
# QUICK TEST
# ============================================================

if __name__ == "__main__":

    result = generate_image(
        "A futuristic AI robot standing in a cyberpunk city, cinematic lighting"
    )

    print(result)