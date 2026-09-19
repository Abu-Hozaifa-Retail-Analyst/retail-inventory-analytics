# Retail Inventory Analytics

## GulfMart Retail — Inventory Availability, Efficiency & Replenishment Analytics

> **Portfolio Project | Retail Analytics | Python | Pandas | SQL Server | Power BI**

---

## 📌 Project Overview

This project analyzes inventory performance for a fictional GCC retailer, **GulfMart Retail**, with the objective of improving inventory availability, reducing excess stock, and supporting better replenishment decisions.

The project is being developed as an end-to-end **Retail Inventory Analytics** solution using:

* Python / Pandas for data generation, profiling, cleaning, validation, and analytical preparation
* SQL Server for structured data storage and business analysis
* Power BI for interactive reporting and decision-making
* Git/GitHub for version control and portfolio presentation

The project uses a realistic synthetic retail dataset designed around GCC retail business scenarios.

The project is intentionally developed incrementally, with each major stage validated before moving to the next stage.

---

# 🎯 Business Problem

GulfMart Retail is experiencing an inventory imbalance:

* High-demand products may frequently go out of stock.
* Low-demand products may remain in inventory for long periods.
* Some stores may hold too much inventory while others face shortages.
* Promotions and seasonal demand can create temporary demand spikes.
* Long supplier lead times can increase replenishment risk.
* Excess inventory ties up working capital.

### Core Business Question

> **Do we have the right products, in the right quantities, at the right stores, at the right time — while maintaining healthy inventory efficiency and profitability?**

---

# 🎯 Project Objective

The primary objective is to:

> **Improve inventory availability and inventory efficiency while protecting profitability and reducing excess working capital.**

The project will eventually support decisions related to:

* Inventory replenishment
* Stockout prevention
* Excess inventory reduction
* Store-to-store transfers
* Product assortment
* Supplier performance
* Markdown opportunities
* Working capital optimization
* Demand and inventory planning

---

# 🏗️ Project Architecture

The project follows an end-to-end retail analytics workflow:

```text
Business Problem
       ↓
Project Setup
       ↓
Synthetic Retail Data Generation
       ↓
Data Profiling
       ↓
Data Cleaning
       ↓
Data Validation
       ↓
Demand Calibration
       ↓
Inventory Generation
       ↓
Inventory Reconciliation
       ↓
Inventory KPI Analysis
       ↓
Stockout Analysis
       ↓
Overstock Analysis
       ↓
ABC Analysis
       ↓
Inventory Aging
       ↓
Replenishment Analysis
       ↓
Store & Product Diagnosis
       ↓
Root Cause Analysis
       ↓
SQL Server Implementation
       ↓
Power BI Dashboard
       ↓
Business Recommendations
```

---

# 📊 Dataset

The project uses a synthetic dataset representing a GCC retail business.

### Current Dataset Scope

| Entity                    |                   Volume |
| -------------------------- | -----------------------: |
| Stores                     |                       20 |
| Products                   |                      500 |
| Customers                  |                    5,000 |
| Suppliers                  |                       30 |
| Date Range                 | 2023-01-01 to 2025-12-31 |
| Target Sales Transactions  |                  125,000 |
| Inventory Records (daily)  |               10,960,000 |

The dataset is intentionally generated with realistic retail relationships rather than being a random collection of numbers.

---

# 🗂️ Data Model

The project uses a dimensional/star-schema-oriented structure.

```text
                    dim_date
                       |
                       |
dim_customer ─── fact_sales ─── dim_product
                       |
                       |
                   dim_store
                       |
                  dim_supplier


                    dim_date
                       |
                       |
dim_product ─── fact_inventory ─── dim_store
                       |
                  dim_supplier
```

### Main Tables

#### Dimension Tables

* `dim_date`
* `dim_product`
* `dim_store`
* `dim_customer`
* `dim_supplier`

#### Fact Tables

* `fact_sales` — generated, validated, and saved to `data/raw/fact_sales.csv`
* `fact_inventory` — generated, validated, and saved to `data/raw/fact_inventory.csv.gz` (gzip-compressed, ~10.96M rows)

---

# 🧱 Current Project Structure

