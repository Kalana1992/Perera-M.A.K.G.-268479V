-- Seller Geographic Analytics View

CREATE OR REPLACE VIEW vw_seller_geography AS

SELECT
    s.seller_id,
    s.seller_zip_code_prefix,
    s.seller_city,
    s.seller_state,

    g.median_latitude,
    g.median_longitude,
    g.geographic_quality_status

FROM sellers s

LEFT JOIN vw_geolocation_by_zip_quality g
    ON s.seller_zip_code_prefix = g.zip_code_prefix;
