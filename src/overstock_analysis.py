"""
GulfMart Retail Inventory Analytics
------------------------------------

Overstock / excess-inventory analysis module.

Purpose
-------
Quantifies the systemic overstock finding from 03_inventory_kpis.ipynb
in dollar terms, grounded in the inventory model's OWN replenishment
policy target rather than an external threshold:

    Excess Units = max(closing_stock - target_stock_level, 0)
    Excess Value = Excess Units * unit_cost

This module also attributes a portion of that excess specifically to
the supplier minimum-order-quantity (MOQ) floor, by comparing what was
actually ordered (planned_order_quantity) against what the replenishment
policy target called for (target_stock_level) at every real
replenishment event.

Important
---------
The capital-recapture "what-if" functions in this module (see
estimate_moq_cap_recapture()) are RETROSPECTIVE COUNTERFACTUALS on the
historical data already generated -- they estimate how much excess this
specific dataset would not have accumulated under a capped-MOQ rule.
They are not a forecast of future savings, and do not re-simulate how a
different ordering rule would have changed subsequent days' demand
fulfillment or reorder timing. State this plainly wherever these
numbers are reported.
"""

import numpy as np
import pandas as pd

from data_validation import print_section


# ============================================================
# 1. EXCESS INVENTORY VALUE
# ============================================================


def compute_excess_value(fact_inventory, dim_product):
    """
    Add excess_units and excess_value columns to fact_inventory,
    where excess is defined relative to the inventory model's own
    target_stock_level policy field (not an external threshold).

    Returns a NEW DataFrame; does not modify the input.
    """

    print_section("Computing Excess Inventory Value")

    fact_inventory_excess = fact_inventory.merge(
        dim_product[["product_id", "unit_cost", "category"]],
        on="product_id",
        how="left",
        validate="many_to_one",
    )

    fact_inventory_excess["excess_units"] = (
        fact_inventory_excess["closing_stock"]
        - fact_inventory_excess["target_stock_level"]
    ).clip(lower=0)

    fact_inventory_excess["excess_value"] = (
        fact_inventory_excess["excess_units"] * fact_inventory_excess["unit_cost"]
    )

    rows_with_excess = (fact_inventory_excess["excess_units"] > 0).sum()

    print(f"Rows: {len(fact_inventory_excess):,}")
    print(
        f"Rows above target_stock_level: {rows_with_excess:,} "
        f"({rows_with_excess / len(fact_inventory_excess):.1%})"
    )
    print(
        f"Total excess_value across all rows (period-cumulative, not a "
        f"balance): {fact_inventory_excess['excess_value'].sum():,.2f}"
    )

    return fact_inventory_excess


# ============================================================
# 2. AVERAGE EXCESS VALUE BY GRAIN
# ============================================================


def summarize_excess_by(fact_inventory_excess, group_column):
    """
    Time-averaged excess units/value by a grouping column
    (e.g. 'product_id', 'store_id', 'category', 'demand_class').

    Time-averaging (average of each day's group total, not a raw sum
    across all rows) is used so the result represents a realistic
    "typical amount of capital tied up," not an artifact of how many
    days are in the period.

    Returns a DataFrame sorted by avg_excess_value, descending.
    """

    daily_totals = (
        fact_inventory_excess.groupby([group_column, "date"])
        .agg(
            excess_units=("excess_units", "sum"),
            excess_value=("excess_value", "sum"),
        )
        .reset_index()
    )

    summary = daily_totals.groupby(group_column).agg(
        avg_excess_units=("excess_units", "mean"),
        avg_excess_value=("excess_value", "mean"),
    )

    return summary.sort_values("avg_excess_value", ascending=False)


# ============================================================
# 3. MOQ ROOT-CAUSE ATTRIBUTION
# ============================================================


