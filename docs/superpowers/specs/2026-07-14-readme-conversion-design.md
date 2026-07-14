# README conversion design

## Goal

Make the repository understandable and trialable within a minute for a first-time GitHub visitor, without changing the investment-research workflow, data discipline, or safety boundaries.

## Audience

- Traditional-Chinese-speaking retail investors who use, or are considering, Claude Code.
- English-speaking Claude Code users evaluating whether the skill fits their workflow.

## Scope

Update `README.md` and `README.zh-TW.md` only.

Each README will:

1. Lead with the input-to-output value proposition.
2. Surface three trust commitments: cited figures, explicit missing data, and no order execution.
3. Offer a low-cost, single-stage first prompt before the full six-stage workflow.
4. Present the modes as user jobs rather than an undifferentiated feature list.
5. Include a complete clone-and-install command path and distinguish the fast path from optional data setup.
6. Explain the report/dashboard deliverable without inventing a performance claim or a sample result.
7. Keep language-output expectations explicit in the English README.

## Content structure

1. Product name, language switcher, and one-sentence outcome.
2. Short positioning paragraph and trust commitments.
3. "Start here" / "先試這句" low-friction prompt.
4. User-goal table and full-report deliverables.
5. Six-stage pipeline and data/cost expectations.
6. Installation with `git clone`, then advanced requirements/install-guide link.
7. Disclaimer and license.

## Constraints

- Do not claim returns, accuracy, or institutional affiliation.
- Do not imply the skill gives investment advice or executes trades.
- Do not fabricate a dashboard image, testimonial, or example report.
- Preserve correct links to the existing installation guides and license.
- Keep the English and Traditional-Chinese documents semantically aligned while writing idiomatically for each audience.

## Verification

- Review the rendered Markdown structure and all local links.
- Verify that clone commands, file names, and stated requirements match the repository.
- Inspect the final diff for unsupported claims and accidental changes outside the two README files plus this design document.
