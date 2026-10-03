
-- ============================================================
-- GulfMart Retail Inventory Analytics
-- 05_inventory_kpis.sql
-- ============================================================
-- T-SQL port of src/inventory_kpis.py / 03_inventory_kpis.ipynb.
-- Same three grains (overall, product, store), same formulas, same
-- annualization convention (period COGS scaled by 365/period_days) --
-- a direct port, so results should match the Python notebook's
-- findings, not just be "similar."
--
-- beginning_inventory_units (Python's initial_opening_stock) is not
-- a persisted fact_inventory column in either CSV or SQL -- it is
-- recovered here as each product-store combination's OPENING_STOCK
-- on its earliest date, since that is exactly how the Python
-- simulation seeded it. Same ROW_NUMBER()-over-partition technique
-- already used in 04_data_validation.sql's continuity check.
--
-- Tolerance: none needed here -- these are aggregate SUM/AVG/COUNT
-- queries, not row-by-row formula re-derivation, so there is no
-- float32-rounding comparison risk like in 04_data_validation.sql.
-- ============================================================

USE GulfMartRetailAnalytics;
GO

DECLARE @PeriodDays INT = (SELECT COUNT(DISTINCT [date]) FROM dbo.fact_inventory);
DECLARE @ExcessThresholdDays INT = 365;

-- ============================================================
-- Shared building block: beginning inventory per combo
-- (opening_stock on each combo's earliest date)
-- ============================================================

IF OBJECT_ID('tempdb..#BeginningInventory') IS NOT NULL DROP TABLE #BeginningInventory;

SELECT store_id, product_id, opening_stock AS beginning_inventory_units
INTO #BeginningInventory
FROM (
    SELECT
        store_id, product_id, opening_stock,
        ROW_NUMBER() OVER (PARTITION BY store_id, product_id ORDER BY [date]) AS rn
    FROM dbo.fact_inventory
) ranked
WHERE rn = 1;

-- ============================================================
-- Shared building block: daily total inventory value/units
-- (needed for time-averaged, not period-summed, inventory value --
-- matches Python's groupby(date).mean() pattern)
-- ============================================================

IF OBJECT_ID('tempdb..#DailyInventoryTotals') IS NOT NULL DROP TABLE #DailyInventoryTotals;

SELECT
    fi.[date],
    SUM(fi.closing_stock * p.unit_cost) AS total_inventory_value,
    SUM(fi.closing_stock) AS total_inventory_units
INTO #DailyInventoryTotals
FROM dbo.fact_inventory fi
JOIN dbo.dim_product p ON fi.product_id = p.product_id
GROUP BY fi.[date];

-- ============================================================
-- SECTION 1: OVERALL KPIs
-- ============================================================

DECLARE @AvgInventoryValue DECIMAL(18,2) = (SELECT AVG(total_inventory_value) FROM #DailyInventoryTotals);
DECLARE @AvgInventoryUnits DECIMAL(18,2) = (SELECT AVG(CAST(total_inventory_units AS DECIMAL(18,2))) FROM #DailyInventoryTotals);
DECLARE @TotalCogsPeriod DECIMAL(18,2) = (SELECT SUM(cogs) FROM dbo.fact_sales);
DECLARE @AnnualizedCogs DECIMAL(18,2) = @TotalCogsPeriod / @PeriodDays * 365;
DECLARE @TurnoverAnnualized DECIMAL(18,6) =
    CASE WHEN @AvgInventoryValue > 0 THEN @AnnualizedCogs / @AvgInventoryValue ELSE NULL END;
DECLARE @DaysOfInventory DECIMAL(18,2) =
    CASE WHEN @TurnoverAnnualized > 0 THEN ROUND(365.0 / @TurnoverAnnualized, 2) ELSE NULL END;

DECLARE @TotalUnitsSold BIGINT = (SELECT SUM(sales_units) FROM dbo.fact_inventory);
DECLARE @BeginningInventoryTotal BIGINT = (SELECT SUM(beginning_inventory_units) FROM #BeginningInventory);
DECLARE @TotalReceipts BIGINT = (SELECT SUM(receipts) FROM dbo.fact_inventory);
DECLARE @SellThroughPct DECIMAL(10,4) =
    CASE WHEN (@BeginningInventoryTotal + @TotalReceipts) > 0
        THEN CAST(@TotalUnitsSold AS DECIMAL(18,4)) / (@BeginningInventoryTotal + @TotalReceipts) * 100
        ELSE NULL END;

DECLARE @StockoutRatePct DECIMAL(10,4) = (
    SELECT AVG(CAST(stockout_event AS DECIMAL(10,4))) * 100 FROM dbo.fact_inventory
);

DECLARE @AvgCoverageDays DECIMAL(18,4) = (SELECT AVG(inventory_coverage_days) FROM dbo.fact_inventory);

DECLARE @ExcessSharePct DECIMAL(10,4) = (
    SELECT
        CAST(SUM(CASE WHEN inventory_coverage_days > @ExcessThresholdDays THEN 1 ELSE 0 END) AS DECIMAL(18,4))
        / NULLIF(COUNT(inventory_coverage_days), 0) * 100
    FROM dbo.fact_inventory
);

DECLARE @GrossProfitTotal DECIMAL(18,2) = (SELECT SUM(gross_profit) FROM dbo.fact_sales);
DECLARE @NetSalesTotal DECIMAL(18,2) = (SELECT SUM(net_sales) FROM dbo.fact_sales);
DECLARE @GrossMarginPct DECIMAL(10,4) =
    CASE WHEN @NetSalesTotal > 0 THEN @GrossProfitTotal / @NetSalesTotal * 100 ELSE NULL END;
DECLARE @Gmroi DECIMAL(18,6) =
    CASE WHEN @AvgInventoryValue > 0 THEN @GrossProfitTotal / @AvgInventoryValue ELSE NULL END;

DECLARE @DeadStockCombos INT = (
    SELECT COUNT(*) FROM (
        SELECT store_id, product_id
        FROM dbo.fact_inventory
        GROUP BY store_id, product_id
        HAVING SUM(sales_units) = 0
    ) dead
);
DECLARE @TotalCombos INT = (
    SELECT COUNT(*) FROM (SELECT DISTINCT store_id, product_id FROM dbo.fact_inventory) c
);
DECLARE @DeadStockSharePct DECIMAL(10,4) =
    CAST(@DeadStockCombos AS DECIMAL(18,4)) / @TotalCombos * 100;

SELECT
    @PeriodDays AS period_days,
    @AvgInventoryUnits AS avg_inventory_units,
    @AvgInventoryValue AS avg_inventory_value,
    @AnnualizedCogs AS annualized_cogs,
    @TurnoverAnnualized AS inventory_turnover_annualized,
    @DaysOfInventory AS days_of_inventory,
    @SellThroughPct AS sell_through_pct,
    @StockoutRatePct AS stockout_rate_pct,
    (100 - @StockoutRatePct) AS in_stock_rate_pct,
    @AvgCoverageDays AS avg_coverage_days,
    @ExcessSharePct AS excess_inventory_share_pct,
    @GrossMarginPct AS gross_margin_pct,
    @Gmroi AS gmroi,
    @DeadStockCombos AS dead_stock_combo_count,
    @DeadStockSharePct AS dead_stock_combo_share_pct;

-- ============================================================
-- SECTION 2: PRODUCT-LEVEL KPIs
-- ============================================================

WITH DailyProductValue AS (
    SELECT fi.product_id, fi.[date],
        SUM(fi.closing_stock * p.unit_cost) AS daily_value,
        SUM(fi.closing_stock) AS daily_units
    FROM dbo.fact_inventory fi
    JOIN dbo.dim_product p ON fi.product_id = p.product_id
    GROUP BY fi.product_id, fi.[date]
),
ProductInventory AS (
    SELECT
        product_id,
        AVG(daily_value) AS avg_inventory_value,
        AVG(CAST(daily_units AS DECIMAL(18,2))) AS avg_inventory_units
    FROM DailyProductValue
    GROUP BY product_id
),
ProductSales AS (
    SELECT
        product_id,
        SUM(cogs) AS total_cogs,
        SUM(gross_profit) AS gross_profit,
        SUM(net_sales) AS net_sales,
        SUM(quantity) AS total_units_sold
    FROM dbo.fact_sales
    GROUP BY product_id
),
ProductInventoryFacts AS (
    SELECT
        fi.product_id,
        SUM(fi.receipts) AS total_receipts,
        AVG(CAST(fi.stockout_event AS DECIMAL(10,4))) * 100 AS stockout_rate_pct,
        AVG(fi.inventory_coverage_days) AS avg_coverage_days
    FROM dbo.fact_inventory fi
    GROUP BY fi.product_id
),
ProductBeginningInventory AS (
    SELECT product_id, SUM(beginning_inventory_units) AS beginning_inventory_units
    FROM #BeginningInventory
    GROUP BY product_id
),
ProductDeadStores AS (
    SELECT product_id, COUNT(*) AS dead_store_count
    FROM (
        SELECT product_id, store_id
        FROM dbo.fact_inventory
        GROUP BY product_id, store_id
        HAVING SUM(sales_units) = 0
    ) dead
    GROUP BY product_id
)
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.demand_class,
    inv.avg_inventory_units,
    inv.avg_inventory_value,
    bi.beginning_inventory_units,
    invf.total_receipts,
    invf.stockout_rate_pct,
    invf.avg_coverage_days,
    ISNULL(ds.dead_store_count, 0) AS dead_store_count,
    s.total_cogs,
    s.gross_profit,
    s.net_sales,
    s.total_units_sold,
    (s.total_cogs / @PeriodDays * 365) AS annualized_cogs,
    CASE WHEN inv.avg_inventory_value > 0
        THEN (s.total_cogs / @PeriodDays * 365) / inv.avg_inventory_value
        ELSE NULL END AS inventory_turnover_annualized,
        CASE WHEN inv.avg_inventory_value > 0 AND
        ((s.total_cogs / @PeriodDays * 365) / inv.avg_inventory_value) > 0
        THEN ROUND(365.0 / ((s.total_cogs / @PeriodDays * 365) / inv.avg_inventory_value), 2)
        ELSE NULL END AS days_of_inventory,
    CASE WHEN (ISNULL(bi.beginning_inventory_units, 0) + ISNULL(invf.total_receipts, 0)) > 0
        THEN CAST(s.total_units_sold AS DECIMAL(18,4))
             / (ISNULL(bi.beginning_inventory_units, 0) + ISNULL(invf.total_receipts, 0)) * 100
        ELSE NULL END AS sell_through_pct,
    CASE WHEN s.net_sales > 0 THEN s.gross_profit / s.net_sales * 100 ELSE NULL END AS gross_margin_pct,
    CASE WHEN inv.avg_inventory_value > 0 THEN s.gross_profit / inv.avg_inventory_value ELSE NULL END AS gmroi,
    CASE WHEN invf.avg_coverage_days > @ExcessThresholdDays THEN 1 ELSE 0 END AS is_excess_inventory
FROM dbo.dim_product p
LEFT JOIN ProductInventory inv ON p.product_id = inv.product_id
LEFT JOIN ProductSales s ON p.product_id = s.product_id
LEFT JOIN ProductInventoryFacts invf ON p.product_id = invf.product_id
LEFT JOIN ProductBeginningInventory bi ON p.product_id = bi.product_id
LEFT JOIN ProductDeadStores ds ON p.product_id = ds.product_id
ORDER BY inventory_turnover_annualized DESC;

-- ============================================================
-- SECTION 3: STORE-LEVEL KPIs
-- ============================================================

WITH DailyStoreValue AS (
    SELECT fi.store_id, fi.[date],
        SUM(fi.closing_stock * p.unit_cost) AS daily_value,
        SUM(fi.closing_stock) AS daily_units
    FROM dbo.fact_inventory fi
    JOIN dbo.dim_product p ON fi.product_id = p.product_id
    GROUP BY fi.store_id, fi.[date]
),
StoreInventory AS (
    SELECT
        store_id,
        AVG(daily_value) AS avg_inventory_value,
        AVG(CAST(daily_units AS DECIMAL(18,2))) AS avg_inventory_units
    FROM DailyStoreValue
    GROUP BY store_id
),
StoreSales AS (
    SELECT
        store_id,
        SUM(cogs) AS total_cogs,
        SUM(gross_profit) AS gross_profit,
        SUM(net_sales) AS net_sales,
        SUM(quantity) AS total_units_sold
    FROM dbo.fact_sales
    GROUP BY store_id
),
StoreInventoryFacts AS (
    SELECT
        store_id,
        SUM(receipts) AS total_receipts,
        AVG(CAST(stockout_event AS DECIMAL(10,4))) * 100 AS stockout_rate_pct,
        AVG(inventory_coverage_days) AS avg_coverage_days
    FROM dbo.fact_inventory
    GROUP BY store_id
),
StoreBeginningInventory AS (
    SELECT store_id, SUM(beginning_inventory_units) AS beginning_inventory_units
    FROM #BeginningInventory
    GROUP BY store_id
),
StoreDeadProducts AS (
    SELECT store_id, COUNT(*) AS dead_product_count
    FROM (
        SELECT store_id, product_id
        FROM dbo.fact_inventory
        GROUP BY store_id, product_id
        HAVING SUM(sales_units) = 0
    ) dead
    GROUP BY store_id
)
SELECT
    st.store_id,
    st.store_name,
    st.store_type,
    st.region,
    inv.avg_inventory_units,
    inv.avg_inventory_value,
    bi.beginning_inventory_units,
    invf.total_receipts,
    invf.stockout_rate_pct,
    invf.avg_coverage_days,
    ISNULL(dp.dead_product_count, 0) AS dead_product_count,
    s.total_cogs,
    s.gross_profit,
    s.net_sales,
    s.total_units_sold,
    (s.total_cogs / @PeriodDays * 365) AS annualized_cogs,
    CASE WHEN inv.avg_inventory_value > 0
        THEN (s.total_cogs / @PeriodDays * 365) / inv.avg_inventory_value
        ELSE NULL END AS inventory_turnover_annualized,
        CASE WHEN inv.avg_inventory_value > 0 AND
        ((s.total_cogs / @PeriodDays * 365) / inv.avg_inventory_value) > 0
        THEN ROUND(365.0 / ((s.total_cogs / @PeriodDays * 365) / inv.avg_inventory_value), 2)
        ELSE NULL END AS days_of_inventory,
    CASE WHEN (ISNULL(bi.beginning_inventory_units, 0) + ISNULL(invf.total_receipts, 0)) > 0
        THEN CAST(s.total_units_sold AS DECIMAL(18,4))
             / (ISNULL(bi.beginning_inventory_units, 0) + ISNULL(invf.total_receipts, 0)) * 100
        ELSE NULL END AS sell_through_pct,
    CASE WHEN s.net_sales > 0 THEN s.gross_profit / s.net_sales * 100 ELSE NULL END AS gross_margin_pct,
    CASE WHEN inv.avg_inventory_value > 0 THEN s.gross_profit / inv.avg_inventory_value ELSE NULL END AS gmroi,
    CASE WHEN invf.avg_coverage_days > @ExcessThresholdDays THEN 1 ELSE 0 END AS is_excess_inventory
FROM dbo.dim_store st
LEFT JOIN StoreInventory inv ON st.store_id = inv.store_id
LEFT JOIN StoreSales s ON st.store_id = s.store_id
LEFT JOIN StoreInventoryFacts invf ON st.store_id = invf.store_id
LEFT JOIN StoreBeginningInventory bi ON st.store_id = bi.store_id
LEFT JOIN StoreDeadProducts dp ON st.store_id = dp.store_id
ORDER BY inventory_turnover_annualized DESC;

DROP TABLE #BeginningInventory;
DROP TABLE #DailyInventoryTotals;
GO