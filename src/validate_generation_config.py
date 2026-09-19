# ============================================================
# GulfMart Retail Inventory Analytics
# Dataset Generation Configuration Validation
# ============================================================
#
# Purpose:
# Validate all synthetic-data generation assumptions before
# the dataset is generated.
#
# Important:
# This file validates CONFIGURATION only.
#
# It does NOT validate generated datasets.
# Generated-data validation belongs in:
#     src/data_validation.py
# ============================================================


from datetime import datetime

from data_generation_config import (
    RANDOM_SEED,
    START_DATE,
    END_DATE,
    NUMBER_OF_STORES,
    NUMBER_OF_PRODUCTS,
    NUMBER_OF_CUSTOMERS,
    NUMBER_OF_SUPPLIERS,
    TARGET_SALES_TRANSACTIONS,
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
    REPLENISHMENT_INTERVAL_DAYS,
    LOW_SAFETY_STOCK_PROBABILITY,
    LONG_LEAD_TIME_RISK_PROBABILITY,
    DEMAND_SPIKE_PROBABILITY,
    DEMAND_SPIKE_FACTOR,
    INJECT_DATA_QUALITY_ISSUES,
    DATA_QUALITY_ISSUE_PROBABILITY,
)

# ============================================================
# Random Seed Validation
# ============================================================


def validate_random_seed():
    """
    Validate that the random seed is a valid integer.

    The random seed ensures that synthetic data generation
    is reproducible.
    """

    print("\n--- Random Seed Validation ---")

    assert isinstance(RANDOM_SEED, int), "RANDOM_SEED must be an integer."

    print(f"PASS: Random seed is valid ({RANDOM_SEED}).")


# Add helper functions
def check_probability_distribution(name, distribution):
    """Check that probabilities are between 0 and 1 and sum to 1."""

    total = sum(distribution.values())

    assert all(0 <= probability <= 1 for probability in distribution.values()), (
        f"{name} contains invalid probabilities."
    )

    assert abs(total - 1.0) < 1e-9, f"{name} must sum to 1. Current total: {total}"

    print(f"PASS: {name} sums to 100%")

    # Validate probability distributions


def validate_probabilities():
    print("\n--- Probability Validation ---")

    check_probability_distribution(
        "Demand class probabilities",
        DEMAND_CLASS_PROBABILITIES,
    )

    check_probability_distribution(
        "Demand trajectory probabilities",
        DEMAND_TRAJECTORY_PROBABILITIES,
    )

    check_probability_distribution(
        "Store type probabilities",
        STORE_TYPE_PROBABILITIES,
    )

    check_probability_distribution(
        "Supplier region probabilities",
        SUPPLIER_REGION_PROBABILITIES,
    )

    check_probability_distribution(
        "Supplier status probabilities",
        SUPPLIER_STATUS_PROBABILITIES,
    )

    check_probability_distribution(
        "Customer segment probabilities",
        CUSTOMER_SEGMENT_PROBABILITIES,
    )

    check_probability_distribution(
        "Customer gender probabilities",
        CUSTOMER_GENDER_PROBABILITIES,
    )

    # Validate dataset sizes


def validate_dataset_sizes():
    print("\n--- Dataset Size Validation ---")

    assert NUMBER_OF_STORES > 0
    assert NUMBER_OF_PRODUCTS > 0
    assert NUMBER_OF_CUSTOMERS > 0
    assert NUMBER_OF_SUPPLIERS > 0
    assert TARGET_SALES_TRANSACTIONS > 0

    print("PASS: Dataset sizes are positive.")

    # Validate the date range


from datetime import datetime


def validate_dates():
    """
    Validate that START_DATE and END_DATE are valid dates
    and that START_DATE occurs before END_DATE.
    """

    print("\n--- Date Validation ---")

    start_date = datetime.strptime(
        START_DATE,
        "%Y-%m-%d",
    )

    end_date = datetime.strptime(
        END_DATE,
        "%Y-%m-%d",
    )

    assert start_date < end_date, "START_DATE must be earlier than END_DATE."

    print(f"PASS: Date range is {START_DATE} to {END_DATE}")

    # Validate product configuration


