-- ============================================================
-- GulfMart Retail Inventory Analytics
-- 03_load_data.sql
-- ============================================================
-- Loads dimension tables and fact_sales via BULK INSERT.
-- fact_inventory is loaded separately via a Python script
-- (see src/sql_loader.py) -- not handled here. See README for why.
--
-- IMPORTANT: update the file paths below to your actual repo
-- location before running.
--
-- ROWTERMINATOR = '0x0d0a' (CRLF): source CSVs use Windows-style
-- line endings; '0x0a' alone leaves a stray \r on the last column
-- of every row.
-- ============================================================

USE GulfMartRetailAnalytics;
GO

TRUNCATE TABLE dbo.fact_sales;
TRUNCATE TABLE dbo.staging_fact_sales;
TRUNCATE TABLE dbo.staging_dim_date;
DELETE FROM dbo.dim_customer;
DELETE FROM dbo.dim_product;
DELETE FROM dbo.dim_store;
DELETE FROM dbo.dim_supplier;
DELETE FROM dbo.dim_date;
GO

-- ============================================================
-- dim_date
-- ============================================================

BULK INSERT dbo.staging_dim_date
FROM 'D:\GitHub\retail-inventory-analytics\data\raw\dim_date.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '0x0d0a', TABLOCK, CODEPAGE = '65001');
GO

INSERT INTO dbo.dim_date (
    [date], [year], quarter, [month], month_name, week_of_year,
    [day], day_name, day_of_week, is_weekend, season, is_ramadan, is_eid_period
)
SELECT
    [date], [year], quarter, [month], month_name, week_of_year,
    [day], day_name, day_of_week,
    CASE WHEN is_weekend = 'True' THEN 1 ELSE 0 END,
    season,
    CASE WHEN is_ramadan = 'True' THEN 1 ELSE 0 END,
    CASE WHEN is_eid_period = 'True' THEN 1 ELSE 0 END
FROM dbo.staging_dim_date;
GO

-- ============================================================
-- dim_supplier
-- ============================================================

BULK INSERT dbo.dim_supplier
FROM 'D:\GitHub\retail-inventory-analytics\data\cleaned\dim_supplier.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '0x0d0a', TABLOCK, CODEPAGE = '65001');
GO

-- ============================================================
-- dim_product
-- ============================================================

BULK INSERT dbo.dim_product
FROM 'D:\GitHub\retail-inventory-analytics\data\cleaned\dim_product.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '0x0d0a', TABLOCK, CODEPAGE = '65001');
GO

-- ============================================================
-- dim_store
-- ============================================================

BULK INSERT dbo.dim_store
FROM 'D:\GitHub\retail-inventory-analytics\data\cleaned\dim_store.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '0x0d0a', TABLOCK, CODEPAGE = '65001');
GO

-- ============================================================
-- dim_customer
-- ============================================================

BULK INSERT dbo.dim_customer
FROM 'D:\GitHub\retail-inventory-analytics\data\cleaned\dim_customer.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '0x0d0a', TABLOCK, CODEPAGE = '65001');
GO

-- ============================================================
-- staging_fact_sales
-- ============================================================

BULK INSERT dbo.staging_fact_sales
FROM 'D:\GitHub\retail-inventory-analytics\data\cleaned\fact_sales.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '0x0d0a', TABLOCK, CODEPAGE = '65001');
GO

PRINT 'Staging and dimension loads complete. Row counts:';

SELECT 'dim_date' AS table_name, COUNT(*) AS row_count FROM dbo.dim_date
UNION ALL SELECT 'dim_supplier', COUNT(*) FROM dbo.dim_supplier
UNION ALL SELECT 'dim_product', COUNT(*) FROM dbo.dim_product
UNION ALL SELECT 'dim_store', COUNT(*) FROM dbo.dim_store
UNION ALL SELECT 'dim_customer', COUNT(*) FROM dbo.dim_customer
UNION ALL SELECT 'staging_fact_sales', COUNT(*) FROM dbo.staging_fact_sales;
GO

-- ============================================================
-- Transform staging_fact_sales -> fact_sales (normalized)
-- is_ramadan / is_eid_period now carried through -- see
-- 02_create_tables.sql header note.
-- ============================================================

INSERT INTO dbo.fact_sales (
    transaction_id, transaction_date, product_id, store_id, customer_id,
    quantity, unit_price, discount_pct, gross_sales, discount_amount,
    net_sales, cogs, gross_profit, is_promotion, demand_spike,
    is_ramadan, is_eid_period
)
SELECT
    transaction_id, transaction_date, product_id, store_id, customer_id,
    quantity, unit_price, discount_pct, gross_sales, discount_amount,
    net_sales, cogs, gross_profit,
    CASE WHEN is_promotion = 'True' THEN 1 ELSE 0 END,
    CASE WHEN demand_spike = 'True' THEN 1 ELSE 0 END,
    CASE WHEN is_ramadan = 'True' THEN 1 ELSE 0 END,
    CASE WHEN is_eid_period = 'True' THEN 1 ELSE 0 END
FROM dbo.staging_fact_sales;
GO

PRINT 'fact_sales populated from staging. Row count:';
SELECT COUNT(*) AS fact_sales_row_count FROM dbo.fact_sales;
GO