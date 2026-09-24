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

| Entity                     |                   Volume |
| --------------------------- | -----------------------: |
| Stores                      |                       20 |
| Products                    |                      500 |
| Customers                   |                    5,000 |
| Suppliers                   |                       30 |
| Date Range                  | 2023-01-01 to 2025-12-31 |
| Target Sales Transactions   |                  125,000 |
| Inventory Records (daily)   |               10,960,000 |

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

* `fact_sales` — generated, validated, cleaned, and saved to `data/raw/fact_sales.csv` (raw) / `data/cleaned/fact_sales.csv` (cleaned)
* `fact_inventory` — generated, validated, and saved to `data/raw/fact_inventory.csv.gz` (gzip-compressed, ~10.96M rows); never modified by cleaning (had zero planted issues)

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
│   ├── data_profiling.py
│   ├── inventory_kpis.py
│   ├── stockout_analysis.py
│   ├── overstock_analysis.py
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

The full pipeline is orchestrated end to end through a single entry point:

```python
generate_all_data()
```

which calls every generation stage in sequence, validates the result, persists it to `data/raw/`, and returns all generated tables as a dictionary. Running:

```bash
python src/data_generation.py
```

produces a complete, validated, saved dataset with **no manual steps required**.

---

# 📅 Date Dimension

```text
2023-01-01 → 2025-12-31
```

**1,096 calendar days**, including leap-year coverage for 2024. Includes Date, Year, Quarter, Month, Month Name, Week of Year, Day, Day Name, Day of Week, Weekend Flag, Season, Ramadan Flag, Eid Period Flag.

```text
✓ Date range validated
✓ Calendar generated successfully
✓ 1,096 calendar days
✓ Ramadan and Eid attributes available
```

---

# 🏭 Supplier Dimension

Supplier ID, Name, Region (Local / Regional / International, each with different synthetic lead-time ranges), Lead Time, Minimum Order Quantity, Supplier Status.

```text
✓ 30 suppliers configured
✓ Supplier IDs generated
✓ Supplier regions generated
✓ Lead times generated
✓ Minimum order quantities generated
```

---

# 📦 Product Dimension

Product ID, Name, Category, Subcategory, Brand, Supplier ID, Unit Cost, Selling Price, Product Status, Launch Date, Shelf Life, Demand Class, Demand Trajectory, Base Demand.

**Demand Classes:** Fast-moving · Medium-moving · Slow-moving
**Demand Trajectories:** Growing · Stable · Declining · Volatile
**Categories:** Grocery, Beverages, Personal Care, Household, Electronics, Fashion, Home & Living, Beauty

```text
✓ 500 products generated
✓ Product categories generated
✓ Supplier relationships generated
✓ Pricing attributes generated
✓ Demand classes and trajectories generated
```

---

# 🏪 Store Dimension

Formats: Hypermarket, Supermarket, Express, E-commerce, across Riyadh, Jeddah, Makkah, Madinah, Dammam, Khobar, Tabuk, Abha. Each store has a synthetic demand factor based on store type and region.

```text
✓ 20 stores generated
✓ Store formats and locations generated
✓ Store demand factors generated
```

---

# 👥 Customer Dimension

**5,000 synthetic customers** — Segment, Gender, Age Group, City, Tenure, Preferred Channel, Purchase Frequency Factor, Average Basket Factor, Price Sensitivity.
**Segments:** Premium · Regular · Value · New

```text
✓ 5,000 customers generated, IDs unique
✓ Purchase frequency and basket factors generated
✓ Price sensitivity generated
```

---

# 💰 Sales Fact Table

`fact_sales`: **125,125 transactions generated** → **125,000 after cleaning** (125 planted duplicate transactions removed in `02_data_cleaning.ipynb`).

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
Base Demand × Demand Class × Demand Trajectory × Store Demand
× Customer Behavior × Day-of-Week × Seasonality × Promotion
× Random Variation × Demand Spikes
```

### Promotion & Seasonality Validation

```text
Non-promotion average quantity ≈ 4.35
Promotion average quantity     ≈ 4.97

