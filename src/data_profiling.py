"""
GulfMart Retail Inventory Analytics
------------------------------------

Data profiling module for the generated retail dataset.

Purpose
-------
This module answers: "what does the data actually look like,
and what's messy about it?" — before any cleaning happens.

It is intentionally separate from data_validation.py:

    data_validation.py -> asserts correctness (PASS/FAIL/REVIEW)
    data_profiling.py  -> describes shape, quality, and messiness

This module should NOT generate, modify, or validate business
correctness of the dataset. It only inspects and reports.
"""

import pandas as pd


# ============================================================
# GENERAL HELPERS
# ============================================================


def print_section(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


# ============================================================
# 1. MISSINGNESS PROFILE
# ============================================================


def profile_missingness(df, table_name):
    """
    Report missing-value counts and percentages per column.

    Only columns with at least one missing value are shown,
    so tables with no issues print a clean "no missing values"
    message instead of a wall of zeros.
    """

    print_section(f"{table_name} — Missingness Profile")

    missing_counts = df.isna().sum()
    missing_counts = missing_counts[missing_counts > 0]

    if missing_counts.empty:
        print("No missing values detected.")
        return pd.DataFrame(columns=["column", "missing_count", "missing_pct"])

    report = (
        pd.DataFrame(
            {
                "column": missing_counts.index,
                "missing_count": missing_counts.values,
                "missing_pct": (missing_counts.values / len(df) * 100).round(2),
            }
        )
        .sort_values("missing_count", ascending=False)
        .reset_index(drop=True)
    )

    print(report.to_string(index=False))

    return report


# ============================================================
# 2. DUPLICATE PROFILE
# ============================================================


def profile_duplicates(df, table_name, key_columns=None):
    """
    Report duplicate rows.

    Checks full-row duplicates always. If key_columns is
    provided, also checks duplicates on that subset (e.g. a
    business key like transaction_id) separately, since a
    duplicate business key with differing other columns
    would otherwise be missed by a full-row check.
    """

    print_section(f"{table_name} — Duplicate Profile")

    full_row_duplicates = df.duplicated().sum()

    print(f"Full-row duplicates: {full_row_duplicates:,}")

    key_duplicates = None

    if key_columns is not None:
        key_duplicates = df.duplicated(subset=key_columns).sum()

        print(f"Duplicate on key {key_columns}: {key_duplicates:,}")

    return {
        "full_row_duplicates": int(full_row_duplicates),
        "key_duplicates": int(key_duplicates) if key_duplicates is not None else None,
    }


# ============================================================
# 3. TEXT CONSISTENCY PROFILE
# ============================================================


def profile_text_consistency(df, table_name, min_variants=2):
    """
    Scan every object/string column for inconsistent text
    formatting.

    A value is flagged as inconsistent when its normalized
    form (stripped of leading/trailing whitespace, lower-cased)
    matches another value's normalized form, but the raw text
    differs — e.g. "Riyadh" and "RIYADH  " normalize to the
    same "riyadh" but are stored as two different strings.

    This is deliberately generic and does not assume any
    "correct" casing style (title case, upper case, etc.),
    so it works safely across ID columns, names, and free text
    alike without false-flagging things like "PROD0001".
    """

    print_section(f"{table_name} — Text Consistency Profile")

    text_columns = df.select_dtypes(include="object").columns

    any_issues = False

    results = {}

    for column in text_columns:
        series = df[column].dropna().astype(str)

        if series.empty:
            continue

        normalized = series.str.strip().str.lower()

        # Group raw values by their normalized form.
        variant_counts = (
            pd.DataFrame({"raw": series, "normalized": normalized})
            .drop_duplicates()
            .groupby("normalized")["raw"]
            .nunique()
        )

        inconsistent_groups = variant_counts[variant_counts >= min_variants]

        # Also flag values that need stripping even if they're
        # the only variant (e.g. "Riyadh " with no counterpart).
        needs_strip = (series != series.str.strip()).sum()

        if len(inconsistent_groups) > 0 or needs_strip > 0:
            any_issues = True

            affected_rows = normalized.isin(inconsistent_groups.index).sum()

            print(
                f"Column '{column}': "
                f"{len(inconsistent_groups)} normalized value(s) with multiple "
                f"raw variants, affecting {affected_rows:,} rows. "
                f"Rows needing whitespace-strip: {needs_strip:,}."
            )

            results[column] = {
                "inconsistent_groups": len(inconsistent_groups),
                "affected_rows": int(affected_rows),
                "needs_strip": int(needs_strip),
            }

    if not any_issues:
        print("No text-consistency issues detected.")

    return results


# ============================================================
# 4. FULL PROFILING PIPELINE
# ============================================================


def profile_table(df, table_name, key_columns=None):
    """
    Run the full profiling suite on a single table.
    """

    print()
    print("#" * 60)
    print(f"# PROFILING: {table_name}")
    print("#" * 60)

    print(f"\nShape: {df.shape[0]:,} rows x {df.shape[1]} columns")

    memory_mb = df.memory_usage(deep=True).sum() / 1024**2
    print(f"Memory usage: {memory_mb:.2f} MB")

    missingness = profile_missingness(df, table_name)
    duplicates = profile_duplicates(df, table_name, key_columns)
    text_consistency = profile_text_consistency(df, table_name)

    return {
        "table_name": table_name,
        "shape": df.shape,
        "memory_mb": memory_mb,
        "missingness": missingness,
        "duplicates": duplicates,
        "text_consistency": text_consistency,
    }


def profile_all_tables(tables):
    """
    Profile every table in a {table_name: dataframe} dict,
    with sensible default key columns per known table name.

    Parameters
    ----------
    tables : dict[str, pd.DataFrame]
        e.g. {"dim_product": dim_product, "fact_sales": fact_sales, ...}
    """

    default_keys = {
        "dim_product": "product_id",
        "dim_store": "store_id",
        "dim_customer": "customer_id",
        "dim_supplier": "supplier_id",
        "fact_sales": "transaction_id",
        "fact_inventory": ["date", "store_id", "product_id"],
    }

    results = {}

    for table_name, df in tables.items():
        key_columns = default_keys.get(table_name)

        results[table_name] = profile_table(df, table_name, key_columns)

    print_section("PROFILING COMPLETE")

    for table_name, result in results.items():
        print(
            f"{table_name:15s} {result['shape'][0]:>10,} rows  "
            f"{result['memory_mb']:>8.2f} MB"
        )

    return results
