# self-insight Design System — Pattern B (Dashboard)

> Light dashboard aesthetic, inspired by The Pattern / 16Personalities. Replaces the
> previous dark "iUMA Mystic" theme (2026-07-20 zero-based redesign; content unchanged,
> visual design only). Base system: `Projects/DESIGN.md` (iUMA Dark) — this project
> deliberately diverges to a light theme, see "What this file is NOT" below.

## design_system key
```
design_system: pattern-b-dashboard
```

## Color Tokens

| Token | Value | Usage |
|---|---|---|
| `--bg` | `#F5F4F0` | Page background |
| `--card` | `#FFFFFF` | Card / panel surface |
| `--ink` | `#191C22` | Primary text |
| `--sub` | `#5C6370` | Secondary text |
| `--faint` | `#8B909B` | De-emphasized text |
| `--line` | `#E8E5DE` | Borders, dividers |
| `--essence` / `--essence-bg` | `#4F46E5` / `#EEF0FE` | 本質 (personality) domain — indigo |
| `--money` / `--money-bg` | `#A16207` / `#FBF3E2` | 金運 (money) domain — gold |
| `--work` | `#1D4ED8` | 仕事 (work) domain — blue |
| `--relationships` | `#BE334E` | 人間関係 (relationships) domain — red |
| `--arc` / `--arc-bg` | `#0F766E` / `#E4F2F0` | 過去と未来 (life-arc) domain — teal |
| `--warn` / `--warn-bg` | `#B45309` / `#FDF1E3` | Warnings |

## Typography

| Role | Font | Notes |
|---|---|---|
| Headings | Inter | 600–800 |
| Body | Inter + Noto Sans JP | 400–700, 15–16px |
| Numbers / scores | Inter | Tabular nums |

No serif or monospace fonts (Cormorant Garamond, JetBrains Mono both removed 2026-07-20).

## Layout Principles

- **Information hierarchy**: Core Identity → 命式 → Monthly Forecast → Charts → Premium sections
- **Card pattern**: white `--card` surface, 1px border `--line`, `--radius: 18px`,
  shadow `0 1px 2px rgba(25,28,34,.04), 0 8px 24px rgba(25,28,34,.06)`
- **Section width**: max 860px centered
- **Grid**: CSS Grid, `repeat(auto-fit)` — no horizontal scroll on mobile

## Component Notes

- Chart.js: use direct hex `#4F46E5` / `#A16207` (not CSS vars — Chart.js cannot read vars);
  grid lines `rgba(25,28,34,0.07)`
- Content-generator `.py` files (core_identity.py, divination_forecast.py, monthly.py,
  eto_cross.py, premium_sections.py, charts.py, navigation.py, glossary.py) still embed
  a handful of literal dark-theme inline hex colors. Rather than rewriting those files,
  `sections/styles.py`'s `CSS` block ends with an attribute-selector override
  (`[style*="color:#a5b4fc"]{color:#4F46E5!important}` etc.) that re-themes them without
  touching content logic — same technique `CSS_FEMALE` already used. Extend this override
  block (not the content files) if a new literal inline color surfaces.
- Female users: `CSS_FEMALE` in `sections/styles.py` is a separate light-pink theme,
  applied via `gender_css = CSS_FEMALE if identity.sex == 'female' else ''` — untouched
  by the Pattern B redesign, wins via `!important`.

## What this file is NOT

- Not a mukonoso/editorial migration plan
- Not a dark theme — self-insight moved to light (Pattern B) 2026-07-20; the previous
  "iUMA Mystic" dark spec is superseded, not this file's current content
