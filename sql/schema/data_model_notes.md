# E-Commerce BI & Decision Support System
## Relational Data Model Documentation

### 1. Project Overview

This document describes the logical relationships between the
nine Olist datasets stored in the DuckDB database.

Database: ecommerce.duckdb

### 2. Core Database Tables

| Table | Primary Identifier | Description |
|---|---|---|
| orders | order_id | Customer order information |
| order_items | order_id + order_item_id | Products included in each order |
| order_payments | order_id + payment_sequential | Payment transactions |
| order_reviews | review_id | Customer reviews |
| customers | customer_id | Customer information |
| sellers | seller_id | Seller information |
| products | product_id | Product information |
| geolocation | zip_code_prefix + coordinates | Geographic reference data |
| category_translation | product_category_name | Product category translations |

Note: These identifiers are proposed logical keys.
Their uniqueness and integrity must be validated.

### 3. Main Relationships

| Parent Table | Child Table | Join Column | Relationship |
|---|---|---|---|
| customers | orders | customer_id | One-to-many |
| orders | order_items | order_id | One-to-many |
| orders | order_payments | order_id | One-to-many |
| orders | order_reviews | order_id | One-to-many |
| products | order_items | product_id | One-to-many |
| sellers | order_items | seller_id | One-to-many |
| products | category_translation | product_category_name | Many-to-one |

### 4. Geographic Relationships

Customer and seller location information can be
associated with the geolocation dataset using zip_code_prefix.

The geolocation dataset contains repeated geographic
records. Therefore, uniqueness and aggregation must be
investigated before joining it to customer or seller data.

### 5. Analytical Design Principles

1. Preserve all original raw tables.
2. Use separate SQL views for analytical transformations.
3. Validate join keys before joining datasets.
4. Avoid unintended row multiplication during joins.
5. Aggregate order items and payments carefully.
6. Exclude canceled and unavailable orders from
   appropriate delivery performance calculations.
7. Preserve missing values where imputation is not justified.
8. Prevent target leakage in machine learning datasets.

### 6. Machine Learning Considerations

The proposed prediction target is late delivery.

Late delivery is determined by comparing the actual
customer delivery date against the estimated delivery date.

Only information available at the selected prediction
time should be used as model features.

Actual delivery timestamps, delivery outcomes and
post-delivery customer reviews must not be used
as predictive features.

### 7. Validation Status

Initial logical model documented.

Primary key uniqueness, foreign key coverage,
duplicate records and join cardinality require
empirical validation before final analytical view creation.
