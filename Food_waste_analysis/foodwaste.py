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