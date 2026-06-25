# Day 1 Log — Project Setup & Data Acquisition

**Project:** Multi-Omics Integration Platform for Cancer Drug Response Prediction
**Date:** June 25, 2026
**Phase:** 1 — Data Acquisition & Integration
**Status:** ✅ Complete

---

## Goal for the day
Go from an empty repository to a fully configured, version-controlled project with a reproducible Python environment and the TCGA-BRCA multi-omics dataset downloaded and verified.

---

## What was done

### 1. Git configuration
- Confirmed Git installed (`git version 2.50.0.windows.2`).
- Set global identity (`user.name`, `user.email`) so all commits are attributed correctly.
- *One-time machine setup; not repeated.*

### 2. Repository creation
- Created GitHub repo `multiomics-drug-response-predictor` with README, Python `.gitignore`, and license.
- Cloned locally to `C:\Users\varsh\Downloads\`.
- This repo is the project's home base and the eventual portfolio artifact.

### 3. Folder structure
Created the following directories for clean separation of concerns:

| Folder | Purpose |
|---|---|
| `data/raw` | Untouched source data |
| `data/processed` | Cleaned / engineered data |
| `notebooks` | Exploration and analysis |
| `src` | Reusable code modules |
| `models` | Trained model files |
| `app` | Web application |

### 4. Virtual environment
- Created an isolated environment: `python -m venv omics_env`.
- Activated it (prompt shows `(omics_env)` when active).
- Fixed PowerShell script-blocking with `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.

### 5. `.gitignore` setup
- Added `omics_env/` and `data/raw/` so the venv and large raw data are never pushed to GitHub.
- Verified later: final push was only **727 bytes**, confirming data stayed local.

### 6. Package installation
Installed the core stack:

| Package(s) | Role |
|---|---|
| pandas, numpy | Data handling |
| scikit-learn, xgboost | Machine learning |
| shap | Model explainability |
| matplotlib, seaborn, plotly | Visualization |
| gseapy | Pathway enrichment analysis |
| jupyter | Notebooks |
| requests | HTTP / data fetching |

- Snapshotted exact versions with `pip freeze > requirements.txt` for reproducibility.
- **Issue encountered:** install crashed on Windows' 260-character path limit (jupyter's deeply nested files).
- **Fix:** enabled long-path support via registry (`LongPathsEnabled = 1`, as admin), then re-ran the install successfully.
- Confirmed versions: pandas 3.0.3, scikit-learn 1.9.0, xgboost 3.3.0, shap 0.52.0, gseapy 1.3.0.

### 7. Data download
- Source: **cBioPortal** — "Breast Invasive Carcinoma (TCGA, PanCancer Atlas)".
- Size: 509 MB `.tar.gz` archive.
- Extracted with `tar -xzf <file> -C data\raw`.
- **Decision:** chose cBioPortal over TCGAbiolinks because TCGAbiolinks is an R package and wouldn't fit the Python workflow; cBioPortal provides clean, pre-merged, tab-delimited files that pandas reads directly.
- Archive included more than expected: beyond the four core files, also methylation, protein/RPPA, and phosphoprotein data (available as stretch-goal layers later).

**Core files in use:**
- `data_clinical_patient.txt` — clinical + survival data
- `data_mutations.txt` — somatic mutations
- `data_mrna_seq_v2_rsem.txt` — RNA-seq expression
- `data_cna.txt` — copy number (optional 3rd omics layer)

### 8. Data load verification
Wrote and ran `notebooks/00_load_check.py`:

```python
import pandas as pd

base = "../data/raw/brca_tcga_pan_can_atlas_2018/"
clin = pd.read_csv(base + "data_clinical_patient.txt", sep="\t", comment="#")
muts = pd.read_csv(base + "data_mutations.txt", sep="\t", comment="#")
expr = pd.read_csv(base + "data_mrna_seq_v2_rsem.txt", sep="\t")

print("Clinical:", clin.shape)
print("Mutations:", muts.shape)
print("Expression:", expr.shape)
print("\nClinical columns:\n", clin.columns.tolist())
```

Key parsing details:
- `sep="\t"` — files are tab-separated.
- `comment="#"` — cBioPortal files have `#`-prefixed metadata header rows that would otherwise break parsing.

All three datasets loaded without errors.

### 9. Target variable identified
The clinical columns revealed no clean drug-response field, but four well-populated survival endpoints (each with a status + months pair):

- **OS** — Overall Survival (`OS_STATUS`, `OS_MONTHS`)
- **DSS** — Disease-Specific Survival
- **DFS** — Disease-Free Survival
- **PFS** — Progression-Free Survival (`PFS_STATUS`, `PFS_MONTHS`)

**Decision:** target = **Overall Survival (OS)**, framed as binary classification (survived past a cutoff vs. not), compatible with the planned Random Forest / XGBoost / SHAP pipeline.

Candidate clinical input features spotted: `AGE`, `RACE`, `PATH_T_STAGE`, `PATH_N_STAGE`, `PATH_M_STAGE`, `RADIATION_THERAPY`, tumor status.

### 10. Commit & push
```powershell
git add .
git commit -m "Day 1: setup, data download, load check"
git push
```
Push succeeded (`main -> main`, 727 bytes), confirming `.gitignore` correctly excluded the data.

---

## Obstacles cleared
1. **PowerShell execution policy** blocked venv activation → fixed with `RemoteSigned` scope.
2. **Windows 260-char path limit** broke the install → fixed by enabling long-path support in registry.

## Outcome
Went from an empty folder to a fully configured, version-controlled project with a reproducible environment and 509 MB of verified multi-omics cancer data — and locked in the prediction target (patient overall survival).

## Next session (June 29)
- Build the binary survival target from `OS_STATUS` / `OS_MONTHS`.
- Handle patient-ID matching across the omics files.
- First real exploratory data analysis (EDA).