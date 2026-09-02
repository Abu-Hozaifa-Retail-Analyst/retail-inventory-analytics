# Retail Inventory Analytics — Data Generation Specification

## 1. Project Overview

### Retailer

**GulfMart Retail**

GulfMart Retail is a fictional GCC retailer operating physical stores and an e-commerce channel across Saudi Arabia.

The purpose of this synthetic dataset is to simulate realistic retail sales and inventory behavior for an end-to-end Retail Inventory Analytics project.

### Business Problem

The retailer is experiencing inventory imbalance where high-demand products may frequently go out of stock while low-demand products remain in inventory for extended periods.

This creates:

* Lost-sales risk
* Excess inventory
* Slow-moving and dead stock
* Inefficient working capital
* Poor inventory availability
* Replenishment challenges
* Uneven inventory allocation across stores

### Primary Objective

Improve inventory availability and inventory efficiency while protecting profitability and reducing excess working capital.

---

# 2. Dataset Design Principles

The dataset must satisfy the following principles:

1. It must resemble realistic retail data.
2. Each table must have a clearly defined grain.
3. Primary and foreign-key relationships must be valid.
4. Inventory movements must reconcile mathematically.
5. Sales and inventory behavior must be related.
6. Product and store characteristics must influence demand.
7. The dataset must contain realistic business variation.
8. The data must support inventory KPI calculations.
9. The data must support root-cause analysis.
10. The data must be reproducible using a fixed random seed.
11. Synthetic business scenarios must be realistic rather than arbitrary.
12. No real customer personal information will be used.

---

# 3. Dataset Time Period

### Start Date

`2023-01-01`

### End Date

`2025-12-31`

### Duration

3 years.

### Purpose

The three-year period provides enough history for:

* Year-over-year analysis
* Monthly trends
* Seasonal analysis
* Demand trends
* Inventory turnover
* Stockout trends
* Product lifecycle analysis
* Recent vs historical demand comparison

---

# 4. Tables

The dataset will contain seven tables:

1. `dim_date`
2. `dim_product`
3. `dim_store`
4. `dim_supplier`
5. `dim_customer`
6. `fact_sales`
7. `fact_inventory`

---

# 5. Table: dim_date

## Grain

One row per calendar date.

## Target Rows

Approximately 1,096 rows.

## Columns

| Column        | Data Type | Description             |
| ------------- | --------- | ----------------------- |
| date          | DATE      | Calendar date           |
| year          | INTEGER   | Calendar year           |
| quarter       | INTEGER   | Quarter number          |
| month         | INTEGER   | Month number            |
| month_name    | VARCHAR   | Month name              |
| week_of_year  | INTEGER   | ISO-style week number   |
| day           | INTEGER   | Day of month            |
| day_name      | VARCHAR   | Day name                |
| day_of_week   | INTEGER   | Day-of-week number      |
| is_weekend    | BOOLEAN   | Weekend indicator       |
| season        | VARCHAR   | Seasonal classification |
| is_ramadan    | BOOLEAN   | Ramadan indicator       |
| is_eid_period | BOOLEAN   | Eid-period indicator    |

## Business Rules

* Every date must be unique.
* No dates may be missing inside the defined date range.
* `month` must be between 1 and 12.
* `quarter` must be between 1 and 4.
* Weekend classification must be consistent.
* Ramadan/Eid flags must be based on defined dates rather than randomly assigned.

---

# 6. Table: dim_product

## Grain

One row per product.

## Target Rows

500 products.

## Columns

| Column              | Data Type | Description                          |
| ------------------- | --------- | ------------------------------------ |
| product_id          | VARCHAR   | Unique product identifier            |
| product_name        | VARCHAR   | Product description                  |
| category            | VARCHAR   | Main product category                |
| subcategory         | VARCHAR   | Product subcategory                  |
| brand               | VARCHAR   | Brand                                |
| supplier_id         | VARCHAR   | Primary supplier                     |
| unit_cost           | DECIMAL   | Product cost                         |
| selling_price       | DECIMAL   | Standard selling price               |
| product_status      | VARCHAR   | Active/discontinued                  |
| product_launch_date | DATE      | Product introduction date            |
| shelf_life_days     | INTEGER   | Expected shelf life where applicable |

## Categories

The dataset should contain categories such as:

* Grocery
* Beverages
* Personal Care
* Household
* Electronics
* Fashion
* Home & Living
* Beauty

## Product Demand Classes

