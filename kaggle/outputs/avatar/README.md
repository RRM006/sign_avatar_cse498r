# Avatar exports (test sentences)

# Avatar export — limitations (read before showing this anywhere)

- kaggle400 is small-scale (320 training clips) and signer-dependent. Model B's motion is a model output
  from G0 pseudo-gloss input; it has NOT been checked by a BdSL-competent person.
- B1 replays the real recording of a DIFFERENT training sentence (most similar by gloss words).
- "Real" is the MediaPipe reconstruction of the actual test recording (noisy hands, monocular depth).
- No claim of correct BdSL grammar, comprehensibility or naturalness is made. Hand sides are MediaPipe's
  labels as given (mirroring unknown, G8). The face mapping to avatar expressions is rough and unchecked.

- `1255/`: তুমি কি সি পি কিভাবে (B1 source 787)
- `2513/`: আমার চাচাতো ভাই নেপাল যাবে (B1 source 2492)
- `1863/`: আমার ভাই বিমানে যাবে (B1 source 1663)
- `3061/`: আমি বৃহস্পতিবার এ কানাডা যাব (B1 source 3062)
- `3232/`: আমি সোমবারে জাপান যাবো (B1 source 3098)
