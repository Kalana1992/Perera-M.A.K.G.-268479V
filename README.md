# E-Commerce Business Intelligence and Decision Support System (BI-DSS)

CS5998 Capstone Project – Master of Data Science & Artificial Intelligence

## Project objective
Develop an end-to-end e-commerce BI-DSS using the Olist Brazilian E-Commerce Public Dataset. The system will integrate data, perform descriptive and diagnostic analytics, predict late-delivery risk, and present decision-support insights through an interactive application.

## Planned technology stack
- Python 3.11+
- Pandas and NumPy
- DuckDB and SQL
- Scikit-learn
- Streamlit
- Plotly
- SHAP (if justified and feasible)
- Pytest
- Git and GitHub

## Initial setup (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Place the downloaded Olist CSV files in `data/raw/`. Do not commit large raw datasets to GitHub.

## Run the application

The application entry point will be added during the application development phase.

## Project structure
See the repository folders. Development is divided into data ingestion, validation, transformation, database modelling, EDA, BI, machine learning, decision support, application integration, and testing.

## Reproducibility
Record package versions, data preparation rules, random seeds, model configurations, and test results. Keep secrets in `.env`, which must never be committed.