Products should be assigned different demand profiles:

* Fast-moving
* Medium-moving
* Slow-moving

Demand class should influence expected sales velocity.

## Price Rules

Selling price must be greater than unit cost.

A product's gross margin should generally be positive.

Example:

```text
Unit Cost = 50 SAR
Selling Price = 80 SAR
```

Gross margin before discount:

```text
30 SAR
```

## Business Rules

* `product_id` must be unique.
* Every product must have a valid supplier.
* Unit cost must be greater than zero.
* Selling price must be greater than unit cost.
* Product launch date must fall within or before the analysis period.
* Discontinued products may have limited sales after discontinuation.
* Product categories and subcategories must be logically consistent.

---

# 7. Table: dim_store

## Grain

One row per physical retail store.

## Target Rows

20 stores.

## Columns

| Column         | Data Type | Description             |
| -------------- | --------- | ----------------------- |
| store_id       | VARCHAR   | Unique store identifier |
| store_name     | VARCHAR   | Store name              |
| city           | VARCHAR   | Saudi city              |
| region         | VARCHAR   | Geographic region       |
| store_type     | VARCHAR   | Store format            |
| opening_date   | DATE      | Store opening date      |
| store_size_sqm | INTEGER   | Approximate store size  |
| channel        | VARCHAR   | Physical/E-commerce     |

## Regions

The dataset should represent Saudi regions such as:

* Central
* Western
* Eastern
* Northern
* Southern

## Example Cities

Examples may include:

* Riyadh
* Jeddah
* Dammam
* Khobar
* Makkah
* Madinah
* Abha
* Tabuk

## Store Types

* Hypermarket
* Supermarket
* Express
* E-commerce

## Business Rules

* `store_id` must be unique.
* Every store must belong to one region.
* Store opening date must be valid.
* Store size must be positive.
* Store characteristics should influence demand capacity.

E-commerce may be modeled as a separate channel/store entity if required by the analytical model.

---

# 8. Table: dim_supplier

## Grain

One row per supplier.

## Target Rows

30 suppliers.

## Columns

| Column            | Data Type | Description                     |
| ----------------- | --------- | ------------------------------- |
| supplier_id       | VARCHAR   | Unique supplier identifier      |
| supplier_name     | VARCHAR   | Supplier name                   |
| supplier_region   | VARCHAR   | Supplier location/region        |
| lead_time_days    | INTEGER   | Typical replenishment lead time |
| minimum_order_qty | INTEGER   | Minimum order quantity          |
| supplier_status   | VARCHAR   | Active/inactive                 |

## Lead-Time Distribution

Suppliers should have different lead times.

Example ranges:

* Local suppliers: approximately 2–7 days
* Regional suppliers: approximately 7–14 days
* Long-lead suppliers: approximately 14–30 days

The exact values will be generated programmatically.

## Business Rules

* `supplier_id` must be unique.
* Lead time must be positive.
* Minimum order quantity must be positive.
* Every active product must have a valid supplier.

---

# 9. Table: dim_customer

## Grain

One row per customer.

## Target Rows

5,000 customers.

## Columns

| Column           | Data Type | Description                |
| ---------------- | --------- | -------------------------- |
| customer_id      | VARCHAR   | Unique customer identifier |
| customer_segment | VARCHAR   | Customer segment           |
| gender           | VARCHAR   | Customer gender            |
| age_group        | VARCHAR   | Age category               |
| city             | VARCHAR   | Customer city              |

## Customer Segments

* Premium
* Regular
* Value
* New

## Age Groups

Examples:

* 18–24
* 25–34
* 35–44
* 45–54
* 55+

## Business Rules

The customer table is designed for analytical segmentation rather than personal identification.

No names, phone numbers, email addresses, addresses, or other unnecessary personal information will be generated.

---

# 10. Table: fact_sales

## Grain

One row per sales transaction line.

## Target Rows

Approximately 100,000–150,000 transaction lines.

## Columns

| Column           | Data Type | Description                   |
| ---------------- | --------- | ----------------------------- |
| transaction_id   | VARCHAR   | Unique transaction identifier |
| transaction_date | DATE      | Transaction date              |
| store_id         | VARCHAR   | Selling store/channel         |
| product_id       | VARCHAR   | Product sold                  |
| customer_id      | VARCHAR   | Customer                      |
| quantity         | INTEGER   | Units sold                    |
| unit_price       | DECIMAL   | Selling price per unit        |
| discount_amount  | DECIMAL   | Discount amount               |
| gross_sales      | DECIMAL   | Sales before discount         |
| net_sales        | DECIMAL   | Sales after discount          |
| unit_cost        | DECIMAL   | Cost per unit                 |
| cogs             | DECIMAL   | Cost of goods sold            |
| gross_profit     | DECIMAL   | Net sales minus COGS          |

