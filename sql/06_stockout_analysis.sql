-- ============================================================
-- GulfMart Retail Inventory Analytics
-- 06_stockout_analysis.sql
-- ============================================================
-- T-SQL port of src/stockout_analysis.py / 04_stockout_analysis.ipynb.
-- True stockouts are zero (confirmed below) -- this script analyzes
-- the same near-miss signal (low_stock_event) and reproduces the
-- same two retrospective stress tests.
--
-- Stress tests use a CROSS JOIN against a small VALUES table of
-- factors/cut-percentages, aggregated with conditional SUM -- this
-- computes every scenario in ONE set-based query instead of looping
-- per factor the way the Python version iterates. Same formulas,
-- same "retrospective sensitivity, not a forecast" caveat as
-- src/stockout_analysis.py's docstrings.
-- ============================================================

USE GulfMartRetailAnalytics;
GO

-- ============================================================
-- SECTION 1: Confirm zero true stockouts
-- ============================================================

SELECT
    SUM(CAST(stockout_event AS INT)) AS true_stockout_events,
    SUM(CASE WHEN closing_stock < 0 THEN 1 ELSE 0 END) AS negative_closing_stock_rows,
    SUM(CAST(low_stock_event AS INT)) AS low_stock_events,
    CAST(AVG(CAST(low_stock_event AS DECIMAL(10,6))) * 100 AS DECIMAL(10,4)) AS low_stock_event_rate_pct
FROM dbo.fact_inventory;

-- ============================================================
-- SECTION 2: Combo summary (one row per store_id, product_id)
-- ============================================================

IF OBJECT_ID('tempdb..#ComboSummary') IS NOT NULL DROP TABLE #ComboSummary;

SELECT
    fi.store_id,
    fi.product_id,
    fi.supplier_id,
    MIN(fi.closing_stock) AS min_closing_stock,
    SUM(CAST(fi.low_stock_event AS INT)) AS low_stock_days,
    COUNT(*) AS total_days,
    MAX(fi.demand_rate) AS demand_rate,            -- static per combo
    MAX(fi.lead_time_days) AS lead_time_days,       -- static per combo
    MAX(fi.safety_stock_units) AS safety_stock_units, -- static per combo
    MIN(NULLIF(fi.inventory_coverage_days, 0)) AS min_coverage_days
INTO #ComboSummary
FROM dbo.fact_inventory fi
GROUP BY fi.store_id, fi.product_id, fi.supplier_id;

ALTER TABLE #ComboSummary ADD low_stock_pct AS (
    CAST(low_stock_days AS DECIMAL(10,6)) / total_days * 100
);

SELECT
    COUNT(*) AS combinations_summarized,
    SUM(CASE WHEN low_stock_days > 0 THEN 1 ELSE 0 END) AS combinations_with_low_stock
FROM #ComboSummary;

-- ============================================================
-- SECTION 3: Risk breakdowns
-- ============================================================

-- By demand class
SELECT
    p.demand_class,
    COUNT(*) AS combo_count,
    SUM(CASE WHEN cs.low_stock_days > 0 THEN 1 ELSE 0 END) AS combos_with_low_stock,
    AVG(cs.low_stock_pct) AS avg_low_stock_pct,
    AVG(cs.min_coverage_days) AS avg_min_coverage_days
FROM #ComboSummary cs
JOIN dbo.dim_product p ON cs.product_id = p.product_id
GROUP BY p.demand_class
ORDER BY avg_low_stock_pct DESC;

-- By category
SELECT
    p.category,
    COUNT(*) AS combo_count,
    SUM(CASE WHEN cs.low_stock_days > 0 THEN 1 ELSE 0 END) AS combos_with_low_stock,
    AVG(cs.low_stock_pct) AS avg_low_stock_pct,
    AVG(cs.min_coverage_days) AS avg_min_coverage_days
FROM #ComboSummary cs
JOIN dbo.dim_product p ON cs.product_id = p.product_id
GROUP BY p.category
ORDER BY avg_low_stock_pct DESC;

-- By store type and region
SELECT
    st.store_type,
    COUNT(*) AS combo_count,
    SUM(CASE WHEN cs.low_stock_days > 0 THEN 1 ELSE 0 END) AS combos_with_low_stock,
    AVG(cs.low_stock_pct) AS avg_low_stock_pct,
    AVG(cs.min_coverage_days) AS avg_min_coverage_days
FROM #ComboSummary cs
JOIN dbo.dim_store st ON cs.store_id = st.store_id
GROUP BY st.store_type
ORDER BY avg_low_stock_pct DESC;

SELECT
    st.region,
    COUNT(*) AS combo_count,
    SUM(CASE WHEN cs.low_stock_days > 0 THEN 1 ELSE 0 END) AS combos_with_low_stock,
    AVG(cs.low_stock_pct) AS avg_low_stock_pct,
    AVG(cs.min_coverage_days) AS avg_min_coverage_days
FROM #ComboSummary cs
JOIN dbo.dim_store st ON cs.store_id = st.store_id
GROUP BY st.region
ORDER BY avg_low_stock_pct DESC;

