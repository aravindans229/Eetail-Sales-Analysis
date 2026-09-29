"""
Generates a synthetic but realistic retail sales dataset,
similar in structure to the popular Kaggle 'Superstore' dataset.
"""
import numpy as np
import pandas as pd

np.random.seed(42)

N = 3000

regions = ["South", "North", "East", "West"]
categories = {
    "Furniture": ["Chairs", "Tables", "Bookcases", "Furnishings"],
    "Office Supplies": ["Binders", "Paper", "Storage", "Art"],
    "Technology": ["Phones", "Accessories", "Machines", "Copiers"],
}
segments = ["Consumer", "Corporate", "Home Office"]
ship_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]

dates = pd.date_range("2023-01-01", "2024-12-31", freq="D")

rows = []
order_id_counter = 1000

for i in range(N):
    order_date = np.random.choice(dates)
    order_date = pd.Timestamp(order_date)
    ship_delay = np.random.randint(1, 8)
    ship_date = order_date + pd.Timedelta(days=int(ship_delay))

    region = np.random.choice(regions, p=[0.30, 0.28, 0.22, 0.20])
    category = np.random.choice(list(categories.keys()), p=[0.25, 0.45, 0.30])
    sub_category = np.random.choice(categories[category])
    segment = np.random.choice(segments, p=[0.5, 0.3, 0.2])
    ship_mode = np.random.choice(ship_modes, p=[0.55, 0.2, 0.15, 0.1])

    # base price varies by category
    base_price = {
        "Furniture": np.random.uniform(60, 900),
        "Office Supplies": np.random.uniform(5, 150),
        "Technology": np.random.uniform(50, 1800),
    }[category]

    quantity = np.random.randint(1, 10)
    discount = np.random.choice([0, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5],
                                 p=[0.35, 0.2, 0.15, 0.1, 0.1, 0.05, 0.05])
    sales = round(base_price * quantity * (1 - discount * 0.3), 2)  # discount softens revenue a bit

    # profit: technology has thinner margins when discount is high; furniture can go negative
    margin = np.random.uniform(0.05, 0.35)
    if discount >= 0.3:
        margin -= discount * 0.4  # heavy discounts erode / flip margin
    profit = round(sales * margin, 2)

    rows.append({
        "Order_ID": f"ORD-{order_id_counter}",
        "Order_Date": order_date.date().isoformat(),
        "Ship_Date": ship_date.date().isoformat(),
        "Ship_Mode": ship_mode,
        "Segment": segment,
        "Region": region,
        "Category": category,
        "Sub_Category": sub_category,
        "Quantity": quantity,
        "Discount": discount,
        "Sales": sales,
        "Profit": profit,
    })
    order_id_counter += 1

df = pd.DataFrame(rows)

# introduce a bit of realistic messiness for the cleaning step
dupe_rows = df.sample(15, random_state=1)
df = pd.concat([df, dupe_rows], ignore_index=True)
null_idx = df.sample(20, random_state=2).index
df.loc[null_idx, "Ship_Mode"] = None

df.to_csv("data/sales_data.csv", index=False)
print(f"Generated {len(df)} rows -> data/sales_data.csv")
