# session_protocol.md — How We Start and End Every Session

> This file is the operating manual for **Bangla Text-to-BdSL Translation Using a 3D Avatar**. It's not
> project content. It's the habit that keeps the shared memory (`agent_docs/`) useful across sessions.
> Copy-paste the prompts below.

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
   - agent_docs/open_questions.md (just the question titles)
3. Tell me the single next step from current_task.md.
4. Then STOP and wait for my "go". Do not write code or make changes yet.
Remember: don't invent project facts, ask when something important is unclear, don't finalize any
pipeline/model/dataset/avatar/evaluation decision without me, keep evidence vs. proposals vs. future
work separate, and don't read the PDFs in research/papers/.
```

Why: an AI starts each session with a blank memory and auto-loads only `CLAUDE.md`. This prompt makes
it read the few files that matter and get oriented quickly, without you re-explaining the project.

---

## ⏹️ END-OF-SESSION prompt (paste this before you stop working)

```
End of session. Please update our memory files now:
1. changelog.md — add a new entry at the TOP using the template (Did / Decided / Broke / Deferred / Next).
2. current_task.md — OVERWRITE it so it describes exactly what to do next session and the precise next step.
3. milestone_log.md — update any milestone/status that changed.
4. decisions.md — if I confirmed a real decision, add a new ADR entry.
5. open_questions.md — mark answered questions (with the ADR id) and add any new ones.
6. test_log.md — if we tested or verified anything, add the result (with numbers/evidence).
7. codebase_map.md — if we added or moved files, update the map.
Show me a short summary of what changed in each file before saving.
```

Why: this is what prevents "the AI forgot where we were." A couple of minutes at the end saves
re-explaining everything next time.

---

## 🔁 DURING a session — small reminders

- If the AI starts deciding the design on its own: `Stop. List the options with trade-offs and a
  recommendation, then wait for my decision.`
- If the AI starts coding without being asked: `Stop. Show me the plan first, then wait for my go.`
- New ideas or requirements from you: drop them in `new_project_intake/` or say them in chat, and ask
  the AI to record them.
- Keep the main thread focused on the current task; park side questions in `open_questions.md`.
- If context feels full or the AI seems to forget recent things, reset the session and re-paste the
  START-OF-SESSION prompt (CLAUDE.md reloads automatically).

---

## The habit in one line
**Start:** paste the start prompt → read → plan → go.
**End:** paste the end prompt → update changelog + current_task → stop.
