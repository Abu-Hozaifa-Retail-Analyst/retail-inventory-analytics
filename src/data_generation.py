# ============================================================
# GulfMart Retail Inventory Analytics
# Synthetic Dataset Generator
# ============================================================
# %%
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
# %%
# Add the imports

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
    REPLENISHMENT_INTERVAL_DAYS,
)


# ============================================================
# Random Number Generator
# ============================================================
# %%
rng = np.random.default_rng(RANDOM_SEED)

# ============================================================
# Dimension Table Generators
# ============================================================


# %%
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


# %%
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


# %%
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


# %%
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


# %%
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


# %%
def _run_sequential_inventory_simulation(
    group,
):
    """
    Simulate daily inventory for one product-store combination.

    The simulation is sequential because today's inventory depends
    on what happened yesterday.

    Main logic:
        Opening Stock
        → Receive Purchase Orders
        → Demand
        → Fulfilled Sales
        → Lost Sales
        → Closing Stock
        → Replenishment Decision
    """

    # ---------------------------------------------------------
    # STEP 1 — Sort the group by date
    # ---------------------------------------------------------
    # Inventory must be simulated in chronological order.
    # Example:
    #
    # 2023-01-01
    # 2023-01-02
    # 2023-01-03
    #
    # We cannot calculate today's closing stock before knowing
    # yesterday's closing stock.
    # ---------------------------------------------------------

    group = group.sort_values("date").copy()

    # ---------------------------------------------------------
    # STEP 2 — Create the basic state variables
    # ---------------------------------------------------------

    # These variables represent the inventory state as we move
    # through each day.

    opening_stock = 0
    on_order_inventory = 0

    # ---------------------------------------------------------
    # STEP 3 — Store simulation results
    # ---------------------------------------------------------

    results = []

    # ---------------------------------------------------------
    # STEP 4 — Process each day sequentially
    # ---------------------------------------------------------

    for _, row in group.iterrows():
        # -----------------------------------------------------
        # Today's demand
        # -----------------------------------------------------

        demand_units = row["sales_units"]

        # -----------------------------------------------------
        # Receive purchase orders due today
        # -----------------------------------------------------

        receipts_today = 0

        # We will add the actual purchase-order pipeline
        # in the next part of Step 10B.
        #
        # For now:
        # receipts_today = 0

        # -----------------------------------------------------
        # Available inventory before today's demand
        # -----------------------------------------------------

        available_stock = opening_stock + receipts_today

        # -----------------------------------------------------
        # Fulfill today's demand
        # -----------------------------------------------------

        fulfilled_sales_units = min(demand_units, available_stock)

        # -----------------------------------------------------
        # Lost sales
        # -----------------------------------------------------
        # If customers want 10 units but only 6 are available:
        #
        # Demand = 10
        # Fulfilled = 6
        # Lost sales = 4
        # -----------------------------------------------------

        lost_sales_units = demand_units - fulfilled_sales_units

        # -----------------------------------------------------
        # Closing inventory
        # -----------------------------------------------------

        closing_stock = available_stock - fulfilled_sales_units

        # -----------------------------------------------------
        # Inventory position
        # -----------------------------------------------------
        # Inventory Position =
        # Closing Stock + On-Order Inventory
        # -----------------------------------------------------

        inventory_position = closing_stock + on_order_inventory

        # -----------------------------------------------------
        # Save today's results
        # -----------------------------------------------------

        results.append(
            {
                "date": row["date"],
                "store_id": row["store_id"],
                "product_id": row["product_id"],
                "opening_stock": opening_stock,
                "demand_units": demand_units,
                "receipts_units": receipts_today,
                "fulfilled_sales_units": fulfilled_sales_units,
                "lost_sales_units": lost_sales_units,
                "closing_stock": closing_stock,
                "on_order_inventory": on_order_inventory,
                "inventory_position": inventory_position,
            }
        )

        # -----------------------------------------------------
        # Move today's closing stock into tomorrow
        # -----------------------------------------------------

        opening_stock = closing_stock

    # ---------------------------------------------------------
    # STEP 5 — Return the simulation result
    # ---------------------------------------------------------

    return pd.DataFrame(results)


