# Nano Banana Pro Prompting Reference

Source: [Google Cloud Blog - Ultimate Nano Banana Prompting Guide](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana)

## Table of Contents

- [Core Principles](#core-principles)
- [Prompt Formula](#prompt-formula)
- [Text Rendering](#text-rendering)
- [Creative Director Techniques](#creative-director-techniques)
- [Blog Post Image Patterns](#blog-post-image-patterns)

## Core Principles

- **Be specific**: Concrete details on subject, lighting, composition.
- **Positive framing**: Describe what you want, not what you don't. Say "empty street" not "no cars."
- **Control the camera**: Use photographic/cinematic terms: "low angle", "aerial view", "macro lens."
- **Start with a strong verb**: Tell the model the primary operation.
- **Iterate conversationally**: Refine with follow-up prompts.

## Prompt Formula

```
[Subject] + [Action] + [Location/context] + [Composition] + [Style]
```

Example: "A striking fashion model wearing a tailored brown dress, sleek boots, and holding a structured handbag. Posing with a confident stance, slightly turned. A seamless, deep cherry red studio backdrop. Medium-full shot, center-framed. Fashion magazine editorial, shot on medium-format analog film, pronounced grain, high saturation, cinematic lighting."

### With Reference Images

```
[Reference images] + [Relationship instruction] + [New scenario]
```

## Text Rendering

Nano Banana Pro excels at sharp, legible text in 10+ languages.

Rules:
- **Use quotes**: Enclose desired text in quotes: `"Happy Birthday"`, `"URBAN EXPLORER"`
- **Choose a font**: Describe typography: "bold, white, sans-serif font" or "Century Gothic 12px font"
- **Translate**: Write prompt in one language, specify target language for output
- **Text-first hack**: Generate text concepts conversationally first, then ask for the image with that text

## Creative Director Techniques

### Lighting
- Studio setups: "three-point softbox setup"
- Dramatic: "Chiaroscuro lighting with harsh, high contrast"
- Natural: "Golden hour backlighting creating long shadows"

### Camera and Lens
- Hardware: GoPro (immersive/distorted), Fujifilm (authentic color), disposable camera (raw/nostalgic)
- Lens: "shallow depth of field (f/1.8)", "wide-angle lens" (vast scale), "macro lens" (details)
- Angle: "low-angle shot", "aerial view", "bird's eye"

### Color Grading
- Nostalgic: "as if on 1980s color film, slightly grainy"
- Modern moody: "cinematic color grading with muted teal tones"
- Vibrant: "high saturation, Kodak Portra 400 film stock"

### Materiality and Texture
- Don't say "suit jacket" — say "navy blue tweed suit jacket"
- Don't say "armor" — say "ornate elven plate armor, etched with silver leaf patterns"
- For mockups: "minimalist ceramic coffee mug", "brushed aluminum laptop"

## Blog Post Image Patterns

When generating images for blog posts (cover images, section headers, inline figures):

### Cover Images
- Use **16:9** or **3:2** aspect ratio for wide hero images
- Use **1:1** for card thumbnails
- Keep compositions clean with negative space for text overlay
- Prompt pattern: "Abstract [concept] visualization, dark background with [accent color] highlights, clean geometric shapes, editorial style, minimal, professional"

### Section Header Icons
- Use **1:1** at **1K** resolution
- For icons and simple illustrations, use the local selfhst/icons cache at `/tmp/selfhst-icons/`:
  - PNG: `/tmp/selfhst-icons/png/{name}.png`
  - SVG: `/tmp/selfhst-icons/svg/{name}.svg`
  - WebP: `/tmp/selfhst-icons/webp/{name}.webp`
  - Browse the full directory at [selfh.st/icons](https://selfh.st/icons)
- When generating custom icons: "Flat icon of [concept], single color on transparent background, clean vector style, minimal detail"

### Inline Figures / Diagrams
- Use **16:9** or **3:2** for landscape figures
- For technical concepts: "Clean technical illustration of [concept], dark mode color scheme, purple and blue accents, professional infographic style"
- For process flows: Consider Excalidraw via the excalidraw skill instead of image generation

### Style Consistency
- Establish a palette prompt prefix for the project and reuse it across all images
- Example prefix: "Dark background (#0a0a0f), purple accent (#7c5bf0), clean editorial style, "
- Append this to every generation prompt for visual coherence across a blog
