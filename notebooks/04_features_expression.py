import pandas as pd
import numpy as np

base = "../data/raw/brca_tcga_pan_can_atlas_2018/"
proc = "../data/processed/"

cohort = pd.read_csv(proc + "cohort_labeled.csv")
cohort_ids = set(cohort["PATIENT_ID"])

# --- Load expression (genes x samples), this file is large ---
print("Loading expression file (may take a moment)...")
expr = pd.read_csv(base + "data_mrna_seq_v2_rsem.txt", sep="\t")
print("Raw expression shape (genes x cols):", expr.shape)

# --- Clean gene index: drop Entrez col, drop missing symbols,
#     collapse duplicate gene symbols by averaging ---
expr = expr.drop(columns=["Entrez_Gene_Id"])
expr = expr.dropna(subset=["Hugo_Symbol"])
expr = expr.groupby("Hugo_Symbol").mean()
print("After cleaning (unique genes x samples):", expr.shape)

# --- Transpose to samples x genes, make patient key ---
expr_t = expr.T
expr_t.index = expr_t.index.str[:12]              # sample -> patient ID
expr_t = expr_t.groupby(level=0).mean()           # collapse dup samples/patient

# --- Keep only our cohort ---
expr_t = expr_t.loc[expr_t.index.isin(cohort_ids)]
print("Expression restricted to cohort:", expr_t.shape)

# --- Log-transform (expression is heavily skewed) ---
expr_log = np.log2(expr_t + 1)

# --- Feature selection: top 500 most-variable genes (unsupervised) ---
TOP_GENES = 500
variances = expr_log.var(axis=0).sort_values(ascending=False)
top = variances.head(TOP_GENES).index
expr_features = expr_log[top].copy()
expr_features.columns = [f"expr_{g}" for g in expr_features.columns]
expr_features.index.name = "PATIENT_ID"

print(f"\nSelected top {TOP_GENES} variable genes.")
print("Expression feature matrix shape:", expr_features.shape)
print("\nMost-variable genes (first 10):")
print(list(top[:10]))

expr_features.to_csv(proc + "features_expression.csv")
print(f"\nSaved -> {proc}features_expression.csv")