# Excalidraw Plugin

Gnarlysoft-branded Excalidraw diagram creator. Generates `.excalidraw` JSON files with a dark mode purple theme matching the Gnarlysoft CRM design system.

## Theme

- **Canvas**: `#1a1a1a` (dark background)
- **Primary accent**: `#8b5cf6` / `#7c3aed` (purple)
- **Text**: `#c4b5fd` (light purple titles), `#fafafa` (body on shapes), `#a3a3a3` (muted details)
- **Semantic colors**: Orange triggers, green success, red errors, yellow decisions, light purple AI/LLM

## Usage

```
/excalidraw-diagram [description of what to visualize]
```

## First-Time Setup

```bash
cd plugins/excalidraw/skills/excalidraw-diagram/references
uv sync
uv run playwright install chromium
```

## Customization

Edit `skills/excalidraw-diagram/references/color-palette.md` to change brand colors. All other skill files reference it as the single source of truth.
