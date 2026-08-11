# Neutral Homepage Palette Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the site's cyan-tinted interface palette with the approved neutral gray and single-blue palette without changing layout, typography, HTML content, or links.

**Architecture:** Keep the existing semantic CSS token system in `assets/site.css`, but map every interface color to the approved neutral palette. Extend the existing site-contract script so it protects the exact semantic colors, rejects the previous cyan palette, and checks core text/link contrast ratios.

**Tech Stack:** Static HTML, shared CSS custom properties, Python standard-library contract test, in-app browser responsive verification.

---

### Task 1: Add a failing palette contract

**Files:**
- Modify: `scripts/check_site_contract.py`
- Test: `scripts/check_site_contract.py`

- [x] **Step 1: Define the approved and forbidden palettes**

Add exact semantic mappings for `--color-header`, `--color-header-ink`, `--color-header-muted`, `--color-paper`, `--color-canvas`, `--color-ink`, `--color-secondary-ink`, `--color-muted`, `--color-line`, `--color-accent`, `--color-accent-dark`, and `--color-header-line`. Add the former cyan values to a forbidden set.

- [x] **Step 2: Add contrast helpers and assertions**

Use the Python standard library to convert sRGB channels to relative luminance and calculate contrast ratios. Assert at least `4.5:1` for primary text, weak text, and link blue against both white and the neutral canvas where each role appears.

- [x] **Step 3: Run the contract and verify the red state**

Run:

```bash
python3 scripts/check_site_contract.py
```

Expected: `SITE CONTRACT: FAIL`, reporting missing approved palette values and retained cyan colors.

### Task 2: Apply the approved palette

**Files:**
- Modify: `assets/site.css`
- Test: `scripts/check_site_contract.py`

- [x] **Step 1: Replace root tokens**

Use these exact values:

```css
--color-header: #f5f5f7;
--color-header-ink: #1d1d1f;
--color-header-muted: #6e6e73;
--color-paper: #ffffff;
--color-canvas: #f5f5f7;
--color-ink: #1d1d1f;
--color-secondary-ink: #515154;
--color-muted: #6e6e73;
--color-line: #d2d2d7;
--color-accent: #0066cc;
--color-accent-dark: #004a99;
--color-header-line: #d2d2d7;
--shadow-paper: 0 8px 24px rgba(29, 29, 31, 0.05);
```

- [x] **Step 2: Remove hard-coded cyan and blue-gray colors**

Map the focus outline to `var(--color-accent)`, publication abstract text to `var(--color-secondary-ink)`, and TOC/code backgrounds to `var(--color-canvas)`.

- [x] **Step 3: Run the contract and formatting check**

Run:

```bash
python3 scripts/check_site_contract.py
git diff --check
```

Expected: `SITE CONTRACT: PASS (16 HTML pages checked)` and exit code `0`.

### Task 3: Verify visual consistency and preserve scope

**Files:**
- Verify: `index.html`
- Verify: `notes.html`
- Verify: `publications.html`
- Verify: `notes/tb/准周期1.html`
- Commit: `assets/site.css`, `scripts/check_site_contract.py`, `docs/superpowers/plans/2026-08-11-neutral-palette.md`

- [x] **Step 1: Verify desktop and mobile rendering**

Inspect the homepage and Publications page at the default desktop viewport, 390px, and 320px. Confirm no horizontal overflow, readable navigation, neutral header/canvas, white cards, and blue used only for interactive or structural emphasis.

- [x] **Step 2: Verify representative note pages**

Inspect Notes and `notes/tb/准周期1.html` to confirm inline legacy styles are overridden by the shared neutral palette and code/TOC backgrounds remain distinguishable.

- [x] **Step 3: Verify scope and commit locally**

Run:

```bash
python3 scripts/check_site_contract.py
git diff --check
git diff --name-only
```

Confirm no HTML content files changed. Stage only the plan, shared CSS, and contract test, then create a local `v1` commit. Do not push.
