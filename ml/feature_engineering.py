# ============================================================
# ml/feature_engineering.py — Per-Return Feature Builder
# ============================================================
#
# YEH FILE KYA KARTI HAI?
# ────────────────────────
# 1. Input: customer_id + return_id (+ data dict / cutoff_time)
# 2. Output: Single feature vector (23 features)
# 3. Data Leakage Protection: Only data strictly BEFORE return_date is used.
# 4. Fast pre-indexed lookups for real-time inference and ultra-fast training dataset generation.
# ============================================================

import os
import sys
from datetime import timedelta
import numpy as np
import pandas as pd

# Logger aur Exception import
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.logger import logger
from src.exception import CustomException

_data_cache = {}


def _load_data(data_dir: str = None) -> dict:
    """
    Loads all raw CSV files and builds indexed lookups for fast retrieval.
    """
    global _data_cache
    if _data_cache:
        return _data_cache

    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

    logger.info(f"Loading raw CSV data from: {data_dir}")

    customers = pd.read_csv(os.path.join(data_dir, "customers.csv"))
    orders = pd.read_csv(os.path.join(data_dir, "orders.csv"))
    returns = pd.read_csv(os.path.join(data_dir, "returns.csv"))
    refunds = pd.read_csv(os.path.join(data_dir, "refunds.csv"))
    devices = pd.read_csv(os.path.join(data_dir, "devices.csv"))
    addresses = pd.read_csv(os.path.join(data_dir, "addresses.csv"))

    # Date parsing
    customers["signup_date"] = pd.to_datetime(customers["signup_date"])
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    returns["return_date"] = pd.to_datetime(returns["return_date"])
    refunds["refund_date"] = pd.to_datetime(refunds["refund_date"])

    # Build indexed lookups for high performance
    customers_dict = customers.set_index("customer_id").to_dict(orient="index")
    orders_dict = orders.set_index("order_id").to_dict(orient="index")
    returns_dict = returns.set_index("return_id").to_dict(orient="index")
    devices_dict = devices.set_index("device_id").to_dict(orient="index")
    addresses_dict = addresses.set_index("address_id").to_dict(orient="index")

    # Grouped dataframes for fast customer filtering
    orders_by_cust = {cid: df for cid, df in orders.groupby("customer_id")}
    returns_by_cust = {cid: df for cid, df in returns.groupby("customer_id")}
    refunds_by_cust = {cid: df for cid, df in refunds.groupby("customer_id")}

    _data_cache = {
        "customers": customers,
        "orders": orders,
        "returns": returns,
        "refunds": refunds,
        "devices": devices,
        "addresses": addresses,
        "customers_dict": customers_dict,
        "orders_dict": orders_dict,
        "returns_dict": returns_dict,
        "devices_dict": devices_dict,
        "addresses_dict": addresses_dict,
        "orders_by_cust": orders_by_cust,
        "returns_by_cust": returns_by_cust,
        "refunds_by_cust": refunds_by_cust,
    }

    logger.info(
        f"Loaded: customers={len(customers)}, orders={len(orders)}, "
        f"returns={len(returns)}, refunds={len(refunds)}"
    )
    return _data_cache


# ════════════════════════════════════════════════════════════
# CANONICAL FEATURE LIST
# ════════════════════════════════════════════════════════════
FEATURE_COLUMNS = [
    # ── Historical aggregate features ──
    "account_age_days",              # Account age up to cutoff
    "previous_orders",               # Orders before cutoff
    "previous_returns",              # Returns before cutoff
    "return_rate",                   # previous_returns / previous_orders
    "previous_refund_count",         # Refunds before cutoff
    "previous_refund_amount",        # Refund amount before cutoff
    "average_order_value",           # Historical average order value
    "refund_to_order_ratio",         # previous_refund_amount / total_order_amount

    # ── Velocity features ──
    "orders_last_24h",               # Orders in 24h prior to cutoff
    "returns_last_7d",               # Returns in 7d prior to cutoff
    "returns_last_30d",              # Returns in 30d prior to cutoff
    "refunds_last_30d",              # Refunds in 30d prior to cutoff

    # ── Current return request features ──
    "current_order_amount",          # Value of the associated order
    "current_return_amount",         # Value of current return
    "return_to_order_ratio",         # current_return_amount / current_order_amount
    "days_to_return",                # Days elapsed between order and return

    # ── Behavioral pattern features ──
    "same_reason_count",             # Previous returns with the same reason
    "unique_return_reasons",         # Count of distinct return reasons
    "return_frequency",              # Returns per month
    "return_gap_days",               # Days since last return
    "high_value_return_flag",        # return_amount > 2 * avg_order_value

    # ── Device / Address linkage ──
    "device_linked_accounts",        # Accounts sharing the same device
    "address_linked_accounts",       # Accounts sharing the same address
]