# %%
def generate_fact_inventory(
    fact_sales,
    dim_product,
    dim_store,
    dim_supplier,
    dim_date,
):
    """
    Generate daily inventory records
    at the product-store level.
    """

    print("\nGenerating fact_inventory...")

    # ============================================================
    # Step 1: Aggregate daily sales
    # ============================================================

    daily_sales = (
        fact_sales.groupby(
            [
                "transaction_date",
                "store_id",
                "product_id",
            ],
            as_index=False,
        )["quantity"]
        .sum()
        .rename(columns={"quantity": "sales_units"})
    )

    print(f"Daily sales combinations: {len(daily_sales):,}")

    # ============================================================
    # Step 2: Create product-store combinations
    # ============================================================

    product_store = dim_product[
        [
            "product_id",
            "supplier_id",
            "demand_class",
            "base_demand",
        ]
    ].merge(
        dim_store[
            [
                "store_id",
                "store_demand_factor",
            ]
        ],
        how="cross",
    )

    print(f"Product-store combinations: {len(product_store):,}")

    # ============================================================
    # Step 5: Add supplier information
    # ============================================================

    product_store = product_store.merge(
        dim_supplier[
            [
                "supplier_id",
                "lead_time_days",
                "minimum_order_qty",
                "supplier_status",
            ]
        ],
        on="supplier_id",
        how="left",
        validate="many_to_one",
    )

    print(
        f"Missing supplier lead times: {product_store['lead_time_days'].isna().sum():,}"
    )

    print(
        f"Missing minimum order quantities: "
        f"{product_store['minimum_order_qty'].isna().sum():,}"
    )

    # ============================================================
    # Step 6: Calculate initial inventory assumptions
    # ============================================================

    product_store["initial_inventory_days"] = product_store["demand_class"].map(
        INITIAL_INVENTORY_DAYS
    )

    product_store["expected_daily_demand"] = (
        product_store["base_demand"] * product_store["store_demand_factor"]
    )

    product_store["initial_opening_stock"] = (
        (
            product_store["expected_daily_demand"]
            * product_store["initial_inventory_days"]
        )
        .round()
        .astype(int)
    )

    product_store["initial_opening_stock"] = product_store[
        "initial_opening_stock"
    ].clip(lower=1)

    print("\nInitial opening stock summary:")

    print(product_store["initial_opening_stock"].describe())

    # ============================================================
    # Step 7: Create daily product-store calendar
    # ============================================================

    daily_calendar = (
        product_store.assign(key=1)
        .merge(
            dim_date[["date"]].assign(key=1),
            on="key",
        )
        .drop(columns="key")
    )

    print(f"\nDaily inventory calendar rows: {len(daily_calendar):,}")

    # ============================================================
    # Step 8: Merge daily sales into inventory calendar
    # ============================================================

    daily_calendar = daily_calendar.merge(
        daily_sales,
        how="left",
        left_on=[
            "date",
            "store_id",
            "product_id",
        ],
        right_on=[
            "transaction_date",
            "store_id",
            "product_id",
        ],
    )

    daily_calendar["sales_units"] = daily_calendar["sales_units"].fillna(0).astype(int)

    daily_calendar = daily_calendar.drop(columns=["transaction_date"])

    print(f"\nRows after sales merge: {len(daily_calendar):,}")

    print(f"Days with sales: {(daily_calendar['sales_units'] > 0).sum():,}")

    print(f"Days without sales: {(daily_calendar['sales_units'] == 0).sum():,}")

    # ============================================================
    # Step 9: Calculate historical demand metrics
    # ============================================================

    # Total calendar days in the project horizon.
    number_of_days = len(dim_date)

    actual_demand = fact_sales.groupby(
        [
            "store_id",
            "product_id",
        ],
        as_index=False,
    ).agg(
        total_sales_units=(
            "quantity",
            "sum",
        ),
        sales_days=(
            "transaction_date",
            "nunique",
        ),
    )

    # Calendar-day average demand
    actual_demand["actual_avg_daily_demand"] = (
        actual_demand["total_sales_units"] / number_of_days
    )

    # Demand velocity on active selling days
    actual_demand["active_day_demand_rate"] = (
        actual_demand["total_sales_units"] / actual_demand["sales_days"]
    )

    print("\nHistorical demand summary:")

    print(
        actual_demand[
            [
                "total_sales_units",
                "sales_days",
                "actual_avg_daily_demand",
                "active_day_demand_rate",
            ]
        ].describe()
    )

    daily_calendar = daily_calendar.merge(
        actual_demand[
            [
                "store_id",
                "product_id",
                "total_sales_units",
                "sales_days",
                "actual_avg_daily_demand",
                "active_day_demand_rate",
            ]
        ],
        on=[
            "store_id",
            "product_id",
        ],
        how="left",
        validate="many_to_one",
    )

    daily_calendar["actual_avg_daily_demand"] = daily_calendar[
        "actual_avg_daily_demand"
    ].fillna(0)

    daily_calendar["active_day_demand_rate"] = daily_calendar[
        "active_day_demand_rate"
    ].fillna(0)

    # ============================================================
    # Step 9C: Create calibrated demand rate
    # ============================================================

    daily_calendar["demand_rate"] = daily_calendar["active_day_demand_rate"]

    print("\nCalibrated demand summary:")

    print(daily_calendar["demand_rate"].describe())

    # ============================================================
    # Step 10A: Recalibrate initial inventory
    # ============================================================
    #
    # Initial inventory is now based on actual historical
    # average daily demand rather than theoretical demand.
    #
    # Formula:
    #
    # Initial Stock =
    # Actual Daily Demand × Initial Inventory Days
    #
    # This prevents excessive starting inventory caused by
    # theoretical demand assumptions.
    # ============================================================

    daily_calendar["initial_inventory_days"] = daily_calendar["demand_class"].map(
        INITIAL_INVENTORY_DAYS
    )

    daily_calendar["initial_opening_stock"] = (
        (daily_calendar["demand_rate"] * daily_calendar["initial_inventory_days"])
        .round()
        .astype(int)
    )

    # Minimum stock floor
    daily_calendar["initial_opening_stock"] = daily_calendar[
        "initial_opening_stock"
    ].clip(lower=1)

    print("\nRecalibrated initial inventory summary:")

    print(daily_calendar["initial_opening_stock"].describe())

    # ============================================================
    # Step 10B: Calculate safety stock
    # ============================================================

    daily_calendar["safety_stock_days"] = daily_calendar["demand_class"].map(
        SAFETY_STOCK_DAYS
    )

    daily_calendar["safety_stock_units"] = (
        daily_calendar["demand_rate"] * daily_calendar["safety_stock_days"]
    )

    daily_calendar["safety_stock_units"] = daily_calendar["safety_stock_units"].clip(
        lower=0
    )

    print("\nSafety stock summary:")

    print(daily_calendar["safety_stock_units"].describe())

    # ============================================================
    # Step 10C: Replenishment review period
    # ============================================================

    daily_calendar["replenishment_interval_days"] = daily_calendar["demand_class"].map(
        REPLENISHMENT_INTERVAL_DAYS
    )

    # ============================================================
    # Step 10D: Calculate lead-time demand
    # ============================================================
    #
    # Lead-time demand estimates how many units are expected
    # to be sold while waiting for a replenishment order.
    #
    # Formula:
    #
    # Lead-Time Demand =
    # Demand Rate × Supplier Lead Time
    #
    # ============================================================

    daily_calendar["lead_time_demand"] = (
        daily_calendar["demand_rate"] * daily_calendar["lead_time_days"]
    )

    daily_calendar["lead_time_demand"] = daily_calendar["lead_time_demand"].clip(
        lower=0
    )

    print("\nLead-time demand summary:")
    print(daily_calendar["lead_time_demand"].describe())

    # ============================================================
    # Step 10E: Calculate reorder point
    # ============================================================
    #
    # Reorder Point (ROP) tells us when inventory should trigger
    # a replenishment decision.
    #
    # Formula:
    #
    # ROP =
    # Lead-Time Demand + Safety Stock
    #
    # ============================================================

    daily_calendar["reorder_point"] = (
        daily_calendar["lead_time_demand"] + daily_calendar["safety_stock_units"]
    )

    daily_calendar["reorder_point"] = daily_calendar["reorder_point"].clip(lower=0)

    print("\nReorder point summary:")
    print(daily_calendar["reorder_point"].describe())

    # ============================================================
    # Step 10F: Calculate review-period demand
    # ============================================================
    #
    # Review-period demand estimates expected demand between
    # inventory review opportunities.
    #
    # ============================================================

    daily_calendar["review_period_demand"] = (
        daily_calendar["demand_rate"] * daily_calendar["replenishment_interval_days"]
    )

    daily_calendar["review_period_demand"] = daily_calendar[
        "review_period_demand"
    ].clip(lower=0)

    print("\nReview-period demand summary:")
    print(daily_calendar["review_period_demand"].describe())

    # ============================================================
    # Step 10G: Calculate target stock level
    # ============================================================
    #
    # Target Stock represents the desired inventory position
    # after replenishment.
    #
    # Formula:
    #
    # Target Stock =
    # Lead-Time Demand
    # + Review-Period Demand
    # + Safety Stock
    #
    # ============================================================

    daily_calendar["target_stock_level"] = (
        daily_calendar["lead_time_demand"]
        + daily_calendar["review_period_demand"]
        + daily_calendar["safety_stock_units"]
    )

    daily_calendar["target_stock_level"] = daily_calendar["target_stock_level"].clip(
        lower=0
    )

    print("\nTarget stock level summary:")
    print(daily_calendar["target_stock_level"].describe())

    # ============================================================
    # Step 10F: Identify replenishment review dates
    # ============================================================

    daily_calendar["days_since_start"] = (
        daily_calendar["date"] - daily_calendar["date"].min()
    ).dt.days

    daily_calendar["is_replenishment_review"] = (
        daily_calendar["days_since_start"]
        % daily_calendar["replenishment_interval_days"]
        == 0
    )

    print("\nReplenishment review events:")
    print(daily_calendar["is_replenishment_review"].sum())

    # ============================================================
    # Step 10G: Planned replenishment quantity
    # ============================================================

    daily_calendar["planned_order_quantity"] = daily_calendar["target_stock_level"]

    # Orders only occur on review dates
    daily_calendar["planned_order_quantity"] = daily_calendar[
        "planned_order_quantity"
    ].where(
        daily_calendar["is_replenishment_review"],
        0,
    )

    # Respect supplier MOQ
    daily_calendar["planned_order_quantity"] = np.where(
        daily_calendar["planned_order_quantity"] > 0,
        np.maximum(
            daily_calendar["planned_order_quantity"],
            daily_calendar["minimum_order_qty"],
        ),
        0,
    )

    daily_calendar["planned_order_quantity"] = daily_calendar[
        "planned_order_quantity"
    ].astype(int)

    print("\nPlanned order quantity summary:")
    print(
        daily_calendar.loc[
            daily_calendar["planned_order_quantity"] > 0,
            "planned_order_quantity",
        ].describe()
    )

    # ============================================================
    # Step 10H: Calculate expected receipt date
    # ============================================================

    daily_calendar["expected_receipt_date"] = daily_calendar["date"] + pd.to_timedelta(
        daily_calendar["lead_time_days"],
        unit="D",
    )

    print("\nExpected receipt dates calculated.")

    # ============================================================
    # Step 10I: Create replenishment orders
    # ============================================================

    replenishment_orders = daily_calendar.loc[
        daily_calendar["planned_order_quantity"] > 0,
        [
            "date",
            "store_id",
            "product_id",
            "supplier_id",
            "planned_order_quantity",
            "lead_time_days",
            "expected_receipt_date",
        ],
    ].copy()

    replenishment_orders = replenishment_orders.rename(
        columns={
            "date": "order_date",
            "planned_order_quantity": "order_quantity",
        }
    )

    print(f"\nReplenishment orders created: {len(replenishment_orders):,}")
    print("\nReplenishment order preview:")
    print(replenishment_orders.head())

    # ============================================================
    # Step 10J: Convert replenishment orders into receipts
    # ============================================================

    replenishment_receipts = (
        replenishment_orders.groupby(
            [
                "expected_receipt_date",
                "store_id",
                "product_id",
            ],
            as_index=False,
        )["order_quantity"]
        .sum()
        .rename(
            columns={
                "expected_receipt_date": "date",
                "order_quantity": "receipts",
            }
        )
    )

    print(f"\nReceipt events created: {len(replenishment_receipts):,}")

    # ============================================================
    # Step 10K: Merge receipts into inventory calendar
    # ============================================================

    daily_calendar = daily_calendar.merge(
        replenishment_receipts,
        on=[
            "date",
            "store_id",
            "product_id",
        ],
        how="left",
    )

    daily_calendar["receipts"] = daily_calendar["receipts"].fillna(0).astype(int)

    print("\nReceipt summary:")
    print(daily_calendar["receipts"].describe())

    # ============================================================
    # Step 11A: Initialize inventory event fields
    # ============================================================

    daily_calendar["transfers_in"] = 0
    daily_calendar["transfers_out"] = 0
    daily_calendar["returns_units"] = 0
    daily_calendar["damaged_units"] = 0
    daily_calendar["inventory_adjustments"] = 0

    # ============================================================
    # Step 11B: Sort inventory records chronologically
    # ============================================================

    daily_calendar = daily_calendar.sort_values(
        [
            "store_id",
            "product_id",
            "date",
        ]
    ).reset_index(drop=True)

    # ============================================================
    # Step 11C: Calculate daily inventory movement
    # ============================================================

    daily_calendar["net_inventory_change"] = (
        daily_calendar["receipts"]
        + daily_calendar["transfers_in"]
        - daily_calendar["transfers_out"]
        - daily_calendar["sales_units"]
        + daily_calendar["returns_units"]
        - daily_calendar["damaged_units"]
        + daily_calendar["inventory_adjustments"]
    )

    # ============================================================
    # Step 11D: Calculate closing inventory
    # ============================================================

    daily_calendar["closing_stock"] = (
        daily_calendar["initial_opening_stock"]
        + daily_calendar.groupby(
            [
                "store_id",
                "product_id",
            ]
        )["net_inventory_change"].cumsum()
    )

    daily_calendar["closing_stock"] = (
        daily_calendar["closing_stock"].round().astype(int)
    )

    # ============================================================
    # Step 11E: Calculate opening inventory
    # ============================================================

    previous_closing_stock = daily_calendar.groupby(
        [
            "store_id",
            "product_id",
        ]
    )["closing_stock"].shift(1)

    daily_calendar["opening_stock"] = previous_closing_stock.fillna(
        daily_calendar["initial_opening_stock"]
    )

    daily_calendar["opening_stock"] = (
        daily_calendar["opening_stock"].round().astype(int)
    )

    # ============================================================
    # Step 11F-1: Inventory continuity validation
    # ============================================================

    previous_closing_stock = daily_calendar.groupby(
        [
            "store_id",
            "product_id",
        ]
    )["closing_stock"].shift(1)

    has_previous_day = previous_closing_stock.notna()

    continuity_check = daily_calendar["opening_stock"].eq(previous_closing_stock)

    continuity_failures = (continuity_check[has_previous_day] == False).sum()

    print("\nInventory continuity validation:")
    print(f"Rows checked: {has_previous_day.sum():,}")
    print(f"Continuity failures: {continuity_failures:,}")

    # ============================================================
    # Step 11F-2: Inventory reconciliation validation
    # ============================================================

    calculated_closing = (
        daily_calendar["opening_stock"] + daily_calendar["net_inventory_change"]
    )

    reconciliation_failures = (
        daily_calendar["closing_stock"].ne(calculated_closing)
    ).sum()

    print("\nInventory reconciliation validation:")
    print(f"Reconciliation failures: {reconciliation_failures:,}")

    # ============================================================
    # Step 11F-3: Negative inventory validation
    # ============================================================

    negative_inventory_rows = (daily_calendar["closing_stock"] < 0).sum()

    negative_inventory_rate = negative_inventory_rows / len(daily_calendar)

    print("\nNegative inventory validation:")
    print(f"Negative inventory rows: {negative_inventory_rows:,}")
    print(f"Negative inventory rate: {negative_inventory_rate:.2%}")

    # ============================================================
    # Step 12A: Stockout events
    # ============================================================

    daily_calendar["stockout_event"] = daily_calendar["closing_stock"] <= 0

    # ============================================================
    # Step 12B: Low-stock events
    # ============================================================

    daily_calendar["low_stock_event"] = (
        daily_calendar["closing_stock"] <= daily_calendar["reorder_point"]
    )

    # ============================================================
    # Step 12C: Receipt events
    # ============================================================

    daily_calendar["receipt_event"] = daily_calendar["receipts"] > 0

    # ============================================================
    # Step 12D: Sales events
    # ============================================================

    daily_calendar["sales_event"] = daily_calendar["sales_units"] > 0

    # ============================================================
    # Step 12E: Replenishment order events
    # ============================================================

    daily_calendar["replenishment_order_event"] = (
        daily_calendar["planned_order_quantity"] > 0
    )

    # ============================================================
    # Step 12F: Inventory coverage days
    # ============================================================

    daily_calendar["inventory_coverage_days"] = np.where(
        daily_calendar["demand_rate"] > 0,
        daily_calendar["closing_stock"] / daily_calendar["demand_rate"],
        np.nan,
    )

    # ============================================================
    # Step 12G: Inventory status
    # ============================================================

    daily_calendar["inventory_status"] = np.select(
        [
            daily_calendar["closing_stock"] <= 0,
            daily_calendar["closing_stock"] <= daily_calendar["reorder_point"],
        ],
        [
            "Stockout",
            "Low Stock",
        ],
        default="Healthy",
    )

    # ============================================================
    # Step 12H: Final inventory preview
    # ============================================================

    print("\nInventory status distribution:")
    print(daily_calendar["inventory_status"].value_counts())

    print("\nInventory event summary:")
    print(
        {
            "Replenishment Orders": int(
                daily_calendar["replenishment_order_event"].sum()
            ),
            "Receipt Events": int(daily_calendar["receipt_event"].sum()),
            "Sales Events": int(daily_calendar["sales_event"].sum()),
            "Low Stock Events": int(daily_calendar["low_stock_event"].sum()),
            "Stockout Events": int(daily_calendar["stockout_event"].sum()),
        }
    )

    print("\nInventory coverage summary:")
    print(daily_calendar["inventory_coverage_days"].describe())

    return daily_calendar