✓ Summer has the highest average quantity among standard seasons
✓ Ramadan demand is higher than normal-period demand
✓ Eid-period demand is higher than normal-period demand
✓ Ramadan/Eid overlap = 0
```

### Sales Data Validation

```text
Structural: 125,000 transactions, unique IDs, 100% referential integrity
Financial:  Quantity>0, Unit Price>0, all derived calculations verified correct
Business:   Fast-moving (5.29) > Medium-moving (1.67) > Slow-moving (1.51) avg qty
            Promotions generate higher average quantities
            Seasonal / Ramadan / Eid demand uplift present
```

---

# 📦 Inventory Fact Table — Generated, Validated & Saved

`fact_inventory` grain: **one row = one product × one store × one day**

```text
20 stores × 500 products × 1,096 days = 10,960,000 rows
```

```text
Opening Stock + Receipts + Transfers In − Transfers Out − Sales
+ Returns − Damaged Units ± Inventory Adjustments = Closing Stock
```

### Actual Demand Calibration

Theoretical demand (`Base Demand × Store Demand Factor`) overstated real demand, so inventory is calibrated against **observed historical sales**:

```text
Active-Day Demand Rate = Total Historical Sales Units ÷ Number of Active Selling Days
```

used as `demand_rate` for all downstream inventory logic (the sales dataset is sparse relative to the full product-store-day calendar, so calendar-day averaging would understate real demand intensity).

```text
Product-store combinations: 10,000 (7,825 with any sales)
Mean active-day demand rate: 2.33 units/day | Median: 1.75 | Max: 8.39
```

### Recalibrated Initial Inventory & Replenishment Logic

```text
Initial Stock       = Calibrated Demand Rate × Initial Inventory Days (by demand class)
Safety Stock        = Demand Rate × Safety Stock Days (by demand class)
Lead-Time Demand    = Demand Rate × Supplier Lead Time
Reorder Point (ROP) = Lead-Time Demand + Safety Stock
Review-Period Demand= Demand Rate × Replenishment Interval
Target Stock Level  = Lead-Time Demand + Review-Period Demand + Safety Stock
```

Orders trigger only on periodic review dates, respect each supplier's minimum order quantity (MOQ), and convert into receipt events on `order date + lead time`.

```text
Replenishment review events: 818,440
Replenishment orders created: 730,069
Receipt events created: 730,069
```

### Validation Results

```text
✓ Inventory continuity   — 10,950,000 rows checked, 0 failures
✓ Inventory reconciliation — 0 failures
✓ Negative inventory      — 0 rows (0.00%)
✓ Row count matches expected grain — 10,960,000 rows
```

```text
Inventory status:  Healthy 10,926,211 | Low Stock 33,789 | Stockout 0
Events: Replenishment Orders 730,069 | Receipts 722,087 | Sales 122,236
        | Low Stock 33,789 | Stockout 0
