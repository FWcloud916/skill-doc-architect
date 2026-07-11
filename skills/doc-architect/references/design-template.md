# Template: `DESIGN.md` (UI design-system module)

A plain-markdown design-system document that AI agents read before generating or
restyling UI, so output stays visually consistent with the project's design language.
The format follows the Google Stitch `DESIGN.md` convention (ecosystem of examples:
[VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)): a
**machine contract** (YAML frontmatter of design tokens) plus **human/agent guidance**
(prose sections). Any tool-agnostic AI agent picks it up from the repo root.

**Applicability:** generate only when the project renders a UI — the matched stack
file carries the `> **UI surface:** yes` marker in its header blockquote — and only
with the user's explicit opt-in. Mode G: offer it when a UI is planned. Mode B: offer
it at the step-3 plan gate; selected → discovery additionally reads the theme/token
sources (§Extraction map below). Skipped → one-line reason in the module-selection
report, like any other module.

**Location: repo root**, next to `AGENTS.md` — the cross-tool convention is that
agents find `DESIGN.md` at the root. It does NOT use the docs frontmatter convention;
its YAML frontmatter IS the token block below.

---

## Skeleton

```markdown
---
colors:
  primary: "#RRGGBB"
  primary-active: "#RRGGBB"
  background: "#RRGGBB"
  surface: "#RRGGBB"
  text-primary: "#RRGGBB"
  text-secondary: "#RRGGBB"
  border: "#RRGGBB"
  accent: "#RRGGBB"
  success: "#RRGGBB"
  warning: "#RRGGBB"
  error: "#RRGGBB"
typography:
  heading-1: { fontFamily: "…", fontSize: "…", fontWeight: 000, lineHeight: "…", letterSpacing: "…" }
  heading-2: { fontFamily: "…", fontSize: "…", fontWeight: 000, lineHeight: "…", letterSpacing: "…" }
  body:      { fontFamily: "…", fontSize: "…", fontWeight: 000, lineHeight: "…", letterSpacing: "…" }
  caption:   { fontFamily: "…", fontSize: "…", fontWeight: 000, lineHeight: "…", letterSpacing: "…" }
  button:    { fontFamily: "…", fontSize: "…", fontWeight: 000, lineHeight: "…", letterSpacing: "…" }
rounded: { none: "0", sm: "…", md: "…", lg: "…", full: "9999px" }
spacing: { xs: "…", sm: "…", md: "…", lg: "…", xl: "…", xxl: "…" }
components:
  button-primary: { background: "{colors.primary}", color: "…", rounded: "{rounded.md}", padding: "{spacing.sm} {spacing.md}" }
  card:           { background: "{colors.surface}", rounded: "{rounded.lg}", shadow: "…" }
  input:          { border: "1px solid {colors.border}", rounded: "{rounded.md}" }
---
# <Project> Design System

## Overview            <visual theme & atmosphere, 2–4 sentences>
## Colors              <semantic roles, usage rules, contrast notes>
## Typography          <families, scale, hierarchy rules>
## Layout              <spacing-scale usage, grid, whitespace philosophy>
## Elevation & Depth   <shadow levels, layering rules>
## Shapes              <radius-scale usage per component class>
## Components          <per-component look + states: hover/active/disabled/error>
## Responsive Behavior <breakpoints, adaptation rules; fixed-window desktop → N/A>
## Do's and Don'ts     <paired bullets — guardrails and anti-patterns>
## Agent Prompt Guide  <how an agent applies this file when generating UI>
```

Required prose sections: Overview, Colors, Typography, Layout, Components,
Do's and Don'ts. The rest (Elevation & Depth, Shapes, Responsive Behavior,
Agent Prompt Guide) MAY read `N/A — <reason>`.

## Writing rules

- **Tokens are the machine contract**: every hex value or size named in prose MUST
  match its frontmatter token; every `{group.key}` reference in `components` MUST
  resolve to a defined token. (Checked: `audit-checklist.md` §2 DESIGN.md block.)
