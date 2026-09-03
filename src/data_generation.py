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
    CUSTOMER_CHANNEL_PROBABILITIES,
    CUSTOMER_PURCHASE_FREQUENCY_FACTORS,
    CUSTOMER_BASKET_FACTORS,
    CUSTOMER_PRICE_SENSITIVITY,
    TRANSACTION_QUANTITY_RANGE,
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

    # ---------------------------------------------------------
    # Customer IDs
    # ---------------------------------------------------------

    customer_ids = [f"CUST{i:05d}" for i in range(1, NUMBER_OF_CUSTOMERS + 1)]

    # ---------------------------------------------------------
    # Customer segments
    # ---------------------------------------------------------

    customer_segments = list(CUSTOMER_SEGMENT_PROBABILITIES.keys())

    customer_segment = rng.choice(
        customer_segments,
        size=NUMBER_OF_CUSTOMERS,
        p=list(CUSTOMER_SEGMENT_PROBABILITIES.values()),
    )

    # ---------------------------------------------------------
    # Gender
    # ---------------------------------------------------------

    genders = list(CUSTOMER_GENDER_PROBABILITIES.keys())

    gender = rng.choice(
        genders,
        size=NUMBER_OF_CUSTOMERS,
        p=list(CUSTOMER_GENDER_PROBABILITIES.values()),
    )

    # ---------------------------------------------------------
    # Age group
    # ---------------------------------------------------------

    age_group = rng.choice(
        CUSTOMER_AGE_GROUPS,
        size=NUMBER_OF_CUSTOMERS,
    )

    # ---------------------------------------------------------
    # City
    # ---------------------------------------------------------
    #
    # Customers are assigned to cities represented in
    # the retailer's store network.
    # ---------------------------------------------------------

    customer_cities = [city for cities in REGION_CITIES.values() for city in cities]

    city = rng.choice(
        customer_cities,
        size=NUMBER_OF_CUSTOMERS,
    )

    # ---------------------------------------------------------
    # Customer tenure
    # ---------------------------------------------------------
    #
    # Represents how long the customer has been in the
    # retailer's customer base.
    # ---------------------------------------------------------

    project_start = pd.Timestamp(START_DATE)

    project_end = pd.Timestamp(END_DATE)

    customer_start_dates = project_start + pd.to_timedelta(
        rng.integers(
            0,
            (project_end - project_start).days + 1,
            size=NUMBER_OF_CUSTOMERS,
        ),
        unit="D",
    )

    customer_tenure_days = (project_end - customer_start_dates).days

    # ---------------------------------------------------------
    # Preferred channel
    # ---------------------------------------------------------

    channels = list(CUSTOMER_CHANNEL_PROBABILITIES.keys())

    preferred_channel = rng.choice(
        channels,
        size=NUMBER_OF_CUSTOMERS,
        p=list(CUSTOMER_CHANNEL_PROBABILITIES.values()),
    )

    # ---------------------------------------------------------
    # Purchase frequency factor
    # ---------------------------------------------------------

    purchase_frequency_factor = (
        pd.Series(customer_segment)
        .map(CUSTOMER_PURCHASE_FREQUENCY_FACTORS)
        .to_numpy()
        .copy()
    )

    # Add controlled customer-level variation.
    purchase_frequency_factor *= rng.uniform(
        0.85,
        1.15,
        size=NUMBER_OF_CUSTOMERS,
    )

    purchase_frequency_factor = np.round(
        purchase_frequency_factor,
        2,
    )

    # ---------------------------------------------------------
    # Average basket factor
    # ---------------------------------------------------------

    average_basket_factor = (
        pd.Series(customer_segment).map(CUSTOMER_BASKET_FACTORS).to_numpy().copy()
    )

    # Add controlled customer-level variation.
    average_basket_factor *= rng.uniform(
        0.85,
        1.15,
        size=NUMBER_OF_CUSTOMERS,
    )

    average_basket_factor = np.round(
        average_basket_factor,
        2,
    )

    # ---------------------------------------------------------
    # Price sensitivity
    # ---------------------------------------------------------

    price_sensitivity = (
        pd.Series(customer_segment).map(CUSTOMER_PRICE_SENSITIVITY).to_numpy().copy()
    )

    # Add controlled variation while keeping the values
    # within the 0-1 range.
    price_sensitivity *= rng.uniform(
        0.90,
        1.10,
        size=NUMBER_OF_CUSTOMERS,
    )

    price_sensitivity = np.clip(
        price_sensitivity,
        0.0,
        1.0,
    )

    price_sensitivity = np.round(
        price_sensitivity,
        2,
    )

    # ---------------------------------------------------------
    # Build customer dimension
    # ---------------------------------------------------------

    dim_customer = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "customer_segment": customer_segment,
            "gender": gender,
            "age_group": age_group,
            "city": city,
            "customer_start_date": customer_start_dates,
            "customer_tenure_days": customer_tenure_days,
            "preferred_channel": preferred_channel,
            "purchase_frequency_factor": (purchase_frequency_factor),
            "average_basket_factor": (average_basket_factor),
            "price_sensitivity": price_sensitivity,
        }
    )

    return dim_customer


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

    transaction_dates = rng.choice(
        dim_date["date"].to_numpy(),
        size=TARGET_SALES_TRANSACTIONS,
    )

    product_weights = (
        dim_product["base_demand"]
        * dim_product["demand_class"].map(DEMAND_CLASS_FACTORS)
        * dim_product["demand_trajectory"].map(DEMAND_TRAJECTORY_FACTORS)
    )

    product_weights = product_weights / product_weights.sum()

    product_indices = rng.choice(
        dim_product.index,
        size=TARGET_SALES_TRANSACTIONS,
        p=product_weights.to_numpy(),
    )

    store_weights = (
        dim_store["store_demand_factor"] / dim_store["store_demand_factor"].sum()
    )

    store_indices = rng.choice(
        dim_store.index,
        size=TARGET_SALES_TRANSACTIONS,
        p=store_weights.to_numpy(),
    )
    customer_weights = (
        dim_customer["purchase_frequency_factor"]
        * dim_customer["average_basket_factor"]
    )

    customer_weights = customer_weights / customer_weights.sum()

    customer_indices = rng.choice(
        dim_customer.index,
        size=TARGET_SALES_TRANSACTIONS,
        p=customer_weights.to_numpy(),
    )

    product_data = dim_product.loc[product_indices].reset_index(drop=True)

    store_data = dim_store.loc[store_indices].reset_index(drop=True)

    customer_data = dim_customer.loc[customer_indices].reset_index(drop=True)

    sales = pd.DataFrame(
        {
            "transaction_id": [
                f"TXN{i:07d}"
                for i in range(
                    1,
                    TARGET_SALES_TRANSACTIONS + 1,
                )
            ],
            "transaction_date": transaction_dates,
            "product_id": product_data["product_id"],
            "store_id": store_data["store_id"],
            "customer_id": customer_data["customer_id"],
        }
    )

    # --------------------------------------------------
    # Product demand attributes
    # --------------------------------------------------

    sales["base_demand"] = product_data["base_demand"].to_numpy()

    sales["demand_class"] = product_data["demand_class"].to_numpy()

    sales["demand_class_factor"] = (
        product_data["demand_class"].map(DEMAND_CLASS_FACTORS).to_numpy()
    )

    sales["demand_trajectory"] = product_data["demand_trajectory"].to_numpy()

    sales["demand_trajectory_factor"] = (
        product_data["demand_trajectory"].map(DEMAND_TRAJECTORY_FACTORS).to_numpy()
    )

    sales["category"] = product_data["category"].to_numpy()

    sales["unit_cost"] = product_data["unit_cost"].to_numpy()

    sales["product_selling_price"] = product_data["selling_price"].to_numpy()

    # --------------------------------------------------
    # Store demand attributes
    # --------------------------------------------------

    sales["store_demand_factor"] = store_data["store_demand_factor"].to_numpy()

    # --------------------------------------------------
    # Customer demand attributes
    # --------------------------------------------------

    sales["customer_frequency_factor"] = customer_data[
        "purchase_frequency_factor"
    ].to_numpy()

    sales["customer_basket_factor"] = customer_data["average_basket_factor"].to_numpy()

    sales["price_sensitivity"] = customer_data["price_sensitivity"].to_numpy()

    # --------------------------------------------------
    # Calendar attributes
    # --------------------------------------------------

    transaction_dates = pd.to_datetime(sales["transaction_date"])

    sales["month"] = transaction_dates.dt.month

    sales["day_of_week"] = transaction_dates.dt.dayofweek

    sales["season"] = np.select(
        [
            sales["month"].isin([12, 1, 2]),
            sales["month"].isin([3, 4, 5]),
            sales["month"].isin([6, 7, 8]),
            sales["month"].isin([9, 10, 11]),
        ],
        [
            "Winter",
            "Spring",
            "Summer",
            "Autumn",
        ],
        default="Unknown",
    )

    sales["day_of_week_factor"] = (
        sales["day_of_week"].map(DAY_OF_WEEK_FACTORS).to_numpy()
    )

    # --------------------------------------------------
    # Ramadan / Eid indicators
    # Synthetic calendar assumptions
    # --------------------------------------------------

    transaction_year = transaction_dates.dt.year

    transaction_month = transaction_dates.dt.month

    transaction_day = transaction_dates.dt.day

    sales["is_ramadan"] = (
        (
            (transaction_year == 2023)
            & (transaction_month == 3)
            & (transaction_day >= 23)
        )
        | (
            (transaction_year == 2024)
            & (transaction_month == 3)
            & (transaction_day <= 31)
        )
        | ((transaction_year == 2025) & (transaction_month == 3))
    )

    sales["is_eid_period"] = (
        ((transaction_year == 2023) & (transaction_month == 4) & (transaction_day <= 5))
        | (
            (transaction_year == 2024)
            & (transaction_month == 4)
            & (transaction_day <= 12)
        )
        | (
            (transaction_year == 2025)
            & (transaction_month == 3)
            & (transaction_day >= 30)
        )
    )

    # Keep Ramadan and Eid mutually exclusive.
    sales["is_eid_period"] = sales["is_eid_period"] & ~sales["is_ramadan"]
    # --------------------------------------------------
    # Category seasonality
    # --------------------------------------------------

    seasonality_factor = np.ones(TARGET_SALES_TRANSACTIONS)

    for category in CATEGORY_SEASONALITY_FACTORS:
        category_mask = sales["category"] == category

        normal_mask = category_mask & ~sales["is_ramadan"] & ~sales["is_eid_period"]

        for season_name, config_name in [
            ("Winter", "winter"),
            ("Spring", "normal"),
            ("Summer", "summer"),
            ("Autumn", "normal"),
        ]:
            season_mask = normal_mask & (sales["season"] == season_name)

            seasonality_factor[season_mask] = CATEGORY_SEASONALITY_FACTORS[category][
                config_name
            ]

        ramadan_mask = category_mask & sales["is_ramadan"]

        seasonality_factor[ramadan_mask] = CATEGORY_SEASONALITY_FACTORS[category][
            "ramadan"
        ]

        eid_mask = category_mask & sales["is_eid_period"]

        seasonality_factor[eid_mask] = CATEGORY_SEASONALITY_FACTORS[category]["eid"]

    sales["seasonality_factor"] = np.round(
        seasonality_factor,
        2,
    )

    # --------------------------------------------------
    # Core demand intensity
    # --------------------------------------------------

    sales["demand_intensity"] = (
        sales["base_demand"]
        * sales["demand_class_factor"]
        * sales["demand_trajectory_factor"]
        * sales["store_demand_factor"]
        * sales["customer_frequency_factor"]
        * sales["customer_basket_factor"]
        * sales["day_of_week_factor"]
        * sales["seasonality_factor"]
    )

    # --------------------------------------------------
    # Random demand variation
    # --------------------------------------------------

    random_variation = rng.uniform(
        0.75,
        1.25,
        size=TARGET_SALES_TRANSACTIONS,
    )

    sales["demand_intensity"] *= random_variation

    # --------------------------------------------------
    # Demand spikes
    # --------------------------------------------------

    sales["demand_spike"] = (
        rng.random(TARGET_SALES_TRANSACTIONS) < DEMAND_SPIKE_PROBABILITY
    )

    sales.loc[
        sales["demand_spike"],
        "demand_intensity",
    ] *= DEMAND_SPIKE_FACTOR

    # --------------------------------------------------
    # Promotions
    # --------------------------------------------------

    sales["is_promotion"] = (
        rng.random(TARGET_SALES_TRANSACTIONS) < PROMOTION_PROBABILITY
    )

    sales["discount_pct"] = np.where(
        sales["is_promotion"],
        rng.uniform(
            PROMOTION_DISCOUNT_RANGE[0],
            PROMOTION_DISCOUNT_RANGE[1],
            size=TARGET_SALES_TRANSACTIONS,
        ),
        0.0,
    )

    sales["discount_pct"] = sales["discount_pct"].round(2)

    sales.loc[
        sales["is_promotion"],
        "demand_intensity",
    ] *= PROMOTION_DEMAND_LIFT

    sales["demand_intensity"] = sales["demand_intensity"].round(2)

    # --------------------------------------------------
    # Final transaction quantity
    # --------------------------------------------------

    # Convert demand intensity into realistic transaction quantity.
    quantity_lambda = sales["demand_intensity"] / sales["demand_intensity"].median() * 3

    quantity_lambda = quantity_lambda.clip(
        lower=0.5,
        upper=8.0,
    )

    sales["quantity"] = rng.poisson(quantity_lambda.to_numpy()) + 1

    sales["quantity"] = sales["quantity"].clip(
        lower=TRANSACTION_QUANTITY_RANGE[0],
        upper=TRANSACTION_QUANTITY_RANGE[1],
    )

    # --------------------------------------------------
    # Selling price
    # --------------------------------------------------

    price_variation = rng.uniform(
        0.98,
        1.02,
        size=TARGET_SALES_TRANSACTIONS,
    )

    sales["unit_price"] = (sales["product_selling_price"] * price_variation).round(2)

    # --------------------------------------------------
    # Gross sales
    # --------------------------------------------------

    sales["gross_sales"] = (sales["quantity"] * sales["unit_price"]).round(2)

    # --------------------------------------------------
    # Discount amount
    # --------------------------------------------------

    sales["discount_amount"] = (sales["gross_sales"] * sales["discount_pct"]).round(2)

    # --------------------------------------------------
    # Net sales
    # --------------------------------------------------

    sales["net_sales"] = (sales["gross_sales"] - sales["discount_amount"]).round(2)

    # --------------------------------------------------
    # COGS
    # --------------------------------------------------

    sales["cogs"] = (sales["quantity"] * sales["unit_cost"]).round(2)

    # --------------------------------------------------
    # Gross profit
    # --------------------------------------------------

    sales["gross_profit"] = (sales["net_sales"] - sales["cogs"]).round(2)

    return sales


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
    dim_date = generate_dim_date()
    dim_product = generate_dim_product()
    dim_store = generate_dim_store()
    dim_customer = generate_dim_customer()

    fact_sales = generate_fact_sales(
        dim_date,
        dim_product,
        dim_store,
        dim_customer,
    )

    print("=" * 60)
    print("fact_sales Initial Test")
    print("=" * 60)

    print(f"PASS: Row count = {len(fact_sales):,}")

    print(f"PASS: Unique transactions = {fact_sales['transaction_id'].nunique():,}")

    print("\nColumns:")
    print(fact_sales.columns.tolist())

    print("\nSample Transactions:")
    print("\n" + "=" * 60)
    print("Business Behavior Validation")
    print("=" * 60)

    print("\nSales by Demand Class:")
    print(
        fact_sales.groupby("demand_class")["quantity"]
        .sum()
        .sort_values(ascending=False)
    )

    print("\nSales by Demand Trajectory:")
    print(
        fact_sales.groupby("demand_trajectory")["quantity"]
        .sum()
        .sort_values(ascending=False)
    )

    print("\nSales by Promotion:")
    print(fact_sales.groupby("is_promotion")["quantity"].sum())

    print("\nAverage Demand Intensity by Demand Class:")
    print(
        fact_sales.groupby("demand_class")["demand_intensity"]
        .mean()
        .sort_values(ascending=False)
    )
    print("\nAverage Quantity by Promotion:")
    print(fact_sales.groupby("is_promotion")["quantity"].mean())
    print("\nFinancial Validation:")

