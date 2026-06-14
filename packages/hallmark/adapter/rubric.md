# Hallmark Rubric — 65-gate slop test

This file maps Hallmark's slop test gates to
harnessable Rubric criteria. Add to the DIP
Verification Checklists for any design mandate
that uses /hallmark.

QA evaluates these criteria after Designer output.
One FAIL = MUST_FIX. One PASS required before
the mandate can advance to DONE.

## How to run

Hallmark runs the slop test automatically before
emitting output. QA re-runs it independently:

  Open the generated HTML/CSS in a browser.
  Work through the gate checklist below.
  Any YES is a failure.

---

## Gate clusters

### Pre-emit self-critique (stamp + 6 axes)
- [ ] Pre-emit stamp (/* Hallmark · pre-emit critique: … */) missing from the CSS? (NO = PASS)
- [ ] Philosophy (P) axis scored below 3 in the pre-emit stamp? (NO = PASS)
- [ ] Hierarchy (H) axis scored below 3 in the pre-emit stamp? (NO = PASS)
- [ ] Execution (E) axis scored below 3 in the pre-emit stamp? (NO = PASS)
- [ ] Specificity (S) axis scored below 3 in the pre-emit stamp? (NO = PASS)
- [ ] Restraint (R) axis scored below 3 in the pre-emit stamp? (NO = PASS)
- [ ] Variety (V) axis scored below 3 in the pre-emit stamp? (NO = PASS)

### Visual (gates 1–7)
- [ ] Display font is Inter, Roboto, Open Sans, Poppins, Lato, or a system default? (NO = PASS)
- [ ] Purple-to-blue or cyan-to-magenta gradient present — including a background-clip: text gradient headline? (NO = PASS)
- [ ] 3-equal-column card grid with icon-above-heading tiles? (NO = PASS)
- [ ] Card nested inside another card? (NO = PASS)
- [ ] Card using a thick coloured left/right side-stripe border? (NO = PASS)
- [ ] Hero is min-height: 100vh with eyebrow, title, lede, and CTA all stacked on the same centred vertical axis? (NO = PASS)
- [ ] Pure #000 or pure #fff used as a base colour? (NO = PASS)

### Structural (gates 8–9)
- [ ] Page reuses the AI default template (Hero → 3 features → CTA → footer) or the same macrostructure as a prior Hallmark output in this project? (NO = PASS)
- [ ] Sections separated only by equal whitespace with no rule, ornament, or colour shift? (NO = PASS)

### Microinteractions (gates 10–19)
- [ ] transition-all or transition: all used anywhere? (NO = PASS)
- [ ] hover:scale-105 (uniform hover-scale) applied across multiple unrelated elements? (NO = PASS)
- [ ] Bouncy / overshoot easings used on UI state changes (buttons, modals, tooltips)? (NO = PASS)
- [ ] Any element has more than one hover effect simultaneously (translate + scale + shadow + colour + rotate)? (NO = PASS)
- [ ] width, height, top, left, margin, or padding animated? (NO = PASS)
- [ ] Focus ring fades in (transitions into existence) instead of appearing instantly? (NO = PASS)
- [ ] Celebratory success toast for an action whose effect the user can already see? (NO = PASS)
- [ ] Tooltip hover-delay and focus-delay are equal (hover should be 800–1000 ms; focus should be 0 ms)? (NO = PASS)
- [ ] Auto-rotating content (carousel, banner, stats counter) lacks pause-on-hover-and-focus? (NO = PASS)
- [ ] Placeholder name "Jane Doe / John Smith" or startup cliché (Acme, Nexus, Seamless, Unleash) present? (NO = PASS)

### Variety (gates 20–21)
- [ ] Hallmark macrostructure stamp (/* Hallmark · macrostructure: … */) missing from the top of the CSS? (NO = PASS)
- [ ] Specimen macrostructure defaulted to when the brief did not explicitly call for editorial / foundry energy? (NO = PASS)

### Implementation (gates 22–27)
- [ ] Any neutral / surface colour has zero chroma — oklch(… 0 …)? (NO = PASS)
- [ ] Accent colour covers more than ~5% of any single viewport by area? (NO = PASS)
- [ ] Any padding / gap / margin value is not on the named spacing scale (not a multiple of 4 px)? (NO = PASS)
- [ ] Any prose container's max-width is outside the 45–75 ch range? (NO = PASS)
- [ ] Any interactive element lacks :focus-visible, :active, or :disabled styling? (NO = PASS)
- [ ] Any transform / animation keyframe lacks a prefers-reduced-motion fallback? (NO = PASS)

### Hero enrichment (gates 28–31)
- [ ] Demo video autoplays with sound, lacks a poster attribute, lacks fetchpriority="high", or uses loading="lazy" on the LCP element? (NO = PASS)
- [ ] Abstract background uses more than one accent colour, covers more than ~5% footprint, or is an animating mesh-gradient on the whole page? (NO = PASS)
- [ ] Page mixes two or more icon libraries, or uses an emoji glyph (✨ 🚀 ⚡ 🔥 🎯 ✅) as a feature-card / value-prop / step / pricing-tier icon? (NO = PASS)
- [ ] Illustration defaults to a Lottie library when a hand-built SVG or pure-CSS shape would have worked? (NO = PASS)

