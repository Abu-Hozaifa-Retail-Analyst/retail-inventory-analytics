-- ============================================================
-- GulfMart Retail Inventory Analytics
-- 07_overstock_analysis.sql
-- ============================================================
-- T-SQL port of src/overstock_analysis.py / 05_overstock_analysis.ipynb.
-- Excess is defined against the inventory model's OWN policy target
-- (target_stock_level), not an external threshold -- same formula
-- as the Python phase:
--     Excess Units = MAX(closing_stock - target_stock_level, 0)
--     Excess Value = Excess Units * unit_cost
--
-- CASE WHEN is used in place of GREATEST()/LEAST() throughout (both
-- require SQL Server 2022+) for broader compatibility with whatever
-- edition this is running against.
--
-- Capital recapture (Section 6) is a RETROSPECTIVE COUNTERFACTUAL,
-- not a forecast -- same caveat as 05_overstock_analysis.ipynb: it
-- estimates the one-time order-quantity reduction at each historical
-- order event, holding everything else constant. It does not
-- re-simulate how a smaller order would change subsequent days'
-- closing stock or future reorder timing/sizing.
-- ============================================================

USE GulfMartRetailAnalytics;
GO

-- ============================================================
-- SECTION 1: Row-level excess value (temp table, reused below)
-- ============================================================

IF OBJECT_ID('tempdb..#InventoryExcess') IS NOT NULL DROP TABLE #InventoryExcess;

SELECT
    fi.[date],
    fi.store_id,
    fi.product_id,
    fi.closing_stock,
    fi.target_stock_level,
    fi.planned_order_quantity,
    p.unit_cost,
    p.category,
    p.demand_class,
    CASE WHEN fi.closing_stock > fi.target_stock_level
        THEN fi.closing_stock - fi.target_stock_level ELSE 0 END AS excess_units,
    CASE WHEN fi.closing_stock > fi.target_stock_level
        THEN (fi.closing_stock - fi.target_stock_level) * p.unit_cost ELSE 0 END AS excess_value,
    fi.closing_stock * p.unit_cost AS inventory_value
INTO #InventoryExcess
FROM dbo.fact_inventory fi
JOIN dbo.dim_product p ON fi.product_id = p.product_id;

CREATE CLUSTERED INDEX IX_InventoryExcess_product_date
    ON #InventoryExcess (product_id, [date]);

SELECT
    COUNT(*) AS rows_evaluated,
    SUM(CASE WHEN excess_units > 0 THEN 1 ELSE 0 END) AS rows_above_target,
    CAST(SUM(CASE WHEN excess_units > 0 THEN 1 ELSE 0 END) AS DECIMAL(18,4))
        / COUNT(*) * 100 AS rows_above_target_pct
FROM #InventoryExcess;

