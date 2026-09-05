"""
ReturnShield AI — Synthetic Dataset Generator
==============================================
Generates realistic e-commerce data with embedded behavioral patterns
for identifying potentially abusive return/refund behavior.

Usage:
    python generate_dataset.py              # default seed=42
    python generate_dataset.py --seed 123   # custom seed

Output:
    customers.csv, orders.csv, returns.csv,
    refunds.csv, devices.csv, addresses.csv
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import argparse
import sys

# ════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════

NUM_CUSTOMERS = 5000

# Timeline
REFERENCE_DATE = datetime(2026, 9, 1)       # "today" for account-age calc
SIGNUP_EARLIEST = datetime(2025, 3, 1)       # oldest possible signup
SIGNUP_LATEST_NORMAL = datetime(2026, 6, 1)  # normal customers sign up earlier
SIGNUP_LATEST_ABUSIVE = datetime(2026, 8, 15)# abusive skew newer
ORDER_START = datetime(2026, 1, 1)
ORDER_END = datetime(2026, 8, 31)

# ── Behavior buckets (hidden label, NOT in final CSV) ──────
BEHAVIOR_COUNTS = {
    "normal": 3900,
    "mild_abusive": 500,
    "heavy_abusive": 250,
    "edge_case": 350,
}

# ── Geography ──────────────────────────────────────────────
CITIES_INFO = [
    # (city_name, weight, postal_prefix)
    ("Mumbai", 0.15, "400"),
    ("Delhi", 0.14, "110"),
    ("Bangalore", 0.12, "560"),
    ("Hyderabad", 0.09, "500"),
    ("Chennai", 0.08, "600"),
    ("Kolkata", 0.07, "700"),
    ("Pune", 0.08, "411"),
    ("Ahmedabad", 0.06, "380"),
    ("Jaipur", 0.05, "302"),
    ("Lucknow", 0.04, "226"),
    ("Chandigarh", 0.03, "160"),
    ("Kochi", 0.03, "682"),
    ("Indore", 0.03, "452"),
    ("Surat", 0.03, "395"),
]
CITY_NAMES = [c[0] for c in CITIES_INFO]
CITY_WEIGHTS = [c[1] for c in CITIES_INFO]
CITY_POSTAL = {c[0]: c[2] for c in CITIES_INFO}

# ── Product categories & prices ────────────────────────────
CATEGORIES = [
    "Electronics", "Clothing", "Footwear", "Home & Kitchen",
    "Beauty", "Books", "Sports", "Accessories",
]
CATEGORY_PRICE = {
    "Electronics": (2000, 55000),
    "Clothing": (400, 6000),
    "Footwear": (600, 8000),
    "Home & Kitchen": (300, 12000),
    "Beauty": (150, 4000),
    "Books": (100, 1500),
    "Sports": (400, 8000),
    "Accessories": (200, 4000),
}
# Normal customers buy across categories evenly
NORMAL_CAT_WEIGHTS = [0.15, 0.20, 0.12, 0.13, 0.10, 0.08, 0.10, 0.12]
# Abusive customers lean toward high-value + easy-return categories
ABUSIVE_CAT_WEIGHTS = [0.28, 0.22, 0.14, 0.08, 0.06, 0.02, 0.08, 0.12]

PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "Net Banking", "COD", "Wallet"]
PAYMENT_WEIGHTS = [0.20, 0.18, 0.30, 0.08, 0.15, 0.09]

DEVICE_TYPES = ["Mobile Browser", "Desktop Browser", "Tablet", "Mobile App"]
DEVICE_TYPE_WEIGHTS = [0.30, 0.22, 0.08, 0.40]

RETURN_REASONS = [
    "Defective Product",
    "Wrong Item Received",
    "Changed Mind",
    "Not As Described",
    "Size/Fit Issue",
    "Better Price Found",
    "Damaged in Transit",
    "Quality Not Satisfactory",
]
NORMAL_REASON_W = [0.20, 0.10, 0.12, 0.08, 0.22, 0.05, 0.15, 0.08]
ABUSIVE_REASON_W = [0.08, 0.05, 0.30, 0.25, 0.08, 0.10, 0.05, 0.09]

CUSTOMER_SEGMENTS = ["regular", "premium", "new", "occasional"]

DELIVERY_STATUSES = ["Delivered", "In Transit", "Returned to Seller", "Cancelled"]


# ════════════════════════════════════════════════════════════
# HELPER UTILITIES
# ════════════════════════════════════════════════════════════

def random_date(start: datetime, end: datetime) -> datetime:
    """Return a random datetime between start and end."""
    delta = (end - start).days
    if delta <= 0:
        return start
    return start + timedelta(days=np.random.randint(0, delta + 1))


def random_date_after(base: datetime, min_days: int, max_days: int,
                      ceiling: datetime = None) -> datetime:
    """Return a random date at least min_days and at most max_days after base."""
    days = np.random.randint(min_days, max_days + 1)
    result = base + timedelta(days=days)
    if ceiling and result > ceiling:
        result = ceiling
    return result


def round_amount(val: float) -> float:
    """Round to 2 decimal places, ensure positive."""
    return max(round(val, 2), 0.01)


# ════════════════════════════════════════════════════════════
# STEP 1 — ASSIGN BEHAVIOR TYPES
# ════════════════════════════════════════════════════════════

def assign_behavior_types(n: int) -> list:
    """Create a shuffled list of behavior labels for n customers."""
    labels = []
    for btype, count in BEHAVIOR_COUNTS.items():
        labels.extend([btype] * count)
    # Pad/trim to exactly n
    while len(labels) < n:
        labels.append("normal")
    labels = labels[:n]
    np.random.shuffle(labels)
    return labels


# ════════════════════════════════════════════════════════════
# STEP 2 — GENERATE DEVICES
# ════════════════════════════════════════════════════════════

def generate_devices_and_assign(behavior_types: list):
    """
    Create device IDs and assign them to customers.
    Some devices are shared across multiple accounts.

    Returns: (device_assignments: list[str], devices_df: pd.DataFrame)
    """
    n = len(behavior_types)

    # ── Determine who shares devices ───────────────────────
    # Probability of being in a shared-device group
    share_prob = {
        "normal": 0.04,
        "mild_abusive": 0.35,
        "heavy_abusive": 0.65,
        "edge_case": 0.15,
    }

    customer_indices = list(range(n))
    sharers = []
    non_sharers = []

    for idx in customer_indices:
        p = share_prob[behavior_types[idx]]
        if np.random.random() < p:
            sharers.append(idx)
        else:
            non_sharers.append(idx)

    np.random.shuffle(sharers)

    # ── Group sharers into device rings (2–5 customers each) ─
    device_assignments = [""] * n
    device_records = []
    device_counter = 1

    i = 0
    while i < len(sharers):
        group_size = min(np.random.randint(2, 6), len(sharers) - i)
        if group_size < 2:
            non_sharers.append(sharers[i])
            i += 1
            continue
        group = sharers[i : i + group_size]
        did = f"DEV{device_counter:05d}"
        dtype = np.random.choice(DEVICE_TYPES, p=DEVICE_TYPE_WEIGHTS)
        first_seen = random_date(SIGNUP_EARLIEST, ORDER_END)
        device_records.append({
            "device_id": did,
            "device_type": dtype,
            "first_seen": first_seen.strftime("%Y-%m-%d"),
            "linked_accounts": len(group),
        })
        for idx in group:
            device_assignments[idx] = did
        device_counter += 1
        i += group_size

    # ── Unique devices for everyone else ───────────────────
    for idx in non_sharers:
        did = f"DEV{device_counter:05d}"
        dtype = np.random.choice(DEVICE_TYPES, p=DEVICE_TYPE_WEIGHTS)
        first_seen = random_date(SIGNUP_EARLIEST, ORDER_END)
        device_records.append({
            "device_id": did,
            "device_type": dtype,
            "first_seen": first_seen.strftime("%Y-%m-%d"),
            "linked_accounts": 1,
        })
        device_assignments[idx] = did
        device_counter += 1

    devices_df = pd.DataFrame(device_records)
    return device_assignments, devices_df


# ════════════════════════════════════════════════════════════
# STEP 3 — GENERATE ADDRESSES
# ════════════════════════════════════════════════════════════

def generate_addresses_and_assign(behavior_types: list):
    """
    Create address IDs and assign them to customers.
    Some addresses are shared (roommates, fraud rings, etc.).

    Returns: (address_assignments, city_assignments, address_df)
    """
    n = len(behavior_types)

    share_prob = {
        "normal": 0.05,
        "mild_abusive": 0.30,
        "heavy_abusive": 0.60,
        "edge_case": 0.12,
    }

    sharers, non_sharers = [], []
    for idx in range(n):
        p = share_prob[behavior_types[idx]]
        if np.random.random() < p:
            sharers.append(idx)
        else:
            non_sharers.append(idx)

    np.random.shuffle(sharers)

    address_assignments = [""] * n
    city_assignments = [""] * n
    address_records = []
    addr_counter = 1

    # ── Shared address groups ──────────────────────────────
    i = 0
    while i < len(sharers):
        group_size = min(np.random.randint(2, 5), len(sharers) - i)
        if group_size < 2:
            non_sharers.append(sharers[i])
            i += 1
            continue
        group = sharers[i : i + group_size]
        aid = f"ADDR{addr_counter:05d}"
        city = np.random.choice(CITY_NAMES, p=CITY_WEIGHTS)
        postal = CITY_POSTAL[city] + f"{np.random.randint(100, 999)}"
        address_records.append({
            "address_id": aid,
            "city": city,
            "postal_area": postal,
            "linked_accounts": len(group),
        })
        for idx in group:
            address_assignments[idx] = aid
            city_assignments[idx] = city
        addr_counter += 1
        i += group_size

    # ── Unique addresses ───────────────────────────────────
    for idx in non_sharers:
        aid = f"ADDR{addr_counter:05d}"
        city = np.random.choice(CITY_NAMES, p=CITY_WEIGHTS)
        postal = CITY_POSTAL[city] + f"{np.random.randint(100, 999)}"
        address_records.append({
            "address_id": aid,
            "city": city,
            "postal_area": postal,
            "linked_accounts": 1,
        })
        address_assignments[idx] = aid
        city_assignments[idx] = city
        addr_counter += 1

    addresses_df = pd.DataFrame(address_records)
    return address_assignments, city_assignments, addresses_df


# ════════════════════════════════════════════════════════════
# STEP 4 — GENERATE CUSTOMERS
# ════════════════════════════════════════════════════════════

def generate_customers(behavior_types, device_assignments, address_assignments,
                       city_assignments):
    """Build the customers DataFrame."""
    records = []
    for idx in range(len(behavior_types)):
        btype = behavior_types[idx]
        cid = f"CUST{idx + 1:05d}"

        # Signup date — abusive customers tend to be newer
        if btype in ("heavy_abusive", "mild_abusive"):
            # 70 % chance of being a recent signup
            if np.random.random() < 0.70:
                signup = random_date(datetime(2026, 4, 1), SIGNUP_LATEST_ABUSIVE)
            else:
                signup = random_date(SIGNUP_EARLIEST, SIGNUP_LATEST_NORMAL)
        elif btype == "edge_case":
            signup = random_date(datetime(2025, 9, 1), datetime(2026, 7, 1))
        else:  # normal
            signup = random_date(SIGNUP_EARLIEST, SIGNUP_LATEST_NORMAL)

        account_age = (REFERENCE_DATE - signup).days

        # Customer segment — business-level label (not a fraud flag)
        if account_age < 90:
            seg_weights = [0.15, 0.05, 0.70, 0.10]
        elif account_age < 270:
            seg_weights = [0.55, 0.15, 0.10, 0.20]
        else:
            seg_weights = [0.50, 0.25, 0.02, 0.23]

        # Abusive customers sometimes game premium status
        if btype in ("heavy_abusive",) and np.random.random() < 0.15:
            segment = "premium"
        else:
            segment = np.random.choice(CUSTOMER_SEGMENTS, p=seg_weights)

        records.append({
            "customer_id": cid,
            "signup_date": signup.strftime("%Y-%m-%d"),
            "account_age_days": account_age,
            "device_id": device_assignments[idx],
            "address_id": address_assignments[idx],
            "city": city_assignments[idx],
            "customer_segment": segment,
        })

    return pd.DataFrame(records), {r["customer_id"]: behavior_types[i]
                                    for i, r in enumerate(records)}


# ════════════════════════════════════════════════════════════
# STEP 5 — GENERATE ORDERS
# ════════════════════════════════════════════════════════════

def generate_orders(customers_df, behavior_map):
    """
    Create orders for each customer.
    Order volume and patterns depend on behavior type.
    """
    records = []
    order_counter = 1

    for _, cust in customers_df.iterrows():
        cid = cust["customer_id"]
        btype = behavior_map[cid]
        signup = datetime.strptime(cust["signup_date"], "%Y-%m-%d")
        # Orders can only start after signup (and after ORDER_START)
        earliest_order = max(signup, ORDER_START)
        if earliest_order > ORDER_END:
            continue

        # Number of orders
        if btype == "normal":
            n_orders = np.random.randint(3, 9)          # 3–8
        elif btype == "mild_abusive":
            n_orders = np.random.randint(8, 18)          # 8–17
        elif btype == "heavy_abusive":
            n_orders = np.random.randint(12, 26)         # 12–25
        else:  # edge_case
            n_orders = np.random.randint(3, 13)          # 3–12

        # Abusive customers sometimes bunch orders in short windows
        cluster_orders = btype in ("heavy_abusive", "mild_abusive") and np.random.random() < 0.50
        if cluster_orders:
            cluster_start = random_date(earliest_order,
                                        ORDER_END - timedelta(days=30))
            cluster_end = cluster_start + timedelta(days=np.random.randint(7, 30))
            cluster_end = min(cluster_end, ORDER_END)
            n_cluster = max(1, int(n_orders * np.random.uniform(0.4, 0.7)))
        else:
            n_cluster = 0

        cat_weights = ABUSIVE_CAT_WEIGHTS if btype in ("heavy_abusive", "mild_abusive") else NORMAL_CAT_WEIGHTS

        for i in range(n_orders):
            oid = f"ORD{order_counter:06d}"

            # Determine order date
            if cluster_orders and i < n_cluster:
                odate = random_date(cluster_start, cluster_end)
            else:
                odate = random_date(earliest_order, ORDER_END)

            # Category & amount
            cat = np.random.choice(CATEGORIES, p=cat_weights)
            lo, hi = CATEGORY_PRICE[cat]
            # Log-normal ish distribution for prices
            mean_price = (lo + hi) / 2
            amount = round_amount(np.random.lognormal(
                mean=np.log(mean_price * 0.6), sigma=0.5))
            amount = round_amount(np.clip(amount, lo, hi))

            # Payment method
            pm = np.random.choice(PAYMENT_METHODS, p=PAYMENT_WEIGHTS)

            # Delivery status
            if odate > ORDER_END - timedelta(days=7):
                # Recent orders might still be in transit
                ds = np.random.choice(DELIVERY_STATUSES, p=[0.60, 0.25, 0.05, 0.10])
            else:
                ds = np.random.choice(DELIVERY_STATUSES, p=[0.88, 0.02, 0.05, 0.05])

            records.append({
                "order_id": oid,
                "customer_id": cid,
                "order_date": odate.strftime("%Y-%m-%d"),
                "order_amount": amount,
                "category": cat,
                "payment_method": pm,
                "delivery_status": ds,
            })
            order_counter += 1

    return pd.DataFrame(records)


# ════════════════════════════════════════════════════════════
# STEP 6 — GENERATE RETURNS
# ════════════════════════════════════════════════════════════

def generate_returns(orders_df, behavior_map):
    """
    Create returns for a subset of orders.
    Return rate depends on customer behavior type.
    Only delivered orders can be returned.
    """
    records = []
    return_counter = 1

    delivered = orders_df[orders_df["delivery_status"] == "Delivered"].copy()

    for _, order in delivered.iterrows():
        cid = order["customer_id"]
        btype = behavior_map[cid]

        # Per-order return probability
        if btype == "normal":
            p_return = np.random.uniform(0.03, 0.12)
        elif btype == "mild_abusive":
            p_return = np.random.uniform(0.25, 0.50)
        elif btype == "heavy_abusive":
            p_return = np.random.uniform(0.40, 0.72)
        else:  # edge_case
            p_return = np.random.uniform(0.08, 0.35)

        if np.random.random() >= p_return:
            continue

        rid = f"RET{return_counter:06d}"
        odate = datetime.strptime(order["order_date"], "%Y-%m-%d")

        # Return date: 1–30 days after order; abusive tend to return faster
        if btype in ("heavy_abusive", "mild_abusive"):
            rdate = random_date_after(odate, 1, 14, ceiling=ORDER_END + timedelta(days=15))
        else:
            rdate = random_date_after(odate, 2, 30, ceiling=ORDER_END + timedelta(days=30))

        # Return reason
        reason_w = ABUSIVE_REASON_W if btype in ("heavy_abusive", "mild_abusive") else NORMAL_REASON_W
        reason = np.random.choice(RETURN_REASONS, p=reason_w)

        # Return amount (full or partial)
        if np.random.random() < 0.80:
            ret_amount = order["order_amount"]  # full return
        else:
            ret_amount = round_amount(order["order_amount"] * np.random.uniform(0.4, 0.95))

        # Return status
        if btype == "heavy_abusive":
            rstatus = np.random.choice(
                ["Approved", "Pending", "Rejected"], p=[0.55, 0.25, 0.20])
        elif btype == "mild_abusive":
            rstatus = np.random.choice(
                ["Approved", "Pending", "Rejected"], p=[0.60, 0.22, 0.18])
        else:
            rstatus = np.random.choice(
                ["Approved", "Pending", "Rejected"], p=[0.72, 0.15, 0.13])

        records.append({
            "return_id": rid,
            "order_id": order["order_id"],
            "customer_id": cid,
            "return_date": rdate.strftime("%Y-%m-%d"),
            "return_reason": reason,
            "return_amount": ret_amount,
            "return_status": rstatus,
        })
        return_counter += 1

    return pd.DataFrame(records)


# ════════════════════════════════════════════════════════════
# STEP 7 — GENERATE REFUNDS
# ════════════════════════════════════════════════════════════

def generate_refunds(returns_df, orders_df, behavior_map):
    """
    Create refunds.
    - Most approved returns → refund
    - Some pending returns → refund (partial processing)
    - A few refunds without a return (customer-service gestures)
    """
    records = []
    refund_counter = 1

    # ── Refunds from returns ───────────────────────────────
    for _, ret in returns_df.iterrows():
        cid = ret["customer_id"]
        btype = behavior_map[cid]

        if ret["return_status"] == "Approved":
            p_refund = 0.92
        elif ret["return_status"] == "Pending":
            p_refund = 0.35
        else:  # Rejected
            p_refund = 0.03  # rare error / override

        if np.random.random() >= p_refund:
            continue

        rfid = f"REF{refund_counter:06d}"
        rdate = datetime.strptime(ret["return_date"], "%Y-%m-%d")
        refund_date = random_date_after(rdate, 1, 12,
                                        ceiling=ORDER_END + timedelta(days=30))

        # Refund amount ≤ return amount
        if np.random.random() < 0.85:
            ref_amount = ret["return_amount"]  # full
        else:
            ref_amount = round_amount(ret["return_amount"] * np.random.uniform(0.5, 0.95))

        # Refund status
        if refund_date > ORDER_END:
            rstatus = np.random.choice(["Processed", "Pending"], p=[0.55, 0.45])
        else:
            rstatus = np.random.choice(
                ["Processed", "Pending", "Declined"], p=[0.82, 0.12, 0.06])

        records.append({
            "refund_id": rfid,
            "order_id": ret["order_id"],
            "customer_id": cid,
            "refund_date": refund_date.strftime("%Y-%m-%d"),
            "refund_amount": ref_amount,
            "refund_status": rstatus,
        })
        refund_counter += 1

    # ── A small number of goodwill / CS refunds (no return) ─
    delivered_no_return = orders_df[
        (orders_df["delivery_status"] == "Delivered") &
        (~orders_df["order_id"].isin(returns_df["order_id"] if len(returns_df) > 0 else []))
    ]
    n_goodwill = int(len(delivered_no_return) * 0.008)  # ~0.8 %
    if n_goodwill > 0:
        goodwill_sample = delivered_no_return.sample(n=n_goodwill)
        for _, order in goodwill_sample.iterrows():
            rfid = f"REF{refund_counter:06d}"
            odate = datetime.strptime(order["order_date"], "%Y-%m-%d")
            refund_date = random_date_after(odate, 3, 45,
                                            ceiling=ORDER_END + timedelta(days=30))
            ref_amount = round_amount(
                order["order_amount"] * np.random.uniform(0.10, 0.50))
            records.append({
                "refund_id": rfid,
                "order_id": order["order_id"],
                "customer_id": order["customer_id"],
                "refund_date": refund_date.strftime("%Y-%m-%d"),
                "refund_amount": ref_amount,
                "refund_status": "Processed",
            })
            refund_counter += 1

    return pd.DataFrame(records)


# ════════════════════════════════════════════════════════════
# STEP 8 — VALIDATION
# ════════════════════════════════════════════════════════════

def validate_all(customers, orders, returns, refunds, devices, addresses):
    """Run comprehensive data-quality checks. Returns report string."""
    lines = []

    def heading(text):
        lines.append(f"\n{'=' * 60}")
        lines.append(f"  {text}")
        lines.append(f"{'=' * 60}")

    def check(label, passed):
        status = "[PASS]" if passed else "[FAIL]"
        lines.append(f"  {status}  {label}")

    # -- Row counts
    heading("ROW COUNTS")
    lines.append(f"  customers : {len(customers):,}")
    lines.append(f"  orders    : {len(orders):,}")
    lines.append(f"  returns   : {len(returns):,}")
    lines.append(f"  refunds   : {len(refunds):,}")
    lines.append(f"  devices   : {len(devices):,}")
    lines.append(f"  addresses : {len(addresses):,}")

    # -- Unique IDs
    heading("UNIQUE-ID CHECKS")
    check("customer_id unique",
          customers["customer_id"].is_unique)
    check("order_id unique",
          orders["order_id"].is_unique)
    check("return_id unique",
          returns["return_id"].is_unique)
    check("refund_id unique",
          refunds["refund_id"].is_unique)
    check("device_id unique",
          devices["device_id"].is_unique)
    check("address_id unique",
          addresses["address_id"].is_unique)

    # -- Null checks
    heading("NULL CHECKS")
    for name, df in [("customers", customers), ("orders", orders),
                     ("returns", returns), ("refunds", refunds),
                     ("devices", devices), ("addresses", addresses)]:
        nulls = df.isnull().sum()
        has_nulls = nulls.sum() > 0
        if has_nulls:
            cols_with = nulls[nulls > 0].to_dict()
            check(f"{name} - no nulls", False)
            for col, cnt in cols_with.items():
                lines.append(f"          -> {col}: {cnt} nulls")
        else:
            check(f"{name} - no nulls", True)

    # -- Foreign-key integrity
    heading("FOREIGN-KEY CHECKS")
    cust_ids = set(customers["customer_id"])
    order_ids = set(orders["order_id"])
    dev_ids = set(devices["device_id"])
    addr_ids = set(addresses["address_id"])

    check("orders.customer_id -> customers",
          set(orders["customer_id"]).issubset(cust_ids))
    check("returns.order_id -> orders",
          set(returns["order_id"]).issubset(order_ids))
    check("returns.customer_id -> customers",
          set(returns["customer_id"]).issubset(cust_ids))
    check("refunds.order_id -> orders",
          set(refunds["order_id"]).issubset(order_ids))
    check("refunds.customer_id -> customers",
          set(refunds["customer_id"]).issubset(cust_ids))
    check("customers.device_id -> devices",
          set(customers["device_id"]).issubset(dev_ids))
    check("customers.address_id -> addresses",
          set(customers["address_id"]).issubset(addr_ids))

    # -- Impossible values
    heading("IMPOSSIBLE-VALUE CHECKS")
    check("order_amount > 0",
          (orders["order_amount"] > 0).all())
    check("return_amount > 0",
          (returns["return_amount"] > 0).all() if len(returns) > 0 else True)
    check("refund_amount > 0",
          (refunds["refund_amount"] > 0).all() if len(refunds) > 0 else True)

    # Refund <= order amount
    if len(refunds) > 0:
        merged = refunds.merge(orders[["order_id", "order_amount"]], on="order_id")
        check("refund_amount <= order_amount",
              (merged["refund_amount"] <= merged["order_amount"] + 0.01).all())

    # Return amount <= order amount
    if len(returns) > 0:
        merged_r = returns.merge(orders[["order_id", "order_amount"]], on="order_id")
        check("return_amount <= order_amount",
              (merged_r["return_amount"] <= merged_r["order_amount"] + 0.01).all())

    check("linked_accounts >= 1 (devices)",
          (devices["linked_accounts"] >= 1).all())
    check("linked_accounts >= 1 (addresses)",
          (addresses["linked_accounts"] >= 1).all())
    check("account_age_days >= 0",
          (customers["account_age_days"] >= 0).all())

    # -- Date consistency
    heading("DATE-CONSISTENCY CHECKS")

    # return_date >= order_date
    if len(returns) > 0:
        ret_ord = returns.merge(orders[["order_id", "order_date"]], on="order_id")
        ret_ord["order_date"] = pd.to_datetime(ret_ord["order_date"])
        ret_ord["return_date"] = pd.to_datetime(ret_ord["return_date"])
        check("return_date >= order_date",
              (ret_ord["return_date"] >= ret_ord["order_date"]).all())

    # refund_date >= order_date
    if len(refunds) > 0:
        ref_ord = refunds.merge(orders[["order_id", "order_date"]], on="order_id")
        ref_ord["order_date"] = pd.to_datetime(ref_ord["order_date"])
        ref_ord["refund_date"] = pd.to_datetime(ref_ord["refund_date"])
        check("refund_date >= order_date",
              (ref_ord["refund_date"] >= ref_ord["order_date"]).all())

    # order_date >= signup_date
    ord_cust = orders.merge(customers[["customer_id", "signup_date"]], on="customer_id")
    ord_cust["signup_date"] = pd.to_datetime(ord_cust["signup_date"])
    ord_cust["order_date"] = pd.to_datetime(ord_cust["order_date"])
    check("order_date >= signup_date",
          (ord_cust["order_date"] >= ord_cust["signup_date"]).all())

    # -- Distribution summaries
    heading("DISTRIBUTION SUMMARIES")

    # Returns per customer
    ret_counts = returns.groupby("customer_id").size()
    cust_with_returns = ret_counts.index
    cust_without = len(cust_ids - set(cust_with_returns))
    lines.append(f"  Customers with 0 returns : {cust_without}")
    lines.append(f"  Customers with >=1 return: {len(cust_with_returns)}")
    if len(ret_counts) > 0:
        lines.append(f"  Max returns per customer : {ret_counts.max()}")
        lines.append(f"  Mean returns (returners) : {ret_counts.mean():.1f}")

    # Shared devices
    shared_dev = devices[devices["linked_accounts"] > 1]
    lines.append(f"  Shared devices (>1 acct) : {len(shared_dev)}")

    # Shared addresses
    shared_addr = addresses[addresses["linked_accounts"] > 1]
    lines.append(f"  Shared addresses (>1 acct): {len(shared_addr)}")

    # Orders per customer stats
    ord_counts = orders.groupby("customer_id").size()
    lines.append(f"  Orders/customer — min: {ord_counts.min()}, "
                 f"max: {ord_counts.max()}, mean: {ord_counts.mean():.1f}")

    report = "\n".join(lines)
    return report


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════

def main(seed: int = 42, output_dir: str = None):
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(__file__))

    np.random.seed(seed)
    random.seed(seed)

    print(f"[ReturnShield AI] Dataset Generator")
    print(f"   Seed: {seed}")
    print(f"   Output: {output_dir}")
    print()

    # -- Step 1: Behavior types
    print("  [1/7] Assigning behavior types...")
    behavior_types = assign_behavior_types(NUM_CUSTOMERS)

    # -- Step 2: Devices
    print("  [2/7] Generating devices...")
    device_assignments, devices_df = generate_devices_and_assign(behavior_types)

    # -- Step 3: Addresses
    print("  [3/7] Generating addresses...")
    address_assignments, city_assignments, addresses_df = \
        generate_addresses_and_assign(behavior_types)

    # -- Step 4: Customers
    print("  [4/7] Generating customers...")
    customers_df, behavior_map = generate_customers(
        behavior_types, device_assignments, address_assignments, city_assignments)

    # -- Step 5: Orders
    print("  [5/7] Generating orders...")
    orders_df = generate_orders(customers_df, behavior_map)

    # -- Step 6: Returns
    print("  [6/7] Generating returns...")
    returns_df = generate_returns(orders_df, behavior_map)

    # -- Step 7: Refunds
    print("  [7/7] Generating refunds...")
    refunds_df = generate_refunds(returns_df, orders_df, behavior_map)

    # -- Validate
    print("\n  Running validation checks...\n")
    report = validate_all(customers_df, orders_df, returns_df,
                          refunds_df, devices_df, addresses_df)
    print(report)

    # -- Save CSVs
    os.makedirs(output_dir, exist_ok=True)
    customers_df.to_csv(os.path.join(output_dir, "customers.csv"), index=False)
    orders_df.to_csv(os.path.join(output_dir, "orders.csv"), index=False)
    returns_df.to_csv(os.path.join(output_dir, "returns.csv"), index=False)
    refunds_df.to_csv(os.path.join(output_dir, "refunds.csv"), index=False)
    devices_df.to_csv(os.path.join(output_dir, "devices.csv"), index=False)
    addresses_df.to_csv(os.path.join(output_dir, "addresses.csv"), index=False)

    print(f"\n  [OK] All 6 CSV files saved to: {output_dir}")
    print(f"     customers.csv  - {len(customers_df):,} rows")
    print(f"     orders.csv     - {len(orders_df):,} rows")
    print(f"     returns.csv    - {len(returns_df):,} rows")
    print(f"     refunds.csv    - {len(refunds_df):,} rows")
    print(f"     devices.csv    - {len(devices_df):,} rows")
    print(f"     addresses.csv  - {len(addresses_df):,} rows")

    # Save validation report
    with open(os.path.join(output_dir, "validation_report.txt"), "w",
              encoding="utf-8") as f:
        f.write(report)
    print(f"     validation_report.txt saved.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ReturnShield AI — Synthetic Dataset Generator")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output directory (default: same as script)")
    args = parser.parse_args()
    main(seed=args.seed, output_dir=args.output)
