import pandas as pd

base = "../data/raw/brca_tcga_pan_can_atlas_2018/"
clin = pd.read_csv(base + "data_clinical_patient.txt", sep="\t", comment="#")
muts = pd.read_csv(base + "data_mutations.txt", sep="\t", comment="#")
expr = pd.read_csv(base + "data_mrna_seq_v2_rsem.txt", sep="\t")

print("Clinical:", clin.shape)
print("Mutations:", muts.shape)
print("Expression:", expr.shape)
print("\nClinical columns:\n", clin.columns.tolist())