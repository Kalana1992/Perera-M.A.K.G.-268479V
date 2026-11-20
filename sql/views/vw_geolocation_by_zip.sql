-- =====================================================
-- View: Aggregated Geolocation by ZIP Code Prefix
-- Purpose: Create one representative coordinate per ZIP
-- =====================================================

CREATE OR REPLACE VIEW vw_geolocation_by_zip AS

SELECT
    geolocation_zip_code_prefix AS zip_code_prefix,

    MEDIAN(geolocation_lat) AS median_latitude,

    MEDIAN(geolocation_lng) AS median_longitude,

    COUNT(*) AS source_record_count,

    COUNT(DISTINCT (
        geolocation_lat,
        geolocation_lng
    )) AS distinct_coordinate_count

FROM geolocation

GROUP BY
    geolocation_zip_code_prefix;
