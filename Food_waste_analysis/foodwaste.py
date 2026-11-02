import os 
from mysql.connector import connect 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()

conn = connect(
    host = os.getenv("DB_HOST"),
    user = os.getenv("DB_USER"),
    password = os.getenv("DB_PASSWORD"),
    database = os.getenv("DB_NAME")
)

curs = conn.cursor()

def read():
    sql = "SELECT * FROM food_waste"
    curs.execute(sql)
    values = curs.fetchall()                       # ellaa rows
    columns = [col[0] for col in curs.description] # column names
    return values, columns

values, columns = read()
df = pd.DataFrame.from_records(values, columns=columns, coerce_float=True)



print(df.head())
print(df.shape)
print(df.describe())
print(df.tail())

df.info()
print(df.isnull().sum())
print(df.duplicated().sum())

df['date'] = pd.to_datetime(df['date'])
df['special_event'] = df['special_event'].fillna('None')

df["day_type"] = np.where(df["day_of_week"].isin(["Saturday","Sunday"]),"Weekend","Weekday")
day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
meal_order = ["Breakfast","Lunch","Snacks","Dinner"]


total_prepared = df["quantity_prepared_kg"].sum()
total_wasted = df["quantity_wasted_kg"].sum()

print("Total prepared :", round(total_prepared), "kg")
print("Total wasted :", round(total_wasted), "kg")
print("waste %    :", round(total_wasted / total_prepared * 100, 1), "%")
print("Total waste cost: Rs", round(df["waste_cost_inr"].sum()))


day_summary = df.groupby("day_of_week").agg(
    total_prepared_kg=("quantity_prepared_kg", "sum"),
    total_wasted_kg=("quantity_wasted_kg", "sum"),
    avg_waste_pct=("waste_percentage", "mean")
).reindex(day_order)

days_count = df.groupby("day_of_week")["date"].nunique().reindex(day_order)
day_summary["avg_kg_per_day"] = day_summary["total_wasted_kg"] / days_count

print("\nDay wise summary:")
print(day_summary.round(1))

meal_summary = df.groupby("meal").agg(
    total_prepared_kg=("quantity_prepared_kg", "sum"),
    total_wasted_kg=("quantity_wasted_kg", "sum"),
    avg_waste_pct=("waste_percentage", "mean")
).reindex(meal_order)

meal_summary["share_of_total_waste_pct"] = (
    meal_summary["total_wasted_kg"] / meal_summary["total_wasted_kg"].sum() * 100
)

print("\nMeal wise summary:")
print(meal_summary.round(1))
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 20)


# ---- Item wise ----
item_summary = df.groupby("menu_item").agg(
    total_wasted_kg=("quantity_wasted_kg", "sum"),
    avg_waste_pct=("waste_percentage", "mean"),
    total_waste_cost_rs=("waste_cost_inr", "sum")
)

print("\nTop 10 items by waste (kg):")
print(item_summary.sort_values("total_wasted_kg", ascending=False).head(10).round(1))

print("\nTop 10 items by waste % (disliked items):")
print(item_summary.sort_values("avg_waste_pct", ascending=False).head(10).round(1))

print("\nTop 10 items by waste cost (Rs):")
print(item_summary.sort_values("total_waste_cost_rs", ascending=False).head(10).round(0))


# ---- Category wise ----
cat_summary = df.groupby("category").agg(
    total_prepared_kg=("quantity_prepared_kg", "sum"),
    total_wasted_kg=("quantity_wasted_kg", "sum"),
    avg_waste_pct=("waste_percentage", "mean"),
    total_waste_cost_rs=("waste_cost_inr", "sum")
).sort_values("total_wasted_kg", ascending=False)

print("\nCategory wise summary:")
print(cat_summary.round(1))



# ---- Weekday vs Weekend ----
daytype_summary = df.groupby("day_type").agg(
    total_prepared_kg=("quantity_prepared_kg", "sum"),
    total_wasted_kg=("quantity_wasted_kg", "sum"),
    avg_waste_pct=("waste_percentage", "mean")
)

n_days = df.groupby("day_type")["date"].nunique()
daytype_summary["avg_kg_per_day"] = daytype_summary["total_wasted_kg"] / n_days

print("\nWeekday vs Weekend:")
print(daytype_summary.round(1))


