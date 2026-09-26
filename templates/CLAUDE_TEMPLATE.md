# CLAUDE_TEMPLATE

<!-- HOW TO USE THIS TEMPLATE
This becomes CLAUDE.md at the NEW project's root. Claude Code auto-reads CLAUDE.md at the start of
every session, so keep it SHORT (aim under ~200 lines) and point to the living docs in agent_docs/
for detail. Fill every [[...]] from the project intake/idea. Delete these guidance comments and any
section that genuinely doesn't apply. Keep it plain and skimmable. -->

# CLAUDE.md — [[Project Name]]

> Claude Code (and any AI assistant) reads this file at the start of every session.
> Keep it SHORT. The detailed, living docs are in `agent_docs/` (listed at the bottom).

## What this project is

[[2–5 sentences: what the project is, who it's for, and what it does — in plain language.
State the current phase/status in one line so a fresh session knows where things stand.]]

## NON-NEGOTIABLE RULES (never break these)

<!-- The absolute rules of this project — safety/legal/ethical/data/architectural invariants that
must never be broken, even if a user asks. If the project has none yet, write the few that clearly
apply (e.g. "never commit secrets", "never touch production data") and refine as it grows. -->

1. [[rule — one line, with the "why" if it isn't obvious]]
2. [[...]]

## HOW I WANT YOU (THE AI) TO WORK WITH ME

<!-- The owner's collaboration preferences. Common, strong defaults shown — keep/edit to taste. -->

- [[e.g. Plan with me first, then wait for my "go" before writing code.]]
- [[e.g. Before coding, show a short plan: which files, what approach, and why.]]
- [[e.g. When there's a real choice, give me 2–3 options with simple trade-offs + a recommendation.]]
- [[e.g. Make small, reviewable changes — one step at a time. No giant code dumps.]]
- [[e.g. If anything is unclear, ASK. Do not guess.]]
- [[any environment/platform requirement, e.g. "must work on Windows AND Linux from one setup".]]

## TECH CONSTRAINTS

[[The immovable technical box: platforms/OS/browsers, hardware limits, cost/free-tier limits,
offline/on-prem needs, performance budgets, compliance. One line each. Omit if none yet.]]

## CURRENT STACK

[[The chosen languages, frameworks, database, key libraries, and hosting — with a one-line reason or
a pointer to the ADR in decisions.md. Mark anything still undecided as "(TBD — see open questions)".]]

## COMMANDS

<!-- The handful of commands used constantly. Fill as soon as they exist. -->

- Setup / install: `[[command]]`
- Run (dev): `[[command]]`
- Test: `[[command]]`
- Build / deploy: `[[command]]`

## CONVENTIONS (follow what's actually in the code)

[[Naming, file organization, the project's recurring patterns/idioms, and any style rules the code
actually follows. Keep it short; the detail lives in agent_docs/ as the project grows.]]

## PROJECT MEMORY FILES — our shared brain (in `agent_docs/`)

**At the START of every session, read these in order:**
1. `agent_docs/session_protocol.md` — exactly how we start and end a session
2. `agent_docs/current_task.md` — what we are doing RIGHT NOW + the next step
3. `agent_docs/changelog.md` — recent session history (newest first)
4. `agent_docs/milestone_log.md` — status of all planned milestones/modules

**Read these when relevant:**
5. `agent_docs/constitution.md` — full, stable project rules + architecture
6. `agent_docs/decisions.md` — why we chose each tool/approach (ADR style)
7. `agent_docs/codebase_map.md` — where everything lives in the repo
8. `agent_docs/test_log.md` — what was tested + results
[[Add any project-specific docs here as they are created.]]

**At the END of every session**, update `changelog.md` and `current_task.md` (and
`milestone_log.md` / `decisions.md` / `test_log.md` / `codebase_map.md` if they changed). The exact
steps are in `session_protocol.md`.
