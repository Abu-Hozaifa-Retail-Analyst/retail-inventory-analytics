-- ============================================================
-- GulfMart Retail Inventory Analytics
-- 04_data_validation.sql
-- ============================================================
-- T-SQL equivalent of src/data_validation.py's validate_generated_
-- dataset(). See file header notes from the original version for
-- full design rationale (schema guarantees vs. re-scanned checks).
--
-- Tolerance note: inventory-policy formula checks use a combined
-- absolute + relative tolerance (|a-b| <= atol + rtol*|b|), matching
-- np.isclose() in the Python phase's validate_inventory_policy().
-- fact_inventory values were downcast to float32 before being saved
-- to CSV (save_datasets() in data_generation.py), so a flat absolute
-- tolerance is too strict for larger-magnitude rows.
-- ============================================================

USE GulfMartRetailAnalytics;
GO

DECLARE @Results TABLE (
    check_id     INT IDENTITY(1,1),
    section      VARCHAR(40),
    check_name   VARCHAR(100),
    status       VARCHAR(10),
    detail       VARCHAR(500)
);

-- ============================================================
-- SECTION 1: ROW COUNTS
-- ============================================================

DECLARE @dim_date_count INT = (SELECT COUNT(*) FROM dbo.dim_date);
DECLARE @dim_supplier_count INT = (SELECT COUNT(*) FROM dbo.dim_supplier);
DECLARE @dim_product_count INT = (SELECT COUNT(*) FROM dbo.dim_product);
DECLARE @dim_store_count INT = (SELECT COUNT(*) FROM dbo.dim_store);
DECLARE @dim_customer_count INT = (SELECT COUNT(*) FROM dbo.dim_customer);
DECLARE @fact_sales_count INT = (SELECT COUNT(*) FROM dbo.fact_sales);
DECLARE @fact_inventory_count BIGINT = (SELECT COUNT(*) FROM dbo.fact_inventory);

INSERT INTO @Results (section, check_name, status, detail)
SELECT 'Row Counts', 'dim_date row count',
    CASE WHEN @dim_date_count = 1096 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Expected 1096, found ', @dim_date_count)
UNION ALL SELECT 'Row Counts', 'dim_supplier row count',
    CASE WHEN @dim_supplier_count = 30 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Expected 30, found ', @dim_supplier_count)
UNION ALL SELECT 'Row Counts', 'dim_product row count',
    CASE WHEN @dim_product_count = 500 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Expected 500, found ', @dim_product_count)
UNION ALL SELECT 'Row Counts', 'dim_store row count',
    CASE WHEN @dim_store_count = 20 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Expected 20, found ', @dim_store_count)
UNION ALL SELECT 'Row Counts', 'dim_customer row count',
    CASE WHEN @dim_customer_count = 5000 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Expected 5000, found ', @dim_customer_count)
UNION ALL SELECT 'Row Counts', 'fact_sales row count',
    CASE WHEN @fact_sales_count = 125000 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Expected 125000, found ', @fact_sales_count)
UNION ALL SELECT 'Row Counts', 'fact_inventory row count',
    CASE WHEN @fact_inventory_count = 10960000 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Expected 10960000, found ', @fact_inventory_count);

-- ============================================================
-- SECTION 2: SCHEMA GUARANTEES
-- ============================================================

INSERT INTO @Results (section, check_name, status, detail)
SELECT 'Schema Guarantees', CONCAT('PRIMARY KEY exists on ', t.table_name),
    CASE WHEN EXISTS (
        SELECT 1 FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
        WHERE tc.TABLE_NAME = t.table_name AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
    ) THEN 'PASS' ELSE 'FAIL' END,
    'Guarantees uniqueness on every row without re-scanning data'
FROM (VALUES ('dim_date'), ('dim_supplier'), ('dim_product'), ('dim_store'),
             ('dim_customer'), ('fact_sales'), ('fact_inventory')) AS t(table_name);

