# ============================================================
# GulfMart Retail Inventory Analytics
# Synthetic Dataset Generator
# ============================================================

"""
Generate a realistic synthetic retail dataset for
inventory and sales analytics.

Generation pipeline:

1. Generate dimension tables
2. Generate sales transactions
3. Generate daily inventory
4. Inject controlled data-quality issues
5. Validate generated data
6. Save datasets to CSV
"""

# Add the imports

from pathlib import Path

import numpy as np
import pandas as pd

from data_generation_config import (
    RANDOM_SEED,
    START_DATE,
    END_DATE,
    NUMBER_OF_STORES,
    NUMBER_OF_PRODUCTS,
    NUMBER_OF_CUSTOMERS,
    NUMBER_OF_SUPPLIERS,
    TARGET_SALES_TRANSACTIONS,
    RAW_DATA_DIR,
    PRODUCT_CATEGORIES,
    DEMAND_CLASS_PROBABILITIES,
    DEMAND_CLASS_FACTORS,
    DEMAND_TRAJECTORY_PROBABILITIES,
    DEMAND_TRAJECTORY_FACTORS,
    STORE_TYPE_PROBABILITIES,
    STORE_TYPE_DEMAND_FACTORS,
    REGION_CITIES,
    REGION_DEMAND_FACTORS,
    SUPPLIER_REGION_PROBABILITIES,
    SUPPLIER_LEAD_TIME_RANGES,
    SUPPLIER_STATUS_PROBABILITIES,
    CUSTOMER_SEGMENT_PROBABILITIES,
    CUSTOMER_AGE_GROUPS,
    CUSTOMER_GENDER_PROBABILITIES,
    DAY_OF_WEEK_FACTORS,
    CATEGORY_SEASONALITY_FACTORS,
    PROMOTION_PROBABILITY,
    PROMOTION_DISCOUNT_RANGE,
    PROMOTION_DEMAND_LIFT,
    PRODUCT_COST_RANGE,
    PRODUCT_MARGIN_RANGE,
    SAFETY_STOCK_DAYS,
    INITIAL_INVENTORY_DAYS,
    MINIMUM_COVERAGE_DAYS,
    LOW_SAFETY_STOCK_PROBABILITY,
    LONG_LEAD_TIME_RISK_PROBABILITY,
    DEMAND_SPIKE_PROBABILITY,
    DEMAND_SPIKE_FACTOR,
    INJECT_DATA_QUALITY_ISSUES,
    DATA_QUALITY_ISSUE_PROBABILITY,
)

# ============================================================
# Random Number Generator
# ============================================================

rng = np.random.default_rng(RANDOM_SEED)

# ============================================================
# Dimension Table Generators
# ============================================================


def generate_dim_date():
    """Generate the date dimension."""

    dates = pd.date_range(
        start=START_DATE,
        end=END_DATE,
        freq="D",
    )

    dim_date = pd.DataFrame(
        {
            "date": dates,
        }
    )

    dim_date["year"] = dim_date["date"].dt.year

    dim_date["quarter"] = "Q" + dim_date["date"].dt.quarter.astype(str)

    dim_date["month"] = dim_date["date"].dt.month

    dim_date["month_name"] = dim_date["date"].dt.month_name()

    dim_date["week_of_year"] = dim_date["date"].dt.isocalendar().week.astype(int)

    dim_date["day"] = dim_date["date"].dt.day

    dim_date["day_name"] = dim_date["date"].dt.day_name()

    dim_date["day_of_week"] = dim_date["date"].dt.dayofweek

    dim_date["is_weekend"] = dim_date["day_of_week"] >= 4

    dim_date["season"] = np.select(
        [
            dim_date["month"].isin([12, 1, 2]),
            dim_date["month"].isin([3, 4, 5]),
            dim_date["month"].isin([6, 7, 8]),
            dim_date["month"].isin([9, 10, 11]),
        ],
        [
            "Winter",
            "Spring",
            "Summer",
            "Autumn",
        ],
        default="Unknown",
    )

    dim_date["is_ramadan"] = False

    dim_date["is_eid_period"] = False

    return dim_date


