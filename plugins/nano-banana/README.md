# Nano Banana

AI image generation plugin using Google's Nano Banana Pro (Gemini 3 Pro Image) model.

## Features

- Text-to-image generation with configurable aspect ratio and resolution
- Reference image support (up to 14 images) for logo compositions and style transfer
- Vendor logo workflow via selfhst/icons repository
- Comprehensive prompting guide for blog post imagery

## Requirements

- **uv** — Python package manager
- **GEMINI_API_KEY** or **GOOGLE_API_KEY** — Get one at https://aistudio.google.com/apikey

## Usage

```
/gnarlysoft:nano-banana "A clean hero image with dark background and purple accents" -o cover.png --aspect-ratio 16:9 --size 2K
```

With reference images (vendor logos):

```
/gnarlysoft:nano-banana "Compose these logos into a hero image on a dark background" \
  -r /tmp/selfhst-icons/png/claude.png -r /tmp/selfhst-icons/png/docker.png \
  -o cover.png --aspect-ratio 16:9 --size 2K
```
