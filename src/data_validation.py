"""
GulfMart Retail Inventory Analytics
------------------------------------

Data validation module for the generated retail dataset.

Purpose
-------
This module validates whether the generated retail data is:

1. Structurally correct
2. Internally consistent
3. Referentially valid
4. Inventory mathematically consistent
5. Business-plausible

Architecture
------------
data_generation_config.py
    -> Defines assumptions

validate_generation_config.py
    -> Validates assumptions

data_generation.py
    -> Generates / simulates data

data_validation.py
    -> Validates generated data

Important
---------
This file should NOT generate or modify the dataset.

It should only inspect the data and report PASS / FAIL / REVIEW.
"""


# ============================================================
# IMPORTS
# ============================================================

import pandas as pd
import numpy as np


# ============================================================
# GENERAL VALIDATION HELPERS
# ============================================================


def print_section(title):
    """
    Print a clear section heading.
    """

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def print_check(name, passed, message):
    """
    Print a standardized validation result.

    Parameters
    ----------
    name : str
        Name of the validation check.

    passed : bool
        Whether the check passed.

    message : str
        Explanation of the result.
    """

    status = "PASS" if passed else "FAIL"

    print(f"{status}: {name} - {message}")


# ============================================================
# 1. DIMENSION TABLE VALIDATION
# ============================================================


def validate_dimension_table(
    df,
    table_name,
    key_column,
):
    """
    Validate a dimension table.

    Checks:
    - DataFrame exists
    - Required key exists
    - Key is not NULL
    - Key is unique
    - Table is not empty
    """

    print_section(f"{table_name} Validation")

    if df is None:
        print_check(
            table_name,
            False,
            "DataFrame is None.",
        )
        return False

    if df.empty:
        print_check(
            table_name,
            False,
            "Table is empty.",
        )
        return False

    if key_column not in df.columns:
        print_check(
            table_name,
            False,
            f"Missing key column: {key_column}",
        )
        return False

    null_keys = df[key_column].isna().sum()

    print_check(
        f"{table_name} key completeness",
        null_keys == 0,
        f"NULL {key_column} values: {null_keys}",
    )

    duplicate_keys = df[key_column].duplicated().sum()

    print_check(
        f"{table_name} key uniqueness",
        duplicate_keys == 0,
        f"Duplicate {key_column} values: {duplicate_keys}",
    )

    return null_keys == 0 and duplicate_keys == 0


# ============================================================
# 2. FACT SALES VALIDATION
# ============================================================


def validate_fact_sales(fact_sales):
    """
    Validate the fact_sales table.

    Checks:
    - Required columns
    - Transaction IDs
    - Dates
    - Quantity
    - Sales values
    - Foreign-key completeness
    """

    print_section("Fact Sales Validation")

    required_columns = [
        "transaction_id",
        "transaction_date",
        "store_id",
        "product_id",
        "customer_id",
        "quantity",
    ]

    missing_columns = [
        column for column in required_columns if column not in fact_sales.columns
    ]

    print_check(
        "Required columns",
        len(missing_columns) == 0,
        f"Missing columns: {missing_columns}",
    )

    if missing_columns:
        return False

    checks = []

    # --------------------------------------------------------
    # Transaction ID validation
    # --------------------------------------------------------

    duplicate_transactions = fact_sales["transaction_id"].duplicated().sum()

    duplicate_transactions_ok = duplicate_transactions == 0

    print_check(
        "Transaction ID uniqueness",
        duplicate_transactions_ok,
        f"Duplicate transactions: {duplicate_transactions}",
    )

    checks.append(duplicate_transactions_ok)

    # --------------------------------------------------------
    # Quantity validation
    # --------------------------------------------------------

    invalid_quantity = (fact_sales["quantity"] <= 0).sum()

    invalid_quantity_ok = invalid_quantity == 0

    print_check(
        "Positive sales quantity",
        invalid_quantity_ok,
        f"Invalid quantity rows: {invalid_quantity}",
    )

    checks.append(invalid_quantity_ok)

    # --------------------------------------------------------
    # Date validation
    # --------------------------------------------------------

    invalid_dates = fact_sales["transaction_date"].isna().sum()

    invalid_dates_ok = invalid_dates == 0

    print_check(
        "Sales dates",
        invalid_dates_ok,
        f"Missing transaction dates: {invalid_dates}",
    )

    checks.append(invalid_dates_ok)

    # --------------------------------------------------------
    # Foreign-key completeness
    # --------------------------------------------------------

    for column in [
        "store_id",
        "product_id",
        "customer_id",
    ]:
        missing_values = fact_sales[column].isna().sum()

        missing_values_ok = missing_values == 0

        print_check(
            f"{column} completeness",
            missing_values_ok,
            f"Missing values: {missing_values}",
        )

        checks.append(missing_values_ok)

    return all(checks)


