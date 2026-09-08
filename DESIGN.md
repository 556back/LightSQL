---
version: alpha
name: LightSQL
description: A data observatory for asking business questions and tracing reliable answers.
colors:
  primary: "#167568"
  background: "#f3f6fa"
  foreground: "#22344b"
  card: "#ffffff"
  muted-foreground: "#607186"
  border: "#dde5ed"
  sidebar: "#162a43"
  sidebar-primary: "#9fe0ce"
  destructive: "#c13f49"
typography:
  sans:
    fontFamily: '"Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif'
  display:
    fontFamily: '"Bahnschrift", "Segoe UI", "Microsoft YaHei", sans-serif'
  mono:
    fontFamily: '"Cascadia Code", "Consolas", monospace'
rounded:
  DEFAULT: "0.75rem"
  sm: "0.375rem"
  feature: "1.125rem"
spacing:
  section-gap: "1.5rem"
  page-max: "90rem"
components:
  button:
    height: "2.5rem"
  card:
    rounded: "1rem"
  dialog:
    rounded: "0.75rem"
---

# LightSQL Design System

## Overview

The creative reference is a data observatory: a dark blue instrument frame around a pale, readable work surface. Business analysts explore authorized data; administrators prepare connections, table catalogs, and semantic topics. This is a product interface, with a more expressive login surface.

The signature is a bundle of intersecting data paths, implemented in `DataSpectrum.tsx`. It is decorative, hidden from assistive technology, and never presented as a real chart. Use it only at entry points; working forms and result tables stay quiet.

The September 2026 redesign is authorized by the request to refactor the frontend with beauty, usability, and artistic character. Product evidence: `README.md`, `docs/前端体验优化.md`, and the domain API. The audience uses simplified Chinese in an internal enterprise tool; geographic market and Japanese support are not established. No remote fonts or image services are required.

**Runtime ownership:** `frontend/src/index.css` is canonical. This document mirrors its named light-theme values. CSS variables flow through the existing `@theme inline` adapter into Tailwind and shared `ui/` components. `.dark` changes semantic values in the same file; sidebar text uses its own scoped tokens. No generated token copies exist. Verify documented colors and typography against CSS, then run browser checks in both themes.

## Colors

Mist blue gives large work areas a cool, low-glare surface. White identifies editable or inspectable content. Deep blue anchors navigation; mint marks the active destination. Teal is reserved for forward actions and selected scope. Red means destructive or failed, while existing labeled green/amber badges convey ready/review states. Color never replaces labels.

Dark mode uses blue-black surfaces with brighter mint actions and dark button text for contrast. Scrollbars have global thumb, track, hover, and active tokens in both themes. Forced colors restores system colors and hides the decorative spectrum.

## Typography

Segoe UI and local Chinese sans-serif fallbacks own body text. Bahnschrift is restrained to the wordmark, page headings, and numerical summaries; Chinese falls back to readable local sans-serif. Cascadia Code/Consolas own SQL and technical values. No font download or late font swap. Body copy uses 14px with generous 24–28px leading; dense labels use 12px. Page titles scale from 26–32px. Chinese text is never artificially italicized.

## Layout

The existing 256px sidebar collapses to icons and becomes a modal navigation sheet below 768px. Content stays in document flow with 16/24/32px responsive padding and a 1440px maximum. Large cards use 24px rhythm; working controls use tighter existing spacing. Topic cards use one, two, then three columns. The topic guide is compact enough to keep filters and cards close to the first viewport.

Tables own horizontal overflow; the shell never clips long forms. Dialogs own their bounded vertical overflow. Search, retry, and empty states retain their containers. No decorative animation loops.

## Elevation & Depth

Use borders and tonal separation first. Cards receive a nearly invisible ambient shadow, with a modest border/shadow response on hover or focus within. The header uses a translucent white/dark surface with a border. Modal elevation remains stronger than content cards. No stacked glass panels or bright gradients.

## Shapes

Controls use the existing 6–8px radius family, cards use 12–16px, and the spectrum panel uses 18px. Status badges remain compact pills. Only the brand mark gets a distinct softly squared silhouette.

## Components

`PageHeader` owns the eyebrow, title, explanation, and primary action. `DataJourney` retains the real four-step preparation sequence. Shared Radix buttons, tabs, dialogs, sheets, and menus preserve keyboard behavior. Native selects remain native where the OS popup is accepted; the existing Radix Select owns authored selection flows.

Buttons have solid, outline, ghost, and destructive variants, with hover, visible focus, pressed, disabled, and busy states. New forms own inline validation and preserve values on failure. `SearchInput` owns the icon, clear action, localized accessible name, and focus return. Textareas cannot be dragged; use adequate height and internal scrolling for long text.

Lucide is the icon family, normally 16–20px with labels. The global stylesheet handles reduced motion and focus. UI wording states the next action plainly; missing data shows a dash, never a fabricated statistic. SQL and business identifiers preserve original content.

## Do's and Don'ts

- Do keep the data spectrum confined to entry surfaces and repeat the underlying palette across management pages.
- Do preserve source/topic context, drafts, access checks, and backend error explanations.
- Don't use decorative charts as real business evidence or invent operational status.
- Don't trade readable tables and accessible controls for artistic effects.
