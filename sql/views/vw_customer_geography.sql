-- Customer Geographic Analytics View

CREATE OR REPLACE VIEW vw_customer_geography AS

SELECT
    c.customer_id,
    c.customer_unique_id,
    c.customer_zip_code_prefix,
    c.customer_city,
    c.customer_state,

    g.median_latitude,
    g.median_longitude,
    g.geographic_quality_status

FROM customers c

LEFT JOIN vw_geolocation_by_zip_quality g
    ON c.customer_zip_code_prefix = g.zip_code_prefix;