## Sales Formula

```text
Gross Sales
=
Quantity × Unit Price
```

```text
Net Sales
=
Gross Sales − Discount Amount
```

```text
COGS
=
Quantity × Unit Cost
```

```text
Gross Profit
=
Net Sales − COGS
```

## Business Rules

* Quantity must be positive for normal sales transactions.
* Unit price must be positive.
* Discount must not exceed gross sales.
* Net sales must not be negative.
* COGS must be positive.
* Gross profit must equal Net Sales − COGS.
* Every `product_id` must exist in `dim_product`.
* Every `store_id` must exist in `dim_store`.
* Every `customer_id` must exist in `dim_customer`.
* Every transaction date must exist in `dim_date`.

---

# 11. Sales Demand Distribution

Sales must NOT be uniformly random.

Demand will be influenced by:

### Product

Fast-moving products receive higher expected demand.

### Store

Larger/high-traffic stores receive higher expected demand.

### Category

Different categories have different typical demand levels.

### Seasonality

Some products experience seasonal demand changes.

### Day of Week

Demand may differ between weekdays and weekends.

### Promotion/Discount

Discounted products may receive increased demand.

### Random Variation

A controlled amount of randomness will prevent the dataset from becoming artificially predictable.

Conceptually:

```text
Expected Demand
=
Base Product Demand
× Store Factor
× Category Factor
× Seasonality Factor
× Day-of-Week Factor
× Promotion Factor
× Random Variation
```

---

# 12. Table: fact_inventory

## Grain

One row per product × store × day.

## Columns

| Column                | Data Type | Description                  |
| --------------------- | --------- | ---------------------------- |
| inventory_date        | DATE      | Inventory snapshot date      |
| store_id              | VARCHAR   | Store                        |
| product_id            | VARCHAR   | Product                      |
| opening_stock         | INTEGER   | Stock at start of day        |
| receipts              | INTEGER   | Supplier receipts            |
| transfers_in          | INTEGER   | Units transferred into store |
| transfers_out         | INTEGER   | Units transferred out        |
| sales_units           | INTEGER   | Units sold                   |
| returns_units         | INTEGER   | Units returned               |
| inventory_adjustments | INTEGER   | Inventory adjustments        |
| damaged_units         | INTEGER   | Damaged inventory            |
| closing_stock         | INTEGER   | End-of-day inventory         |

## Inventory Reconciliation Formula

The primary inventory equation is:

```text
Closing Stock
=
Opening Stock
+ Receipts
+ Transfers In
− Transfers Out
− Sales
+ Returns
− Damaged Units
± Inventory Adjustments
```

The exact treatment of damaged units and adjustments must remain consistent throughout the project.

## Critical Rule

The generated `closing_stock` must be derived from the inventory movement equation rather than independently generated as a random number.

This allows later validation to test whether:

```text
Calculated Closing Stock
=
Recorded Closing Stock
```

---

# 13. Inventory Initialization

At the beginning of the analysis period, each active product-store combination receives an opening inventory level based on:

* Product demand class
* Store type
* Expected demand
* Product category
* Replenishment characteristics

High-demand products should generally begin with higher stock levels than slow-moving products.

---

# 14. Inventory Replenishment Behavior

Inventory receipts should not occur randomly every day.

They should be influenced by:

* Current inventory
* Expected demand
* Reorder point
* Supplier lead time
* Safety stock
* Minimum order quantity

Conceptually:

```text
If projected inventory risk is high
        ↓
Replenishment order
        ↓
Supplier lead time
        ↓
Receipt into store
```

This creates realistic replenishment patterns.

---

# 15. Reorder Point Concept

The dataset will support the following replenishment formula:

```text
Reorder Point
=
Average Daily Demand × Lead Time
+
Safety Stock
```

The dataset itself should contain enough information to calculate this metric rather than simply generating a final reorder-point number without business logic.

---

# 16. Safety Stock

Safety stock will represent protection against demand variability and supply uncertainty.

It may be derived using a simplified statistical approach based on:

* Demand variability
* Lead time
* Service-level assumptions

