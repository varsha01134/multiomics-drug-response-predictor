# Day 3 Log — Feature Engineering

**Project:** Multi-Omics Integration Platform for Cancer Drug Response Prediction
**Date:** July 1, 2026
**Phase:** 1 — Data Acquisition & Integration (feature engineering)
**Status:** ✅ Complete

---

## Goal for the day
Turn the three raw data files into a single clean, numeric, model-ready table for the 324-patient cohort — combining genomics (mutations), transcriptomics (expression), and clinical data. Central challenge: ~20,500 features vs 324 patients (p ≫ n), so feature reduction was essential.

---

## What was done

### 1. Mutation features (`03_features_mutations.py`)
- **TMB (Tumor Mutation Burden):** total mutations per patient.
- **Top 30 mutated genes:** binary 1/0 flag per patient per gene.
- **Sanity check passed:** top genes were TP53, PIK3CA, GATA3, CDH1, PTEN, MAP3K1 — known breast cancer drivers. Long "passenger" genes (TTN, MUC16) also appeared, as expected.
- Output: 324 × 31 → `features_mutations.csv`
- Note: TMB is heavily right-skewed (one hypermutator at 824); to be log-transformed during scaling.

### 2. Expression features (`04_features_expression.py`)
- Cleaned the ~20,500-gene file (dropped Entrez col, dropped missing symbols, collapsed duplicate gene symbols by averaging → 20,511 unique genes).
- Transposed to patients × genes, restricted to cohort.
- **Log2(x+1) transform** to tame skew.
- **Selected top 500 most-variable genes** (unsupervised — never looks at the label, so no data leakage).
- **Sanity check passed:** most-variable genes were breast/hormone markers (SCGB2A2/mammaglobin, PIP, TFF1, S100A7).
- Output: 324 × 500 → `features_expression.csv`

### 3. Merge (`05_merge_features.py`)
- Joined label + age + mutation + expression on PATIENT_ID.
- Result: 324 × 534, **0 missing values** → `model_dataset.csv`

### 4. Inspect clinical fields (`06_inspect_clinical.py`)
- Printed value counts for categorical clinical columns before encoding (look-before-encoding).
- Revealed sub-stages (IIA/IIB…), "X"/unassessable codes, and missing values to handle.

### 5. Encode & add clinical (`07_add_clinical.py`)
- **SEX:** dropped (321/324 female → no signal).
- **RACE:** one-hot (White / Black / Asian); missing → all zeros.
- **Overall stage:** ordinal 1–4 (sub-stages collapsed); "STAGE X"/missing → median-imputed.
- **T / N / M stages:** ordinal from the digit; "X" → median-imputed.
- **RADIATION_THERAPY:** binary Yes/No → 1/0; 40 missing (~12%) → median-imputed.
- Merged onto the model dataset (idempotent — safe to re-run).
- Result: 324 × 542, **0 missing values** → `model_dataset.csv`

---

## Results

| Item | Result |
|---|---|
| Final dataset | 324 patients × 542 features |
| Missing values | 0 |
| Label balance | 236 survived / 88 did not (~27% positive) |
| Mutation features | 31 (TMB + 30 gene flags) |
| Expression features | 500 (top-variable, from ~20,500) |
| Clinical features | 9 (age, stage, T/N/M, radiation, 3 race columns) |
| Scripts written | 5 (`03`–`07`) |

**Final dataset file:** `data/processed/model_dataset.csv`

---

## Key decisions
1. **Unsupervised feature selection** (top-variance genes) to fight p ≫ n without leaking the label.
2. **Ordinal encoding** for tumor stage — preserves natural order compactly (vs one-hot).
3. **Median imputation** for missing stage / radiation values (alternative: explicit "unknown" flag).
4. **Dropped SEX** — no discriminative power in a near-all-female cohort.

## Caveat to carry forward
Even after reduction, 542 features vs 324 patients means overfitting risk remains. Watch for a large train/test gap in modeling; if it appears, dial expression genes down from 500 to ~200.

## Outcome
Built a complete, five-script feature-engineering pipeline and produced a fully integrated, model-ready dataset combining genomics + transcriptomics + clinical data, with all biological sanity checks passing. Heaviest phase of the project — done.

## Next session (Day 4)
Modeling — Phase 2 begins:
- Train/validation/test split (stratified on the label)
- First baseline model (logistic regression), then Random Forest
- Baseline metrics: accuracy, AUROC, precision/recall — see how well molecular data predicts 5-year survival