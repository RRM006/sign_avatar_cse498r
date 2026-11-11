# RESULTS_SUMMARY — kaggle400 experiment

Generated 2026-10-23T15:22:07+00:00 by `kaggle/src/k400/report.py` (notebook 08)
from the files listed below. **Every number is labelled; all are "measured" (none estimated).**

## Status
The single final test evaluation **has run** (`outputs/FINAL_TEST_LOCK.json`, 20261023T151119Z, results `FINAL_test_20261023T151119Z`).

## Honesty rules for using these numbers
- All numbers are **measured** on the kaggle400 subset (320 train / 40 val / 40 test clips): small-scale and
  **signer-dependent** (signers unknown; the same people appear in every split).
- The test split was evaluated **once**, after the configuration was frozen (`outputs/FINAL_TEST_LOCK.json`).
  Nothing was tuned on test.
- **Low coordinate error is not proof of correct sign language.** B0 gives every sentence the same average
  motion and can still have competitive error. Only BdSL-competent human evaluation can test correctness;
  none exists for this project (no human or expert validation is claimed).
- Model A numbers are **agreement with the rule glosser (G0 pseudo-gloss)**, not BdSL correctness: the
  references are G0 auto_draft outputs, not human annotation.
- Model B input glosses are G0 pseudo-glosses (auto_draft), not BdSL annotation.
- Baselines are reported exactly as measured. Where Model B does not beat a baseline, the tables show it.

