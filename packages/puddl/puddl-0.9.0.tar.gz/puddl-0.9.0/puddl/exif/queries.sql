-- be sure to run definitions.sql first

SELECT exif_coords2float_coords('[47, 51, 38]');

SELECT year, month, count(*)
FROM jpg_date
GROUP BY year, month