The methodology will be documented separately before the final replenishment analysis.

---

# 17. Stockout Behavior

Stockouts should occur naturally when:

```text
Demand
>
Available Inventory
```

The dataset should contain a realistic mixture of:

* No stockout
* Occasional stockout
* Frequent stockout

Stockouts should be more likely for:

* Fast-moving products
* High-demand stores
* Products with long supplier lead times
* Products experiencing demand increases
* Products with insufficient safety stock

---

# 18. Overstock Behavior

Overstock should not simply mean "high inventory."

A product should be considered a potential overstock candidate when multiple indicators point in the same direction:

```text
High inventory
+
Low demand velocity
+
High inventory coverage
+
Low sell-through
```

This distinction is critical.

Example:

```text
Product A
Inventory = 1,000 units
Daily demand = 200
Coverage = 5 days
```

This may be healthy.

But:

```text
Product B
Inventory = 1,000 units
Daily demand = 2
Coverage = 500 days
```

This is a strong potential overstock signal.

---

# 19. Slow-Moving and Dead Stock

The dataset should contain products that naturally develop into:

### Slow-moving inventory

Low sales velocity while inventory remains available.

### Dead stock

Inventory with extremely low or zero recent sales over a defined period.

The exact thresholds will be determined during the analytical phase rather than hard-coded into the raw dataset.

---

# 20. Inventory Aging

The dataset must support inventory aging analysis.

Potential aging buckets:

```text
0–30 days
31–60 days
61–90 days
91–180 days
181–365 days
365+ days
```

Aging methodology will be documented separately.

---

# 21. ABC Analysis Support

Sales and profitability distributions should be sufficiently unequal to support ABC classification.

Expected concept:

### A products

Small percentage of products contributing a large share of sales/value.

### B products

Moderate contribution.

### C products

Large number of products contributing a relatively small share.

The classification will be calculated during analysis rather than directly stored in the raw product table.

---

# 22. Product-Store Allocation

Not every product needs identical demand at every store.

Allocation should depend on:

* Store type
* Store size
* City/region
* Product category
* Product demand profile
* Store-specific demand patterns

This allows analysis of store-level assortment and inventory imbalance.

---

# 23. Store Imbalance Scenarios

The dataset should contain realistic opportunities such as:

```text
Store A
High inventory
Low demand
High coverage

        versus

Store B
Low inventory
High demand
Stockout risk
```

for the same product.

This supports later analysis of:

> Potential store-to-store inventory transfer opportunities.

---

# 24. Seasonal Behavior

Selected categories/products should experience seasonal demand changes.

Examples may include:

* Beverages during hotter periods
* Certain fashion categories during seasonal periods
* Grocery demand changes during Ramadan/Eid
* Selected consumer products during promotional periods

However:

**Seasonality must be validated through the data.**

We will not claim that a particular event caused a sales increase unless the analysis provides evidence.

---

# 25. Demand Trend Scenarios

The dataset should contain different product demand trajectories.

Examples:

### Growing

```text
2023 → Moderate demand
2024 → Higher demand
2025 → Strong demand
```

### Declining

```text
2023 → Strong demand
2024 → Moderate demand
2025 → Weak demand
```

### Stable

Relatively consistent demand.

### Volatile

Large fluctuations in demand.

These patterns will support demand trend and inventory-risk analysis.

---

# 26. Profitability Behavior

Products should have different gross-margin characteristics.

Some products may have:

* High sales + high margin
* High sales + low margin
* Low sales + high margin
* Low sales + low margin

This is important for GMROI and profitability analysis.

---

# 27. GMROI Support

The dataset must support:

```text
GMROI
=
Gross Margin
÷
Average Inventory Cost
```

where:

```text
Gross Margin
=
Gross Profit
```

and inventory cost is based on inventory units × unit cost.

This allows us to identify products that generate strong or weak returns relative to inventory investment.

---

# 28. Referential Integrity Rules

The following relationships must be valid:

```text
fact_sales.product_id
        ↓
dim_product.product_id
```

```text
fact_sales.store_id
        ↓
dim_store.store_id
```

```text
fact_sales.customer_id
        ↓
dim_customer.customer_id
```

```text
fact_sales.transaction_date
        ↓
dim_date.date
```

```text
fact_inventory.product_id
        ↓
dim_product.product_id
```

```text
fact_inventory.store_id
        ↓
dim_store.store_id
```

```text
dim_product.supplier_id
        ↓
dim_supplier.supplier_id
```