def build_features_for_return(
    customer_id: str,
    return_id: str,
    data: dict = None
) -> dict:
    """
    Builds the 23-feature vector for a specific return request.
    Strict historical cutoff ensures zero data leakage.
    """
    if data is None:
        data = _load_data()

    # Fast dictionary lookups
    ret_row = data["returns_dict"].get(return_id)
    if not ret_row:
        # Fallback to dataframe search
        match = data["returns"][data["returns"]["return_id"] == return_id]
        if match.empty:
            raise ValueError(f"Return ID {return_id} not found in data")
        ret_row = match.iloc[0].to_dict()

    cutoff_time = ret_row["return_date"]
    current_return_amount = float(ret_row["return_amount"])
    current_order_id = ret_row["order_id"]
    current_return_reason = str(ret_row["return_reason"])

    # Current order lookup
    ord_row = data["orders_dict"].get(current_order_id)
    if ord_row:
        current_order_amount = float(ord_row["order_amount"])
        order_date = ord_row["order_date"]
    else:
        current_order_amount = current_return_amount
        order_date = cutoff_time

    # Customer lookup
    cust_row = data["customers_dict"].get(customer_id)
    if not cust_row:
        match = data["customers"][data["customers"]["customer_id"] == customer_id]
        if match.empty:
            raise ValueError(f"Customer {customer_id} not found in data")
        cust_row = match.iloc[0].to_dict()

    signup_date = cust_row["signup_date"]
    device_id = cust_row["device_id"]
    address_id = cust_row["address_id"]

    # Customer history before cutoff
    all_cust_orders = data["orders_by_cust"].get(customer_id)
    if all_cust_orders is not None and not all_cust_orders.empty:
        cust_orders = all_cust_orders[all_cust_orders["order_date"] < cutoff_time]
    else:
        cust_orders = pd.DataFrame()

    previous_orders = len(cust_orders)
    total_order_amount = float(cust_orders["order_amount"].sum()) if previous_orders > 0 else 0.0
    average_order_value = float(cust_orders["order_amount"].mean()) if previous_orders > 0 else 0.0

    all_cust_returns = data["returns_by_cust"].get(customer_id)
    if all_cust_returns is not None and not all_cust_returns.empty:
        cust_returns = all_cust_returns[
            (all_cust_returns["return_date"] < cutoff_time) &
            (all_cust_returns["return_id"] != return_id)
        ]
    else:
        cust_returns = pd.DataFrame()

    previous_returns = len(cust_returns)
    return_rate = previous_returns / previous_orders if previous_orders > 0 else 0.0

    all_cust_refunds = data["refunds_by_cust"].get(customer_id)
    if all_cust_refunds is not None and not all_cust_refunds.empty:
        cust_refunds = all_cust_refunds[all_cust_refunds["refund_date"] < cutoff_time]
    else:
        cust_refunds = pd.DataFrame()

    previous_refund_count = len(cust_refunds)
    previous_refund_amount = float(cust_refunds["refund_amount"].sum()) if previous_refund_count > 0 else 0.0
    refund_to_order_ratio = previous_refund_amount / total_order_amount if total_order_amount > 0 else 0.0

    # Account age
    account_age_days = max(0, (cutoff_time - signup_date).days)

    # Velocity features
    if previous_orders > 0:
        orders_last_24h = int((cust_orders["order_date"] >= (cutoff_time - timedelta(hours=24))).sum())
    else:
        orders_last_24h = 0

    if previous_returns > 0:
        returns_last_7d = int((cust_returns["return_date"] >= (cutoff_time - timedelta(days=7))).sum())
        returns_last_30d = int((cust_returns["return_date"] >= (cutoff_time - timedelta(days=30))).sum())
    else:
        returns_last_7d = 0
        returns_last_30d = 0

    if previous_refund_count > 0:
        refunds_last_30d = int((cust_refunds["refund_date"] >= (cutoff_time - timedelta(days=30))).sum())
    else:
        refunds_last_30d = 0

    # Current request features
    return_to_order_ratio = (
        current_return_amount / current_order_amount
        if current_order_amount > 0 else 0.0
    )
    days_to_return = max(0, (cutoff_time - order_date).days)

    # Behavioral pattern features
    if previous_returns > 0:
        same_reason_count = int((cust_returns["return_reason"] == current_return_reason).sum())
        unique_return_reasons = int(cust_returns["return_reason"].nunique())
        last_return_date = cust_returns["return_date"].max()
        return_gap_days = max(0, (cutoff_time - last_return_date).days)
    else:
        same_reason_count = 0
        unique_return_reasons = 0
        return_gap_days = account_age_days

    if account_age_days > 0:
        return_frequency = round(previous_returns / (account_age_days / 30.0), 4)
    else:
        return_frequency = 0.0

    high_value_return_flag = 1 if (
        average_order_value > 0 and current_return_amount > 2 * average_order_value
    ) else 0

    # Device and address linkage
    dev_info = data["devices_dict"].get(device_id, {})
    device_linked_accounts = int(dev_info.get("linked_accounts", 1))

    addr_info = data["addresses_dict"].get(address_id, {})
    address_linked_accounts = int(addr_info.get("linked_accounts", 1))

    return {
        "account_age_days": account_age_days,
        "previous_orders": previous_orders,
        "previous_returns": previous_returns,
        "return_rate": round(return_rate, 4),
        "previous_refund_count": previous_refund_count,
        "previous_refund_amount": round(previous_refund_amount, 2),
        "average_order_value": round(average_order_value, 2),
        "refund_to_order_ratio": round(refund_to_order_ratio, 4),
        "orders_last_24h": orders_last_24h,
        "returns_last_7d": returns_last_7d,
        "returns_last_30d": returns_last_30d,
        "refunds_last_30d": refunds_last_30d,
        "current_order_amount": round(current_order_amount, 2),
        "current_return_amount": round(current_return_amount, 2),
        "return_to_order_ratio": round(return_to_order_ratio, 4),
        "days_to_return": days_to_return,
        "same_reason_count": same_reason_count,
        "unique_return_reasons": unique_return_reasons,
        "return_frequency": round(return_frequency, 4),
        "return_gap_days": return_gap_days,
        "high_value_return_flag": high_value_return_flag,
        "device_linked_accounts": device_linked_accounts,
        "address_linked_accounts": address_linked_accounts,
    }