# ============================================================
# 3. FOREIGN-KEY VALIDATION
# ============================================================


def validate_foreign_keys(
    fact_sales,
    dim_product,
    dim_store,
    dim_customer,
):
    """
    Validate foreign-key relationships between fact_sales
    and dimension tables.
    """

    print_section("Foreign-Key Validation")

    checks = []

    # --------------------------------------------------------
    # Product relationship
    # --------------------------------------------------------

    missing_products = (~fact_sales["product_id"].isin(dim_product["product_id"])).sum()

    print_check(
        "Sales -> Product",
        missing_products == 0,
        f"Unknown product IDs: {missing_products}",
    )

    checks.append(missing_products == 0)

    # --------------------------------------------------------
    # Store relationship
    # --------------------------------------------------------

    missing_stores = (~fact_sales["store_id"].isin(dim_store["store_id"])).sum()

    print_check(
        "Sales -> Store",
        missing_stores == 0,
        f"Unknown store IDs: {missing_stores}",
    )

    checks.append(missing_stores == 0)

    # --------------------------------------------------------
    # Customer relationship
    # --------------------------------------------------------

    missing_customers = (
        ~fact_sales["customer_id"].isin(dim_customer["customer_id"])
    ).sum()

    print_check(
        "Sales -> Customer",
        missing_customers == 0,
        f"Unknown customer IDs: {missing_customers}",
    )

    checks.append(missing_customers == 0)

    return all(checks)


# ============================================================
# 4. FACT INVENTORY STRUCTURE VALIDATION
# ============================================================


def validate_fact_inventory_structure(fact_inventory):
    """
    Validate the structure of fact_inventory.

    This check does NOT evaluate whether the inventory model
    is commercially realistic. It only checks that the expected
    fields exist and basic values are valid.
    """

    print_section("Fact Inventory Structure Validation")

    required_columns = [
        "date",  # was "transaction_date"
        "store_id",
        "product_id",
        "opening_stock",
        "closing_stock",
        "sales_units",
    ]

    optional_columns = [
        "demand_rate",
        "safety_stock_units",
        "lead_time_demand",
        "reorder_point",
        "review_period_demand",
        "target_stock_level",
        "planned_order_quantity",
        "receipts",
        "stockout_event",
        "low_stock_event",
        "inventory_status",
        "inventory_coverage_days",
    ]

    missing_required = [
        column for column in required_columns if column not in fact_inventory.columns
    ]

    print_check(
        "Required inventory columns",
        len(missing_required) == 0,
        f"Missing columns: {missing_required}",
    )

    if missing_required:
        return False

    present_optional = [
        column for column in optional_columns if column in fact_inventory.columns
    ]

    print(
        f"INFO: Optional inventory columns available: "
        f"{len(present_optional)}/{len(optional_columns)}"
    )

    return True


# ============================================================
# 5. INVENTORY VALUE VALIDATION
# ============================================================


def validate_non_negative_inventory(fact_inventory):
    """
    Check for negative inventory.

    Negative closing inventory should never occur in the
    final inventory simulation.
    """

    print_section("Negative Inventory Validation")

    negative_opening = (fact_inventory["opening_stock"] < 0).sum()

    negative_closing = (fact_inventory["closing_stock"] < 0).sum()

    print_check(
        "Opening inventory",
        negative_opening == 0,
        f"Negative opening-stock rows: {negative_opening}",
    )

    print_check(
        "Closing inventory",
        negative_closing == 0,
        f"Negative closing-stock rows: {negative_closing}",
    )

    total_negative = negative_opening + negative_closing

    rate = total_negative / len(fact_inventory) * 100

    print(f"Negative inventory rate: {rate:.2f}%")

    return total_negative == 0


# ============================================================
# 6. INVENTORY CONTINUITY VALIDATION
# ============================================================


