-- ============================================================
-- GulfMart Retail Inventory Analytics
-- 08_replenishment_analysis.sql
-- ============================================================
-- T-SQL port of src/replenishment_analysis.py / 07_replenishment_
-- analysis.ipynb -- the capstone script. Measures the deepest root
-- cause (inventory-position netting flaw) and builds the final
-- Replenishment Action List.
--
-- GO separators added between sections: SQL Server does not allow a
-- computed column to reference another computed column in the same
-- ALTER TABLE sequence (hit this directly below, fixed by inlining
-- the expression instead of chaining it) -- separating into batches
-- also means a failure in one section cannot silently cascade into
-- the next the way it did without GO boundaries.
-- ============================================================

USE GulfMartRetailAnalytics;
GO

-- ============================================================
-- SECTION 1: Netting overshoot (deepest root-cause measurement)
-- ============================================================

IF OBJECT_ID('tempdb..#ReplenishmentEvents') IS NOT NULL DROP TABLE #ReplenishmentEvents;

SELECT
    fi.[date], fi.store_id, fi.product_id,
    p.unit_cost,
    fi.opening_stock,
    fi.target_stock_level,
    fi.planned_order_quantity,
    fi.minimum_order_qty,
    CASE
        WHEN fi.opening_stock >= fi.target_stock_level THEN 0
        ELSE CASE
            WHEN (fi.target_stock_level - fi.opening_stock) > fi.minimum_order_qty
            THEN fi.target_stock_level - fi.opening_stock
            ELSE fi.minimum_order_qty
        END
    END AS ideal_order,
    CASE WHEN fi.planned_order_quantity > fi.target_stock_level
        THEN fi.planned_order_quantity - fi.target_stock_level ELSE 0 END AS moq_overshoot_units
INTO #ReplenishmentEvents
FROM dbo.fact_inventory fi
JOIN dbo.dim_product p ON fi.product_id = p.product_id
WHERE fi.planned_order_quantity > 0;
GO

-- netting_overshoot_value is inlined as ONE expression (not chained
-- through netting_overshoot_units) -- SQL Server does not allow a
-- computed column to reference another computed column.
ALTER TABLE #ReplenishmentEvents ADD netting_overshoot_units AS (
    CASE WHEN (planned_order_quantity - ideal_order) > 0
        THEN planned_order_quantity - ideal_order ELSE 0 END
);
GO

ALTER TABLE #ReplenishmentEvents ADD netting_overshoot_value AS (
    (CASE WHEN (planned_order_quantity - ideal_order) > 0
        THEN planned_order_quantity - ideal_order ELSE 0 END) * unit_cost
);
GO

-- moq_overshoot_units is a real (non-computed) column from the
-- SELECT INTO above, so referencing it here is fine -- no chaining.
ALTER TABLE #ReplenishmentEvents ADD moq_overshoot_value AS (
    moq_overshoot_units * unit_cost
);
GO

SELECT
    COUNT(*) AS total_replenishment_orders,
    SUM(CASE WHEN ideal_order = 0 THEN 1 ELSE 0 END) AS orders_should_not_have_been_placed,
    CAST(SUM(CASE WHEN ideal_order = 0 THEN 1 ELSE 0 END) AS DECIMAL(18,4))
        / COUNT(*) * 100 AS orders_should_not_have_been_placed_pct,
    SUM(netting_overshoot_value) AS total_netting_overshoot_value,
    SUM(moq_overshoot_value) AS total_moq_overshoot_value,
    SUM(netting_overshoot_value) / NULLIF(SUM(moq_overshoot_value), 0) AS netting_to_moq_ratio
FROM #ReplenishmentEvents;
GO

-- ============================================================
-- SECTION 2: Combo-level excess tier (High / Medium / Low)
-- ============================================================

IF OBJECT_ID('tempdb..#ComboExcessTiered') IS NOT NULL DROP TABLE #ComboExcessTiered;

