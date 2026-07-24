# md-doc-forge - Context for AI Agents

## Project Overview

**md-doc-forge** is a manifest-driven Markdown → PDF/DOCX/ODT document generation engine, packaged as an installable Python CLI (`md-doc-forge`).

- **src/md_doc_forge** — the package: `manifest.py` (manifest parsing), `builder.py` (pandoc/typst/soffice orchestration), `postprocess.py` (DOCX table/TOC fixups + PDF outline view), `cli.py` (entry point), `assets/` (bundled default templates and pandoc Lua filters)
- **tests** — manifest parsing tests + an end-to-end build smoke test

Extracted from the `saudi-realesate-tokenization-license` repo, which remains the reference consumer. A second consumer (a `personal` repo for letters/cover-letters) and a portable agent skill wrapping this CLI are the reasons template overrides (`templates.docxReference` / `templates.typstHeader`) exist in the manifest schema — every consumer can supply its own DOCX/Typst styling without forking the engine.

## Project Status

Early stage — freshly extracted. Breaking changes are expected until a second real consumer has integrated successfully.

## Project Type

`Development — Python`

## Architecture & Stack

See [`agents-instructions/architecture-reference.md`](agents-instructions/architecture-reference.md) for tech stack, engineering patterns, and architectural decisions. Only read that file when the task involves stack choices, new dependencies, or architecture.

## Development Rules

- **Code Quality**: Type-hint public functions. Prefer stdlib + the three declared runtime deps (`python-docx`, `PyMuPDF`, `lxml`) over adding new ones.
- **Documentation Location**:
  - Persistent architecture/usage docs → `docs/` (create if/when needed) or `README.md`
  - Ephemeral agent planning/logs → `execution-plans/` (do not gitignore)
  - All other `.md` files should only be created inside `execution-plans/` or `docs/` unless the task explicitly requires otherwise.
- **Testing**: Pytest. Manifest logic must have unit tests with no external binary dependency. Build logic tests may `skipif` when `pandoc`/`typst` are missing, but must never silently pass without exercising real output when the tools are present.
- **No backward compatibility**: Early stage, no external consumers beyond the one reference repo. Never add shims, compat layers, or transitional adapters. Break interfaces freely — always implement the cleanest design.
- **Knowledge capture**: When you discover a reusable pattern or architectural insight during a task, append it to `execution-plans/todo/scratch.md` — don't break focus to write to `docs/` mid-task.
- **Template parity**: Any change to `assets/reference.docx`, `assets/typst-header.typ`, or the Lua filters must be verified against the `saudi-realesate-tokenization-license` repo's existing manifests to avoid silently changing that repo's regulatory-submission output.
- **No git write ops without explicit per-operation approval**: `git commit`, `git push`, branch deletion, force-push, and amend each require their own explicit approval — even mid-workflow. Read-only git commands are fine.
- **Specs vs. code**: If code deviates from a spec but the code is better, propose updating the spec — don't "fix" working code.
- **Test failures**: Investigate production code first before assuming the test is wrong.

## AI Agent Workflow (The "execution-plans" system)

> **First thing every session:** Check `execution-plans/doing/` for unfinished work from a previous session before starting anything new.

When planning complex tasks, investigating bugs, or leaving context for future sessions, use the `execution-plans/` directory. **Skip this for trivial, single-step changes** — not every task needs an artifact.

### Directory Structure & Lifecycle

`execution-plans/[status]/[category]/`

- **[status]**: `todo/`, `doing/`, `done/`
- **[category]**: `features/`, `fixes/`, `analysis/` — the standard categories. Add others only when these three don't fit.

**`todo/` scope rules:**

- `todo/[category]/` — Items to work on during the **current project phase**.
- `todo/deferred/` — Items intentionally deferred to a **future phase**. Not picked up until the project advances to that phase. Files here are not categorized into subfolders.

**Workflow Rules:**

