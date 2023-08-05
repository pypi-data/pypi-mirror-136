DROP FUNCTION IF EXISTS timestamp_to_iso8601 CASCADE
;
CREATE OR REPLACE FUNCTION timestamp_to_iso8601(t TIMESTAMP WITH TIME ZONE)
    RETURNS TEXT AS
$$
BEGIN
    RETURN to_char(t, 'YYYY-MM-DD"T"HH24:MI:SSOF:00');
END
$$ LANGUAGE plpgsql
;

DROP FUNCTION IF EXISTS exif_coords2float_coords(exif_coords TEXT) CASCADE
;

CREATE OR REPLACE FUNCTION exif_coords2float_coords(x TEXT)
    RETURNS DOUBLE PRECISION AS
$$
DECLARE
    hr        NUMERIC;
    min       NUMERIC;
    sec       NUMERIC;
    precision NUMERIC;
    hmsp      NUMERIC[];
BEGIN
    hmsp = regexp_matches(x, '\[(\d+), (\d+), (\d+)/?(\d+)?\]');
    SELECT hmsp[1] INTO hr;
    SELECT hmsp[2] INTO min;
    SELECT hmsp[3] INTO sec;
    SELECT coalesce(hmsp[4], 1) INTO precision;
    RAISE DEBUG 'hr=%, min=%, sec=%, precision=%', hr, min, sec, precision;
    RETURN hr + (min / 60) + (sec / 3600 / precision);
END
$$ LANGUAGE plpgsql
;

COMMENT ON FUNCTION exif_coords2float_coords(x TEXT) IS 'Converts exif text coordinates, e.g. "[41, 51, 38]", into decimal coordinates'
;

DROP VIEW IF EXISTS markers
;

CREATE OR REPLACE VIEW markers AS
WITH a AS (
    SELECT index,
           _name AS name,
           _path,
           exif_coords2float_coords("GPS GPSLatitude") AS lat,
           exif_coords2float_coords("GPS GPSLongitude") AS lng,
           coalesce("Image GPSInfo"::INT, 400) as alt,
           -- We parse the datetime to make sure it is interpreted without timezone and make it a text
           -- just to be able to concatenate it with the given offset.
           -- Then we cast it with time zone again.
           (
                       to_timestamp("EXIF DateTimeOriginal", 'YYYY:MM:DD HH24:MI:SS')::TIMESTAMP WITHOUT TIME ZONE::TEXT
                       || ' ' || COALESCE("EXIF OffsetTime", '+02:00')
               )::TIMESTAMP WITH TIME ZONE
               AS dt,
           thumb
    FROM s7
    WHERE _name IS NOT NULL
      AND "GPS GPSLatitude" IS NOT NULL
      AND "GPS GPSLongitude" IS NOT NULL
)
SELECT index as id,
       name,
       'file://' || _path AS url,
       lat,
       lng,
       alt,
       timestamp_to_iso8601(dt) AS dt,
       dt AS dt_ts,
       thumb,
       (dt::timestamptz - (SELECT min(dt)::timestamptz FROM a))::text AS since_start
FROM a
;

-- something completely different
-- goal is to find a good folder structure with neither too many nor too few entries
-- - year-segments are too large for my collection (700+ entries)
--   SELECT year, count(*) FROM jpg_date GROUP BY YEAR;
-- - year/month-segments have 30 folders and weird distribution of entries (from 19 to 200)
--   SELECT year, month, count(*) FROM jpg_date GROUP BY year, month
CREATE OR REPLACE VIEW jpg_date AS
WITH x AS (SELECT regexp_matches(_name, '(\d\d\d\d)(\d\d)(\d\d)_.*') AS a
           FROM s7)
SELECT a[1]::NUMERIC AS year,
       a[2]::NUMERIC AS month,
       a[3]::NUMERIC AS day
FROM x
;

