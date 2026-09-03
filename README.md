
# Retail Inventory Analytics

## GulfMart Retail — Inventory Availability, Efficiency & Replenishment Analytics

> **Portfolio Project | Retail Analytics | Python | Pandas | SQL Server | Power BI**

---

## 📌 Project Overview

This project analyzes inventory performance for a fictional GCC retailer, **GulfMart Retail**, with the objective of improving inventory availability, reducing excess stock, and supporting better replenishment decisions.

The project is being developed as an end-to-end **Retail Inventory Analytics** solution using:

* Python / Pandas for data generation, profiling, cleaning, and analytical preparation
* SQL Server for structured data storage and business analysis
* Power BI for interactive reporting and decision-making
* Git/GitHub for version control and portfolio presentation

The project uses a realistic synthetic retail dataset designed around GCC retail business scenarios.

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
SQL Server
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
Power BI Dashboard
       ↓
Business Recommendations
```

---

# 📊 Dataset

The project uses a synthetic dataset representing a GCC retail business.

### Current Dataset Scope

| Entity                    |                   Volume |
| ------------------------- | -----------------------: |
| Stores                    |                       20 |
| Products                  |                      500 |
| Customers                 |                    5,000 |
| Suppliers                 |                       30 |
| Date Range                | 2023-01-01 to 2025-12-31 |
| Target Sales Transactions |                  125,000 |

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

* `fact_sales`
* `fact_inventory` *(in progress)*

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

---

# 📅 Date Dimension

The project currently generates a date dimension covering:

```text
2023-01-01 → 2025-12-31
```

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

These fields will later support:

* Seasonal inventory analysis
* Monthly trends
* Ramadan analysis
* Eid analysis
* Year-over-year analysis
* Demand trend analysis

---

# 🏭 Supplier Dimension

The supplier dimension currently models:

* Supplier ID
* Supplier Name
* Supplier Region
* Lead Time
* Minimum Order Quantity
* Supplier Status

Supplier regions include:

* Local
* Regional
* International

Different supplier regions are assigned different synthetic lead-time ranges.

This will later support:

* Replenishment analysis
* Lead-time risk
* Supplier performance
* Safety-stock calculations
* Reorder-point analysis

---

# 📦 Product Dimension

The product dimension currently contains:

* Product ID
* Product Name
* Category
* Subcategory
* Brand
* Supplier
* Unit Cost
* Selling Price
* Product Status
* Product Launch Date
* Shelf Life
* Demand Class
* Demand Trajectory
* Base Demand

### Demand Classes

Products are classified into:

```text
Fast-moving
Medium-moving
Slow-moving
```

with different demand behavior.

### Demand Trajectories

Products can have:

```text
Growing
Stable
Declining
Volatile
```

These attributes will later support inventory prioritization and demand analysis.

---

# 🏪 Store Dimension

The store dimension currently models different retail formats:

* Hypermarket
* Supermarket
* Express
* E-commerce

Stores are distributed across synthetic GCC/Saudi-oriented locations including:

* Riyadh
* Jeddah
* Makkah
* Madinah
* Dammam
* Khobar
* Tabuk
* Abha

Each store receives a synthetic demand factor based on:

* Store type
* Region
* Retail format

This will later support:

* Store-level inventory analysis
* Stockout analysis
* Store-to-store comparisons
* Replenishment prioritization

---

# 👥 Customer Dimension

The customer dimension currently contains 5,000 synthetic customers.

Customer attributes include:

* Customer ID
* Customer Segment
* Gender
* Age Group
* City
* Customer Start Date
* Customer Tenure
* Preferred Channel
* Purchase Frequency Factor
* Average Basket Factor
* Price Sensitivity

Customer segments include:

```text
Premium
Regular
Value
New
```

These attributes will eventually support customer-driven demand analysis.

---

# 💰 Sales Fact Table

The `fact_sales` generation is currently completed and validated.

### Current Volume

```text
125,000 transactions
```

Each transaction contains:

* Transaction ID
* Transaction Date
* Product ID
* Store ID
* Customer ID
* Quantity
* Unit Price
* Discount
* Gross Sales
* Net Sales
* COGS
* Gross Profit

The generated sales model also contains analytical helper attributes such as:

* Demand Class
* Demand Trajectory
* Demand Intensity
* Season
* Day-of-week factor
* Seasonality factor
* Promotion Flag
* Demand Spike Flag

---

# 📈 Sales Calculation Logic

### Gross Sales

```text
Gross Sales = Quantity × Unit Price
```

### Discount Amount

```text
Discount Amount = Gross Sales × Discount %
```

### Net Sales

```text
Net Sales = Gross Sales − Discount Amount
```

### COGS

```text
COGS = Quantity × Unit Cost
```

### Gross Profit

```text
Gross Profit = Net Sales − COGS
```

These calculations have been programmatically validated.

---

# 🧠 Demand Modeling

The sales generator models demand using multiple business factors.

Conceptually:

```text
Base Demand
     ×
