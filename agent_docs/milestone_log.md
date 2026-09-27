# milestone_log.md — Big-Picture Status Board

> This answers one question: **"Where are we in the whole project right now?"**

**Status keys:** ⬜ Not started · 🟨 In progress · 🟦 Blocked · ✅ Done · ⛔ Retired

**Last updated:** 2026-09-27
**Current phase:** Phase 2 — Design & pipeline decision. Scope and dataset are settled
(ADR-0007–0009); the design itself is still open (ADR-0002, ADR-0010).

---

## Milestones / modules

Implementation milestones will be added once the owner chooses a design. The deliverable they must
lead to: report + literature review + trained model + results, aimed at a publishable paper (ADR-0007).

| # | Milestone / Module | Status | "Done" means (testable) |
|---|--------------------|:------:|--------------------------|
| 0 | Project folder bootstrap | ✅ | `CLAUDE.md` + `agent_docs/` exist; materials are in `research/` and `dataset/`; `templates/` removed; file counts verified (see `test_log.md`, 2026-09-27) |
| 1 | Initial literature review | ✅ | Owner declared it complete, 2026-09-27 (ADR-0012). 6 papers analysed + 2 comparisons; wrong context removed |
| 2 | Scope questions answered | ✅ | A1–A3 answered and recorded (ADR-0007), 2026-09-27 |
| 3 | Initial dataset understood | ✅ | B1–B6 answered and recorded (ADR-0008, ADR-0009), 2026-09-27. Left open: signer count (B7), split definition (B8) |
| 4 | Design / pipeline chosen | ⬜ | **(TBD — decide with owner)**. At minimum, C1–C5 in `open_questions.md` are decided and recorded as ADRs. Next up |
| … | Implementation / evaluation milestones | ⬜ | (TBD — defined after milestone 4) |

---

## Roadmap phases

### Phase 0 — Setup
**Goal:** An organized folder and a living project memory.
**Move on when:** Milestone 0 is done. ✅ (2026-09-27)

### Phase 1 — Research & idea generation
**Goal:** Collect and understand the literature, bring in the owner's ideas and requirements, and answer
the scope and dataset questions.
**Move on when:** Done ✅ (2026-09-27 — ADR-0007, ADR-0008, ADR-0009, ADR-0012).

### Phase 2 — Design & pipeline decision (current)
**Goal:** Research and then choose, with the owner, the end-to-end pipeline: sign representation, text →
sign mapping, sign lexicon, avatar technology, model/training and evaluation details.
**Move on when:** (TBD — decide with owner).

### Later phases
(TBD — defined once the design is chosen.)

---

## Notes
- Nothing is "done" until its testable definition above is met **and** the result is recorded
  (in `test_log.md` where measurement applies).
- Don't start a later milestone early without the owner's go.
