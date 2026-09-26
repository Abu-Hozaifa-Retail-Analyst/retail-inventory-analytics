"""
GulfMart Retail Inventory Analytics
------------------------------------

Replenishment analysis module -- the capstone notebook of the
project's analytical arc.

Purpose
-------
1. Measure the deepest root cause found in this project: the
   replenishment order logic in generate_fact_inventory() orders
   target_stock_level again every review cycle WITHOUT netting
   against existing inventory position (opening_stock). This is
   distinct from, and more complete than, the MOQ-flooring measurement
   in 05_overstock_analysis.ipynb -- see compute_netting_overshoot().

2. Build a per-product-store Replenishment Action List (SUPPRESS /
   REDUCE / MAINTAIN / EXPEDITE), synthesizing:
     - real stockout risk (04_stockout_analysis.ipynb: low_stock_pct)
     - ABC importance (06_abc_analysis.ipynb: annual_cogs_class)
     - excess intensity (05_overstock_analysis.ipynb methodology,
       applied at product-store grain here)
   into the single actionable deliverable this project has been
   building toward.

3. Estimate the retrospective value recoverable by following the
   action list's SUPPRESS/REDUCE recommendations.
"""

import numpy as np
import pandas as pd

from data_validation import print_section
from abc_analysis import classify_by_value
from overstock_analysis import compute_excess_value, summarize_excess_by


# ============================================================
# 1. NETTING OVERSHOOT (deepest root-cause measurement)
# ============================================================


def compute_netting_overshoot(fact_inventory, dim_product):
    """
    For every actual replenishment order, compute what an inventory
    policy that nets against existing position (opening_stock) WOULD
    have ordered, and compare it to what was actually ordered.

        ideal_order = 0                              if opening_stock >= target_stock_level
                    = max(target_stock_level - opening_stock,
                          minimum_order_qty)          otherwise

        netting_overshoot_units = max(planned_order_quantity - ideal_order, 0)
        netting_overshoot_value = netting_overshoot_units * unit_cost

    This is a MORE COMPLETE measurement than 05_overstock_analysis.py's
    MOQ attribution: that measurement compared the order to
    target_stock_level alone, ignoring whether stock already on hand
    made the order unnecessary. netting_overshoot_value is always
    >= the MOQ-only overshoot value by construction, since it also
    captures orders placed when opening_stock already met or exceeded
    target (ideal_order = 0), which the MOQ-only view could not see.

    Limitation, stated plainly: opening_stock is used as the
    inventory-position proxy. The model does not separately track
    outstanding (in-transit) orders as a pipeline field, so this does
    not account for stock already on order but not yet received --
    the same category of simplification as the stress tests in
    04_stockout_analysis.ipynb.
    """

    print_section("Computing Netting Overshoot (deepest root-cause measurement)")

    fi = fact_inventory.merge(
        dim_product[["product_id", "unit_cost"]], on="product_id", how="left"
    )

    replenishment_events = fi[fi["planned_order_quantity"] > 0].copy()

    ideal_order = np.where(
        replenishment_events["opening_stock"]
        >= replenishment_events["target_stock_level"],
        0,
        np.maximum(
            replenishment_events["target_stock_level"]
            - replenishment_events["opening_stock"],
            replenishment_events["minimum_order_qty"],
        ),
    )

    replenishment_events["ideal_order"] = ideal_order

    replenishment_events["netting_overshoot_units"] = (
        replenishment_events["planned_order_quantity"]
        - replenishment_events["ideal_order"]
    ).clip(lower=0)

    replenishment_events["netting_overshoot_value"] = (
        replenishment_events["netting_overshoot_units"]
        * replenishment_events["unit_cost"]
    )

    total_orders = len(replenishment_events)
    unnecessary_orders = (replenishment_events["ideal_order"] == 0).sum()
    total_overshoot_value = replenishment_events["netting_overshoot_value"].sum()

    summary = {
        "total_replenishment_orders": int(total_orders),
        "orders_that_should_not_have_been_placed": int(unnecessary_orders),
        "orders_that_should_not_have_been_placed_pct": unnecessary_orders
        / total_orders
        * 100,
        "total_netting_overshoot_value": total_overshoot_value,
    }

    print(f"Total replenishment orders: {total_orders:,}")
    print(
        f"Orders where existing stock already met/exceeded target "
        f"(should not have been placed at all): {unnecessary_orders:,} "
        f"({summary['orders_that_should_not_have_been_placed_pct']:.1f}%)"
    )
    print(
        f"Total netting overshoot value (comprehensive): {total_overshoot_value:,.2f}"
    )

    return replenishment_events, summary