## Every number, with its source
| quantity | value | label | run_or_eval_id | source_file |
|---|---|---|---|---|
| train clips | 320 | measured | kaggle400_v1 split | data/subset_manifest.csv |
| val clips | 40 | measured | kaggle400_v1 split | data/subset_manifest.csv |
| val OOV token rate vs train vocabulary | 20.7% | measured | kaggle400_v1 split | data/SELECTION_META.json |
| test clips | 40 | measured | kaggle400_v1 split | data/subset_manifest.csv |
| test OOV token rate vs train vocabulary | 12.1% | measured | kaggle400_v1 split | data/SELECTION_META.json |
| test left/right hand coverage | 68.6% / 26.5% | measured | feat_ver fa89892d4908 | processed/qc/hand_coverage_summary.csv |
| train left/right hand coverage | 62.8% / 25.2% | measured | feat_ver fa89892d4908 | processed/qc/hand_coverage_summary.csv |
| val left/right hand coverage | 62.5% / 24.3% | measured | feat_ver fa89892d4908 | processed/qc/hand_coverage_summary.csv |
| all left/right hand coverage | 63.3% / 25.3% | measured | feat_ver fa89892d4908 | processed/qc/hand_coverage_summary.csv |
| model_a seed 42 best epoch | 62 | measured | G0REF_text2gloss_kaggle400_20261023T142908Z | outputs/runs/G0REF_text2gloss_kaggle400_20261023T142908Z/metrics.json |
| model_a seed 42 training time (s) | 67.9 | measured | G0REF_text2gloss_kaggle400_20261023T142908Z | outputs/runs/G0REF_text2gloss_kaggle400_20261023T142908Z/metrics.json |
| model_a seed 43 best epoch | 92 | measured | G0REF_text2gloss_kaggle400_20261023T142908Z | outputs/runs/G0REF_text2gloss_kaggle400_20261023T142908Z/metrics.json |
| model_a seed 43 training time (s) | 89.3 | measured | G0REF_text2gloss_kaggle400_20261023T142908Z | outputs/runs/G0REF_text2gloss_kaggle400_20261023T142908Z/metrics.json |
| model_a seed 44 best epoch | 57 | measured | G0REF_text2gloss_kaggle400_20261023T142908Z | outputs/runs/G0REF_text2gloss_kaggle400_20261023T142908Z/metrics.json |
| model_a seed 44 training time (s) | 63.9 | measured | G0REF_text2gloss_kaggle400_20261023T142908Z | outputs/runs/G0REF_text2gloss_kaggle400_20261023T142908Z/metrics.json |
| model_b_gloss seed 42 best epoch | 38 | measured | gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/runs/gloss2motion_gloss_kaggle400_20261023T135437Z/metrics.json |
| model_b_gloss seed 42 training time (s) | 98.7 | measured | gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/runs/gloss2motion_gloss_kaggle400_20261023T135437Z/metrics.json |
| model_b_gloss seed 43 best epoch | 27 | measured | gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/runs/gloss2motion_gloss_kaggle400_20261023T135437Z/metrics.json |
| model_b_gloss seed 43 training time (s) | 87.3 | measured | gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/runs/gloss2motion_gloss_kaggle400_20261023T135437Z/metrics.json |
| model_b_gloss seed 44 best epoch | 18 | measured | gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/runs/gloss2motion_gloss_kaggle400_20261023T135437Z/metrics.json |
| model_b_gloss seed 44 training time (s) | 77.9 | measured | gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/runs/gloss2motion_gloss_kaggle400_20261023T135437Z/metrics.json |
| model_b_text seed 42 best epoch | 66 | measured | gloss2motion_text_kaggle400_20261023T141059Z | outputs/runs/gloss2motion_text_kaggle400_20261023T141059Z/metrics.json |
| model_b_text seed 42 training time (s) | 130.5 | measured | gloss2motion_text_kaggle400_20261023T141059Z | outputs/runs/gloss2motion_text_kaggle400_20261023T141059Z/metrics.json |
| model_b_text seed 43 best epoch | 34 | measured | gloss2motion_text_kaggle400_20261023T141059Z | outputs/runs/gloss2motion_text_kaggle400_20261023T141059Z/metrics.json |
| model_b_text seed 43 training time (s) | 96.9 | measured | gloss2motion_text_kaggle400_20261023T141059Z | outputs/runs/gloss2motion_text_kaggle400_20261023T141059Z/metrics.json |
| model_b_text seed 44 best epoch | 38 | measured | gloss2motion_text_kaggle400_20261023T141059Z | outputs/runs/gloss2motion_text_kaggle400_20261023T141059Z/metrics.json |
| model_b_text seed 44 training time (s) | 101.3 | measured | gloss2motion_text_kaggle400_20261023T141059Z | outputs/runs/gloss2motion_text_kaggle400_20261023T141059Z/metrics.json |
| model_b_gloss train MPJPE body (training-run evaluation) | 0.187 | measured | gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/runs/gloss2motion_gloss_kaggle400_20261023T135437Z/metrics.json |
| model_b_gloss val MPJPE body (training-run evaluation) | 0.218 | measured | gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/runs/gloss2motion_gloss_kaggle400_20261023T135437Z/metrics.json |
| model_b_text train MPJPE body (training-run evaluation) | 0.168 | measured | gloss2motion_text_kaggle400_20261023T141059Z | outputs/runs/gloss2motion_text_kaggle400_20261023T141059Z/metrics.json |
| model_b_text val MPJPE body (training-run evaluation) | 0.216 | measured | gloss2motion_text_kaggle400_20261023T141059Z | outputs/runs/gloss2motion_text_kaggle400_20261023T141059Z/metrics.json |
| val model_b_gloss mpjpe_body (mean over seeds) | 0.218 | measured | val_20261023T151028Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_gloss mpjpe_lhand (mean over seeds) | 52.1 | measured | val_20261023T151028Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_gloss mpjpe_rhand (mean over seeds) | 61.6 | measured | val_20261023T151028Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_gloss dtw_body (mean over seeds) | 0.194 | measured | val_20261023T151028Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_gloss dtw_lhand (mean over seeds) | 39.9 | measured | val_20261023T151028Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_gloss dtw_rhand (mean over seeds) | 44.6 | measured | val_20261023T151028Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_gloss duration_err_s (mean over seeds) | 2.33 | measured | val_20261023T151028Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_gloss velocity_ratio (mean over seeds) | 0.13 | measured | val_20261023T151028Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_gloss jerk_ratio (mean over seeds) | 0.10 | measured | val_20261023T151028Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_gloss hand_energy_ratio (mean over seeds) | 0.03 | measured | val_20261023T151028Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_gloss diversity_ratio (mean over seeds) | 0.38 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_text mpjpe_body (mean over seeds) | 0.216 | measured | val_20261023T151028Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_text mpjpe_lhand (mean over seeds) | 52.4 | measured | val_20261023T151028Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_text mpjpe_rhand (mean over seeds) | 62.3 | measured | val_20261023T151028Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_text dtw_body (mean over seeds) | 0.192 | measured | val_20261023T151028Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_text dtw_lhand (mean over seeds) | 39.9 | measured | val_20261023T151028Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_text dtw_rhand (mean over seeds) | 45.1 | measured | val_20261023T151028Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_text duration_err_s (mean over seeds) | 2.21 | measured | val_20261023T151028Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_text velocity_ratio (mean over seeds) | 0.18 | measured | val_20261023T151028Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_text jerk_ratio (mean over seeds) | 0.15 | measured | val_20261023T151028Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_text hand_energy_ratio (mean over seeds) | 0.04 | measured | val_20261023T151028Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val model_b_text diversity_ratio (mean over seeds) | 0.46 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B0 mpjpe_body | 0.229 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B0 mpjpe_lhand | 56.8 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B0 mpjpe_rhand | 63.4 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B0 dtw_body | 0.209 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B0 dtw_lhand | 47.3 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B0 dtw_rhand | 47.6 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B0 duration_err_s | 2.35 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B0 velocity_ratio | 0.11 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B0 jerk_ratio | 0.03 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B0 hand_energy_ratio | 0.02 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B0 diversity_ratio | 0.00 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B1 mpjpe_body | 0.265 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B1 mpjpe_lhand | 66.2 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B1 mpjpe_rhand | 67.4 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B1 dtw_body | 0.205 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B1 dtw_lhand | 43.6 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B1 dtw_rhand | 50.4 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B1 duration_err_s | 2.32 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B1 velocity_ratio | 0.98 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B1 jerk_ratio | 1.01 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B1 hand_energy_ratio | 1.03 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val B1 diversity_ratio | 0.94 | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - B0 mpjpe_body | -0.011 [-0.016, -0.005] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - B0 mpjpe_lhand | -4.7 [-6.4, -3.0] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - B0 mpjpe_rhand | -1.8 [-4.5, 1.1] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - B0 dtw_body | -0.014 [-0.020, -0.009] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - B0 dtw_lhand | -7.4 [-9.6, -5.1] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - B0 dtw_rhand | -2.9 [-5.4, -0.2] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - B0 duration_err_s | -0.03 [-0.59, 0.58] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - B1 mpjpe_body | -0.047 [-0.063, -0.031] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - B1 mpjpe_lhand | -14.1 [-17.4, -10.9] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - B1 mpjpe_rhand | -5.8 [-10.9, -1.4] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - B1 dtw_body | -0.011 [-0.027, 0.005] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - B1 dtw_lhand | -3.7 [-6.1, -1.3] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - B1 dtw_rhand | -5.8 [-8.4, -3.1] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - B1 duration_err_s | 0.01 [-0.54, 0.61] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - model_b_text mpjpe_body | 0.002 [-0.002, 0.006] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - model_b_text mpjpe_lhand | -0.3 [-1.5, 0.9] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - model_b_text mpjpe_rhand | -0.7 [-3.2, 1.2] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - model_b_text dtw_body | 0.002 [-0.003, 0.007] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - model_b_text dtw_lhand | -0.0 [-1.3, 1.1] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - model_b_text dtw_rhand | -0.5 [-2.5, 1.3] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_gloss - model_b_text duration_err_s | 0.12 [-0.17, 0.45] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_text - B0 mpjpe_body | -0.013 [-0.020, -0.005] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_text - B0 mpjpe_lhand | -4.4 [-6.7, -2.0] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_text - B0 mpjpe_rhand | -1.1 [-5.0, 3.1] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_text - B0 dtw_body | -0.017 [-0.024, -0.010] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_text - B0 dtw_lhand | -7.4 [-10.1, -4.6] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_text - B0 dtw_rhand | -2.4 [-5.4, 1.1] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val paired diff model_b_text - B0 duration_err_s | -0.15 [-0.57, 0.29] | measured | val_20261023T151028Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val Model A wer (agreement with G0) | 34.5 | measured | val_20261023T151028Z / G0REF_text2gloss_kaggle400_20261023T142908Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val Model A exact_match (agreement with G0) | 30.0 | measured | val_20261023T151028Z / G0REF_text2gloss_kaggle400_20261023T142908Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val Model A tag_accuracy (agreement with G0) | 97.5 | measured | val_20261023T151028Z / G0REF_text2gloss_kaggle400_20261023T142908Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val Model A chrf (agreement with G0) | 60.6 | measured | val_20261023T151028Z / G0REF_text2gloss_kaggle400_20261023T142908Z | outputs/eval/val_20261023T151028Z/metrics.json |
| val Model A bleu4 (agreement with G0) | 47.0 | measured | val_20261023T151028Z / G0REF_text2gloss_kaggle400_20261023T142908Z | outputs/eval/val_20261023T151028Z/metrics.json |
| test model_b_gloss mpjpe_body (mean over seeds) | 0.199 | measured | FINAL_test_20261023T151119Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_gloss mpjpe_lhand (mean over seeds) | 49.5 | measured | FINAL_test_20261023T151119Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_gloss mpjpe_rhand (mean over seeds) | 57.3 | measured | FINAL_test_20261023T151119Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_gloss dtw_body (mean over seeds) | 0.181 | measured | FINAL_test_20261023T151119Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_gloss dtw_lhand (mean over seeds) | 40.0 | measured | FINAL_test_20261023T151119Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_gloss dtw_rhand (mean over seeds) | 41.6 | measured | FINAL_test_20261023T151119Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_gloss duration_err_s (mean over seeds) | 1.92 | measured | FINAL_test_20261023T151119Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_gloss velocity_ratio (mean over seeds) | 0.14 | measured | FINAL_test_20261023T151119Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_gloss jerk_ratio (mean over seeds) | 0.11 | measured | FINAL_test_20261023T151119Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_gloss hand_energy_ratio (mean over seeds) | 0.03 | measured | FINAL_test_20261023T151119Z / gloss2motion_gloss_kaggle400_20261023T135437Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_gloss diversity_ratio (mean over seeds) | 0.43 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_text mpjpe_body (mean over seeds) | 0.198 | measured | FINAL_test_20261023T151119Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_text mpjpe_lhand (mean over seeds) | 48.5 | measured | FINAL_test_20261023T151119Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_text mpjpe_rhand (mean over seeds) | 56.5 | measured | FINAL_test_20261023T151119Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_text dtw_body (mean over seeds) | 0.181 | measured | FINAL_test_20261023T151119Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_text dtw_lhand (mean over seeds) | 38.6 | measured | FINAL_test_20261023T151119Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_text dtw_rhand (mean over seeds) | 42.7 | measured | FINAL_test_20261023T151119Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_text duration_err_s (mean over seeds) | 1.66 | measured | FINAL_test_20261023T151119Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_text velocity_ratio (mean over seeds) | 0.18 | measured | FINAL_test_20261023T151119Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_text jerk_ratio (mean over seeds) | 0.15 | measured | FINAL_test_20261023T151119Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_text hand_energy_ratio (mean over seeds) | 0.05 | measured | FINAL_test_20261023T151119Z / gloss2motion_text_kaggle400_20261023T141059Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test model_b_text diversity_ratio (mean over seeds) | 0.50 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B0 mpjpe_body | 0.212 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B0 mpjpe_lhand | 53.3 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B0 mpjpe_rhand | 63.2 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B0 dtw_body | 0.199 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B0 dtw_lhand | 46.6 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B0 dtw_rhand | 48.5 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B0 duration_err_s | 2.05 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B0 velocity_ratio | 0.11 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B0 jerk_ratio | 0.03 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B0 hand_energy_ratio | 0.02 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B0 diversity_ratio | 0.00 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B1 mpjpe_body | 0.249 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B1 mpjpe_lhand | 61.6 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B1 mpjpe_rhand | 64.9 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B1 dtw_body | 0.198 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B1 dtw_lhand | 43.2 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B1 dtw_rhand | 48.3 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B1 duration_err_s | 1.97 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B1 velocity_ratio | 1.13 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B1 jerk_ratio | 1.19 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B1 hand_energy_ratio | 1.61 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test B1 diversity_ratio | 1.00 | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - B0 mpjpe_body | -0.013 [-0.019, -0.006] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - B0 mpjpe_lhand | -3.8 [-5.6, -2.0] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - B0 mpjpe_rhand | -5.9 [-9.3, -2.6] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - B0 dtw_body | -0.017 [-0.025, -0.009] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - B0 dtw_lhand | -6.6 [-8.8, -4.4] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - B0 dtw_rhand | -6.9 [-10.0, -4.2] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - B0 duration_err_s | -0.13 [-0.63, 0.35] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - B1 mpjpe_body | -0.049 [-0.061, -0.037] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - B1 mpjpe_lhand | -12.1 [-14.9, -9.5] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - B1 mpjpe_rhand | -7.7 [-11.5, -4.0] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - B1 dtw_body | -0.017 [-0.032, -0.004] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - B1 dtw_lhand | -3.2 [-6.2, -0.2] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - B1 dtw_rhand | -6.7 [-9.4, -4.0] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - B1 duration_err_s | -0.05 [-0.59, 0.51] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - model_b_text mpjpe_body | 0.001 [-0.003, 0.006] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - model_b_text mpjpe_lhand | 1.0 [-0.5, 2.4] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - model_b_text mpjpe_rhand | 0.8 [-2.2, 3.6] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - model_b_text dtw_body | -0.000 [-0.005, 0.005] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - model_b_text dtw_lhand | 1.3 [-0.1, 2.9] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - model_b_text dtw_rhand | -1.1 [-2.9, 0.6] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_gloss - model_b_text duration_err_s | 0.26 [0.01, 0.51] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_text - B0 mpjpe_body | -0.014 [-0.022, -0.006] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_text - B0 mpjpe_lhand | -4.8 [-7.7, -2.1] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_text - B0 mpjpe_rhand | -6.7 [-11.3, -2.4] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_text - B0 dtw_body | -0.017 [-0.025, -0.009] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_text - B0 dtw_lhand | -7.9 [-10.8, -5.5] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_text - B0 dtw_rhand | -5.8 [-9.6, -2.4] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test paired diff model_b_text - B0 duration_err_s | -0.39 [-0.83, 0.03] | measured | FINAL_test_20261023T151119Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test Model A wer (agreement with G0) | 19.7 | measured | FINAL_test_20261023T151119Z / G0REF_text2gloss_kaggle400_20261023T142908Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test Model A exact_match (agreement with G0) | 54.2 | measured | FINAL_test_20261023T151119Z / G0REF_text2gloss_kaggle400_20261023T142908Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test Model A tag_accuracy (agreement with G0) | 94.2 | measured | FINAL_test_20261023T151119Z / G0REF_text2gloss_kaggle400_20261023T142908Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test Model A chrf (agreement with G0) | 76.8 | measured | FINAL_test_20261023T151119Z / G0REF_text2gloss_kaggle400_20261023T142908Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |
| test Model A bleu4 (agreement with G0) | 68.7 | measured | FINAL_test_20261023T151119Z / G0REF_text2gloss_kaggle400_20261023T142908Z | outputs/eval/FINAL_test_20261023T151119Z/metrics.json |


