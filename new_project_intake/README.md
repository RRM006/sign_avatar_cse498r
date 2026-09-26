# new_project_intake — drop everything about the new project here

Drop everything about the project here — docs, notes, specs, screenshots, links, diagrams,
meeting scribbles, half-formed ideas. **Any format, no polish needed.** The more you put here, the
better the generated output will be.

Then hand any AI the contents of the prompt for the flow you want (run it from inside the project's
repo). It will read the codebase **plus** everything in this folder and produce the output:

- **Starting a NEW project you want to build** → `../BOOTSTRAP_PROJECT_PROMPT.md`
  → creates `CLAUDE.md` + an `agent_docs/` living-docs folder tailored to your idea.
  Here the intake IS the project: your vision, goals, planned features, stack ideas, and rules.
- **Handing off / documenting an EXISTING project** → `../GENERATE_KIT_PROMPT.md`
  → creates a static `ai_handoff_kit/` snapshot. Here the intake is whatever notes exist (or just a
  pointer to the repo's own docs).

## What's useful to drop in

- A one-paragraph "what this project is / who it's for" note (even rough).
- The problem it solves and any goals/success criteria.
- Current status: what works, what's broken, what's next.
- Any rules/constraints (safety, legal, budget, "don't touch X", supported platforms).
- Key decisions already made and why (so the AI doesn't re-litigate them).
- Setup/run notes, environment variables (use placeholders, **never paste real secrets**), test/deploy steps.
- Screenshots, wireframes, API docs, data samples, links to tickets/boards.

## If the project already keeps its own notes

You don't have to copy them. Just leave a pointer here so the AI knows where to look — for example:

```
The project's own living notes are in: ./agent_docs/   (or ./docs/, README, a wiki URL, an issue tracker…)
Treat those as authoritative and more current than anything I paste here.
```

## Tips

- Contradictions are fine — the AI will surface them into `07_open_questions.md` rather than guess.
- Date your notes if they might go stale, so the AI can tell newest from oldest.
- **Never include real secrets, credentials, or real/identifiable personal data.** Use placeholders.

_(Empty for now — drop your material in this folder.)_
