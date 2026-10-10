-- ============================================================
-- GulfMart Retail Inventory Analytics
-- 09_powerbi_views.sql
-- ============================================================
-- Reporting layer for Power BI. Nothing here modifies a table; it
-- only creates views over the validated star schema.
--
-- Design:
--   * fact_inventory (10.96M rows) is pre-aggregated to MONTH x STORE
--     x PRODUCT (360,000 rows) -- small enough to import, rich enough
--     to slice by any product/store attribute.
--   * Monthly views store SUMS of daily values (e.g. inventory_value_
--     days), never pre-computed averages. Averaging pre-averaged
--     numbers is wrong once a report re-aggregates; with sums, a DAX
--     measure divides by days-in-period and is correct at any grain.
--   * dim_date is deliberately NOT exposed: its is_ramadan/is_eid_
--     period flags are permanently FALSE (known generator quirk, see
--     README) and month grain is all the dashboard needs. vw_dim_month
--     replaces it.
--   * Refresh cost: several views scan fact_inventory when Power BI
--     refreshes. Expect a few minutes, not seconds. If that becomes
--     annoying, materialize vw_inventory_monthly into a table.
-- ============================================================

USE GulfMartRetailAnalytics;
GO

-- ============================================================
-- DIMENSIONS
-- ============================================================

IF OBJECT_ID('dbo.vw_dim_month', 'V') IS NOT NULL DROP VIEW dbo.vw_dim_month;
GO
CREATE VIEW dbo.vw_dim_month AS
SELECT
    DATEFROMPARTS([year], [month], 1) AS month_start,
    [year]        AS year_number,
    quarter       AS quarter_label,
    [month]       AS month_number,
    month_name,
    COUNT(*)      AS days_in_month
FROM dbo.dim_date
GROUP BY DATEFROMPARTS([year], [month], 1), [year], quarter, [month], month_name;
GO

IF OBJECT_ID('dbo.vw_dim_product', 'V') IS NOT NULL DROP VIEW dbo.vw_dim_product;
GO
-- Supplier attributes are denormalized onto the product so the model
-- stays a clean star (no snowflake through dim_supplier).
CREATE VIEW dbo.vw_dim_product AS
SELECT
    p.product_id, p.product_name, p.category, p.subcategory, p.brand,
    p.demand_class, p.demand_trajectory, p.product_status,
    p.unit_cost, p.selling_price, p.shelf_life_days,
    s.supplier_id, s.supplier_name, s.supplier_region, s.supplier_status,
    s.lead_time_days,
    CASE
        WHEN s.lead_time_days <= 7  THEN 'Short (<=7d)'
        WHEN s.lead_time_days <= 14 THEN 'Medium (8-14d)'
        ELSE 'Long (>14d)'
    END AS lead_time_bucket
FROM dbo.dim_product p
JOIN dbo.dim_supplier s ON p.supplier_id = s.supplier_id;
GO

IF OBJECT_ID('dbo.vw_dim_store', 'V') IS NOT NULL DROP VIEW dbo.vw_dim_store;
GO
CREATE VIEW dbo.vw_dim_store AS
SELECT
    store_id, store_name, city, region, store_type, channel,
    store_size_sqm, store_demand_factor, opening_date
FROM dbo.dim_store;
GO

-- ============================================================
-- FACT VIEWS (month x store x product)
-- ============================================================

IF OBJECT_ID('dbo.vw_inventory_monthly', 'V') IS NOT NULL DROP VIEW dbo.vw_inventory_monthly;
GO
CREATE VIEW dbo.vw_inventory_monthly AS
SELECT
    DATEFROMPARTS(YEAR(fi.[date]), MONTH(fi.[date]), 1) AS month_start,
    fi.store_id,
    fi.product_id,
    COUNT(*)                                             AS days_observed,
    SUM(fi.closing_stock * p.unit_cost)                  AS inventory_value_days,
    SUM(CAST(fi.closing_stock AS BIGINT))                AS inventory_units_days,
    SUM(CASE WHEN fi.closing_stock > fi.target_stock_level
             THEN (fi.closing_stock - fi.target_stock_level) * p.unit_cost
             ELSE 0 END)                                 AS excess_value_days,
    SUM(CASE WHEN fi.closing_stock > fi.target_stock_level
             THEN fi.closing_stock - fi.target_stock_level
             ELSE 0 END)                                 AS excess_units_days,
    SUM(fi.sales_units)                                  AS sales_units,
    SUM(fi.receipts)                                     AS receipts_units,
    SUM(CAST(fi.low_stock_event AS INT))                 AS low_stock_days,
    SUM(CAST(fi.stockout_event AS INT))                  AS stockout_days