def validate_products():
    """
    Validate product categories, demand-class configuration,
    product cost range, and product margin range.
    """

    print("\n--- Product Configuration Validation ---")

    # --------------------------------------------------------
    # Product categories
    # --------------------------------------------------------

    assert len(PRODUCT_CATEGORIES) > 0, "PRODUCT_CATEGORIES cannot be empty."

    for category, subcategories in PRODUCT_CATEGORIES.items():
        assert category.strip() != "", "Product category names cannot be empty."

        assert len(subcategories) > 0, (
            f"{category} must contain at least one subcategory."
        )

        for subcategory in subcategories:
            assert subcategory.strip() != "", (
                f"{category} contains an empty subcategory."
            )

    # --------------------------------------------------------
    # Demand class configuration
    # --------------------------------------------------------

    assert set(DEMAND_CLASS_PROBABILITIES) == set(DEMAND_CLASS_FACTORS), (
        "Demand class probabilities and factors must contain the same demand classes."
    )

    for demand_class, factor in DEMAND_CLASS_FACTORS.items():
        assert factor > 0, f"Demand factor for {demand_class} must be positive."

    # --------------------------------------------------------
    # Product cost and margin ranges
    # --------------------------------------------------------

    min_cost, max_cost = PRODUCT_COST_RANGE

    min_margin, max_margin = PRODUCT_MARGIN_RANGE

    assert min_cost > 0, "Minimum product cost must be greater than 0."

    assert max_cost >= min_cost, "Maximum product cost must be >= minimum cost."

    assert 0 < min_margin < max_margin < 1, (
        "Product margin range must be between 0 and 1 with minimum < maximum."
    )

    print("PASS: Product configuration is internally consistent.")


# Validate demand trajectory configuration
def validate_demand_trajectories():
    """
    Validate that demand trajectory probabilities and demand
    factors use the same trajectory categories and that all
    factors are positive.
    """

    print("\n--- Demand Trajectory Validation ---")

    assert set(DEMAND_TRAJECTORY_PROBABILITIES) == set(DEMAND_TRAJECTORY_FACTORS), (
        "Demand trajectory probabilities and factors "
        "must contain the same trajectories."
    )

    for trajectory, factor in DEMAND_TRAJECTORY_FACTORS.items():
        assert factor > 0, f"Demand factor for {trajectory} must be positive."

    print("PASS: Demand trajectory configuration is valid.")


# Validate store configuration
def validate_stores():
    """
    Validate store-type probabilities, store demand factors,
    region definitions, and regional demand factors.
    """

    print("\n--- Store Configuration Validation ---")

    assert set(STORE_TYPE_PROBABILITIES) == set(STORE_TYPE_DEMAND_FACTORS), (
        "Store type probabilities and demand factors must contain the same store types."
    )

    assert set(REGION_CITIES) == set(REGION_DEMAND_FACTORS), (
        "REGION_CITIES and REGION_DEMAND_FACTORS must contain the same regions."
    )

    for region, cities in REGION_CITIES.items():
        assert len(cities) > 0, f"{region} must contain at least one city."

        for city in cities:
            assert city.strip() != "", f"{region} contains an empty city name."

    for factor in STORE_TYPE_DEMAND_FACTORS.values():
        assert factor > 0, "Store demand factors must be positive."

    for factor in REGION_DEMAND_FACTORS.values():
        assert factor > 0, "Region demand factors must be positive."

    print("PASS: Store configuration is valid.")


# Validate supplier configuration
def validate_suppliers():
    """
    Validate supplier regions and lead-time assumptions.

    Lead times must be positive and the maximum lead time
    cannot be smaller than the minimum.
    """

    print("\n--- Supplier Configuration Validation ---")

    assert set(SUPPLIER_REGION_PROBABILITIES) == set(SUPPLIER_LEAD_TIME_RANGES), (
        "Supplier region probabilities and lead-time ranges "
        "must contain the same regions."
    )

    for supplier_region, lead_time_range in SUPPLIER_LEAD_TIME_RANGES.items():
        minimum, maximum = lead_time_range

        assert minimum > 0, (
            f"{supplier_region} minimum lead time must be greater than 0."
        )

        assert maximum >= minimum, (
            f"{supplier_region} maximum lead time must be >= minimum lead time."
        )

    print("PASS: Supplier configuration is valid.")


# Validate seasonality configuration
def validate_seasonality():
    """
    Validate that every product category has a complete
    set of positive seasonal demand factors.
    """
    print("\n--- Seasonality Validation ---")

    assert set(PRODUCT_CATEGORIES) == set(CATEGORY_SEASONALITY_FACTORS)

    expected_seasons = {
        "normal",
        "ramadan",
        "eid",
        "summer",
        "winter",
    }

    for category, factors in CATEGORY_SEASONALITY_FACTORS.items():
        assert set(factors) == expected_seasons

        for season, factor in factors.items():
            assert factor > 0, f"{category} has invalid factor for {season}."

    print("PASS: Category seasonality configuration is valid.")


# Validate promotions
def validate_promotions():
    """
    Validate promotion probability, discount range,
    and demand-lift assumptions.
    """

    print("\n--- Promotion Validation ---")

    assert 0 <= PROMOTION_PROBABILITY <= 1, (
        "PROMOTION_PROBABILITY must be between 0 and 1."
    )

    minimum_discount, maximum_discount = PROMOTION_DISCOUNT_RANGE

    assert 0 <= minimum_discount < maximum_discount <= 1, (
        "PROMOTION_DISCOUNT_RANGE must be between 0 and 1 with minimum < maximum."
    )

    assert PROMOTION_DEMAND_LIFT > 0, "PROMOTION_DEMAND_LIFT must be greater than 0."

    print("PASS: Promotion configuration is valid.")