```

---

# 🧪 Controlled Data-Quality Injection

`inject_data_quality_issues()` deliberately plants a small, controlled set of issues **after** core generation/validation — not into `fact_inventory`, to avoid contradicting its continuity/reconciliation checks — so `02_data_cleaning.ipynb` has real, known problems to detect and fix.

```text
✓ Missing brand values → dim_product
✓ Missing city values → dim_customer
✓ Inconsistent city text formatting (case + whitespace) → dim_store
✓ Missing supplier_name values → dim_supplier
✓ Duplicate transactions → fact_sales
```

Controlled by `DATA_QUALITY_ISSUE_PROBABILITY` (default 0.1%, scaled up for tiny tables like `dim_store` so issues stay visible).

```text
Latest injection run:
dim_product  : 0 missing brand values
dim_customer : 4 missing city values
dim_store    : 0 inconsistent city text values
dim_supplier : 1 missing supplier_name value
fact_sales   : 125 duplicate transactions
```

Exact counts vary run to run (probability-driven on small tables) — expected variance, not a bug.

---

# 🧪 Automated Dataset Validation

`validate_generated_dataset()` (in `src/data_validation.py`) runs a full suite of structural, financial, business-rule, and inventory-policy checks across every table — 17 checks total, reused identically inside `data_generation.py`, `01_data_profiling.ipynb`, and `02_data_cleaning.ipynb`, so "correctness" always means the same thing everywhere in this project.

**On "DATA VALIDATION FAILED":** when `INJECT_DATA_QUALITY_ISSUES = True` (default), `fact_sales` correctly shows FAIL due to the planted duplicates — expected, not a bug. Validation is intentionally strict and does not auto-suppress known-expected issues (that risk hides real future bugs behind an "expected" label); the FAIL clears once `02_data_cleaning.ipynb` removes the duplicates.

```text
Pre-cleaning run:  14 PASS / 1 FAIL (fact_sales — expected) / 2 REVIEW
Post-cleaning run: 15 PASS / 0 FAIL / 2 REVIEW
```

The 2 REVIEW items (`inventory_reconciliation`, `lost_sales`) are architectural, not defects — they check for `demand_units` / `fulfilled_sales_units` / `lost_sales_units` columns belonging to an earlier row-by-row simulation design this project no longer uses. The current vectorized model reconciles through cumulative closing stock instead, which `inventory_continuity` already confirms holds exactly (0 failures).

Two real bugs were found and fixed during this validation work, documented rather than silently patched:
* `validate_inventory_policy()` had an indentation bug making `expected_rop` unreachable, plus a hardcoded float64-precision tolerance that broke once `fact_inventory` was downcast to float32 for memory efficiency — fixed with `np.isclose(rtol=1e-4, atol=1e-4)`.
* `validate_fact_sales()` always returned `True` regardless of its internal checks (a `numpy.bool_` vs Python `True` identity-check bug in the aggregation loop, plus a bare `return True`) — fixed to properly aggregate with `all(checks)`.

---

# 🛠️ Data Output

```text
data/raw/
├── dim_date.csv, dim_product.csv, dim_store.csv, dim_customer.csv, dim_supplier.csv
├── fact_sales.csv
└── fact_inventory.csv.gz   (gzip-compressed, ~10.96M rows)