assert (fact_sales["quantity"] > 0).all()

assert (fact_sales["unit_price"] > 0).all()

assert (fact_sales["gross_sales"] >= fact_sales["net_sales"]).all()

assert (fact_sales["discount_amount"] >= 0).all()

assert (fact_sales["net_sales"] > 0).all()

assert (fact_sales["cogs"] > 0).all()

assert np.allclose(
    fact_sales["gross_sales"],
    fact_sales["quantity"] * fact_sales["unit_price"],
    atol=0.01,
)

assert np.allclose(
    fact_sales["net_sales"],
    fact_sales["gross_sales"] - fact_sales["discount_amount"],
    atol=0.01,
)

assert np.allclose(
    fact_sales["cogs"],
    fact_sales["quantity"] * fact_sales["unit_cost"],
    atol=0.01,
)

assert np.allclose(
    fact_sales["gross_profit"],
    fact_sales["net_sales"] - fact_sales["cogs"],
    atol=0.01,
)

print("PASS: Quantity values are positive.")
print("PASS: Unit prices are positive.")
print("PASS: Gross Sales >= Net Sales.")
print("PASS: Discount amounts are non-negative.")
print("PASS: Net Sales are positive.")
print("PASS: COGS values are positive.")
print("PASS: Gross Sales calculation is correct.")
print("PASS: Net Sales calculation is correct.")
print("PASS: COGS calculation is correct.")
print("PASS: Gross Profit calculation is correct.")

