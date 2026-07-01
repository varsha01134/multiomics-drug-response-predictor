# Day 2 Log — Survival Target & Cohort Construction

**Project:** Multi-Omics Integration Platform for Cancer Drug Response Prediction
**Date:** July 1, 2026
**Phase:** 1 — Data Acquisition & Integration
**Status:** ✅ Complete

---

## Goal for the day
Turn the raw data files into a clean, labeled, model-ready patient cohort: define the prediction target, build the label, and solve patient-ID matching across the three files.

---

## What was done

### 1. Explored the survival target (`01_explore_and_target.py`)
Ran an exploration script before building anything, to confirm exact field formats (guessing causes bugs). Findings:
- **`OS_STATUS`** is formatted as `0:LIVING` / `1:DECEASED` → convert to 0/1 by checking if the string starts with "1".
- **`OS_MONTHS`** (follow-up time) ranges 0–283 months, median ~27 → many patients have short follow-up (relevant for censoring).
- **ID formats differ across files:** clinical is patient-level (`TCGA-3C-AAAU`, 12 chars); mutations and expression are sample-level with a `-01` suffix (`TCGA-3C-AAAU-01`). Shared key = first 12 characters.

### 2. Compared two target definitions (`02_build_target.py`)

| Option | Definition | Tradeoff |
|---|---|---|
| **A** | Vital status (deceased vs living) | Uses all patients, but only 13.9% positive and ignores *time* of death |
| **B** | 5-year survival (survived past 60 months vs died within) | More meaningful + better balance, but requires excluding censored patients (alive with <5yr follow-up) |

### 3. Chose Option B
- Left 348 labeled patients with better class balance (~28% positive) than Option A (14%).
- Handling right-censoring correctly (excluding patients without adequate follow-up rather than mislabeling them) is a defensible, interview-worthy methodological choice.

### 4. Solved patient-ID matching
- Trimmed sample IDs to the 12-character patient key.
- Intersected all three files to find patients with clinical **and** mutation **and** expression data.
- This is the core (and trickiest) multi-omics integration step.

### 5. Built and saved the final cohort
- Filtered to patients with both a clean Option B label **and** all three data types.
- Saved to `data/processed/cohort_labeled.csv` with clinical features attached.

### 6. Committed and pushed
- Both scripts (`01_explore_and_target.py`, `02_build_target.py`) pushed to GitHub.

---

## Results

| Metric | Result |
|---|---|
| Total patients in dataset | 1,084 |
| Deceased (all patients) | 151 (13.9%) |
| Labeled under Option B | 348 (249 survivors / 99 non-survivors) |
| Excluded as censored | 736 |
| Patients with all 3 data types | 1,007 |
| **Final cohort (labeled + all 3 data types)** | **324** |
| **Final label balance** | **236 survivors / 88 non-survivors (~27%)** |
| Clinical features retained | AGE, SEX, RACE, AJCC tumor stage, PATH T/N/M stage, radiation therapy |

**Target chosen:** `SURV_5YR` — binary 5-year overall survival (0 = survived past 60 months, 1 = died within 60 months).

---

## Key decisions
1. **Target = Option B (5-year survival, censoring-aware)** over vital status — better balance and stronger methodology.
2. **Patient key = first 12 characters** of the TCGA barcode, to reconcile patient-level vs sample-level IDs.

## Caveat to carry forward
324 patients vs ~20,500 expression genes = severe p ≫ n problem. Feature engineering (next phase) must aggressively reduce feature count (top-variance genes, pathway scores) to prevent overfitting.

## Outcome
Defined a defensible prediction target, solved patient-ID matching across three files, and produced a clean 324-patient labeled cohort — the foundation everything else builds on.

## Next session (Day 3)
Feature engineering — build the numeric feature matrix for the 324 patients:
- Mutations → tumor mutation burden + binary features for top mutated genes
- Expression → log-transform, reduce to most-variable genes
- Assemble the model-ready feature table joined to the labels