WITH InventoryExcess AS (
    SELECT
        fi.[date], fi.store_id, fi.product_id,
        CASE WHEN fi.closing_stock > fi.target_stock_level
            THEN (fi.closing_stock - fi.target_stock_level) * p.unit_cost ELSE 0 END AS excess_value
    FROM dbo.fact_inventory fi
    JOIN dbo.dim_product p ON fi.product_id = p.product_id
),
DailyComboExcess AS (
    SELECT store_id, product_id, [date], SUM(excess_value) AS daily_value
    FROM InventoryExcess
    GROUP BY store_id, product_id, [date]
),
ComboAvgExcess AS (
    SELECT store_id, product_id, AVG(daily_value) AS avg_excess_value
    FROM DailyComboExcess
    GROUP BY store_id, product_id
),
ComboRanked AS (
    SELECT
        store_id, product_id, avg_excess_value,
        CASE WHEN avg_excess_value > 0 THEN
            SUM(CASE WHEN avg_excess_value > 0 THEN avg_excess_value ELSE 0 END)
                OVER (ORDER BY avg_excess_value DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
            / NULLIF(SUM(CASE WHEN avg_excess_value > 0 THEN avg_excess_value ELSE 0 END) OVER (), 0) * 100
        ELSE NULL END AS cumulative_share_pct
    FROM ComboAvgExcess
)
SELECT
    store_id, product_id, avg_excess_value,
    CASE
        WHEN avg_excess_value <= 0 THEN 'Low'
        WHEN cumulative_share_pct <= 80 THEN 'High'
        WHEN cumulative_share_pct <= 95 THEN 'Medium'
        ELSE 'Low'
    END AS excess_tier
INTO #ComboExcessTiered
FROM ComboRanked;
GO

SELECT excess_tier, COUNT(*) AS combo_count
FROM #ComboExcessTiered
GROUP BY excess_tier
ORDER BY CASE excess_tier WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END;
GO

-- ============================================================
-- SECTION 3: Product-level ABC classification (by annual COGS)
-- ============================================================

IF OBJECT_ID('tempdb..#ProductAbcClassified') IS NOT NULL DROP TABLE #ProductAbcClassified;

DECLARE @PeriodDays INT = (SELECT COUNT(DISTINCT [date]) FROM dbo.fact_inventory);

WITH ProductCogs AS (
    SELECT
        p.product_id,
        ISNULL(SUM(fs.cogs), 0) / @PeriodDays * 365 AS annual_cogs
    FROM dbo.dim_product p
    LEFT JOIN dbo.fact_sales fs ON p.product_id = fs.product_id
    GROUP BY p.product_id
),
ProductRanked AS (
    SELECT
        product_id, annual_cogs,
        CASE WHEN annual_cogs > 0 THEN
            SUM(CASE WHEN annual_cogs > 0 THEN annual_cogs ELSE 0 END)
                OVER (ORDER BY annual_cogs DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
            / NULLIF(SUM(CASE WHEN annual_cogs > 0 THEN annual_cogs ELSE 0 END) OVER (), 0) * 100
        ELSE NULL END AS cumulative_share_pct
    FROM ProductCogs
)
SELECT
    product_id, annual_cogs,
    CASE
        WHEN annual_cogs <= 0 THEN 'C'
        WHEN cumulative_share_pct <= 80 THEN 'A'
        WHEN cumulative_share_pct <= 95 THEN 'B'
        ELSE 'C'
    END AS annual_cogs_class
INTO #ProductAbcClassified
FROM ProductRanked;
GO

SELECT annual_cogs_class, COUNT(*) AS product_count, SUM(annual_cogs) AS total_annual_cogs
FROM #ProductAbcClassified
GROUP BY annual_cogs_class
ORDER BY annual_cogs_class;
GO

-- ============================================================
-- SECTION 4: Stockout-risk combo summary
-- ============================================================

IF OBJECT_ID('tempdb..#ComboRisk') IS NOT NULL DROP TABLE #ComboRisk;

SELECT
    store_id, product_id,
    SUM(CAST(low_stock_event AS INT)) AS low_stock_days,
    COUNT(*) AS total_days,
    CAST(SUM(CAST(low_stock_event AS INT)) AS DECIMAL(10,6)) / COUNT(*) * 100 AS low_stock_pct,
    MIN(NULLIF(inventory_coverage_days, 0)) AS min_coverage_days
INTO #ComboRisk
FROM dbo.fact_inventory
GROUP BY store_id, product_id;
GO

-- ============================================================
-- SECTION 5: Build and materialize the Replenishment Action List
-- ============================================================

IF OBJECT_ID('dbo.replenishment_action_list', 'U') IS NOT NULL
    DROP TABLE dbo.replenishment_action_list;

SELECT
    cr.store_id,
    cr.product_id,
    st.store_name,
    st.store_type,
    st.region,
    p.product_name,
    p.category,
    p.demand_class,
    abc.annual_cogs_class,
    cet.avg_excess_value,
    cet.excess_tier,
    cr.low_stock_pct,
    cr.min_coverage_days,
    CASE
        WHEN cr.low_stock_pct > 0 AND abc.annual_cogs_class = 'A' THEN 'EXPEDITE'
        WHEN cr.low_stock_pct > 0 THEN 'MAINTAIN'
        WHEN cet.excess_tier = 'High' THEN 'SUPPRESS'
        WHEN cet.excess_tier = 'Medium' THEN 'REDUCE'
        ELSE 'MAINTAIN'
    END AS recommended_action
INTO dbo.replenishment_action_list
FROM #ComboRisk cr
JOIN #ComboExcessTiered cet ON cr.store_id = cet.store_id AND cr.product_id = cet.product_id
JOIN #ProductAbcClassified abc ON cr.product_id = abc.product_id
JOIN dbo.dim_product p ON cr.product_id = p.product_id
JOIN dbo.dim_store st ON cr.store_id = st.store_id;
GO

SELECT
    recommended_action,
    COUNT(*) AS combo_count,
    CAST(COUNT(*) AS DECIMAL(18,4)) / (SELECT COUNT(*) FROM dbo.replenishment_action_list) * 100 AS pct_of_combos
FROM dbo.replenishment_action_list
GROUP BY recommended_action
ORDER BY combo_count DESC;
GO

-- ============================================================
-- SECTION 6: Drill-downs
-- ============================================================

SELECT TOP 15 store_id, product_id, product_name, store_name, avg_excess_value, annual_cogs_class
FROM dbo.replenishment_action_list
WHERE recommended_action = 'SUPPRESS'
ORDER BY avg_excess_value DESC;

SELECT TOP 15 store_id, product_id, product_name, store_name, low_stock_pct, min_coverage_days
FROM dbo.replenishment_action_list
WHERE recommended_action = 'EXPEDITE'
ORDER BY low_stock_pct DESC;
GO

-- ============================================================
-- SECTION 7: Retrospective recapture by action (not a forecast)
-- ============================================================

SELECT
    ral.recommended_action,
    SUM(re.netting_overshoot_value) AS total_netting_overshoot_value
FROM #ReplenishmentEvents re
JOIN dbo.replenishment_action_list ral
    ON re.store_id = ral.store_id AND re.product_id = ral.product_id
GROUP BY ral.recommended_action
ORDER BY total_netting_overshoot_value DESC;
GO

SELECT
    SUM(re.netting_overshoot_value) AS suppress_reduce_recoverable_value
FROM #ReplenishmentEvents re
JOIN dbo.replenishment_action_list ral
    ON re.store_id = ral.store_id AND re.product_id = ral.product_id
WHERE ral.recommended_action IN ('SUPPRESS', 'REDUCE');
GO

DROP TABLE #ReplenishmentEvents;
DROP TABLE #ComboExcessTiered;
DROP TABLE #ProductAbcClassified;
DROP TABLE #ComboRisk;
GO

SELECT COUNT(*) AS replenishment_action_list_row_count FROM dbo.replenishment_action_list;
GO

PRINT 'dbo.replenishment_action_list created and populated.';
GO