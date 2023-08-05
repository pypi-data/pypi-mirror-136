DROP VIEW IF EXISTS commits CASCADE
;
CREATE VIEW commits AS
WITH clean AS (
    SELECT *,
        regexp_replace(repo_path, '^/home/felix/', '') AS repo
    FROM raw
)
SELECT
    split_part(repo, '/', 1) AS namespace,
    split_part(repo, '/', 2) AS repo_name,
    repo_path,
    repo_path || '/' || file_path AS abspath,
    dt,
    hash,
    file_path
FROM clean
