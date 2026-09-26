# BOOTSTRAP_PROJECT_PROMPT

> Use this when you are **starting a new project** (or setting up an existing one that has no working
> docs yet) and want the "living project brain" — a `CLAUDE.md` at the root plus an `agent_docs/`
> folder of continuously-updated docs — tailored to what you want to build.
>
> This is different from `GENERATE_KIT_PROMPT.md`: that one produces a **static handoff snapshot**
> (`ai_handoff_kit/`) of an existing codebase; **this** one seeds the **living working scaffold** you
> maintain as you build.
>
> Copy everything inside the fenced block below and give it to an AI running **inside the new
> project's repo**, with `universal_ai_kit/` present, and your project idea/context dropped into
> `new_project_intake/`.

---

```
You are setting up the "living project brain" for THIS project: a CLAUDE.md at the repo root plus an
agent_docs/ folder of continuously-updated working docs, tailored to what the owner wants to build.
This scaffold is what lets any AI assistant pick the project up session after session without
re-explaining it. Follow these steps exactly.

STEP 1 — UNDERSTAND WHAT'S BEING BUILT
- Read EVERYTHING in `new_project_intake/` — this is the owner's project idea,
  goals, specs, notes, and constraints. It is the primary source of truth for a project that may not
  have much code yet.
- Also read whatever code/config already exists in the repo (there may be little or none — that's
  fine; this is a bootstrap).
- Build a clear picture: what the project is, who it's for, the problem it solves, the intended
  stack, the major pieces/milestones, the hard rules and constraints, and any decisions already made.
- GROUNDING RULE: base everything on the intake and any existing code. Where the intake is silent,
  do NOT invent specifics — either leave a clearly-marked "(TBD — decide with owner)" placeholder or
  record the open question. Mark anything you infer "(inferred)".

STEP 2 — CREATE THE WORKING SCAFFOLD
Using the templates in `templates/`, create these files (dropping the `_template`
suffix), filled in from the intake:

  ./CLAUDE.md                          (from templates/CLAUDE_TEMPLATE.md — SHORT root guide)
  ./agent_docs/constitution.md         (from templates/agent_docs/constitution_template.md)
  ./agent_docs/session_protocol.md     (from templates/agent_docs/session_protocol_template.md)
  ./agent_docs/current_task.md         (from templates/agent_docs/current_task_template.md)
  ./agent_docs/changelog.md            (from templates/agent_docs/changelog_template.md)
  ./agent_docs/milestone_log.md        (from templates/agent_docs/milestone_log_template.md)
  ./agent_docs/decisions.md            (from templates/agent_docs/decisions_template.md)
  ./agent_docs/codebase_map.md         (from templates/agent_docs/codebase_map_template.md)
  ./agent_docs/test_log.md             (from templates/agent_docs/test_log_template.md)

Fill each file with REAL content from the intake. Replace every [[placeholder]] and remove the
templates' own guidance/comment lines from the final files. In particular:
- CLAUDE.md: short (aim under ~200 lines) — what the project is, the non-negotiable rules, how the
  owner wants the AI to work, tech constraints, chosen stack (mark undecided parts TBD), the key
  commands (as they become known), and the agent_docs/ reading list. It must point to agent_docs/
  for detail, not duplicate it.
- constitution.md: the stable purpose, the non-negotiable rules (with the "why"), the planned major
  pieces + build order, hard constraints, and honest "what's genuinely hard".
- milestone_log.md: one row per planned milestone/module, each with a CONCRETE, testable "done"
  definition; set every status to ⬜ Not started (or the true current status).
- current_task.md: seed the very first concrete step so the first real session knows where to begin.
- changelog.md: seed the "Session 0 — bootstrap" entry.
- decisions.md: record any founding decisions the intake already implies as ADR-0001+ (e.g. the
  choice to use this memory system, the stack, key constraints). Do not fabricate reasons — if a
  choice was made but the reason isn't given, say the reason is TBD.
- codebase_map.md: current structure = what's actually on disk today; planned structure = the target
  layout implied by the intake (clearly marked as planned).
- test_log.md: list what's worth measuring/verifying for this project; leave results empty until work
  is tested.

STEP 3 — HANDLE GAPS HONESTLY
- Do not guess project facts. Where the intake doesn't say, use "(TBD — decide with owner)" and/or
  note it. Keep the non-negotiable rules conservative and safe if the owner hasn't stated them
  (e.g. "never commit secrets", "use only synthetic/consented data in dev") and flag them for
  confirmation.

STEP 4 — REPORT BACK
- Print the full file tree you created (CLAUDE.md + agent_docs/…).
- List every "(TBD — decide with owner)" and every open question you left, so the owner knows exactly
  what to decide next.
- Tell the owner the recommended next move: paste the START-OF-SESSION prompt from
  agent_docs/session_protocol.md to begin the first real working session.

HARD RULES WHILE DOING THIS
- Only create CLAUDE.md and the agent_docs/ files. Do NOT write application code, and do NOT modify
  the universal_ai_kit/ templates. (Read the repo freely; write only these scaffold docs.)
- Ground everything in the intake / existing code. Mark inferences "(inferred)"; mark unknowns
  "(TBD — decide with owner)". Never invent project history, versions, or decisions.
- Keep CLAUDE.md short and pointer-style; put detail in agent_docs/.
- If the owner's intake states a working style (e.g. "plan before coding, wait for my go"), carry it
  into CLAUDE.md and session_protocol.md verbatim in spirit.

OPTIONAL — if the owner also wants a static handoff snapshot of the project as it stands, run
`universal_ai_kit/GENERATE_KIT_PROMPT.md` afterwards to produce an `ai_handoff_kit/` as well. The two
are complementary: agent_docs/ is the living brain you maintain; ai_handoff_kit/ is a point-in-time
package for handing the project to someone (or some AI) cold.
```
