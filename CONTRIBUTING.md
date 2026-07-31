# Contributing to file-itr

Thanks for considering a contribution. The project has two parts that evolve
somewhat independently:

- the **skill** (`skills/itr-india/SKILL.md` + `skills/itr-india/references/`)
  — what actually runs when an agent files a return, and
- the **engine** (`skills/itr-india/engine/`) — a separate, tested Python
  module that independently recomputes the tax to audit the skill's numbers.
  It is not wired into `SKILL.md` and is not part of the `.skill` bundle.

## Ground rules

- **Every statutory number or rule needs a verified citation** to the actual
  section/circular/notification — no rule is added on "this sounds right."
  See [`engine/README.md`](skills/itr-india/engine/README.md) for how the
  engine enforces this (typed `Rule`s, `validate_rule`, contested-rule flags,
  and a fail-loud `OutOfScopeError` instead of a silent guess). Apply the same
  discipline to `references/*.md` in the skill.
- **Never commit real tax data**, in a commit, a test fixture, an issue, or a
  PR description. This includes PAN/Aadhaar/passport numbers, bank/broker/demat
  account numbers, passwords/OTPs/tokens, addresses or contact details, and
  Form 16/26AS/AIS-TIS/ITR JSON/acknowledgements — real or unredacted. If a bug
  only reproduces with sensitive material, describe the behavior instead of
  attaching the source document; use synthetic or fully redacted data. `.gitignore`
  blocks common filenames for this (`*AIS*`, `*26AS*`, `*Form16*`, `*ACK*`,
  `*ChallanReceipt*`, `*Preview*`, `*.json.personal`), but that's a safety net,
  not a guarantee — check `git status` before pushing. See
  [SECURITY.md](SECURITY.md) for what to do if sensitive data does get committed,
  and how to report a security issue privately.

## Dev setup

The engine has no dependency beyond `pytest`:

```bash
pip install pytest
pytest skills/itr-india/engine/tests -v
```

`skills/itr-india/conftest.py` puts `engine/` on `sys.path`, so the tests
collect correctly whether you run pytest from the repo root or from inside
`skills/itr-india/`.

## Making changes

- **Skill changes** (`SKILL.md`, `references/*.md`, `evals/evals.json`): edit
  them directly. Don't hand-edit or hand-commit `itr-india.skill` — CI
  (`.github/workflows/skill-bundle.yml`) rebuilds it deterministically and
  commits it back to `main` whenever those paths change. To check the bundle
  locally first: `./scripts/build-skill-bundle.sh`.
- **Engine changes** (`skills/itr-india/engine/`): add or extend tests
  alongside the change (`engine/tests/`) and make sure
  `pytest skills/itr-india/engine/tests -v` passes. New or changed rules go
  through the same `Rule` / citation / `validate_rule` machinery as existing
  ones — see `engine/rulebase.py` and `engine/rules/ay2026_27.py` for the
  pattern to follow.

## Commit messages

This repo loosely follows [Conventional Commits](https://www.conventionalcommits.org/):
`feat(itr-engine): ...`, `fix: ...`, `test: ...`, `docs: ...`,
`chore(skill): ...`. Skim `git log` for examples before your first commit.

## Pull requests

- Keep PRs focused — one logical change per PR.
- If you touched the engine, note the test command output (or the new/changed
  assertions) in the PR description.
- If you touched `references/*.md` in a way that changes a number a filer
  would rely on (a slab, a limit, a rate, a due date), call that out
  explicitly in the PR description — these are the details most likely to go
  stale between assessment years.

## Not sure where something belongs?

Open an issue first — happy to point you at the right file before you write
code.
