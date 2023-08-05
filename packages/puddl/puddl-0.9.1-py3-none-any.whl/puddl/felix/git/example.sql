SET SESSION TIME ZONE 'Europe/Berlin'
;
-- most commits
SELECT
    repo_path,
    count(*)
FROM raw
GROUP BY repo_path
ORDER BY 2 DESC
;

-- latest commits
SELECT
    dt,
    repo_path,
    file_path
FROM raw
ORDER BY dt DESC
;

-- find a good python project by looking for a recent setup.cfg
SELECT
    max(dt) AS last_touched,
    abspath AS path,
    count(hash) AS count_touches
FROM commits
WHERE file_path = 'setup.cfg'
GROUP BY abspath
ORDER BY max(dt) DESC
;

-- find a Django project that also has as setup.cfg
WITH xs AS (
    SELECT
        commits.*,
        CASE WHEN file_path = 'setup.cfg' THEN 1 ELSE 0 END AS modern_python_project,
        CASE WHEN file_path = 'manage.py' THEN 1 ELSE 0 END AS django
    FROM commits
)
SELECT
    max(dt) AS last_touched,
    repo_name,
    repo_path,
    count(hash) AS count_touches
FROM xs
GROUP BY repo_name, repo_path
HAVING sum(modern_python_project) > 1
    AND sum(django) > 1
ORDER BY max(dt) DESC
;

WITH xs AS (
    SELECT
        commits.*,
        CASE WHEN file_path LIKE '%templates/%' THEN 1 ELSE 0 END AS score
    FROM commits
)
SELECT
    max(dt) AS max_dt,
    repo_name,
    repo_path,
    sum(score) AS score,
    count(hash) AS count_hash
FROM xs
GROUP BY repo_name, repo_path
HAVING sum(score) > 1
ORDER BY sum(score) DESC
;


-- repo activity per week
WITH extracted_dates AS (
    SELECT
        extract(YEAR FROM dt) AS year,
        extract(MONTH FROM dt) AS month,
        extract(WEEK FROM dt) AS week,
        extract(DAY FROM dt) AS day,
        raw.*
    FROM raw
),
    counts AS (
        SELECT
            regexp_replace(repo_path, '^/home/felix/', '') AS repo,
            year,
            month,
            week,
            count(*) AS commits
        FROM extracted_dates
        GROUP BY repo_path, year, month, week
    ),
    human AS (
        SELECT
            year,
            month,
            week,
            repo,
            split_part(repo, '/', 1) AS namespace,
            split_part(repo, '/', 2) AS name,
            commits
        FROM counts
        ORDER BY (year, month, week, commits) DESC
    ),
    ranked AS (
        SELECT
            year,
            month,
            name,
            rank() OVER (PARTITION BY year, month ORDER BY commits) AS rnk,
            commits
        FROM human
        WHERE name IN ('service', 'user-area', 'solr')
        ORDER BY (year, month, namespace, name) DESC
    )
SELECT
    year,
    name,
    sum(commits) AS commits
FROM ranked
WHERE rnk = 1
GROUP BY year, name
ORDER BY year DESC
;