data/cleaned/                (written by 02_data_cleaning.ipynb)
├── dim_product.csv, dim_store.csv, dim_customer.csv, dim_supplier.csv
└── fact_sales.csv           (125,000 rows, duplicates removed)
```

`fact_inventory` is gzip-compressed for size; pandas reads it back transparently (`pd.read_csv("data/raw/fact_inventory.csv.gz")`). `downcast_dtypes()` (`src/utils.py`) shrinks numeric dtypes to the smallest safe size for memory efficiency — applied once before saving (peak-RAM benefit) and again after loading in analysis notebooks (the benefit that actually matters day to day, since CSV stores every value as text and does not preserve dtypes across a save/load round trip).

`data/raw/`, `data/cleaned/`, `data/processed/` are excluded from Git via `.gitignore` — only code is versioned, not generated data.

---

# 🧹 Data Profiling & Cleaning

**`01_data_profiling.ipynb`** — profiles all 7 tables (shape, memory, missingness, duplicates, text-formatting consistency via a generic normalize-and-compare scanner in `src/data_profiling.py`) and runs the full validation checkpoint inline. Correctly surfaced every planted issue (4 missing customer cities, 1 missing supplier name, 125 duplicate transactions) plus two legitimate business findings that are *not* data-quality defects: ~21.75% of product-store combinations never recorded a sale, and ~90% of inventory-days carry more than 365 days of coverage.

**`02_data_cleaning.ipynb`** — resolves the planted issues via `src/data_cleaning.py`: missing `dim_customer.city` and `dim_supplier.supplier_name` imputed with clear, traceable placeholders (e.g. `"Unknown Supplier (SUP014)"`); `dim_store.city` text normalized (strip + title case); `fact_sales` duplicates dropped, keeping first occurrence. Every function returns a new DataFrame (never mutates in place) and prints a before/after report. Re-validation after cleaning: **`fact_sales` flips from FAIL to PASS**, overall **15 PASS / 0 FAIL / 2 REVIEW**. `dim_product` and `fact_inventory` are deliberately left untouched — no planted issues to fix.

---

# 📊 Inventory KPI Analysis — Completed (`03_inventory_kpis.ipynb`)

KPIs computed at three grains — **overall, per-product, per-store** — across the full 3-year period via `src/inventory_kpis.py`. Data sources are deliberately mixed: dimensions/`fact_sales` from `data/cleaned/`, `fact_inventory` from `data/raw/` (it was never modified by cleaning, and its `sales_units` already matches the cleaned `fact_sales`).

```text
Inventory Turnover (annualized) = Annualized COGS ÷ Average Inventory Value
Days of Inventory                = 365 ÷ Inventory Turnover
Sell-Through %                   = Units Sold ÷ (Beginning Inventory + Receipts)
GMROI                            = Gross Profit ÷ Average Inventory Value
```

### Headline Result: Severe, Systemic Overstock

```text
Inventory Turnover (annualized): 0.0035   → inventory turns over ~once per 287 years
Days of Inventory:                104,950.50
GMROI:                            0.0044   → <½ cent of gross profit per $1 tied up in inventory
Sell-through:                     0.53%    of everything ever made available actually sold
Stockout rate:                    0.00%
Excess inventory share:           89.95% of inventory-days (row grain), 99.2% of products (grain)
Dead stock:                       21.75% of product-store combinations, zero sales all period
Gross margin:                     29.59% (healthy on its own — irrelevant if inventory never turns)
```

**Store-level pattern:** turnover is not uniform. Hypermarkets/E-commerce cluster at the top (best: STORE014, 0.0064 turnover); Express-format stores cluster at the bottom (~0.0011) — roughly a 6× spread, tracking `STORE_TYPE_DEMAND_FACTORS` (Express 0.55× vs Hypermarket 1.50× demand), suggesting Express stores are allocated inventory disproportionate to actual demand.

**Root cause identified, not just symptom:** every replenishment order is floored at the supplier's minimum order quantity (MOQ, 10–500 units) regardless of how slow-moving the product is. For a product with demand_rate ~0.2–2 units/day, one MOQ-floored order can represent months to years of real demand — and with no markdown/write-off mechanism anywhere in the model, every oversized order compounds permanently across all 1,096 days.

---

# 🚦 Stockout Analysis — Completed (`04_stockout_analysis.ipynb`)

**True stockout events are zero** (confirmed directly: `stockout_event` never True, `closing_stock` never negative, across all 10.96M rows) — for two compounding reasons: (1) *architectural* — `fact_sales` quantities are generated independently of stock on hand, uncapped; (2) *empirical* — the MOQ-driven oversupply above means demand never comes close to exhausting available stock anywhere.

Since real stockouts don't exist, the notebook analyzes the closest real signal — `low_stock_event` (`closing_stock ≤ reorder_point`, still > 0; 33,789 events, 0.31% of rows) — as a near-miss/risk-proximity indicator, via `src/stockout_analysis.py`.

```text
Combinations with ≥1 low-stock day: 2,022 of 10,000 (20.2%)

By demand class: Fast-moving 0.74% of days low-stock (1,077/1,840 combos)
                 Slow-moving  0.00% — ZERO combos ever affected
By supplier lead time: International 1.27% low-stock rate
                       Local          0.0025% low-stock rate
                       → International suppliers show a 500× higher low-stock rate than Local
```

Fast-moving products carry nearly all real risk (they're the only ones that actually consume inventory fast enough to approach reorder point); slow-moving products are structurally incapable of ever getting close, for the same MOQ-oversupply reason that causes their excess.

### What-If Stress Tests (retrospective sensitivity, not a forecast)

```text
Demand spike:        1.5x → 0.54% of combos would go negative
                      2.0x → 7.42%
                      3.0x → 33.74%
                      5.0x → 58.90%
                     10.0x → 73.14%

Safety stock cut:    even a full 100% cut → only 0.01% of combos would go negative
                     (safety stock ≈ 3–7 days of demand; dwarfed by MOQ-floored
                      base inventory representing months-to-years of demand —
                      safety-stock policy is structurally irrelevant here; MOQ
                      sizing is the real lever)