# ---- Rainy day impact ----
rain = df.groupby("rainy_day").agg(
    total_wasted_kg=("quantity_wasted_kg", "sum"),
    avg_waste_pct=("waste_percentage", "mean")
)
rain["days"] = df.groupby("rainy_day")["date"].nunique()
rain["avg_kg_per_day"] = rain["total_wasted_kg"] / rain["days"]

print("\nRainy vs normal days:")
print(rain.round(1))

# ---- Special event impact ----
event = df.groupby("special_event").agg(
    avg_waste_pct=("waste_percentage", "mean"),
    days=("date", "nunique")
).sort_values("avg_waste_pct", ascending=False)

print("\nSpecial event impact:")
print(event.round(1))

w = df["waste_percentage"].to_numpy()

print("\nNumPY statistics (waste %):")
print("Mean            :", round(np.mean(w), 2))
print("Median          :", round(np.median(w), 2))
print("std deviation   :", round(np.std(w), 2))
print("min             :", round(np.min(w), 2))
print("max             :", round(np.max(w), 2))
print("90th percentile :", round(np.percentile(w, 90), 2))

print("\nCorrelation (students_present vs waste %):",
      round(np.corrcoef(df["students_present"], df["waste_percentage"])[0, 1], 2))
print("\nCorrelation (prepared kg vs wasted kg)  :",
      round(np.corrcoef(df["quantity_prepared_kg"], df["quantity_wasted_kg"])[0, 1], 2))

q1, q3 = np.percentile(w, [25, 75])
iqr = q3 - q1
upper  = q3 + 1.5 * iqr
print("\nOutlier limit (IQR):", round(upper, 1), "%")
print("Outlier rows       :", (w > upper).sum())


#------cooking recommendation-----
df["kg_per_student"] = df["quantity_consumed_kg"] / df["students_present"]

rec = df.groupby(["day_of_week", "meal", "menu_item"])["kg_per_student"].mean().reset_index()
rec["recommended_kg_per_student"] = (rec["kg_per_student"] * 1.05).round(4)

def cook_quantity(day, meal, expected_students):
    r = rec[(rec["day_of_week"] == day) & (rec["meal"] == meal)].copy()
    r["cook_kg"] = (r["recommended_kg_per_student"] * expected_students).round(1)
    return r[["menu_item", "cook_kg"]]

print("\nRecommendation example: Sunday Lunch, 230 students")
print(cook_quantity("Sunday", "Lunch", 230).to_string(index=False))

rec.to_csv("cooking_recommendation.csv", index=False)


#-----savings estimate (train on jul-aug, test on sep) ---- 
keys = ["day_of_week", "meal", "menu_item"]
train = df[df["date"] < "2026-09-01"]
test = df[df["date"] >= "2026-09-01"]
rec_train = train.groupby(keys)["kg_per_student"].mean().reset_index()

results = []
for buffer in [1.05, 1.10, 1.15]:
    r = rec_train.copy()
    r["recommended"] = r["kg_per_student"] * buffer
    m = test.merge(r[keys + ["recommended"]], on=keys, how="inner")
    m["new_prepared"] = m["recommended"] * m["students_present"]
    shortage_pct = (m["new_prepared"] < m["quantity_consumed_kg"]).mean() * 100
    m["new_prepared"] = np.maximum(m["new_prepared"], m["quantity_consumed_kg"])
    m["new_wasted"] = m["new_prepared"] - m["quantity_consumed_kg"]
    old_waste = m["quantity_wasted_kg"].sum()
    new_waste = m["new_wasted"].sum()
    old_cost = (m["quantity_wasted_kg"] * m["cost_per_kg_inr"]).sum()
    new_cost = (m["new_wasted"] * m["cost_per_kg_inr"]).sum()
    results.append({
        "buffer": f"{round((buffer - 1) * 100)}%",
        "old_waste_kg": old_waste,
        "new_waste_kg": new_waste,
        "saved_kg": old_waste - new_waste,
        "waste_reduction_pct": (old_waste - new_waste) / old_waste * 100,
        "saved_rs": old_cost - new_cost,
        "shortage_risk_pct": shortage_pct
    })

    print("\nSavings estimate (tested on september date):")
    print(pd.DataFrame(results).round(1).to_string(index=False))