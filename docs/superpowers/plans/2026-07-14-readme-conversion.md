# README Conversion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn both repository READMEs into clear, low-friction product landing pages while retaining the project's research-only safety boundaries.

**Architecture:** The change is documentation-only. `README.zh-TW.md` is the primary Taiwanese retail-investor page; `README.md` mirrors its information architecture for English-speaking evaluators and explicitly sets the Traditional-Chinese report-language expectation. Existing installation guides retain the detailed setup instructions.

**Tech Stack:** GitHub-Flavored Markdown, shell link/content checks.

## Global Constraints

- Do not claim returns, accuracy, or institutional affiliation.
- Do not imply the skill gives investment advice or executes trades.
- Do not fabricate a dashboard image, testimonial, or example report.
- Preserve correct links to the existing installation guides and license.
- Keep the English and Traditional-Chinese documents semantically aligned while writing idiomatically for each audience.

---

### Task 1: Rework the Traditional-Chinese landing page

**Files:**
- Modify: `README.zh-TW.md`
- Verify: `README.zh-TW.md`

**Interfaces:**
- Consumes: `INSTALL.md`, `LICENSE`, `install.sh`, and the existing skill capabilities.
- Produces: A self-contained Chinese landing page that links to the detailed installation guide.

- [ ] **Step 1: Replace the opening section with outcome-led copy and explicit trust commitments**

  Add a one-line result statement, the Claude Code/market positioning, and a three-item promise covering cited figures, named data gaps, and research-only/no order execution.

- [ ] **Step 2: Add the low-friction first-run section**

  Place a `先試這句（約 1 個環節）` section before the full workflow. Use the exact prompt `看 2330 技術面` and state that it runs only the relevant stage, so it costs materially less than a complete six-stage analysis.

- [ ] **Step 3: Reframe the mode table around user goals and explain the full deliverable**

  Rename the table columns to a user intent and prompt. Include deep dive, quick check, watchlist check, comparison, and Taiwan-only day trading. State that a complete analysis returns a source-cited report plus an HTML dashboard with position sizing, entry/exit levels, stop-loss, and risks.

- [ ] **Step 4: Add the full pipeline, cost note, and complete fastest install path**

  Retain the six stages. Show `git clone https://github.com/HenryLinyy/invest-committee.git`, `cd invest-committee`, and `./install.sh`. Keep Docker/Futu OpenD requirements and link to `INSTALL.md` for manual/Windows setup and token controls.

- [ ] **Step 5: Verify safety language and local links**

  Run:

  ```bash
  rg -n '不編造|未獲取|不下單|非投資建議|git clone|INSTALL\.md|LICENSE' README.zh-TW.md
  test -f INSTALL.md && test -f LICENSE && test -f install.sh
  ```

  Expected: Every required trust/safety concept is present and all three linked files exist.

- [ ] **Step 6: Commit the Chinese README update**

  ```bash
  git add README.zh-TW.md
  git commit -m "docs: improve Chinese README conversion"
  ```

### Task 2: Mirror the landing-page structure in English

**Files:**
- Modify: `README.md`
- Verify: `README.md`

**Interfaces:**
- Consumes: The content hierarchy established in `README.zh-TW.md`, `INSTALL.en.md`, `LICENSE`, and `install.sh`.
- Produces: An English landing page with equivalent scope and accurate language expectations.

- [ ] **Step 1: Write the English outcome-led opening and trust commitments**

  State that a named-stock prompt produces a source-cited investment-committee memo covering fundamentals, consensus, technical levels, risk flags, and position sizing. Promise sourced figures, explicit missing data, and no order execution.

- [ ] **Step 2: Add an English quick-start prompt and user-goal table**

  Use `Analyze NVDA technicals` as the low-commitment example. Explain that it invokes one relevant stage. Mirror the five modes from the Chinese page and preserve the Taiwan-only restriction for day trading.

- [ ] **Step 3: Make language, cost, installation, and guide expectations explicit**

  State that reports currently generate in Traditional Chinese. Include the same clone/install commands, link to `INSTALL.en.md`, describe optional Docker/Futu setup, and retain the 150–200K-token full-run disclosure without implying a fixed price.

- [ ] **Step 4: Verify safety language and local links**

  Run:

  ```bash
  rg -n 'source|missing data|never places orders|Traditional Chinese|git clone|INSTALL\.en\.md|LICENSE' README.md
  test -f INSTALL.en.md && test -f LICENSE && test -f install.sh
  ```

  Expected: The English page contains all required expectations and all three linked files exist.

- [ ] **Step 5: Commit the English README update**

  ```bash
  git add README.md
  git commit -m "docs: improve English README conversion"
  ```

### Task 3: Verify final documentation coherence

**Files:**
- Verify: `README.md`, `README.zh-TW.md`

**Interfaces:**
- Consumes: Both updated README files.
- Produces: Evidence that the pages remain semantically aligned and render as valid Markdown.

- [ ] **Step 1: Inspect the final diff for unsupported claims and scope creep**

  Run:

  ```bash
  git diff HEAD~2..HEAD -- README.md README.zh-TW.md
  git diff --check HEAD~2..HEAD
  ```

  Expected: Only README copy changes are present; `git diff --check` has no output.

- [ ] **Step 2: Compare required concepts across both pages**

  Run:

  ```bash
  for file in README.md README.zh-TW.md; do
    printf '%s: ' "$file"
    rg -c 'clone|六階段|six-stage|資料|data|風險|risk|不下單|orders|Traditional Chinese|繁體中文' "$file"
  done
  ```

  Expected: Both files have references to installation, pipeline, data discipline, risk, no-execution safety, and the report-language expectation.

- [ ] **Step 3: Report the two README commits and verification results**

  State the changed files, the user-facing improvements, and the exact checks run.