Demand Class
     ×
Demand Trajectory
     ×
Store Demand
     ×
Customer Behavior
     ×
Day-of-Week
     ×
Seasonality
     ×
Promotion
     ×
Random Variation
     ×
Demand Spikes
```

This creates more realistic demand behavior than assigning completely random sales quantities.

---

# 🏷️ Promotion Modeling

Synthetic promotions are included in the sales model.

Promotions have:

* Promotion flag
* Discount percentage
* Demand lift

The current model applies a synthetic demand lift to promotional transactions.

Validation confirmed that promotional transactions have higher average quantities than non-promotional transactions.

Current validation:

```text
Non-promotion average quantity ≈ 4.33
Promotion average quantity     ≈ 4.97
```

This relationship will later help analyze:

> **Whether promotional demand contributes to stockout risk.**

---

# 🌦️ Seasonality Modeling

The model includes category-specific seasonal behavior.

Categories include:

* Grocery
* Beverages
* Personal Care
* Household
* Electronics
* Fashion
* Home & Living
* Beauty

Seasonality is modeled across:

* Winter
* Spring
* Summer
* Autumn
* Ramadan
* Eid

Current validation confirmed that:

* Summer has the highest average quantity among the four standard seasons.
* Ramadan demand is higher than normal-period demand.
* Eid-period demand is higher than normal-period demand.

Ramadan and Eid flags are also mutually exclusive.

---

# 🧪 Data Validation

The generated `fact_sales` data has undergone automated validation.

### Structural Validation

```text
✓ 125,000 transactions
✓ Transaction IDs are unique
✓ Product IDs are valid
✓ Store IDs are valid
✓ Customer IDs are valid
```

### Financial Validation

```text
✓ Quantity > 0
✓ Unit Price > 0
✓ Gross Sales ≥ Net Sales
✓ Discount Amount ≥ 0
✓ Net Sales > 0
✓ COGS > 0
✓ Gross Sales calculation correct
✓ Net Sales calculation correct
✓ COGS calculation correct
✓ Gross Profit calculation correct
```

### Business Behavior Validation

```text
✓ Fast-moving demand > Medium-moving demand > Slow-moving demand
✓ Promotions generate higher average quantities
✓ Seasonal demand behavior is present
✓ Ramadan demand uplift is present
✓ Eid demand uplift is present
✓ Ramadan/Eid overlap = 0
```

---

# 📦 Inventory Analytics — Planned

The next major phase is the generation and analysis of `fact_inventory`.

The intended inventory grain is:

> **One row = one product × one store × one day**

The inventory model will track:

```text
Opening Stock
+
Receipts
+
Transfers In
−
Transfers Out
−
Sales
+
Returns
−
Damaged Units
±
Inventory Adjustments
=
Closing Stock
```

This will allow the project to analyze inventory movement rather than simply looking at static stock levels.

---

# 📊 Planned Inventory KPIs

The project will calculate and analyze:

### Core KPIs

* Inventory Turnover
* Sell-through %
* Stockout Rate
* In-stock Rate
* Average Inventory
* Inventory Value
* Days of Inventory
* Inventory Coverage Days

### Inventory Risk

* Slow-moving Inventory
* Dead Stock
* Excess Inventory
* Stockout Risk
* Replenishment Risk
* Aging Inventory

### Profitability

* Gross Profit
* Gross Margin %
* GMROI

### Replenishment

* Safety Stock
* Reorder Point
* Lead Time
* Minimum Order Quantity
* Replenishment Priority

---

# 🔎 Planned Business Analysis

The completed project will answer questions such as:

### Inventory Availability

* Which products experience the most stockouts?
* Which stores have the highest stockout rates?
* Which high-demand products are frequently unavailable?

### Excess Inventory

* Which products have excessive inventory?
* Which stores are carrying slow-moving stock?
* Which products have very high inventory coverage?

### Product Analysis

* Which products generate the most sales?
* Which products generate the most profit?
* Which products have high demand but poor availability?

### Store Analysis

* Which stores are overstocked?
* Which stores experience frequent shortages?
* Where should inventory be transferred?

### Supplier Analysis

* Which suppliers have long lead times?
* Which suppliers create replenishment risk?
* Which products are exposed to long lead-time dependency?

### Replenishment

* Which products should be reordered first?
* What is the estimated reorder point?
* Which products require higher safety stock?

---

# 📊 Planned ABC Analysis

Products will eventually be classified using ABC analysis based on business value.

Example:

```text
A → Highest-value products
B → Medium-value products
C → Lower-value products
```

This will help prioritize inventory-management effort.

The goal is not simply:

> "Which products sell the most?"

but:

> **"Which products deserve the most inventory-management attention?"**

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

The project follows a hybrid approach rather than forcing every task into one tool.

### Python

Used for:

* Synthetic data generation
* Data profiling
* Data cleaning
* Complex transformations
* Statistical analysis
* Modeling

### SQL Server

Used for:

* Structured storage
* Data validation
* Joins
* KPI calculations
* Business analysis
* Reusable views
* Analytical queries

### Power BI

Used for:

* KPI dashboards
* Inventory health monitoring
* Store analysis
* Product analysis
* Stockout visualization
* Management reporting

This reflects a practical retail analytics workflow.

---

# 🌱 Git Development

The project is being developed incrementally using Git.

Current development milestones include:

```text
Initialize retail inventory analytics project