def validate_inventory_continuity(fact_inventory):
    """
    Validate the basic inventory continuity equation.

    For each product-store combination:

        Opening Stock
        + Receipts
        - Fulfilled Sales
        = Closing Stock

    The validation automatically uses fulfilled_sales_units
    when that column exists.

    If the sequential simulation has not yet been implemented,
    sales_units is used as the fallback.
    """

    print_section("Inventory Continuity Validation")

    required_columns = [
        "store_id",
        "product_id",
        "date",
        "opening_stock",
        "closing_stock",
    ]

    missing = [
        column for column in required_columns if column not in fact_inventory.columns
    ]

    if missing:
        print_check(
            "Inventory continuity",
            False,
            f"Missing columns: {missing}",
        )
        return False

    # --------------------------------------------------------
    # Receipts
    # --------------------------------------------------------

    if "receipts" in fact_inventory.columns:
        receipts = fact_inventory["receipts"].fillna(0)
    else:
        receipts = 0

    # --------------------------------------------------------
    # Fulfilled sales
    # --------------------------------------------------------

    if "fulfilled_sales_units" in fact_inventory.columns:
        fulfilled_sales = fact_inventory["fulfilled_sales_units"].fillna(0)

    else:
        # Temporary fallback for the earlier model.
        fulfilled_sales = fact_inventory["sales_units"].fillna(0)

    expected_closing = fact_inventory["opening_stock"] + receipts - fulfilled_sales

    difference = fact_inventory["closing_stock"] - expected_closing

    failures = (difference.abs() > 0.000001).sum()

    rows_checked = len(fact_inventory)

    print(f"Rows checked: {rows_checked:,}")

    print_check(
        "Inventory continuity",
        failures == 0,
        f"Continuity failures: {failures}",
    )

    return failures == 0


# ============================================================
# 7. INVENTORY RECONCILIATION
# ============================================================


def validate_inventory_reconciliation(fact_inventory):
    """
    Validate sales reconciliation.

    When demand_units, fulfilled_sales_units and
    lost_sales_units are available:

        Demand
        = Fulfilled Sales
        + Lost Sales

    This is an important check for the sequential
    inventory simulation.
    """

    print_section("Inventory Reconciliation Validation")

    required_columns = [
        "demand_units",
        "fulfilled_sales_units",
        "lost_sales_units",
    ]

    if not all(column in fact_inventory.columns for column in required_columns):
        print("REVIEW: Sequential demand reconciliation columns are not available yet.")

        return None

    expected_demand = (
        fact_inventory["fulfilled_sales_units"] + fact_inventory["lost_sales_units"]
    )

    difference = fact_inventory["demand_units"] - expected_demand

    failures = (difference.abs() > 0.000001).sum()

    print_check(
        "Demand reconciliation",
        failures == 0,
        f"Reconciliation failures: {failures}",
    )

    return failures == 0


# ============================================================
# 8. STOCKOUT VALIDATION
# ============================================================


def validate_stockouts(fact_inventory):
    """
    Validate stockout and lost-sales behavior.

    A stockout should occur when closing inventory is zero
    and demand exists.

    This is primarily a business-plausibility check.
    """

    print_section("Stockout Validation")

    if "closing_stock" not in fact_inventory.columns:
        print_check(
            "Stockout validation",
            False,
            "closing_stock column is missing.",
        )
        return False

    if "demand_units" in fact_inventory.columns:
        demand = fact_inventory["demand_units"]

    else:
        demand = fact_inventory["sales_units"]

    stockout_rows = (fact_inventory["closing_stock"] <= 0) & (demand > 0)

    stockout_count = stockout_rows.sum()

    print(f"Stockout events: {stockout_count:,}")

    # --------------------------------------------------------
    # If the sequential model has been implemented, zero
    # stockouts may be suspicious rather than automatically
    # correct.
    # --------------------------------------------------------

    if "lost_sales_units" in fact_inventory.columns:
        lost_sales = fact_inventory["lost_sales_units"].fillna(0).sum()

        print(f"Lost-sales units: {lost_sales:,.0f}")

        if stockout_count == 0 and lost_sales == 0:
            print(
                "REVIEW: No stockouts or lost sales detected. "
                "Check whether inventory policy is too generous."
            )

            return None

    return True


# ============================================================
# 9. LOST SALES VALIDATION
# ============================================================


