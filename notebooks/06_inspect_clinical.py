import pandas as pd

proc = "../data/processed/"
cohort = pd.read_csv(proc + "cohort_labeled.csv")

# Candidate categorical clinical features to potentially encode
cat_cols = ["SEX", "RACE", "AJCC_PATHOLOGIC_TUMOR_STAGE",
            "PATH_T_STAGE", "PATH_N_STAGE", "PATH_M_STAGE", "RADIATION_THERAPY"]

for c in cat_cols:
    print("=" * 55)
    print(c)
    print("=" * 55)
    print(cohort[c].value_counts(dropna=False))
    print()