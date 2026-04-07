#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""Generate an image using Google's Nano Banana Pro (Gemini 3 Pro Image) model."""

import argparse
import os
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an image with Nano Banana Pro")
    parser.add_argument("prompt", help="The image generation prompt")
    parser.add_argument(
        "-o",
        "--output",
        default="generated_image.png",
        help="Output file path (default: generated_image.png)",
    )
    parser.add_argument(
        "-r",
        "--reference",
        action="append",
        default=[],
        help="Reference image path (can be used multiple times, up to 14)",
    )
    parser.add_argument(
        "--aspect-ratio",
        default="1:1",
        choices=[
            "1:1", "1:4", "1:8", "2:3", "3:2", "3:4",
            "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
        ],
        help="Aspect ratio (default: 1:1)",
    )
    parser.add_argument(
        "--size",
        default="1K",
        choices=["512", "1K", "2K", "4K"],
        help="Image resolution (default: 1K)",
    )
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print(
            "Error: No API key found.\n\n"
            "Set one of these environment variables:\n"
            "  export GEMINI_API_KEY='your-key-here'\n"
            "  export GOOGLE_API_KEY='your-key-here'\n\n"
            "Get a key at: https://aistudio.google.com/apikey",
            file=sys.stderr,
        )
        sys.exit(1)

    if len(args.reference) > 14:
        print("Error: Maximum 14 reference images allowed.", file=sys.stderr)
        sys.exit(1)

    from PIL import Image as PILImage

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating image with Nano Banana Pro...")
    print(f"  Prompt: {args.prompt}")
    print(f"  Aspect ratio: {args.aspect_ratio}")
    print(f"  Size: {args.size}")
    if args.reference:
        print(f"  Reference images: {len(args.reference)}")
        for ref in args.reference:
            print(f"    - {ref}")
    print(f"  Output: {output_path}")

    contents: list = []
    for ref_path in args.reference:
        ref = Path(ref_path)
        if not ref.exists():
            print(f"Error: Reference image not found: {ref}", file=sys.stderr)
            sys.exit(1)
        contents.append(PILImage.open(ref))
    contents.append(args.prompt)

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=args.aspect_ratio,
                image_size=args.size,
            ),
        ),
    )

    saved = False
    for part in response.parts:
        if part.text is not None:
            print(f"\nModel notes: {part.text}")
        elif part.inline_data is not None:
            image = part.as_image()
            image.save(str(output_path))
            saved = True
            print(f"\nSaved to {output_path}")

    if not saved:
        print("Error: No image was generated. Try rephrasing the prompt.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