-- ============================================================
-- SECTION 2: Overall picture — excess as % of total inventory value
-- (time-averaged: average of each day's total, not a raw period sum)
-- ============================================================

WITH DailyTotals AS (
    SELECT
        [date],
        SUM(inventory_value) AS total_inventory_value,
        SUM(excess_value) AS total_excess_value
    FROM #InventoryExcess
    GROUP BY [date]
)
SELECT
    AVG(total_inventory_value) AS avg_daily_total_inventory_value,
    AVG(total_excess_value) AS avg_daily_total_excess_value,
    AVG(total_excess_value) / NULLIF(AVG(total_inventory_value), 0) * 100 AS excess_share_of_inventory_pct
FROM DailyTotals;

-- ============================================================
-- SECTION 3: Worst offenders — products
-- (time-averaged avg_excess_value per product)
-- ============================================================

WITH DailyProductExcess AS (
    SELECT product_id, [date], SUM(excess_units) AS daily_units, SUM(excess_value) AS daily_value
    FROM #InventoryExcess
    GROUP BY product_id, [date]
)
SELECT TOP 15
    p.product_id, p.product_name, p.category, p.demand_class,
    AVG(dpe.daily_units) AS avg_excess_units,
    AVG(dpe.daily_value) AS avg_excess_value
FROM DailyProductExcess dpe
JOIN dbo.dim_product p ON dpe.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.demand_class
ORDER BY avg_excess_value DESC;

-- ============================================================
-- SECTION 4: Worst offenders — stores (all 20, small enough to show in full)
-- ============================================================

WITH DailyStoreExcess AS (
    SELECT store_id, [date], SUM(excess_units) AS daily_units, SUM(excess_value) AS daily_value
    FROM #InventoryExcess
    GROUP BY store_id, [date]
)
SELECT
    st.store_id, st.store_name, st.store_type, st.region,
    AVG(dse.daily_units) AS avg_excess_units,
    AVG(dse.daily_value) AS avg_excess_value
FROM DailyStoreExcess dse
JOIN dbo.dim_store st ON dse.store_id = st.store_id
GROUP BY st.store_id, st.store_name, st.store_type, st.region
ORDER BY avg_excess_value DESC;

-- ============================================================
-- SECTION 5: Category breakdown & Pareto concentration
-- ============================================================

WITH DailyCategoryExcess AS (
    SELECT category, [date], SUM(excess_value) AS daily_value
    FROM #InventoryExcess
    GROUP BY category, [date]
)
SELECT
    category,
    AVG(daily_value) AS avg_excess_value
FROM DailyCategoryExcess
GROUP BY category
ORDER BY avg_excess_value DESC;

-- Pareto: how many products account for 80% of total avg excess value
IF OBJECT_ID('tempdb..#ProductExcessRanked') IS NOT NULL DROP TABLE #ProductExcessRanked;

WITH DailyProductExcess AS (
    SELECT product_id, [date], SUM(excess_value) AS daily_value
    FROM #InventoryExcess
    GROUP BY product_id, [date]
),
ProductAvgExcess AS (
    SELECT product_id, AVG(daily_value) AS avg_excess_value
    FROM DailyProductExcess
    GROUP BY product_id
)
SELECT
    product_id,
    avg_excess_value,
    SUM(avg_excess_value) OVER (ORDER BY avg_excess_value DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
        / SUM(avg_excess_value) OVER () * 100 AS cumulative_share_pct,
    ROW_NUMBER() OVER (ORDER BY avg_excess_value DESC) AS rank_desc
INTO #ProductExcessRanked
FROM ProductAvgExcess;

SELECT
    MIN(rank_desc) AS products_needed_for_80pct,
    (SELECT COUNT(*) FROM #ProductExcessRanked) AS total_products,
    CAST(MIN(rank_desc) AS DECIMAL(18,4)) / (SELECT COUNT(*) FROM #ProductExcessRanked) * 100 AS pct_of_catalog
FROM #ProductExcessRanked
WHERE cumulative_share_pct >= 80;

DROP TABLE #ProductExcessRanked;

-- ============================================================
-- SECTION 6: MOQ root-cause attribution (measured, not estimated)
-- At every actual replenishment order, compare what was ordered
-- against what the policy target called for at that moment.
-- ============================================================

IF OBJECT_ID('tempdb..#ReplenishmentEvents') IS NOT NULL DROP TABLE #ReplenishmentEvents;

SELECT
    [date], store_id, product_id, unit_cost,
    planned_order_quantity,
    target_stock_level,
    CASE WHEN planned_order_quantity > target_stock_level
        THEN planned_order_quantity - target_stock_level ELSE 0 END AS moq_overshoot_units,
    CASE WHEN planned_order_quantity > target_stock_level
        THEN (planned_order_quantity - target_stock_level) * unit_cost ELSE 0 END AS moq_overshoot_value
INTO #ReplenishmentEvents
FROM #InventoryExcess
WHERE planned_order_quantity > 0;

SELECT
    COUNT(*) AS total_replenishment_orders,
    SUM(CASE WHEN moq_overshoot_units > 0 THEN 1 ELSE 0 END) AS moq_inflated_orders,
    CAST(SUM(CASE WHEN moq_overshoot_units > 0 THEN 1 ELSE 0 END) AS DECIMAL(18,4))
        / COUNT(*) * 100 AS moq_inflated_order_share_pct,
    SUM(moq_overshoot_value) AS total_moq_overshoot_value
FROM #ReplenishmentEvents;

-- ============================================================
-- SECTION 7: Capital recapture what-if (RETROSPECTIVE, not a forecast)
-- capped_order = MIN(planned_order_quantity, cap_multiplier * target_stock_level),
--                never below target_stock_level
-- recaptured = planned_order_quantity - capped_order (clipped at 0)
-- Set-based via CROSS JOIN, same technique as the stress tests in
-- 06_stockout_analysis.sql.
-- ============================================================

SELECT
    m.cap_multiplier,
    SUM(
        re.planned_order_quantity - (
            CASE
                WHEN (CASE WHEN re.planned_order_quantity < (m.cap_multiplier * re.target_stock_level)
                           THEN re.planned_order_quantity
                           ELSE m.cap_multiplier * re.target_stock_level END) < re.target_stock_level
                THEN re.target_stock_level
                ELSE (CASE WHEN re.planned_order_quantity < (m.cap_multiplier * re.target_stock_level)
                           THEN re.planned_order_quantity
                           ELSE m.cap_multiplier * re.target_stock_level END)
            END
        )
    ) AS recaptured_units,
    SUM(
        (
            re.planned_order_quantity - (
                CASE
                    WHEN (CASE WHEN re.planned_order_quantity < (m.cap_multiplier * re.target_stock_level)
                               THEN re.planned_order_quantity
                               ELSE m.cap_multiplier * re.target_stock_level END) < re.target_stock_level
                    THEN re.target_stock_level
                    ELSE (CASE WHEN re.planned_order_quantity < (m.cap_multiplier * re.target_stock_level)
                               THEN re.planned_order_quantity
                               ELSE m.cap_multiplier * re.target_stock_level END)
                END
            )
        ) * re.unit_cost
    ) AS recaptured_value
FROM #ReplenishmentEvents re
CROSS JOIN (VALUES (1.5), (2.0), (3.0), (5.0)) AS m(cap_multiplier)
GROUP BY m.cap_multiplier
ORDER BY m.cap_multiplier;

DROP TABLE #ReplenishmentEvents;
DROP TABLE #InventoryExcess;
GO