# Homepage Photo and Notes Typography Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the supplied photo exclusively to the homepage profile card and improve all note-page typography without changing note content.

**Architecture:** Keep the homepage change isolated to `index.html` and a browser-safe derivative in `figs/`. Apply note improvements through the existing shared stylesheet so current and future note pages remain consistent without touching their prose. Extend the existing Python site contract before implementation to protect photo scope and typography coverage.

**Tech Stack:** Static HTML, CSS, Python standard-library contract test, Poppler image conversion.

---

### Task 1: Protect the photo scope and note typography contract

**Files:**
- Modify: `scripts/check_site_contract.py`

- [ ] Add parser support for image `src`, `alt`, and class attributes.
- [ ] Require exactly one homepage `.profile-photo` using `figs/fig1.jpg` with non-empty alternative text.
- [ ] Require the JPEG derivative to exist and begin with the JPEG signature.
- [ ] Reject any `notes/**/*.html` page that references `fig1`.
- [ ] Require shared selectors for the profile photo, TOC links, note subheadings, inline code, tables, and blockquotes.
- [ ] Run `python3 scripts/check_site_contract.py` and confirm it fails only for the not-yet-implemented photo and typography markers.

### Task 2: Add the browser-safe homepage photo

**Files:**
- Create: `figs/fig1.jpg`
- Modify: `index.html`
- Modify: `assets/site.css`

- [ ] Render the first page of `figs/fig1.pdf` as JPEG and limit the long edge to 1600 px.
- [ ] Add a single `<img class="profile-photo">` above the homepage name.
- [ ] Style the image as a restrained rectangular crop within the existing profile card.
- [ ] Add responsive sizing without changing the current identity text or homepage sections.

### Task 3: Refine notes through the shared stylesheet

**Files:**
- Modify: `assets/site.css`

- [ ] Constrain note reading width and strengthen the title/meta hierarchy.
- [ ] Replace the heavy TOC box with a light left-rule treatment and clear links.
- [ ] Add consistent spacing for `h2` and `h3` without altering heading text.
- [ ] Refine inline code, code blocks, blockquotes, tables, images, and MathJax overflow.
- [ ] Preserve the existing neutral palette and responsive breakpoints.

### Task 4: Verify content fidelity and rendering

**Files:**
- Test: `scripts/check_site_contract.py`

- [ ] Run `python3 scripts/check_site_contract.py` and confirm all site-contract checks pass.
- [ ] Run `git diff --check` and confirm there are no whitespace errors.
- [ ] Confirm `git diff -- notes` is empty so note source content was not edited.
- [ ] Serve the site locally and visually inspect the homepage and representative DFT, tight-binding, and other note pages at desktop and mobile widths.
- [ ] Confirm no changes are pushed to GitHub.
