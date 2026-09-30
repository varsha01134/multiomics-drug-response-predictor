import streamlit as st
import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="Breast Cancer Survival Predictor", layout="wide")

# ------------------------------------------------------------
# Load data + model once (cached so it doesn't reload on every click)
# ------------------------------------------------------------
@st.cache_resource
def load_everything():
    df = pd.read_csv("data/processed/model_dataset.csv")
    y = df["SURV_5YR"]
    X = df.drop(columns=["PATIENT_ID", "SURV_5YR"])
    X["TMB"] = np.log1p(X["TMB"])
    ids = df["PATIENT_ID"]

    # Recreate the SAME split used in modeling (random_state=42)
    X_tr, X_te, y_tr, y_te, id_tr, id_te = train_test_split(
        X, y, ids, test_size=0.20, stratify=y, random_state=42)

    model = joblib.load("models/final_model.pkl")
    scaler = model.named_steps["scaler"]
    clf = model.named_steps["clf"]
    explainer = shap.TreeExplainer(clf)
    return X_te, y_te, id_te, model, scaler, clf, explainer, X.columns

X_te, y_te, id_te, model, scaler, clf, explainer, feat_names = load_everything()

# ------------------------------------------------------------
# Header
# ------------------------------------------------------------
st.title("🧬 Breast Cancer 5-Year Survival Predictor")
st.markdown(
    "A multi-omics machine learning model (XGBoost) that predicts 5-year "
    "survival from a tumor's molecular profile — genomics, transcriptomics, "
    "and clinical data — with SHAP explanations. "
    "*Research demo on TCGA-BRCA data; not for clinical use.*")

# ------------------------------------------------------------
# Patient picker (from held-out test set)
# ------------------------------------------------------------
st.sidebar.header("Select a patient")
patient_id = st.sidebar.selectbox("Test-set patient", id_te.tolist())

row_idx = id_te.tolist().index(patient_id)
patient_X = X_te.iloc[[row_idx]]
true_label = y_te.iloc[row_idx]

# ------------------------------------------------------------
# Prediction
# ------------------------------------------------------------
proba = model.predict_proba(patient_X)[0, 1]   # P(died within 5 yr)
pred = int(proba >= 0.5)

col1, col2, col3 = st.columns(3)
col1.metric("Predicted risk (died < 5yr)", f"{proba:.0%}")
col2.metric("Model prediction",
            "High risk" if pred == 1 else "Likely survives")
col3.metric("Actual outcome",
            "Died < 5yr" if true_label == 1 else "Survived 5yr+")

if pred == true_label:
    st.success("✓ Model prediction matches the actual outcome for this patient.")
else:
    st.warning("✗ Model prediction does not match the actual outcome here.")

st.divider()

# ------------------------------------------------------------
# SHAP explanation for THIS patient
# ------------------------------------------------------------
st.subheader("Why? Top features driving this prediction")

patient_scaled = pd.DataFrame(
    scaler.transform(patient_X), columns=feat_names)
shap_vals = explainer.shap_values(patient_scaled)[0]

contrib = (pd.DataFrame({"feature": feat_names, "shap": shap_vals})
           .assign(abs=lambda d: d["shap"].abs())
           .sort_values("abs", ascending=False)
           .head(12))

fig, ax = plt.subplots(figsize=(8, 5))
colors = ["#d62728" if v > 0 else "#1f77b4" for v in contrib["shap"]]
ax.barh(contrib["feature"][::-1], contrib["shap"][::-1], color=colors[::-1])
ax.set_xlabel("SHAP value  (red = pushes toward death, blue = toward survival)")
ax.axvline(0, color="black", linewidth=0.8)
st.pyplot(fig)

st.caption(
    "Red bars pushed this patient's prediction toward 'died within 5 years'; "
    "blue bars pushed toward survival. Longer bars = stronger influence.")

# ------------------------------------------------------------
# Model performance context
# ------------------------------------------------------------
with st.expander("About this model & its performance"):
    st.markdown(
        "- **Model:** XGBoost on 540 features (age, 500 expression genes, "
        "31 mutation features, 8 clinical).\n"
        "- **Cross-validated AUROC:** 0.725; **held-out test AUROC:** 0.648.\n"
        "- **Interpretation:** modest but real prognostic signal. Predicting "
        "5-year survival from molecular data is genuinely hard; this is a "
        "proof-of-concept, not a clinical tool.\n"
        "- **Cohort:** 324 TCGA-BRCA patients with complete multi-omics data.")