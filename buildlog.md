# Build log

Chronological record of changes and verification. Timestamps include the timezone.
Design choices and their rationale belong in `docs/decisions.md`; this log records the work performed.

## 2026-11-03 12:14:18 IST (+05:30) — Establish working rules

- Backfilled from commit `b9dd436`, using its author timestamp.
- Read the three project docs and added `AGENTS.md` with incremental development, verification, and harness safety rules.
- Verification: reviewed the staged diff and passed `git diff --cached --check`. No application code or runtime tests existed.

## 2026-11-03 12:16:13 IST (+05:30) — Add change logging

- Added this log and updated `AGENTS.md` to require a timestamped entry for every change in the same commit.
- Clarified that decision entries are for design trade-offs, not routine changes.
- Verification: reviewed the documentation diff and ran `git diff --check`; no runtime tests needed for documentation changes.
