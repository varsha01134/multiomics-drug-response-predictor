# Biological Interpretation of Model Features (SHAP)

**Project:** Multi-Omics Integration Platform for Cancer Drug Response Prediction
**Analysis:** SHAP feature importance on the final XGBoost survival model (TCGA-BRCA, 324 patients)

---

## Summary finding

The features driving 5-year survival predictions form a coherent, literature-supported breast-cancer prognosis story with three themes:

1. **Age dominates** (mean |SHAP| = 0.60, roughly double the next feature) — expected, since age is a strong prognostic factor for overall survival across cancers.
2. **Expression carries the molecular signal, not mutations** — no mutation flags, TMB, or tumor-stage variables appear in the top 20. This matches the literature: in breast cancer, expression signatures (e.g., Oncotype DX, MammaPrint) are prognostic, whereas individual mutations largely are not for overall survival.
3. **The top genes reflect ER/endocrine biology and immune infiltration** — two of the best-established prognostic axes in breast cancer.

---

## Top genes verified against the literature

### SCUBE2 (`expr_SCUBE2`)
One of the 16 cancer-related genes in the commercial **Oncotype DX 21-gene Recurrence Score**, in the estrogen-signaling / hormone group. The model independently surfacing a clinically validated prognostic gene is a strong sanity check.
- Ref: Oncotype DX gene composition — PMC8236154; PMC11538975

### CXCL13 (`expr_CXCL13`)
A B-cell-attracting chemokine and marker of immune infiltration. Elevated CXCL13 is generally associated with **improved overall survival** in breast cancer (validated in TCGA and independent cohorts), though its role is context-dependent — CXCL13–CXCR5 co-expression has also been linked to lymph node metastasis in some studies.
- Refs: PMC8017297 (favorable OS, TCGA-validated); PMC8982548 (context/LNM nuance)

### MAPT / tau (`expr_MAPT`)
An estrogen-regulated gene (its promoter contains an ER response element) linked to **better outcomes in ER-positive breast cancer** and to endocrine sensitivity. Positive correlation with survival has held in multivariate analysis.
- Refs: PMC10511431 (positive survival correlation, multivariate); bcr2598 / PMC2917038 (ER regulation)

### Other top genes (not yet individually verified)
GFRA1, TMPRSS4, SCUBE2's neighbors, and several tubulin genes (TUBA3D/TUBA3E) appear in the list. GFRA1 is reportedly ER-associated and TMPRSS4 is linked to tumor progression in several cancers, **but verify each against a primary source before citing.** Some (e.g., tubulin family) may reflect technical/proliferation variance rather than specific prognostic biology.

---

## Honesty caveats (state these in the write-up)

1. **Exact gene ranking is unstable.** With 324 patients and modest AUROC (CV ≈ 0.73, test ≈ 0.65), a different train split could reorder the list. The **robust findings are the themes** (age dominates; expression > mutations; ER + immune signals), not any single gene's rank.
2. **Feature selection preceded the split.** The top-500 variance filter was computed on the full cohort. It is unsupervised (never sees the label), so leakage is minimal, but this can make CV estimates slightly optimistic — a plausible partial explanation for the CV-vs-test gap.
3. **SHAP shows association, not causation.** These features help the model discriminate; they are not claimed to be causal drivers of survival.

---

## One-paragraph version (for slides / README)

> SHAP analysis showed the model's predictions were driven most strongly by patient age, followed by gene-expression features rather than mutations or tumor stage — consistent with the clinical reality that expression signatures (not individual mutations) are prognostic in breast cancer. The top genes reflected two established prognostic axes: ER/endocrine biology (SCUBE2, an Oncotype DX gene; MAPT, an estrogen-regulated gene) and immune infiltration (CXCL13). This indicates the model learned recognizable breast-cancer biology rather than noise, though with a modest-size cohort the specific gene ranking should be read as thematic rather than exact.