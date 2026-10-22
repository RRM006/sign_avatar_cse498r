# milestone_log.md — Big-Picture Status Board

> This answers one question: **"Where are we in the whole project right now?"**

**Status keys:** ⬜ Not started · 🟨 In progress · 🟦 Blocked · ✅ Done · ⛔ Retired

**Last updated:** 2026-10-22
**Current phase:** Phase 3 — 5-day prototype, in progress (milestones 5–7 done 2026-10-22; milestone 8 code done and run in TEST mode only, ADR-0025; milestones 9–10 done 2026-10-22; real team review of the pilot drafts pending). The design was approved in principle on
2026-10-22 (ADR-0014–0021). Each step starts only on the owner's explicit go.

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
| 3b | Read-only repo + dataset re-audit | ✅ | Done 2026-10-21. Measurements in `test_log.md` (2026-10-21); contradictions listed in `research/design_proposals/03_…` §B |
| 4 | Design / pipeline chosen | ✅ | Approved in principle 2026-10-22; recorded as ADR-0014–0021 (owner bullets Accepted, specifics Accepted in principle) |
| 5 | Day 1 — Step 1: env check + config | ✅ | env_report.json with real values; tests pass or failures documented; only authorised files changed. Done 2026-10-22: 8/8 checks pass, 30 tests pass (`test_log.md`) |
| 6 | Day 1 — Step 2: manifest + S1 v0 + pilot50_v1 | ✅ | 5,010 manifest rows; leakage tests pass; 50/50 copies SHA-256 identical; sources unchanged. Done 2026-10-22: all met; S1 v0 2,700/357/319 groups; pilot 40/5/5, option B (ADR-0022) (`test_log.md`) |
| 7 | Day 2 — Step 1: pilot extraction + QC; Step 2: gloss convention v0.1 + G0 drafts (+ team review) | ✅ | 50/50 extracted or failures logged; timestamp irregularity measured per clip; kill-and-resume test passes; 50/50 annotation rows with a status (no row marked reviewed without a real review). Step 1 done 2026-10-22: 50/50 per mode, resume test passed, VIDEO mode chosen (ADR-0023). Step 2 done 2026-10-22: 50/50 rows auto_draft, validation clean (ADR-0024). The team review itself is pending (open_questions G10) (`test_log.md`) |
| 8 | Day 3 — Model A pilot | 🟨 | G0 vs GRU curves + per-item table ("pipeline test") on team-reviewed rows — or, only if the owner decides, a clearly labelled auto-draft pipeline test; resume test passes. Needs G10 (team review). 2026-10-22: code done and run in TEST mode on fake review data (ADR-0025): overfit 1/40 and kill-and-resume pass, 111 tests (`test_log.md`). The real run waits for a real video review |
| 9 | Day 4 — Model B + text ablation + B0/B1 | ✅ | masked-loss unit test; overfit 1 → 40; table vs B0/B1 ("pipeline test"). Done 2026-10-22: masked-loss test passes; overfit 1 → 5.1% of the start loss, overfit 40 beats B0 on train; 3 seeds × {gloss, text}; kill-and-resume identical; 125 tests (`test_log.md`, ADR-0026). Finding: Model B ≈ B0 on held-out clips (G11) |
| 10 | Day 5 — retarget + viewer + end-to-end demo | ✅ | one sentence → video with versioned log; skeleton fallback; limitations written. Done 2026-10-22: sentence 3246 → Model B + B1 side by side (G11, ADR-0027); skeleton MP4 + browser VRM viewer with .webm recording; `demo_log.json` (versions, hashes); round-trip ≤ 3.4° on the real avatar; `LIMITATIONS.md`; 140 tests (`test_log.md`). Not reviewed by a BdSL-competent person |
| 11 | Weeks 2–4 — full data, model comparison, evaluation, report | ⬜ | per design doc 04 §G; deadline (TBD — G6). Full-dataset plan drafted as proposal 05 on 2026-10-22; not approved |

---

## Roadmap phases

### Phase 0 — Setup
**Goal:** An organized folder and a living project memory.
**Move on when:** Milestone 0 is done. ✅ (2026-09-27)

### Phase 1 — Research & idea generation
**Goal:** Collect and understand the literature, bring in the owner's ideas and requirements, and answer
the scope and dataset questions.
**Move on when:** Done ✅ (2026-09-27 — ADR-0007, ADR-0008, ADR-0009, ADR-0012).

### Phase 2 — Design & pipeline decision
**Goal:** Choose, with the owner, the end-to-end pipeline.
**Move on when:** Done ✅ (2026-10-22 — design approved in principle, ADR-0014–0021).

### Phase 3 — 5-day prototype (current, in progress)
**Goal:** An end-to-end pipeline test on the 50-video pilot (milestones 5–10).
**Move on when:** Milestone 10 is done or the owner decides.

### Phase 4 — Full-dataset experiments, evaluation and report
**Goal:** Milestone 11. Deadline: (TBD — confirm with owner, G6).

---

## Notes
- Nothing is "done" until its testable definition above is met **and** the result is recorded
  (in `test_log.md` where measurement applies).
- Don't start a later milestone early without the owner's go.
- 2026-10-22: notebooks `01_manifest`, `02_extract`, `03_gloss` were added as thin wrappers of the
  Day 1–2 CLI steps (not executed); `00_env_check` ran on Day 1. The Session 6 reports and memory
  updates, along with six earlier commits, were published in Session 7 at `62e719e`.