INSERT INTO @Results (section, check_name, status, detail)
SELECT 'Schema Guarantees', CONCAT('FOREIGN KEY exists: ', fk_name),
    CASE WHEN EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = fk_name)
        THEN 'PASS' ELSE 'FAIL' END,
    'Guarantees referential integrity without re-scanning data'
FROM (VALUES
    ('FK_dim_product_supplier'),
    ('FK_fact_sales_date'), ('FK_fact_sales_product'),
    ('FK_fact_sales_store'), ('FK_fact_sales_customer'),
    ('FK_fact_inventory_date'), ('FK_fact_inventory_product'),
    ('FK_fact_inventory_store'), ('FK_fact_inventory_supplier')
) AS fk(fk_name);

-- ============================================================
-- SECTION 3: FACT_SALES FINANCIAL CORRECTNESS
-- ============================================================

DECLARE @gross_sales_failures INT, @discount_failures INT,
        @net_sales_failures INT, @cogs_failures INT, @gross_profit_failures INT;

SELECT @gross_sales_failures = COUNT(*)
FROM dbo.fact_sales
WHERE ABS(gross_sales - (quantity * unit_price)) > 0.01;

SELECT @discount_failures = COUNT(*)
FROM dbo.fact_sales
WHERE ABS(discount_amount - ROUND(gross_sales * discount_pct, 2)) > 0.01;

SELECT @net_sales_failures = COUNT(*)
FROM dbo.fact_sales
WHERE ABS(net_sales - (gross_sales - discount_amount)) > 0.01;

SELECT @cogs_failures = COUNT(*)
FROM dbo.fact_sales fs
JOIN dbo.dim_product p ON fs.product_id = p.product_id
WHERE ABS(fs.cogs - (fs.quantity * p.unit_cost)) > 0.01;

SELECT @gross_profit_failures = COUNT(*)
FROM dbo.fact_sales
WHERE ABS(gross_profit - (net_sales - cogs)) > 0.01;

INSERT INTO @Results (section, check_name, status, detail)
SELECT 'Financial Correctness', 'gross_sales = quantity * unit_price',
    CASE WHEN @gross_sales_failures = 0 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Mismatches: ', @gross_sales_failures)
UNION ALL SELECT 'Financial Correctness', 'discount_amount = gross_sales * discount_pct',
    CASE WHEN @discount_failures = 0 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Mismatches: ', @discount_failures)
UNION ALL SELECT 'Financial Correctness', 'net_sales = gross_sales - discount_amount',
    CASE WHEN @net_sales_failures = 0 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Mismatches: ', @net_sales_failures)
UNION ALL SELECT 'Financial Correctness', 'cogs = quantity * unit_cost (joined via dim_product)',
    CASE WHEN @cogs_failures = 0 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Mismatches: ', @cogs_failures)
UNION ALL SELECT 'Financial Correctness', 'gross_profit = net_sales - cogs',
    CASE WHEN @gross_profit_failures = 0 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Mismatches: ', @gross_profit_failures);

-- ============================================================
-- SECTION 4: BUSINESS BEHAVIOR
-- Ramadan/Eid now read directly from fact_sales.is_ramadan /
-- is_eid_period -- no join to dim_date needed (its own
-- is_ramadan/is_eid_period columns are permanently False; see
-- 02_create_tables.sql header note).
-- ============================================================

DECLARE @fast_avg DECIMAL(10,2), @medium_avg DECIMAL(10,2), @slow_avg DECIMAL(10,2);

SELECT
    @fast_avg   = AVG(CASE WHEN p.demand_class = 'Fast-moving'   THEN CAST(fs.quantity AS DECIMAL(10,2)) END),
    @medium_avg = AVG(CASE WHEN p.demand_class = 'Medium-moving' THEN CAST(fs.quantity AS DECIMAL(10,2)) END),
    @slow_avg   = AVG(CASE WHEN p.demand_class = 'Slow-moving'   THEN CAST(fs.quantity AS DECIMAL(10,2)) END)
FROM dbo.fact_sales fs
JOIN dbo.dim_product p ON fs.product_id = p.product_id;

