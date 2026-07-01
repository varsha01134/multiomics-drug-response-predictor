import pandas as pd

base = "../data/raw/brca_tcga_pan_can_atlas_2018/"

# --- Load the three core files ---
clin = pd.read_csv(base + "data_clinical_patient.txt", sep="\t", comment="#")
muts = pd.read_csv(base + "data_mutations.txt", sep="\t", comment="#")
expr = pd.read_csv(base + "data_mrna_seq_v2_rsem.txt", sep="\t")

# ============================================================
# 1. SURVIVAL TARGET — what are we working with?
# ============================================================
print("=" * 60)
print("SURVIVAL TARGET EXPLORATION")
print("=" * 60)

print("\nOS_STATUS value counts:")
print(clin["OS_STATUS"].value_counts(dropna=False))

print("\nOS_MONTHS summary:")
print(clin["OS_MONTHS"].describe())

# How many patients have BOTH a status and a months value (usable rows)?
usable = clin.dropna(subset=["OS_STATUS", "OS_MONTHS"])
print(f"\nPatients with usable OS data: {len(usable)} of {len(clin)}")

# ============================================================
# 2. PATIENT ID FORMATS — how is each file labeled?
# ============================================================
print("\n" + "=" * 60)
print("PATIENT / SAMPLE ID FORMATS")
print("=" * 60)

print("\nClinical PATIENT_ID (first 5):")
print(clin["PATIENT_ID"].head().tolist())

print("\nMutations Tumor_Sample_Barcode (first 5):")
print(muts["Tumor_Sample_Barcode"].head().tolist())

print("\nExpression — first 6 column names:")
print(expr.columns[:6].tolist())

print("\nExpression shape (genes x samples):", expr.shape)

# ============================================================
# 3. QUICK COUNTS
# ============================================================
print("\n" + "=" * 60)
print("COUNTS")
print("=" * 60)
print("Unique patients in clinical:", clin["PATIENT_ID"].nunique())
print("Unique samples in mutations:", muts["Tumor_Sample_Barcode"].nunique())
print("Expression sample columns (excl. gene cols):", expr.shape[1] - 2)