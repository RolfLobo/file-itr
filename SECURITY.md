# Security Policy

## Supported versions

Security and privacy fixes apply to the latest commit on `main`.

## Reporting a vulnerability

Do not open a public issue containing taxpayer information, credentials, or an
unredacted document. If you find a security or privacy issue — for example, a
skill instruction that could lead to sensitive data being saved or logged
somewhere unsafe, or an engine bug that could cause tax to be silently
under- or over-computed — use GitHub's private vulnerability reporting
(the repo's **Security** tab → "Report a vulnerability") if it's enabled.
Otherwise, reach the maintainer through their GitHub profile with a minimal,
non-sensitive notice and wait for a private channel before sharing details.

## What's in scope

This project never handles live credentials: it doesn't connect to the
internet, store your password/OTP, or submit/e-verify anything on your
behalf — those remain your actions by design. Its real risk surface is
narrower:

- The **engine** (`skills/itr-india/engine/`) computing a wrong number for a
  case it believes is in scope, rather than failing loud.
- The **skill** (`SKILL.md`/`references/`) giving guidance that could cause a
  user to mishandle their own sensitive documents (e.g. suggesting they be
  saved or pasted somewhere public).

Report either of those the same way as above.

## Sensitive-data handling

This repository must never contain:

- Real PAN, Aadhaar, passport, or other taxpayer identifiers
- Bank, broker, demat, or loan account numbers
- Passwords, OTPs, tokens, or portal session data
- Form 16, Form 26AS, AIS/TIS, or ITR JSON — real or unredacted
- Screenshots of a real filing

`.gitignore` blocks common filenames for these (`*AIS*`, `*26AS*`,
`*Form16*`, `*ACK*`, `*ChallanReceipt*`, `*Preview*`, `*.json.personal`), but
filename matching is a safety net, not a guarantee — check `git status` and
`git diff` before pushing, especially when attaching a repro case to an issue
or PR.

If personal tax data is ever committed, treat it as urgent: rotate or revoke
any exposed credential, and note that removing the file in a follow-up commit
is not sufficient — the data remains in git history until the history itself
is purged.
