"""
GulfMart Retail Inventory Analytics
------------------------------------

ABC analysis module.

Purpose
-------
Classifies products by annual COGS ("annual dollar usage" -- the
standard inventory-management ABC metric, as opposed to a revenue/
merchandising-based ABC) into A/B/C classes using classic cumulative
Pareto thresholds, then cross-tabulates that classification against
the excess-value tiers already computed in
05_overstock_analysis.ipynb (src/overstock_analysis.py) to build a
priority matrix answering the project's stated ABC goal directly:
not "which products sell the most" but "which products deserve the
most inventory-management attention."

The same cumulative-threshold classification function is used for
both dimensions (COGS -> A/B/C, excess value -> High/Medium/Low) --
one general technique applied twice, not two separate pieces of logic.
"""

import numpy as np
import pandas as pd

from data_validation import print_section


DEFAULT_ABC_THRESHOLDS = (0.80, 0.95)


# ============================================================
# 1. ANNUAL COGS BY PRODUCT
# ============================================================


def compute_annual_cogs_by_product(fact_sales, period_days=None):
    """
    Annualized COGS per product_id, the standard "annual dollar
    usage" metric for inventory ABC classification.

    Annualization (period COGS x 365 / period_days) matches the
    same convention used in inventory_kpis.py's turnover calculation,
    for consistency across notebooks. If period_days is None, it is
    inferred from fact_sales["transaction_date"].
    """

    print_section("Computing Annual COGS by Product")

    if period_days is None:
        period_days = pd.to_datetime(fact_sales["transaction_date"]).dt.date.nunique()

    product_cogs = fact_sales.groupby("product_id", as_index=False).agg(
        total_cogs=("cogs", "sum")
    )

    product_cogs["annual_cogs"] = product_cogs["total_cogs"] / period_days * 365

    print(f"Products with sales: {len(product_cogs):,}")
    print(f"Total annual COGS (all products): {product_cogs['annual_cogs'].sum():,.2f}")

    return product_cogs


# ============================================================
# 2. GENERIC CUMULATIVE-THRESHOLD CLASSIFIER
# ============================================================


def classify_by_value(
    df,
    value_column,
    id_column,
    thresholds=DEFAULT_ABC_THRESHOLDS,
    labels=("A", "B", "C"),
):
    """
    Sort df by value_column descending, compute each row's cumulative
    share of the total, and assign a class based on thresholds.

    labels[0] is assigned to rows up to thresholds[0] cumulative
    share (the highest-value rows); labels[-1] to the remainder.
    Used for both COGS-based ABC (labels=("A","B","C")) and
    excess-value tiering (labels=("High","Medium","Low")) -- same
    method, different inputs.

    Products with zero or negative value_column are always placed
    in the lowest tier (labels[-1]), regardless of thresholds, since
    a cumulative-share calculation is not meaningful for them.

    Returns a NEW DataFrame, sorted descending by value_column, with
    added columns: <value_column>_share_pct, cumulative_share_pct,
    and a class column named after value_column (e.g. "abc_class").
    """

    if len(thresholds) != len(labels) - 1:
        raise ValueError("thresholds must have exactly one fewer element than labels.")

    result = df[[id_column, value_column]].copy()

    result = result.sort_values(value_column, ascending=False).reset_index(drop=True)

    total = result[value_column].clip(lower=0).sum()

    result["value_share_pct"] = (
        result[value_column].clip(lower=0) / total * 100 if total > 0 else 0
    )

    result["cumulative_share_pct"] = result["value_share_pct"].cumsum()

    class_column = f"{value_column}_class"

    conditions = [
        result["cumulative_share_pct"] <= (threshold * 100) for threshold in thresholds
    ]

    result[class_column] = np.select(conditions, labels[:-1], default=labels[-1])

    # Zero/negative-value rows always go to the lowest tier.
    result.loc[result[value_column] <= 0, class_column] = labels[-1]

    return result


# ============================================================
# 3. PRIORITY MATRIX
# ============================================================


PRIORITY_LABELS = {
    ("A", "High"): "Urgent — high inventory investment, high excess",
    ("A", "Medium"): "Watch — high investment, moderate excess",
    ("A", "Low"): "Healthy A — investment justified by low excess",
    ("B", "High"): "Priority cleanup — moderate investment, high excess",
    ("B", "Medium"): "Watch B",
    ("B", "Low"): "Healthy B",
    (
        "C",
        "High",
    ): "Classic dead weight — low investment, high excess (cheap, easy win)",
    ("C", "Medium"): "Low priority",
    ("C", "Low"): "Fine as-is",
}


def build_priority_matrix(classified_df, abc_class_column, excess_tier_column):
    """
    Cross-tabulate ABC class against excess tier: product counts per
    cell, plus a plain-language priority label per combination.

    Returns
    -------
    (pd.DataFrame, pd.DataFrame)
        (count matrix, long-format table with priority labels attached)
    """

    print_section("Building ABC x Excess-Tier Priority Matrix")

    count_matrix = pd.crosstab(
        classified_df[abc_class_column],
        classified_df[excess_tier_column],
    ).reindex(index=["A", "B", "C"], columns=["High", "Medium", "Low"], fill_value=0)

    print(count_matrix)

    labeled = classified_df.copy()

    labeled["priority"] = labeled.apply(
        lambda row: PRIORITY_LABELS.get(
            (row[abc_class_column], row[excess_tier_column]), "Unclassified"
        ),
        axis=1,
    )

    return count_matrix, labeled