```

**Overall read:** no current stockout problem, but real, quantified latent fragility to demand shocks (2–3× is not an extreme scenario) concentrated in fast-moving, internationally-supplied products.

---

# 📦 Overstock Analysis — Completed (`05_overstock_analysis.ipynb`)

Excess is defined against the inventory model's **own replenishment policy target**, not an external threshold — a meaningfully stronger basis than a fixed day-count cutoff:

```text
Excess Units = max(closing_stock − target_stock_level, 0)
Excess Value = Excess Units × unit_cost
```

Implemented in `src/overstock_analysis.py`.

```text
Average daily total inventory value: $12.65B
Average daily total excess value:    $12.52B
Excess as % of total inventory value: 99.04%
```

**Worst offenders:** top product PROD0132 (Laundry, Fast-moving, ~$247M avg excess value); top store STORE015 (Hypermarket, Western, ~$699M avg excess value). Notably, **PROD0367** (repeatedly flagged in stockout analysis as closest to a real stockout) does **not** appear among top overstock offenders — a meaningful cross-notebook consistency check: the products most at risk of running out and the products drowning in excess are, correctly, different products.

**Concentration:** 153 of 500 products (30.6%) account for 80% of total average excess value — feeds directly into `06_abc_analysis.ipynb`.

**MOQ attribution — measured directly, not estimated:**

```text
Total replenishment orders: 730,069
Orders inflated above target by MOQ: 368,128 (50.4%)
Total order-time overshoot value: $12.67B
```

**Capital recapture — retrospective counterfactual, explicitly not a forecast** (does not model how smaller historical orders would have changed subsequent days' closing stock or future reorder timing/sizing):

```text
Cap at 1.5x target: ~$10.17B would have been avoided (order-time, retrospective)
Cap at 2.0x target: ~$8.36B
Cap at 3.0x target: ~$5.82B
Cap at 5.0x target: ~$2.83B
```

**Overall read:** overstock here is not diffuse — it's a near-total condition (99% of inventory value) with a specific, directly-measured mechanism (MOQ flooring, $12.67B of overshoot) and a moderately concentrated distribution (30.6% of products driving 80% of excess). MOQ policy reform, targeted first at the top ~150 products, is the highest-leverage intervention identified so far.

---

# 🔎 Business Analysis — Answered So Far

**Inventory Availability** — *Answered (04):* real stockouts are zero; latent risk is concentrated in fast-moving, internationally-supplied products, fragile to 2–3×+ demand shocks.

**Excess Inventory** — *Answered (03, 05):* 99.04% of inventory value is excess above policy target; concentrated in ~31% of products (153 of 500) driving 80% of excess value; root cause is MOQ flooring, measured at $12.67B in order-time overshoot.

**Product Analysis** — *Partially answered:* worst overstock offenders identified by name (05); full profitability-vs-availability cross-analysis still pending ABC/replenishment notebooks.

**Store Analysis** — *Partially answered:* turnover and excess both vary meaningfully by store type/region (03, 05); store-to-store transfer recommendations still pending.

**Supplier Analysis** — *Answered (04):* International (long lead-time) suppliers show a 500× higher low-stock rate than Local suppliers.

**Replenishment** — *Pending `07_replenishment_analysis.ipynb`:* reorder prioritization and safety-stock recommendations.

---

# 📊 ABC Analysis — In Progress (`06_abc_analysis.ipynb`)

```text
A → Highest-value products
B → Medium-value products
C → Lower-value products
```

Goal: not "which products sell the most" but **"which products deserve the most inventory-management attention."** Will formalize the 153-products-drive-80%-of-excess-value concentration pattern already surfaced in `05_overstock_analysis.ipynb` into a full classification across the entire 500-product catalog.

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

The project is developed incrementally using Git, with each stage validated before the next. Code and its corresponding README update are committed together as a single unit of change.

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
Add data_profiling.py and 01_data_profiling.ipynb
Fix inventory column-name mismatch and PASS/FAIL/REVIEW scoring bug in data_validation.py
Add data_cleaning.py and 02_data_cleaning.ipynb
Add inventory_kpis.py and 03_inventory_kpis.ipynb — identifies systemic overstock
Fix magnitude-aware KPI display formatting (turnover/GMROI no longer round to 0.00)
Add stockout_analysis.py and 04_stockout_analysis.ipynb — confirms zero true stockouts, quantifies latent risk
Add overstock_analysis.py and 05_overstock_analysis.ipynb — quantifies 99%+ excess inventory, measures MOQ attribution
```

### Current Development Milestone

