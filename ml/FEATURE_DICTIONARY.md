# ReturnShield AI — Feature Dictionary

> **ML Unit:** One row = One return request  
> **Total Features:** 22 (all numerical)  
> **Categorical features:** NONE (spec: "Do NOT initially use customer_segment")

---

## Historical Aggregate Features (8)

These use ONLY data from BEFORE the current return's `return_date`.

| # | Feature | Type | Description | Risk Signal |
|---|---------|------|-------------|-------------|
| 1 | `account_age_days` | int | Days since customer signup to return date | New accounts (< 120 days) with high activity = suspicious |
| 2 | `previous_orders` | int | Total orders placed before this return | Context for return_rate calculation |
| 3 | `previous_returns` | int | Total returns made before this return | High absolute count = pattern |
| 4 | `return_rate` | float | `previous_returns / previous_orders` | > 0.35 = strong abuse signal |
| 5 | `previous_refund_count` | int | Total refunds received before this return | High refund history = pattern |
| 6 | `previous_refund_amount` | float | Sum of all previous refund amounts (INR) | Large cumulative refunds = financial drain |
| 7 | `average_order_value` | float | Mean order amount from previous orders (INR) | Baseline for high_value_return_flag |
| 8 | `refund_to_order_ratio` | float | `previous_refund_amount / total_order_amount` | > 0.30 = high refund drain |

## Velocity Features (4)

Recent activity bursts — fraud often shows sudden spikes.

| # | Feature | Type | Description | Risk Signal |
|---|---------|------|-------------|-------------|
| 9 | `orders_last_24h` | int | Orders placed in last 24 hours before return | Burst ordering before return = wardrobing |
| 10 | `returns_last_7d` | int | Returns made in last 7 days | >= 3 in a week = velocity abuse |
| 11 | `returns_last_30d` | int | Returns made in last 30 days | Sustained high return activity |
| 12 | `refunds_last_30d` | int | Refunds received in last 30 days | Sustained refund drain |

## Current Request Features (4)

Details of THIS specific return request.

| # | Feature | Type | Description | Risk Signal |
|---|---------|------|-------------|-------------|
| 13 | `current_order_amount` | float | Order value of the item being returned (INR) | High-value returns = higher risk |
| 14 | `current_return_amount` | float | Return claim amount (INR) | Compared against order value |
| 15 | `return_to_order_ratio` | float | `current_return_amount / current_order_amount` | > 1.0 = over-claiming |
| 16 | `days_to_return` | int | Days between order date and return date | Very fast (< 2 days) or very slow (> 20 days) = suspicious |

## Behavioral Pattern Features (5)

Learned abuse patterns detected from historical behavior.

| # | Feature | Type | Description | Risk Signal |
|---|---------|------|-------------|-------------|
| 17 | `same_reason_count` | int | How many previous returns used the same reason | Repeated "Damaged" claims = abuse pattern |
| 18 | `unique_return_reasons` | int | Number of distinct return reasons ever used | Very high = cycling through reasons |
| 19 | `return_frequency` | float | Returns per month (`previous_returns / (account_age / 30)`) | > 2 per month = high frequency |
| 20 | `return_gap_days` | int | Days since the customer's last return | Very small gap = burst behavior |
| 21 | `high_value_return_flag` | int (0/1) | 1 if `current_return_amount > 2 × average_order_value` | Targeting expensive items for return |

## Device / Address Linkage (2)

Identity fraud signals from shared infrastructure.

| # | Feature | Type | Description | Risk Signal |
|---|---------|------|-------------|-------------|
| 22 | `device_linked_accounts` | int | Number of customer accounts on same device | > 3 = device farm |
| 23 | `address_linked_accounts` | int | Number of customer accounts at same address | > 3 = address farming |

---

## Label

| Field | Type | Values | Method |
|-------|------|--------|--------|
| `potentially_abusive` | int | 0 (normal) or 1 (abusive) | Rule-based with 3% noise flip |

### Labeling Rules (any ONE true → label = 1):
1. `return_rate > 0.35 AND previous_returns >= 3`
2. `refund_to_order_ratio > 0.30`
3. `account_age_days < 120 AND previous_orders > 10`
4. `device_linked_accounts > 3 AND return_rate > 0.20`
5. `address_linked_accounts > 3 AND return_rate > 0.20`
6. `returns_last_7d >= 3` (velocity burst)
7. `high_value_return_flag == 1 AND return_rate > 0.25`
