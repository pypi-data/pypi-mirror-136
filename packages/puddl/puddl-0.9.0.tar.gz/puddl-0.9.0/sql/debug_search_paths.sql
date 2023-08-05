-- https://dba.stackexchange.com/questions/56023/what-is-the-search-path-for-a-given-database-and-user
SELECT
    r.rolname,
    d.datname,
    rs.setconfig
FROM pg_db_role_setting rs
         LEFT JOIN pg_roles r ON r.oid = rs.setrole
         LEFT JOIN pg_database d ON d.oid = rs.setdatabase
