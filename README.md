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

The project uses a dimensional/star-schema-oriented structure, implemented identically in both Python (pandas DataFrames) and SQL Server.

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

* `fact_sales` — generated, validated, cleaned, and saved to `data/raw/fact_sales.csv` (raw) / `data/cleaned/fact_sales.csv` (cleaned); loaded into SQL Server with `is_ramadan`/`is_eid_period` carried through directly
* `fact_inventory` — generated, validated, and saved to `data/raw/fact_inventory.csv.gz` (gzip-compressed, ~10.96M rows); never modified by cleaning (had zero planted issues); loaded into SQL Server via `src/sql_loader.py` only (no `.sql` script reloads it — see SQL Server section)

#### Derived / Analytical Output

* `data/processed/replenishment_action_list.csv` — one row per product-store combination, the Python phase's final actionable deliverable (see `07_replenishment_analysis.ipynb`)

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
│   ├── abc_analysis.py
│   ├── replenishment_analysis.py
│   ├── sql_loader.py
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

**Known quirk, inherited from the generator:** `dim_date.is_ramadan`/`is_eid_period` are hardcoded to `False` for every row in `generate_dim_date()` — the real per-day Ramadan/Eid determination only ever happens inline inside `generate_fact_sales()`, stored there instead. `dim_date`'s own flags are therefore not usable for calendar-level Ramadan/Eid analysis; the SQL Server phase works around this by carrying the real flags on `fact_sales` directly.

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

**Important, discovered in `07_replenishment_analysis.ipynb`:** the order-quantity logic sets `planned_order_quantity = target_stock_level` (MOQ-floored) on every review date — it does **not** subtract existing on-hand stock first. This means every replenishment cycle re-orders the full target amount on top of whatever is already there, rather than ordering only the shortfall. See the Replenishment Analysis section below for the measured impact.

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

# 🧪 Automated Dataset Validation (Python)

`validate_generated_dataset()` (in `src/data_validation.py`) runs a full suite of structural, financial, business-rule, and inventory-policy checks across every table — 17 checks total, reused identically inside `data_generation.py`, `01_data_profiling.ipynb`, and `02_data_cleaning.ipynb`.

```text
Pre-cleaning run:  14 PASS / 1 FAIL (fact_sales — expected) / 2 REVIEW
Post-cleaning run: 15 PASS / 0 FAIL / 2 REVIEW
```

The 2 REVIEW items (`inventory_reconciliation`, `lost_sales`) are architectural, not defects — they check for columns belonging to an earlier row-by-row simulation design this project no longer uses.

Bugs found and fixed during this validation work, documented rather than silently patched:
* `validate_inventory_policy()` had an indentation bug making `expected_rop` unreachable, plus a hardcoded float64-precision tolerance that broke once `fact_inventory` was downcast to float32 — fixed with `np.isclose(rtol=1e-4, atol=1e-4)`.
* `validate_fact_sales()` always returned `True` regardless of its internal checks — fixed to properly aggregate with `all(checks)`.
* `summarize_excess_by()` only supported a single grouping column — fixed to accept either a string or a list.

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

data/processed/               (written by 07_replenishment_analysis.ipynb)
└── replenishment_action_list.csv   (10,000 rows — one per product-store combination)
```

`data/raw/`, `data/cleaned/`, `data/processed/` are excluded from Git via `.gitignore` — only code is versioned, not generated data.

---

# 🧹 Data Profiling & Cleaning

**`01_data_profiling.ipynb`** — profiles all 7 tables and runs the full validation checkpoint inline. Correctly surfaced every planted issue plus two legitimate business findings that are *not* data-quality defects: ~21.75% of product-store combinations never recorded a sale, and ~90% of inventory-days carry more than 365 days of coverage.

**`02_data_cleaning.ipynb`** — resolves the planted issues via `src/data_cleaning.py`. Re-validation after cleaning: **`fact_sales` flips from FAIL to PASS**, overall **15 PASS / 0 FAIL / 2 REVIEW**.

---

# 📊 Inventory KPI Analysis — Completed (`03_inventory_kpis.ipynb`)

KPIs computed at three grains — **overall, per-product, per-store** — across the full 3-year period via `src/inventory_kpis.py`.

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
Sell-through:                     0.53%
Stockout rate:                    0.00%
Excess inventory share:           89.95% of inventory-days, 99.2% of products
Dead stock:                       21.75% of product-store combinations
Gross margin:                     29.59%
```

