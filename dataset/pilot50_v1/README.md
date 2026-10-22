# pilot50_v1

The 50-video pilot set for the 5-day prototype (milestone 6). Selected from split S1 by
`bdsl.cli pilot-select`; see `SELECTION_PROTOCOL.md` for the rules and input hashes.

- `videos/` — byte-identical **copies** of `initial_dataset/SIGN_LANGUAGE_DATA/<Index>.mp4`
  (gitignored; ADR-0017). The originals are never moved or changed.
- `pilot50_manifest.csv` — one row per clip: Index, split, selection reason, sentence, metadata and
  the SHA-256 checked after copying.

This is **not** the committed 50-clip sample in `initial_dataset/videos/` (`sample50`).
Results on this pilot are "pipeline tests", not evidence of generalisation.