def generate_dim_supplier():
    """Generate the supplier dimension."""

    supplier_ids = [f"SUP{i:03d}" for i in range(1, NUMBER_OF_SUPPLIERS + 1)]

    supplier_names = [
        f"GulfMart Supplier {i:03d}" for i in range(1, NUMBER_OF_SUPPLIERS + 1)
    ]

    supplier_regions = rng.choice(
        list(SUPPLIER_REGION_PROBABILITIES.keys()),
        size=NUMBER_OF_SUPPLIERS,
        p=list(SUPPLIER_REGION_PROBABILITIES.values()),
    )

    lead_time_days = np.array(
        [
            rng.integers(
                SUPPLIER_LEAD_TIME_RANGES[region][0],
                SUPPLIER_LEAD_TIME_RANGES[region][1] + 1,
            )
            for region in supplier_regions
        ]
    )

    minimum_order_qty = rng.choice(
        [10, 25, 50, 100, 200, 500],
        size=NUMBER_OF_SUPPLIERS,
    )

    supplier_status = rng.choice(
        list(SUPPLIER_STATUS_PROBABILITIES.keys()),
        size=NUMBER_OF_SUPPLIERS,
        p=list(SUPPLIER_STATUS_PROBABILITIES.values()),
    )

    dim_supplier = pd.DataFrame(
        {
            "supplier_id": supplier_ids,
            "supplier_name": supplier_names,
            "supplier_region": supplier_regions,
            "lead_time_days": lead_time_days,
            "minimum_order_qty": minimum_order_qty,
            "supplier_status": supplier_status,
        }
    )

    return dim_supplier


