import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

proc = "../data/processed/"
df = pd.read_csv(proc + "model_dataset.csv")

# --- Features / label ---
y = df["SURV_5YR"]
X = df.drop(columns=["PATIENT_ID", "SURV_5YR"])

# --- Tame the skewed TMB feature (log scale) ---
X["TMB"] = np.log1p(X["TMB"])

print("X shape:", X.shape, "| Positives (died <5yr):", int(y.sum()), "/", len(y))

# --- Hold out a stratified 20% test set (untouched until final eval) ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, stratify=y, random_state=42)
print("Train patients:", X_train.shape[0], "| Test patients:", X_test.shape[0])

# --- 5-fold stratified cross-validation ---
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

def evaluate(name, model):
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", model)])
    auroc = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="roc_auc")
    acc = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="accuracy")
    print(f"\n{name}")
    print(f"  CV AUROC:    {auroc.mean():.3f} +/- {auroc.std():.3f}")
    print(f"  CV Accuracy: {acc.mean():.3f} +/- {acc.std():.3f}")

# --- Baseline 1: Logistic Regression ---
evaluate("Logistic Regression (L2, balanced)",
         LogisticRegression(max_iter=2000, class_weight="balanced"))

# --- Baseline 2: Random Forest ---
evaluate("Random Forest (balanced)",
         RandomForestClassifier(n_estimators=300, class_weight="balanced",
                                random_state=42))

# --- Reference point: naive "always predict majority" ---
naive_acc = max(y_train.mean(), 1 - y_train.mean())
print(f"\nNaive baseline (always predict 'survived') accuracy: {naive_acc:.3f}")
print("AUROC of 0.5 = random. A useful model must beat that.")
from xgboost import XGBClassifier

# --- Baseline 3: XGBoost ---
# scale_pos_weight handles the class imbalance (neg/pos ratio)
spw = (y_train == 0).sum() / (y_train == 1).sum()
evaluate("XGBoost (tuned for small data)",
         XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.05,
                       subsample=0.8, colsample_bytree=0.8,
                       scale_pos_weight=spw, eval_metric="logloss",
                       random_state=42))