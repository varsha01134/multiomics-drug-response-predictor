import pandas as pd

base = "../data/raw/brca_tcga_pan_can_atlas_2018/"

clin = pd.read_csv(base + "data_clinical_patient.txt", sep="\t", comment="#")
muts = pd.read_csv(base + "data_mutations.txt", sep="\t", comment="#", low_memory=False)
expr = pd.read_csv(base + "data_mrna_seq_v2_rsem.txt", sep="\t")

# ============================================================
# Binary event indicator from OS_STATUS
# "1:DECEASED" -> 1, "0:LIVING" -> 0
# ============================================================
clin["OS_EVENT"] = clin["OS_STATUS"].str.startswith("1").astype(int)

# ---- OPTION A: vital status, all patients ----
print("=" * 60)
print("OPTION A - Vital status (deceased vs living), ALL patients")
print("=" * 60)
print(clin["OS_EVENT"].value_counts())
print(f"Total: {len(clin)}  |  Positive (deceased): {clin['OS_EVENT'].mean():.1%}")

# ---- OPTION B: 5-year survival, censoring-aware ----
CUTOFF = 60  # months = 5 years

def make_label(r):
    if r["OS_EVENT"] == 1 and r["OS_MONTHS"] < CUTOFF:
        return 1          # died within 5 years  -> poor outcome
    elif r["OS_MONTHS"] >= CUTOFF:
        return 0          # followed past 5 years -> good outcome
    else:
        return pd.NA      # alive but <5yr follow-up -> unknown (censored)

clin["SURV_5YR"] = clin.apply(make_label, axis=1)
labeled = clin.dropna(subset=["SURV_5YR"]).copy()
labeled["SURV_5YR"] = labeled["SURV_5YR"].astype(int)

print("\n" + "=" * 60)
print("OPTION B - 5-year survival (censored patients excluded)")
print("=" * 60)
print(labeled["SURV_5YR"].value_counts())
print(f"Usable: {len(labeled)} of {len(clin)}  |  Excluded as censored: {len(clin) - len(labeled)}")

# ============================================================
# Patient-ID matching across all three files (first 12 chars)
# ============================================================
clin_ids = set(clin["PATIENT_ID"])
mut_ids = set(muts["Tumor_Sample_Barcode"].str[:12])
expr_cols = pd.Series([c for c in expr.columns if c.startswith("TCGA")])
expr_ids = set(expr_cols.str[:12])

print("\n" + "=" * 60)
print("DATA AVAILABILITY (patient overlap)")
print("=" * 60)
print("Clinical patients:      ", len(clin_ids))
print("Mutation patients:      ", len(mut_ids))
print("Expression patients:    ", len(expr_ids))
print("In ALL THREE files:     ", len(clin_ids & mut_ids & expr_ids))
print("All three + labeled (B):", len(set(labeled["PATIENT_ID"]) & mut_ids & expr_ids))

# ============================================================
# Build and save the analysis cohort (Option B + all 3 data types)
# ============================================================
import os

common = clin_ids & mut_ids & expr_ids
cohort = labeled[labeled["PATIENT_ID"].isin(common)].copy()

# Keep the label plus useful clinical features (only those that exist)
keep_cols = ["PATIENT_ID", "SURV_5YR", "OS_STATUS", "OS_MONTHS", "OS_EVENT",
             "AGE", "SEX", "RACE", "AJCC_PATHOLOGIC_TUMOR_STAGE",
             "PATH_T_STAGE", "PATH_N_STAGE", "PATH_M_STAGE", "RADIATION_THERAPY"]
keep_cols = [c for c in keep_cols if c in cohort.columns]
cohort = cohort[keep_cols]

os.makedirs("../data/processed", exist_ok=True)
cohort.to_csv("../data/processed/cohort_labeled.csv", index=False)

print("\n" + "=" * 60)
print("SAVED ANALYSIS COHORT")
print("=" * 60)
print(f"Patients: {len(cohort)}  ->  data/processed/cohort_labeled.csv")
print("Columns saved:", cohort.columns.tolist())
print("\nLabel balance in final cohort:")
print(cohort["SURV_5YR"].value_counts())