DROP VIEW IF EXISTS puddl_databases CASCADE
;

CREATE VIEW puddl_databases AS
SELECT
    datname AS name
FROM pg_database
WHERE NOT datistemplate
    AND datname != 'postgres'
ORDER BY datname
;

SELECT *
FROM puddl_databases
;
