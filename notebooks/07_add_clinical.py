import pandas as pd

proc = "../data/processed/"
df = pd.read_csv(proc + "model_dataset.csv")
cohort = pd.read_csv(proc + "cohort_labeled.csv")

c = cohort[["PATIENT_ID", "RACE", "AJCC_PATHOLOGIC_TUMOR_STAGE",
            "PATH_T_STAGE", "PATH_N_STAGE", "PATH_M_STAGE",
            "RADIATION_THERAPY"]].copy()

# --- Overall stage -> ordinal 1-4 (collapse sub-stages; X -> unknown) ---
def stage_num(s):
    if pd.isna(s):
        return pd.NA
    s = str(s)
    if "IV" in s:  return 4
    if "III" in s: return 3
    if "II" in s:  return 2
    if "I" in s:   return 1
    return pd.NA  # STAGE X

c["STAGE_NUM"] = c["AJCC_PATHOLOGIC_TUMOR_STAGE"].apply(stage_num)

# --- T / N / M -> ordinal from the digit (X -> NaN) ---
c["T_NUM"] = c["PATH_T_STAGE"].str.extract(r"T(\d)").astype(float)
c["N_NUM"] = c["PATH_N_STAGE"].str.extract(r"N(\d)").astype(float)
c["M_NUM"] = c["PATH_M_STAGE"].str.extract(r"M(\d)").astype(float)

# --- Radiation -> binary ---
c["RADIATION"] = c["RADIATION_THERAPY"].map({"Yes": 1, "No": 0})

# --- Race -> one-hot (missing -> all zeros) ---
race_d = pd.get_dummies(c["RACE"], prefix="RACE").astype(int)

# --- Assemble clinical block ---
num_cols = ["STAGE_NUM", "T_NUM", "N_NUM", "M_NUM", "RADIATION"]
clin_enc = pd.concat([c[["PATIENT_ID"] + num_cols], race_d], axis=1)

# --- Median-impute the ordinal/binary numerics ---
for col in num_cols:
    clin_enc[col] = pd.to_numeric(clin_enc[col], errors="coerce")
    clin_enc[col] = clin_enc[col].fillna(clin_enc[col].median())

# --- Merge onto model dataset (idempotent: drop first if re-run) ---
new_cols = [x for x in clin_enc.columns if x != "PATIENT_ID"]
df = df.drop(columns=[x for x in new_cols if x in df.columns], errors="ignore")
df = df.merge(clin_enc, on="PATIENT_ID", how="left")

print("Final dataset shape:", df.shape)
print("Added clinical features:", new_cols)
print("Total missing values:", int(df.isna().sum().sum()))
print("\nPreview of clinical columns:")
print(df[["PATIENT_ID", "AGE"] + num_cols + list(race_d.columns)].head())

df.to_csv(proc + "model_dataset.csv", index=False)
print(f"\nSaved -> {proc}model_dataset.csv")