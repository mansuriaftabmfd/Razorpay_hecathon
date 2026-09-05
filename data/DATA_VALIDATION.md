# ReturnShield AI - Data Validation Report

> Generated with seed `42` on 2026-09-05
> Script: `generate_dataset.py`

---

## 1. Row Counts

| Table | Rows | Expected Range | Status |
|-------|------|----------------|--------|
| `customers.csv` | 5,000 | 5,000 | PASS |
| `orders.csv` | 34,809 | 25,000 - 40,000 | PASS |
| `returns.csv` | 5,998 | Realistic subset of orders | PASS |
| `refunds.csv` | 4,127 | Subset of returns + goodwill | PASS |
| `devices.csv` | 4,598 | < 5,000 (some shared) | PASS |
| `addresses.csv` | 4,666 | < 5,000 (some shared) | PASS |

---

## 2. Duplicate / Unique-ID Checks

All primary keys are verified to be unique with zero duplicates.

| Check | Result |
|-------|--------|
| `customer_id` unique | PASS |
| `order_id` unique | PASS |
| `return_id` unique | PASS |
| `refund_id` unique | PASS |
| `device_id` unique | PASS |
| `address_id` unique | PASS |

---

## 3. Null Checks

Every column across all 6 tables has zero null values.

| Table | Null Columns | Result |
|-------|-------------|--------|
| `customers.csv` | None | PASS |
| `orders.csv` | None | PASS |
| `returns.csv` | None | PASS |
| `refunds.csv` | None | PASS |
| `devices.csv` | None | PASS |
| `addresses.csv` | None | PASS |

---

## 4. Foreign-Key Integrity Checks

Every foreign-key reference points to a valid record in the parent table.

| FK Relationship | Result |
|----------------|--------|
| `orders.customer_id` -> `customers.customer_id` | PASS |
| `returns.order_id` -> `orders.order_id` | PASS |
| `returns.customer_id` -> `customers.customer_id` | PASS |
| `refunds.order_id` -> `orders.order_id` | PASS |
| `refunds.customer_id` -> `customers.customer_id` | PASS |
| `customers.device_id` -> `devices.device_id` | PASS |
| `customers.address_id` -> `addresses.address_id` | PASS |

**0 broken foreign keys found across all tables.**

---

## 5. Impossible-Value Checks

| Check | Description | Result |
|-------|-------------|--------|
| `order_amount > 0` | No zero or negative order amounts | PASS |
| `return_amount > 0` | No zero or negative return amounts | PASS |
| `refund_amount > 0` | No zero or negative refund amounts | PASS |
| `refund_amount <= order_amount` | Refund never exceeds the original order value | PASS |
| `return_amount <= order_amount` | Return value never exceeds the original order value | PASS |
| `linked_accounts >= 1` (devices) | Every device is linked to at least 1 account | PASS |
| `linked_accounts >= 1` (addresses) | Every address is linked to at least 1 account | PASS |
| `account_age_days >= 0` | No future signup dates | PASS |

---

## 6. Date Consistency Checks

| Check | Description | Result |
|-------|-------------|--------|
| `return_date >= order_date` | Returns happen after the order was placed | PASS |
| `refund_date >= order_date` | Refunds happen after the order was placed | PASS |
| `order_date >= signup_date` | Orders happen after the customer signed up | PASS |

**0 date-consistency violations found.**

---

## 7. Distribution Summaries

### Returns Distribution
| Metric | Value |
|--------|-------|
| Customers with 0 returns | 2,795 (55.9%) |
| Customers with >= 1 return | 2,205 (44.1%) |
| Max returns per customer | 16 |
| Mean returns (among returners) | 2.7 |

### Shared Resources
| Metric | Value |
|--------|-------|
| Shared devices (> 1 account) | 153 |
| Shared addresses (> 1 account) | 169 |
| Total unique devices | 4,598 |
| Total unique addresses | 4,666 |

### Order Volume
| Metric | Value |
|--------|-------|
| Min orders per customer | 3 |
| Max orders per customer | 25 |
| Mean orders per customer | 7.0 |

---

## 8. Overall Validation Summary

| Category | Checks Run | Passed | Failed |
|----------|-----------|--------|--------|
| Unique IDs | 6 | 6 | 0 |
| Null Checks | 6 | 6 | 0 |
| Foreign Keys | 7 | 7 | 0 |
| Impossible Values | 8 | 8 | 0 |
| Date Consistency | 3 | 3 | 0 |
| **TOTAL** | **30** | **30** | **0** |

> **Result: ALL 30 VALIDATION CHECKS PASSED**