## Tables (CSV for data, Markdown for reading, LaTeX for the paper)
- `tables/T1_split` (.csv / .md / .tex)
- `tables/T2_feature_coverage` (.csv / .md / .tex)
- `tables/T3_training` (.csv / .md / .tex)
- `tables/T8_train_val_test` (.csv / .md / .tex)
- `tables/T4_modelB_val` (.csv / .md / .tex)
- `tables/T5_paired_val` (.csv / .md / .tex)
- `tables/T6_modelA_val` (.csv / .md / .tex)
- `tables/T7_error_analysis_val` (.csv / .md / .tex)
- `tables/T4_modelB_test` (.csv / .md / .tex)
- `tables/T5_paired_test` (.csv / .md / .tex)
- `tables/T6_modelA_test` (.csv / .md / .tex)
- `tables/T7_error_analysis_test` (.csv / .md / .tex)

## Figures
- `figures/F1_split_summary.png`
- `figures/F2_curves_modelB_gloss.png`
- `figures/F3_curves_modelB_text.png`
- `figures/F4_curves_modelA.png`
- `figures/F5_methods_val.png`
- `figures/F6_error_analysis_val.png`
- `figures/F5_methods_test.png`
- `figures/F6_error_analysis_test.png`

## Not available yet
- nothing