> The status folders track **active implementation**, not the Markdown document. `doing/` = actively writing code. `done/` = code implemented, verified, and committed.

1. **New Request / Planning**: Create (or keep) the markdown file in `todo/[category]/`. Write plans, checklists, and context here. A fully-planned item stays in `todo/` until implementation begins.
2. **Starting Implementation**: Move the file to `doing/[category]/` when you begin writing code.
3. **Completion**: Once code is fully implemented, verified, and committed, move the file to `done/[category]/`.

### Proactive Filing

If you notice anything worth noting during unrelated work (bugs, ideas, patterns, insights), append your thoughts to `execution-plans/todo/scratch.md` and move on. Don't create artifacts or backlog entries mid-task — stay focused.

> `todo/` is a passive backlog. **Never** autonomously pick up items from it — only work on them when the user explicitly asks.

### Stale Work

If you find items in `doing/` that appear outdated or abandoned, move them back to `todo/` (preserving all notes) or forward to `done/` with an `## Outcome: Canceled — [reason]` note. Ask the user if unsure.

### Naming Convention

Use this format: `YYYY-MM-DD-HHmm-[title].md`, e.g. `2026-03-01-1430-fix-auth-redirect.md`. Always write dates with time in 24-hour format (e.g. `2026-03-24 14:30`).

One file per task. Plans, progress, and outcomes all live inside the same file using the structure below.

### Artifact File Structure

Every artifact file must follow this layout:

```markdown
---
created: YYYY-MM-DD HH:mm
created_by: [LLM name and version]
edits:
  - date: YYYY-MM-DD HH:mm
    author: [LLM name and version]
---

## Context

[Concisely: why this task exists]

## Plan

- [ ] Step 1
- [ ] Step 2

...

## Rationale

_If needed — for reviewers_

[Why this approach over alternatives, key findings from investigation, design decisions, constraints, assumptions to verify]

---

## Outcome

[What was done and why — keep it concise]

### Notes

_If needed_

[Trade-offs, deferred work, follow-ups]
```

- Fill `Context` and `Plan` while the file is in `todo/`.
- Fill `Rationale` while planning when the approach isn't self-evident, or when it rests on significant or deep investigation whose findings a reviewer would otherwise overlook — record what led to the decision so reviewers don't miss it. Skip it for trivial work.
- Fill `Outcome` when moving to `done/`. Check off plan items as you go.
- For implementation work, include the checklist from [`agents-instructions/implementation-checklist.md`](agents-instructions/implementation-checklist.md) in your plan.
- For writing or reviewing prompts for major work, follow [`agents-instructions/prompt-authoring-guide.md`](agents-instructions/prompt-authoring-guide.md).
- After completing work, follow the checklist in [`agents-instructions/post-implementation-checklist.md`](agents-instructions/post-implementation-checklist.md).

## Communication & Reasoning Standards

- **Fact-based, not agreeable**: If a request relies on a flawed assumption or conflicts with project conventions/architecture, challenge it directly. Do not execute a bad plan just to be helpful.
- **Critical plan evaluation**: Plans, architecture docs, and prior agent artifacts are inputs, not gospel. Verify claims against actual code and data before executing. When you spot gaps, conflicts, or suboptimal choices — flag them before executing and propose an alternative. Do not over-flag cosmetic or subjective concerns — focus on issues that would cause bugs, data inconsistencies, or architectural drift.
- **No silent omissions**: If an edge case, requirement, or code block is being skipped, explicitly state what was omitted and why.
- **Zero filler**: Skip formalities like pleasantries and apologies. Focus on actionable steps and code.
- **Copyable text as code blocks**: When asked to provide a piece of text for direct use (a template, message, example, form field value, very concise prompt, etc.) rather than to answer a question, wrap it in a fenced Markdown code block.

## Dev Scripts

No `scripts/` directory — the engine itself is the CLI (`md-doc-forge`). See `README.md` for install and usage.
