"""
GulfMart Retail Inventory Analytics
------------------------------------

Data cleaning module for the generated retail dataset.

Purpose
-------
This module resolves the data-quality issues identified during
profiling (src/data_profiling.py, notebooks/01_data_profiling.ipynb)
and intentionally planted by inject_data_quality_issues() in
data_generation.py.

Architecture
------------
data_profiling.py  -> describes what's messy
data_validation.py -> asserts correctness (PASS/FAIL/REVIEW)
data_cleaning.py   -> fixes what profiling found

Important
---------
Every function here returns a NEW DataFrame (never mutates its
input in place) and prints a short before/after report, so cleaning
steps are transparent and auditable rather than silent.

fact_inventory is NOT cleaned here. It had zero missing values,
zero duplicates, and zero text-consistency issues in profiling
(data-quality injection intentionally excludes it, to avoid
contradicting its continuity/reconciliation validation). Downstream
notebooks should continue reading it directly from data/raw/.
"""

import numpy as np
import pandas as pd

from data_validation import print_section


# ============================================================
# 1. CUSTOMER CLEANING
# ============================================================


def clean_dim_customer(dim_customer):
    """
    Fill missing dim_customer.city with a clear placeholder.

    Returns
    -------
    (pd.DataFrame, dict)
        Cleaned dataframe and a small report of what changed.
    """

    print_section("Cleaning dim_customer")

    dim_customer = dim_customer.copy()

    missing_before = dim_customer["city"].isna().sum()

    dim_customer["city"] = dim_customer["city"].fillna("Unknown")

    print(f"Filled {missing_before:,} missing 'city' values with 'Unknown'.")

    return dim_customer, {"city_filled": int(missing_before)}


# ============================================================
# 2. SUPPLIER CLEANING
# ============================================================


def clean_dim_supplier(dim_supplier):
    """
    Fill missing dim_supplier.supplier_name with a traceable
    placeholder that embeds the supplier_id, e.g.
    "Unknown Supplier (SUP014)", so the record can still be
    identified later even without its name.

    Returns
    -------
    (pd.DataFrame, dict)
    """

    print_section("Cleaning dim_supplier")

    dim_supplier = dim_supplier.copy()

    missing_mask = dim_supplier["supplier_name"].isna()

    missing_before = missing_mask.sum()

    dim_supplier.loc[missing_mask, "supplier_name"] = (
        "Unknown Supplier (" + dim_supplier.loc[missing_mask, "supplier_id"] + ")"
    )

    print(
        f"Filled {missing_before:,} missing 'supplier_name' values "
        f"with a supplier_id-traceable placeholder."
    )

    return dim_supplier, {"supplier_name_filled": int(missing_before)}


# ============================================================
# 3. STORE CLEANING
# ============================================================


def clean_dim_store(dim_store):
    """
    Normalize dim_store.city text formatting: strip surrounding
    whitespace and apply title case, so values like "RIYADH  "
    and "Riyadh" collapse to a single consistent "Riyadh".

    Title case is a safe canonical choice here specifically
    because dim_store.city values are real city names drawn from
    a known, fixed list (REGION_CITIES in data_generation_config.py)
    -- this is NOT a generic assumption applied blindly to any text
    column, only to a field we know represents place names.

    Returns
    -------
    (pd.DataFrame, dict)
    """

    print_section("Cleaning dim_store")

    dim_store = dim_store.copy()

    original = dim_store["city"].copy()

    normalized = original.str.strip().str.title()

    changed_mask = original != normalized

    changed_count = changed_mask.sum()

    dim_store["city"] = normalized

    if changed_count > 0:
        print(f"Normalized {changed_count:,} 'city' value(s) to consistent formatting:")

        for before, after in zip(original[changed_mask], normalized[changed_mask]):
            print(f"  {before!r} -> {after!r}")

    else:
        print("No inconsistent 'city' formatting found -- nothing to normalize.")

    return dim_store, {"city_normalized": int(changed_count)}


# ============================================================
# 4. SALES CLEANING
# ============================================================


