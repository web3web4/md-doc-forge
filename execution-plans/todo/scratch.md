## Follow-ups from the initial extraction (2026-07-24)

Left after the initial extraction from `saudi-realesate-tokenization-license` and
its cutover to consume this CLI (see that repo's
`execution-plans/done/revisions/2026-07-19-1533-extract-doc-generation-sdk.md`
and this repo's `execution-plans/done/features/2026-07-24-2030-extract-and-package-md-doc-forge.md`).

- [x] Install `pipx` on any machine that will run `md-doc-forge build` locally without
      an ad-hoc venv (not present on the dev machine used for the initial extraction;
      CI already installs it via `pip3 install`, not `pipx` — see `.github/workflows/ci.yml`).
      LibreOffice, by contrast, IS present on the dev machine (just not on `PATH`) and
      the Writer-PDF pipeline has been verified working locally.
      **Done (2026-07-24):** `brew install pipx && pipx ensurepath`, then
      `pipx install "git+https://github.com/web3web4/md-doc-forge.git"`. Verified
      `md-doc-forge` resolves globally (`/Users/funcy/.local/bin/md-doc-forge`, no venv
      activation needed) and a real `--format docx` build against the license repo's
      manifest succeeds.
- [ ] Decide whether to publish to PyPI, or stay a git-URL install
      (`pipx install "git+https://github.com/web3web4/md-doc-forge.git"`) indefinitely.
- [ ] Integrate this CLI into the `personal` repo (letters/cover-letters) — this is
      the consumer that motivated the `templates.docxReference` / `templates.typstHeader`
      manifest override mechanism; it hasn't been exercised by a real second consumer yet.
- [ ] Build the portable agent-skill wrapper around this CLI (per the original
      extraction prompt's second consumer).
- [ ] Once a second consumer is live, revisit the superseded extraction plan's
      "Phase 3" ideas: per-document `formats` restriction, pandoc variable overrides,
      JSON Schema for `build-manifest.json` — only if actually needed, not speculatively.