```text
retail-inventory-analytics/
│
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── processed/
│
├── notebooks/
│   ├── 01_data_profiling.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_inventory_kpis.ipynb
│   ├── 04_stockout_analysis.ipynb
│   ├── 05_overstock_analysis.ipynb
│   ├── 06_abc_analysis.ipynb
│   └── 07_replenishment_analysis.ipynb
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── data_validation.py
│   ├── inventory_kpis.py
│   ├── utils.py
│   ├── data_generation_config.py
│   ├── validate_generation_config.py
│   └── data_generation.py
│
├── sql/
│   ├── 01_create_database.sql
│   ├── 02_create_tables.sql
│   ├── 03_load_data.sql
│   ├── 04_data_validation.sql
│   ├── 05_inventory_kpis.sql
│   ├── 06_stockout_analysis.sql
│   ├── 07_overstock_analysis.sql
│   └── 08_replenishment_analysis.sql
│
├── powerbi/
│   └── retail_inventory_analytics.pbix
│
├── docs/
│   ├── business_problem.md
│   ├── data_dictionary.md
│   ├── kpi_definitions.md
│   ├── inventory_methodology.md
│   └── business_recommendations.md
│
├── outputs/
│   ├── figures/
│   └── reports/
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

# 🐍 Python Data Generation

A major part of the project is a configurable synthetic retail data-generation framework.

The generator is controlled through:

```text
src/data_generation_config.py
```

and implemented through:

```text
src/data_generation.py
```

A fixed random seed is used to make the dataset reproducible:

```python
RANDOM_SEED = 42
```

### Generation Architecture

```text
Configuration
      ↓
dim_date
      ↓
dim_supplier
      ↓
dim_product
      ↓
dim_store
      ↓
dim_customer
      ↓
fact_sales
      ↓
fact_inventory
      ↓
Data Quality Injection
      ↓
Data Validation
      ↓
Save Datasets
```

The full pipeline is now orchestrated end to end through a single entry point:

```python
generate_all_data()
```

which calls every generation stage in sequence, validates the result, persists it to `data/raw/`, and returns all generated tables as a dictionary. Running:

```bash
python src/data_generation.py
```

now produces a complete, validated, saved dataset with **no manual steps required**.

---

# 📅 Date Dimension

The project currently generates a date dimension covering:

```text
2023-01-01 → 2025-12-31
```

This produces **1,096 calendar days**, including leap-year coverage for 2024.

The date dimension includes fields such as:

* Date
* Year
* Quarter
* Month
* Month Name
* Week of Year
* Day
* Day Name
* Day of Week
* Weekend Flag
* Season
* Ramadan Flag
* Eid Period Flag

### Validation

```text
✓ Date range validated
✓ Calendar generated successfully
✓ 1,096 calendar days
✓ Ramadan and Eid attributes available
```

---

# 🏭 Supplier Dimension

The supplier dimension currently models:

* Supplier ID
* Supplier Name
* Supplier Region
* Lead Time
* Minimum Order Quantity
* Supplier Status

Supplier regions include Local, Regional, and International, each with different synthetic lead-time ranges.

### Validation

```text
✓ 30 suppliers configured
✓ Supplier IDs generated
✓ Supplier regions generated
✓ Lead times generated
✓ Minimum order quantities generated
```

---

# 📦 Product Dimension

The product dimension currently contains Product ID, Name, Category, Subcategory, Brand, Supplier ID, Unit Cost, Selling Price, Product Status, Launch Date, Shelf Life, Demand Class, Demand Trajectory, and Base Demand.

### Demand Classes

```text
Fast-moving
Medium-moving
Slow-moving
```

### Demand Trajectories

```text
Growing
Stable
Declining
Volatile
```

### Product Categories

Grocery, Beverages, Personal Care, Household, Electronics, Fashion, Home & Living, Beauty

### Validation

```text
✓ 500 products generated
✓ Product categories generated
✓ Supplier relationships generated
✓ Pricing attributes generated
✓ Demand classes and trajectories generated
```

---

# 🏪 Store Dimension

Store formats: Hypermarket, Supermarket, Express, E-commerce, distributed across Riyadh, Jeddah, Makkah, Madinah, Dammam, Khobar, Tabuk, and Abha.

Each store has a synthetic demand factor based on store type and region.

### Validation

```text
✓ 20 stores generated
✓ Store formats and locations generated
✓ Store demand factors generated
```

---

# 👥 Customer Dimension

**5,000 synthetic customers** with Segment, Gender, Age Group, City, Tenure, Preferred Channel, Purchase Frequency Factor, Average Basket Factor, and Price Sensitivity.

Segments: Premium, Regular, Value, New.

### Validation

```text
✓ 5,000 customers generated, IDs unique
✓ Purchase frequency and basket factors generated
✓ Price sensitivity generated
```

---

# 💰 Sales Fact Table

`fact_sales` is completed, validated, and persisted: **125,000 transactions**.

### Sales Calculation Logic

```text
Gross Sales      = Quantity × Unit Price
Discount Amount  = Gross Sales × Discount %
Net Sales        = Gross Sales − Discount Amount
COGS             = Quantity × Unit Cost
Gross Profit     = Net Sales − COGS
```

### Demand Modeling

```text
Base Demand
     × Demand Class
     × Demand Trajectory
     × Store Demand
     × Customer Behavior
     × Day-of-Week
     × Seasonality
     × Promotion
     × Random Variation
     × Demand Spikes