def generate_dim_product():
    """Generate the product dimension."""

    product_ids = [f"PROD{i:04d}" for i in range(1, NUMBER_OF_PRODUCTS + 1)]

    # ---------------------------------------------------------
    # Product category and subcategory
    # ---------------------------------------------------------

    categories = list(PRODUCT_CATEGORIES.keys())

    category_weights = np.array(
        [
            0.20,  # Grocery
            0.12,  # Beverages
            0.12,  # Personal Care
            0.12,  # Household
            0.10,  # Electronics
            0.12,  # Fashion
            0.10,  # Home & Living
            0.12,  # Beauty
        ]
    )

    category_weights = category_weights / category_weights.sum()

    product_categories = rng.choice(
        categories,
        size=NUMBER_OF_PRODUCTS,
        p=category_weights,
    )

    product_subcategories = [
        rng.choice(PRODUCT_CATEGORIES[category]) for category in product_categories
    ]

    # ---------------------------------------------------------
    # Product names and brands
    # ---------------------------------------------------------

    product_names = [
        f"{subcategory} Product {i:04d}"
        for i, subcategory in enumerate(
            product_subcategories,
            start=1,
        )
    ]

    brands = [
        "GulfMart",
        "PrimeChoice",
        "DailyValue",
        "SmartBuy",
        "FreshLife",
        "HomePlus",
        "TechPro",
        "UrbanStyle",
        "PureCare",
        "ValueMax",
    ]

    product_brands = rng.choice(
        brands,
        size=NUMBER_OF_PRODUCTS,
    )

    # ---------------------------------------------------------
    # Supplier assignment
    # ---------------------------------------------------------

    supplier_ids = [f"SUP{i:03d}" for i in range(1, NUMBER_OF_SUPPLIERS + 1)]

    product_supplier_ids = rng.choice(
        supplier_ids,
        size=NUMBER_OF_PRODUCTS,
    )

    # ---------------------------------------------------------
    # Demand classification
    # ---------------------------------------------------------

    demand_classes = list(DEMAND_CLASS_PROBABILITIES.keys())

    demand_class = rng.choice(
        demand_classes,
        size=NUMBER_OF_PRODUCTS,
        p=list(DEMAND_CLASS_PROBABILITIES.values()),
    )

    # ---------------------------------------------------------
    # Demand trajectory
    # ---------------------------------------------------------

    demand_trajectories = list(DEMAND_TRAJECTORY_PROBABILITIES.keys())

    demand_trajectory = rng.choice(
        demand_trajectories,
        size=NUMBER_OF_PRODUCTS,
        p=list(DEMAND_TRAJECTORY_PROBABILITIES.values()),
    )

    # ---------------------------------------------------------
    # Base demand
    # ---------------------------------------------------------
    #
    # This represents the underlying average daily demand
    # before store, seasonality, promotion, weekday and
    # trajectory effects are applied.
    # ---------------------------------------------------------

    base_demand = np.zeros(NUMBER_OF_PRODUCTS)

    for demand_type in demand_classes:
        mask = demand_class == demand_type

        if demand_type == "Fast-moving":
            base_demand[mask] = rng.uniform(
                8,
                25,
                size=mask.sum(),
            )

        elif demand_type == "Medium-moving":
            base_demand[mask] = rng.uniform(
                2,
                8,
                size=mask.sum(),
            )

        elif demand_type == "Slow-moving":
            base_demand[mask] = rng.uniform(
                0.2,
                2,
                size=mask.sum(),
            )

    # ---------------------------------------------------------
    # Product cost
    # ---------------------------------------------------------

    unit_cost = rng.uniform(
        PRODUCT_COST_RANGE[0],
        PRODUCT_COST_RANGE[1],
        size=NUMBER_OF_PRODUCTS,
    )

    # ---------------------------------------------------------
    # Target margin
    # ---------------------------------------------------------

    target_margin = rng.uniform(
        PRODUCT_MARGIN_RANGE[0],
        PRODUCT_MARGIN_RANGE[1],
        size=NUMBER_OF_PRODUCTS,
    )

    # ---------------------------------------------------------
    # Selling price
    # ---------------------------------------------------------
    #
    # Margin formula:
    #
    # Margin % =
    # (Selling Price - Unit Cost) / Selling Price
    #
    # Therefore:
    #
    # Selling Price =
    # Unit Cost / (1 - Margin %)
    # ---------------------------------------------------------

    selling_price = unit_cost / (1 - target_margin)

    selling_price = np.round(
        selling_price,
        2,
    )

    unit_cost = np.round(
        unit_cost,
        2,
    )

    # ---------------------------------------------------------
    # Product lifecycle
    # ---------------------------------------------------------

    project_start = pd.Timestamp(START_DATE)
    project_end = pd.Timestamp(END_DATE)

    launch_dates = project_start + pd.to_timedelta(
        rng.integers(
            0,
            (project_end - project_start).days + 1,
            size=NUMBER_OF_PRODUCTS,
        ),
        unit="D",
    )

    product_status = rng.choice(
        ["Active", "Discontinued"],
        size=NUMBER_OF_PRODUCTS,
        p=[0.95, 0.05],
    )

    # ---------------------------------------------------------
    # Shelf life
    # ---------------------------------------------------------

    shelf_life_days = np.zeros(
        NUMBER_OF_PRODUCTS,
        dtype=int,
    )

    for category in categories:
        mask = product_categories == category

        if category in [
            "Grocery",
            "Beverages",
            "Personal Care",
            "Beauty",
        ]:
            shelf_life_days[mask] = rng.choice(
                [30, 60, 90, 180, 365, 730],
                size=mask.sum(),
            )

        elif category in [
            "Fashion",
            "Electronics",
            "Home & Living",
        ]:
            shelf_life_days[mask] = rng.choice(
                [365, 730, 1095, 1825],
                size=mask.sum(),
            )

        else:
            shelf_life_days[mask] = rng.choice(
                [90, 180, 365, 730],
                size=mask.sum(),
            )

    # ---------------------------------------------------------
    # Build product dimension
    # ---------------------------------------------------------

    dim_product = pd.DataFrame(
        {
            "product_id": product_ids,
            "product_name": product_names,
            "category": product_categories,
            "subcategory": product_subcategories,
            "brand": product_brands,
            "supplier_id": product_supplier_ids,
            "unit_cost": unit_cost,
            "selling_price": selling_price,
            "product_status": product_status,
            "product_launch_date": launch_dates,
            "shelf_life_days": shelf_life_days,
            "demand_class": demand_class,
            "demand_trajectory": demand_trajectory,
            "base_demand": np.round(
                base_demand,
                2,
            ),
        }
    )

    return dim_product