# ============================================================
# 2. COMBO-LEVEL EXCESS TIER (product-store grain)
# ============================================================


def compute_combo_excess_tier(fact_inventory, dim_product, thresholds=(0.80, 0.95)):
    """
    Excess-value tiering at PRODUCT-STORE grain (05/06 computed this
    at product grain, or store grain, separately). Reuses the same
    compute_excess_value() + summarize_excess_by() + classify_by_value()
    building blocks, applied to the combo grain this notebook needs
    for its action list.
    """

    print_section("Computing Combo-Level Excess Tier")

    fact_inventory_excess = compute_excess_value(fact_inventory, dim_product)

    combo_excess = summarize_excess_by(
        fact_inventory_excess, ["store_id", "product_id"]
    ).reset_index()

    combo_excess["combo_id"] = (
        combo_excess["store_id"].astype(str)
        + "_"
        + combo_excess["product_id"].astype(str)
    )

    tiered = classify_by_value(
        combo_excess,
        value_column="avg_excess_value",
        id_column="combo_id",
        thresholds=thresholds,
        labels=("High", "Medium", "Low"),
    )

    combo_excess = combo_excess.merge(
        tiered[["combo_id", "avg_excess_value_class"]], on="combo_id", how="left"
    )

    return combo_excess, fact_inventory_excess


# ============================================================
# 3. REPLENISHMENT ACTION LIST
# ============================================================


def build_replenishment_action_list(combo_summary, combo_excess, abc_classified):
    """
    Synthesize stockout-risk (combo_summary, from stockout_analysis.py),
    excess intensity (combo_excess, from compute_combo_excess_tier()),
    and product-level ABC class (abc_classified, from abc_analysis.py)
    into one action per product-store combination.

    Rules (evaluated in order, first match wins):
        low_stock_pct > 0 AND ABC class A  -> EXPEDITE
        low_stock_pct > 0 (any class)      -> MAINTAIN (real risk exists; never suppress)
        excess tier == High                -> SUPPRESS
        excess tier == Medium               -> REDUCE
        otherwise                           -> MAINTAIN
    """

    print_section("Building Replenishment Action List")

    action_list = combo_summary.merge(
        combo_excess[
            ["store_id", "product_id", "avg_excess_value", "avg_excess_value_class"]
        ],
        on=["store_id", "product_id"],
        how="left",
    )

    action_list = action_list.merge(
        abc_classified[["product_id", "annual_cogs_class"]],
        on="product_id",
        how="left",
    )

    conditions = [
        (action_list["low_stock_pct"] > 0) & (action_list["annual_cogs_class"] == "A"),
        action_list["low_stock_pct"] > 0,
        action_list["avg_excess_value_class"] == "High",
        action_list["avg_excess_value_class"] == "Medium",
    ]

    choices = ["EXPEDITE", "MAINTAIN", "SUPPRESS", "REDUCE"]

    action_list["recommended_action"] = np.select(
        conditions, choices, default="MAINTAIN"
    )

    print("Action distribution:")
    print(action_list["recommended_action"].value_counts())

    return action_list


# ============================================================
# 4. RETROSPECTIVE RECAPTURE FROM THE ACTION LIST
# ============================================================


def estimate_action_list_recapture(replenishment_events, action_list):
    """
    RETROSPECTIVE, not a forecast (same category of caveat as
    05_overstock_analysis.ipynb's capital recapture estimate).

    Sums netting_overshoot_value (see compute_netting_overshoot())
    for every historical order belonging to a combination flagged
    SUPPRESS or REDUCE by build_replenishment_action_list() -- i.e.
    "how much of the measured overshoot sits specifically in the
    combinations this project's own action list says should have
    been throttled."
    """

    print_section("Estimating Action-List Recapture (retrospective)")

    events = replenishment_events.merge(
        action_list[["store_id", "product_id", "recommended_action"]],
        on=["store_id", "product_id"],
        how="left",
    )

    by_action = events.groupby("recommended_action")["netting_overshoot_value"].sum()

    for action in ["SUPPRESS", "REDUCE", "MAINTAIN", "EXPEDITE"]:
        value = by_action.get(action, 0)
        print(f"  {action:>9s}: {value:,.2f} in netting overshoot value")

    suppress_reduce_value = by_action.get("SUPPRESS", 0) + by_action.get("REDUCE", 0)

    print(
        f"\nTotal recoverable (SUPPRESS + REDUCE combos): {suppress_reduce_value:,.2f}"
    )

    return by_action, suppress_reduce_value
