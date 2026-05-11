# Writing Guidelines

## Executive Summary

2-3 sentences. What and why.

**Good:**
> Add an `aig update` command for selective component updates. Currently `--force` overwrites everything, losing user customizations.

**Bad:**
> This proposal aims to enhance the user experience by providing a more granular approach to updating project components, which will enable users to maintain their customizations while still benefiting from upstream improvements.

**Rule:** If it takes more than 30 seconds to read, it's too long.

## Goals vs Non-Goals

Non-goals are "things someone might expect, but we're explicitly excluding."

| Good Non-Goal                        | Bad Non-Goal             |
| ------------------------------------ | ------------------------ |
| Three-way merge — Too complex for v1 | Make coffee — Irrelevant |
| GUI support — CLI-first MVP          | Be fast — Obvious goal   |

## Design Section

| Include                    | Skip                        |
| -------------------------- | --------------------------- |
| Component diagrams         | Implementation code details |
| Data flow                  | Pseudo-code                 |
| CLI/API interface examples | Line-by-line logic          |
| File structure             |                             |

## Alternatives Considered

Proves you thought it through. **Minimum 2 alternatives.**

| Alternative    | Pros              | Cons              | Why Not Chosen    |
| -------------- | ----------------- | ----------------- | ----------------- |
| Git submodules | Proper versioning | Complex for users | Friction > benefit |
| Manual copy    | No tooling        | Error-prone       | Poor UX           |

## Open Questions

Genuine unknowns only.

**Good:** Should `--dry-run` be the default? Current thinking: No, but show summary before applying.

**Bad:** What color should the output be?

## Anti-Patterns

| Anti-Pattern            | Problem                      | Fix                                            |
| ----------------------- | ---------------------------- | ---------------------------------------------- |
| **The Novel**           | 20+ pages nobody reads       | Keep under 3 pages (excl. diagrams)            |
| **The Vague Handwave**  | "Figure it out later"        | If you can't explain it, you don't understand it |
| **The Fait Accompli**   | Proposal after implementation| Proposals come BEFORE code                     |
| **The Kitchen Sink**    | Every possible feature       | Focus on MVP, use non-goals to defer           |

## Security-Sensitive Features

For auth, crypto, or data access features:

1. Write draft design
2. Get security review **BEFORE** task decomposition
3. Incorporate security requirements
4. THEN break into implementation tasks