```

### Promotion Validation

```text
Non-promotion average quantity ≈ 4.35
Promotion average quantity     ≈ 4.97
```

### Seasonality Validation

```text
✓ Summer has the highest average quantity among standard seasons
✓ Ramadan demand is higher than normal-period demand
✓ Eid-period demand is higher than normal-period demand
✓ Ramadan/Eid overlap = 0
```

### Sales Data Validation

```text
Structural
✓ 125,000 transactions
✓ Product / Store / Customer IDs valid (100% referential integrity)

Financial
✓ Quantity > 0, Unit Price > 0
✓ Gross Sales ≥ Net Sales, Net Sales > 0, COGS > 0
✓ All derived calculations verified correct

Business Behavior
✓ Fast-moving (5.29) > Medium-moving (1.67) > Slow-moving (1.51) avg quantity
✓ Promotions generate higher average quantities
✓ Seasonal / Ramadan / Eid demand uplift present
✓ Ramadan/Eid periods mutually exclusive
```

---

# 📦 Inventory Analytics — Fact Table Generated, Validated & Saved

`fact_inventory` generation is now **complete, validated, and persisted** end-to-end.

Grain: **one row = one product × one store × one day**

```text
20 stores × 500 products × 1,096 days = 10,960,000 rows
```

Inventory flow modeled as:

```text
Opening Stock
+ Receipts
+ Transfers In
− Transfers Out
− Sales
+ Returns
− Damaged Units
± Inventory Adjustments
= Closing Stock
```

### Actual Demand Calibration

Initial theoretical demand (`Base Demand × Store Demand Factor`) was found to overstate real demand, so inventory is calibrated against **observed historical sales** instead:

```text
Actual Average Daily Demand = Total Historical Sales Units ÷ Number of Calendar Days
Active-Day Demand Rate      = Total Historical Sales Units ÷ Number of Active Selling Days
```

`active_day_demand_rate` is used as the calibrated `demand_rate` driving all downstream inventory logic, since the synthetic sales dataset is sparse relative to the full product-store-day calendar.

```text
Product-store combinations: 10,000
Product-store combinations with sales: 7,825
Mean active-day demand rate: 2.33 units/day
Median active-day demand rate: 1.75 units/day
Max active-day demand rate: 8.39 units/day
```

### Recalibrated Initial Inventory

```text
Initial Stock = Calibrated Demand Rate × Initial Inventory Days (by demand class)
```

```text
count    10,960,000
mean          35.25
50%           34.00
max          225.00
```

Down from a theoretical-demand mean of ~115 units — confirming the recalibration meaningfully corrected over-stocking.

### Replenishment Logic

Implemented in full:

* **Safety stock** = demand rate × safety stock days (by demand class)
* **Lead-time demand** = demand rate × supplier lead time
* **Reorder point (ROP)** = lead-time demand + safety stock
* **Review-period demand** = demand rate × replenishment interval
* **Target stock level** = lead-time demand + review-period demand + safety stock
* **Planned order quantity**, triggered only on periodic review dates, respecting each supplier's minimum order quantity (MOQ)
* Orders converted into **receipt events** on their expected receipt date (`order date + lead time`)

```text
Replenishment review events: 818,440
Replenishment orders created: 730,069
Receipt events created: 730,069
```

### Daily Inventory Flow & Reconciliation

Closing stock is computed as a running cumulative balance per product-store combination:

```text
Closing Stock = Initial Opening Stock + Σ(Net Inventory Change)
Net Inventory Change = Receipts + Transfers In − Transfers Out − Sales + Returns − Damaged + Adjustments
Opening Stock (day n) = Closing Stock (day n−1)
```

### Validation Results

```text
✓ Inventory continuity check   — 10,950,000 rows checked, 0 failures
✓ Inventory reconciliation      — 0 failures
✓ Negative inventory check      — 0 negative rows (0.00%)
✓ fact_inventory row count matches expected grain — 10,960,000 rows
```

### Inventory Status Distribution

```text
Healthy      10,926,211
Low Stock        33,789
Stockout               0
```

```text
Replenishment Orders : 730,069
Receipt Events        : 722,087
Sales Events          : 122,236
Low Stock Events      :  33,789
Stockout Events       :       0
```

Zero real stockouts is an expected result of well-calibrated safety stock / reorder-point logic on synthetic demand — this will be a deliberate discussion point in the eventual Stockout Analysis notebook (e.g. testing what happens under tighter safety-stock assumptions or demand shocks).

---

# 🧪 Controlled Data-Quality Injection

To make the downstream data-cleaning notebook (`02_data_cleaning.ipynb`) meaningful, a small, controlled set of data-quality issues is deliberately injected **after** generation and validation of the core datasets — not into `fact_inventory`, to avoid contradicting the reconciliation/continuity checks above.

Implemented via `inject_data_quality_issues()`:

```text
✓ Missing brand values injected into dim_product
✓ Missing city values injected into dim_customer
✓ Inconsistent city text formatting injected into dim_store (case + whitespace)
✓ Missing supplier_name values injected into dim_supplier
✓ Duplicate transactions injected into fact_sales
```

Controlled by `DATA_QUALITY_ISSUE_PROBABILITY` in `data_generation_config.py` (default 0.1%, scaled up for very small tables like `dim_store` so issues remain visible).

### Latest Injection Run

```text
dim_product      : 0 missing brand values
dim_customer     : 4 missing city values
dim_store        : 0 inconsistent city text values
dim_supplier     : 1 missing supplier_name value
fact_sales       : 125 duplicate transactions
```

Note: exact counts vary slightly run to run because they're probability-driven against small tables (e.g. 500 products × 0.1% ≈ 0.5 expected) — this is expected variance, not a bug. `fact_sales` (125,000 rows) reliably produces visible duplicates every run.

---

# 🧪 Automated Dataset Validation

`validate_generated_dataset()` runs a full suite of automated checks across every generated table after generation and data-quality injection, replacing what was previously manual/visual inspection of print statements.

### Structural Validation

```text
✓ Row counts match configuration for every dimension table
✓ fact_sales referential integrity (product_id, store_id, customer_id all resolve)
✓ fact_inventory row count matches expected grain (stores × products × days)
```

### Financial Validation

```text
✓ Quantity > 0, Unit Price > 0
✓ Gross Sales ≥ Net Sales, Net Sales > 0, COGS > 0
✓ Gross Sales / Net Sales / COGS / Gross Profit calculations all verified correct
```

### Business Behavior Validation

```text
✓ Fast-moving > Medium-moving > Slow-moving average quantity
✓ Promotions generate higher average quantities than non-promotions
✓ Ramadan / Eid periods are mutually exclusive
```

### Inventory Validation

```text
✓ No negative closing or opening stock
✓ Inventory continuity holds (opening stock = previous day's closing stock)
```

### Data-Quality Validation (informational — reports counts, does not fail the run)

```text
✓ Missing brand / city / supplier_name counts reported
✓ Inconsistent city formatting count reported
✓ Duplicate transaction count reported
```

### Latest Validation Run

```text
Validation summary: 30/30 checks passed
```

---

# 🛠️ Data Output

Running the full pipeline (`python src/data_generation.py`) now saves every table to `data/raw/`:

```text
data/raw/
├── dim_date.csv
├── dim_product.csv
├── dim_store.csv
├── dim_customer.csv
├── dim_supplier.csv
├── fact_sales.csv
└── fact_inventory.csv.gz      (gzip-compressed — ~10.96M rows)
```

`fact_inventory` is gzip-compressed because of its size; pandas reads it back transparently:

```python
fact_inventory = pd.read_csv("data/raw/fact_inventory.csv.gz")
```

`data/raw/`, `data/cleaned/`, and `data/processed/` are excluded from Git via `.gitignore` — only the generation code is versioned, not the generated data itself.

---

# 📊 Planned Inventory KPIs

### Core KPIs

Inventory Turnover · Sell-through % · Stockout Rate · In-stock Rate · Average Inventory · Inventory Value · Days of Inventory · Inventory Coverage Days

### Inventory Risk

Slow-moving Inventory · Dead Stock · Excess Inventory · Stockout Risk · Replenishment Risk · Aging Inventory

### Profitability

Gross Profit · Gross Margin % · GMROI

### Replenishment

Safety Stock · Reorder Point · Lead Time · Minimum Order Quantity · Replenishment Priority

---

# 🔎 Planned Business Analysis

**Inventory Availability** — Which products/stores experience the most stockouts? Which high-demand products are frequently unavailable?

**Excess Inventory** — Which products/stores carry excessive or slow-moving stock?

**Product Analysis** — Which products drive the most sales/profit? Which have high demand but poor availability?

**Store Analysis** — Which stores are overstocked or understocked? Where should inventory be transferred?

**Supplier Analysis** — Which suppliers have long lead times or create replenishment risk?

**Replenishment** — Which products should be reordered first, and at what safety-stock level?

---

# 📊 Planned ABC Analysis

```text
A → Highest-value products
B → Medium-value products
C → Lower-value products
```

Goal: not "which products sell the most" but **"which products deserve the most inventory-management attention."**

---

# 🛠️ Technology Stack

| Technology  | Purpose                              |
| ----------- | ------------------------------------ |
| Python      | Data generation, cleaning & analysis |
| Pandas      | Data manipulation                    |
| NumPy       | Numerical modeling                   |
| Matplotlib  | Visualization                        |
| Seaborn     | Exploratory visualization            |
| SQL Server  | Data storage & SQL analytics         |
| SSMS        | Database development                 |
| Power BI    | Dashboard & reporting                |
| DAX         | BI calculations                      |
| Power Query | Data transformation                  |
| Git         | Version control                      |
| GitHub      | Portfolio & project collaboration    |
| VS Code     | Development environment              |
| Jupyter     | Exploratory analysis                 |

---

# 🔄 Hybrid Analytics Architecture

**Python** — synthetic data generation, profiling, cleaning, complex transformations, statistical/demand/inventory modeling.

**SQL Server** — structured storage, validation, joins, KPI calculations, reusable views, analytical queries.

**Power BI** — KPI dashboards, inventory health monitoring, store/product analysis, stockout visualization, management reporting.

---

# 🌱 Git Development

The project is developed incrementally using Git, with each stage validated before the next.

```text
Initialize retail inventory analytics project
Add project README
Add dataset generator module skeleton
Implement date dimension generation
Implement supplier dimension generation
Implement product dimension generation
Implement store dimension generation
Implement customer dimension generation
Implement fact sales generation
Implement actual demand calibration for inventory generation
Implement recalibrated initial inventory and replenishment logic
Implement daily inventory flow, continuity & reconciliation validation
Wire complete data generation pipeline (generate_all_data)
Implement inject_data_quality_issues() for controlled data messiness
Implement validate_generated_dataset() with structural, financial, and data-quality checks
Implement save_datasets() — persist generated tables to data/raw/
```

### Current Development Milestone

```text
Full data generation pipeline complete — moving to notebooks (data profiling)
```

Each major development stage is validated before moving to the next stage. Code and its corresponding README documentation update are committed together, as a single unit of change.

---

# 🚧 Project Status

## Completed

* [x] Project structure
* [x] Git/GitHub setup
* [x] Python environment
* [x] Requirements setup
* [x] Data-generation configuration
* [x] Date dimension
* [x] Supplier dimension
* [x] Product dimension
* [x] Store dimension
* [x] Customer dimension
* [x] Sales fact generation
* [x] Sales financial validation
* [x] Demand behavior validation
* [x] Promotion validation
* [x] Seasonality validation
* [x] Ramadan/Eid validation
* [x] Product-store inventory calendar
* [x] Daily sales aggregation for inventory
* [x] Supplier information integration
* [x] Actual historical demand calculation
* [x] Demand-rate calibration
* [x] Recalibrated initial inventory
* [x] Safety stock / reorder point / target stock level logic
* [x] Replenishment order & receipt generation
* [x] Daily inventory flow (closing stock cumulative calculation)
* [x] Inventory continuity validation (0 failures)
* [x] Inventory reconciliation validation (0 failures)
* [x] Negative inventory validation (0 rows)
* [x] Stockout / low-stock / inventory status flags
* [x] Full pipeline orchestration (`generate_all_data`)
* [x] Controlled data-quality issue injection
* [x] `validate_generated_dataset()` — automated structural/financial/business/data-quality checks (30/30 passing)
* [x] `save_datasets()` — persist all generated tables to `data/raw/` (CSV, `fact_inventory` gzip-compressed)

## In Progress

* [ ] Remove/refactor dead `_run_sequential_inventory_simulation` (superseded by vectorized cumulative approach)
* [ ] `notebooks/01_data_profiling.ipynb` — profile the saved raw dataset

## Planned

* [ ] Data cleaning (`02_data_cleaning.ipynb`) — resolve the injected data-quality issues
* [ ] Inventory KPI calculations
* [ ] Stockout analysis
* [ ] Overstock analysis
* [ ] ABC analysis
* [ ] Inventory aging
* [ ] Replenishment analysis
* [ ] Store/product diagnosis
* [ ] Root-cause analysis
* [ ] SQL Server implementation
* [ ] Power BI dashboard
* [ ] Business recommendations
* [ ] Final portfolio documentation

---

# 🧭 Current Development Roadmap

```text
Actual Sales
     ↓
Actual Demand Calibration ✓
     ↓
Recalibrate Initial Inventory ✓
     ↓
Build Replenishment Logic ✓
     ↓
Calculate Daily Inventory Flow ✓
     ↓
Validate Inventory Continuity ✓
     ↓
Validate Inventory Health ✓
     ↓
Inject Controlled Data-Quality Issues ✓
     ↓
Validate Generated Dataset ✓
     ↓
Save Datasets to CSV ✓
     ↓
Data Profiling (01_data_profiling.ipynb)  ← current
     ↓
Data Cleaning (02_data_cleaning.ipynb)
     ↓
Inventory KPIs
     ↓
Stockout Analysis
     ↓
Overstock Analysis
     ↓
Replenishment Analysis
```

The entire Python data-generation phase of the project is now complete: dimensions, facts, demand calibration, replenishment logic, validation, and persistence. The project now moves from **data engineering** into **data analysis** — starting with profiling the saved dataset.

---

# 💼 Business Value

```text
Raw Data
   ↓
Data Quality
   ↓
Business Metrics
   ↓
Demand Calibration
   ↓
Inventory Diagnosis
   ↓
Root Cause
   ↓
Business Action
```

The goal is not simply to calculate KPIs. The goal is to answer:

> **What is happening? Why is it happening? Which products/stores are affected? What should the retailer do? What business impact could the decision create?**

---

# ⚠️ Data Disclaimer

This project uses **synthetic data** created specifically for portfolio and learning purposes. The locations, customers, products, suppliers, transactions, demand patterns, and financial values do not represent actual GulfMart Retail data or actual company performance. Business assumptions such as Ramadan/Eid periods, demand factors, supplier lead times, promotions, and seasonality are synthetic modeling assumptions.

---

# 👨‍💻 Project Purpose

This project is part of a Retail Analytics portfolio demonstrating practical skills in:

Retail business analysis · Sales analytics · Inventory analytics · Demand analysis · Data quality · Python/Pandas · NumPy · SQL Server · Power BI · KPI development · Business problem solving · Git/GitHub · Data-driven decision making

---

## ⭐ Key Portfolio Question

> **Can data help a retailer keep the right products available at the right stores, reduce excess inventory, improve inventory efficiency, and protect profitability?**

This project is designed to answer that question.
