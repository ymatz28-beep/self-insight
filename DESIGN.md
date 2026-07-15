# self-insight Design System — iUMA Mystic

> Variant of iUMA Dark tuned for divination / spiritual / psychological content.
> Base system: `Projects/DESIGN.md` (iUMA Dark). Overrides listed below.

## design_system key
```
design_system: iuma-mystic
```

## Color Tokens

| Token | Value | Usage |
|---|---|---|
| `--bg` | `#0D0B14` | Page background (deeper purple-black vs iUMA's `#0f1117`) |
| `--surface` | `#1A1626` | Card / panel surface |
| `--surface2` | `#251E36` | Nested surfaces, elevated panels |
| `--border` | `#2E2545` | Dividers, card outlines |
| `--gold` | `#C9A84C` | Primary accent (unchanged from iUMA) |
| `--accent` | `#8B5CF6` | Mystic purple — replaces iUMA indigo `#6366f1` |
| `--accent-warm` | `#A78BFA` | Lighter purple for hover/secondary emphasis |
| `--accent-green` | `#22c55e` | Chart line 2 (keep — already in use) |
| `--accent-teal` | `#14b8a6` | Monthly 西洋 tags |
| `--text-primary` | `#F5F0E8` | Warm white (vs iUMA pure `#ffffff`) |
| `--text-secondary` | `#A89EC0` | Muted warm purple-grey |
| `--text-muted` | `#6B6285` | De-emphasized text |

## Typography

| Role | Font | Notes |
|---|---|---|
| Display / taglines | Cormorant Garamond | 400/600, italic for poetic lines |
| Headings | Inter | 600-700 |
| Body | Inter + Noto Sans JP | 400, 15-16px |
| Numbers / scores | Cormorant Garamond | Tabular nums |

Max display size: 40px (same as iUMA base rule)

## Layout Principles

- **Information hierarchy**: Core Identity → 命式 → Monthly Forecast → Charts
- **Card pattern**: surface2 background, 1px border `--border`, 16-24px padding, 12px radius
- **Section width**: max 860px centered
- **Grid**: CSS Grid for 命式 3-card panel, single-column default

## UI/UX Architecture Differences (vs. mukonoso editorial)

| Dimension | self-insight (iUMA Mystic) | mukonoso editorial |
|---|---|---|
| Layout | Dashboard — scan vertical, cards | Article — read linear, prose |
| Information model | Data display (scores/charts) | Narrative prose |
| Interaction paradigm | At-a-glance overview | Reading / deep dive |
| Typography scale | Inter body + Cormorant display | Shippori Mincho body |
| Target cadence | Check monthly | Read per visit |

## Component Notes

- Chart.js: use direct hex `#8B5CF6` / `#22c55e` (not CSS vars — Chart.js cannot read vars)
- Monthly tag colors: indigo `rgba(99,102,241,0.15)` / phase-color / teal `rgba(20,184,166,0.15)`
- Female users: inject `--female-bg: #f5eff2` into `:root` (QA script: `scripts/qa_gender_css.py`)

## What this file is NOT

- Not a mukonoso/editorial migration plan
- Not a light-theme variant
- self-insight stays dark; this spec formalizes what's already built + the accent shift to mystic purple