def compute_moq_attribution(fact_inventory_excess):
    """
    For every actual replenishment order (planned_order_quantity > 0),
    compare what was ordered against what the policy target called
    for at that moment (target_stock_level).

        moq_overshoot = max(planned_order_quantity - target_stock_level, 0)
        moq_overshoot_value = moq_overshoot * unit_cost

    A positive moq_overshoot means the order was inflated beyond the
    policy's own target -- almost always because minimum_order_qty
    exceeded target_stock_level (see generate_fact_inventory() Step
    10G in data_generation.py). Summed across all replenishment events,
    this is a directly measured, order-by-order attribution of excess
    to the MOQ floor specifically, not an estimate.

    Returns
    -------
    (pd.DataFrame, dict)
        The filtered replenishment-events dataframe with the new
        columns, and a small summary dict.
    """

    print_section("MOQ Root-Cause Attribution")

    replenishment_events = fact_inventory_excess[
        fact_inventory_excess["planned_order_quantity"] > 0
    ].copy()

    replenishment_events["moq_overshoot_units"] = (
        replenishment_events["planned_order_quantity"]
        - replenishment_events["target_stock_level"]
    ).clip(lower=0)

    replenishment_events["moq_overshoot_value"] = (
        replenishment_events["moq_overshoot_units"] * replenishment_events["unit_cost"]
    )

    total_orders = len(replenishment_events)
    moq_inflated_orders = (replenishment_events["moq_overshoot_units"] > 0).sum()
    total_overshoot_value = replenishment_events["moq_overshoot_value"].sum()

    summary = {
        "total_replenishment_orders": int(total_orders),
        "moq_inflated_orders": int(moq_inflated_orders),
        "moq_inflated_order_share_pct": moq_inflated_orders / total_orders * 100,
        "total_moq_overshoot_value": total_overshoot_value,
    }

    print(f"Total replenishment orders: {total_orders:,}")
    print(
        f"Orders inflated above target by MOQ: {moq_inflated_orders:,} "
        f"({summary['moq_inflated_order_share_pct']:.1f}%)"
    )
    print(
        f"Total order-time overshoot value (one-time, at order): {total_overshoot_value:,.2f}"
    )

    return replenishment_events, summary


# ============================================================
# 4. CAPITAL RECAPTURE WHAT-IF (retrospective counterfactual)
# ============================================================


def estimate_moq_cap_recapture(replenishment_events, cap_multipliers=(1.5, 2, 3, 5)):
    """
    RETROSPECTIVE COUNTERFACTUAL, not a forecast.

    For each cap_multiplier, estimate how much of the historical
    MOQ overshoot (see compute_moq_attribution()) would NOT have
    accumulated if every order had instead been capped at
    (cap_multiplier x target_stock_level) rather than allowed to
    follow minimum_order_qty unconditionally:

        capped_order = min(planned_order_quantity, cap_multiplier * target_stock_level)
        recaptured_units = planned_order_quantity - max(capped_order, target_stock_level)
        recaptured_value = recaptured_units * unit_cost

    This does NOT re-simulate subsequent days: a smaller historical
    order would change every following day's closing_stock, which
    would change future reorder timing and quantities. This estimates
    only the one-time order-quantity reduction at each historical
    order event, holding everything else constant -- a defensible
    order-of-magnitude estimate, not a validated forecast.
    """

    print_section("Capital Recapture What-If (retrospective, order-time only)")

    results = []

    for multiplier in cap_multipliers:
        capped_order = np.minimum(
            replenishment_events["planned_order_quantity"],
            multiplier * replenishment_events["target_stock_level"],
        )

        # Never cap below the policy target itself.
        capped_order = np.maximum(
            capped_order, replenishment_events["target_stock_level"]
        )

        recaptured_units = (
            replenishment_events["planned_order_quantity"] - capped_order
        ).clip(lower=0)

        recaptured_value = recaptured_units * replenishment_events["unit_cost"]

        results.append(
            {
                "cap_multiplier": multiplier,
                "recaptured_units": recaptured_units.sum(),
                "recaptured_value": recaptured_value.sum(),
            }
        )

        print(
            f"  Cap at {multiplier:>4.1f}x target: "
            f"{recaptured_units.sum():,.0f} units / "
            f"{recaptured_value.sum():,.2f} value recaptured (order-time, retrospective)"
        )

    return pd.DataFrame(results)
