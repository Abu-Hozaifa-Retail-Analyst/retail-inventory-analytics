"""
GulfMart Retail Inventory Analytics
------------------------------------

Inventory KPI module.

Purpose
-------
Aggregates fact_inventory and fact_sales into business-readable KPIs
at three grains: overall, per-product, and per-store, for the full
project time horizon (no monthly/quarterly trend in this module).

Important
---------
Several fact_inventory columns are STATIC per product-store
combination (initial_opening_stock, lead_time_days,
safety_stock_days, replenishment_interval_days, minimum_order_qty)
-- they repeat identically across every day for that combination.
Summing them directly across a grain would silently multiply them by
the number of days in the group. This module always de-duplicates to
one row per (store_id, product_id) before aggregating static columns,
and only sums/averages daily-varying columns (closing_stock,
sales_units, receipts, stockout_event, inventory_coverage_days, ...)
directly.

Data source expectations
-------------------------
fact_sales, dim_product, dim_store, dim_customer, dim_supplier should
be the CLEANED versions (data/cleaned/). fact_inventory should be the
RAW version (data/raw/) -- it was never modified by cleaning, and its
sales_units was built from fact_sales BEFORE the duplicate-transaction
injection, so it is already consistent with the cleaned fact_sales
rather than the raw (duplicated) one.
"""

import numpy as np
import pandas as pd

from data_validation import print_section


EXCESS_COVERAGE_THRESHOLD_DAYS = 365


def format_kpi_value(value):
    """
    Format a KPI value for display, choosing precision based on
    magnitude so small ratios (e.g. turnover near 0) don't silently
    round to a misleading "0.00" the way a fixed 2-decimal format
    would.
    """

    if isinstance(value, (int, np.integer)):
        return f"{value:,}"

    if abs(value) >= 1:
        return f"{value:,.2f}"

    return f"{value:.6f}"


def format_table_for_display(
    df, small_ratio_columns=("inventory_turnover_annualized", "gmroi")
):
    """
    Return a display-only COPY of a KPI table with column-appropriate
    formatting: small-magnitude ratio columns (turnover, GMROI) get
    5 decimal places so they don't silently round to "0.00" the way
    a single global 2-decimal format does; other float columns keep
    thousands separators at 2 decimals. Does not modify df or affect
    any further calculation -- formatting only.
    """

    display_df = df.copy()

    for column in display_df.columns:
        if not pd.api.types.is_float_dtype(display_df[column]):
            continue

        if column in small_ratio_columns:
            display_df[column] = display_df[column].map(
                lambda v: f"{v:.5f}" if pd.notna(v) else "NaN"
            )
        else:
            display_df[column] = display_df[column].map(
                lambda v: f"{v:,.2f}" if pd.notna(v) else "NaN"
            )

    return display_df


# ============================================================
# 1. STATIC ATTRIBUTE EXTRACTION
# ============================================================


def get_combo_static_attributes(fact_inventory):
    """
    Return one row per (store_id, product_id) combination, containing
    only the attributes that are constant across every day for that
    combination (e.g. initial_opening_stock, lead_time_days).

    Use this before summing/averaging any static column across a
    grain -- summing the raw fact_inventory table directly would
    multiply these values by the number of days in the group.
    """

    static_columns = [
        "store_id",
        "product_id",
        "initial_opening_stock",
        "lead_time_days",
        "minimum_order_qty",
        "safety_stock_days",
        "replenishment_interval_days",
    ]

    static_columns = [c for c in static_columns if c in fact_inventory.columns]

    return fact_inventory.drop_duplicates(subset=["store_id", "product_id"])[
        static_columns
    ].reset_index(drop=True)


# ============================================================
# 2. INVENTORY VALUE
# ============================================================


def compute_inventory_value(fact_inventory, dim_product):
    """
    Merge unit_cost and demand_class from dim_product onto
    fact_inventory, and compute row-level inventory_value =
    closing_stock * unit_cost.

    Returns a NEW DataFrame; does not modify the input.
    """

    print_section("Computing Inventory Value")

    # fact_inventory already carries its own demand_class column
    # (needed upstream in generate_fact_inventory() for
    # INITIAL_INVENTORY_DAYS / SAFETY_STOCK_DAYS lookups). Merging
    # dim_product's demand_class on top would collide and pandas
    # would silently rename both to demand_class_x/demand_class_y
    # rather than error -- so it is deliberately excluded here and
    # the existing column is reused instead.
    merge_columns = ["product_id", "unit_cost", "category"]

    fact_inventory_value = fact_inventory.merge(
        dim_product[merge_columns],
        on="product_id",
        how="left",
        validate="many_to_one",
    )

    missing_cost = fact_inventory_value["unit_cost"].isna().sum()

    if missing_cost > 0:
        print(f"WARNING: {missing_cost:,} rows have no matching unit_cost.")

    fact_inventory_value["inventory_value"] = (
        fact_inventory_value["closing_stock"] * fact_inventory_value["unit_cost"]
    )

    total_value = fact_inventory_value["inventory_value"].sum()

    print(f"Rows: {len(fact_inventory_value):,}")
    print(f"Total inventory_value across all rows (all days): {total_value:,.2f}")
    print("(This is a period-cumulative figure, not a point-in-time balance --")
    print(" use compute_overall_kpis()/compute_product_kpis()/compute_store_kpis()")
    print(" for correctly time-averaged inventory value.)")

    return fact_inventory_value