def validate_lost_sales(fact_inventory):
    """
    Validate lost-sales values.

    Lost sales must:
    - Never be negative
    - Never exceed demand
    """

    print_section("Lost Sales Validation")

    required_columns = [
        "demand_units",
        "lost_sales_units",
    ]

    if not all(column in fact_inventory.columns for column in required_columns):
        print("REVIEW: Lost-sales columns are not available yet.")

        return None

    negative_lost_sales = (fact_inventory["lost_sales_units"] < 0).sum()

    lost_sales_above_demand = (
        fact_inventory["lost_sales_units"] > fact_inventory["demand_units"]
    ).sum()

    print_check(
        "Non-negative lost sales",
        negative_lost_sales == 0,
        f"Negative lost-sales rows: {negative_lost_sales}",
    )

    print_check(
        "Lost sales <= demand",
        lost_sales_above_demand == 0,
        (f"Rows where lost sales exceed demand: {lost_sales_above_demand}"),
    )

    return negative_lost_sales == 0 and lost_sales_above_demand == 0


# ============================================================
# 10. REPLENISHMENT VALIDATION
# ============================================================


def validate_replenishment(fact_inventory):
    """
    Validate replenishment quantities.

    Checks:
    - Orders are non-negative
    - Orders do not occur without inventory need
      when inventory-position information exists
    """

    print_section("Replenishment Validation")

    if "planned_order_quantity" not in fact_inventory.columns:
        print("REVIEW: planned_order_quantity is not available.")

        return None

    negative_orders = (fact_inventory["planned_order_quantity"] < 0).sum()

    print_check(
        "Non-negative order quantities",
        negative_orders == 0,
        f"Negative order rows: {negative_orders}",
    )

    # --------------------------------------------------------
    # Inventory-position logic
    # --------------------------------------------------------

    if {
        "inventory_position",
        "reorder_point",
    }.issubset(fact_inventory.columns):
        unnecessary_orders = (
            (fact_inventory["inventory_position"] > fact_inventory["reorder_point"])
            & (fact_inventory["planned_order_quantity"] > 0)
        ).sum()

        print_check(
            "Orders respect inventory position",
            unnecessary_orders == 0,
            (f"Orders placed above reorder point: {unnecessary_orders}"),
        )

    return negative_orders == 0


# ============================================================
# 11. INVENTORY COVERAGE VALIDATION
# ============================================================