# Validate inventory configuration
def validate_inventory():
    """
    Validate inventory planning assumptions.

    Inventory assumptions are defined by demand class and
    will later be used by the replenishment and inventory
    simulation logic in data_generation.py.
    """

    print("\n--- Inventory Configuration Validation ---")

    # --------------------------------------------------------
    # Demand-class alignment
    # --------------------------------------------------------

    demand_classes = set(DEMAND_CLASS_PROBABILITIES)

    assert set(SAFETY_STOCK_DAYS) == demand_classes, (
        "SAFETY_STOCK_DAYS must contain all demand classes."
    )

    assert set(INITIAL_INVENTORY_DAYS) == demand_classes, (
        "INITIAL_INVENTORY_DAYS must contain all demand classes."
    )

    assert set(REPLENISHMENT_INTERVAL_DAYS) == demand_classes, (
        "REPLENISHMENT_INTERVAL_DAYS must contain all demand classes."
    )

    # --------------------------------------------------------
    # Validate inventory days
    # --------------------------------------------------------

    for demand_class in demand_classes:
        assert SAFETY_STOCK_DAYS[demand_class] > 0, (
            f"Safety stock days for {demand_class} must be greater than 0."
        )

        assert INITIAL_INVENTORY_DAYS[demand_class] > SAFETY_STOCK_DAYS[demand_class], (
            f"Initial inventory days for {demand_class} "
            f"must be greater than safety stock days."
        )

        assert REPLENISHMENT_INTERVAL_DAYS[demand_class] > 0, (
            f"Replenishment interval for {demand_class} must be greater than 0."
        )

    # --------------------------------------------------------
    # Minimum coverage
    # --------------------------------------------------------

    assert MINIMUM_COVERAGE_DAYS > 0, "MINIMUM_COVERAGE_DAYS must be greater than 0."

    print("PASS: Inventory configuration is valid.")


# Validate risk configuration
def validate_risk_parameters():
    """
    Validate probabilities and scaling factors used to
    introduce realistic inventory and demand risk.
    """

    print("\n--- Risk Parameter Validation ---")

    probability_parameters = {
        "LOW_SAFETY_STOCK_PROBABILITY": LOW_SAFETY_STOCK_PROBABILITY,
        "LONG_LEAD_TIME_RISK_PROBABILITY": LONG_LEAD_TIME_RISK_PROBABILITY,
        "DEMAND_SPIKE_PROBABILITY": DEMAND_SPIKE_PROBABILITY,
        "DATA_QUALITY_ISSUE_PROBABILITY": DATA_QUALITY_ISSUE_PROBABILITY,
    }

    for name, probability in probability_parameters.items():
        assert 0 <= probability <= 1, f"{name} must be between 0 and 1."

    assert DEMAND_SPIKE_FACTOR > 1, "DEMAND_SPIKE_FACTOR must be greater than 1."

    print("PASS: Risk parameters are valid.")


def validate_calendar_factors():
    """
    Validate calendar-based demand factors.

    There should be exactly seven day-of-week factors,
    representing Monday through Sunday.
    """

    print("\n--- Calendar Factor Validation ---")

    assert set(DAY_OF_WEEK_FACTORS.keys()) == set(range(7)), (
        "DAY_OF_WEEK_FACTORS must contain keys 0 through 6."
    )

    for day, factor in DAY_OF_WEEK_FACTORS.items():
        assert factor > 0, f"Day-of-week factor for day {day} must be positive."

    print("PASS: Day-of-week factors are valid.")


def validate_customers():
    """
    Validate customer segment, age-group, and gender
    configuration.
    """

    print("\n--- Customer Configuration Validation ---")

    assert len(CUSTOMER_AGE_GROUPS) > 0, "CUSTOMER_AGE_GROUPS cannot be empty."

    for age_group in CUSTOMER_AGE_GROUPS:
        assert age_group.strip() != "", (
            "Customer age groups cannot contain empty values."
        )

    print("PASS: Customer configuration is valid.")


def main():
    """
    Run all configuration validation checks.
    """

    print("=" * 60)

    print("GulfMart Retail Dataset Configuration Validation")

    print("=" * 60)

    validate_random_seed()

    validate_probabilities()

    validate_dataset_sizes()

    validate_dates()

    validate_products()

    validate_demand_trajectories()

    validate_stores()

    validate_suppliers()

    validate_customers()

    validate_calendar_factors()

    validate_seasonality()

    validate_promotions()

    validate_inventory()

    validate_risk_parameters()

    print("\n" + "=" * 60)

    print("ALL CONFIGURATION CHECKS PASSED")

    print("=" * 60)


if __name__ == "__main__":
    main()