def generate_label(features: dict) -> int:
    """
    Rule-based labeling for training dataset: 0 = Normal, 1 = Potentially Abusive.
    """
    if features["return_rate"] > 0.35 and features["previous_returns"] >= 3:
        return 1
    if features["refund_to_order_ratio"] > 0.30:
        return 1
    if features["account_age_days"] < 120 and features["previous_orders"] > 10:
        return 1
    if features["device_linked_accounts"] > 3 and features["return_rate"] > 0.20:
        return 1
    if features["address_linked_accounts"] > 3 and features["return_rate"] > 0.20:
        return 1
    if features["returns_last_7d"] >= 3:
        return 1
    if features["high_value_return_flag"] == 1 and features["return_rate"] > 0.25:
        return 1
    return 0


def build_training_dataset(noise_ratio: float = 0.03, random_seed: int = 42) -> pd.DataFrame:
    """
    Builds the full training dataset with 1 row per return request.
    """
    data = _load_data()
    returns_df = data["returns"]

    logger.info(f"Building training dataset for {len(returns_df)} return requests...")
    print(f"\n[1] Building features for {len(returns_df)} return requests...")

    rows = []
    errors = 0

    for idx, ret in returns_df.iterrows():
        try:
            features = build_features_for_return(
                customer_id=ret["customer_id"],
                return_id=ret["return_id"],
                data=data,
            )
            label = generate_label(features)
            features["potentially_abusive"] = label
            features["return_id"] = ret["return_id"]
            features["customer_id"] = ret["customer_id"]
            rows.append(features)
        except Exception as e:
            errors += 1
            if errors <= 5:
                logger.warning(f"Skipping {ret['return_id']}: {e}")

        if (idx + 1) % 1500 == 0:
            print(f"    Processed {idx + 1}/{len(returns_df)} returns...")

    df = pd.DataFrame(rows)

    # 3% noise flip to prevent artificial trivial separation
    np.random.seed(random_seed)
    noise_n = int(len(df) * noise_ratio)
    noise_idx = np.random.choice(df.index, size=noise_n, replace=False)
    df.loc[noise_idx, "potentially_abusive"] = 1 - df.loc[noise_idx, "potentially_abusive"]

    abusive = int(df["potentially_abusive"].sum())
    normal = len(df) - abusive

    logger.info(f"Training dataset built: {len(df)} rows, {abusive} abusive, {normal} normal, {errors} skipped")
    print(f"\n[OK] Training dataset ready!")
    print(f"     Total rows:   {len(df)}")
    print(f"     Abusive (1):  {abusive} ({abusive/len(df)*100:.1f}%)")
    print(f"     Normal  (0):  {normal} ({normal/len(df)*100:.1f}%)")
    print(f"     Skipped:      {errors}")
    print(f"     Features:     {len(FEATURE_COLUMNS)}")

    return df


if __name__ == "__main__":
    df = build_training_dataset()
    artifacts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    output_path = os.path.join(artifacts_dir, "return_features.csv")
    df.to_csv(output_path, index=False)
    print(f"\n     Saved to: {output_path}")