def generate_dim_store():
    """Generate the store dimension."""

    # ---------------------------------------------------------
    # Store IDs and names
    # ---------------------------------------------------------

    store_ids = [f"STORE{i:03d}" for i in range(1, NUMBER_OF_STORES + 1)]

    store_names = [f"GulfMart Store {i:03d}" for i in range(1, NUMBER_OF_STORES + 1)]

    # ---------------------------------------------------------
    # Store type
    # ---------------------------------------------------------

    store_types = list(STORE_TYPE_PROBABILITIES.keys())

    store_type = rng.choice(
        store_types,
        size=NUMBER_OF_STORES,
        p=list(STORE_TYPE_PROBABILITIES.values()),
    )

    # ---------------------------------------------------------
    # Region
    # ---------------------------------------------------------

    regions = list(REGION_CITIES.keys())

    region = rng.choice(
        regions,
        size=NUMBER_OF_STORES,
    )

    # ---------------------------------------------------------
    # City
    # ---------------------------------------------------------

    city = [rng.choice(REGION_CITIES[selected_region]) for selected_region in region]

    # ---------------------------------------------------------
    # Store size
    # ---------------------------------------------------------

    store_size_sqm = np.zeros(
        NUMBER_OF_STORES,
        dtype=int,
    )

    for store_type_name in store_types:
        mask = store_type == store_type_name

        if store_type_name == "Hypermarket":
            store_size_sqm[mask] = rng.integers(
                5_000,
                15_001,
                size=mask.sum(),
            )

        elif store_type_name == "Supermarket":
            store_size_sqm[mask] = rng.integers(
                1_500,
                5_001,
                size=mask.sum(),
            )

        elif store_type_name == "Express":
            store_size_sqm[mask] = rng.integers(
                300,
                1_501,
                size=mask.sum(),
            )

        elif store_type_name == "E-commerce":
            # E-commerce does not represent a
            # traditional physical store.
            store_size_sqm[mask] = rng.integers(
                500,
                3_001,
                size=mask.sum(),
            )

    # ---------------------------------------------------------
    # Opening date
    # ---------------------------------------------------------

    project_start = pd.Timestamp(START_DATE)

    project_end = pd.Timestamp(END_DATE)

    opening_dates = project_start + pd.to_timedelta(
        rng.integers(
            0,
            (project_end - project_start).days + 1,
            size=NUMBER_OF_STORES,
        ),
        unit="D",
    )

    # ---------------------------------------------------------
    # Channel
    # ---------------------------------------------------------

    channel = np.where(
        store_type == "E-commerce",
        "E-commerce",
        "Physical",
    )

    # ---------------------------------------------------------
    # Store demand factor
    # ---------------------------------------------------------

    store_type_factor = np.array(
        [STORE_TYPE_DEMAND_FACTORS[selected_type] for selected_type in store_type]
    )

    region_factor = np.array(
        [REGION_DEMAND_FACTORS[selected_region] for selected_region in region]
    )

    store_demand_factor = store_type_factor * region_factor

    store_demand_factor = np.round(
        store_demand_factor,
        2,
    )

    # ---------------------------------------------------------
    # Build store dimension
    # ---------------------------------------------------------

    dim_store = pd.DataFrame(
        {
            "store_id": store_ids,
            "store_name": store_names,
            "city": city,
            "region": region,
            "store_type": store_type,
            "opening_date": opening_dates,
            "store_size_sqm": store_size_sqm,
            "channel": channel,
            "store_demand_factor": store_demand_factor,
        }
    )

    return dim_store


def generate_dim_customer():
    """Generate the customer dimension."""
    pass


# ============================================================
# Fact Table Generators
# ============================================================


def generate_fact_sales(
    dim_date,
    dim_product,
    dim_store,
    dim_customer,
):
    """Generate sales transactions based on modeled demand."""
    pass


def generate_fact_inventory(
    dim_date,
    dim_product,
    dim_store,
    dim_supplier,
    fact_sales,
):
    """Generate daily inventory movements and closing stock."""
    pass


# ============================================================
# Data Quality
# ============================================================