INSERT INTO @Results (section, check_name, status, detail)
SELECT 'Business Behavior', 'Fast-moving > Medium-moving > Slow-moving avg quantity',
    CASE WHEN @fast_avg > @medium_avg AND @medium_avg > @slow_avg THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Fast=', @fast_avg, ', Medium=', @medium_avg, ', Slow=', @slow_avg);

DECLARE @promo_avg DECIMAL(10,2), @non_promo_avg DECIMAL(10,2);

SELECT
    @promo_avg     = AVG(CASE WHEN is_promotion = 1 THEN CAST(quantity AS DECIMAL(10,2)) END),
    @non_promo_avg = AVG(CASE WHEN is_promotion = 0 THEN CAST(quantity AS DECIMAL(10,2)) END)
FROM dbo.fact_sales;

INSERT INTO @Results (section, check_name, status, detail)
SELECT 'Business Behavior', 'Promotions generate higher average quantity',
    CASE WHEN @promo_avg > @non_promo_avg THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Promo=', @promo_avg, ', Non-promo=', @non_promo_avg);

DECLARE @ramadan_eid_overlap INT = (
    SELECT COUNT(*) FROM dbo.fact_sales WHERE is_ramadan = 1 AND is_eid_period = 1
);

INSERT INTO @Results (section, check_name, status, detail)
SELECT 'Business Behavior', 'Ramadan / Eid periods are mutually exclusive',
    CASE WHEN @ramadan_eid_overlap = 0 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Overlapping transactions: ', @ramadan_eid_overlap);

DECLARE @ramadan_avg DECIMAL(10,2), @normal_avg DECIMAL(10,2), @eid_avg DECIMAL(10,2);

SELECT
    @ramadan_avg = AVG(CASE WHEN is_ramadan = 1 THEN CAST(quantity AS DECIMAL(10,2)) END),
    @eid_avg     = AVG(CASE WHEN is_eid_period = 1 THEN CAST(quantity AS DECIMAL(10,2)) END),
    @normal_avg  = AVG(CASE WHEN is_ramadan = 0 AND is_eid_period = 0 THEN CAST(quantity AS DECIMAL(10,2)) END)
FROM dbo.fact_sales;

INSERT INTO @Results (section, check_name, status, detail)
SELECT 'Business Behavior', 'Ramadan demand higher than normal-period demand',
    CASE WHEN @ramadan_avg > @normal_avg THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Ramadan=', @ramadan_avg, ', Normal=', @normal_avg)
UNION ALL SELECT 'Business Behavior', 'Eid demand higher than normal-period demand',
    CASE WHEN @eid_avg > @normal_avg THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Eid=', @eid_avg, ', Normal=', @normal_avg);

-- ============================================================
-- SECTION 5: INVENTORY RECONCILIATION & CONTINUITY
-- ============================================================

DECLARE @reconciliation_failures INT;

SELECT @reconciliation_failures = COUNT(*)
FROM dbo.fact_inventory
WHERE closing_stock <> (
    opening_stock + receipts + transfers_in - transfers_out
    - sales_units + returns_units - damaged_units + inventory_adjustments
);

INSERT INTO @Results (section, check_name, status, detail)
SELECT 'Inventory Reconciliation',
    'closing_stock = opening_stock + net_inventory_change',
    CASE WHEN @reconciliation_failures = 0 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Reconciliation failures: ', @reconciliation_failures);

WITH continuity_check AS (
    SELECT
        opening_stock,
        LAG(closing_stock) OVER (
            PARTITION BY store_id, product_id ORDER BY [date]
        ) AS previous_closing_stock
    FROM dbo.fact_inventory
)
INSERT INTO @Results (section, check_name, status, detail)
SELECT 'Inventory Reconciliation', 'Inventory continuity (opening = previous closing)',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Continuity failures: ', COUNT(*))
FROM continuity_check
WHERE previous_closing_stock IS NOT NULL
  AND opening_stock <> previous_closing_stock;

-- ============================================================
-- SECTION 6: NEGATIVE INVENTORY
-- ============================================================

