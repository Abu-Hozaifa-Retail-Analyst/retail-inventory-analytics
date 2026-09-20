"""
GulfMart Retail Inventory Analytics
------------------------------------

Stockout / near-miss risk analysis module.

Purpose
-------
True stockout events in this dataset are ZERO (validated across all
10.96M fact_inventory rows: stockout_event never True, negative
inventory never occurs). This module therefore analyzes the closest
available signal -- low_stock_event (closing_stock <= reorder_point,
but still > 0) -- as a near-miss / risk-proximity indicator, and
provides a simplified what-if stress test estimating what conditions
(demand spikes, safety-stock cuts) WOULD have produced stockouts.

Important: the stress test is a static sensitivity proxy, not a
dynamic re-simulation. See stress_test_demand_spike() and
stress_test_safety_stock_cut() docstrings for exactly what it does
and does not account for.
"""

import numpy as np
import pandas as pd

from data_validation import print_section


# ============================================================
# 1. PRODUCT-STORE COMBO SUMMARY
# ============================================================


def build_combo_summary(fact_inventory, dim_product, dim_store):
    """
    Build one row per (store_id, product_id) combination summarizing
    its low-stock behavior and the static attributes needed for the
    stress tests.
    """

    print_section("Building Product-Store Combo Summary")

    combo_summary = fact_inventory.groupby(
        ["store_id", "product_id"], as_index=False
    ).agg(
        min_closing_stock=("closing_stock", "min"),
        low_stock_days=("low_stock_event", "sum"),
        total_days=("date", "count"),
        demand_rate=("demand_rate", "max"),
        lead_time_days=("lead_time_days", "max"),
        safety_stock_units=("safety_stock_units", "max"),
        supplier_id=("supplier_id", "max"),  # static per combo — added
    )
    coverage_clean = fact_inventory.assign(
        coverage_clean=fact_inventory["inventory_coverage_days"].replace(
            [np.inf, -np.inf], np.nan
        )
    )

    min_coverage = coverage_clean.groupby(["store_id", "product_id"])[
        "coverage_clean"
    ].min()

    combo_summary = combo_summary.merge(
        min_coverage.rename("min_coverage_days"),
        on=["store_id", "product_id"],
        how="left",
    )

    combo_summary["low_stock_pct"] = (
        combo_summary["low_stock_days"] / combo_summary["total_days"] * 100
    )

    combo_summary = combo_summary.merge(
        dim_product[["product_id", "product_name", "category", "demand_class"]],
        on="product_id",
        how="left",
    )

    combo_summary = combo_summary.merge(
        dim_store[["store_id", "store_name", "store_type", "region"]],
        on="store_id",
        how="left",
    )

    print(f"Combinations summarized: {len(combo_summary):,}")
    print(
        f"Combinations with at least one low-stock day: {(combo_summary['low_stock_days'] > 0).sum():,}"
    )

    return combo_summary


# ============================================================
# 2. LOW-STOCK RISK BREAKDOWNS
# ============================================================


def summarize_low_stock_by(combo_summary, group_column):
    """
    Aggregate low-stock behavior by a grouping column (e.g.
    'demand_class', 'category', 'store_type', 'region').

    Returns a DataFrame sorted by average low_stock_pct, descending.
    """

    summary = combo_summary.groupby(group_column, as_index=False).agg(
        combo_count=("low_stock_days", "size"),
        combos_with_low_stock=("low_stock_days", lambda s: (s > 0).sum()),
        avg_low_stock_pct=("low_stock_pct", "mean"),
        avg_min_coverage_days=("min_coverage_days", "mean"),
    )

    return summary.sort_values("avg_low_stock_pct", ascending=False).reset_index(
        drop=True
    )


# ============================================================
# 3. STRESS TEST: DEMAND SPIKE
# ============================================================


def stress_test_demand_spike(combo_summary, spike_factors=(1.5, 2, 3, 5, 10)):
    """
    Static sensitivity proxy: for each spike_factor, estimate how
    many product-store combinations WOULD have gone negative if
    demand had been spike_factor times higher for one lead-time
    window, AT THE COMBO'S ACTUAL HISTORICAL WORST MOMENT
    (min_closing_stock).

        extra_demand_during_leadtime
            = demand_rate * (spike_factor - 1) * lead_time_days

        would_stockout = min_closing_stock < extra_demand_during_leadtime

    This does NOT re-simulate the full 3-year trajectory or account
    for how replenishment orders would react to sustained higher
    demand -- it is a lower-bound fragility check against the worst
    moment that already happened, not a dynamic re-simulation.
    """

    print_section("Stress Test: Demand Spike")

    results = []

    for factor in spike_factors:
        extra_demand = (
            combo_summary["demand_rate"]
            * (factor - 1)
            * combo_summary["lead_time_days"]
        )

        would_stockout = combo_summary["min_closing_stock"] < extra_demand

        results.append(
            {
                "spike_factor": factor,
                "combos_would_stockout": int(would_stockout.sum()),
                "pct_would_stockout": would_stockout.mean() * 100,
            }
        )

        print(
            f"  {factor:>5.1f}x demand spike: "
            f"{would_stockout.sum():,} combos ({would_stockout.mean() * 100:.2f}%) would go negative"
        )

    return pd.DataFrame(results)


# ============================================================
# 4. STRESS TEST: SAFETY STOCK CUT
# ============================================================


def stress_test_safety_stock_cut(combo_summary, cut_percentages=(0.25, 0.5, 0.75, 1.0)):
    """
    Static sensitivity proxy: for each cut_percentages value,
    estimate how many product-store combinations WOULD have gone
    negative if that fraction of their safety-stock cushion had
    never existed, AT THE COMBO'S ACTUAL HISTORICAL WORST MOMENT.

        removed_cushion = safety_stock_units * cut_pct
        would_stockout = min_closing_stock < removed_cushion

    Same limitation as stress_test_demand_spike(): does not
    recompute how smaller safety stock would have changed order
    sizes or downstream trajectory.
    """

    print_section("Stress Test: Safety Stock Cut")

    results = []

    for cut in cut_percentages:
        removed_cushion = combo_summary["safety_stock_units"] * cut

        would_stockout = combo_summary["min_closing_stock"] < removed_cushion

        results.append(
            {
                "safety_stock_cut_pct": cut * 100,
                "combos_would_stockout": int(would_stockout.sum()),
                "pct_would_stockout": would_stockout.mean() * 100,
            }
        )

        print(
            f"  {cut * 100:>5.0f}% safety-stock cut: "
            f"{would_stockout.sum():,} combos ({would_stockout.mean() * 100:.2f}%) would go negative"
        )

    return pd.DataFrame(results)
