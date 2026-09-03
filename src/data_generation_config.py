# ============================================================
# GulfMart Retail Inventory Analytics
# Dataset Generation Configuration
# ============================================================

from pathlib import Path


# ------------------------------------------------------------
# Reproducibility
# ------------------------------------------------------------

RANDOM_SEED = 42


# ------------------------------------------------------------
# Date Configuration
# ------------------------------------------------------------

START_DATE = "2023-01-01"
END_DATE = "2025-12-31"


# ------------------------------------------------------------
# Dataset Size
# ------------------------------------------------------------

NUMBER_OF_STORES = 20
NUMBER_OF_PRODUCTS = 500
NUMBER_OF_CUSTOMERS = 5_000
NUMBER_OF_SUPPLIERS = 30

TARGET_SALES_TRANSACTIONS = 125_000


# ------------------------------------------------------------
# Project Paths
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
CLEANED_DATA_DIR = PROJECT_ROOT / "data" / "cleaned"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

# ------------------------------------------------------------
# Product Categories
# ------------------------------------------------------------

PRODUCT_CATEGORIES = {
    "Grocery": [
        "Rice & Grains",
        "Canned Foods",
        "Snacks",
        "Frozen Foods",
        "Cooking Essentials",
    ],
    "Beverages": [
        "Soft Drinks",
        "Juices",
        "Water",
        "Energy Drinks",
        "Hot Beverages",
    ],
    "Personal Care": [
        "Hair Care",
        "Oral Care",
        "Body Care",
        "Men's Grooming",
        "Personal Hygiene",
    ],
    "Household": [
        "Cleaning Supplies",
        "Laundry",
        "Kitchen Supplies",
        "Paper Products",
        "Home Cleaning",
    ],
    "Electronics": [
        "Mobile Accessories",
        "Small Electronics",
        "Audio",
        "Computer Accessories",
        "Smart Devices",
    ],
    "Fashion": [
        "Men's Clothing",
        "Women's Clothing",
        "Children's Clothing",
        "Footwear",
        "Accessories",
    ],
    "Home & Living": [
        "Kitchenware",
        "Storage",
        "Home Decor",
        "Bedding",
        "Furniture Accessories",
    ],
    "Beauty": [
        "Skincare",
        "Makeup",
        "Fragrances",
        "Beauty Tools",
        "Cosmetics",
    ],
}


# ------------------------------------------------------------
# Product Demand Classes
# ------------------------------------------------------------

DEMAND_CLASS_PROBABILITIES = {
    "Fast-moving": 0.20,
    "Medium-moving": 0.55,
    "Slow-moving": 0.25,
}

DEMAND_CLASS_FACTORS = {
    "Fast-moving": 3.0,
    "Medium-moving": 1.0,
    "Slow-moving": 0.30,
}


# ------------------------------------------------------------
# Product Demand Trajectories
# ------------------------------------------------------------

DEMAND_TRAJECTORY_PROBABILITIES = {
    "Growing": 0.20,
    "Stable": 0.55,
    "Declining": 0.15,
    "Volatile": 0.10,
}

DEMAND_TRAJECTORY_FACTORS = {
    "Growing": 1.20,
    "Stable": 1.00,
    "Declining": 0.80,
    "Volatile": 1.00,
}


# ------------------------------------------------------------
# Store Types
# ------------------------------------------------------------

STORE_TYPE_PROBABILITIES = {
    "Hypermarket": 0.20,
    "Supermarket": 0.45,
    "Express": 0.25,
    "E-commerce": 0.10,
}

STORE_TYPE_DEMAND_FACTORS = {
    "Hypermarket": 1.50,
    "Supermarket": 1.00,
    "Express": 0.55,
    "E-commerce": 1.30,
}


# ------------------------------------------------------------
# Regions and Cities
# ------------------------------------------------------------

REGION_CITIES = {
    "Central": [
        "Riyadh",
    ],
    "Western": [
        "Jeddah",
        "Makkah",
        "Madinah",
    ],
    "Eastern": [
        "Dammam",
        "Khobar",
    ],
    "Northern": [
        "Tabuk",
    ],
    "Southern": [
        "Abha",
    ],
}

REGION_DEMAND_FACTORS = {
    "Central": 1.20,
    "Western": 1.10,
    "Eastern": 1.05,
    "Northern": 0.80,
    "Southern": 0.85,
}


# ------------------------------------------------------------
# Supplier Configuration
# ------------------------------------------------------------

SUPPLIER_REGION_PROBABILITIES = {
    "Local": 0.50,
    "Regional": 0.35,
    "International": 0.15,
}

SUPPLIER_LEAD_TIME_RANGES = {
    "Local": (2, 7),
    "Regional": (7, 14),
    "International": (14, 30),
}

SUPPLIER_STATUS_PROBABILITIES = {
    "Active": 0.90,
    "At Risk": 0.07,
    "Inactive": 0.03,
}