def inject_data_quality_issues(
    dim_product,
    dim_store,
    dim_customer,
    dim_supplier,
    fact_sales,
    fact_inventory,
):
    """Inject a small number of controlled data-quality issues."""
    pass


def validate_generated_dataset(
    dim_date,
    dim_product,
    dim_store,
    dim_customer,
    dim_supplier,
    fact_sales,
    fact_inventory,
):
    """Validate generated tables and relationships."""
    pass


# ============================================================
# Output
# ============================================================


def save_datasets(
    dim_date,
    dim_product,
    dim_store,
    dim_customer,
    dim_supplier,
    fact_sales,
    fact_inventory,
):
    """Save generated datasets as CSV files."""
    pass


# ============================================================
# Main Generation Pipeline
# ============================================================


def generate_all_data():
    """Run the complete synthetic dataset generation pipeline."""
    pass


if __name__ == "__main__":
    dim_store = generate_dim_store()

    expected_rows = NUMBER_OF_STORES

    # ---------------------------------------------------------
    # Basic validation
    # ---------------------------------------------------------

    assert len(dim_store) == expected_rows

    assert dim_store["store_id"].is_unique

    assert not dim_store["store_id"].isna().any()

    assert not dim_store["store_name"].isna().any()

    assert not dim_store["city"].isna().any()

    assert not dim_store["region"].isna().any()

    assert not dim_store["store_type"].isna().any()

    assert not dim_store["opening_date"].isna().any()

    assert not dim_store["store_size_sqm"].isna().any()

    assert not dim_store["channel"].isna().any()

    assert not dim_store["store_demand_factor"].isna().any()

    # ---------------------------------------------------------
    # Business-rule validation
    # ---------------------------------------------------------

    assert (dim_store["store_size_sqm"] > 0).all()

    assert (dim_store["store_demand_factor"] > 0).all()

    assert (dim_store["opening_date"] >= pd.Timestamp(START_DATE)).all()

    assert (dim_store["opening_date"] <= pd.Timestamp(END_DATE)).all()

    # ---------------------------------------------------------
    # Region-city consistency
    # ---------------------------------------------------------

    for _, row in dim_store.iterrows():
        assert row["city"] in REGION_CITIES[row["region"]]

    # ---------------------------------------------------------
    # Channel consistency
    # ---------------------------------------------------------

    ecommerce_check = (
        dim_store.loc[
            dim_store["store_type"] == "E-commerce",
            "channel",
        ]
        == "E-commerce"
    ).all()

    physical_check = (
        dim_store.loc[
            dim_store["store_type"] != "E-commerce",
            "channel",
        ]
        == "Physical"
    ).all()

    assert ecommerce_check
    assert physical_check

    # ---------------------------------------------------------
    # Store type / demand factor validation
    # ---------------------------------------------------------

    expected_demand_factor = dim_store["store_type"].map(
        STORE_TYPE_DEMAND_FACTORS
    ) * dim_store["region"].map(REGION_DEMAND_FACTORS)

    assert np.allclose(
        dim_store["store_demand_factor"],
        expected_demand_factor.round(2),
    )

    # ---------------------------------------------------------
    # Output
    # ---------------------------------------------------------

    print("=" * 60)
    print("dim_store Validation")
    print("=" * 60)

    print(f"PASS: Row count = {len(dim_store):,}")

    print("PASS: Store IDs are unique.")

    print("PASS: No missing store IDs.")

    print("PASS: No missing store names.")

    print("PASS: No missing cities.")

    print("PASS: No missing regions.")

    print("PASS: Store sizes are positive.")

    print("PASS: Opening dates are within the project period.")

    print("PASS: Region-city relationships are valid.")

    print("PASS: Channel assignments are valid.")

    print("PASS: Store demand factors are calculated correctly.")

    print("\nStore Type Distribution:")

    print(dim_store["store_type"].value_counts().sort_index())

    print("\nRegion Distribution:")

    print(dim_store["region"].value_counts().sort_index())

    print("\nChannel Distribution:")

    print(dim_store["channel"].value_counts().sort_index())

    print("\nSample Stores:")

    print(dim_store.head(10).to_string(index=False))