**Root cause identified (Stage 1 of 3):** every replenishment order is floored at the supplier's minimum order quantity (MOQ), regardless of how slow-moving the product is.

---

# 🚦 Stockout Analysis — Completed (`04_stockout_analysis.ipynb`)

**True stockout events are zero** — architectural (demand generation is uncapped by stock on hand) and empirical (MOQ-driven oversupply means demand never exhausts supply) reasons.

```text
Combinations with ≥1 low-stock day: 2,022 of 10,000 (20.2%)
Fast-moving 0.74% of days low-stock | Slow-moving 0.00% — ZERO combos ever affected
International suppliers: 1.27% low-stock rate | Local: 0.0025% — ~500× higher for International
```

### What-If Stress Tests (retrospective, not a forecast)

```text
Demand spike:  1.5x → 0.54% | 2.0x → 7.42% | 3.0x → 33.74% | 5.0x → 58.90% | 10.0x → 73.14%
Safety stock cut: even 100% cut → only 0.01% would go negative (structurally irrelevant)
```

---

# 📦 Overstock Analysis — Completed (`05_overstock_analysis.ipynb`)

```text
Excess Units = max(closing_stock − target_stock_level, 0)
Excess Value = Excess Units × unit_cost
```

```text
Excess as % of total inventory value: 99.04%
Concentration: 153 of 500 products (30.6%) drive 80% of excess value
```

**Root cause (Stage 2 of 3) — measured:**

```text
Orders inflated above target by MOQ: 368,128 of 730,069 (50.4%)
Total order-time overshoot value: $12.67B
```

Independently cross-validated in T-SQL — see `sql/07_overstock_analysis.sql` in the SQL Server section below.

---

# 📊 ABC Analysis — Completed (`06_abc_analysis.ipynb`)

```text
Class A:  51 products (10.2%) → 79.4% of annual COGS
Excess tier: High 152 | Medium 132 | Low 216 (matches 05's 153-product finding)
```

**Priority Matrix:** 96% of Class A products (49 of 51) fall in the High excess tier — excess is concentrated in the business's own most important products.

---

# 🔁 Replenishment Analysis — Completed, Python-Phase Capstone (`07_replenishment_analysis.ipynb`)

**Root cause (Stage 3 of 3 — deepest, most complete):** `planned_order_quantity = target_stock_level` on every review date, **without netting against existing stock**.

```text
Orders that should not have been placed at all: 719,348 of 730,069 (98.5%)
Total netting overshoot value: $25.30B — exactly 2.00x the MOQ-only figure
```

**Replenishment Action List:**

```text
MAINTAIN 57.8% | SUPPRESS 19.0% | REDUCE 17.4% | EXPEDITE 5.8%
SUPPRESS + REDUCE recoverable: $14.60B (retrospective, risk-aware)
```

Saved as `data/processed/replenishment_action_list.csv` (10,000 rows).

---

# 🔎 Business Analysis — Answered

**Inventory Availability** — zero real stockouts; latent risk in fast-moving, internationally-supplied products.
**Excess Inventory** — 99.04% of value excess; root cause fully diagnosed (no inventory-position netting, $25.30B overshoot); 96% of Class A is high-excess.
**Product Analysis** — worst offenders named; full ABC × excess-tier segmentation; final per-combo recommendations.
**Store Analysis** — partially answered (turnover/excess vary by type/region; transfer recommendations not yet built).
**Supplier Analysis** — International suppliers show 500× higher low-stock rate than Local.
**Replenishment** — concrete SUPPRESS/REDUCE/MAINTAIN/EXPEDITE recommendations for all 10,000 combinations.

