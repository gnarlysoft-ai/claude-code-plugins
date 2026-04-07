---
name: "gnarlysoft:nano-banana"
description: "Generate images using Google's Nano Banana Pro (Gemini 3 Pro Image) model. Use when: (1) the user asks to generate, create, or make an image/picture/photo/visual, (2) the user needs a blog post cover image, hero image, or illustration, (3) the user asks for AI image generation, (4) the user mentions nano banana or Gemini image generation. Do NOT use for diagrams or flowcharts (use excalidraw skill instead)."
user-invocable: true
argument-hint: "[prompt for image generation]"
---

# Nano Banana

Generate images with Google's Nano Banana Pro via a single `uv run` script.

## API Key Check

Before running the script, verify a key is set:

```bash
echo "${GEMINI_API_KEY:-${GOOGLE_API_KEY:-NOT SET}}"
```

If `NOT SET`, stop and tell the user:

> You need a Google API key. Get one at https://aistudio.google.com/apikey then set it:
> `export GEMINI_API_KEY='your-key-here'`

## Generating an Image

```bash
uv run SKILL_DIR/scripts/generate.py "your prompt here" -o output.png --aspect-ratio 16:9 --size 2K
```

With reference images:

```bash
uv run SKILL_DIR/scripts/generate.py "Compose these logos into a hero image on a dark background" \
  -r /tmp/selfhst-icons/png/claude.png -r /tmp/selfhst-icons/png/excalidraw.png -r /tmp/selfhst-icons/png/outline.png \
  -o output.png --aspect-ratio 16:9 --size 2K
```

Arguments:
- **prompt** (required): The image generation prompt
- **-o / --output**: Output file path (default: `generated_image.png`)
- **-r / --reference**: Reference image path (repeatable, up to 14 images). Nano Banana uses these as visual input — essential for accurate logos, products, or character consistency.
- **--aspect-ratio**: `1:1` (default), `3:2`, `2:3`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`, `1:4`, `4:1`, `1:8`, `8:1`
- **--size**: `512`, `1K` (default), `2K`, `4K`

`SKILL_DIR` resolves to this skill's directory at runtime. Use it as the prefix for the script path.

## Using Vendor Logos and Icons

**CRITICAL**: When the user's prompt involves brand logos (e.g. "Claude logo", "Docker logo", "Outline logo"), NEVER ask the model to imagine/generate logos from memory. Logos generated from memory will be wrong. Instead, use the real logos from the local icon cache and pass them as reference images.

### Icon Cache: selfhst/icons

The [selfhst/icons](https://github.com/selfhst/icons) repo has thousands of vendor/service icons. A local shallow clone is kept at `/tmp/selfhst-icons/`.

**Before looking up any logos, sync the cache:**

```bash
if [ -d /tmp/selfhst-icons/.git ]; then
  git -C /tmp/selfhst-icons pull --ff-only
else
  git clone --depth 1 https://github.com/selfhst/icons.git /tmp/selfhst-icons
fi
```

Run this once per session. After that, all icons are available locally:

- **PNG**: `/tmp/selfhst-icons/png/{name}.png`
- **SVG**: `/tmp/selfhst-icons/svg/{name}.svg`
- **WebP**: `/tmp/selfhst-icons/webp/{name}.webp`

**Naming conventions** — filenames are lowercase, hyphenated:
- Direct match: `docker.png`, `github.png`, `claude.png`, `outline.png`
- Multi-word: `visual-studio-code.png`, `google-chrome.png`
- Variants: `{name}-light.png` (light theme), `{name}-dark.png` (dark theme)

**Workflow when logos are needed:**

1. Sync the icon cache (command above)
2. Identify which vendor/service logos the user wants
3. Reason about the filename: brand name -> lowercase, hyphenated (e.g. "Visual Studio Code" -> `visual-studio-code`)
4. Check the file exists: `ls /tmp/selfhst-icons/png/{name}.png`
5. If not found, search: `ls /tmp/selfhst-icons/png/ | grep -i '<keyword>'`
6. Pass files as `-r` reference images to the generate script
7. In the prompt, refer to them explicitly: "Using these reference logos, compose them into..."

## Crafting Effective Prompts

Read [references/prompting-guide.md](references/prompting-guide.md) for the full prompting reference. Key points:

**Formula**: `[Subject] + [Action] + [Location/context] + [Composition] + [Style]`

- Be specific and descriptive — no keyword spam ("4k, masterpiece, trending")
- Use positive framing: describe what you want, not what to exclude
- Use photographic terms: "low angle", "shallow depth of field (f/1.8)", "macro lens"
- Specify lighting: "three-point softbox", "golden hour backlighting", "chiaroscuro"
- Define materiality: "navy blue tweed" not "suit jacket"

**Text rendering**: Wrap text in quotes, specify font style, keep to 3-5 words max.

## Blog Post Images

When generating images for blog posts:

- **Cover/hero images**: Use `--aspect-ratio 16:9` or `3:2`, `--size 2K`. Keep compositions clean with space for text overlay.
- **Card thumbnails**: Use `--aspect-ratio 1:1`, `--size 1K`.
- **Inline figures**: Use `--aspect-ratio 16:9`, `--size 1K`.
- **Style consistency**: Establish a palette prefix and reuse across all images for visual coherence.

For **diagrams and flowcharts**, use the excalidraw skill instead.

See [references/prompting-guide.md](references/prompting-guide.md) for detailed blog image patterns and style tips.