def clean_fact_sales(fact_sales):
    """
    Remove duplicate transactions from fact_sales.

    A full-row duplicate here represents the same transaction
    recorded twice (e.g. simulating a POS system double-send),
    so the first occurrence is kept and later occurrences are
    dropped.

    Returns
    -------
    (pd.DataFrame, dict)
    """

    print_section("Cleaning fact_sales")

    fact_sales = fact_sales.copy()

    rows_before = len(fact_sales)

    fact_sales = fact_sales.drop_duplicates(keep="first").reset_index(drop=True)

    rows_after = len(fact_sales)

    removed = rows_before - rows_after

    print(
        f"Removed {removed:,} duplicate transaction(s). {rows_before:,} -> {rows_after:,} rows."
    )

    return fact_sales, {"duplicates_removed": int(removed)}


# ============================================================
# 5. FULL CLEANING PIPELINE
# ============================================================


def clean_generated_dataset(
    dim_product,
    dim_store,
    dim_customer,
    dim_supplier,
    fact_sales,
):
    """
    Run the complete cleaning pipeline on every table known to
    have planted data-quality issues.

    dim_product and fact_inventory are intentionally excluded:
    dim_product was never targeted by inject_data_quality_issues(),
    and fact_inventory is never cleaned (see module docstring).

    Returns
    -------
    dict
        {
            "dim_product": dim_product,       # unchanged, passed through
            "dim_store": <cleaned>,
            "dim_customer": <cleaned>,
            "dim_supplier": <cleaned>,
            "fact_sales": <cleaned>,
            "report": {...},
        }
    """

    print()
    print("=" * 60)
    print("GulfMart Retail Inventory Dataset Cleaning")
    print("=" * 60)

    report = {}

    dim_customer_clean, report["dim_customer"] = clean_dim_customer(dim_customer)
    dim_supplier_clean, report["dim_supplier"] = clean_dim_supplier(dim_supplier)
    dim_store_clean, report["dim_store"] = clean_dim_store(dim_store)
    fact_sales_clean, report["fact_sales"] = clean_fact_sales(fact_sales)

    print_section("CLEANING SUMMARY")

    print(
        f"dim_customer -- city values filled:        {report['dim_customer']['city_filled']:,}"
    )
    print(
        f"dim_supplier -- supplier_name values filled: {report['dim_supplier']['supplier_name_filled']:,}"
    )
    print(
        f"dim_store    -- city values normalized:      {report['dim_store']['city_normalized']:,}"
    )
    print(
        f"fact_sales   -- duplicate rows removed:      {report['fact_sales']['duplicates_removed']:,}"
    )

    print("=" * 60)

    return {
        "dim_product": dim_product,
        "dim_store": dim_store_clean,
        "dim_customer": dim_customer_clean,
        "dim_supplier": dim_supplier_clean,
        "fact_sales": fact_sales_clean,
        "report": report,
    }


# ============================================================
# 6. SAVE CLEANED DATASETS
# ============================================================


def save_cleaned_datasets(cleaned_tables, cleaned_data_dir):
    """
    Save cleaned tables to data/cleaned/ as CSV.

    Parameters
    ----------
    cleaned_tables : dict
        The dict returned by clean_generated_dataset() (the
        "report" key is ignored here, since it isn't a table).
    cleaned_data_dir : Path
        Destination directory, created if it doesn't exist.
    """

    print_section("Saving cleaned datasets")

    cleaned_data_dir.mkdir(parents=True, exist_ok=True)

    for name, df in cleaned_tables.items():
        if name == "report":
            continue

        file_path = cleaned_data_dir / f"{name}.csv"

        df.to_csv(file_path, index=False)

        size_mb = file_path.stat().st_size / (1024 * 1024)

        print(
            f"Saved {name:15s} {len(df):>10,} rows  ->  {file_path.name}  ({size_mb:.2f} MB)"
        )

    print(f"\nOutput directory: {cleaned_data_dir}")


# ============================================================
# MODULE TEST
# ============================================================

if __name__ == "__main__":
    print("data_cleaning.py is a cleaning module.")
    print("Import clean_generated_dataset() from the profiling/cleaning workflow.")
