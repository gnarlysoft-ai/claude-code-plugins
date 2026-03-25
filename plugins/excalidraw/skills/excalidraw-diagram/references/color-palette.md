# Color Palette & Brand Style — Gnarlysoft Dark Theme

**This is the single source of truth for all colors and brand-specific styles.** Derived from the Gnarlysoft CRM shadcn dark mode theme. All diagrams use a dark canvas with purple-accented elements.

---

## Shape Colors (Semantic)

Colors encode meaning, not decoration. Each semantic purpose has a fill/stroke pair. Fills are muted/dark; strokes are vivid for contrast on the dark canvas.

| Semantic Purpose | Fill | Stroke |
|------------------|------|--------|
| Primary/Neutral | `#3b3547` | `#8b5cf6` |
| Secondary | `#2a2a2a` | `#7c3aed` |
| Tertiary | `#383838` | `#6d28d9` |
| Start/Trigger | `#2d2320` | `#f97316` |
| End/Success | `#1a2e22` | `#22c55e` |
| Warning/Reset | `#2e1f1f` | `#ef4444` |
| Decision | `#2e2a1a` | `#eab308` |
| AI/LLM | `#2e2545` | `#c4b5fd` |
| Inactive/Disabled | `#2a2a2a` | `#6d28d9` (use dashed stroke) |
| Error | `#2e1a1a` | `#ef4444` |

**Rule**: Always pair a vivid stroke with a dark/muted fill for contrast on the dark canvas.

---

## Text Colors (Hierarchy)

Use color on free-floating text to create visual hierarchy without containers.

| Level | Color | Use For |
|-------|-------|---------|
| Title | `#c4b5fd` | Section headings, major labels (light purple) |
| Subtitle | `#8b5cf6` | Subheadings, secondary labels (medium purple) |
| Body/Detail | `#a3a3a3` | Descriptions, annotations, metadata (muted gray) |
| On dark fills | `#fafafa` | Text inside dark-colored shapes |
| On vivid fills | `#1a1a1a` | Text inside bright-colored shapes (rare in dark mode) |

---

## Evidence Artifact Colors

Used for code snippets, data examples, and other concrete evidence inside technical diagrams.

| Artifact | Background | Text Color |
|----------|-----------|------------|
| Code snippet | `#1a1a1a` | Syntax-colored (language-appropriate) |
| JSON/data example | `#1a1a1a` | `#22c55e` (green) |

---

## Default Stroke & Line Colors

| Element | Color |
|---------|-------|
| Arrows | Use the stroke color of the source element's semantic purpose |
| Structural lines (dividers, trees, timelines) | `#8b5cf6` (primary purple) or `#a3a3a3` (muted gray) |
| Marker dots (fill + stroke) | `#7c3aed` fill, `#8b5cf6` stroke |

---

## Background

| Property | Value |
|----------|-------|
| Canvas background | `#1a1a1a` |

---

## Brand Reference

These colors are derived from the Gnarlysoft CRM dark mode theme:
- **Primary purple**: `#7c3aed` (oklch 0.438 0.218 303.724)
- **Accent purple**: `#8b5cf6` (oklch 0.627 0.265 303.9)
- **Light purple**: `#c4b5fd` (oklch 0.827 0.119 306.383)
- **Dark background**: `#1a1a1a` (oklch 0.145 0 0)
- **Card background**: `#2a2a2a` (oklch 0.205 0 0)
- **Muted background**: `#383838` (oklch 0.269 0 0)
- **Foreground text**: `#fafafa` (oklch 0.985 0 0)
- **Muted text**: `#a3a3a3` (oklch 0.708 0 0)
