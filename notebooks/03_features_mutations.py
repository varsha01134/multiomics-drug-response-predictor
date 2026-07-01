import pandas as pd

base = "../data/raw/brca_tcga_pan_can_atlas_2018/"
proc = "../data/processed/"

# --- Load our 324-patient cohort and the mutations file ---
cohort = pd.read_csv(proc + "cohort_labeled.csv")
muts = pd.read_csv(base + "data_mutations.txt", sep="\t", comment="#", low_memory=False)

cohort_ids = set(cohort["PATIENT_ID"])

# --- Make a patient key and keep only our cohort's mutations ---
muts["PATIENT_ID"] = muts["Tumor_Sample_Barcode"].str[:12]
muts = muts[muts["PATIENT_ID"].isin(cohort_ids)]
print("Mutation rows for cohort patients:", len(muts))
print("Cohort patients with >=1 mutation:", muts["PATIENT_ID"].nunique())

# ============================================================
# Feature 1: Tumor Mutation Burden (total mutations per patient)
# ============================================================
tmb = muts.groupby("PATIENT_ID").size().rename("TMB")

# ============================================================
# Feature 2: Binary flags for the top mutated genes
# ============================================================
TOP_N = 30
top_genes = muts["Hugo_Symbol"].value_counts().head(TOP_N).index.tolist()
print(f"\nTop {TOP_N} mutated genes in cohort:")
print(top_genes)

# 1 if patient has any mutation in that gene, else 0
mut_flags = (
    muts[muts["Hugo_Symbol"].isin(top_genes)]
    .assign(val=1)
    .pivot_table(index="PATIENT_ID", columns="Hugo_Symbol",
                 values="val", aggfunc="max", fill_value=0)
)
mut_flags.columns = [f"mut_{g}" for g in mut_flags.columns]

# ============================================================
# Combine and align to the full cohort
# ============================================================
mut_features = pd.concat([tmb, mut_flags], axis=1)
mut_features = mut_features.reindex(sorted(cohort_ids)).fillna(0)
mut_features["TMB"] = mut_features["TMB"].astype(int)
mut_features.index.name = "PATIENT_ID"

print("\nMutation feature matrix shape:", mut_features.shape)
print("\nFirst few rows:")
print(mut_features.head())

mut_features.to_csv(proc + "features_mutations.csv")
print(f"\nSaved -> {proc}features_mutations.csv")