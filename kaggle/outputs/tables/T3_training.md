### Training runs used for the paper (frozen configuration; measured)

| role | run | seed | best epoch | epochs run | train time (s) | device | GPU | train loss at best | val monitor at best | monitor |
|---|---|---|---|---|---|---|---|---|---|---|
| model_a | G0REF_text2gloss_kaggle400_20261023T142908Z | 42 | 62 | 92 | 67.9 | cuda:0 | Tesla T4; Tesla T4 | 0.9777 | 31.3609 | val WER vs G0 (%) |
| model_a | G0REF_text2gloss_kaggle400_20261023T142908Z | 43 | 92 | 122 | 89.3 | cuda:0 | Tesla T4; Tesla T4 | 0.9764 | 31.9527 | val WER vs G0 (%) |
| model_a | G0REF_text2gloss_kaggle400_20261023T142908Z | 44 | 57 | 87 | 63.9 | cuda:0 | Tesla T4; Tesla T4 | 0.9742 | 31.3609 | val WER vs G0 (%) |
| model_b_gloss | gloss2motion_gloss_kaggle400_20261023T135437Z | 42 | 38 | 98 | 98.7 | cuda:0 | Tesla T4; Tesla T4 | 0.4738 | 0.6382 | masked pos L1 (std.) |
| model_b_gloss | gloss2motion_gloss_kaggle400_20261023T135437Z | 43 | 27 | 87 | 87.3 | cuda:0 | Tesla T4; Tesla T4 | 0.5342 | 0.6325 | masked pos L1 (std.) |
| model_b_gloss | gloss2motion_gloss_kaggle400_20261023T135437Z | 44 | 18 | 78 | 77.9 | cuda:0 | Tesla T4; Tesla T4 | 0.5826 | 0.6420 | masked pos L1 (std.) |
| model_b_text | gloss2motion_text_kaggle400_20261023T141059Z | 42 | 66 | 126 | 130.5 | cuda:0 | Tesla T4; Tesla T4 | 0.3813 | 0.6424 | masked pos L1 (std.) |
| model_b_text | gloss2motion_text_kaggle400_20261023T141059Z | 43 | 34 | 94 | 96.9 | cuda:0 | Tesla T4; Tesla T4 | 0.5057 | 0.6214 | masked pos L1 (std.) |
| model_b_text | gloss2motion_text_kaggle400_20261023T141059Z | 44 | 38 | 98 | 101.3 | cuda:0 | Tesla T4; Tesla T4 | 0.4624 | 0.6478 | masked pos L1 (std.) |

Early stopping on VAL only. Train loss vs val monitor at the best epoch shows over-fitting.
