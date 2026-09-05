# backend/seed_data.py
# ============================================================
# SEED DATABASE — CSV Data ko SQLite mein load karo
# ============================================================
# Yeh script ek baar chalao: woh sab 6 raw CSV files padh ke
# SQLite database mein rows insert kar deta hai.
#
# Run karo:
#   .venv\Scripts\python.exe backend/seed_data.py
# ============================================================

import os
import sys
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import engine, SessionLocal, Base
from backend import models

DATA_DIR = os.path.join(PROJECT_ROOT, "data")


def seed():
    print("\n[SEED] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("[SEED] Tables created!")

    db = SessionLocal()

    try:
        # ── Customers ─────────────────────────────────────────
        if db.query(models.Customer).count() == 0:
            print("[SEED] Loading customers.csv...")
            df = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))
            for _, row in df.iterrows():
                db.add(models.Customer(
                    customer_id=str(row.get("customer_id", "")),
                    name=str(row.get("name", "")) if pd.notna(row.get("name")) else None,
                    email=str(row.get("email", "")) if pd.notna(row.get("email")) else None,
                    phone=str(row.get("phone", "")) if pd.notna(row.get("phone")) else None,
                    city=str(row.get("city", "")) if pd.notna(row.get("city")) else None,
                    customer_segment=str(row.get("customer_segment", "")) if pd.notna(row.get("customer_segment")) else None,
                    signup_date=str(row.get("signup_date", "")) if pd.notna(row.get("signup_date")) else None,
                    device_id=str(row.get("device_id", "")) if pd.notna(row.get("device_id")) else None,
                    address_id=str(row.get("address_id", "")) if pd.notna(row.get("address_id")) else None,
                ))
            db.commit()
            print(f"    Inserted {len(df)} customers.")
        else:
            print("[SEED] Customers already seeded, skipping.")

        # ── Orders ────────────────────────────────────────────
        if db.query(models.Order).count() == 0:
            print("[SEED] Loading orders.csv...")
            df = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"))
            batch = []
            for _, row in df.iterrows():
                batch.append(models.Order(
                    order_id=str(row.get("order_id", "")),
                    customer_id=str(row.get("customer_id", "")),
                    order_date=str(row.get("order_date", "")) if pd.notna(row.get("order_date")) else None,
                    order_amount=float(row["order_amount"]) if pd.notna(row.get("order_amount")) else None,
                    payment_method=str(row.get("payment_method", "")) if pd.notna(row.get("payment_method")) else None,
                    product_category=str(row.get("product_category", "")) if pd.notna(row.get("product_category")) else None,
                    order_status=str(row.get("order_status", "")) if pd.notna(row.get("order_status")) else None,
                ))
                if len(batch) >= 500:
                    db.bulk_save_objects(batch)
                    db.commit()
                    batch = []
            if batch:
                db.bulk_save_objects(batch)
                db.commit()
            print(f"    Inserted {len(df)} orders.")
        else:
            print("[SEED] Orders already seeded, skipping.")

        # ── Returns ───────────────────────────────────────────
        if db.query(models.Return).count() == 0:
            print("[SEED] Loading returns.csv...")
            df = pd.read_csv(os.path.join(DATA_DIR, "returns.csv"))
            for _, row in df.iterrows():
                db.add(models.Return(
                    return_id=str(row.get("return_id", "")),
                    customer_id=str(row.get("customer_id", "")),
                    order_id=str(row.get("order_id", "")),
                    return_date=str(row.get("return_date", "")) if pd.notna(row.get("return_date")) else None,
                    return_amount=float(row["return_amount"]) if pd.notna(row.get("return_amount")) else None,
                    return_reason=str(row.get("return_reason", "")) if pd.notna(row.get("return_reason")) else None,
                    return_status=str(row.get("return_status", "")) if pd.notna(row.get("return_status")) else None,
                ))
            db.commit()
            print(f"    Inserted {len(df)} returns.")
        else:
            print("[SEED] Returns already seeded, skipping.")

        # ── Refunds ───────────────────────────────────────────
        if db.query(models.Refund).count() == 0:
            print("[SEED] Loading refunds.csv...")
            df = pd.read_csv(os.path.join(DATA_DIR, "refunds.csv"))
            for _, row in df.iterrows():
                db.add(models.Refund(
                    refund_id=str(row.get("refund_id", "")),
                    customer_id=str(row.get("customer_id", "")),
                    return_id=str(row.get("return_id", "")) if pd.notna(row.get("return_id")) else None,
                    refund_date=str(row.get("refund_date", "")) if pd.notna(row.get("refund_date")) else None,
                    refund_amount=float(row["refund_amount"]) if pd.notna(row.get("refund_amount")) else None,
                    refund_status=str(row.get("refund_status", "")) if pd.notna(row.get("refund_status")) else None,
                ))
            db.commit()
            print(f"    Inserted {len(df)} refunds.")
        else:
            print("[SEED] Refunds already seeded, skipping.")

        # ── Devices ───────────────────────────────────────────
        if db.query(models.Device).count() == 0:
            print("[SEED] Loading devices.csv...")
            df = pd.read_csv(os.path.join(DATA_DIR, "devices.csv"))
            for _, row in df.iterrows():
                db.add(models.Device(
                    device_id=str(row.get("device_id", "")),
                    device_type=str(row.get("device_type", "")) if pd.notna(row.get("device_type")) else None,
                    linked_accounts=int(row["linked_accounts"]) if pd.notna(row.get("linked_accounts")) else 1,
                ))
            db.commit()
            print(f"    Inserted {len(df)} devices.")
        else:
            print("[SEED] Devices already seeded, skipping.")

        # ── Addresses ─────────────────────────────────────────
        if db.query(models.Address).count() == 0:
            print("[SEED] Loading addresses.csv...")
            df = pd.read_csv(os.path.join(DATA_DIR, "addresses.csv"))
            for _, row in df.iterrows():
                db.add(models.Address(
                    address_id=str(row.get("address_id", "")),
                    city=str(row.get("city", "")) if pd.notna(row.get("city")) else None,
                    state=str(row.get("state", "")) if pd.notna(row.get("state")) else None,
                    pincode=str(row.get("pincode", "")) if pd.notna(row.get("pincode")) else None,
                    linked_accounts=int(row["linked_accounts"]) if pd.notna(row.get("linked_accounts")) else 1,
                ))
            db.commit()
            print(f"    Inserted {len(df)} addresses.")
        else:
            print("[SEED] Addresses already seeded, skipping.")

        print("\n[SEED] Database seeding complete!")
        print(f"       Customers: {db.query(models.Customer).count()}")
        print(f"       Orders:    {db.query(models.Order).count()}")
        print(f"       Returns:   {db.query(models.Return).count()}")
        print(f"       Refunds:   {db.query(models.Refund).count()}")
        print(f"       Devices:   {db.query(models.Device).count()}")
        print(f"       Addresses: {db.query(models.Address).count()}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
