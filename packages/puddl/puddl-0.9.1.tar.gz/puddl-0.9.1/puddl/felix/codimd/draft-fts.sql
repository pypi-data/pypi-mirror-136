-- FTS
WITH x AS (
    SELECT *,
           setweight(to_tsvector(title), 'A')
               -- h1 headings
--                || setweight(array_to_tsvector(regexp_matches(text, '^#[^#].+$')), 'B')
               -- h2 headings
--                || setweight(array_to_tsvector(regexp_matches(text, '^##+.+$')), 'C')
               || setweight(to_tsvector(text), 'D')
               AS doc
    FROM codimd.index
)
SELECT
    url,
    ts_rank_cd(doc, query, 32) AS rank,
    text
FROM x, to_tsquery('postgres') query
ORDER BY rank DESC
;

