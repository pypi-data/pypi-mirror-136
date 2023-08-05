DROP FUNCTION IF EXISTS puddl_upsert_role(name TEXT, password TEXT)
;

CREATE FUNCTION puddl_upsert_role(name TEXT, password TEXT) RETURNS TEXT
    LANGUAGE plpgsql
AS
$$
BEGIN
    EXECUTE format('CREATE ROLE %s WITH LOGIN PASSWORD ''%s''', name, password);
    RETURN 'created';
EXCEPTION
    WHEN DUPLICATE_OBJECT THEN
        RAISE INFO 'updating password for role % already exists', name;
        EXECUTE format('ALTER ROLE %s PASSWORD ''%s''', name, password);
        RETURN 'updated';
END
$$
;

-- SELECT puddl_upsert_role('foo')