---

# 🗄️ SQL Server Implementation — In Progress

The Python phase is complete and produced a validated, trustworthy dataset. This phase rebuilds the storage layer in SQL Server and re-expresses the core analytical queries behind the Python findings in T-SQL — each one independently cross-validated against its notebook counterpart.

### Schema Design Decisions

**Natural keys**, not surrogate `IDENTITY` keys — the Python pipeline already produces stable, unique, deterministic IDs, so surrogate-key ETL complexity wasn't judged worth it.

**`fact_sales` uses a staging + transform pattern.** `staging_fact_sales` mirrors the raw CSV exactly; the final `fact_sales` table keeps true fact-grain keys/measures plus `is_ramadan`/`is_eid_period` (kept as genuine business facts, not generation scaffolding — see "Bugs Found").

**`fact_inventory` has no staging table and no `.sql` reload path** — it is loaded exclusively via `src/sql_loader.py` (pyodbc + `fast_executemany`, chunked). `sql/02_create_tables.sql` now carries an explicit top-of-file warning that running the full script drops and empties `fact_inventory`, after this happened twice during development (see "Bugs Found").

### Hybrid Loading Strategy

```text
dim_date, dim_supplier, dim_product, dim_store, dim_customer, fact_sales
    → T-SQL BULK INSERT (sql/03_load_data.sql)
fact_inventory (10.96M rows)
    → Python loader, pyodbc + fast_executemany, chunked (src/sql_loader.py)
```

`fact_inventory.csv.gz` is gzip-compressed; `BULK INSERT` cannot read gzip directly, and decompressing + fighting SQL Server file-permission issues on a single large file was judged not worth it versus a scripted loader.

### Bugs Found and Fixed — Documented, Not Silently Patched

* **Boolean columns as text:** pandas writes `bool` to CSV as literal `True`/`False`; `BULK INSERT` can't convert that to `BIT` directly. Fixed via `VARCHAR(5)` staging columns + `CASE WHEN` conversion.
* **`ROWTERMINATOR` mismatch:** CSVs use CRLF; `'0x0a'` (LF only) left a stray `\r` on every row's last column, silently tolerated by numeric columns but not `VARCHAR`. Fixed to `'0x0d0a'` everywhere.
* **Duplicate/conflicting INSERT statements:** an editing mistake produced two `staging_fact_sales → fact_sales` transforms; caught via a primary-key violation.
* **`fact_sales` missing `is_ramadan`/`is_eid_period`:** initially dropped as "generation-only intermediates." Surfaced when `04_data_validation.sql`'s Ramadan/Eid checks returned blank `NULL` averages — traced to `dim_date`'s own flags being permanently `False` (a pre-existing Python-generator quirk). Fixed by adding the columns to `fact_sales` and backfilling from staging.
* **Inventory-policy tolerance:** `fact_inventory` was downcast to float32 before being saved; a flat `ABS() > 0.01` check produced 2,192 and 3,288 false "failures" purely from rounding. Fixed with a combined absolute + relative tolerance, matching the `np.isclose()` fix already applied on the Python side.
* **`fact_inventory` emptied twice during development:** once by an interrupted `sql_loader.py` re-run (left exactly 93 complete 50,000-row chunks = 4,650,000 rows, not an error), once by re-running the full `02_create_tables.sql` after the table was already loaded (which `DROP`s and recreates every table). Both caught only by explicit row-count verification, not by any exception — reinforcing why `sql_loader.py` and `04_data_validation.sql` both verify row counts independently on every run, and why `02_create_tables.sql` now carries an explicit warning comment.
* **`days_of_inventory` / `low_stock_pct` excess decimal precision:** SQL Server's `DECIMAL` division produced 20-30+ digit results (correct but unusable for display/Power BI). Wrapped in `ROUND(..., 2)` / `ROUND(..., 4)`.
* **Password handling:** `sql_loader.py` reads the SQL Server password from the `SQL_PASSWORD` environment variable, set per-terminal-session, never hardcoded or committed to Git.

