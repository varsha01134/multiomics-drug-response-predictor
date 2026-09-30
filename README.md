# 🧬 Breast Cancer 5-Year Survival Predictor

A multi-omics machine learning pipeline that predicts 5-year survival in breast cancer patients using genomic, transcriptomic, and clinical data from TCGA-BRCA, with an interactive web app for exploring predictions and their biological drivers.

**🔗 Live demo:** https://multiomics-drug-response-predictor-5yaj8nkkhpn6ekm7btay9k.streamlit.app/

---

## Problem

Predicting patient outcomes from molecular data is a core challenge in precision oncology — no single data type (genomics, gene expression, or clinical variables alone) tells the whole story. This project integrates all three to predict 5-year survival, and uses SHAP to explain *why* the model makes each prediction, so results are interpretable rather than a black box.

## How it works
TCGA-BRCA raw data (mutations, expression, clinical)
↓
Feature engineering & integration (324 patients, 540 features)
↓
Model comparison: Logistic Regression, Random Forest, XGBoost
↓
XGBoost selected (best cross-validated performance)
↓
SHAP interpretability analysis
↓
Streamlit web app (patient picker → prediction → explanation)


## Results

| Model | Cross-validated AUROC |
|---|---|
| Logistic Regression | 0.676 |
| Random Forest | 0.691 |
| **XGBoost (selected)** | **0.725** |

- **Held-out test set AUROC:** 0.648 (65 unseen patients)
- **Top predictive features (via SHAP):** patient age, and expression of *CXCL13*, *MAPT*, and other genes — consistent with established breast cancer biology (hormone and immune-related signaling), not just noise the model happened to fit.

**Honest limitation:** on the held-out test set, the model correctly identified only 6 of 18 patients who died within 5 years. This is a research proof-of-concept demonstrating a multi-omics integration and interpretability pipeline — **not a validated clinical tool.**

## Tech stack

- **Data processing:** pandas, numpy
- **Modeling:** scikit-learn, XGBoost
- **Interpretability:** SHAP
- **Web app:** Streamlit
- **Data source:** TCGA-BRCA (The Cancer Genome Atlas, Breast Invasive Carcinoma)

## Running it locally

```bash
git clone https://github.com/varsha01134/multiomics-drug-response-predictor.git
cd multiomics-drug-response-predictor
pip install -r requirements.txt
streamlit run app/app.py
```

## Project structure
├── app/ # Streamlit web application
├── data/processed/ # Engineered feature datasets
├── models/ # Trained model + evaluation artifacts
├── notebooks/ # Data prep, modeling, and SHAP analysis notebooks
└── requirements.txt


## Author

Varsha Raghavendra — MS Bioinformatics, Northeastern University