```text
06_abc_analysis.ipynb — formalize the overstock concentration pattern
(153 of 500 products drive 80% of excess value) into a full ABC
classification across the product catalog
```

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
* [x] `validate_generated_dataset()` — automated structural/financial/business/data-quality checks
* [x] `save_datasets()` — persist all generated tables to `data/raw/` (CSV, `fact_inventory` gzip-compressed)
* [x] Fixed `validate_inventory_policy()` indentation bug + float32 tolerance (`np.isclose`)
* [x] Fixed `validate_fact_sales()` to correctly aggregate its own check results
* [x] `downcast_dtypes()` utility (`src/utils.py`) — applied at save time and at analysis-load time
* [x] `01_data_profiling.ipynb` — full profiling of all 7 tables, validation checkpoint
* [x] `02_data_cleaning.ipynb` — resolves all planted data-quality issues, re-validates clean (15 PASS / 0 FAIL / 2 REVIEW)
* [x] `03_inventory_kpis.ipynb` — overall/product/store KPIs; identifies systemic overstock (turnover 0.0035, GMROI 0.0044, 99.2% of products excess inventory) with MOQ-vs-demand mismatch as root cause
* [x] `04_stockout_analysis.ipynb` — confirms zero true stockouts; identifies fast-moving + long-lead-time products as the real (currently latent) risk concentration; demand-spike stress test shows real fragility at 3×+ demand; safety-stock cuts shown structurally irrelevant
* [x] `05_overstock_analysis.ipynb` — quantifies excess against the model's own `target_stock_level` policy (99.04% of inventory value is excess); measures MOQ attribution directly (50.4% of replenishment orders inflated, $12.67B overshoot); retrospective capital-recapture estimate (~$8.36B at a 2× MOQ cap); 153 of 500 products (30.6%) drive 80% of excess value

## In Progress

* [ ] `06_abc_analysis.ipynb`

## Planned

* [ ] Inventory aging
* [ ] `07_replenishment_analysis.ipynb`
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
Data Profiling (01_data_profiling.ipynb) ✓
     ↓
Data Cleaning (02_data_cleaning.ipynb) ✓
     ↓
Inventory KPIs (03_inventory_kpis.ipynb) ✓
     ↓
Stockout Analysis (04_stockout_analysis.ipynb) ✓
     ↓
Overstock Analysis (05_overstock_analysis.ipynb) ✓
     ↓
ABC Analysis (06_abc_analysis.ipynb)  ← current
     ↓
Replenishment Analysis (07_replenishment_analysis.ipynb)
```

The entire Python data-generation phase is complete: dimensions, facts, demand calibration, replenishment logic, validation, and persistence. Data profiling and cleaning are complete, producing a validated, trustworthy dataset (15 PASS / 0 FAIL / 2 REVIEW). Core inventory analysis is well underway: KPIs established systemic overstock as the dominant finding (turnover ~0.0035, GMROI ~0.0044); stockout analysis confirmed zero true stockouts while identifying fast-moving/long-lead-time products as the real latent risk; overstock analysis quantified the problem precisely — 99.04% of inventory value is excess above policy target, with 50.4% of replenishment orders directly measured as MOQ-inflated ($12.67B overshoot). The project now moves into **ABC analysis**, formalizing the 30.6%-of-products-drive-80%-of-excess concentration pattern already surfaced, before closing the analytical arc with replenishment recommendations.

---

# 💼 Business Value

```text
Raw Data → Data Quality → Business Metrics → Demand Calibration
→ Inventory Diagnosis → Root Cause → Business Action
```

The goal is not simply to calculate KPIs. The goal is to answer:

> **What is happening? Why is it happening? Which products/stores are affected? What should the retailer do? What business impact could the decision create?**

This project's clearest answer so far: inventory turnover is near-zero (0.0035, ~287-year turn cycle) and 99.04% of inventory value is excess — caused specifically by supplier MOQ flooring (measured at $12.67B in order-time overshoot, concentrated in 153 of 500 products) — with a defensible retrospective estimate that capping MOQ enforcement at 2× policy target would have avoided roughly $8.36B of that overshoot.

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

This project is designed to answer that question — and has, so far, found and precisely quantified a severe, mechanistically-explained overstock problem as the primary answer.