DECLARE @negative_opening INT = (SELECT COUNT(*) FROM dbo.fact_inventory WHERE opening_stock < 0);
DECLARE @negative_closing INT = (SELECT COUNT(*) FROM dbo.fact_inventory WHERE closing_stock < 0);

INSERT INTO @Results (section, check_name, status, detail)
SELECT 'Inventory Reconciliation', 'No negative opening_stock',
    CASE WHEN @negative_opening = 0 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Negative rows: ', @negative_opening)
UNION ALL SELECT 'Inventory Reconciliation', 'No negative closing_stock',
    CASE WHEN @negative_closing = 0 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Negative rows: ', @negative_closing);

-- ============================================================
-- SECTION 7: INVENTORY POLICY FORMULAS
-- Combined absolute + relative tolerance -- see file header.
-- ============================================================

DECLARE @atol DECIMAL(10,4) = 0.05;
DECLARE @rtol DECIMAL(10,6) = 0.001;
DECLARE @rop_failures INT, @target_failures INT;

SELECT @rop_failures = COUNT(*)
FROM (
    SELECT
        reorder_point,
        (demand_rate * lead_time_days) + safety_stock_units AS expected_rop
    FROM dbo.fact_inventory
) AS calc
WHERE ABS(reorder_point - expected_rop) > (@atol + @rtol * ABS(expected_rop));

SELECT @target_failures = COUNT(*)
FROM (
    SELECT
        target_stock_level,
        (demand_rate * lead_time_days)
        + (demand_rate * replenishment_interval_days)
        + safety_stock_units AS expected_target
    FROM dbo.fact_inventory
) AS calc
WHERE ABS(target_stock_level - expected_target) > (@atol + @rtol * ABS(expected_target));

INSERT INTO @Results (section, check_name, status, detail)
SELECT 'Inventory Policy', 'reorder_point = lead_time_demand + safety_stock_units',
    CASE WHEN @rop_failures = 0 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Formula failures: ', @rop_failures)
UNION ALL SELECT 'Inventory Policy', 'target_stock_level = lead_time_demand + review_period_demand + safety_stock_units',
    CASE WHEN @target_failures = 0 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Formula failures: ', @target_failures);

-- ============================================================
-- SECTION 8: STOCKOUT / STATUS CONSISTENCY
-- ============================================================

DECLARE @true_stockouts BIGINT = (SELECT COUNT(*) FROM dbo.fact_inventory WHERE stockout_event = 1);
DECLARE @low_stock_events BIGINT = (SELECT COUNT(*) FROM dbo.fact_inventory WHERE low_stock_event = 1);
DECLARE @invalid_status INT = (
    SELECT COUNT(*) FROM dbo.fact_inventory
    WHERE inventory_status NOT IN ('Healthy', 'Low Stock', 'Stockout', 'Overstock')
);

INSERT INTO @Results (section, check_name, status, detail)
SELECT 'Inventory Status', 'True stockout events (informational)',
    'INFO', CONCAT('Count: ', @true_stockouts, ' — expect 0, see 04_stockout_analysis.ipynb')
UNION ALL SELECT 'Inventory Status', 'Low-stock events (informational)',
    'INFO', CONCAT('Count: ', @low_stock_events, ' — expect 33,789')
UNION ALL SELECT 'Inventory Status', 'inventory_status values are all valid',
    CASE WHEN @invalid_status = 0 THEN 'PASS' ELSE 'FAIL' END,
    CONCAT('Invalid status rows: ', @invalid_status);

-- ============================================================
-- FINAL SUMMARY
-- ============================================================

SELECT section, check_name, status, detail
FROM @Results
ORDER BY check_id;

SELECT
    status,
    COUNT(*) AS check_count
FROM @Results
GROUP BY status
ORDER BY
    CASE status WHEN 'FAIL' THEN 1 WHEN 'PASS' THEN 2 WHEN 'INFO' THEN 3 END;

IF EXISTS (SELECT 1 FROM @Results WHERE status = 'FAIL')
    PRINT 'SQL DATA VALIDATION: ONE OR MORE CHECKS FAILED';
ELSE
    PRINT 'SQL DATA VALIDATION: ALL CHECKS PASSED';
GO