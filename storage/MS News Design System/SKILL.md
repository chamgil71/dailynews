---
name: ms-news-design
description: Use this skill to generate well-branded interfaces and assets for MS News (AI News Daily / 데일리뉴스), the Korean RSS-driven AI news briefing site — either for production code or throwaway prototypes, mocks, and marketing artifacts. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping faithful to the dailynews brand.
user-invocable: true
---

# MS News Design Skill

Read **`README.md`** in this skill first — it contains the full content
fundamentals, visual foundations, and iconography rules. Then explore the
other files:

- `colors_and_type.css` — drop-in tokens + base element styles. Link this
  from any new HTML and you have the brand for free.
- `assets/` — wordmark SVG + favicon (the only brand artwork that exists).
- `preview/` — small HTML specimen cards. Open any one to see a single
  token / component in isolation; good for grabbing exact markup.
- `ui_kits/news_site/` — interactive recreation of the public website with
  Latest / App / Archive views, well-factored React components, and the
  three sample reports in `data.js`. Lift components from here when building
  new screens.

## Usage

- **Visual artifact** (slide, mock, throwaway prototype, marketing page) —
  copy `colors_and_type.css` and `assets/` into the output, then build
  static HTML. Borrow components from `ui_kits/news_site/components.jsx` if
  the artifact has news-style chrome (cards, badges, pill tabs, navy header).
- **Production code** — read the README, copy the CSS tokens, and respect:
  - Two-color palette (navy `#1e3a5f` + blue `#2563eb`) — don't add hues.
  - Body line-height **1.7** for Korean readability — never tighter.
  - Emoji as the entire icon system — leading position only.
  - No background images, no gradients, no shadows beyond the three tokens
    in `colors_and_type.css`.
  - Editorial voice in Korean (`-요`/`-습니다` mix), em-dash as connector,
    bracketed `[카테고리]` labels.

## When invoked without guidance

Ask the user what they want to build (a new section page? a card for a
specific feature? a marketing one-pager? a slide deck?), then ask 3–5
focused questions about audience, length, and tone before producing HTML
artifacts or production code.

## Source

Reverse-engineered from
[chamgil71/dailynews](https://github.com/chamgil71/dailynews) — the
deployed static news briefing site. The full README documents every
design decision back to a source file.