print("\nKey Validation:")

assert fact_sales["transaction_id"].is_unique
assert fact_sales["product_id"].isin(dim_product["product_id"]).all()
assert fact_sales["store_id"].isin(dim_store["store_id"]).all()
assert fact_sales["customer_id"].isin(dim_customer["customer_id"]).all()

print("PASS: Transaction IDs are unique.")
print("PASS: All product IDs exist in dim_product.")
print("PASS: All store IDs exist in dim_store.")
print("PASS: All customer IDs exist in dim_customer.")


print("\n" + "=" * 60)
print("Seasonality Validation")
print("=" * 60)

print("\nAverage Quantity by Season:")
print(fact_sales.groupby("season")["quantity"].mean().sort_values(ascending=False))

print("\nAverage Quantity - Ramadan vs Normal:")
print(fact_sales.groupby("is_ramadan")["quantity"].mean())

print("\nAverage Quantity - Eid vs Normal:")
print(fact_sales.groupby("is_eid_period")["quantity"].mean())

print("\nTransactions by Season:")
print(fact_sales["season"].value_counts().sort_index())

print("\nRamadan/Eid Transaction Counts:")

print("Ramadan transactions:", fact_sales["is_ramadan"].sum())

print("Eid-period transactions:", fact_sales["is_eid_period"].sum())

print(
    "Both Ramadan and Eid:",
    (fact_sales["is_ramadan"] & fact_sales["is_eid_period"]).sum(),
)

print("\nRamadan/Eid Validation:")

print("Ramadan transactions:", fact_sales["is_ramadan"].sum())

print("Eid-period transactions:", fact_sales["is_eid_period"].sum())

print(
    "Both Ramadan and Eid:",
    (fact_sales["is_ramadan"] & fact_sales["is_eid_period"]).sum(),
)
