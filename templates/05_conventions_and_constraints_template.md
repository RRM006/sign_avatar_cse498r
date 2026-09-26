# 05 — Conventions & Constraints

<!-- HOW TO USE THIS TEMPLATE
Capture the conventions ACTUALLY USED in this codebase and the HARD rules that bind it — not generic
best practices. Read real files to infer style; read the project's rules/notes for constraints.
This is the file the MASTER_PROMPT's <CONSTRAINTS> pulls from, so be precise.
Delete guidance comments before saving. Mark inferences "(inferred)". Unknowns go in 07. -->

## A. Non-negotiable / hard rules (never break these)

<!-- The absolute rules of this project — safety, legal, ethical, data-handling, or architectural
invariants that must never be broken even if a user asks. If the project states them explicitly,
quote/cite. If there are none stated, say so and infer any implicit ones carefully (marked). -->

1. [[rule — stated plainly, with the "why" and where it's enforced in code if applicable]]
2. [[...]]

## B. How the owner wants an assistant to work (working style)

<!-- The project's expectations for HOW to collaborate: plan-first vs. just-do-it, commit/PR habits,
step size, review cadence, communication style, session rituals. Pull from the project's own
guidance docs (e.g. a CLAUDE.md / CONTRIBUTING / notes). If undocumented, mark "(inferred)". -->

- [[working-style expectation]]
- [[...]]

## C. Hard technical constraints

<!-- The immovable technical box: supported OS/browsers/runtimes, hardware limits, cost/free-tier
limits, offline/on-prem requirements, performance budgets, compliance, "must not depend on X". -->

- [[constraint — with the reason]]
- [[...]]

## D. Coding conventions actually used in this codebase

<!-- Observe the real code and describe its actual style so a newcomer's changes blend in: naming,
file/module organization, typing, error handling, config/secrets handling, the project's recurring
patterns/idioms (e.g. a specific interface/seam pattern), migration/versioning discipline, frontend
conventions, test conventions. Point at exemplar files. Do NOT prescribe generic best practices the
project doesn't follow. -->

- [[convention — with an example file/location]]
- [[...]]

## E. Things a new AI should NEVER do without asking first

<!-- Concrete "stop and ask" list: irreversible actions, protected areas ("don't touch module X"),
things that would violate section A/C, decisions that are locked, anything easy to get wrong. -->

- [[don't do X without asking — why]]
- [[...]]
