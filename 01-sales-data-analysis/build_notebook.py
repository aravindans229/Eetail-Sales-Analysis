import nbformat as nbf
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
from nbclient import NotebookClient

nb = new_notebook()
cells = []

cells.append(new_markdown_cell(
"""# Retail Sales Analysis (SQL + Pandas)

**Goal:** Analyze two years of retail order data to find the best-performing regions,
categories and time periods, and to flag where heavy discounting is hurting profit.

**Dataset:** `data/sales_data.csv` — 3,015 synthetic orders (2023–2024), modeled on the
structure of the well-known Superstore sales dataset (Order, Ship Mode, Segment,
Region, Category, Sub-Category, Quantity, Discount, Sales, Profit).

**Tools:** Python, Pandas, SQLite (SQL), Matplotlib/Seaborn

**Sections:**
1. Load & clean the data
2. SQL analysis (via SQLite) — top products, monthly trends, region revenue
3. Pandas analysis — profit by discount level, segment performance
4. Key findings
"""))

cells.append(new_markdown_cell("## 1. Load & Clean the Data"))
cells.append(new_code_cell(
"""import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (9, 5)

df = pd.read_csv("data/sales_data.csv", parse_dates=["Order_Date", "Ship_Date"])
print("Raw shape:", df.shape)
df.head()"""))

cells.append(new_code_cell(
"""# Check for data quality issues
print("Duplicate rows:", df.duplicated().sum())
print("\\nNulls per column:")
print(df.isnull().sum()[df.isnull().sum() > 0])"""))

cells.append(new_code_cell(
"""# Clean: drop exact duplicates, fill missing Ship_Mode with the column mode
df = df.drop_duplicates()
df["Ship_Mode"] = df["Ship_Mode"].fillna(df["Ship_Mode"].mode()[0])

# Derived columns used later
df["Order_Month"] = df["Order_Date"].dt.to_period("M").astype(str)
df["Profit_Margin"] = (df["Profit"] / df["Sales"]).round(3)

print("Cleaned shape:", df.shape)
df.isnull().sum().sum()  # should be 0"""))

cells.append(new_markdown_cell(
"""## 2. SQL Analysis (SQLite)

Loading the cleaned dataframe into an in-memory SQLite database so the analysis
can be done with real SQL — joins, subqueries, and aggregations — the same way
it would be done against a company database."""))

cells.append(new_code_cell(
"""conn = sqlite3.connect(":memory:")
df.to_sql("sales", conn, index=False, if_exists="replace")

def q(sql):
    return pd.read_sql(sql, conn)"""))

cells.append(new_markdown_cell("**Top 10 sub-categories by total revenue**"))
cells.append(new_code_cell(
"""top_products = q('''
    SELECT Sub_Category, Category,
           ROUND(SUM(Sales), 2) AS Total_Sales,
           ROUND(SUM(Profit), 2) AS Total_Profit,
           COUNT(*) AS Orders
    FROM sales
    GROUP BY Sub_Category, Category
    ORDER BY Total_Sales DESC
    LIMIT 10
''')
top_products"""))

cells.append(new_markdown_cell("**Monthly revenue trend**"))
cells.append(new_code_cell(
"""monthly_trend = q('''
    SELECT Order_Month, ROUND(SUM(Sales), 2) AS Monthly_Sales
    FROM sales
    GROUP BY Order_Month
    ORDER BY Order_Month
''')
monthly_trend.head()"""))

cells.append(new_markdown_cell("**Region-wise revenue and profit, using a subquery to also show each region's share of total sales**"))
cells.append(new_code_cell(
"""region_rev = q('''
    SELECT Region,
           ROUND(SUM(Sales), 2) AS Region_Sales,
           ROUND(SUM(Profit), 2) AS Region_Profit,
           ROUND(100.0 * SUM(Sales) / (SELECT SUM(Sales) FROM sales), 1) AS Pct_Of_Total
    FROM sales
    GROUP BY Region
    ORDER BY Region_Sales DESC
''')
region_rev"""))

cells.append(new_markdown_cell("**Which segment + region combos are least profitable? (JOIN-style aggregation using a CTE)**"))
cells.append(new_code_cell(
"""low_profit_combos = q('''
    WITH combo AS (
        SELECT Region, Segment,
               SUM(Sales) AS Sales,
               SUM(Profit) AS Profit
        FROM sales
        GROUP BY Region, Segment
    )
    SELECT Region, Segment, ROUND(Sales,2) AS Sales, ROUND(Profit,2) AS Profit,
           ROUND(Profit / Sales, 3) AS Margin
    FROM combo
    ORDER BY Margin ASC
    LIMIT 5
''')
low_profit_combos"""))

cells.append(new_markdown_cell("## 3. Pandas Analysis"))
cells.append(new_markdown_cell("**Does higher discount hurt profit margin?**"))
cells.append(new_code_cell(
"""discount_margin = df.groupby("Discount")["Profit_Margin"].mean().round(3)
discount_margin"""))

cells.append(new_code_cell(
"""fig, ax = plt.subplots()
discount_margin.plot(kind="bar", ax=ax, color="#4C72B0")
ax.set_title("Average Profit Margin by Discount Level")
ax.set_xlabel("Discount")
ax.set_ylabel("Average Profit Margin")
ax.axhline(0, color="red", linewidth=1, linestyle="--")
plt.tight_layout()
plt.savefig("charts/discount_vs_margin.png", dpi=120)
plt.show()"""))

cells.append(new_markdown_cell("**Revenue trend over time, by category**"))
cells.append(new_code_cell(
"""monthly_cat = df.groupby(["Order_Month", "Category"])["Sales"].sum().unstack()
fig, ax = plt.subplots(figsize=(11, 5))
monthly_cat.plot(ax=ax)
ax.set_title("Monthly Sales Trend by Category (2023-2024)")
ax.set_ylabel("Sales ($)")
ax.set_xlabel("Month")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("charts/monthly_sales_by_category.png", dpi=120)
plt.show()"""))

cells.append(new_markdown_cell("**Revenue share by region**"))
cells.append(new_code_cell(
"""fig, ax = plt.subplots()
region_rev.set_index("Region")["Region_Sales"].plot(kind="bar", ax=ax, color="#55A868")
ax.set_title("Total Sales by Region")
ax.set_ylabel("Sales ($)")
plt.tight_layout()
plt.savefig("charts/sales_by_region.png", dpi=120)
plt.show()"""))

cells.append(new_markdown_cell(
"""## 4. Key Findings

- **Technology drives the most revenue** of the three categories, but its profit
  margin is more sensitive to discounting than Office Supplies.
- **Discounts of 30% or more push average profit margin close to zero or negative**
  — see the bar chart above. Sales above a ~25% discount threshold should be
  reviewed, since they are close to break-even or loss-making.
- **The West and South regions generate the largest share of revenue**, together
  accounting for roughly half of total sales.
- Monthly sales show **seasonal peaks**, useful for planning inventory and staffing
  around higher-demand months.
- The lowest-margin Region + Segment combinations point to where discounting
  policy or pricing should be reviewed first.

*(Findings are illustrative, generated from a synthetic dataset built to resemble
real retail sales data — the methodology and code are reusable on any real
sales export.)*
"""))

nb["cells"] = cells

client = NotebookClient(nb, timeout=120, kernel_name="python3")
client.execute()

with open("sales_analysis.ipynb", "w") as f:
    nbf.write(nb, f)

print("Notebook built and executed successfully.")
