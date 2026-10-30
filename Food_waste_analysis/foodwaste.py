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