# ------------------------------------------------------------
# Customer Configuration
# ------------------------------------------------------------

CUSTOMER_SEGMENT_PROBABILITIES = {
    "Premium": 0.15,
    "Regular": 0.50,
    "Value": 0.25,
    "New": 0.10,
}

CUSTOMER_AGE_GROUPS = [
    "18-24",
    "25-34",
    "35-44",
    "45-54",
    "55+",
]

CUSTOMER_GENDER_PROBABILITIES = {
    "Male": 0.50,
    "Female": 0.50,
}

CUSTOMER_CHANNEL_PROBABILITIES = {
    "Physical": 0.45,
    "E-commerce": 0.35,
    "Omnichannel": 0.20,
}

CUSTOMER_PURCHASE_FREQUENCY_FACTORS = {
    "Premium": 1.50,
    "Regular": 1.00,
    "Value": 0.80,
    "New": 0.60,
}

CUSTOMER_BASKET_FACTORS = {
    "Premium": 1.50,
    "Regular": 1.00,
    "Value": 0.85,
    "New": 0.70,
}

CUSTOMER_PRICE_SENSITIVITY = {
    "Premium": 0.30,
    "Regular": 0.50,
    "Value": 0.80,
    "New": 0.65,
}

# ------------------------------------------------------------
# Day-of-Week Demand Factors
# ------------------------------------------------------------

DAY_OF_WEEK_FACTORS = {
    0: 0.90,  # Monday
    1: 0.95,  # Tuesday
    2: 1.00,  # Wednesday
    3: 1.05,  # Thursday
    4: 1.20,  # Friday
    5: 1.25,  # Saturday
    6: 1.00,  # Sunday
}


# ------------------------------------------------------------
# Seasonal Demand Factors
# ------------------------------------------------------------

CATEGORY_SEASONALITY_FACTORS = {
    "Grocery": {
        "normal": 1.00,
        "ramadan": 1.25,
        "eid": 1.15,
        "summer": 1.00,
        "winter": 1.00,
    },
    "Beverages": {
        "normal": 1.00,
        "ramadan": 1.05,
        "eid": 1.10,
        "summer": 1.35,
        "winter": 0.85,
    },
    "Personal Care": {
        "normal": 1.00,
        "ramadan": 1.10,
        "eid": 1.15,
        "summer": 1.05,
        "winter": 1.00,
    },
    "Household": {
        "normal": 1.00,
        "ramadan": 1.15,
        "eid": 1.10,
        "summer": 1.00,
        "winter": 1.05,
    },
    "Electronics": {
        "normal": 1.00,
        "ramadan": 1.15,
        "eid": 1.20,
        "summer": 1.05,
        "winter": 1.00,
    },
    "Fashion": {
        "normal": 1.00,
        "ramadan": 1.15,
        "eid": 1.30,
        "summer": 1.05,
        "winter": 1.20,
    },
    "Home & Living": {
        "normal": 1.00,
        "ramadan": 1.10,
        "eid": 1.15,
        "summer": 1.00,
        "winter": 1.10,
    },
    "Beauty": {
        "normal": 1.00,
        "ramadan": 1.15,
        "eid": 1.25,
        "summer": 1.05,
        "winter": 1.00,
    },
}


# ------------------------------------------------------------
# Promotion Configuration
# ------------------------------------------------------------

PROMOTION_PROBABILITY = 0.12

PROMOTION_DISCOUNT_RANGE = (0.05, 0.30)

PROMOTION_DEMAND_LIFT = 1.35


# ------------------------------------------------------------
# Pricing and Margin Configuration
# ------------------------------------------------------------

PRODUCT_COST_RANGE = (5.0, 500.0)

PRODUCT_MARGIN_RANGE = (0.15, 0.45)


# ------------------------------------------------------------
# Inventory Configuration
# ------------------------------------------------------------

SAFETY_STOCK_DAYS = {
    "Fast-moving": 7,
    "Medium-moving": 5,
    "Slow-moving": 3,
}

INITIAL_INVENTORY_DAYS = {
    "Fast-moving": 14,
    "Medium-moving": 21,
    "Slow-moving": 45,
}

MINIMUM_COVERAGE_DAYS = 2


# ------------------------------------------------------------
# Inventory Risk Configuration
# ------------------------------------------------------------

LOW_SAFETY_STOCK_PROBABILITY = 0.15

LONG_LEAD_TIME_RISK_PROBABILITY = 0.20

DEMAND_SPIKE_PROBABILITY = 0.08

DEMAND_SPIKE_FACTOR = 1.75


# ------------------------------------------------------------
# Controlled Data Quality Issues
# ------------------------------------------------------------

INJECT_DATA_QUALITY_ISSUES = True

DATA_QUALITY_ISSUE_PROBABILITY = 0.001
