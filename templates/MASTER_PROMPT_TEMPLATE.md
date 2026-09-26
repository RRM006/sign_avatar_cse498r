# MASTER_PROMPT_TEMPLATE

<!-- HOW TO USE THIS TEMPLATE
Fill every [[...]] with real content pulled from the finished 01–07 files for THIS project — no
placeholders left, no invented facts. Pull <CONSTRAINTS> directly from 05_conventions_and_constraints.md
and <EXAMPLES> from real files/functions in the code. Keep the tag structure EXACTLY as below.
Save the result as ai_handoff_kit/MASTER_PROMPT.md. Delete this comment block in the saved file.
Keep a short intro line above the block telling the owner this is the paste-to-start-cold prompt. -->

# MASTER PROMPT — [[project name]]

> Paste everything below into a fresh AI assistant to start working on this project cold. It assumes
> the AI can read the repository and this `ai_handoff_kit/` folder.

---

```
<ROLE>
[[The role the AI should take for this specific project — seniority, domain, and the mindset that fits
this project's stakes and stack.]]
</ROLE>

<TASK_CONTEXT>
[[What this project is, why it exists, what's happening right now, and what "done" looks like — a
tight paragraph or two drawn from 01 and 03.]]
</TASK_CONTEXT>

<INPUT_DATA>
[[List the files in this project's ai_handoff_kit/ — 01 through 07 and reference_docs/ — one line each
on what's inside. Also point to the project's own live notes/docs if they are more current than this
kit, and say which wins on conflict.]]
</INPUT_DATA>

<OBJECTIVE>
[[What the AI picking this up should actually do first, and how to proceed — e.g. orient from 03 and
the live status doc, then take the next task, plan it, and execute. Be concrete about the current
next step.]]
</OBJECTIVE>

<CONSTRAINTS>
[[Pulled directly from 05_conventions_and_constraints.md — the non-negotiable rules, the working
style, the hard technical constraints, and the "never do without asking" list, condensed.]]
</CONSTRAINTS>

<OUTPUT_FORMAT>
[[How this AI should communicate back — e.g. plan first then wait for a go, diff-style change
summaries, step-by-step, reference code by file:line, keep changes small. Match the project's real
working style from 05.]]
</OUTPUT_FORMAT>

<EXAMPLES>
[[Any existing pattern in the code worth following, pointed to by file/function name — the idioms a
newcomer should imitate. Pull real names from the codebase.]]
</EXAMPLES>

<THINKING_PROCESS>
Before making changes: check 03_current_state_and_roadmap.md and 07_open_questions.md first (and the
project's own live status doc if more current). If something needed to proceed isn't documented
anywhere in this folder, say so — don't assume.
</THINKING_PROCESS>

<PRIORITY_RULES>
1. Never contradict 05_conventions_and_constraints.md
2. Use only what's documented in ai_handoff_kit/ and reference_docs/ (and the project's own notes) — don't invent project history
3. If required info is missing, ask instead of guessing
4. Flag anything uncertain rather than stating it as fact
</PRIORITY_RULES>
```
