import pandas as pd

proc = "../data/processed/"

# --- Load the label/clinical table and both feature matrices ---
cohort = pd.read_csv(proc + "cohort_labeled.csv")
mut = pd.read_csv(proc + "features_mutations.csv")
expr = pd.read_csv(proc + "features_expression.csv")

# --- Label + AGE (numeric clinical feature), keyed by PATIENT_ID ---
clin = cohort[["PATIENT_ID", "SURV_5YR", "AGE"]].copy()
clin["AGE"] = pd.to_numeric(clin["AGE"], errors="coerce")
clin["AGE"] = clin["AGE"].fillna(clin["AGE"].median())

# --- Merge everything on PATIENT_ID ---
df = (clin
      .merge(mut, on="PATIENT_ID", how="inner")
      .merge(expr, on="PATIENT_ID", how="inner"))

print("Merged model dataset shape:", df.shape)
print("\nLabel balance:")
print(df["SURV_5YR"].value_counts())

# --- Sanity checks ---
print("\nTotal missing values in table:", int(df.isna().sum().sum()))

n_mut = len([c for c in df.columns if c.startswith("mut_")]) + 1   # +TMB
n_expr = len([c for c in df.columns if c.startswith("expr_")])
print(f"\nFeature breakdown: 1 age + {n_mut} mutation + {n_expr} expression "
      f"= {df.shape[1] - 2} total features")

# --- Save the model-ready dataset ---
df.to_csv(proc + "model_dataset.csv", index=False)
print(f"\nSaved -> {proc}model_dataset.csv")