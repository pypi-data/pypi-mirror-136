CREATE OR REPLACE VIEW videos AS
    WITH j AS ( -- aka. "JSON" (but as columns)
        SELECT id,
            (meta ->> 'source') AS source,
            (meta ->> 'uuid') AS uuid,
            (meta ->> 'uri') AS uri,
--         (meta ->> 'load_dt') AS isodt,
--         (meta ->> 'path') AS path,
            (meta -> 'ffprobe' -> 'format' ->> 'duration')::NUMERIC AS duration_secs,
            to_timestamp((meta -> 'stat' ->> 'st_ctime')::NUMERIC) AS st_ctime,
--        to_timestamp((meta ->> 'path')),
            (meta ->> 'filename') AS filename
--     jsonb_path_query_first(meta, '$.ffprobe.format.duration')::text AS duration_secs
--     (meta #>> '{ffprobe,format,duration}') as d3,
        FROM stream),
        c AS ( -- aka. "clean"
            SELECT j.id,
                j.source,
                j.uuid,
                j.uri,
                (j.duration_secs::TEXT || ' seconds')::INTERVAL AS duration,
                split_part(j.filename, '.', 1) AS c_filename -- filename has date
            FROM j
        ),
        x AS ( -- aka. "extracted"
            SELECT c.*,
                -- we expect all filenames to contain a date of the format 'YYYY-MM-DD_HH24-MI-SS'
                to_timestamp(substring(c_filename, '(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})'),
                             'YYYY-MM-DD_HH24-MI-SS') AS dt
            FROM c
        ),
        f AS ( -- aka. "final"
            SELECT x.id,
                x.source,
                x.dt AS t0,
                x.dt + x.duration AS t1,
                x.uuid,
                x.uri
            FROM x
        )
    SELECT *
    FROM f;
