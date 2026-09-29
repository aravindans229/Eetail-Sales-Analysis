# Retail Sales Analysis (SQL + Pandas)

Analysis of two years of retail order data to find top-performing regions,
categories and sub-categories, monthly revenue trends, and where heavy
discounting is eroding profit margin.

## Problem
A retail business wants to know: which products and regions drive the most
revenue, how sales trend month to month, and whether the current discounting
policy is hurting profitability.

## Dataset
`data/sales_data.csv` — 3,015 orders (2023–2024) with Order/Ship dates, Ship
Mode, Segment, Region, Category, Sub-Category, Quantity, Discount, Sales and
Profit. Structured to resemble the well-known Superstore sales dataset.
(Synthetic data, generated with `generate_data.py`, including intentional
duplicates and missing values to practice data cleaning.)

## Approach
1. **Clean** — removed duplicate rows, imputed missing `Ship_Mode` values.
2. **SQL (SQLite)** — top 10 sub-categories by revenue, monthly revenue trend,
   region-wise revenue with % share (subquery), lowest-margin Region+Segment
   combinations (CTE).
3. **Pandas** — profit margin by discount level, monthly sales trend by
   category, revenue by region — each visualized with Matplotlib/Seaborn.

## Key Findings
- Technology drives the most revenue but its margin is most sensitive to discounting.
- Discounts of 30%+ push average profit margin close to zero or negative.
- West and South regions together account for roughly half of total sales.
- Clear seasonal peaks are visible in the monthly trend, useful for planning.

## Tools
Python · Pandas · SQLite (SQL) · Matplotlib · Seaborn

## Files
- `sales_analysis.ipynb` — full analysis notebook, run top to bottom
- `generate_data.py` — synthetic dataset generator
- `data/sales_data.csv` — the dataset
- `charts/` — exported chart images

## How to Run
```bash
pip install pandas numpy matplotlib seaborn
jupyter notebook sales_analysis.ipynb
```
