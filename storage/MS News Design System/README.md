# MS News — Design System

> 데일리뉴스 / **AI News Daily** — 매일 오전, RSS로 수집한 글로벌·국내 뉴스를
> AI(GPT·Claude·Gemini)가 정리해 웹·이메일로 전달하는 자동화 뉴스 브리핑 서비스.

---

## What this is

**MS News** (a.k.a. *AI News Daily*, *데일리뉴스*) is a **fully-serverless Korean
news briefing site**. RSS feeds in many languages are collected, deduped,
clustered, and summarized by an LLM into a clean daily Markdown report that gets
turned into a static HTML site (GitHub Pages) and an HTML email (Resend).

The product surface is small but opinionated:

| Surface | Role |
|---|---|
| **`index.html`** — latest report | Long-form reading view. Card-on-bg, 860px column. |
| **`app.html`** — dynamic web app | Two-column shell. Sidebar (search + stats + date list) + main column with language-filter tabs. |
| **`archive.html`** — all reports | List of every dated report (one row per day). |
| **`YYYY-MM-DD.html`** | Same template as `index.html`, locked to one date. |
| **HTML email** | Same Markdown rendered for inbox. |

The visual language is **trustworthy newsroom**: dark navy header, white reading
cards on a near-white background, blue links, generous line-height for Korean
text, pill-shaped meta badges, no decoration that distracts from the article.

---

## Theming — swap colors via one class

The system is **plain CSS with CSS custom properties** (not Tailwind). Every
color token is defined on `:root` and reusable component CSS only references
`var(--color-*)`. That makes the whole system **trivially re-skinnable**:
add a class to `<html>` and every component re-colors instantly.

Three palettes ship out of the box (defined in `colors_and_type.css`):

| Class | Vibe | Chrome / Accent / Bg |
|---|---|---|
| _(none — default)_ | **Navy** — modern tech-news | `#1e3a5f` · `#2563eb` · `#f8fafc` |
| `.theme-ink` | **Ink** — traditional Korean newspaper | `#1a1a1a` · `#b91c1c` · `#f7f5f0` |
| `.theme-forest` | **Forest** — fintech-modern, fresh editorial | `#064e3b` · `#047857` · `#f6faf8` |

```html
<!-- Default Navy -->
<html>
  <body>...</body>
</html>

<!-- Or switch with one class -->
<html class="theme-ink">    <!-- newspaper red on cream -->
<html class="theme-forest"> <!-- emerald on mint white -->
```

The `ui_kits/news_site/index.html` prototype has a **Tweaks panel** with a
swatch picker — toggle Tweaks in the toolbar and try all three live. To add
a fourth theme, copy one of the override blocks at the bottom of
`colors_and_type.css` and re-bind any of the `--color-*` tokens.

---

## Source

