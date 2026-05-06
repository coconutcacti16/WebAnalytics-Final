# F1 Product Prediction Models & Analysis

This folder contains predictive machine learning models and forecasts for 2026 F1 best-selling products. It includes outputs from models such as DBSCAN, KMeans, XGBoost, and Neural Networks.

## Contents
- **CSV Data:** `PREDICTED_*.csv` files for each model and `ACTUAL_best_selling_2026.csv`
- **Visuals:** `model_comparison_matrix.png`
- **Scripts:** `predict_2026_nn.py`, `scrape_actual_2026.py`

## How to Run
To scrape actual 2026 products for comparison:
```bash
python scrape_actual_2026.py
```
To run the Neural Network predictions:
```bash
python predict_2026_nn.py
```
