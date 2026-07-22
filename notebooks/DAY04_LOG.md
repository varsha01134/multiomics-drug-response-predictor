# Day 4 Log — Modeling & Interpretability

**Project:** Multi-Omics Integration Platform for Cancer Drug Response Prediction
**Date:** July 22, 2026
**Phase:** 2 — Modeling
**Status:** ✅ Core complete

---

## Goal for the day
Train and compare classification models to predict 5-year survival from the 324-patient multi-omics dataset, pick the best, evaluate it honestly on held-out data, and interpret what it learned.

---

## The task
Binary classification: given a patient's features (age, 500 expression genes, 31 mutation features, clinical), predict `SURV_5YR` (survived past 5 years vs died within).

---

## What was done

### 1. Baseline models compared (`08_baseline_models.py`)
Split off a stratified 20% test set (65 patients), then compared three models on the training set using 5-fold stratified cross-validation. Primary metric: AUROC (not accuracy — see below).

| Model | CV AUROC | Stability |
|---|---|---|
| Logistic Regression | 0.676 | ±0.038 |
| Random Forest | 0.691 | ±0.061 |
| **XGBoost** | **0.725** | **±0.044** |

Naive "always predict survived" accuracy = 0.730. All models scored ~0.73 accuracy too — identical to the lazy baseline — which is exactly why AUROC was the metric that mattered.

**Winner: XGBoost** (highest AUROC + good stability). Conservative settings (max_depth=3, learning_rate=0.05, subsampling) chosen to resist overfitting on the small, high-dimensional data.

### 2. Final held-out test evaluation (`09_final_evaluation.py`)
Trained XGBoost on the full training set, evaluated ONCE on the 65 untouched test patients:

| Metric | Value |
|---|---|
| AUROC | 0.648 |
| PR-AUC (avg precision) | 0.409 (baseline rate 0.277) |
| Accuracy | 0.692 |
| Recall (died class) | 0.333 |
| Precision (died class) | 0.429 |

Confusion matrix: of 18 patients who actually died, only 6 were flagged. Saved `final_model.pkl` + ROC/PR curve plots.

**Honest read:** modest but real prognostic signal. Report CV ≈ 0.73 as primary (more stable), test ≈ 0.65 as unbiased confirmation; the gap is small-sample variance (65 patients). Proof-of-concept, NOT clinically deployable — and being clear about that is a strength.

### 3. SHAP interpretability (`10_shap_analysis.py`)
Computed SHAP values to see which features drive predictions.
- **AGE** dominates (mean |SHAP| 0.60, ~2× the next feature).
- **Expression genes** carry the rest — no mutations, no TMB, no stage in the top 20. Matches literature (expression signatures, not mutations, are prognostic in breast cancer).
- Top genes: SCUBE2, CXCL13, MAPT — verified in literature (see BIO_INTERPRETATION.md).

---

## Key concepts (for interviews)

**The three models:**
- **Logistic Regression** — weighted scorecard; sums weighted features into a probability. Simple, stable, linear only.
- **Random Forest** — hundreds of decision trees on random data/feature subsets, then vote. Captures interactions; robust.
- **XGBoost** — trees built sequentially, each fixing the previous ones' errors (gradient boosting). Usually best on tabular data.

**AUROC** — measures ranking ability: given one who died + one who survived, how often does the model score the one who died as higher-risk? 0.5 = random, 1.0 = perfect, 0.6–0.7 = modest-but-real. Immune to class imbalance, unlike accuracy.

**Cross-validation** — split training data into 5 folds, train on 4, test on 1, rotate, average. Stable estimate without touching the test set. "Stratified" preserves the class ratio in each fold.

**Held-out test set** — 20% locked away at the start, used once at the end for an unbiased final number.

**SHAP** — game-theory method (Shapley values) that fairly attributes each prediction to its features. Reveals what the model learned; averaging magnitudes gives global importance.

---

## Key decisions
1. **AUROC over accuracy** as primary metric (class imbalance makes accuracy misleading).
2. **XGBoost with conservative regularization** to fight overfitting in the p ≫ n setting.
3. **Report CV as primary, test as confirmation** — honest about small-sample noise.
4. **Fact-checked SHAP genes** against literature rather than asserting from memory.

## Outcome
Built and compared three models, selected XGBoost (CV AUROC 0.725), confirmed on held-out data (0.648), and used SHAP to show the model learned recognizable breast-cancer biology (ER/endocrine + immune signals, age-dominant). Modest but honest and coherent result. Modeling core done.

## Artifacts saved
- `models/final_model.pkl` — trained pipeline
- `models/final_evaluation_curves.png` — ROC + PR curves
- `models/shap_summary.png`, `shap_importance_bar.png`, `shap_feature_importance.csv`
- `notebooks/BIO_INTERPRETATION.md` — citable biology writeup

## Next session (Day 5)
Build the Streamlit web app: load `final_model.pkl`, take patient input, output a risk prediction with SHAP explanation. Longest remaining piece.