-- =====================================================
-- View: Geolocation Quality Classification
-- Purpose: Flag coordinates outside broad Brazil bounds
-- =====================================================

CREATE OR REPLACE VIEW vw_geolocation_by_zip_quality AS

SELECT
    zip_code_prefix,
    median_latitude,
    median_longitude,
    source_record_count,
    distinct_coordinate_count,

    CASE
        WHEN median_latitude < -35
          OR median_latitude > 6
          OR median_longitude < -75
          OR median_longitude > -30
        THEN 'OUTSIDE_BRAZIL_SCREENING_BOUNDS'

        ELSE 'WITHIN_BRAZIL_SCREENING_BOUNDS'
    END AS geographic_quality_status

FROM vw_geolocation_by_zip;