# ============================================================
# Fact Table Generators
# ============================================================


# %%


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


# ============================================================
# Data Quality
# ============================================================


# %%
def inject_data_quality_issues(
    dim_product,
    dim_store,
    dim_customer,
    dim_supplier,
    fact_sales,
    fact_inventory,
):
    """Inject a small number of controlled data-quality issues."""

    print("\nInjecting controlled data-quality issues...")

    # Work on copies so we never mutate the "clean" dataframes
    # that were already generated upstream.
    dim_product = dim_product.copy()
    dim_store = dim_store.copy()
    dim_customer = dim_customer.copy()
    dim_supplier = dim_supplier.copy()
    fact_sales = fact_sales.copy()
    fact_inventory = fact_inventory.copy()

    # ------------------------------------------------------
    # Issue 1: Missing brand values (dim_product)
    # ------------------------------------------------------
    issue_mask = rng.random(len(dim_product)) < DATA_QUALITY_ISSUE_PROBABILITY
    dim_product.loc[issue_mask, "brand"] = np.nan
    print(f"dim_product: {issue_mask.sum()} missing 'brand' values injected")

    # ------------------------------------------------------
    # Issue 2: Missing city values (dim_customer)
    # ------------------------------------------------------
    issue_mask = rng.random(len(dim_customer)) < DATA_QUALITY_ISSUE_PROBABILITY
    dim_customer.loc[issue_mask, "city"] = np.nan
    print(f"dim_customer: {issue_mask.sum()} missing 'city' values injected")

    # ------------------------------------------------------
    # Issue 3: Inconsistent text formatting (dim_store.city)
    # e.g. "Riyadh" -> "RIYADH  " (wrong case + trailing spaces)
    # Slightly higher rate so it's actually visible in a
    # 20-row table.
    # ------------------------------------------------------
    issue_mask = rng.random(len(dim_store)) < (DATA_QUALITY_ISSUE_PROBABILITY * 20)
    dim_store.loc[issue_mask, "city"] = (
        dim_store.loc[issue_mask, "city"].str.upper() + "  "
    )
    print(f"dim_store: {issue_mask.sum()} inconsistent 'city' text values injected")

    # ------------------------------------------------------
    # Issue 4: Missing supplier_name (dim_supplier)
    # ------------------------------------------------------
    issue_mask = rng.random(len(dim_supplier)) < DATA_QUALITY_ISSUE_PROBABILITY
    dim_supplier.loc[issue_mask, "supplier_name"] = np.nan
    print(f"dim_supplier: {issue_mask.sum()} missing 'supplier_name' values injected")

    # ------------------------------------------------------
    # Issue 5: Duplicate transactions (fact_sales)
    # Simulates a POS system sending the same sale twice.
    # ------------------------------------------------------
    n_duplicates = max(1, int(len(fact_sales) * DATA_QUALITY_ISSUE_PROBABILITY))
    duplicate_rows = fact_sales.sample(n=n_duplicates, random_state=RANDOM_SEED)
    fact_sales = pd.concat([fact_sales, duplicate_rows], ignore_index=True)
    print(f"fact_sales: {n_duplicates} duplicate transactions injected")

    print("Data-quality injection completed.")

    return (
        dim_product,
        dim_store,
        dim_customer,
        dim_supplier,
        fact_sales,
        fact_inventory,
    )