FROM dbo.fact_inventory fi
JOIN dbo.dim_product p ON fi.product_id = p.product_id
GROUP BY DATEFROMPARTS(YEAR(fi.[date]), MONTH(fi.[date]), 1), fi.store_id, fi.product_id;
GO

IF OBJECT_ID('dbo.vw_sales_monthly', 'V') IS NOT NULL DROP VIEW dbo.vw_sales_monthly;
GO
CREATE VIEW dbo.vw_sales_monthly AS
SELECT
    DATEFROMPARTS(YEAR(transaction_date), MONTH(transaction_date), 1) AS month_start,
    store_id,
    product_id,
    COUNT(*)             AS transactions,
    SUM(quantity)        AS units_sold,
    SUM(gross_sales)     AS gross_sales,
    SUM(discount_amount) AS discount_amount,
    SUM(net_sales)       AS net_sales,
    SUM(cogs)            AS cogs,
    SUM(gross_profit)    AS gross_profit
FROM dbo.fact_sales
GROUP BY DATEFROMPARTS(YEAR(transaction_date), MONTH(transaction_date), 1), store_id, product_id;
GO

-- Root-cause view: one row per month x store x product that placed
-- at least one order. ideal_order is what an inventory-position-
-- netting policy would have ordered (same logic as 08_replenishment_
-- analysis.sql). Limitation carried over: opening_stock is the
-- inventory-position proxy; in-transit orders are not tracked.
IF OBJECT_ID('dbo.vw_replenishment_overshoot_monthly', 'V') IS NOT NULL
    DROP VIEW dbo.vw_replenishment_overshoot_monthly;
GO
CREATE VIEW dbo.vw_replenishment_overshoot_monthly AS
SELECT
    DATEFROMPARTS(YEAR(fi.[date]), MONTH(fi.[date]), 1) AS month_start,
    fi.store_id,
    fi.product_id,
    COUNT(*)                                              AS orders_placed,
    SUM(CASE WHEN io.ideal_order = 0 THEN 1 ELSE 0 END)   AS unnecessary_orders,
    SUM(CASE WHEN fi.planned_order_quantity > fi.target_stock_level
             THEN 1 ELSE 0 END)                           AS moq_inflated_orders,
    SUM(fi.planned_order_quantity * p.unit_cost)          AS ordered_value,
    SUM(CASE WHEN fi.planned_order_quantity > io.ideal_order
             THEN (fi.planned_order_quantity - io.ideal_order) * p.unit_cost
             ELSE 0 END)                                  AS netting_overshoot_value,
    SUM(CASE WHEN fi.planned_order_quantity > fi.target_stock_level
             THEN (fi.planned_order_quantity - fi.target_stock_level) * p.unit_cost
             ELSE 0 END)                                  AS moq_overshoot_value
FROM dbo.fact_inventory fi
JOIN dbo.dim_product p ON fi.product_id = p.product_id
CROSS APPLY (
    SELECT CASE
        WHEN fi.opening_stock >= fi.target_stock_level THEN 0
        WHEN (fi.target_stock_level - fi.opening_stock) > fi.minimum_order_qty
            THEN fi.target_stock_level - fi.opening_stock
        ELSE fi.minimum_order_qty
    END AS ideal_order
) io
WHERE fi.planned_order_quantity > 0
GROUP BY DATEFROMPARTS(YEAR(fi.[date]), MONTH(fi.[date]), 1), fi.store_id, fi.product_id;
GO

-- ============================================================
-- PRODUCT-GRAIN VIEW: ABC x excess-tier (feeds the priority matrix)
-- Same cumulative-threshold technique as 07/08. Zero-value rows are
-- forced to the lowest tier; all 500 products are kept (products with
-- no sales get annual_cogs = 0 and land in class C).
-- ============================================================

