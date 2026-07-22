import os
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (roc_auc_score, accuracy_score, precision_score,
                             recall_score, f1_score, confusion_matrix,
                             classification_report, roc_curve,
                             precision_recall_curve, average_precision_score)
from xgboost import XGBClassifier

proc = "../data/processed/"
df = pd.read_csv(proc + "model_dataset.csv")

y = df["SURV_5YR"]
X = df.drop(columns=["PATIENT_ID", "SURV_5YR"])
X["TMB"] = np.log1p(X["TMB"])

# --- SAME split as baselines (random_state=42) -> identical, untouched test set ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, stratify=y, random_state=42)

# --- Final model: XGBoost with the conservative small-data settings ---
spw = (y_train == 0).sum() / (y_train == 1).sum()
model = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.05,
                          subsample=0.8, colsample_bytree=0.8,
                          scale_pos_weight=spw, eval_metric="logloss",
                          random_state=42))
])

# --- Train on full training set, evaluate ONCE on the held-out test set ---
model.fit(X_train, y_train)
proba = model.predict_proba(X_test)[:, 1]
pred = model.predict(X_test)

print("=" * 55)
print("FINAL TEST-SET EVALUATION (65 patients, never seen)")
print("=" * 55)
print(f"AUROC:                  {roc_auc_score(y_test, proba):.3f}")
print(f"Avg Precision (PR-AUC): {average_precision_score(y_test, proba):.3f}")
print(f"Accuracy:               {accuracy_score(y_test, pred):.3f}")
print(f"Precision (died class): {precision_score(y_test, pred):.3f}")
print(f"Recall (died class):    {recall_score(y_test, pred):.3f}")
print(f"F1 (died class):        {f1_score(y_test, pred):.3f}")

print("\nConfusion matrix (rows=true, cols=pred):")
print(confusion_matrix(y_test, pred))
print("\nClassification report:")
print(classification_report(y_test, pred, target_names=["survived", "died <5yr"]))

# --- ROC + Precision-Recall curves ---
fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
fpr, tpr, _ = roc_curve(y_test, proba)
ax[0].plot(fpr, tpr, label=f"XGBoost (AUROC={roc_auc_score(y_test, proba):.3f})")
ax[0].plot([0, 1], [0, 1], "k--", alpha=0.5)
ax[0].set_xlabel("False Positive Rate"); ax[0].set_ylabel("True Positive Rate")
ax[0].set_title("ROC Curve"); ax[0].legend()

prec, rec, _ = precision_recall_curve(y_test, proba)
ax[1].plot(rec, prec, label=f"AP={average_precision_score(y_test, proba):.3f}")
ax[1].axhline(y_test.mean(), color="k", ls="--", alpha=0.5, label="baseline")
ax[1].set_xlabel("Recall"); ax[1].set_ylabel("Precision")
ax[1].set_title("Precision-Recall Curve"); ax[1].legend()
plt.tight_layout()

os.makedirs("../models", exist_ok=True)
plt.savefig("../models/final_evaluation_curves.png", dpi=120)
print("\nSaved curves -> ../models/final_evaluation_curves.png")

# --- Save the trained model for the web app ---
joblib.dump(model, "../models/final_model.pkl")
print("Saved model  -> ../models/final_model.pkl")