# ============================================================
# 3. OVERALL KPIs
# ============================================================


def compute_overall_kpis(fact_inventory_value, fact_sales):
    """
    Compute business-wide KPIs for the full time horizon.

    Returns
    -------
    dict
    """

    print_section("Overall Inventory KPIs")

    period_days = fact_inventory_value["date"].nunique()

    combo_static = get_combo_static_attributes(fact_inventory_value)

    # --------------------------------------------------------
    # Average inventory (units and value), time-averaged
    # --------------------------------------------------------

    daily_units = fact_inventory_value.groupby("date")["closing_stock"].sum()
    avg_inventory_units = daily_units.mean()

    daily_value = fact_inventory_value.groupby("date")["inventory_value"].sum()
    avg_inventory_value = daily_value.mean()

    # --------------------------------------------------------
    # Turnover & Days of Inventory (annualized)
    # --------------------------------------------------------

    total_cogs_period = fact_sales["cogs"].sum()
    annualized_cogs = (total_cogs_period / period_days) * 365

    turnover_annualized = (
        annualized_cogs / avg_inventory_value if avg_inventory_value > 0 else np.nan
    )

    days_of_inventory = (
        365 / turnover_annualized
        if turnover_annualized and turnover_annualized > 0
        else np.nan
    )

    # --------------------------------------------------------
    # Sell-through %
    # --------------------------------------------------------

    total_units_sold = fact_inventory_value["sales_units"].sum()
    beginning_inventory_units = combo_static["initial_opening_stock"].sum()
    total_receipts = fact_inventory_value["receipts"].sum()

    sell_through_pct = (
        total_units_sold / (beginning_inventory_units + total_receipts) * 100
        if (beginning_inventory_units + total_receipts) > 0
        else np.nan
    )

    # --------------------------------------------------------
    # Stockout / in-stock rate
    # --------------------------------------------------------

    stockout_rate_pct = fact_inventory_value["stockout_event"].mean() * 100
    in_stock_rate_pct = 100 - stockout_rate_pct

    # --------------------------------------------------------
    # Coverage
    # --------------------------------------------------------

    coverage = (
        fact_inventory_value["inventory_coverage_days"]
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    avg_coverage_days = coverage.mean()

    excess_share_pct = (
        (coverage > EXCESS_COVERAGE_THRESHOLD_DAYS).sum() / len(coverage) * 100
        if len(coverage) > 0
        else np.nan
    )

    # --------------------------------------------------------
    # Profitability
    # --------------------------------------------------------

    gross_profit_total = fact_sales["gross_profit"].sum()
    net_sales_total = fact_sales["net_sales"].sum()

    gross_margin_pct = (
        gross_profit_total / net_sales_total * 100 if net_sales_total > 0 else np.nan
    )

    gmroi = (
        gross_profit_total / avg_inventory_value if avg_inventory_value > 0 else np.nan
    )

    # --------------------------------------------------------
    # Risk shares (by inventory value)
    # --------------------------------------------------------

    total_value_sum = fact_inventory_value["inventory_value"].sum()

    slow_moving_value_share_pct = (
        fact_inventory_value.loc[
            fact_inventory_value["demand_class"] == "Slow-moving", "inventory_value"
        ].sum()
        / total_value_sum
        * 100
        if total_value_sum > 0
        else np.nan
    )

    combo_sales = fact_inventory_value.groupby(["store_id", "product_id"])[
        "sales_units"
    ].sum()

    dead_stock_combo_count = (combo_sales == 0).sum()
    dead_stock_combo_share_pct = (
        dead_stock_combo_count / len(combo_sales) * 100
        if len(combo_sales) > 0
        else np.nan
    )

    kpis = {
        "period_days": int(period_days),
        "avg_inventory_units": avg_inventory_units,
        "avg_inventory_value": avg_inventory_value,
        "annualized_cogs": annualized_cogs,
        "inventory_turnover_annualized": turnover_annualized,
        "days_of_inventory": days_of_inventory,
        "sell_through_pct": sell_through_pct,
        "stockout_rate_pct": stockout_rate_pct,
        "in_stock_rate_pct": in_stock_rate_pct,
        "avg_coverage_days": avg_coverage_days,
        "excess_inventory_share_pct": excess_share_pct,
        "gross_margin_pct": gross_margin_pct,
        "gmroi": gmroi,
        "slow_moving_value_share_pct": slow_moving_value_share_pct,
        "dead_stock_combo_count": int(dead_stock_combo_count),
        "dead_stock_combo_share_pct": dead_stock_combo_share_pct,
    }

    for key, value in kpis.items():
        print(f"{key:35s} {format_kpi_value(value)}")

    return kpis


# ============================================================
# 4. PRODUCT-LEVEL KPIs
# ============================================================


def compute_product_kpis(fact_inventory_value, fact_sales, dim_product):
    """
    Compute the same KPI family per product_id, aggregated across
    all stores and the full time horizon.

    Returns
    -------
    pd.DataFrame, one row per product_id
    """

    print_section("Product-Level Inventory KPIs")

    period_days = fact_inventory_value["date"].nunique()

    combo_static = get_combo_static_attributes(fact_inventory_value)

    # Average inventory (units/value), time-averaged per product
    daily_units = (
        fact_inventory_value.groupby(["product_id", "date"])["closing_stock"]
        .sum()
        .reset_index()
    )
    avg_units = daily_units.groupby("product_id")["closing_stock"].mean()

    daily_value = (
        fact_inventory_value.groupby(["product_id", "date"])["inventory_value"]
        .sum()
        .reset_index()
    )
    avg_value = daily_value.groupby("product_id")["inventory_value"].mean()

    # Sales-side aggregates
    sales_agg = fact_sales.groupby("product_id").agg(
        total_cogs=("cogs", "sum"),
        gross_profit=("gross_profit", "sum"),
        net_sales=("net_sales", "sum"),
        total_units_sold=("quantity", "sum"),
    )

    # Inventory-side aggregates
    beginning_inventory = combo_static.groupby("product_id")[
        "initial_opening_stock"
    ].sum()
    total_receipts = fact_inventory_value.groupby("product_id")["receipts"].sum()
    stockout_rate = (
        fact_inventory_value.groupby("product_id")["stockout_event"].mean() * 100
    )

    coverage = (
        fact_inventory_value.assign(
            coverage_clean=fact_inventory_value["inventory_coverage_days"].replace(
                [np.inf, -np.inf], np.nan
            )
        )
        .groupby("product_id")["coverage_clean"]
        .mean()
    )

    dead_store_count = (
        fact_inventory_value.groupby(["product_id", "store_id"])["sales_units"]
        .sum()
        .reset_index()
        .assign(is_dead=lambda d: d["sales_units"] == 0)
        .groupby("product_id")["is_dead"]
        .sum()
    )

    product_kpis = pd.DataFrame(
        {
            "avg_inventory_units": avg_units,
            "avg_inventory_value": avg_value,
            "beginning_inventory_units": beginning_inventory,
            "total_receipts": total_receipts,
            "stockout_rate_pct": stockout_rate,
            "avg_coverage_days": coverage,
            "dead_store_count": dead_store_count,
        }
    ).join(sales_agg, how="left")

    product_kpis["annualized_cogs"] = product_kpis["total_cogs"] / period_days * 365

    product_kpis["inventory_turnover_annualized"] = np.where(
        product_kpis["avg_inventory_value"] > 0,
        product_kpis["annualized_cogs"] / product_kpis["avg_inventory_value"],
        np.nan,
    )

    product_kpis["days_of_inventory"] = np.where(
        product_kpis["inventory_turnover_annualized"] > 0,
        365 / product_kpis["inventory_turnover_annualized"],
        np.nan,
    )

    product_kpis["sell_through_pct"] = np.where(
        (product_kpis["beginning_inventory_units"] + product_kpis["total_receipts"])
        > 0,
        product_kpis["total_units_sold"]
        / (product_kpis["beginning_inventory_units"] + product_kpis["total_receipts"])
        * 100,
        np.nan,
    )

    product_kpis["gross_margin_pct"] = np.where(
        product_kpis["net_sales"] > 0,
        product_kpis["gross_profit"] / product_kpis["net_sales"] * 100,
        np.nan,
    )

    product_kpis["gmroi"] = np.where(
        product_kpis["avg_inventory_value"] > 0,
        product_kpis["gross_profit"] / product_kpis["avg_inventory_value"],
        np.nan,
    )

    product_kpis["is_excess_inventory"] = (
        product_kpis["avg_coverage_days"] > EXCESS_COVERAGE_THRESHOLD_DAYS
    )

    product_kpis = product_kpis.merge(
        dim_product[["product_id", "product_name", "category", "demand_class"]],
        on="product_id" if "product_id" in product_kpis.columns else None,
        left_index=True if "product_id" not in product_kpis.columns else False,
        right_on="product_id",
        how="left",
    )

    product_kpis = (
        product_kpis.reset_index(drop=True)
        if "product_id" in product_kpis.columns
        else product_kpis
    )

    print(f"Computed KPIs for {len(product_kpis):,} products.")

    return product_kpis


# ============================================================
# 5. STORE-LEVEL KPIs
# ============================================================


def compute_store_kpis(fact_inventory_value, fact_sales, dim_store):
    """
    Compute the same KPI family per store_id, aggregated across all
    products and the full time horizon.

    Returns
    -------
    pd.DataFrame, one row per store_id
    """

    print_section("Store-Level Inventory KPIs")

    period_days = fact_inventory_value["date"].nunique()

    combo_static = get_combo_static_attributes(fact_inventory_value)

    daily_units = (
        fact_inventory_value.groupby(["store_id", "date"])["closing_stock"]
        .sum()
        .reset_index()
    )
    avg_units = daily_units.groupby("store_id")["closing_stock"].mean()

    daily_value = (
        fact_inventory_value.groupby(["store_id", "date"])["inventory_value"]
        .sum()
        .reset_index()
    )
    avg_value = daily_value.groupby("store_id")["inventory_value"].mean()

    sales_agg = fact_sales.groupby("store_id").agg(
        total_cogs=("cogs", "sum"),
        gross_profit=("gross_profit", "sum"),
        net_sales=("net_sales", "sum"),
        total_units_sold=("quantity", "sum"),
    )

    beginning_inventory = combo_static.groupby("store_id")[
        "initial_opening_stock"
    ].sum()
    total_receipts = fact_inventory_value.groupby("store_id")["receipts"].sum()
    stockout_rate = (
        fact_inventory_value.groupby("store_id")["stockout_event"].mean() * 100
    )

    coverage = (
        fact_inventory_value.assign(
            coverage_clean=fact_inventory_value["inventory_coverage_days"].replace(
                [np.inf, -np.inf], np.nan
            )
        )
        .groupby("store_id")["coverage_clean"]
        .mean()
    )

    dead_product_count = (
        fact_inventory_value.groupby(["store_id", "product_id"])["sales_units"]
        .sum()
        .reset_index()
        .assign(is_dead=lambda d: d["sales_units"] == 0)
        .groupby("store_id")["is_dead"]
        .sum()
    )

    store_kpis = pd.DataFrame(
        {
            "avg_inventory_units": avg_units,
            "avg_inventory_value": avg_value,
            "beginning_inventory_units": beginning_inventory,
            "total_receipts": total_receipts,
            "stockout_rate_pct": stockout_rate,
            "avg_coverage_days": coverage,
            "dead_product_count": dead_product_count,
        }
    ).join(sales_agg, how="left")

    store_kpis["annualized_cogs"] = store_kpis["total_cogs"] / period_days * 365

    store_kpis["inventory_turnover_annualized"] = np.where(
        store_kpis["avg_inventory_value"] > 0,
        store_kpis["annualized_cogs"] / store_kpis["avg_inventory_value"],
        np.nan,
    )

    store_kpis["days_of_inventory"] = np.where(
        store_kpis["inventory_turnover_annualized"] > 0,
        365 / store_kpis["inventory_turnover_annualized"],
        np.nan,
    )

    store_kpis["sell_through_pct"] = np.where(
        (store_kpis["beginning_inventory_units"] + store_kpis["total_receipts"]) > 0,
        store_kpis["total_units_sold"]
        / (store_kpis["beginning_inventory_units"] + store_kpis["total_receipts"])
        * 100,
        np.nan,
    )

    store_kpis["gross_margin_pct"] = np.where(
        store_kpis["net_sales"] > 0,
        store_kpis["gross_profit"] / store_kpis["net_sales"] * 100,
        np.nan,
    )

    store_kpis["gmroi"] = np.where(
        store_kpis["avg_inventory_value"] > 0,
        store_kpis["gross_profit"] / store_kpis["avg_inventory_value"],
        np.nan,
    )

    store_kpis["is_excess_inventory"] = (
        store_kpis["avg_coverage_days"] > EXCESS_COVERAGE_THRESHOLD_DAYS
    )

    store_kpis = store_kpis.merge(
        dim_store[["store_id", "store_name", "store_type", "region"]],
        left_index=True,
        right_on="store_id",
        how="left",
    ).reset_index(drop=True)

    print(f"Computed KPIs for {len(store_kpis):,} stores.")

    return store_kpis
