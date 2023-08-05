CREATE OR REPLACE VIEW codimd.index AS
SELECT
    n.id,
    r.name AS remote_name,
    (TIMESTAMP WITHOUT TIME ZONE 'epoch' + time * INTERVAL '1 millisecond') AT TIME ZONE 'UTC' AS dt,
    r.url || '/' || n.note_id AS url,
    h.text AS title,
    tags,
    n.text AS text
FROM codimd.history h
         INNER JOIN codimd.notes n ON h.id = n.note_id
         INNER JOIN codimd.remotes r ON n.remote_id = r.id
ORDER BY dt DESC
;

CREATE OR REPLACE VIEW codimd.cli_ls AS
SELECT id, remote_name, dt, title
FROM codimd.index
;