### Diversification (gates 32–33)
- [ ] Same archetype reused from a prior Hallmark output without any different variation knob? (NO = PASS)
- [ ] Visual-only SVG, custom-art div, canvas, or decorative figure lacks aria-label or aria-hidden="true"? (NO = PASS)

### Layout-safety (gates 34–36)
- [ ] Page horizontally scrolls on any viewport between 320 px and 1920 px (overflow-x: clip missing on both html and body)? (NO = PASS)
- [ ] Decorative text effect (highlighter band / accent stroke / underline) not visually confirmed for correct vertical position and size? (NO = PASS)
- [ ] Interactive bars (nav, toolbar, hero CTA row, footer strip) lack explicit align-items: center — elements not vertically centred? (NO = PASS)

### Typography discipline (gates 37–38a)
- [ ] More than three distinct font-family families on the page? (NO = PASS)
- [ ] Outlier face used in more than two slots on the page? (NO = PASS)
- [ ] Any heading or display type is italic (font-style: italic on h1–h6, a title class, wordmark, stat figure, or em inside a heading)? (NO = PASS)

### Input-state (gate 39)
- [ ] Input / textarea / select fields fail any of: border-width shifts between states; focus ring built from border not outline; input height ≠ adjacent button height on same form; helper-text slot has no reserved min-height; disabled signalled by opacity alone? (NO = PASS)

### Contrast & readability (gates 40–41)
- [ ] Any text, icon, or :focus-visible ring fails its APCA / WCAG contrast threshold against its computed background? (NO = PASS)
- [ ] Button text ≈ button fill colour, OR --color-accent-ink missing / unused on accent-filled surfaces, OR dark section (L < 50%) uses ink-coloured text without a colour swap? (NO = PASS)

### Nav · footer · hero structural slop (gates 42–45)
- [ ] Nav is the AI default fingerprint: wordmark-left + 4–5 inline links + button-right at full viewport width + 1 px border-bottom + white background? (NO = PASS)
- [ ] Footer is the AI default fingerprint: 4 link columns (Product / Company / Resources / Legal) + social-icon row + tiny copyright + 1 px border-top + neutral grey background? (NO = PASS)
- [ ] Hero fit fails: padding-block-end < 1.3× padding-block-start (symmetric or top-heavy), OR essential content (eyebrow, headline, lede, primary CTA, visual focal point) requires scrolling at 1280×800 to see? (NO = PASS)
- [ ] Hero contains a decorative element (cursor, scanline, gradient blob, ornament, badge, sticker) with no semantic anchor in the content? (NO = PASS)

### Honest copy (gate 46)
- [ ] Page contains a quantitative claim ("10× faster", "trusted by 50,000+ teams", "99.9% uptime", "+47% conversion") not supplied by the user and with no source? (NO = PASS)

### Re-drawn UI chrome (gate 47)
- [ ] Hand-built fake browser bar, fake phone frame, fake code-block window, fake terminal frame, or fake IDE chrome present in HTML/CSS/SVG? (NO = PASS)

### Token discipline (gate 48)
- [ ] Any colour value (#hex, oklch(…), rgb(…), hsl(…)) or font-family declaration appears outside the design tokens defined in :root / [data-theme]? (NO = PASS)

### Responsive — clickable affordances (gate 49)
- [ ] Any button label, primary nav link, footer link, tab label, breadcrumb, or CTA text wraps to two or more lines at any viewport between 320 px and 1920 px? (NO = PASS)

### Mobile — non-negotiables (gates 50–57)
- [ ] Image-bearing grid track uses bare 1fr instead of minmax(0, 1fr)? (NO = PASS)
- [ ] Display-size heading (h1, .hero__display, .section__title, or equivalent) lacks overflow-wrap: anywhere; min-width: 0? (NO = PASS)
- [ ] Per-theme section-head override lacks a mobile-collapse rule (grid-template-columns: 1fr) at max-width: 48rem with matching specificity? (NO = PASS)
- [ ] CSS-only radio tab pattern has radios at position: absolute; top: 0 without a JS handler that prevents scroll-jump on label click? (NO = PASS)
- [ ] Section eyebrow / number / mono-cap label renders beside the heading in multi-column layout instead of stacking vertically in the same column? (NO = PASS)
- [ ] All-caps display element declares line-height below 1.0 (cap-collision risk on wrap)? (NO = PASS)
- [ ] In-page sticky element uses top: 0 when a page-level sticky nav also uses top: 0 (overlap / bleed into nav)? (NO = PASS)
- [ ] Study diagnosis was emitted earlier in this conversation but the CSS stamp names a catalog theme instead of studied-DNA (source: …)? (NO = PASS)

---

## Overall verdict

PASS:   all 65 gates NO (no slop detected)
FAIL:   any gate YES → MUST_FIX before DONE

## QA note

Hallmark runs this test before emitting. QA's
independent run is not redundant — it catches
cases where the model self-reported PASS incorrectly.
Trust the independent check, not the self-report.