# %%
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


# %%
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


# %%
def generate_all_data():
    """Run the complete synthetic dataset generation pipeline."""

    print("=" * 60)
    print("GulfMart Retail Inventory Analytics — Data Generation")
    print("=" * 60)

    # --------------------------------------------------------
    # Step 1: Dimensions
    # --------------------------------------------------------
    dim_date = generate_dim_date()
    dim_supplier = generate_dim_supplier()
    dim_product = generate_dim_product()
    dim_store = generate_dim_store()
    dim_customer = generate_dim_customer()

    # --------------------------------------------------------
    # Step 2: Facts
    # --------------------------------------------------------
    fact_sales = generate_fact_sales(
        dim_date,
        dim_product,
        dim_store,
        dim_customer,
    )

    fact_inventory = generate_fact_inventory(
        fact_sales,
        dim_product,
        dim_store,
        dim_supplier,
        dim_date,
    )

    # --------------------------------------------------------
    # Step 3: Data quality injection (controlled, optional)
    # --------------------------------------------------------
    if INJECT_DATA_QUALITY_ISSUES:
        (
            dim_product,
            dim_store,
            dim_customer,
            dim_supplier,
            fact_sales,
            fact_inventory,
        ) = inject_data_quality_issues(
            dim_product,
            dim_store,
            dim_customer,
            dim_supplier,
            fact_sales,
            fact_inventory,
        )

    # --------------------------------------------------------
    # Step 4: Validation
    # --------------------------------------------------------
    validate_generated_dataset(
        dim_date,
        dim_product,
        dim_store,
        dim_customer,
        dim_supplier,
        fact_sales,
        fact_inventory,
    )

    # --------------------------------------------------------
    # Step 5: Save
    # --------------------------------------------------------
    save_datasets(
        dim_date,
        dim_product,
        dim_store,
        dim_customer,
        dim_supplier,
        fact_sales,
        fact_inventory,
    )

    print("\nData generation pipeline completed successfully.")

    return {
        "dim_date": dim_date,
        "dim_product": dim_product,
        "dim_store": dim_store,
        "dim_customer": dim_customer,
        "dim_supplier": dim_supplier,
        "fact_sales": fact_sales,
        "fact_inventory": fact_inventory,
    }


# %%
if __name__ == "__main__":
    generated_data = generate_all_data()
# %%
