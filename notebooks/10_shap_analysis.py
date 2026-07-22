import os
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import shap
from sklearn.model_selection import train_test_split

proc = "../data/processed/"
df = pd.read_csv(proc + "model_dataset.csv")

y = df["SURV_5YR"]
X = df.drop(columns=["PATIENT_ID", "SURV_5YR"])
X["TMB"] = np.log1p(X["TMB"])

# --- Load the trained pipeline, split out scaler + model ---
model = joblib.load("../models/final_model.pkl")
scaler = model.named_steps["scaler"]
clf = model.named_steps["clf"]

# --- Scale all patients (SHAP explains the model's actual inputs) ---
X_scaled = pd.DataFrame(scaler.transform(X), columns=X.columns, index=X.index)

# --- SHAP values via TreeExplainer (fast + exact for tree models) ---
explainer = shap.TreeExplainer(clf)
shap_values = explainer.shap_values(X_scaled)

# --- Global importance = mean absolute SHAP per feature ---
importance = (pd.DataFrame({
    "feature": X.columns,
    "mean_abs_shap": np.abs(shap_values).mean(axis=0)})
    .sort_values("mean_abs_shap", ascending=False)
    .reset_index(drop=True))

print("Top 20 features driving survival predictions:")
print(importance.head(20).to_string(index=False))

os.makedirs("../models", exist_ok=True)
importance.to_csv("../models/shap_feature_importance.csv", index=False)

# --- Beeswarm summary plot (importance + direction) ---
shap.summary_plot(shap_values, X_scaled, max_display=20, show=False)
plt.tight_layout()
plt.savefig("../models/shap_summary.png", dpi=120, bbox_inches="tight")
plt.close()

# --- Bar plot (clean ranking) ---
shap.summary_plot(shap_values, X_scaled, plot_type="bar", max_display=20, show=False)
plt.tight_layout()
plt.savefig("../models/shap_importance_bar.png", dpi=120, bbox_inches="tight")
plt.close()

print("\nSaved -> shap_summary.png, shap_importance_bar.png, shap_feature_importance.csv")