- **Mode B — extract, never invent**: every token value MUST be traceable to a theme
  source read this session (§Extraction map). Not found in code →
  `TODO — not found in code`; never invent brand values (same rule as commands:
  never write what you did not find).
- **Mode G**: undecided values read `TODO — not yet designed` (same convention as
  project-overview's TBD sections).
- **Semantic token names** (`primary`, `surface`, `text-primary`…), never literal
  ones (`blue-500`) — the name states the role, the value states the paint.
- **Dark mode**: when the code defines two palettes, nest `colors.light` /
  `colors.dark` and add a Dark Mode subsection under Colors; a single palette stays
  a flat `colors` map.
- A themeless codebase (hard-coded styles everywhere) still qualifies: extract the
  observed recurring values and flag the absence of a theme layer in the Overview.

## Extraction map (Mode B — where tokens live per ecosystem)

Read only the sources for the detected surface(s); the matched stack file's
§Diff → doc section map names the same paths for Mode U-1 syncing.

| Stack | Token sources to read |
|---|---|
| Frontend web | `tailwind.config.{js,ts}` `theme`, CSS custom properties (`:root` in global/tokens CSS), UI-lib theme objects (MUI/Chakra/Mantine, styled-components, vanilla-extract), `design-tokens.json` |
| React Native | theme constant modules / `StyleSheet` constants, NativeWind (tailwind config), tamagui/restyle/styled-components themes |
| Flutter | `ThemeData` / `ColorScheme` / `TextTheme` passed to `MaterialApp(theme:)`, `ThemeExtension` classes |
| Apple (iOS/macOS) | asset-catalog colors (`*.xcassets/**/*.colorset`), SwiftUI `Color`/`Font` extensions, `UIAppearance` setup |
| Android | `res/values/colors.xml`, `themes.xml`/`styles.xml`, Compose `MaterialTheme` (`ColorScheme`/`Typography` objects) |
| Electron | renderer theme sources — same as Frontend web |
| Tauri | frontend theme sources — same as Frontend web |
| Windows desktop (.NET) | XAML `ResourceDictionary` (`App.xaml`, `Themes/*.xaml`): Colors/Brushes/Styles, ThemeResources |

## Mode G design interview

Ask (AskUserQuestion or conversational), then fill the skeleton from the answers:

- Existing brand assets or design guidelines? (logo, brand colors, a style guide)
- Overall mood: minimal / playful / enterprise / editorial / …?
- Light, dark, or both?
- Known primary/accent colors (hex if decided)?
- Font preferences or constraints (licensing, system-font-only)?
- Density: compact vs airy?
- 2–3 reference apps/sites whose look the user admires?

**Starter-template route**: when the user has no design system yet, offer picking a
starter `DESIGN.md` from
[awesome-design-md](https://github.com/VoltAgent/awesome-design-md) (70+ examples)
that matches the stated mood, then adapt names and values to the interview answers.
Record the chosen starter in the file's Overview. Remaining gaps stay
`TODO — not yet designed`.

## Coupling with AGENTS.md

When this module is selected, add one row to the AGENTS.md task→doc table:

```markdown
| Building or restyling UI (colors, typography, components) | [DESIGN.md](DESIGN.md) |
```

Unlike `PROGRESS.md`, `DESIGN.md` IS task routing — an agent about to build UI must
be routed to it — so it belongs in the table.

## Maintenance

- **Mode U-1**: theme-source diffs map to `DESIGN.md` via the matched stack file's
  §Diff → doc section map and `audit-checklist.md` §1 — tokens first, then the
  matching prose section (Colors/Typography/Shapes/Components).
- **Mode U-2 / Mode B self-check**: the §2 DESIGN.md invariant block
  (`audit-checklist.md`) — frontmatter parses, references resolve, no prose/token
  drift, no docs-only ghost colors.