IF OBJECT_ID('dbo.vw_product_abc', 'V') IS NOT NULL DROP VIEW dbo.vw_product_abc;
GO
CREATE VIEW dbo.vw_product_abc AS
WITH PeriodDays AS (
    SELECT COUNT(*) AS period_days FROM dbo.dim_date
),
ProductCogs AS (
    SELECT p.product_id,
           ISNULL(SUM(fs.cogs), 0) / pd.period_days * 365 AS annual_cogs
    FROM dbo.dim_product p
    LEFT JOIN dbo.fact_sales fs ON p.product_id = fs.product_id
    CROSS JOIN PeriodDays pd
    GROUP BY p.product_id, pd.period_days
),
ProductExcess AS (
    SELECT m.product_id,
           SUM(m.excess_value_days) / pd.period_days AS avg_excess_value
    FROM dbo.vw_inventory_monthly m
    CROSS JOIN PeriodDays pd
    GROUP BY m.product_id, pd.period_days
),
Combined AS (
    SELECT c.product_id, c.annual_cogs, ISNULL(e.avg_excess_value, 0) AS avg_excess_value
    FROM ProductCogs c
    LEFT JOIN ProductExcess e ON c.product_id = e.product_id
),
Ranked AS (
    SELECT
        product_id, annual_cogs, avg_excess_value,
        CASE WHEN annual_cogs > 0 THEN
            SUM(CASE WHEN annual_cogs > 0 THEN annual_cogs ELSE 0 END)
                OVER (ORDER BY annual_cogs DESC, product_id
                      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
            / NULLIF(SUM(CASE WHEN annual_cogs > 0 THEN annual_cogs ELSE 0 END) OVER (), 0) * 100
        END AS cogs_cumulative_pct,
        CASE WHEN avg_excess_value > 0 THEN
            SUM(CASE WHEN avg_excess_value > 0 THEN avg_excess_value ELSE 0 END)
                OVER (ORDER BY avg_excess_value DESC, product_id
                      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
            / NULLIF(SUM(CASE WHEN avg_excess_value > 0 THEN avg_excess_value ELSE 0 END) OVER (), 0) * 100
        END AS excess_cumulative_pct
    FROM Combined
),
Classified AS (
    SELECT
        product_id, annual_cogs, cogs_cumulative_pct,
        CASE
            WHEN annual_cogs <= 0 THEN 'C'
            WHEN cogs_cumulative_pct <= 80 THEN 'A'
            WHEN cogs_cumulative_pct <= 95 THEN 'B'
            ELSE 'C'
        END AS abc_class,
        avg_excess_value, excess_cumulative_pct,
        CASE
            WHEN avg_excess_value <= 0 THEN 'Low'
            WHEN excess_cumulative_pct <= 80 THEN 'High'
            WHEN excess_cumulative_pct <= 95 THEN 'Medium'
            ELSE 'Low'
        END AS excess_tier
    FROM Ranked
)
SELECT *, abc_class + ' x ' + excess_tier AS priority_segment
FROM Classified;
GO

-- ============================================================
-- ACTION LIST (materialized by 08_replenishment_analysis.sql)
-- ============================================================

IF OBJECT_ID('dbo.vw_replenishment_action_list', 'V') IS NOT NULL
    DROP VIEW dbo.vw_replenishment_action_list;
GO
-- Carries each combo's whole-period order-overshoot totals so the action
-- list is self-contained: "recoverable value by SUPPRESS / REDUCE" works
-- without a two-column relationship to the monthly fact views.
CREATE VIEW dbo.vw_replenishment_action_list AS
WITH Overshoot AS (
    SELECT
        store_id, product_id,
        SUM(orders_placed)            AS orders_placed,
        SUM(unnecessary_orders)       AS unnecessary_orders,
        SUM(moq_inflated_orders)      AS moq_inflated_orders,
        SUM(ordered_value)            AS ordered_value,
        SUM(netting_overshoot_value)  AS netting_overshoot_value,
        SUM(moq_overshoot_value)      AS moq_overshoot_value
    FROM dbo.vw_replenishment_overshoot_monthly
    GROUP BY store_id, product_id
)
SELECT
    a.store_id, a.product_id, a.annual_cogs_class, a.excess_tier,
    a.avg_excess_value, a.low_stock_pct, a.min_coverage_days,
    a.recommended_action,
    ISNULL(o.orders_placed, 0)            AS orders_placed,
    ISNULL(o.unnecessary_orders, 0)       AS unnecessary_orders,
    ISNULL(o.moq_inflated_orders, 0)      AS moq_inflated_orders,
    ISNULL(o.ordered_value, 0)            AS ordered_value,
    ISNULL(o.netting_overshoot_value, 0)  AS netting_overshoot_value,
    ISNULL(o.moq_overshoot_value, 0)      AS moq_overshoot_value
FROM dbo.replenishment_action_list a
LEFT JOIN Overshoot o ON a.store_id = o.store_id AND a.product_id = o.product_id;
GO

-- ============================================================
-- RECONCILIATION: every view must tie back to a number already
-- established in the Python phase or in scripts 04-08.
-- Expect a minute or two -- this scans fact_inventory through the views.
-- ============================================================

DECLARE @Checks TABLE (
    check_name VARCHAR(80),
    actual     DECIMAL(28,4),
    expected   DECIMAL(28,4),
    tolerance  DECIMAL(28,6),
    status     VARCHAR(6)
);

DECLARE @days DECIMAL(18,4) = (SELECT COUNT(*) FROM dbo.dim_date);

INSERT INTO @Checks (check_name, actual, expected, tolerance)
SELECT 'vw_inventory_monthly rows (10,000 x 36)', CAST(COUNT(*) AS DECIMAL(28,4)), 360000, 0
FROM dbo.vw_inventory_monthly
UNION ALL SELECT 'Avg daily inventory value (03/05: 12.646B)',
    CAST(SUM(inventory_value_days) / @days AS DECIMAL(28,4)), 12646166082.5415, 12646166082.5415 * 0.000001
FROM dbo.vw_inventory_monthly
UNION ALL SELECT 'Avg daily excess value (05/07: 12.524B)',
    CAST(SUM(excess_value_days) / @days AS DECIMAL(28,4)), 12524496539.5339, 12524496539.5339 * 0.000001
FROM dbo.vw_inventory_monthly
UNION ALL SELECT 'Low-stock events (04/06: 33,789)',
    CAST(SUM(low_stock_days) AS DECIMAL(28,4)), 33789, 0
FROM dbo.vw_inventory_monthly
UNION ALL SELECT 'Stockout events (expect 0)',
    CAST(SUM(stockout_days) AS DECIMAL(28,4)), 0, 0
FROM dbo.vw_inventory_monthly
UNION ALL SELECT 'Sales transactions (125,000)',
    CAST(SUM(transactions) AS DECIMAL(28,4)), 125000, 0
FROM dbo.vw_sales_monthly
UNION ALL SELECT 'Replenishment orders (730,069)',
    CAST(SUM(orders_placed) AS DECIMAL(28,4)), 730069, 0
FROM dbo.vw_replenishment_overshoot_monthly
UNION ALL SELECT 'Unnecessary orders (08: 719,348)',
    CAST(SUM(unnecessary_orders) AS DECIMAL(28,4)), 719348, 0
FROM dbo.vw_replenishment_overshoot_monthly
UNION ALL SELECT 'Netting overshoot value (08: 25.305B)',
    CAST(SUM(netting_overshoot_value) AS DECIMAL(28,4)), 25304721276.1605, 25304721276.1605 * 0.000001
FROM dbo.vw_replenishment_overshoot_monthly
UNION ALL SELECT 'MOQ overshoot value (07/08: 12.668B)',
    CAST(SUM(moq_overshoot_value) AS DECIMAL(28,4)), 12667872550.2330, 12667872550.2330 * 0.000001
FROM dbo.vw_replenishment_overshoot_monthly
UNION ALL SELECT 'ABC class A products (51)',
    CAST(COUNT(*) AS DECIMAL(28,4)), 51, 0 FROM dbo.vw_product_abc WHERE abc_class = 'A'
UNION ALL SELECT 'ABC class B products (105)',
    CAST(COUNT(*) AS DECIMAL(28,4)), 105, 0 FROM dbo.vw_product_abc WHERE abc_class = 'B'
UNION ALL SELECT 'ABC class C products (344)',
    CAST(COUNT(*) AS DECIMAL(28,4)), 344, 0 FROM dbo.vw_product_abc WHERE abc_class = 'C'
UNION ALL SELECT 'High excess tier products (06: 152, +/-1 at boundary)',
    CAST(COUNT(*) AS DECIMAL(28,4)), 152, 1 FROM dbo.vw_product_abc WHERE excess_tier = 'High'
UNION ALL SELECT 'Action list rows (10,000)',
    CAST(COUNT(*) AS DECIMAL(28,4)), 10000, 0 FROM dbo.vw_replenishment_action_list;

UPDATE @Checks
SET status = CASE WHEN ABS(actual - expected) <= tolerance THEN 'PASS' ELSE 'FAIL' END;

SELECT check_name, actual, expected, status FROM @Checks;

IF EXISTS (SELECT 1 FROM @Checks WHERE status = 'FAIL')
    PRINT 'POWER BI VIEWS: ONE OR MORE RECONCILIATION CHECKS FAILED';
ELSE
    PRINT 'POWER BI VIEWS: ALL RECONCILIATION CHECKS PASSED';
GO


