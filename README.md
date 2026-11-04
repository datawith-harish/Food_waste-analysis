# Food Waste Analysis for a Hostel Mess

An analytics mini project that studies how much food a hostel mess prepares versus how much is actually eaten, finds where and when the waste happens, and recommends how much to cook to reduce it.

**Domain:** Data Analytics
**Tools:** Python (NumPy, Pandas, Matplotlib), MySQL, VS Code

---

## Objective

1. Track daily food prepared vs. consumed in a hostel mess.
2. Find the wasted quantity by day, meal and menu item.
3. Suggest how much to cook so that waste (and cost) is reduced.

---

## Dataset

The dataset is **simulated (synthetic)** to look like real hostel mess records, because real mess data is not publicly available.

| Detail | Value |
|---|---|
| Records | 977 rows, 15 columns |
| Period | 1 July 2026 to 28 September 2026 (90 days) |
| Hostel size | About 320 students |
| Meals | Breakfast, Lunch, Snacks, Dinner |
| Menu items | 37 items (Idli, Sambar, Rice, Chicken Biryani, Payasam, etc.) |

**Columns:** `record_id, date, day_of_week, meal, menu_item, category, students_present, quantity_prepared_kg, quantity_consumed_kg, quantity_wasted_kg, waste_percentage, cost_per_kg_inr, waste_cost_inr, rainy_day, special_event`

> Note: Because the data is simulated, the numbers show that the method works. Results on a real hostel will differ.

---

## Project Workflow

```
MySQL (store data) -> Python (load) -> Pandas (clean and analyse)
-> NumPy (statistics) -> Matplotlib (charts) -> Recommendation and savings
```

| Step | Work |
|---|---|
| 1 | Create dataset and import it into MySQL (`food_waste_db`) |
| 2 | Connect Python to MySQL (credentials stored safely in a `.env` file) |
| 3 | Explore the data and run quality checks (nulls, duplicates, logic check) |
| 4 | Clean the data (date type, missing event values) |
| 5 | Analyse waste by day, meal, item, category, weekday vs weekend, rain and events |
| 6 | Statistics with NumPy (mean, median, standard deviation, correlation, outliers) |
| 7 | Build the cooking recommendation (kg per student for each day, meal and item) |
| 8 | Estimate savings by testing the recommendation on unseen data |
| 9 | Create charts with Matplotlib |

---

## Key Findings

**Overall**
- Total food prepared: **41,160 kg**
- Total food wasted: **10,094 kg (24.5%)**
- Total waste cost: **Rs 721,642** in about 3 months

**By day**
- Sunday has the highest waste: **40.3%** (about 165 kg per day).
- Tuesday has the lowest waste: **17.8%** (about 77 kg per day).

**Weekday vs Weekend**
- Weekend waste is **36.8%** against **21.0%** on weekdays.
- Per day, the weekend wastes about **162 kg** against **92 kg** on a weekday.

**By meal**
- Lunch wastes the most food in kg (3,742 kg, 37% of all waste).
- Snacks has the highest waste percentage (30.7%).
- Worst combination: Sunday Snacks (45.2%). Best combination: Tuesday Lunch (13.8%).

**By item**
- Sambar wastes the most food in kg (about 1,116 kg).
- Chicken Biryani is the biggest money loss (about Rs 73,104).
- Payasam has the highest waste percentage (39.9%).

**Special days**
- Holidays: waste goes up to **47% to 55%**.
- Exam week: waste is lowest at **19.9%**.
- Rain has very little effect (26.6% on rainy days vs 25.2% on normal days).

**Statistics**
- Correlation between students present and waste % is **-0.85**: when fewer students come, waste goes up, because the kitchen cooks a fixed quantity.

---

## Cooking Recommendation

For each day, meal and menu item, the project calculates the average kg eaten per student and adds a safety buffer. The kitchen can then use the function:

```python
cook_quantity("Sunday", "Lunch", 230)
```

Example output (Sunday Lunch, 230 students):

| Menu item | Cook (kg) |
|---|---|
| Chicken Biryani | 91.8 |
| Egg Curry | 28.1 |
| Payasam | 23.1 |

The full table is saved as `cooking_recommendation.csv`.

---

## Savings Estimate

The recommendation was built from **July and August** data and tested on **September** data that it had never seen.

| Safety buffer | Waste reduced | Food saved (kg) | Money saved (Rs) | Risk of running short |
|---|---|---|---|---|
| 5% | 81.2% | 2,497 | 180,817 | 22.7% |
| **10% (recommended)** | **67.4%** | **2,074** | **151,732** | **7.2%** |
| 15% | 52.2% | 1,606 | 119,441 | 1.6% |

A smaller buffer saves more food but increases the risk of food running short. A 10% buffer is a good balance.

---

## Charts

All charts are saved in the `charts/` folder.

| Chart | What it shows |
|---|---|
| `1_day_kg.png` | Average waste per day (kg) |
| `2_day_percent.png` | Average waste % by day |
| `3_meal_kg.png` | Total waste by meal (kg) |
| `4_top10_items.png` | Top 10 wasted items |
| `5_weekday_weekend.png` | Weekday vs weekend waste |
| `6_day_meal.png` | Waste % by day and meal |

---

## Project Structure

```
Food_waste_analysis/
├── foodwaste.py                      # Main analysis script
├── hostel_food_waste_dataset.csv     # Dataset (CSV)
├── hostel_food_waste_dataset.sql     # Dataset (MySQL import file)
├── cooking_recommendation.csv        # Output: how much to cook
├── charts/                           # Output: charts
├── .gitignore
└── README.md
```

---

## How to Run

**1. Install the libraries**
```
pip install pandas numpy matplotlib mysql-connector-python python-dotenv
```

**2. Create the database**
Open `hostel_food_waste_dataset.sql` in MySQL Workbench and run it. This creates the database `food_waste_db` and the table `food_waste` with all records.

**3. Create a `.env` file** in the project folder (same folder as `foodwaste.py`):
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=food_waste_db
```

**4. Run the script**
```
python foodwaste.py
```
The results are printed in the terminal, the charts are saved in `charts/`, and `cooking_recommendation.csv` is created.

---

## Skills Used

- SQL: database and table creation, data import
- Python: MySQL connection, environment variables
- Pandas: groupby, aggregation, pivot tables, merge
- NumPy: mean, median, standard deviation, percentile, correlation, IQR outliers
- Matplotlib: bar charts with custom colours
- Data analysis: quality checks, train and test split, savings estimation

---

## Future Improvements

- Use real mess data collected over a longer period.
- Add a simple forecast for the number of students expected each day.
- Build a small dashboard so the kitchen staff can enter the student count and see the quantity to cook.

---

## Author

Data Analytics Intern. Mini project created during a one-month internship.
