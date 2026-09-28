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
-- ROWTERMINATOR = '0x0d0a' (CRLF), not '0x0a' (LF only): the
-- source CSVs use Windows-style CRLF line endings. Using '0x0a'
-- alone leaves a stray \r attached to each row's LAST column,
-- which numeric columns silently tolerate (trimmed on conversion)
-- but VARCHAR columns do not -- causing a "truncation" error
-- whenever the last column is text (as happened with dim_date's
-- is_eid_period). Fixed here for every table, not just the one
-- that errored, since the same stray \r was silently present in
-- every load.
--
-- Source folders, deliberately mixed (matches the same choice made
-- consistently across every analysis notebook in this project):
--   dim_product, dim_store, dim_customer, dim_supplier, fact_sales
--     -> data/cleaned/
--   dim_date -> data/raw/ (never touched by cleaning)
-- ============================================================

USE GulfMartRetailAnalytics;
GO

-- ============================================================
-- Truncate before reload (idempotent re-run during development)
-- Order matters: fact tables before the dimensions they reference.
-- ============================================================

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
-- dim_date  (from data/raw/ — staged, then converted True/False -> BIT)
-- ============================================================

BULK INSERT dbo.staging_dim_date
FROM 'D:\GitHub\retail-inventory-analytics\data\raw\dim_date.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0d0a',
    TABLOCK,
    CODEPAGE = '65001'
);
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
-- dim_supplier  (from data/cleaned/ — imputed supplier_name)
-- ============================================================

BULK INSERT dbo.dim_supplier
FROM 'D:\GitHub\retail-inventory-analytics\data\cleaned\dim_supplier.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0d0a',
    TABLOCK,
    CODEPAGE = '65001'
);
GO

-- ============================================================
-- dim_product  (from data/cleaned/)
-- ============================================================

BULK INSERT dbo.dim_product
FROM 'D:\GitHub\retail-inventory-analytics\data\cleaned\dim_product.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0d0a',
    TABLOCK,
    CODEPAGE = '65001'
);
GO

-- ============================================================
-- dim_store  (from data/cleaned/ — text-normalized city)
-- ============================================================

BULK INSERT dbo.dim_store
FROM 'D:\GitHub\retail-inventory-analytics\data\cleaned\dim_store.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0d0a',
    TABLOCK,
    CODEPAGE = '65001'
);
GO

-- ============================================================
-- dim_customer  (from data/cleaned/ — imputed city)
-- ============================================================

BULK INSERT dbo.dim_customer
FROM 'D:\GitHub\retail-inventory-analytics\data\cleaned\dim_customer.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0d0a',
    TABLOCK,
    CODEPAGE = '65001'
);
GO

-- ============================================================
-- staging_fact_sales  (from data/cleaned/ — duplicates removed,
-- 125,000 rows)
-- ============================================================

BULK INSERT dbo.staging_fact_sales
FROM 'D:\GitHub\retail-inventory-analytics\data\cleaned\fact_sales.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0d0a',
    TABLOCK,
    CODEPAGE = '65001'
);
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
-- ============================================================

INSERT INTO dbo.fact_sales (
    transaction_id, transaction_date, product_id, store_id, customer_id,
    quantity, unit_price, discount_pct, gross_sales, discount_amount,
    net_sales, cogs, gross_profit, is_promotion, demand_spike
)
SELECT
    transaction_id, transaction_date, product_id, store_id, customer_id,
    quantity, unit_price, discount_pct, gross_sales, discount_amount,
    net_sales, cogs, gross_profit,
    CASE WHEN is_promotion = 'True' THEN 1 ELSE 0 END,
    CASE WHEN demand_spike = 'True' THEN 1 ELSE 0 END
FROM dbo.staging_fact_sales;
GO

PRINT 'fact_sales populated from staging. Row count:';
SELECT COUNT(*) AS fact_sales_row_count FROM dbo.fact_sales;
GO

USE GulfMartRetailAnalytics;
GO

SELECT 'dim_date' AS table_name, COUNT(*) AS row_count FROM dbo.dim_date
UNION ALL SELECT 'dim_supplier', COUNT(*) FROM dbo.dim_supplier
UNION ALL SELECT 'dim_product', COUNT(*) FROM dbo.dim_product
UNION ALL SELECT 'dim_store', COUNT(*) FROM dbo.dim_store
UNION ALL SELECT 'dim_customer', COUNT(*) FROM dbo.dim_customer
UNION ALL SELECT 'fact_sales', COUNT(*) FROM dbo.fact_sales
UNION ALL SELECT 'fact_inventory', COUNT(*) FROM dbo.fact_inventory;

-- ============================================================
-- TROUBLESHOOTING: "Access is denied" on BULK INSERT
-- ============================================================
-- BULK INSERT runs as the SQL Server SERVICE ACCOUNT, not your
-- Windows login -- so a file readable in your own File Explorer
-- can still be denied to SQL Server. Fixes, in order of ease:
--   1. Right-click the data/ folder -> Properties -> Security ->
--      grant Read access to the SQL Server service account
--      (Services.msc -> SQL Server (MSSQLSERVER or your instance
--      name) -> Log On tab shows which account that is; often
--      "NT Service\MSSQLSERVER" for a default local install).
--   2. Or move/copy the CSVs to a folder already accessible to
--      that account (e.g. C:\SQLData\...).
--   3. Or, if using SQL Server Express/Developer locally with
--      mixed-mode auth, confirm you're not blocked by antivirus
--      real-time scanning on the folder.
-- ============================================================