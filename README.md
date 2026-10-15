# PrescriptAI: Project Overview

## 1. Project Objective

The goal of this project is to build an automated, end-to-end inventory optimization and demand forecasting system for a multichannel retailer. Instead of relying on manual intuition or standard single-point estimates, the system transforms historical sales data into cost-effective purchase orders under uncertainty.

The platform addresses three core requirements:

1. **Probabilistic Demand Forecasting:** Predict daily demand per SKU across a 30 to 90-day horizon using quantile regression (P10, P50, P90) to measure demand uncertainty, intermittency, and risk.
2. **Prescriptive Inventory Optimization:** Translate demand intervals into optimal supplier purchase orders using Mixed-Integer Linear Programming (PuLP/SciPy), balancing stockout penalties against holding costs subject to budget, warehouse capacity, and minimum order quantity (MOQ) limits.
3. **"What-If" Scenario Simulation:** Provide an interactive dashboard where operations managers can adjust business variables (promotions, price changes, lead time shifts, budget cuts) to observe the direct impact on margins and inventory health in real time.

---

## 2. Dataset

The project uses historical Walmart retail data from the **Kaggle M5 Forecasting** competition:

* **`sales_train_evaluation.csv`:** Contains daily unit sales for 3,049 distinct products across 10 stores in 3 US states (California, Texas, Wisconsin) over 1,941 days (~5.3 years). It provides hierarchical categories (Hobbies, Foods, Household) and captures real-world challenges like intermittent and zero-inflated demand.
* **`calendar.csv`:** Contains temporal metadata for every date, including day of the week, month, year, cultural/religious events, and SNAP benefit distribution days (which drive major retail demand spikes by state).
* **`sell_prices.csv`:** Contains weekly unit selling prices for each product-store pair, allowing the model to account for price changes, promotional discounts, and revenue estimation.

---

## 3. High-Level Workflow

1. **Feature Engineering:** Build lag features ($t-28$ and older to avoid leakage), rolling statistics (7, 14, 28 days), calendar signals, and relative price discounts.
2. **Model Training:** Train multi-quantile regressors (LightGBM / MLForecast) to predict the P10 (pessimistic), P50 (median), and P90 (high demand/buffer) bounds.
3. **Prescriptive Engine:** Run linear programming to generate purchase order recommendations tailored to target service levels and physical constraints.
4. **App & Simulation:** Serve forecasts and optimization logic via a FastAPI backend connected to an interactive frontend for real-time scenario testing.