- **GitHub:** [chamgil71/dailynews](https://github.com/chamgil71/dailynews) — main branch
  - `publish/index.html`, `publish/app.html`, `publish/archive.html` — live HTML
    (the only "design system" the repo has — there is no Figma / no separate token file).
  - `scripts/build_site.py` — Python builder that renders MD → HTML using the same CSS.
  - `templates/daily_report.md` — Jinja2 daily report template.
  - `README.md`, `GUIDE.md` — context, copy tone, voice samples.

All design decisions in this document were reverse-engineered from those files.
The repo owner is **chamgil71**; the deployed site lives at
`https://chamgil71.github.io/dailynews/` and a richer Vercel build at
`https://ms-dailynews.vercel.app/`.

> 🔍 **Want more?** Browse the repo directly — `publish/2026-*.html` files are
> a great archive of how the layout renders against real daily content. Read
> `GUIDE.md` for editorial / prompt conventions if you're extending the system.

---

## Content fundamentals

### Voice & tone

The product speaks like a **professional news desk writing for busy Korean
knowledge workers**. Two distinct voices live side-by-side:

1. **UI / product chrome** — Korean, friendly-formal (`-요`/`-습니다` mix),
   sometimes a short imperative. Always plain, no jargon.
   - `최신 리포트` · `전체 목록` · `리포트를 불러오는 중...` · `구독 신청하기`
   - `검색`, `통계`, `리포트 날짜`
   - Email CTA: `매일 오전 AI가 정리한 글로벌 뉴스 브리핑을 이메일로 받아보세요.`

2. **Editorial body** — analytical, declarative, third-person. No "I", no
   "you". The author is the *AI 분석 전문가* persona; tone is sober, factual,
   slightly textbook-like.
   - Section titles use article-style nouns: `핵심 이슈 TOP 3`, `주목할 트렌드`
   - Each item leads with **a bolded thesis**, then an em-dash, then the
     reasoning. Example pattern:
     `**AI 에이전트의 실무 도입 가속화** — Anthropic의 'Cowork', Notion의
     AI 에이전트 플랫폼... 단순 챗봇을 넘어 업무를 직접 수행하는 '에이전트'
     중심의 서비스가 주류로 자리 잡고 있습니다.`

### Casing & punctuation

- **Korean default.** English brand names stay English (`OpenAI`, `Anthropic`,
  `xAI`, `GitHub Actions`) — no translation.
- **Mixed-script handling:** English run inside Korean is fine; no italics.
- **Em-dash (`—`) as connector** between a thesis and its explanation —
  characteristic move of this product's analyses.
- **Bracketed labels** as category tags inline: `[국내 IT·기술]`, `[글로벌 기술]`,
  `[AI·ML]`, `[국내 경제]`. Always in square brackets, always bold.
- **Numbers** are Arabic, Korean unit suffixes (`38건`, `94건`, `~$0.5~1/월`).
- **Dates** are `YYYY-MM-DD` in source / metadata, `YYYY년 MM월 DD일` for users.
- Punctuation: `·` (middle dot) is the standard separator in Korean labels
  (`AI·ML`, `국내 IT·기술`); avoid `/` for the same purpose.

### Emoji

**Used heavily as a navigation/label device, not as decoration.** A small,
consistent vocabulary; never random:

| Emoji | Meaning in this product |
|---|---|
| 📰 | The product itself (logo prefix, "Daily News Brief") |
| 📅 | Date / scheduling |
| 🤖 | AI / automation |
| 🌐 | English / global news |
| 🇰🇷 | Korean / domestic news |
| 📊 | Stats / metrics |
| 🔍 | Search / lookup |
| 📅 / 📄 | Report entry |
| 📚 | Archive / collection |
| 📬 | Email subscription |
| ⚠️ | Empty / error state |
| 📭 | "No reports yet" empty state |

Rule of thumb: **one emoji per label, leading position**, never as inline
decoration mid-sentence.

### Microcopy examples (verbatim)

- Section: `🌐 Global News Analysis`
- Section: `🇰🇷 국내 뉴스 분석`
- Section: `🔍 키워드 매칭 기사 (2건)`
- Section: `📋 수집 기사 전체 목록`
- Empty: `📭 아직 리포트가 없습니다.`
- Empty (search): `🔍 "{query}" 검색 결과 없음`
- Loading: `리포트를 불러오는 중...`
- Footer: `Powered by GitHub Actions · OpenAI GPT · RSS Feeds — 매일 자동 업데이트`

### Vibe

Quiet, dense, trustworthy. Reads like an internal company newsletter that
happens to be public. **No marketing voice, no superlatives, no exclamation
marks** in editorial copy.

---

## Visual foundations

### Colors

The palette is **two-color minimal**: a dark navy for chrome (header, headings)
and a saturated blue for action (links, primary buttons, h2). Everything else
is grayscale. Semantic accents (green / orange) only appear inside the
language-counter badges.

| Token | Hex | Used for |
|---|---|---|
| `--color-navy` | `#1e3a5f` | Header background, `h1` / `h3` text, strong product voice |
| `--color-blue` | `#2563eb` | Links, `h2`, action buttons, focus border |
| `--color-blue-light` | `#60a5fa` | Logo "News" accent only |
| `--color-blue-50` | `#eff6ff` | Badge bg, blockquote bg |
| `--color-bg` | `#f8fafc` | Page background |
| `--color-card` | `#ffffff` | Cards / surfaces |
| `--color-border` | `#e2e8f0` | Hairlines, input borders, dividers |
| `--color-text` | `#1e293b` | Body |
| `--color-muted` | `#64748b` | Captions, footer, blockquote, "x건" counts |
| `--color-green` | `#16a34a` | "KO 70건" badge |
| `--color-orange` | `#ea580c` | "AI 분석 40건" badge |
| `--color-yellow-mark` | `#fef08a` | Search-hit `<mark>` |

> **Color is not the brand.** It's almost monochrome with one accent. Resist
> adding more hues — the editorial density does the heavy lifting.

### Type

- **Family:** system stack first — `-apple-system, "Segoe UI", sans-serif`.
  This design system adds **Pretendard** as the optional web font for
  higher-fidelity Korean rendering. (See `Font substitution` below.)
- **Reading body:** 16px / line-height **1.7** — important. This much leading
  is intentional for dense Korean copy.
- **Scale:**
  | role | size | weight | color |
  |---|---|---|---|
  | h1 | 1.6rem | 700 | navy |
  | h2 | 1.2rem | 600 | blue (with 2px border-bottom) |
  | h3 | 1rem | 600 | navy |
  | body | 1rem | 400 | text |
  | small / nav | 0.9rem | 400 | varies |
  | badge | 0.78rem | 500 | semantic |
  | footer | 0.8rem | 400 | muted |
- **No display face.** No serifs anywhere. No italic for emphasis (Korean
  doesn't italicize well); bold + color is the only emphasis.

### Spacing

8px grid, but practical values are `8 / 12 / 16 / 20 / 24 / 32 / 36 / 48 / 80`.
- Card interior padding: **32px 36px** desktop, **20px** mobile.
- Vertical rhythm between cards: **24px**.
- Container reading width: **860px**.
- App layout (sidebar + main): **1100px**, sidebar **260px** fixed.

### Backgrounds & imagery

- **No background images.** No gradients. No textures. The chrome is solid
  navy, the canvas is solid `#f8fafc`. This is deliberate — a news product
  cannot let chrome compete with content.
- **No illustrations.** Visual interest comes only from typography density
  and the navy/blue/white contrast.
- **No hero images / no thumbnails.** Articles are pure text + link.

### Borders, radius, shadow

- **Cards:** `1px solid #e2e8f0`, `border-radius: 12px`, `box-shadow:
  0 1px 4px rgba(0,0,0,.06)`. Always white on `--bg`.
- **Header:** no border, `box-shadow: 0 2px 8px rgba(0,0,0,.25)` (heavier, dark).
- **Inputs / buttons:** `border-radius: 8px`, 1px gray border.
- **Pills (badges, tabs):** `border-radius: 20px` (full-pill), 1px colored border.
- **Inline code:** `border-radius: 4px`.
- **Blockquote:** asymmetric radius `0 8px 8px 0`, **4px solid blue left bar**.
- **No inner shadows** anywhere.

### Buttons & interactive states

- **Primary CTA (subscribe):** filled blue, white text, `padding: 10px 24px`,
  `border-radius: 8px`, weight 600. No icon. No shadow.
- **Filter tabs:** pill, 1px gray border, white bg. **Active = blue fill +
  white text.** Hover = blue border + blue text only.
- **Hover:** color shift only (link → darker, nav → full white, tab → blue
  border). **No opacity dimming, no transform.**
- **Transitions:** `.15s` for color, `.20s` for input border, `.30s` for
  fadeIn. All `ease`. **No bounce, no spring.**
- **Animations:** one fadeIn on report card mount (`translateY(8px) → 0,
  opacity 0 → 1`, 300ms). That's it.

### Layout rules

- **Sticky header** (`position: sticky; top: 0; z-index: 100`) — always
  visible while scrolling.
- **Sticky sidebar** in app view (`top: 80px`, `align-self: start`).
- Single reading column on `/index`, dual-column on `/app`.
- **Mobile breakpoint at 720px** — sidebar disappears, content goes
  full-width.
- **Mobile breakpoint at 600px** — card padding shrinks 32px → 20px, logo
  font shrinks slightly.

### Transparency & blur

- **Only one use:** `rgba(255,255,255,.8)` on nav links inside the navy
  header, fading to full white on hover.
- **No backdrop-filter, no glass effects.** This product reads as a document,
  not an OS surface.

### Imagery color treatment

N/A — there is no imagery. If imagery is ever introduced, it should be **cool
neutral** (matching the navy/blue palette) and avoid warm tones / grain /
hand-drawn looks.

### Density

High. The product is a wall of text by design. Generous *leading* (1.7) is
what keeps it readable; the gaps are vertical, not horizontal. Don't add
white space between list items "to breathe" — the rhythm depends on tight
list spacing.

---

## Iconography

**The product uses emoji as its entire icon system.** No SVG icons, no
icon font, no Lucide / Heroicons. This is a deliberate, low-maintenance
choice for a static-site product.

### Inventory

See **Content fundamentals → Emoji** above for the full vocabulary. Every
icon you see in the live product is a Unicode emoji rendered by the OS:

- Navigation: 📰 📚 🔍 📊 📅 📄 📬
- Language flags: 🌐 🇰🇷
- State: 🤖 ⚠️ 📭 📋
- Arrows in toggle buttons: ▲ ▼ (geometric shapes, not emoji)
- Spinner: CSS border + `@keyframes spin` (no icon)

### Rules

- **Leading position only** — emoji opens a label (`📅 2026.05.14`), never
  sits in the middle of a sentence.
- **One emoji per element.** Stacking (`📅📰`) is forbidden.
- **Color is OS-dependent and that's fine** — don't try to recolor emoji.
- **No custom SVG illustrations.** If a UI ever needs a "real" icon (e.g.
  for a button in a Korean text-input toolbar), pick from **Lucide** at the
  same stroke weight as the rest of the chrome (1.5px) and document the
  substitution.
- **No emoji in editorial copy** — they belong to chrome, not content.

> **Substitution flagged:** Because the repo has no custom icons, no assets
> were copied — `assets/` only contains a generated wordmark SVG for the
> design-system tab. If you want a custom logo / favicon / OG image, drop them
> into `assets/` and we'll wire them up.

---

## Font substitution

The source uses the **system font stack** (`-apple-system, "Segoe UI",
sans-serif`). System fonts render Korean acceptably on macOS / Windows but
inconsistently on Linux and some Android builds.

**This design system adds [Pretendard](https://github.com/orioncactus/pretendard)
as an optional web font** — a popular open-source Korean sans that is widely
used in Korean product design and matches the source's visual weight
extremely well. It's loaded via CSS `@font-face` in `colors_and_type.css`
fallback chain; if you don't have the files, system fonts kick in
automatically.

> ⚠️ **No font files are bundled in this project yet** — Pretendard is referenced
> by name only. If you want to ship it self-hosted, download from
> [the official repo](https://github.com/orioncactus/pretendard/releases) and
> drop the woff2 files into `fonts/`. Otherwise the system stack is already a
> good faithful match.

---

## Index — what's in this folder

```
README.md                  ← this file
SKILL.md                   ← skill manifest (for Claude Code / agents)
colors_and_type.css        ← all CSS vars + base element styles
assets/                    ← logos, brand marks
preview/                   ← Design System tab cards (small specimen HTMLs)
ui_kits/
  news_site/               ← MS News website recreation (the only product)
    README.md
    index.html             ← full interactive prototype
    *.jsx                  ← Header, ReportCard, Badge, Sidebar, etc.
```

### UI kits

- **`ui_kits/news_site/`** — recreation of the public `dailynews` website
  (index + app + archive surfaces). Single product; no mobile app exists.

### Cards (Design System tab)

The Design System tab is populated from `preview/*.html` files and
auto-grouped by **Type · Colors · Spacing · Components · Brand**. Open the
tab to scan the whole system at a glance.

---

## Caveats & next steps

- **No custom logo / favicon exists in the source.** The generated mark in
  `assets/logo.svg` is a placeholder that uses the brand wordmark only —
  swap it if you have real artwork.
- **No imagery system** — articles are link-only. If you ever need hero
  images, define a new sub-system (aspect ratio, alt-text rules, crop logic).
- **No mobile app surface** to recreate — the product is web + email only.
- **No design tokens file in source** — all CSS values were lifted from
  inline `<style>` blocks in `publish/*.html`.