-- By supplier lead-time bucket and supplier region
SELECT
    CASE
        WHEN cs.lead_time_days <= 7 THEN 'Short (<=7d, Local-like)'
        WHEN cs.lead_time_days <= 14 THEN 'Medium (8-14d, Regional-like)'
        ELSE 'Long (>14d, International-like)'
    END AS lead_time_bucket,
    COUNT(*) AS combo_count,
    SUM(CASE WHEN cs.low_stock_days > 0 THEN 1 ELSE 0 END) AS combos_with_low_stock,
    AVG(cs.low_stock_pct) AS avg_low_stock_pct,
    AVG(cs.min_coverage_days) AS avg_min_coverage_days
FROM #ComboSummary cs
GROUP BY
    CASE
        WHEN cs.lead_time_days <= 7 THEN 'Short (<=7d, Local-like)'
        WHEN cs.lead_time_days <= 14 THEN 'Medium (8-14d, Regional-like)'
        ELSE 'Long (>14d, International-like)'
    END
ORDER BY avg_low_stock_pct DESC;

SELECT
    sup.supplier_region,
    COUNT(*) AS combo_count,
    SUM(CASE WHEN cs.low_stock_days > 0 THEN 1 ELSE 0 END) AS combos_with_low_stock,
    AVG(cs.low_stock_pct) AS avg_low_stock_pct,
    AVG(cs.min_coverage_days) AS avg_min_coverage_days
FROM #ComboSummary cs
JOIN dbo.dim_supplier sup ON cs.supplier_id = sup.supplier_id
GROUP BY sup.supplier_region
ORDER BY avg_low_stock_pct DESC;

-- ============================================================
-- SECTION 4: Near-miss deep dive
-- ============================================================

-- Top 10 by share of days in Low Stock status
SELECT TOP 10
    cs.store_id, cs.product_id, p.product_name, st.store_name,
    p.demand_class, cs.low_stock_pct, cs.min_coverage_days
FROM #ComboSummary cs
JOIN dbo.dim_product p ON cs.product_id = p.product_id
JOIN dbo.dim_store st ON cs.store_id = st.store_id
WHERE cs.low_stock_days > 0
ORDER BY cs.low_stock_pct DESC;

-- Top 10 by lowest minimum coverage days (closest to the edge)
SELECT TOP 10
    cs.store_id, cs.product_id, p.product_name, st.store_name,
    p.demand_class, cs.min_coverage_days, cs.low_stock_pct
FROM #ComboSummary cs
JOIN dbo.dim_product p ON cs.product_id = p.product_id
JOIN dbo.dim_store st ON cs.store_id = st.store_id
WHERE cs.low_stock_days > 0
ORDER BY cs.min_coverage_days ASC;

-- ============================================================
-- SECTION 5: Stress test — demand spike
-- Set-based: all 5 factors computed in one query via CROSS JOIN,
-- not a loop. extra_demand_during_leadtime =
--   demand_rate * (factor - 1) * lead_time_days
-- would_stockout = min_closing_stock < extra_demand_during_leadtime
-- Retrospective sensitivity proxy -- see 04_stockout_analysis.ipynb
-- for full limitation notes (static check against each combo's
-- actual historical worst moment, not a dynamic re-simulation).
-- ============================================================

SELECT
    f.spike_factor,
    SUM(CASE
        WHEN cs.min_closing_stock < (cs.demand_rate * (f.spike_factor - 1) * cs.lead_time_days)
        THEN 1 ELSE 0
    END) AS combos_would_stockout,
    CAST(
        SUM(CASE
            WHEN cs.min_closing_stock < (cs.demand_rate * (f.spike_factor - 1) * cs.lead_time_days)
            THEN 1 ELSE 0
        END) AS DECIMAL(18,4)
    ) / COUNT(*) * 100 AS pct_would_stockout
FROM #ComboSummary cs
CROSS JOIN (VALUES (1.5), (2.0), (3.0), (5.0), (10.0)) AS f(spike_factor)
GROUP BY f.spike_factor
ORDER BY f.spike_factor;

-- ============================================================
-- SECTION 6: Stress test — safety stock cut
-- removed_cushion = safety_stock_units * cut_pct
-- would_stockout = min_closing_stock < removed_cushion
-- ============================================================

SELECT
    c.cut_pct * 100 AS safety_stock_cut_pct,
    SUM(CASE
        WHEN cs.min_closing_stock < (cs.safety_stock_units * c.cut_pct)
        THEN 1 ELSE 0
    END) AS combos_would_stockout,
    CAST(
        SUM(CASE
            WHEN cs.min_closing_stock < (cs.safety_stock_units * c.cut_pct)
            THEN 1 ELSE 0
        END) AS DECIMAL(18,4)
    ) / COUNT(*) * 100 AS pct_would_stockout
FROM #ComboSummary cs
CROSS JOIN (VALUES (0.25), (0.5), (0.75), (1.0)) AS c(cut_pct)
GROUP BY c.cut_pct
ORDER BY c.cut_pct;

DROP TABLE #ComboSummary;
GO