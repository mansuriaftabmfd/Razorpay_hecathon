# Data Leakage Check — ReturnShield AI Phase 1

## What is Data Leakage?

Data leakage happens when the model accidentally "sees" future information
during training that it wouldn't have during real-time prediction.

Example of leakage:
- Training on return_rate computed over ALL returns (including future ones)
- Using tomorrow's refund data to predict today's return risk

## How We Prevent Leakage

### Cutoff Time

Every feature is computed using a **strict historical cutoff**:

```
cutoff_time = return_date of the CURRENT return request
```

All data filters use `< cutoff_time` (strictly before):

| Data Source | Filter Applied |
|-------------|---------------|
| Orders | `order_date < cutoff_time` |
| Returns | `return_date < cutoff_time AND return_id != current_return_id` |
| Refunds | `refund_date < cutoff_time` |

### Current Return Exclusion

The current return being scored is **explicitly excluded** from historical
aggregates. For example, `previous_returns` counts returns BEFORE the current
one, not including it.

### No Future Data

- `return_rate` = returns BEFORE this return / orders BEFORE this return
- `returns_last_7d` = returns in the 7 days BEFORE this return (excluding it)
- `refund_to_order_ratio` = refund amount from BEFORE / order amount from BEFORE

### Static Features (No Temporal Risk)

- `device_linked_accounts`: From devices table (point-in-time snapshot)
- `address_linked_accounts`: From addresses table (point-in-time snapshot)

These are not time-varying in the current dataset, so no leakage risk.

## Train/Test Split

- 80/20 split with `stratify=y` (label ratio preserved)
- `random_state=42` (reproducible)
- Split is on return-level rows (not customer-level)

**Note:** We do NOT use temporal splitting (train on older, test on newer)
in this version. A temporal split would be more realistic but requires
sorting by return_date first. This is acceptable for a hackathon prototype.

## Verification

Run `python ml/train.py` and check that:
1. Test accuracy is reasonable (not 99.9%+ which would suggest leakage)
2. SHAP feature importances make business sense
3. The model generalizes to unseen returns