### Verified Load — Final Row Counts

```text
dim_date 1,096 | dim_supplier 30 | dim_product 500 | dim_store 20
dim_customer 5,000 | fact_sales 125,000 | fact_inventory 10,960,000
```

### SQL-Side Data Validation (`sql/04_data_validation.sql`)

Not a 1:1 port of the Python validator — SQL Server's `PRIMARY KEY`/`FOREIGN KEY` constraints already make duplicate keys and orphaned foreign keys physically impossible to load, so this script validates what the schema *cannot* auto-guarantee (row counts, financial-formula correctness, business behavior, inventory reconciliation/continuity, inventory-policy formulas) while separately confirming the schema's own guarantees exist via the system catalog.

```text
40 PASS / 0 FAIL / 2 INFO
```

Low-stock events (33,789) and every financial/reconciliation/continuity/policy check match the Python-side findings exactly.

### SQL-Side Inventory KPIs (`sql/05_inventory_kpis.sql`)

Direct T-SQL port of `03_inventory_kpis.ipynb`'s overall/product/store KPIs, same formulas and annualization convention. `beginning_inventory_units` (Python's `initial_opening_stock`, never persisted as its own column) is recovered via `ROW_NUMBER() OVER (PARTITION BY store_id, product_id ORDER BY [date])` — each combo's `opening_stock` on its earliest date, exactly how the Python simulation seeded it.

```text
Turnover: 0.003478 (Python: 0.0035) | GMROI: 0.004389 (Python: 0.0044)
Sell-through: 0.528% (Python: 0.53%) | Dead stock: 21.75% (exact match)
Excess share: 89.95% (exact match) | Store ranking: same order as Python (STORE014 best)
```

### SQL-Side Stockout Analysis (`sql/06_stockout_analysis.sql`)

Direct T-SQL port of `04_stockout_analysis.ipynb`'s near-miss risk breakdowns and both stress tests. Stress tests use a `CROSS JOIN` against a small `VALUES` table of factors, aggregated with conditional `SUM` — every scenario computed in one set-based query instead of a loop, the idiomatic SQL equivalent of the Python version's per-factor iteration.

```text
Combinations with low-stock exposure: 2,022 of 10,000 (exact match)
Fast-moving 0.74% | Slow-moving 0.00% (exact match)
International 1.27% vs Local 0.0025% — ~500x gap (exact match)
Demand spike: 0.55/7.41/33.74/58.91/73.14% (Python: 0.54/7.42/33.74/58.90/73.14%)
Safety stock cut: 0/0/0/1 combo at 25/50/75/100% cut (exact match)
```

### SQL-Side Overstock Analysis (`sql/07_overstock_analysis.sql`)

