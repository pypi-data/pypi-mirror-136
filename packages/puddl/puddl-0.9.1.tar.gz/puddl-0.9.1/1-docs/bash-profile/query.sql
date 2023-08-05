CREATE OR REPLACE VIEW timed_lines AS
SELECT
    index AS num,
    line
FROM lines
WHERE line LIKE '▬%'
;

CREATE VIEW matches AS
SELECT
    num,
    line,
    regexp_matches(line, '(▬+)\s+(\d+\.\d+)\s+(.*)') AS m
FROM timed_lines
;

CREATE VIEW flat AS
SELECT
    num,
    char_length(m[1]) - 1 AS lvl,
    m[2]::NUMERIC AS t,
    m[3] AS line
FROM matches
;

CREATE VIEW sane AS
SELECT
    a.num,
    a.lvl,
    a.t::NUMERIC AS t0,
    b.t::NUMERIC AS t1,
    a.line
FROM flat a
         JOIN flat b ON b.num = (a.num + 1)
;

CREATE VIEW durations AS
SELECT
    num,
    lvl,
    line,
    (t1 - t0) AS dur
FROM sane
ORDER BY dur DESC
;


SELECT *
FROM durations
LIMIT 10
;
