SET client_min_messages TO 'debug';
SELECT exif_coords2float_coords('[47, 40, 870483/25000]') = 47.6763387;
SELECT exif_coords2float_coords('[47, 40, 35]') = 47.67638888888889;
SELECT timestamp_to_iso8601('2021-09-11 22:35:08.742355 +00:00'::timestamp) = '2021-09-11T22:35:08Z';

SELECT * FROM markers;
SHOW TIMEZONE;
SELECT current_timestamp;