Direct T-SQL port of `05_overstock_analysis.ipynb`: row-level excess value against `target_stock_level`, worst-offender rankings (product and store, all 20), category breakdown, Pareto concentration via a window-function running total (`SUM(...) OVER (ORDER BY ... ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` — the T-SQL equivalent of pandas' `.cumsum()`), MOQ root-cause attribution, and the capital-recapture what-if (same `CROSS JOIN`-against-`VALUES` set-based technique as the stress tests in `06`).

```text
Excess share: 99.04% (exact match) | Top product: PROD0132, $247.06M avg excess (exact match)
Top store: STORE015, $698.57M avg excess (exact match)
Pareto: 153 of 500 products (30.6%) for 80% of excess (exact match)
MOQ attribution: 50.42% of orders, $12.67B overshoot (exact match)
Capital recapture at 2x cap: $8.33B (Python: $8.36B)
```

The strongest cross-validation run of the SQL phase — the top-15 product ranking matches the Python notebook's ranking in the same order, product for product.

Four independent T-SQL scripts in a row (`04`, `05`, `06`, `07`) now reproduce the Python phase's findings essentially exactly, on the same 10.96M-row dataset — strong evidence the analysis reflects a real property of the data, not an artifact of one tool's implementation.

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
| pyodbc      | Python → SQL Server bulk loading     |
| Power BI    | Dashboard & reporting                |
| DAX         | BI calculations                      |
| Power Query | Data transformation                  |
| Git         | Version control                      |
| GitHub      | Portfolio & project collaboration    |
| VS Code     | Development environment              |
| Jupyter     | Exploratory analysis                 |

---

# 🔄 Hybrid Analytics Architecture

**Python** — synthetic data generation, profiling, cleaning, complex transformations, statistical/demand/inventory modeling. *Complete.*
**SQL Server** — structured storage, validation, KPIs, and stockout analysis complete; overstock/replenishment queries in progress.
**Power BI** — KPI dashboards, inventory health monitoring, store/product analysis, stockout visualization, management reporting. *Next phase.*

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
Add abc_analysis.py and 06_abc_analysis.ipynb — ABC x excess-tier priority matrix, finds 96% of Class A is high-excess
Fix summarize_excess_by() to support multi-column grain
Add replenishment_analysis.py and 07_replenishment_analysis.ipynb — netting root cause (2x MOQ, 98.5% unnecessary orders), final action list ($14.6B recoverable)
SQL Server: create database, star-schema tables (natural keys), BULK INSERT load for dims + fact_sales
Add sql_loader.py: pyodbc chunked loader for fact_inventory (10.96M rows, fast_executemany)
SQL Server validation (40/40 PASS): fix fact_sales missing is_ramadan/is_eid_period, fix inventory-policy tolerance for float32-downcast data
Add sql/05_inventory_kpis.sql — cross-validated against 03_inventory_kpis.ipynb; round days_of_inventory; add fact_inventory-wipe warning to 02_create_tables.sql
Add sql/06_stockout_analysis.sql — near-miss breakdowns and stress tests, cross-validated against 04_stockout_analysis.ipynb
Add sql/07_overstock_analysis.sql — excess value, worst offenders, Pareto, MOQ attribution, capital recapture, cross-validated against 05_overstock_analysis.ipynb (near-exact match on every figure)
```

### Current Development Milestone

```text
sql/08_replenishment_analysis.sql — re-express 07_replenishment_analysis.ipynb's
deepest root-cause measurement (inventory-position netting) and the final
Replenishment Action List as T-SQL, closing out the SQL Server phase
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
* [x] `downcast_dtypes()` utility (`src/utils.py`)
* [x] `01_data_profiling.ipynb`
* [x] `02_data_cleaning.ipynb` — re-validates clean (15 PASS / 0 FAIL / 2 REVIEW)
* [x] `03_inventory_kpis.ipynb` — identifies systemic overstock (turnover 0.0035, GMROI 0.0044)
* [x] `04_stockout_analysis.ipynb` — confirms zero true stockouts; quantifies latent risk
* [x] `05_overstock_analysis.ipynb` — quantifies excess (99.04%); measures MOQ attribution ($12.67B)
* [x] `06_abc_analysis.ipynb` — finds 96% of Class A products carry high excess
* [x] Fixed `summarize_excess_by()` to support multi-column grain
* [x] `07_replenishment_analysis.ipynb` — deepest root cause (netting flaw, $25.30B, 98.5% unnecessary orders); final Replenishment Action List ($14.60B recoverable); saved as `data/processed/replenishment_action_list.csv`
* [x] `sql/01_create_database.sql`
* [x] `sql/02_create_tables.sql` — star-schema tables, natural keys, staging pattern, `is_ramadan`/`is_eid_period` on `fact_sales`, fact_inventory-wipe warning
* [x] `sql/03_load_data.sql` — BULK INSERT load for dims + fact_sales, all row counts verified
* [x] `src/sql_loader.py` — pyodbc chunked loader for `fact_inventory` (10,960,000 rows verified, ~15,700 rows/sec)
* [x] `sql/04_data_validation.sql` — 40/40 checks PASS (2 INFO), cross-validates every Python-phase finding independently in T-SQL
* [x] `sql/05_inventory_kpis.sql` — cross-validated against `03_inventory_kpis.ipynb` (turnover, GMROI, sell-through, dead stock, excess share all match)
* [x] `sql/06_stockout_analysis.sql` — cross-validated against `04_stockout_analysis.ipynb` (low-stock exposure, lead-time risk, both stress tests all match)
* [x] `sql/07_overstock_analysis.sql` — cross-validated against `05_overstock_analysis.ipynb` (excess share, worst offenders, Pareto concentration, MOQ attribution, capital recapture all match)

## In Progress

* [ ] `sql/08_replenishment_analysis.sql`

## Planned

* [ ] Inventory aging
* [ ] Store/product diagnosis (store-to-store transfer recommendations)
* [ ] Power BI dashboard
* [ ] Business recommendations (`docs/business_recommendations.md`)
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
ABC Analysis (06_abc_analysis.ipynb) ✓
     ↓
Replenishment Analysis (07_replenishment_analysis.ipynb) ✓
     ↓
SQL Server: Database + Tables + Data Load ✓
     ↓
SQL Server: Data Validation (sql/04_data_validation.sql) ✓ — 40/40 PASS
     ↓
SQL Server: Inventory KPIs (sql/05_inventory_kpis.sql) ✓ — cross-validated
     ↓
SQL Server: Stockout Analysis (sql/06_stockout_analysis.sql) ✓ — cross-validated
     ↓
SQL Server: Overstock Analysis (sql/07_overstock_analysis.sql) ✓ — cross-validated
     ↓
SQL Server: Replenishment Queries (sql/08_replenishment_analysis.sql)  ← current
     ↓
Power BI Dashboard
     ↓
Business Recommendations
```

**The entire Python data-generation and analytical phase of this project is complete.** SQL Server implementation now has a fully loaded, fully validated database, with four consecutive analytical scripts (`04` data validation, `05` KPIs, `06` stockout analysis, `07` overstock analysis) independently reproducing the Python phase's findings to a very close — in several cases exact — match, including specific product and store names ranking identically in both stacks. This is strong, repeated evidence that the project's conclusions reflect a real property of the dataset, not an artifact of any one tool. Several real bugs were found and fixed throughout the SQL phase, all documented rather than silently patched, consistent with this project's approach throughout. The project now moves into the final analytical script — replenishment — before Power BI.

---

# 💼 Business Value

```text
Raw Data → Data Quality → Business Metrics → Demand Calibration
→ Inventory Diagnosis → Root Cause → Business Action
```

This project's fullest answer: inventory turnover is near-zero (0.0035, ~287-year turn cycle) and 99.04% of inventory value is excess — caused specifically by a replenishment policy that never nets new orders against existing stock (98.5% of historical orders should not have been placed at all, $25.30B in measured overshoot), compounded by supplier MOQ flooring, and concentrated overwhelmingly in the business's own most important products (96% of Class A). The project closes its Python phase with a concrete, risk-aware, per-product-store action list — $14.60B retrospectively recoverable through SUPPRESS/REDUCE actions alone — and this same diagnosis is now independently confirmed, repeatedly, in a live SQL Server database, on its way toward a Power BI dashboard.

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

This project answers that question with a fully traced, three-level root-cause diagnosis and a concrete, saved, actionable deliverable — independently cross-validated, repeatedly, across two different technology stacks (Python/pandas and SQL Server/T-SQL) — and is now being carried into Power BI to demonstrate the same analysis in a production-style stack.
