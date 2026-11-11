### VAL: Model A — agreement with the rule glosser (G0 pseudo-gloss); NOT BdSL correctness

| model | split | seeds | items | gloss WER vs G0 (%) | exact match (%) | tag accuracy (%) | chrF | BLEU-4 | items with source OOV |
|---|---|---|---|---|---|---|---|---|---|
| A-GRU trained on G0 pseudo-glosses | val | 3 | 40 | 34.5 ± 2.5 [23.9, 44.6] | 30.0 ± 0.0 [16.7, 44.2] | 97.5 ± 0.0 [93.3, 100.0] | 60.6 ± 0.5 [50.1, 71.3] | 47.0 ± 2.2 [32.9, 60.2] | 22 |

References are G0 auto_draft outputs. Mean ± sd over 3 seeds [95% bootstrap CI].