def validate_inventory_coverage(fact_inventory):
    """
    Validate inventory coverage.

    Inventory coverage is useful for identifying unrealistic
    accumulation of inventory.

    Formula:

        Closing Inventory
        -----------------
        Daily Demand Rate
    """

    print_section("Inventory Coverage Validation")

    if "inventory_coverage_days" not in fact_inventory.columns:
        print("REVIEW: inventory_coverage_days is not available.")

        return None

    coverage = (
        fact_inventory["inventory_coverage_days"]
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    if coverage.empty:
        print("REVIEW: No valid inventory coverage values.")

        return None

    print(coverage.describe())

    negative_coverage = (coverage < 0).sum()

    print_check(
        "Non-negative inventory coverage",
        negative_coverage == 0,
        f"Negative coverage rows: {negative_coverage}",
    )

    # --------------------------------------------------------
    # Business-plausibility review
    # --------------------------------------------------------
    #
    # We intentionally do NOT automatically fail on high
    # coverage because slow-moving products can legitimately
    # have high days of inventory.
    #
    # Extremely high values should instead trigger REVIEW.
    # --------------------------------------------------------

    extreme_coverage = (coverage > 365).sum()

    extreme_rate = extreme_coverage / len(coverage) * 100

    print(f"Coverage > 365 days: {extreme_coverage:,} ({extreme_rate:.2f}%)")

    if extreme_rate > 5:
        print("REVIEW: A large share of inventory has more than one year of coverage.")

    return negative_coverage == 0


# ============================================================
# 12. INVENTORY STATUS VALIDATION
# ============================================================


def validate_inventory_status(fact_inventory):
    """
    Validate inventory status values.
    """

    print_section("Inventory Status Validation")

    if "inventory_status" not in fact_inventory.columns:
        print("REVIEW: inventory_status is not available.")

        return None

    valid_statuses = {
        "Healthy",
        "Low Stock",
        "Stockout",
        "Overstock",
    }

    actual_statuses = set(fact_inventory["inventory_status"].dropna().unique())

    invalid_statuses = actual_statuses - valid_statuses

    print_check(
        "Inventory status values",
        len(invalid_statuses) == 0,
        f"Invalid statuses: {invalid_statuses}",
    )

    return len(invalid_statuses) == 0


# ============================================================
# 13. INVENTORY POLICY VALIDATION
# ============================================================


def validate_inventory_policy(fact_inventory):
    """
    Validate the mathematical relationship between:

        Lead-time demand
        Safety stock
        Reorder point
        Review-period demand
        Target stock

    Expected:

        ROP
        = Lead-time Demand + Safety Stock

        Target Stock
        = Lead-time Demand
        + Review-period Demand
        + Safety Stock
    """

    print_section("Inventory Policy Validation")

    required_columns = [
        "lead_time_demand",
        "safety_stock_units",
        "reorder_point",
        "review_period_demand",
        "target_stock_level",
    ]

    if not all(column in fact_inventory.columns for column in required_columns):
        print("REVIEW: Inventory policy columns are incomplete.")

        return None

    # --------------------------------------------------------
    # Reorder point
    # --------------------------------------------------------

    expected_rop = (
        fact_inventory["lead_time_demand"] + fact_inventory["safety_stock_units"]
    )

    # np.isclose combines a relative tolerance (rtol) and an absolute
    # tolerance (atol): |a - b| <= atol + rtol * |b|. This is
    # necessary rather than a fixed epsilon because fact_inventory
    # may be float32 (downcast before saving in save_datasets()),
    # where independent per-column rounding of derived columns
    # naturally breaks exact equality between formulas like
    # reorder_point = lead_time_demand + safety_stock_units, even
    # when the underlying calculation was correct.
    rop_failures = (
        ~np.isclose(
            fact_inventory["reorder_point"],
            expected_rop,
            rtol=1e-4,
            atol=1e-4,
        )
    ).sum()

    print_check(
        "Reorder point formula",
        rop_failures == 0,
        f"ROP formula failures: {rop_failures}",
    )

    # --------------------------------------------------------
    # Target stock
    # --------------------------------------------------------

    expected_target = (
        fact_inventory["lead_time_demand"]
        + fact_inventory["review_period_demand"]
        + fact_inventory["safety_stock_units"]
    )

    target_failures = (
        ~np.isclose(
            fact_inventory["target_stock_level"],
            expected_target,
            rtol=1e-4,
            atol=1e-4,
        )
    ).sum()

    print_check(
        "Target stock formula",
        target_failures == 0,
        f"Target stock formula failures: {target_failures}",
    )

    return rop_failures == 0 and target_failures == 0


# ============================================================
# 14. DUPLICATE INVENTORY RECORD VALIDATION
# ============================================================


def validate_inventory_duplicates(fact_inventory):
    """
    Check whether there are duplicate daily records for the
    same store-product-date combination.
    """

    print_section("Inventory Duplicate Validation")

    required_columns = [
        "date",
        "store_id",
        "product_id",
    ]

    if not all(column in fact_inventory.columns for column in required_columns):
        print("REVIEW: Cannot check inventory duplicates.")

        return None

    duplicate_rows = fact_inventory.duplicated(
        subset=[
            "date",
            "store_id",
            "product_id",
        ]
    ).sum()

    print_check(
        "Daily product-store uniqueness",
        duplicate_rows == 0,
        f"Duplicate daily inventory rows: {duplicate_rows}",
    )

    return duplicate_rows == 0


# ============================================================
# 15. DATASET SUMMARY
# ============================================================


def print_dataset_summary(
    fact_sales,
    fact_inventory,
    dim_product,
    dim_store,
    dim_customer,
    dim_supplier,
):
    """
    Print a concise dataset summary.
    """

    print_section("Dataset Summary")

    print(f"Products:       {len(dim_product):,}")

    print(f"Stores:         {len(dim_store):,}")

    print(f"Customers:      {len(dim_customer):,}")

    print(f"Suppliers:      {len(dim_supplier):,}")

    print(f"Sales rows:     {len(fact_sales):,}")

    print(f"Inventory rows: {len(fact_inventory):,}")


# ============================================================
# 16. COMPLETE VALIDATION PIPELINE
# ============================================================


def validate_generated_dataset(
    fact_sales,
    fact_inventory,
    dim_product,
    dim_store,
    dim_customer,
    dim_supplier,
):
    """
    Run the complete generated-dataset validation pipeline.

    Returns
    -------
    dict
        Validation results by category.
    """

    print()
    print("=" * 60)
    print("GulfMart Retail Inventory Dataset Validation")
    print("=" * 60)

    results = {}

    # --------------------------------------------------------
    # Dataset summary
    # --------------------------------------------------------

    print_dataset_summary(
        fact_sales,
        fact_inventory,
        dim_product,
        dim_store,
        dim_customer,
        dim_supplier,
    )

    # --------------------------------------------------------
    # Dimension validation
    # --------------------------------------------------------

    results["product_dimension"] = validate_dimension_table(
        dim_product,
        "Product Dimension",
        "product_id",
    )

    results["store_dimension"] = validate_dimension_table(
        dim_store,
        "Store Dimension",
        "store_id",
    )

    results["customer_dimension"] = validate_dimension_table(
        dim_customer,
        "Customer Dimension",
        "customer_id",
    )

    results["supplier_dimension"] = validate_dimension_table(
        dim_supplier,
        "Supplier Dimension",
        "supplier_id",
    )

    # --------------------------------------------------------
    # Sales validation
    # --------------------------------------------------------

    results["fact_sales"] = validate_fact_sales(fact_sales)

    results["foreign_keys"] = validate_foreign_keys(
        fact_sales,
        dim_product,
        dim_store,
        dim_customer,
    )

    # --------------------------------------------------------
    # Inventory structure
    # --------------------------------------------------------

    results["inventory_structure"] = validate_fact_inventory_structure(fact_inventory)

    # --------------------------------------------------------
    # Inventory duplicates
    # --------------------------------------------------------

    results["inventory_duplicates"] = validate_inventory_duplicates(fact_inventory)

    # --------------------------------------------------------
    # Inventory policy
    # --------------------------------------------------------

    results["inventory_policy"] = validate_inventory_policy(fact_inventory)

    # --------------------------------------------------------
    # Inventory continuity
    # --------------------------------------------------------

    results["inventory_continuity"] = validate_inventory_continuity(fact_inventory)

    # --------------------------------------------------------
    # Negative inventory
    # --------------------------------------------------------

    results["negative_inventory"] = validate_non_negative_inventory(fact_inventory)

    # --------------------------------------------------------
    # Demand reconciliation
    # --------------------------------------------------------

    results["inventory_reconciliation"] = validate_inventory_reconciliation(
        fact_inventory
    )

    # --------------------------------------------------------
    # Lost sales
    # --------------------------------------------------------

    results["lost_sales"] = validate_lost_sales(fact_inventory)

    # --------------------------------------------------------
    # Stockouts
    # --------------------------------------------------------

    results["stockouts"] = validate_stockouts(fact_inventory)

    # --------------------------------------------------------
    # Replenishment
    # --------------------------------------------------------

    results["replenishment"] = validate_replenishment(fact_inventory)

    # --------------------------------------------------------
    # Inventory coverage
    # --------------------------------------------------------

    results["inventory_coverage"] = validate_inventory_coverage(fact_inventory)

    # --------------------------------------------------------
    # Inventory status
    # --------------------------------------------------------

    results["inventory_status"] = validate_inventory_status(fact_inventory)

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print_section("FINAL VALIDATION SUMMARY")

    passed = 0
    failed = 0
    review = 0

    for check_name, result in results.items():
        if result is None:
            status = "REVIEW"
            review += 1

        elif result:
            status = "PASS"
            passed += 1

        else:
            status = "FAIL"
            failed += 1

        print(f"{status:<8} {check_name}")

    print()
    print(f"PASS:   {passed}")
    print(f"FAIL:   {failed}")
    print(f"REVIEW: {review}")

    print()

    if failed == 0 and review == 0:
        print("ALL DATA VALIDATION CHECKS PASSED")

    elif failed == 0:
        print("DATA VALIDATION COMPLETED WITH BUSINESS REVIEW ITEMS")

    else:
        print("DATA VALIDATION FAILED")

    print("=" * 60)

    return results


# ============================================================
# MODULE TEST
# ============================================================

if __name__ == "__main__":
    print("data_validation.py is a validation module.")

    print("Import validate_generated_dataset() from the data-generation workflow.")
