# ============================================================
# GulfMart Retail Inventory Analytics
# Dataset Generation Configuration Validation
# ============================================================

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
    LOW_SAFETY_STOCK_PROBABILITY,
    LONG_LEAD_TIME_RISK_PROBABILITY,
    DEMAND_SPIKE_PROBABILITY,
    DEMAND_SPIKE_FACTOR,
    INJECT_DATA_QUALITY_ISSUES,
    DATA_QUALITY_ISSUE_PROBABILITY,
)

# Add helper functions
def check_probability_distribution(name, distribution):
    """Check that probabilities are between 0 and 1 and sum to 1."""
    
    total = sum(distribution.values())

    assert all(
        0 <= probability <= 1
        for probability in distribution.values()
    ), f"{name} contains invalid probabilities."

    assert abs(total - 1.0) < 1e-9, (
        f"{name} must sum to 1. Current total: {total}"
    )

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
    print("\n--- Date Validation ---")

    start_date = datetime.strptime(START_DATE, "%Y-%m-%d")
    end_date = datetime.strptime(END_DATE, "%Y-%m-%d")

    assert start_date < end_date, (
        "START_DATE must be earlier than END_DATE."
    )

    print(f"PASS: Date range is {START_DATE} to {END_DATE}")
    
    # Validate product configuration
def validate_products():
    print("\n--- Product Configuration Validation ---")

    assert len(PRODUCT_CATEGORIES) > 0

    for category, subcategories in PRODUCT_CATEGORIES.items():
        assert category.strip() != ""
        assert len(subcategories) > 0

        for subcategory in subcategories:
            assert subcategory.strip() != ""

    assert set(DEMAND_CLASS_PROBABILITIES) == set(DEMAND_CLASS_FACTORS)

    for demand_class, factor in DEMAND_CLASS_FACTORS.items():
        assert factor > 0, (
            f"Demand factor for {demand_class} must be positive."
        )

    min_cost, max_cost = PRODUCT_COST_RANGE
    min_margin, max_margin = PRODUCT_MARGIN_RANGE

    assert min_cost > 0
    assert max_cost > min_cost

    assert 0 < min_margin < max_margin < 1

    print("PASS: Product configuration is internally consistent.")
    
# Validate demand trajectory configuration
def validate_demand_trajectories():
    print("\n--- Demand Trajectory Validation ---")

    assert set(DEMAND_TRAJECTORY_PROBABILITIES) == set(
        DEMAND_TRAJECTORY_FACTORS
    )

    for trajectory, factor in DEMAND_TRAJECTORY_FACTORS.items():
        assert factor > 0, (
            f"Demand factor for {trajectory} must be positive."
        )

    print("PASS: Demand trajectory configuration is valid.")
    
# Validate store configuration
def validate_stores():
    print("\n--- Store Configuration Validation ---")

    assert set(STORE_TYPE_PROBABILITIES) == set(
        STORE_TYPE_DEMAND_FACTORS
    )

    assert set(REGION_CITIES) == set(REGION_DEMAND_FACTORS)

    for region, cities in REGION_CITIES.items():
        assert len(cities) > 0

        for city in cities:
            assert city.strip() != ""

    for factor in STORE_TYPE_DEMAND_FACTORS.values():
        assert factor > 0

    for factor in REGION_DEMAND_FACTORS.values():
        assert factor > 0

    print("PASS: Store configuration is valid.")
    
# Validate supplier configuration
def validate_suppliers():
    print("\n--- Supplier Configuration Validation ---")

    assert set(SUPPLIER_REGION_PROBABILITIES) == set(
        SUPPLIER_LEAD_TIME_RANGES
    )

    for supplier_region, lead_time_range in SUPPLIER_LEAD_TIME_RANGES.items():

        minimum, maximum = lead_time_range

        assert minimum > 0
        assert maximum >= minimum

    print("PASS: Supplier configuration is valid.")
    
# Validate seasonality configuration
def validate_seasonality():
    print("\n--- Seasonality Validation ---")

    assert set(PRODUCT_CATEGORIES) == set(
        CATEGORY_SEASONALITY_FACTORS
    )

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
            assert factor > 0, (
                f"{category} has invalid factor for {season}."
            )

    print("PASS: Category seasonality configuration is valid.")
    
# Validate promotions
def validate_promotions():
    print("\n--- Promotion Validation ---")

    assert 0 <= PROMOTION_PROBABILITY <= 1

    minimum_discount, maximum_discount = PROMOTION_DISCOUNT_RANGE

    assert 0 <= minimum_discount < maximum_discount <= 1

    assert PROMOTION_DEMAND_LIFT > 0

    print("PASS: Promotion configuration is valid.")
    
# Validate inventory configuration
def validate_inventory():
    print("\n--- Inventory Configuration Validation ---")

    assert set(SAFETY_STOCK_DAYS) == set(
        DEMAND_CLASS_PROBABILITIES
    )

    assert set(INITIAL_INVENTORY_DAYS) == set(
        DEMAND_CLASS_PROBABILITIES
    )

    for demand_class in DEMAND_CLASS_PROBABILITIES:

        assert SAFETY_STOCK_DAYS[demand_class] > 0

        assert INITIAL_INVENTORY_DAYS[demand_class] > (
            SAFETY_STOCK_DAYS[demand_class]
        )

    assert MINIMUM_COVERAGE_DAYS > 0

    print("PASS: Inventory configuration is valid.")
    
    
# Validate risk configuration
def validate_risk_parameters():
    print("\n--- Risk Parameter Validation ---")

    probability_parameters = {
        "LOW_SAFETY_STOCK_PROBABILITY":
            LOW_SAFETY_STOCK_PROBABILITY,

        "LONG_LEAD_TIME_RISK_PROBABILITY":
            LONG_LEAD_TIME_RISK_PROBABILITY,

        "DEMAND_SPIKE_PROBABILITY":
            DEMAND_SPIKE_PROBABILITY,

        "DATA_QUALITY_ISSUE_PROBABILITY":
            DATA_QUALITY_ISSUE_PROBABILITY,
    }

    for name, probability in probability_parameters.items():

        assert 0 <= probability <= 1, (
            f"{name} must be between 0 and 1."
        )

    assert DEMAND_SPIKE_FACTOR > 1

    print("PASS: Risk parameters are valid.")
    
    
# Add the main validation runner
def main():
    print("=" * 60)
    print("GulfMart Retail Dataset Configuration Validation")
    print("=" * 60)

    validate_probabilities()
    validate_dataset_sizes()
    validate_dates()
    validate_products()
    validate_demand_trajectories()
    validate_stores()
    validate_suppliers()
    validate_seasonality()
    validate_promotions()
    validate_inventory()
    validate_risk_parameters()

    print("\n" + "=" * 60)
    print("ALL CONFIGURATION CHECKS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
