# Post-Implementation Checklist

> **Scope:** Software development projects only. Adapted here for a Python CLI project (not the TypeScript default).

Run this checklist after implementation is complete and code is committed.

## 1. Metadata

- [ ] Frontmatter `created` / `created_by` fields are set (or add an `edits` entry if you're not the original author)
- [ ] Add `issue` and/or `pr` number to frontmatter if applicable

## 2. Plan vs Implementation Review

- [ ] Walk each plan checkbox — confirm the code matches intent
- [ ] Mark completed steps `[x]`, note any skipped steps with reason (capture follow-ups in step 5)

## 3. Quality Gates

Run from the repo root. Fix any failures before proceeding.

```sh
pip install -e ".[dev]"   # editable install with dev deps
pytest -v                 # unit + smoke tests
```

> **Automation context:** CI (`.github/workflows/ci.yml`) runs the same suite plus an end-to-end CLI smoke build on every push/PR to `main`. Running these checks locally before pushing is recommended to avoid CI failures.

## 4. Final Diff Review

- [ ] Review the full git diff against the plan: `git diff main...HEAD`
- [ ] No unintended changes, no leftover debug code, no stray `print()` used for debugging
- [ ] No hardcoded host-repo-specific paths introduced

## 5. Deferred Work

- [ ] File skipped plan items or new ideas to `todo/[category]/` or `todo/deferred/` (follow [Proactive Filing](../AGENTS.md#proactive-filing))

## 6. Artifact Lifecycle

- [ ] Fill `## Outcome` section in the artifact
- [ ] Move artifact from `doing/[category]/` → `done/[category]/`

## 7. Knowledge Extraction

- [ ] If the work reveals a reusable architectural pattern → update `docs/` or `AGENTS.md`
- [ ] Record lessons learned in repo/user memory if applicable

## 8. Git Operations — Explicit Approval Required

- [ ] When the user asks for a **New PR Creation Data** provide each of the following fields under a bold label with a separate MarkDown code block — paste-ready for GitHub forms fields:
  - issue title,
  - issue description
  - branch name
  - commit message
  - PR title
  - PR description
- [ ] **Stop. Wait for explicit approval before running any git write operation** (commit, push, branch create/delete, force-push, amend).

**Note:** Be very concise.

**Git Conventions:**

- **Branch:** `type/issue-number-description` — e.g. `feat/42-template-overrides`, `fix/87-typst-path-resolution`
- **Commit & PR title:** `type(scope): description` — e.g. `feat(manifest): support per-document template overrides`
- **Issue title/description:** Plain English

Types: `feat`, `fix`, `chore`, `refactor`, `test`, `docs`
