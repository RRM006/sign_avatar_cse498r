# session_protocol.md — How We Start and End Every Session

<!-- HOW TO USE THIS TEMPLATE
This is the "operating manual" — the habit that makes the memory system actually work. It is mostly
generic and can be used almost as-is; just fill the [[project name]] and adjust the file list if the
project uses different living docs. Delete guidance comments before saving. -->

> This file is the operating manual for [[Project Name]]. It's not project content — it's the habit
> that keeps the shared memory (`agent_docs/`) useful across sessions. Copy-paste the prompts below.

---

## ▶️ START-OF-SESSION prompt (paste this first, every new session)

```
Start of session. Before doing anything else:
1. Read CLAUDE.md.
2. Read these and give me a 5-line summary of where we are:
   - agent_docs/session_protocol.md
   - agent_docs/current_task.md
   - agent_docs/changelog.md (just the newest 2 entries)
   - agent_docs/milestone_log.md (just the status board + current phase)
3. Tell me the single next step from current_task.md.
4. Then STOP and wait for my "go". Do not write code or make changes yet.
Remember: [[the owner's core working rules — e.g. don't assume anything, plan first, keep it
cross-platform, respect the non-negotiable rules]].
```

Why: an AI starts each session with a blank memory and auto-loads only `CLAUDE.md`. This prompt makes
it read the few files that matter and orient in seconds — without re-explaining the project.

---

## ⏹️ END-OF-SESSION prompt (paste this before you stop working)

```
End of session. Please update our memory files now:
1. changelog.md — add a new entry at the TOP using the template (Did / Decided / Broke / Deferred / Next).
2. current_task.md — OVERWRITE it so it describes exactly what to do next session and the precise next step.
3. milestone_log.md — update any milestone/status that changed.
4. decisions.md — if we made a real decision, add a new ADR entry.
5. test_log.md — if we tested anything, add the result (with numbers/evidence).
6. codebase_map.md — if we added or moved files, update the map.
Show me a short summary of what changed in each file before saving.
```

Why: this is what prevents "the AI forgot where we were." A couple of minutes at the end saves
re-explaining everything next time.

---

## 🔁 DURING a session — small reminders

- If the AI starts coding without a plan: `Stop. Show me the plan and options first, then wait for my go.`
- Keep the main thread focused on the current task; park side questions.
- If context feels full or the AI seems to forget recent things, reset the session and re-paste the
  START-OF-SESSION prompt (CLAUDE.md reloads automatically).

---

## The habit in one line
**Start:** paste the start prompt → read → plan → go.
**End:** paste the end prompt → update changelog + current_task → stop.