No orphan foreign keys should exist in the clean final dataset.

---

# 29. Data Quality Rules

The raw generator should aim to create structurally valid data.

Expected rules include:

### Primary keys

No duplicate primary keys.

### Foreign keys

No invalid references.

### Dates

Valid dates within the intended period.

### Numeric values

No impossible negative values where prohibited.

### Prices

Selling price > unit cost.

### Sales

Net sales must reconcile with gross sales and discounts.

### Profit

Gross profit must reconcile with sales and COGS.

### Inventory

Closing stock must reconcile with inventory movements.

### Grain

`fact_inventory` must have at most one record per:

```text
inventory_date + store_id + product_id
```

---

# 30. Controlled Imperfections

The raw dataset should be structurally realistic, but we may intentionally introduce a small number of controlled data-quality issues later for the Data Validation phase.

Examples:

* Missing value
* Duplicate record
* Invalid reference
* Unexpected value
* Inventory reconciliation error

These issues will be intentionally documented and used to demonstrate the data-quality workflow.

They must be clearly identified as synthetic test issues and must not compromise the main analytical dataset.

---

# 31. Reproducibility

The generator must use a fixed random seed:

```python
RANDOM_SEED = 42
```

All major generation steps should use reproducible random logic.

The same specification and seed should produce the same dataset, subject to the same software environment.

---

# 32. Target Dataset Size

Initial targets:

| Table          |                                 Target |
| -------------- | -------------------------------------: |
| dim_date       |                                 ~1,096 |
| dim_product    |                                    500 |
| dim_store      |                                     20 |
| dim_supplier   |                                     30 |
| dim_customer   |                                  5,000 |
| fact_sales     |                       ~100,000–150,000 |
| fact_inventory | Manageable daily product-store dataset |

The exact `fact_inventory` size will be determined during implementation to balance realism, SQL Server performance, Power BI performance, and laptop resource usage.

---

# 33. Intended Analytical Outputs

The dataset must support analysis of:

* Inventory value
* Average inventory
* Inventory turnover
* Days of inventory
* Inventory coverage
* Sell-through %
* Stockout rate
* In-stock rate
* Slow-moving inventory
* Dead stock
* Excess inventory
* Inventory aging
* ABC classification
* Demand trends
* Seasonality
* Reorder point
* Safety stock
* Replenishment priority
* Store-to-store transfer opportunities
* Gross margin
* GMROI
* Product performance
* Store performance
* Supplier lead-time risk
* Root causes of inventory imbalance

---

# 34. Final Business Questions Supported

The completed dataset must allow us to answer:

### Question 1

How much inventory do we hold, and where is it concentrated across stores, categories, and products?

### Question 2

Which products and stores experience the highest stockout rates and frequency?

### Question 3

Are high-demand and high-priority products experiencing stockouts?

### Question 4

Which products and stores have excessive inventory relative to their demand and sales velocity?

### Question 5

Which products are becoming slow-moving or dead stock, and how much inventory value is at risk?

---

# 35. Generation Philosophy

The generator must follow this principle:

```text
Business Rule
      ↓
Data Generation Logic
      ↓
Raw Dataset
      ↓
Data Profiling
      ↓
Data Validation
      ↓
KPI Calculation
      ↓
Business Finding
      ↓
Business Decision
```

The purpose of the dataset is therefore not simply to create realistic-looking numbers.

The purpose is to create a controlled retail environment where a Retail Analyst can demonstrate:

**Data → Analysis → Diagnosis → Business Impact → Recommendation → Action**

---

# 36. Data Storage

Generated raw CSV files will be saved under:

```text
data/raw/
```

Expected files:

```text
data/raw/
├── dim_date.csv
├── dim_product.csv
├── dim_store.csv
├── dim_supplier.csv
├── dim_customer.csv
├── fact_sales.csv
└── fact_inventory.csv
```

The raw files must remain unchanged after generation.

Cleaning and transformation will occur in later stages.

---

# 37. Next Implementation Stage

After this specification is approved, the next stage is:

**STEP 3.1.2 — Build the dataset-generation configuration**

We will define the Python constants and controlled distributions for:

* Date range
* Number of stores
* Number of products
* Number of customers
* Number of suppliers
* Categories
* Store types
* Product demand classes
* Supplier lead times
* Store demand factors
* Category demand factors
* Seasonal factors
* Random seed

Only after that will we begin generating the dimension tables.