Implement date dimension generation

Implement supplier dimension generation

Implement product dimension generation

Implement store dimension generation

Implement customer dimension generation

Implement fact sales generation
```

Each major development stage is validated before moving to the next stage.

---

# 🚧 Project Status

### Completed

* [X] Project structure
* [X] Git/GitHub setup
* [X] Python environment
* [X] Requirements setup
* [X] Data-generation configuration
* [X] Date dimension
* [X] Supplier dimension
* [X] Product dimension
* [X] Store dimension
* [X] Customer dimension
* [X] Sales fact generation
* [X] Sales financial validation
* [X] Demand behavior validation
* [X] Promotion validation
* [X] Seasonality validation
* [X] Ramadan/Eid validation

### In Progress

* [ ] Inventory fact generation
* [ ] Inventory reconciliation
* [ ] Inventory data validation
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

# 💼 Business Value

The final project is designed to demonstrate how a Retail Analyst can move from:

```text
Raw Data
   ↓
Data Quality
   ↓
Business Metrics
   ↓
Inventory Diagnosis
   ↓
Root Cause
   ↓
Business Action
```

The goal is not simply to calculate KPIs.

The goal is to answer:

> **What is happening?**

> **Why is it happening?**

> **Which products/stores are affected?**

> **What should the retailer do?**

> **What business impact could the decision create?**

---

# ⚠️ Data Disclaimer

This project uses **synthetic data** created specifically for portfolio and learning purposes.

The locations, customers, products, suppliers, transactions, demand patterns, and financial values do not represent actual GulfMart Retail data or actual company performance.

Business assumptions such as Ramadan/Eid periods, demand factors, supplier lead times, promotions, and seasonality are synthetic modeling assumptions.

---

# 👨‍💻 Project Purpose

This project is part of a Retail Analytics portfolio demonstrating practical skills in:

* Retail business analysis
* Customer and product analytics
* Inventory analytics
* Sales analytics
* Data quality
* Python/Pandas
* SQL Server
* Power BI
* KPI development
* Business problem solving
* Git/GitHub
* Data-driven decision making

---

## ⭐ Key Portfolio Question

> **Can data help a retailer keep the right products available at the right stores, reduce excess inventory, improve inventory efficiency, and protect profitability?**

This project is designed to answer that question.
