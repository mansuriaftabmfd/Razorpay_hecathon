# ReturnShield AI - Data Dictionary

> This document describes every column across all 6 CSV files in the ReturnShield AI data foundation.
> Columns are classified as **Raw Data** (directly recorded/stored) or **Derived** (computed from other fields).

---

## 1. `customers.csv`

| Column | Type | Description | Classification |
|--------|------|-------------|----------------|
| `customer_id` | String | Unique identifier for each customer (e.g., `CUST00001`). Primary key. | Raw Data |
| `signup_date` | Date (YYYY-MM-DD) | The date when the customer registered their account on the platform. | Raw Data |
| `account_age_days` | Integer | Number of days between `signup_date` and the reference date (2026-09-01). Indicates how long the account has existed. | **Derived** (computed from `signup_date` and reference date) |
| `device_id` | String | Foreign key referencing `devices.csv`. The primary device associated with this customer's account. | Raw Data |
| `address_id` | String | Foreign key referencing `addresses.csv`. The primary shipping/billing address on file. | Raw Data |
| `city` | String | City of the customer's primary address (e.g., Mumbai, Delhi, Bangalore). | Raw Data |
| `customer_segment` | String | Business-level customer classification. Values: `regular`, `premium`, `new`, `occasional`. **This is NOT a fraud/abuse label** - it reflects business segmentation based on account age and purchase patterns. | Raw Data |

---

## 2. `orders.csv`

| Column | Type | Description | Classification |
|--------|------|-------------|----------------|
| `order_id` | String | Unique identifier for each order (e.g., `ORD000001`). Primary key. | Raw Data |
| `customer_id` | String | Foreign key referencing `customers.csv`. The customer who placed this order. | Raw Data |
| `order_date` | Date (YYYY-MM-DD) | The date when the order was placed. Always on or after the customer's `signup_date`. | Raw Data |
| `order_amount` | Float | Total monetary value of the order in INR. Range varies by product category. Always > 0. | Raw Data |
| `category` | String | Product category. Values: `Electronics`, `Clothing`, `Footwear`, `Home & Kitchen`, `Beauty`, `Books`, `Sports`, `Accessories`. | Raw Data |
| `payment_method` | String | How the customer paid. Values: `Credit Card`, `Debit Card`, `UPI`, `Net Banking`, `COD`, `Wallet`. | Raw Data |
| `delivery_status` | String | Current delivery state. Values: `Delivered`, `In Transit`, `Returned to Seller`, `Cancelled`. Only `Delivered` orders can have returns. | Raw Data |

---

## 3. `returns.csv`

| Column | Type | Description | Classification |
|--------|------|-------------|----------------|
| `return_id` | String | Unique identifier for each return request (e.g., `RET000001`). Primary key. | Raw Data |
| `order_id` | String | Foreign key referencing `orders.csv`. The order being returned. Only references orders with `delivery_status = 'Delivered'`. | Raw Data |
| `customer_id` | String | Foreign key referencing `customers.csv`. The customer initiating the return. | Raw Data |
| `return_date` | Date (YYYY-MM-DD) | The date the return was initiated. Always on or after the corresponding `order_date`. | Raw Data |
| `return_reason` | String | Stated reason for the return. Values: `Defective Product`, `Wrong Item Received`, `Changed Mind`, `Not As Described`, `Size/Fit Issue`, `Better Price Found`, `Damaged in Transit`, `Quality Not Satisfactory`. | Raw Data |
| `return_amount` | Float | Monetary value of items being returned in INR. Always > 0 and always <= the original `order_amount`. Can be full or partial. | Raw Data |
| `return_status` | String | Processing outcome. Values: `Approved`, `Pending`, `Rejected`. | Raw Data |

---

## 4. `refunds.csv`

| Column | Type | Description | Classification |
|--------|------|-------------|----------------|
| `refund_id` | String | Unique identifier for each refund (e.g., `REF000001`). Primary key. | Raw Data |
| `order_id` | String | Foreign key referencing `orders.csv`. The order associated with this refund. | Raw Data |
| `customer_id` | String | Foreign key referencing `customers.csv`. The customer receiving the refund. | Raw Data |
| `refund_date` | Date (YYYY-MM-DD) | The date the refund was issued. Always on or after the `order_date`. For return-based refunds, also on or after `return_date`. | Raw Data |
| `refund_amount` | Float | Amount refunded in INR. Always > 0 and always <= the original `order_amount`. Can be full or partial. | Raw Data |
| `refund_status` | String | Processing state. Values: `Processed`, `Pending`, `Declined`. | Raw Data |

---

## 5. `devices.csv`

| Column | Type | Description | Classification |
|--------|------|-------------|----------------|
| `device_id` | String | Unique identifier for each device (e.g., `DEV00001`). Primary key. Referenced by `customers.device_id`. | Raw Data |
| `device_type` | String | Type of device used to access the platform. Values: `Mobile Browser`, `Desktop Browser`, `Tablet`, `Mobile App`. | Raw Data |
| `first_seen` | Date (YYYY-MM-DD) | The date this device was first recorded in the system. | Raw Data |
| `linked_accounts` | Integer | Number of distinct customer accounts associated with this device. A value > 1 indicates the device is shared across multiple accounts. | **Derived** (counted from customer-device assignments) |

---

## 6. `addresses.csv`

| Column | Type | Description | Classification |
|--------|------|-------------|----------------|
| `address_id` | String | Unique identifier for each address (e.g., `ADDR00001`). Primary key. Referenced by `customers.address_id`. | Raw Data |
| `city` | String | City where the address is located (e.g., Mumbai, Delhi, Pune). | Raw Data |
| `postal_area` | String | 6-digit postal/PIN code area (e.g., `400523`, `110245`). | Raw Data |
| `linked_accounts` | Integer | Number of distinct customer accounts registered at this address. A value > 1 indicates the address is shared. | **Derived** (counted from customer-address assignments) |

---

## Key Relationships

```
customers.device_id   -->  devices.device_id
customers.address_id  -->  addresses.address_id
orders.customer_id    -->  customers.customer_id
returns.order_id      -->  orders.order_id
returns.customer_id   -->  customers.customer_id
refunds.order_id      -->  orders.order_id
refunds.customer_id   -->  customers.customer_id
```

---

## Notes on Derived vs. Raw Data

| Type | Meaning |
|------|---------|
| **Raw Data** | Directly captured/recorded data points. These exist in the CSV as-is. |
| **Derived** | Computed from other raw fields. `account_age_days` is derived from `signup_date`. `linked_accounts` in devices/addresses is derived from counting customer assignments. |

### Future ML Features (NOT yet created)

The following concepts are **NOT columns in the current data** but will be engineered during the ML phase from raw data:

- `return_rate` - proportion of a customer's orders that were returned
- `avg_return_amount` - mean return value per customer
- `days_to_return` - time gap between order and return
- `refund_rate` - proportion of orders that led to refunds
- `order_frequency` - orders per unit time
- `burst_score` - measure of order clustering in short time windows
- `device_sharing_score` - risk signal from shared device patterns
- `address_sharing_score` - risk signal from shared address patterns
- `category_concentration` - how focused a customer is on high-value categories
- `return_reason_entropy` - diversity/pattern in stated return reasons
